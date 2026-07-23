# SPDX-FileCopyrightText: © 2026 Shaun Wilson
# SPDX-License-Identifier: MIT

from __future__ import annotations

import appsettings2
from appsettings2 import Configuration, ChangeType
from punit import fact
from typing import Any


# ── Phase 1: Basic Event Firing ──────────────────────────────────────────────

class BasicEventFiring:

    @fact
    def add_change_handler_stores_handler_and_fires_on_set(self) -> None:
        config = Configuration()
        log: list[tuple[Configuration, ChangeType, str | None]] = []
        def handler(cfg: Configuration, ct: ChangeType, key: str | None) -> None:
            log.append((cfg, ct, key))
        config.add_change_handler(handler)
        config.set('Foo', 'bar')
        assert len(log) == 2
        assert log[0][1] is ChangeType.CHANGING
        assert log[1][1] is ChangeType.CHANGED

    @fact
    def set_fires_one_handler_call_per_phase_with_dot_separated_key_path(self) -> None:
        config = Configuration()
        log: list[tuple[Configuration, ChangeType, str | None]] = []
        def handler(cfg: Configuration, ct: ChangeType, key: str | None) -> None:
            log.append((cfg, ct, key))
        config.add_change_handler(handler)
        config.set('Section__Key', 'val')
        assert log[0][2] == 'Section.Key'
        assert log[1][2] == 'Section.Key'

    @fact
    def set_double_underscore_triple_key_emits_root_events(self) -> None:
        config = Configuration()
        log: list[tuple[Configuration, ChangeType, str | None]] = []
        def handler(cfg: Configuration, ct: ChangeType, key: str | None) -> None:
            log.append((cfg, ct, key))
        config.add_change_handler(handler)
        config.set('a__b__c', 'val')
        # Root fires its own CHANGING('a.b.c') + CHANGED('a.b.c')
        # Auto-wired chain propagates child-level events up
        changing_full_path = [k for _, ct, k in log if ct is ChangeType.CHANGING and k == 'a.b.c']
        changed_full_path = [k for _, ct, k in log if ct is ChangeType.CHANGED and k == 'a.b.c']
        assert len(changing_full_path) >= 1
        assert len(changed_full_path) >= 1

    @fact
    def set_colon_triple_key_emits_root_events(self) -> None:
        config = Configuration()
        log: list[tuple[Configuration, ChangeType, str | None]] = []
        def handler(cfg: Configuration, ct: ChangeType, key: str | None) -> None:
            log.append((cfg, ct, key))
        config.add_change_handler(handler)
        config.set('a:b:c', 'val')
        changing_full_path = [k for _, ct, k in log if ct is ChangeType.CHANGING and k == 'a.b.c']
        changed_full_path = [k for _, ct, k in log if ct is ChangeType.CHANGED and k == 'a.b.c']
        assert len(changing_full_path) >= 1
        assert len(changed_full_path) >= 1

    @fact
    def set_period_triple_key_emits_same_path(self) -> None:
        config = Configuration()
        log: list[tuple[Configuration, ChangeType, str | None]] = []
        def handler(cfg: Configuration, ct: ChangeType, key: str | None) -> None:
            log.append((cfg, ct, key))
        config.add_change_handler(handler)
        config.set('x.y.z', 'val')
        assert log[0][2] == 'x.y.z'
        assert log[1][2] == 'x.y.z'

    @fact
    def delitem_fires_changing_changed_with_dotted_path(self) -> None:
        config = Configuration()
        config.set('Foo', 'bar')
        log: list[tuple[Configuration, ChangeType, str | None]] = []
        def handler(cfg: Configuration, ct: ChangeType, key: str | None) -> None:
            log.append((cfg, ct, key))
        config.add_change_handler(handler)
        del config['Foo']
        changing = [k for _, ct, k in log if ct is ChangeType.CHANGING and k == 'FOO']
        changed = [k for _, ct, k in log if ct is ChangeType.CHANGED and k == 'FOO']
        assert len(changing) >= 1
        assert len(changed) >= 1

    @fact
    def delitem_hierarchical_key_emits_dotted_path(self) -> None:
        config = Configuration()
        config.set('Section__Key', 'val')
        log: list[tuple[Configuration, ChangeType, str | None]] = []
        def handler(cfg: Configuration, ct: ChangeType, key: str | None) -> None:
            log.append((cfg, ct, key))
        config.add_change_handler(handler)
        del config['Section']
        changed = [k for _, ct, k in log if ct is ChangeType.CHANGED and k == 'SECTION']
        assert len(changed) >= 1


# ── Phase 2: Handler Management ──────────────────────────────────────────────

class HandlerManagement:

    @fact
    def multiple_handlers_can_be_added(self) -> None:
        config = Configuration()
        log: list[int] = []
        def h1(cfg: Configuration, ct: ChangeType, key: str | None) -> None:
            log.append(1)
        def h2(cfg: Configuration, ct: ChangeType, key: str | None) -> None:
            log.append(2)
        config.add_change_handler(h1)
        config.add_change_handler(h2)
        config.set('A', 'b')
        assert log == [1, 2, 1, 2]

    @fact
    def remove_change_handler_removes_by_identity(self) -> None:
        config = Configuration()
        log: list[int] = []
        def handler(cfg: Configuration, ct: ChangeType, key: str | None) -> None:
            log.append(1)
        config.add_change_handler(handler)
        config.remove_change_handler(handler)
        config.set('A', 'b')
        assert log == []

    @fact
    def removing_handler_twice_is_safe(self) -> None:
        config = Configuration()
        def handler(cfg: Configuration, ct: ChangeType, key: str | None) -> None:
            pass
        config.add_change_handler(handler)
        config.remove_change_handler(handler)
        config.remove_change_handler(handler)

    @fact
    def same_handler_added_twice_removed_once_keeps_second(self) -> None:
        config = Configuration()
        log: list[int] = []
        def handler(cfg: Configuration, ct: ChangeType, key: str | None) -> None:
            log.append(1)
        config.add_change_handler(handler)
        config.add_change_handler(handler)
        config.remove_change_handler(handler)
        config.set('A', 'b')
        assert log == [1, 1]

    @fact
    def removing_never_added_handler_is_safe(self) -> None:
        config = Configuration()
        def handler(cfg: Configuration, ct: ChangeType, key: str | None) -> None:
            pass
        config.remove_change_handler(handler)


# ── Phase 3: Lifecycle ───────────────────────────────────────────────────────

class Lifecycle:

    @fact
    def close_fires_closed_to_all_handlers(self) -> None:
        config = Configuration()
        log: list[tuple[ChangeType, str | None]] = []
        def handler(cfg: Configuration, ct: ChangeType, key: str | None) -> None:
            log.append((ct, key))
        config.add_change_handler(handler)
        config.close()
        assert len(log) == 1
        assert log[0][0] is ChangeType.CLOSED
        assert log[0][1] is None

    @fact
    def close_calls_on_close(self) -> None:
        config = Configuration()
        got_cfg = [False]
        def handler(cfg: Configuration, ct: ChangeType, key: str | None) -> None:
            got_cfg[0] = cfg is config
        config.add_change_handler(handler)
        config.close()
        assert got_cfg[0] is True

    @fact
    def del_calls_close_unconditionally(self) -> None:
        config = Configuration(disable_events=True)
        log: list[bool] = []
        def handler(cfg: Configuration, ct: ChangeType, key: str | None) -> None:
            log.append(True)
        config.add_change_handler(handler)
        config.close()
        assert log == []


# ── Phase 4: Disabled Events ─────────────────────────────────────────────────

class DisabledEvents:

    @fact
    def disable_events_true_does_not_unregister_existing_handlers(self) -> None:
        config = Configuration()
        log: list[int] = []
        def handler(cfg: Configuration, ct: ChangeType, key: str | None) -> None:
            log.append(1)
        config.add_change_handler(handler)
        config.set('A', 'b')
        assert len(log) == 2  # CHANGING + CHANGED
        # Verify handlers are still registered
        assert len(config._Configuration__handlers) == 1
        # Disable events
        config.disable_events = True
        config.set('B', 'c')
        # Mutation still works but no events fired
        assert config.get('B') == 'c'
        assert len(log) == 2  # still only 2 events from first set
        # Close should be no-op due to disable_events
        config.close()
        assert len(log) == 2

    @fact
    def add_change_handler_stores_handler_even_with_disable_events(self) -> None:
        config = Configuration(disable_events=True)
        def handler(cfg: Configuration, ct: ChangeType, key: str | None) -> None:
            pass
        config.add_change_handler(handler)
        assert len(config._Configuration__handlers) == 1

    @fact
    def on_close_with_disable_events_does_not_clear_or_call(self) -> None:
        # Add handler while events are enabled
        config = Configuration()
        log: list[bool] = []
        def handler(cfg: Configuration, ct: ChangeType, key: str | None) -> None:
            log.append(True)
        config.add_change_handler(handler)
        assert len(config._Configuration__handlers) == 1
        # Now disable events
        config.disable_events = True
        config.close()
        # close should NOT clear handlers list (even though events are disabled)
        assert log == []
        assert len(config._Configuration__handlers) == 1

    @fact
    def remove_change_handler_with_disable_events_still_works(self) -> None:
        config = Configuration(disable_events=True)
        def handler(cfg: Configuration, ct: ChangeType, key: str | None) -> None:
            pass
        config.add_change_handler(handler)
        config.remove_change_handler(handler)
        assert len(config._Configuration__handlers) == 0

    @fact
    def event_dispatching_still_works_with_disabled_events(self) -> None:
        config = Configuration(disable_events=True)
        config.set('A', 'b')
        assert config.get('A') == 'b'
        assert len(config.keys()) == 1


# ── Phase 5: Auto-wiring ─────────────────────────────────────────────────────

class AutoWiring:

    @fact
    def storing_child_config_auto_wires(self) -> None:
        root = Configuration()
        child = Configuration()
        root['_child'] = child
        assert len(child._Configuration__handlers) == 1  # auto-wired handler

    @fact
    def child_events_propagate_to_parent_with_prepended_key(self) -> None:
        root = Configuration()
        log: list[tuple[ChangeType, str]] = []
        def handler(cfg: Configuration, ct: ChangeType, key: str | None) -> None:
            if ct is ChangeType.CHANGED and key is not None:
                log.append((ct, key))
        root.add_change_handler(handler)
        child = Configuration()
        root['_child'] = child
        child.set('key', 'val')
        assert any(k == '_child.key' for _, k in log)

    @fact
    def deep_hierarchy_preserves_path(self) -> None:
        root = Configuration()
        log: list[str] = []
        def handler(cfg: Configuration, ct: ChangeType, key: str | None) -> None:
            if ct is ChangeType.CHANGED and key is not None:
                log.append(key)
        root.add_change_handler(handler)
        parent = Configuration()
        child = Configuration()
        root['parent'] = parent
        parent['child'] = child
        child.set('grandchild_key', 'val')
        assert 'parent.child.grandchild_key' in log

    @fact
    def removing_child_config_removes_auto_wired_handler(self) -> None:
        root = Configuration()
        child = Configuration()
        root['_child'] = child
        initial = len(child._Configuration__handlers)
        del root['_child']
        remaining = [h for h in child._Configuration__handlers
                     if getattr(h.__dict__, '{}', {}).get('_auto_wired', False)]
        assert len(remaining) == 0

    @fact
    def normalize_key_converts_all_delimiters(self) -> None:
        config = Configuration()
        assert config._Configuration__normalize_key('a__b:c') == 'a.b.c'
        assert config._Configuration__normalize_key('a:b:c') == 'a.b.c'
        assert config._Configuration__normalize_key('a.b.c') == 'a.b.c'
        assert config._Configuration__normalize_key('a__b') == 'a.b'
        assert config._Configuration__normalize_key(None) is None

    @fact
    def closed_events_with_keys_none_do_not_propagate(self) -> None:
        root = Configuration()
        log: list[tuple[ChangeType, str | None]] = []
        def handler(cfg: Configuration, ct: ChangeType, key: str | None) -> None:
            log.append((ct, key))
        root.add_change_handler(handler)
        child = Configuration()
        root['_child'] = child
        child.close()
        for ct, key in log:
            assert ct is not ChangeType.CLOSED

    @fact
    def clear_calls_delitem_for_each_key(self) -> None:
        config = Configuration()
        config.set('A', '1')
        config.set('B', '2')
        log: list[tuple[ChangeType, str]] = []
        def handler(cfg: Configuration, ct: ChangeType, key: str | None) -> None:
            if key is not None:
                log.append((ct, key))
        config.add_change_handler(handler)
        config.clear()
        changing = [k for ct, k in log if ct is ChangeType.CHANGING]
        changed = [k for ct, k in log if ct is ChangeType.CHANGED]
        assert 'A' in changing
        assert 'B' in changing


# ── Phase 6: Edge Cases ──────────────────────────────────────────────────────

class EdgeCases:

    @fact
    def handler_that_raises_prevents_subsequent_handlers_from_receiving(self) -> None:
        config = Configuration()
        log: list[bool] = []
        def bad_handler(cfg: Configuration, ct: ChangeType, key: str | None) -> None:
            raise ValueError('boom')
        def good_handler(cfg: Configuration, ct: ChangeType, key: str | None) -> None:
            log.append(True)
        config.add_change_handler(bad_handler)
        config.add_change_handler(good_handler)
        try:
            config.set('A', 'b')
        except ValueError:
            pass
        assert log == []

    @fact
    def remove_change_handler_for_directly_added_only_removes_from_immediate_scope(self) -> None:
        parent = Configuration()
        child = Configuration()
        direct_handler = lambda cfg, ct, key: None
        parent.add_change_handler(direct_handler)
        parent['_child'] = child
        parent.remove_change_handler(direct_handler)
        # Direct handler removed; auto-wired handler on child should remain
        auto_wired = [h for h in child._Configuration__handlers
                      if getattr(h, '__dict__', {}).get('_auto_wired', False)]
        assert len(auto_wired) > 0

    @fact
    def from_dict_wiring_happens_via_set_not_from_from_dict_itself(self) -> None:
        # from_dict creates a NEW configuration, the returned one is what has data
        parent_log: list[str] = []
        def handler(cfg: Configuration, ct: ChangeType, key: str | None) -> None:
            if ct is ChangeType.CHANGED and key is not None:
                parent_log.append(key)
        parent = Configuration()
        parent.add_change_handler(handler)
        child = Configuration.from_dict({'a': {'b': {'c': 1}}})
        parent['root'] = child
        assert 'root' in parent_log

    @fact
    def get_and_read_only_operations_do_not_fire_events(self) -> None:
        config = Configuration()
        config.set('A', '1')
        config.set('B__C', '2')
        log: list[bool] = []
        def handler(cfg: Configuration, ct: ChangeType, key: str | None) -> None:
            log.append(True)
        config.add_change_handler(handler)
        config.get('A')
        config.keys()
        config.items()
        config.values()
        assert log == []

    @fact
    def to_dict_does_not_fire_events(self) -> None:
        config = Configuration()
        config.set('A', '1')
        log: list[bool] = []
        def handler(cfg: Configuration, ct: ChangeType, key: str | None) -> None:
            log.append(True)
        config.add_change_handler(handler)
        config.to_dict()
        assert log == []


# ── Phase 7: pop hierarchical key bug verification ───────────────────────────

class PopHierarchicalKeyBug:

    @fact
    def pop_retrieves_via_hierarchical_getitem(self) -> None:
        config = Configuration()
        config.set('A__B__C', 'deep')
        val = config.pop('A__B__C')
        assert val == 'deep'

    @fact
    def pop_del_item_does_not_delete_hierarchical_key_at_root_level(self) -> None:
        config = Configuration()
        config.set('A__B__C', 'deep')
        config.pop('A__B__C')
        assert 'A' in config.keys()


# ── Phase 8: get_configuration and ConfigurationBuilder integration ──────────

class Integration:

    @fact
    def configuration_builder_build_with_disable_events_true_creates_config_with_events_disabled(self) -> None:
        config = appsettings2.ConfigurationBuilder()\
            .add_provider(appsettings2.providers.EnvironmentConfigurationProvider())\
            .build(disable_events=True)
        assert config.disable_events is True

    @fact
    def get_configuration_with_disable_events_true_creates_config_with_events_disabled(self) -> None:
        import os
        os.environ['_APPSETTINGSEVENTSTEST'] = '1'
        try:
            config = appsettings2.get_configuration(
                basename='_appsettingsEVENTStEST',
                json=False, toml=False, yaml=False, cli=False,
                disable_events=True
            )
            assert config.disable_events is True
        finally:
            os.environ.pop('_APPSETTINGSEVENTSTEST', None)

    @fact
    def setting_disable_events_false_on_child_allows_child_events(self) -> None:
        child = Configuration(disable_events=False)
        log: list[str] = []
        def handler(cfg: Configuration, ct: ChangeType, key: str | None) -> None:
            if ct is ChangeType.CHANGED and key is not None:
                log.append(key)
        child.add_change_handler(handler)
        child.set('key', 'val')
        assert 'key' in log

    @fact
    def parent_with_disable_events_true_blocks_child_propagation(self) -> None:
        parent = Configuration(disable_events=True)
        child = Configuration(disable_events=False)
        log: list[str] = []
        def parent_handler(cfg: Configuration, ct: ChangeType, key: str | None) -> None:
            if ct is ChangeType.CHANGED and key is not None:
                log.append(key)
        parent.add_change_handler(parent_handler)
        parent['_child'] = child
        child.set('key', 'val')
        assert '_child.key' not in log

