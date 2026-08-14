"""Tests for diagnostic registry and functions.

Verifies load_diagnostics and sort_diagnostics_by_dependencies
using a minimal in-memory config dict (no filesystem required).
"""

import types
import unittest
from io import StringIO
from unittest.mock import patch

import yaml

from dlamp.data.registry.diagnostic_registry import (
    load_diagnostics,
    sort_diagnostics_by_dependencies,
)

_REGISTRY_DICT = {
    "registry": {
        "varname": {
            "wind_speed": {
                "function": "calc_wind_speed",
                "requires": ["U", "V"],
            },
            "kinetic_energy": {
                "function": "calc_kinetic_energy",
                "requires": ["wind_speed"],
            },
        }
    }
}
_REGISTRY_YAML = yaml.dump(_REGISTRY_DICT)


def _fake_open(*args, **kwargs):
    """Return a StringIO of the fake YAML, ignoring the path."""
    return StringIO(_REGISTRY_YAML)


def _fake_import_module(name: str) -> types.ModuleType:
    """Return a module with stub diagnostic functions."""
    mod = types.ModuleType(name)
    mod.calc_wind_speed = lambda ds: ds  # type: ignore[attr-defined]
    mod.calc_kinetic_energy = lambda ds: ds  # type: ignore[attr-defined]
    return mod


class LoadDiagnosticsTest(unittest.TestCase):
    """Tests for load_diagnostics()."""

    def _call(self) -> dict:
        with (
            patch(
                "dlamp.data.registry.diagnostic_registry.open",
                side_effect=_fake_open,
            ),
            patch(
                "dlamp.data.registry.diagnostic_registry.importlib.import_module",
                side_effect=_fake_import_module,
            ),
        ):
            return load_diagnostics("/fake/registry.yaml")

    def test_returns_dict_with_expected_keys(self) -> None:
        """load_diagnostics returns a dict keyed by variable name."""
        result = self._call()
        self.assertIn("wind_speed", result)
        self.assertIn("kinetic_energy", result)

    def test_stores_requires_field(self) -> None:
        """Each entry contains a 'requires' list."""
        result = self._call()
        self.assertEqual(result["wind_speed"]["requires"], ["U", "V"])

    def test_stores_callable_function(self) -> None:
        """Each entry's 'function' field is callable."""
        result = self._call()
        self.assertTrue(callable(result["wind_speed"]["function"]))


class SortDiagnosticsTest(unittest.TestCase):
    """Tests for sort_diagnostics_by_dependencies()."""

    def _make_diagnostics(self) -> dict:
        dummy = lambda ds: ds
        return {
            "wind_speed": {"requires": ["U", "V"], "function": dummy},
            "kinetic_energy": {"requires": ["wind_speed"], "function": dummy},
        }

    def test_dependency_before_dependent(self) -> None:
        """wind_speed must appear before kinetic_energy."""
        diags = self._make_diagnostics()
        order = sort_diagnostics_by_dependencies(diags)
        self.assertLess(
            order.index("wind_speed"),
            order.index("kinetic_energy"),
        )

    def test_returns_all_keys(self) -> None:
        """All variables appear in the sorted list."""
        diags = self._make_diagnostics()
        order = sort_diagnostics_by_dependencies(diags)
        self.assertEqual(set(order), {"wind_speed", "kinetic_energy"})


if __name__ == "__main__":
    unittest.main()
