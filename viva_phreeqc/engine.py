"""The genuine USGS PHREEQC (IPhreeqc) engine, driven by a config-supplied recipe.

One general bridge every workspace can reuse instead of embedding phreeqpython calls
in a domain process. A *recipe* is plain data (a dict / YAML) describing a PHREEQC
speciation — the aqueous solution, optional reactant phases to add, phases to
equilibrate against, and what to read back — so a domain model supplies the chemistry
as config and this module runs the real engine.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any


class PhreeqcEngine:
    """A reused PhreeqPython (IPhreeqc) instance bound to a thermodynamic database.

    ``database_directory`` lets a workspace ship its own database (e.g. an LLNL
    table with the Fe-redox / H2 machinery the stock wheel lacks).
    """

    def __init__(self, database: str = "phreeqc.dat", database_directory: str | None = None):
        self._database = database
        self._database_directory = database_directory
        self._pp = None

    @property
    def pp(self):
        if self._pp is None:
            from phreeqpython import PhreeqPython  # lazy — the real IPhreeqc bridge
            kw = {"database": self._database}
            if self._database_directory is not None:
                kw["database_directory"] = Path(self._database_directory)
            self._pp = PhreeqPython(**kw)
        return self._pp


def _resolve(v: Any, values: dict):
    """Substitute a ``"$name"`` placeholder from ``values``; pass anything else through."""
    if isinstance(v, str) and v.startswith("$"):
        return values[v[1:]]
    return v


def speciate(engine: PhreeqcEngine, recipe: dict, values: dict | None = None) -> dict:
    """Run ONE real PHREEQC speciation from ``recipe`` and return the extracted outputs.

    recipe keys:
      solution:  dict passed to ``add_solution`` (values may be ``"$port"`` placeholders)
      reactants: list of ``{phase, amount|extent, factor?, units?}`` added via ``sol.add``
                 (``extent`` is a placeholder scaled by ``factor``; skipped when <= 0)
      equalize:  ``{phases: [...], targets: [...]}`` for ``sol.equalize``
      extract:   ``{out_name: spec}`` where spec is one of
                 ``{species: "H2"}`` | ``{pH: true}`` | ``{pe: true}`` |
                 ``{si: "Calcite", default: 0.0}`` | ``{total: "charge"}``
    """
    values = values or {}
    pp = engine.pp
    sol_spec = {k: _resolve(v, values) for k, v in recipe["solution"].items()}
    sol = pp.add_solution(sol_spec)
    try:
        for r in recipe.get("reactants", []):
            if "extent" in r:
                amount = float(_resolve(r["extent"], values)) * float(r.get("factor", 1.0))
            else:
                amount = float(_resolve(r["amount"], values))
            if amount > 0.0:
                sol.add(r["phase"], amount, r.get("units", "mol"))
        eq = recipe.get("equalize")
        if eq and any(float(_resolve(r.get("extent", r.get("amount", 0)), values) or 0) > 0
                      for r in recipe.get("reactants", [])):
            sol.equalize(list(eq["phases"]), list(eq["targets"]))
        out = {}
        sp = sol.species
        for name, spec in recipe["extract"].items():
            if "species" in spec:
                out[name] = float(sp.get(spec["species"], 0.0))
            elif spec.get("pH"):
                out[name] = float(sol.pH)
            elif spec.get("pe"):
                out[name] = float(sol.pe)
            elif "total" in spec:
                out[name] = float(sol.total(spec["total"]))
            elif "si" in spec:
                try:
                    out[name] = float(sol.si(spec["si"]))
                except Exception:
                    out[name] = float(spec.get("default", 0.0))
        return out
    finally:
        sol.forget()  # release the PHREEQC solution slot (avoid a leak over a long run)
