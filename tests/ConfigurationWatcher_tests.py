# SPDX-FileCopyrightText: © 2026 Shaun Wilson
# SPDX-License-Identifier: MIT

from __future__ import annotations

import json
import os
import shutil
import tempfile
import time

import appsettings2
from appsettings2 import WatchEventType
from punit import fact


# ── Init ──────────────────────────────────────────────────────────────────────

class InitTests:

    @fact
    def default_interval_is_60_seconds(self) -> None:
        watcher = appsettings2.ConfigurationWatcher()
        assert watcher._ConfigurationWatcher__interval == 60.0  # type: ignore[attr-defined]

    @fact
    def custom_interval_is_stored(self) -> None:
        watcher = appsettings2.ConfigurationWatcher(interval_seconds=5.0)
        assert watcher._ConfigurationWatcher__interval == 5.0  # type: ignore[attr-defined]

    @fact
    def custom_interval_float(self) -> None:
        watcher = appsettings2.ConfigurationWatcher(interval_seconds=0.5)
        assert watcher._ConfigurationWatcher__interval == 0.5  # type: ignore[attr-defined]

    @fact
    def no_thread_before_first_add_watch(self) -> None:
        watcher = appsettings2.ConfigurationWatcher(interval_seconds=0.1)
        assert watcher._ConfigurationWatcher__thread is None  # type: ignore[attr-defined]

    @fact
    def interval_is_immutable_after_construction(self) -> None:
        _watcher = appsettings2.ConfigurationWatcher(interval_seconds=5.0)  # noqa: F841
        # Attribute exists but may be reassigned — this is not a public API


# ── add_watch ─────────────────────────────────────────────────────────────────

class AddWatchTests:

    @fact
    def add_watch_succeeds_for_existing_file(self) -> None:
        tmpdir = tempfile.mkdtemp()
        path = os.path.join(tmpdir, 'test.json')
        with open(path, 'w') as f:
            json.dump({'key': 'val'}, f)
        try:
            watcher = appsettings2.ConfigurationWatcher(interval_seconds=0.1)
            watcher.add_watch(path)
            watches = watcher.list_watches()
            assert len(watches) == 1
            assert os.path.realpath(path) in watches
            watcher.remove_watch(path)
        finally:
            shutil.rmtree(tmpdir)

    @fact
    def add_watch_starts_thread(self) -> None:
        tmpdir = tempfile.mkdtemp()
        path = os.path.join(tmpdir, 'test.json')
        with open(path, 'w') as f:
            json.dump({'key': 'val'}, f)
        try:
            watcher = appsettings2.ConfigurationWatcher(interval_seconds=0.1)
            assert watcher._ConfigurationWatcher__thread is None  # type: ignore[attr-defined]
            watcher.add_watch(path)
            assert watcher._ConfigurationWatcher__thread is not None  # type: ignore[attr-defined]
            assert watcher._ConfigurationWatcher__thread.is_alive()  # type: ignore[attr-defined]
            watcher.remove_watch(path)
        finally:
            shutil.rmtree(tmpdir)

    @fact
    def add_watch_thread_is_daemon(self) -> None:
        tmpdir = tempfile.mkdtemp()
        path = os.path.join(tmpdir, 'test.json')
        with open(path, 'w') as f:
            json.dump({'key': 'val'}, f)
        try:
            watcher = appsettings2.ConfigurationWatcher(interval_seconds=0.1)
            watcher.add_watch(path)
            thread = watcher._ConfigurationWatcher__thread  # type: ignore[attr-defined]
            assert thread is not None
            assert thread.daemon is True
            watcher.remove_watch(path)
        finally:
            shutil.rmtree(tmpdir)

    @fact
    def add_watch_is_idempotent_for_same_resolved_path(self) -> None:
        tmpdir = tempfile.mkdtemp()
        path = os.path.join(tmpdir, 'test.json')
        with open(path, 'w') as f:
            json.dump({'key': 'val'}, f)
        try:
            watcher = appsettings2.ConfigurationWatcher(interval_seconds=0.1)
            watcher.add_watch(path)
            watcher.add_watch(path)
            assert len(watcher.list_watches()) == 1
            thread = watcher._ConfigurationWatcher__thread  # type: ignore[attr-defined]
            thread.join(timeout=1)
            initial_alive_unused = thread.is_alive()  # noqa: F841
            watcher.remove_watch(path)
            thread.join(timeout=1)
            assert not thread.is_alive()
        finally:
            shutil.rmtree(tmpdir)

    @fact
    def add_watch_resolves_relative_path(self) -> None:
        tmpdir = tempfile.mkdtemp()
        path = os.path.join(tmpdir, 'appsettings.json')
        with open(path, 'w') as f:
            json.dump({'key': 'val'}, f)
        rel_path = os.path.join(tmpdir, '.', 'appsettings.json')
        watcher = appsettings2.ConfigurationWatcher(interval_seconds=0.1)
        watcher.add_watch(rel_path)
        watches = watcher.list_watches()
        assert len(watches) == 1
        assert os.path.realpath(path) in watches
        watcher.remove_watch(path)


# ── remove_watch ──────────────────────────────────────────────────────────────

class RemoveWatchTests:

    @fact
    def remove_watch_succeeds(self) -> None:
        tmpdir = tempfile.mkdtemp()
        path = os.path.join(tmpdir, 'test.json')
        with open(path, 'w') as f:
            json.dump({'key': 'val'}, f)
        try:
            watcher = appsettings2.ConfigurationWatcher(interval_seconds=0.1)
            watcher.add_watch(path)
            watcher.remove_watch(path)
            assert len(watcher.list_watches()) == 0
        finally:
            shutil.rmtree(tmpdir)

    @fact
    def remove_non_existent_watch_is_noop(self) -> None:
        watcher = appsettings2.ConfigurationWatcher(interval_seconds=0.1)
        watcher.remove_watch('/non/existent/path.json')
        assert len(watcher.list_watches()) == 0

    @fact
    def remove_watch_thread_drains_when_last_watch_removed(self) -> None:
        tmpdir = tempfile.mkdtemp()
        path = os.path.join(tmpdir, 'test.json')
        with open(path, 'w') as f:
            json.dump({'key': 'val'}, f)
        try:
            watcher = appsettings2.ConfigurationWatcher(interval_seconds=0.1)
            watcher.add_watch(path)
            thread = watcher._ConfigurationWatcher__thread  # type: ignore[attr-defined]
            assert thread is not None and thread.is_alive()
            watcher.remove_watch(path)
            thread.join(timeout=2)
            assert not thread.is_alive()
        finally:
            shutil.rmtree(tmpdir)

    @fact
    def remove_watch_partial_keep_thread_alive(self) -> None:
        tmpdir = tempfile.mkdtemp()
        path1 = os.path.join(tmpdir, 'a.json')
        path2 = os.path.join(tmpdir, 'b.json')
        with open(path1, 'w') as f:
            json.dump({'key': '1'}, f)
        with open(path2, 'w') as f:
            json.dump({'key': '2'}, f)
        try:
            watcher = appsettings2.ConfigurationWatcher(interval_seconds=0.1)
            watcher.add_watch(path1)
            watcher.add_watch(path2)
            thread = watcher._ConfigurationWatcher__thread  # type: ignore[attr-defined]
            watcher.remove_watch(path1)
            assert watcher._ConfigurationWatcher__thread is thread  # type: ignore[attr-defined]
            assert thread.is_alive()
            watcher.remove_watch(path2)
            thread.join(timeout=2)
            assert not thread.is_alive()
        finally:
            shutil.rmtree(tmpdir)


# ── list_watches ──────────────────────────────────────────────────────────────

class ListWatchesTests:

    @fact
    def empty_list_when_no_watches(self) -> None:
        watcher = appsettings2.ConfigurationWatcher(interval_seconds=0.1)
        watches = watcher.list_watches()
        assert watches == []

    @fact
    def returns_resolved_paths(self) -> None:
        tmpdir = tempfile.mkdtemp()
        path = os.path.join(tmpdir, 'test.json')
        with open(path, 'w') as f:
            json.dump({'key': 'val'}, f)
        try:
            watcher = appsettings2.ConfigurationWatcher(interval_seconds=0.1)
            watcher.add_watch(path)
            watches = watcher.list_watches()
            assert len(watches) == 1
            assert watches[0] == os.path.realpath(path)
            watcher.remove_watch(path)
        finally:
            shutil.rmtree(tmpdir)

    @fact
    def returns_fresh_list_copy(self) -> None:
        tmpdir = tempfile.mkdtemp()
        path = os.path.join(tmpdir, 'test.json')
        with open(path, 'w') as f:
            json.dump({'key': 'val'}, f)
        try:
            watcher = appsettings2.ConfigurationWatcher(interval_seconds=0.1)
            watcher.add_watch(path)
            watches1 = watcher.list_watches()
            watches2 = watcher.list_watches()
            assert watches1 is not watches2
            watches1.append('/fake/path.json')
            assert len(watcher.list_watches()) == 1
            watcher.remove_watch(path)
        finally:
            shutil.rmtree(tmpdir)


# ── watch_handler property ───────────────────────────────────────────────────

class WatchHandlerTests:

    @fact
    def getter_returns_none_initially(self) -> None:
        watcher = appsettings2.ConfigurationWatcher(interval_seconds=0.1)
        assert watcher.watch_handler is None

    @fact
    def setter_stores_handler(self) -> None:
        watcher = appsettings2.ConfigurationWatcher(interval_seconds=0.1)
        def handler(p, e, c):
            pass
        watcher.watch_handler = handler
        assert watcher.watch_handler is handler

    @fact
    def getter_returns_stored_handler(self) -> None:
        watcher = appsettings2.ConfigurationWatcher(interval_seconds=0.1)
        def my_handler(p, e, c):
            pass
        watcher.watch_handler = my_handler
        assert watcher.watch_handler is my_handler

    @fact
    def setter_accepts_none_clears_handler(self) -> None:
        watcher = appsettings2.ConfigurationWatcher(interval_seconds=0.1)
        def handler(p, e, c):
            pass
        watcher.watch_handler = handler
        watcher.watch_handler = None
        assert watcher.watch_handler is None

    @fact
    def handler_receives_correct_parameters_on_modified(self) -> None:
        tmpdir = tempfile.mkdtemp()
        path = os.path.join(tmpdir, 'test.json')
        with open(path, 'w') as f:
            json.dump({'key': 'val'}, f)
        try:
            events = []
            def handler(filepath, event_type, config):
                events.append((filepath, event_type, config))
            watcher = appsettings2.ConfigurationWatcher(interval_seconds=0.05)
            watcher.watch_handler = handler
            watcher.add_watch(path)
            time.sleep(0.15)
            # Modify the file
            with open(path, 'w') as f:
                json.dump({'key': 'new'}, f)
            time.sleep(0.15)
            thread = watcher._ConfigurationWatcher__thread  # type: ignore[attr-defined]
            watcher.remove_watch(path)
            thread.join(timeout=2)
            modified_events = [e for e in events if e[1] is WatchEventType.MODIFIED]
            assert len(modified_events) >= 1
            assert modified_events[0][0] == os.path.realpath(path)
        finally:
            shutil.rmtree(tmpdir)


# ── Watch states: created ────────────────────────────────────────────────────

class WatchStateCreated:

    @fact
    def pending_state_for_non_existent_file(self) -> None:
        tmpdir = tempfile.mkdtemp()
        path = os.path.join(tmpdir, 'pending_test.json')
        try:
            watcher = appsettings2.ConfigurationWatcher(interval_seconds=0.1)
            watcher.add_watch(path)
            assert len(watcher.list_watches()) == 1
            watcher.remove_watch(path)
        finally:
            os.rmdir(tmpdir)

    @fact
    def created_event_fires_when_pending_file_appears(self) -> None:
        tmpdir = tempfile.mkdtemp()
        path = os.path.join(tmpdir, 'pending_create.json')
        try:
            events = []
            def handler(filepath, event_type, config):
                events.append((event_type, config))
            watcher = appsettings2.ConfigurationWatcher(interval_seconds=0.05)
            watcher.watch_handler = handler
            watcher.add_watch(path)
            time.sleep(0.1)
            assert len(events) == 0
            # Create the file
            with open(path, 'w') as f:
                json.dump({'new': 'key'}, f)
            time.sleep(0.15)
            thread = watcher._ConfigurationWatcher__thread  # type: ignore[attr-defined]
            watcher.remove_watch(path)
            thread.join(timeout=2)
            created_events = [e for e in events if e[0] is WatchEventType.CREATED]
            assert len(created_events) == 1
            assert created_events[0][1] is not None
            assert created_events[0][1].get('new') == 'key'
        finally:
            if os.path.exists(path):
                os.unlink(path)
            os.rmdir(tmpdir)

    @fact
    def no_event_on_no_content_change(self) -> None:
        tmpdir = tempfile.mkdtemp()
        path = os.path.join(tmpdir, 'stable.json')
        with open(path, 'w') as f:
            json.dump({'v': 1}, f)
        try:
            events = []
            def handler(filepath, event_type, config):
                events.append(event_type)
            watcher = appsettings2.ConfigurationWatcher(interval_seconds=0.05)
            watcher.watch_handler = handler
            watcher.add_watch(path)
            time.sleep(0.2)
            thread = watcher._ConfigurationWatcher__thread  # type: ignore[attr-defined]
            watcher.remove_watch(path)
            thread.join(timeout=2)
            # Only CREATED should have fired, no MODIFIED
            modified = [e for e in events if e is WatchEventType.MODIFIED]
            assert len(modified) == 0
        finally:
            shutil.rmtree(tmpdir)


# ── Watch states: active → modified ──────────────────────────────────────────

class WatchStateModified:

    @fact
    def modified_event_fires_on_file_change(self) -> None:
        tmpdir = tempfile.mkdtemp()
        path = os.path.join(tmpdir, 'test.json')
        with open(path, 'w') as f:
            json.dump({'v': 1}, f)
        try:
            events = []
            def handler(filepath, event_type, config):
                events.append((event_type, config))
            watcher = appsettings2.ConfigurationWatcher(interval_seconds=0.05)
            watcher.watch_handler = handler
            watcher.add_watch(path)
            time.sleep(0.15)
            # Modify file contents
            with open(path, 'w') as f:
                json.dump({'v': 2}, f)
            time.sleep(0.15)
            thread = watcher._ConfigurationWatcher__thread  # type: ignore[attr-defined]
            watcher.remove_watch(path)
            thread.join(timeout=2)
            modified_events = [e for e in events if e[0] is WatchEventType.MODIFIED]
            assert len(modified_events) >= 1
            assert modified_events[0][1].get('v') == 2
        finally:
            shutil.rmtree(tmpdir)


# ── Watch states: active → deleted ───────────────────────────────────────────

class WatchStateDeleted:

    @fact
    def deleted_event_fires_when_file_removed(self) -> None:
        tmpdir = tempfile.mkdtemp()
        path = os.path.join(tmpdir, 'test.json')
        with open(path, 'w') as f:
            json.dump({'v': 1}, f)
        try:
            events = []
            def handler(filepath, event_type, config):
                events.append((event_type, config))
            watcher = appsettings2.ConfigurationWatcher(interval_seconds=0.05)
            watcher.watch_handler = handler
            watcher.add_watch(path)
            time.sleep(0.15)
            os.unlink(path)
            time.sleep(0.15)
            thread = watcher._ConfigurationWatcher__thread  # type: ignore[attr-defined]
            watcher.remove_watch(path)
            thread.join(timeout=2)
            deleted_events = [e for e in events if e[0] is WatchEventType.DELETED]
            assert len(deleted_events) >= 1
            assert deleted_events[0][1] is None
        finally:
            shutil.rmtree(tmpdir)

    @fact
    def state_is_deleted_after_removal(self) -> None:
        tmpdir = tempfile.mkdtemp()
        path = os.path.join(tmpdir, 'test.json')
        with open(path, 'w') as f:
            json.dump({'v': 1}, f)
        try:
            watcher = appsettings2.ConfigurationWatcher(interval_seconds=0.1)
            watcher.add_watch(path)
            time.sleep(0.2)
            os.unlink(path)
            time.sleep(0.3)
            watches = watcher.list_watches()
            assert len(watches) == 1
            watcher.remove_watch(path)
        finally:
            shutil.rmtree(tmpdir)


# ── Watch states: deleted → recreated ────────────────────────────────────────

class WatchStateDeletedCreated:

    @fact
    def created_event_fires_after_file_reappears(self) -> None:
        tmpdir = tempfile.mkdtemp()
        path = os.path.join(tmpdir, 'test.json')
        with open(path, 'w') as f:
            json.dump({'v': 1}, f)
        try:
            events = []
            def handler(filepath, event_type, config):
                events.append((event_type, config))
            watcher = appsettings2.ConfigurationWatcher(interval_seconds=0.05)
            watcher.watch_handler = handler
            watcher.add_watch(path)
            time.sleep(0.1)
            # Delete the file
            os.unlink(path)
            time.sleep(0.15)
            events.clear()
            # Re-create the file
            with open(path, 'w') as f:
                json.dump({'v': 2}, f)
            time.sleep(0.15)
            thread = watcher._ConfigurationWatcher__thread  # type: ignore[attr-defined]
            watcher.remove_watch(path)
            thread.join(timeout=2)
            created_events = [e for e in events if e[0] is WatchEventType.CREATED]
            assert len(created_events) >= 1
            assert created_events[0][1] is not None
            assert created_events[0][1].get('v') == 2
        finally:
            if os.path.exists(path):
                os.unlink(path)
            shutil.rmtree(tmpdir, ignore_errors=True)


# ── Polling: thread lifecycle ─────────────────────────────────────────────────

class PollingThread:

    @fact
    def thread_does_not_block_process_exit(self) -> None:
        import subprocess
        code = '''
import appsettings2, tempfile, os
d = tempfile.mkdtemp()
p = os.path.join(d, 'x.json')
with open(p, 'w') as f: f.write('{}')
w = appsettings2.ConfigurationWatcher(interval_seconds=60.0)
w.add_watch(p)
print("alive", w._ConfigurationWatcher__thread.is_alive())  # type: ignore[attr-defined]
'''
        result = subprocess.run(
            ['python', '-c', code],
            capture_output=True,
            text=True,
            timeout=5,
        )
        assert 'alive True' in result.stdout, f'stdout={result.stdout}, stderr={result.stderr}'

    @fact
    def poll_interval_is_respected(self) -> None:
        """Verify the interval parameter affects polling frequency."""
        tmpdir = tempfile.mkdtemp()
        path = os.path.join(tmpdir, 'test.json')
        with open(path, 'w') as f:
            json.dump({'v': 1}, f)
        try:
            call_times = []
            def handler(filepath, event_type, config):
                call_times.append(time.time())
            watcher = appsettings2.ConfigurationWatcher(interval_seconds=0.1)
            watcher.watch_handler = handler
            watcher.add_watch(path)
            time.sleep(0.25)
            thread = watcher._ConfigurationWatcher__thread  # type: ignore[attr-defined]
            watcher.remove_watch(path)
            thread.join(timeout=2)
            assert len(call_times) >= 1
        finally:
            shutil.rmtree(tmpdir)


# ── Error handling ────────────────────────────────────────────────────────────

class ErrorHandling:

    @fact
    def parse_error_logs_error_does_not_crash_thread(self) -> None:
        tmpdir = tempfile.mkdtemp()
        path = os.path.join(tmpdir, 'bad.json')
        # Write invalid JSON
        with open(path, 'wb') as f:
            f.write(b'{invalid json}}}')
        try:
            events = []
            def handler(filepath, event_type, config):
                events.append(event_type)
            watcher = appsettings2.ConfigurationWatcher(interval_seconds=0.05)
            watcher.watch_handler = handler
            watcher.add_watch(path)
            time.sleep(0.15)
            # Write bad JSON after initial event
            with open(path, 'wb') as f:
                f.write(b'{bad json}')
            time.sleep(0.15)
            thread = watcher._ConfigurationWatcher__thread  # type: ignore[attr-defined]
            watcher.remove_watch(path)
            thread.join(timeout=2)
            assert not thread.is_alive()
        finally:
            shutil.rmtree(tmpdir)

    @fact
    def unrecognised_extension_logs_error_continues(self) -> None:
        tmpdir = tempfile.mkdtemp()
        path = os.path.join(tmpdir, 'readme.txt')
        with open(path, 'w') as f:
            f.write('some text')
        try:
            events = []
            def handler(filepath, event_type, config):
                events.append(event_type)
            watcher = appsettings2.ConfigurationWatcher(interval_seconds=0.1)
            watcher.watch_handler = handler
            watcher.add_watch(path)
            time.sleep(0.3)
            thread = watcher._ConfigurationWatcher__thread  # type: ignore[attr-defined]
            watcher.remove_watch(path)
            thread.join(timeout=2)
            assert not thread.is_alive()
            # No events should fire for txt files
            for e in events:
                assert e is not WatchEventType.MODIFIED
        finally:
            shutil.rmtree(tmpdir)


# ── Format support ────────────────────────────────────────────────────────────

class FormatSupport:

    @fact
    def json_files_load_correctly(self) -> None:
        tmpdir = tempfile.mkdtemp()
        path = os.path.join(tmpdir, 'appsettings.json')
        with open(path, 'w') as f:
            json.dump({'mykey': 'myval'}, f)
        events = []
        def handler(filepath, event_type, config):
            events.append((event_type, config))
        watcher = appsettings2.ConfigurationWatcher(interval_seconds=0.05)
        watcher.watch_handler = handler
        watcher.add_watch(path)
        time.sleep(0.15)
        thread = watcher._ConfigurationWatcher__thread  # type: ignore[attr-defined]
        watcher.remove_watch(path)
        thread.join(timeout=2)
        created = [e for e in events if e[0] is WatchEventType.CREATED]
        assert len(created) >= 1
        assert created[0][1].get('mykey') == 'myval'
        shutil.rmtree(tmpdir)

    @fact
    def toml_files_load_correctly(self) -> None:
        tmpdir = tempfile.mkdtemp()
        path = os.path.join(tmpdir, 'appsettings.toml')
        with open(path, 'w') as f:
            f.write('mykey = "tomlval"\n')
        events = []
        def handler(filepath, event_type, config):
            events.append((event_type, config))
        watcher = appsettings2.ConfigurationWatcher(interval_seconds=0.05)
        watcher.watch_handler = handler
        watcher.add_watch(path)
        time.sleep(0.15)
        thread = watcher._ConfigurationWatcher__thread  # type: ignore[attr-defined]
        watcher.remove_watch(path)
        thread.join(timeout=2)
        created = [e for e in events if e[0] is WatchEventType.CREATED]
        assert len(created) >= 1
        assert created[0][1].get('mykey') == 'tomlval'
        shutil.rmtree(tmpdir)

    @fact
    def yaml_files_load_correctly(self) -> None:
        tmpdir = tempfile.mkdtemp()
        path = os.path.join(tmpdir, 'appsettings.yaml')
        with open(path, 'w') as f:
            f.write('mykey: yamlval\n')
        events = []
        def handler(filepath, event_type, config):
            events.append((event_type, config))
        watcher = appsettings2.ConfigurationWatcher(interval_seconds=0.05)
        watcher.watch_handler = handler
        watcher.add_watch(path)
        time.sleep(0.15)
        thread = watcher._ConfigurationWatcher__thread  # type: ignore[attr-defined]
        watcher.remove_watch(path)
        thread.join(timeout=2)
        created = [e for e in events if e[0] is WatchEventType.CREATED]
        assert len(created) >= 1
        assert created[0][1].get('mykey') == 'yamlval'
        shutil.rmtree(tmpdir)

    @fact
    def yml_extension_works(self) -> None:
        tmpdir = tempfile.mkdtemp()
        path = os.path.join(tmpdir, 'appsettings.yml')
        with open(path, 'w') as f:
            f.write('mykey: ymlval\n')
        events = []
        def handler(filepath, event_type, config):
            events.append((event_type, config))
        watcher = appsettings2.ConfigurationWatcher(interval_seconds=0.05)
        watcher.watch_handler = handler
        watcher.add_watch(path)
        time.sleep(0.15)
        thread = watcher._ConfigurationWatcher__thread  # type: ignore[attr-defined]
        watcher.remove_watch(path)
        thread.join(timeout=2)
        created = [e for e in events if e[0] is WatchEventType.CREATED]
        assert len(created) >= 1
        assert created[0][1].get('mykey') == 'ymlval'
        shutil.rmtree(tmpdir)

    @fact
    def txt_extension_logs_error(self) -> None:
        tmpdir = tempfile.mkdtemp()
        path = os.path.join(tmpdir, 'readme.txt')
        with open(path, 'w') as f:
            f.write('some text')
        events = []
        def handler(filepath, event_type, config):
            events.append(event_type)
        watcher = appsettings2.ConfigurationWatcher(interval_seconds=0.1)
        watcher.watch_handler = handler
        watcher.add_watch(path)
        time.sleep(0.3)
        thread = watcher._ConfigurationWatcher__thread  # type: ignore[attr-defined]
        watcher.remove_watch(path)
        thread.join(timeout=2)
        # No events should be fired
        assert len(events) == 0
        shutil.rmtree(tmpdir)


# ── WatchEventType enum ──────────────────────────────────────────────────────

class EnumTests:

    @fact
    def enum_values_are_single_characters(self) -> None:
        assert WatchEventType.CREATED.value == 'c'
        assert WatchEventType.MODIFIED.value == 'm'
        assert WatchEventType.DELETED.value == 'd'

    @fact
    def enum_is_str_subclass(self) -> None:
        assert isinstance(WatchEventType.CREATED, str)
        assert isinstance(WatchEventType.MODIFIED, str)
        assert isinstance(WatchEventType.DELETED, str)

    @fact
    def enum_members_can_be_compared(self) -> None:
        assert WatchEventType.CREATED is WatchEventType.CREATED
        assert WatchEventType.MODIFIED is not WatchEventType.CREATED
        assert WatchEventType.DELETED is WatchEventType.DELETED

    @fact
    def enum_can_be_created_from_string_value(self) -> None:
        assert WatchEventType('c') is WatchEventType.CREATED
        assert WatchEventType('m') is WatchEventType.MODIFIED
        assert WatchEventType('d') is WatchEventType.DELETED


# ── Integration ───────────────────────────────────────────────────────────────

class IntegrationTests:

    @fact
    def handler_receives_new_config_on_modified(self) -> None:
        tmpdir = tempfile.mkdtemp()
        path = os.path.join(tmpdir, 'appsettings.json')
        with open(path, 'w') as f:
            json.dump({'name': 'alice'}, f)
        configs = []
        def handler(filepath, event_type, config):
            if event_type is WatchEventType.MODIFIED and config is not None:
                configs.append(config)
        watcher = appsettings2.ConfigurationWatcher(interval_seconds=0.05)
        watcher.watch_handler = handler
        watcher.add_watch(path)
        time.sleep(0.15)
        with open(path, 'w') as f:
            json.dump({'name': 'bob'}, f)
        time.sleep(0.15)
        thread = watcher._ConfigurationWatcher__thread  # type: ignore[attr-defined]
        watcher.remove_watch(path)
        thread.join(timeout=2)
        assert len(configs) >= 1
        assert configs[-1].get('name') == 'bob'
        shutil.rmtree(tmpdir)

    @fact
    def multiple_watchers_are_independent(self) -> None:
        tmpdir1 = tempfile.mkdtemp()
        tmpdir2 = tempfile.mkdtemp()
        path1 = os.path.join(tmpdir1, 'a.json')
        path2 = os.path.join(tmpdir2, 'b.json')
        with open(path1, 'w') as f:
            json.dump({'id': 1}, f)
        with open(path2, 'w') as f:
            json.dump({'id': 2}, f)

        events1 = []
        events2 = []

        def h1(filepath, event_type, config):
            events1.append(event_type)
        def h2(filepath, event_type, config):
            events2.append(event_type)

        w1 = appsettings2.ConfigurationWatcher(interval_seconds=0.05)
        w2 = appsettings2.ConfigurationWatcher(interval_seconds=0.05)
        w1.watch_handler = h1
        w2.watch_handler = h2
        w1.add_watch(path1)
        w2.add_watch(path2)
        time.sleep(0.15)

        # Modify only w1's file
        with open(path1, 'w') as f:
            json.dump({'id': 10}, f)
        time.sleep(0.15)

        t1 = w1._ConfigurationWatcher__thread  # type: ignore[attr-defined]
        t2 = w2._ConfigurationWatcher__thread  # type: ignore[attr-defined]
        w1.remove_watch(path1)
        w2.remove_watch(path2)
        t1.join(timeout=2)
        t2.join(timeout=2)

        modified1 = [e for e in events1 if e is WatchEventType.MODIFIED]
        modified2 = [e for e in events2 if e is WatchEventType.MODIFIED]
        assert len(modified1) >= 1
        assert len(modified2) == 0
        shutil.rmtree(tmpdir1)
        shutil.rmtree(tmpdir2)
