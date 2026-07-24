# SPDX-FileCopyrightText: © 2026 Shaun Wilson
# SPDX-License-Identifier: MIT

from __future__ import annotations

import logging
import os
import threading
import time
from enum import Enum
from typing import Callable, TypeAlias, TypedDict

from .Configuration import Configuration
from .providers import (
    JsonConfigurationProvider,
    TomlConfigurationProvider,
    YamlConfigurationProvider,
)


class WatchEventType(str, Enum):
    """The type of file system event detected during polling.

    A ``str``-backed ``Enum`` with compact single-character values.
    """

    CREATED = 'c'
    """The file was created or appeared after being deleted."""

    MODIFIED = 'm'
    """The file was modified (mtime or file size changed)."""

    DELETED = 'd'
    """The file was deleted or disappeared."""


class WatchState(TypedDict):
    """Internal state dictionary for a single watched file.

    Attributes:
        path: The fully resolved (canonical) file path.
        size: Last known file size in bytes, or ``None`` if not yet polled.
        mtime: Last known modification time, or ``None`` if not yet polled.
        state: One of ``'active'``, ``'deleted'``, or ``'pending'``.
    """

    path: str
    size: int | None
    mtime: float | None
    state: str


WatchEventHandler: TypeAlias = (
    Callable[[str, WatchEventType, Configuration | None], None] | None
)


class ConfigurationWatcher:
    """Monitors configuration files on disk for file system changes.

    Uses periodic polling with metadata comparison (mtime + file size) rather than
    OS-specific file system APIs. A background daemon thread manages the polling
    loop and spawns/terminates automatically based on active watches.
    """

    __interval: float
    __handler: WatchEventHandler
    __handler_lock: threading.Lock
    __lock: threading.Lock
    __logger: logging.Logger
    __running: bool
    __thread: threading.Thread | None
    __watches: dict[str, WatchState]

    def __init__(self, interval_seconds: float | None = None) -> None:
        """Initialize the configuration file watcher.

        Args:
            interval_seconds: Polling interval in seconds. Defaults to ``60.0``.
        """
        self.__interval = interval_seconds if interval_seconds is not None else 60.0
        self.__watches = {}
        self.__thread = None
        self.__running = False
        self.__lock = threading.Lock()
        self.__handler = None
        self.__handler_lock = threading.Lock()
        self.__logger = logging.getLogger(__name__)

    def add_watch(self, filepath: str) -> ConfigurationWatcher:
        """Add a file path to be watched for changes.

        The path is normalised to a fully-qualified (canonical) path via
        ``os.path.realpath``. Duplicate resolved paths are silently ignored.
        The polling thread is started on the first ``add_watch`` call.

        Args:
            filepath: The file system path to watch.
        """
        resolved = os.path.realpath(filepath)
        with self.__lock:
            is_first_watch = len(self.__watches) == 0
            if resolved not in self.__watches:
                self.__watches[resolved] = {
                    'path': resolved,
                    'size': None,
                    'mtime': None,
                    'state': 'pending',
                }
                if is_first_watch:
                    self.__start_thread()
        return self

    def remove_watch(self, filepath: str) -> ConfigurationWatcher:
        """Remove a previously added watch.

        Silently does nothing if the watch does not exist. The polling thread
        drains and exits when the last watch is removed.

        Args:
            filepath: The file system path whose watch should be removed.
        """
        resolved = os.path.realpath(filepath)
        with self.__lock:
            if resolved in self.__watches:
                del self.__watches[resolved]
                if len(self.__watches) == 0 and self.__thread is not None:
                    self.__drain_thread()
        return self

    def list_watches(self) -> list[str]:
        """Return a fresh list of all currently watched file paths.

        Returns:
            A list of canonical (resolved) file path strings.
        """
        with self.__lock:
            return [e['path'] for e in self.__watches.values()]

    @property
    def watch_handler(self) -> WatchEventHandler:
        """The callback invoked for file system events.

        The getter returns ``None`` if no handler has been set. The setter
        accepts ``None`` to clear the handler.

        The handler reference is captured under a lock and then invoked
        outside the lock to avoid potential deadlocks with external calls
        from within the handler (e.g. ``add_watch`` / ``remove_watch``).

        Returns:
            A callable of the form ``Callable[[str, WatchEventType, Configuration], None]``,
            or ``None`` if no handler is set.
        """
        with self.__handler_lock:
            return self.__handler

    @watch_handler.setter
    def watch_handler(self, handler: WatchEventHandler) -> None:
        """Set the event handler callback.

        Args:
            handler: A callable of the form ``Callable[[str, WatchEventType, Configuration], None]``,
                or ``None`` to clear.
        """
        with self.__handler_lock:
            self.__handler = handler

    def __start_thread(self) -> None:
        """Start the background polling thread.

        Called internally on the first ``add_watch``. The thread is a
        daemon thread so it does not prevent process exit.
        """
        self.__running = True
        self.__thread = threading.Thread(target=self.__poll_loop, daemon=True)
        self.__thread.start()

    def __drain_thread(self) -> None:
        """Stop the background polling thread and wait for it to exit.

        Sets ``__running`` to ``False``, then joins the thread with a
        timeout of ``self.__interval + 1`` seconds.
        """
        self.__running = False
        if self.__thread is not None:
            self.__thread.join(timeout=self.__interval + 1)
            if self.__thread.is_alive():
                self.__logger.warning(
                    'Watcher thread did not drain within %s seconds.',
                    self.__interval + 1,
                )
            self.__thread = None

    def __poll_loop(self) -> None:
        """Background thread entry point — continuous polling loop."""
        while self.__running:
            self.__poll_once()
            try:
                time.sleep(self.__interval)
            except KeyboardInterrupt:
                break

    def __poll_once(self) -> None:
        """Execute a single poll cycle over all watches.

        A snapshot of watch states is taken at the start of the cycle so
        that concurrent ``add_watch``/``remove_watch`` calls do not
        interfere with the current iteration. All file I/O and parsing
        errors are logged at ERROR level and do not crash the thread.
        The watch state is updated directly in ``self.__watches`` after
        each event is processed.
        """
        with self.__lock:
            paths = list(self.__watches.keys())

        if not paths:
            return

        handler_ref = None
        with self.__handler_lock:
            handler_ref = self.__handler

        for path in paths:
            with self.__lock:
                if path not in self.__watches:
                    continue
                state = self.__watches[path]
                prev_state = state['state']
                prev_size = state['size']
                prev_mtime = state['mtime']

                file_exists = os.path.isfile(path)

                if file_exists and prev_state in ('deleted', 'pending'):
                    self.__on_created(path, state, handler_ref)
                elif file_exists and prev_state == 'active':
                    if prev_size is None or prev_mtime is None:
                        try:
                            stat = os.stat(path)
                            state['size'] = stat.st_size
                            state['mtime'] = stat.st_mtime
                        except OSError:
                            state['state'] = 'deleted'
                            self.__on_deleted(path, handler_ref)
                    else:
                        try:
                            stat = os.stat(path)
                            if stat.st_size != prev_size or stat.st_mtime != prev_mtime:
                                self.__on_modified(path, state, handler_ref)
                            else:
                                state['size'] = stat.st_size
                                state['mtime'] = stat.st_mtime
                        except OSError:
                            state['state'] = 'deleted'
                            self.__on_deleted(path, handler_ref)
                elif not file_exists and prev_state == 'active':
                    state['state'] = 'deleted'
                    self.__on_deleted(path, handler_ref)

    def __on_created(
        self, path: str, state: WatchState, handler: WatchEventHandler,
    ) -> None:
        """Handle a CREATED event.

        Loads the configuration from the newly appeared file, updates the
        watch state to ``'active'``, and fires the handler.

        Args:
            path: The canonical file path.
            state: The watch state dictionary (updated in place, already in ``self.__watches``).
            handler: The handler callback reference (local copy).
        """
        if handler is None:
            return
        config = self.__load_configuration(path)
        if config is not None:
            state['state'] = 'active'
            try:
                stat = os.stat(path)
                state['size'] = stat.st_size
                state['mtime'] = stat.st_mtime
            except OSError:
                pass
            handler(path, WatchEventType.CREATED, config)

    def __on_modified(
        self, path: str, state: WatchState, handler: WatchEventHandler,
    ) -> None:
        """Handle a MODIFIED event.

        Loads the configuration from the modified file and fires the handler.
        Updates the watch state only if the configuration was successfully
        loaded.

        Args:
            path: The canonical file path.
            state: The watch state dictionary (updated in place, already in ``self.__watches``).
            handler: The handler callback reference (local copy).
        """
        if handler is None:
            return
        config = self.__load_configuration(path)
        if config is not None:
            try:
                stat = os.stat(path)
                state['size'] = stat.st_size
                state['mtime'] = stat.st_mtime
            except OSError:
                pass
            handler(path, WatchEventType.MODIFIED, config)

    def __on_deleted(self, path: str, handler: WatchEventHandler) -> None:
        """Handle a DELETED event.

        Fires the handler with ``None`` as the configuration parameter since
        the file cannot be parsed.

        Args:
            path: The canonical file path.
            handler: The handler callback reference (local copy).
        """
        if handler is None:
            return
        handler(path, WatchEventType.DELETED, None)

    def __load_configuration(self, path: str) -> Configuration | None:
        """Load a Configuration from a file based on its extension.

        Supported extensions: ``.json``, ``.toml``, ``.yaml`` / ``.yml``.
        Unrecognised extensions cause an error to be logged and ``None``
        is returned. Parsing errors and I/O errors are logged and return
        ``None`` without crashing.

        Args:
            path: The canonical file path to load.

        Returns:
            A populated ``Configuration`` instance, or ``None`` if the
            file cannot be loaded.
        """
        ext = os.path.splitext(path)[1].lower()
        try:
            configuration = Configuration()
            if ext == '.json':
                JsonConfigurationProvider(
                    filepath=path, required=False,
                ).populate_configuration(configuration)
            elif ext == '.toml':
                TomlConfigurationProvider(
                    filepath=path, required=False,
                ).populate_configuration(configuration)
            elif ext in ('.yaml', '.yml'):
                YamlConfigurationProvider(
                    filepath=path, required=False,
                ).populate_configuration(configuration)
            else:
                self.__logger.error(
                    'Cannot determine format for watched file %s '
                    '(extension \'%s\'). Skipping.',
                    path,
                    ext,
                )
                return None
            return configuration
        except Exception as e:
            self.__logger.error(
                'Error loading configuration from %s: %s. Skipping update.',
                path,
                e,
            )
            return None


__all__ = ['ConfigurationWatcher', 'WatchEventType']
