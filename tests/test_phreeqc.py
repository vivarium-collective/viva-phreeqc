"""Smoke tests for the config-driven PHREEQC bridge (stock phreeqc.dat)."""
import pytest

pytest.importorskip("phreeqpython")
from viva_phreeqc import PhreeqcEngine, speciate, PhreeqcProcess  # noqa: E402


def _recipe():
    # A database-agnostic speciation: NaCl at 25 C; read pH + total Na + a guarded SI.
    return {
        "solution": {"units": "mol/kgw", "temp": 25.0, "pH": 7.0, "Na": "$na", "Cl": 0.1},
        "extract": {"pH": {"pH": True}, "pe": {"pe": True}, "Na": {"total": "Na"},
                    "si_halite": {"si": "Halite", "default": 0.0}},
    }


def test_speciate_runs_real_phreeqc():
    out = speciate(PhreeqcEngine(), _recipe(), {"na": 0.1})
    assert 5.0 < out["pH"] < 9.0          # ~neutral NaCl
    assert out["Na"] > 0.0                 # total Na reported (phreeqpython total() is mmol/kgw)
    assert isinstance(out["si_halite"], float)   # guarded SI returns a number even if absent


def test_speciate_placeholder_substitution():
    eng = PhreeqcEngine()
    assert speciate(eng, _recipe(), {"na": 0.5})["Na"] > speciate(eng, _recipe(), {"na": 0.01})["Na"]


def test_process_is_configured():
    # The general process declares its ports from config (no engine run needed).
    assert "recipe" in PhreeqcProcess.config_schema
