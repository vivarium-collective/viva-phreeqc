"""A general, config-driven process-bigraph wrapper over the PHREEQC engine."""
from __future__ import annotations

from engine_core import EngineProcess

from .engine import PhreeqcEngine, speciate


class PhreeqcProcess(EngineProcess):
    """Run a real PHREEQC speciation each step from a config-supplied recipe.

    ``config['recipe']`` is the speciation (data: solution / reactants / equalize /
    extract — see :func:`viva_phreeqc.engine.speciate`); ``config['inputs']`` and
    ``config['outputs']`` (from :class:`~engine_core.EngineProcess`) declare the
    ports. Input ports fill the recipe's ``"$name"`` placeholders; the extracted values
    are emitted on the output ports. A domain model that needs pre/post logic should
    instead reuse :func:`speciate` + :class:`PhreeqcEngine` directly.
    """

    config_schema = {
        **EngineProcess.config_schema,
        "database": {"_type": "string", "_default": "phreeqc.dat"},
        "database_directory": {"_type": "string", "_default": ""},
        "recipe": {"_type": "tree", "_default": {}},
    }

    def build_engine(self, config):
        return PhreeqcEngine(
            config.get("database", "phreeqc.dat"),
            config.get("database_directory") or None,
        )

    def run(self, values, interval):
        return speciate(self._engine, self.config["recipe"], values)
