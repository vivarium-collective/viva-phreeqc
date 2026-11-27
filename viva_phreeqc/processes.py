"""A general, config-driven process-bigraph wrapper over the PHREEQC engine."""
from __future__ import annotations

from process_bigraph import Process

from .engine import PhreeqcEngine, speciate


class PhreeqcProcess(Process):
    """Run a real PHREEQC speciation each step from a config-supplied recipe.

    ``config['recipe']`` is the speciation (data: solution / reactants / equalize /
    extract — see :func:`viva_phreeqc.engine.speciate`); ``config['inputs']`` and
    ``config['outputs']`` declare the ports (``{name: <pbg type dict>}``). Input ports
    fill the recipe's ``"$name"`` placeholders; the extracted values are emitted on the
    output ports. A domain model that needs pre/post logic (drivers, flux geometry,
    derived heat) should instead reuse :func:`speciate` + :class:`PhreeqcEngine`
    directly and keep that logic in its own process.
    """

    config_schema = {
        "database": {"_type": "string", "_default": "phreeqc.dat"},
        "database_directory": {"_type": "string", "_default": ""},
        "recipe": {"_type": "tree", "_default": {}},
        "inputs": {"_type": "tree", "_default": {}},
        "outputs": {"_type": "tree", "_default": {}},
    }

    def __init__(self, config=None, core=None):
        super().__init__(config=config, core=core)
        self._engine = PhreeqcEngine(
            self.config.get("database", "phreeqc.dat"),
            self.config.get("database_directory") or None,
        )

    def inputs(self):
        return dict(self.config.get("inputs") or {})

    def outputs(self):
        return dict(self.config.get("outputs") or {})

    def update(self, state, interval):
        ports = self.config.get("inputs") or {}
        values = {k: state[k] for k in ports if k in state}
        return speciate(self._engine, self.config["recipe"], values)
