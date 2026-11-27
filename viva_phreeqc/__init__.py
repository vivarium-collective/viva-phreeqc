"""viva-phreeqc — the genuine USGS PHREEQC (IPhreeqc) engine as a reusable,
config-driven process-bigraph bridge.

Use ``PhreeqcProcess`` for a config-only speciation, or reuse ``PhreeqcEngine`` +
``speciate(engine, recipe, values)`` from a domain process that keeps its own
pre/post logic.
"""
from .engine import PhreeqcEngine, speciate  # noqa: F401
from .processes import PhreeqcProcess  # noqa: F401

__all__ = ["PhreeqcEngine", "speciate", "PhreeqcProcess"]
