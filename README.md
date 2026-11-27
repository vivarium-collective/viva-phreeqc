# viva-phreeqc

The genuine **USGS PHREEQC** geochemical engine (IPhreeqc, via `phreeqpython`) as a
reusable, config-driven [process-bigraph](https://github.com/vivarium-collective/process-bigraph)
bridge — one engine every workspace reuses instead of embedding `phreeqpython` calls in
a domain process.

## Use it two ways

**1. As a config-only process** — the chemistry is data:
```python
from viva_phreeqc import PhreeqcProcess
p = PhreeqcProcess(config={
    "database": "llnl.dat", "database_directory": "<dir with llnl.dat>",
    "recipe": {                      # a speciation, as data
        "solution": {"units": "mol/kgw", "temp": "$temp_c", "pH": 6.5, "C(4)": "$dic"},
        "reactants": [{"phase": "Forsterite", "extent": "$moles", "factor": 0.75}],
        "equalize": {"phases": ["Chrysotile", "Brucite"], "targets": [0, 0]},
        "extract": {"H2": {"species": "H2"}, "pH": {"pH": True}},
    },
    "inputs":  {"temp_c": {"_type": "float"}, "dic": {"_type": "float"}, "moles": {"_type": "float"}},
    "outputs": {"H2": {"_type": "float"}, "pH": {"_type": "float"}},
}, core=core)
```

**2. As a reusable engine + recipe** — when a domain model needs its own pre/post logic
(drivers, flux geometry, derived heat), keep that logic in your process and reuse the engine:
```python
from viva_phreeqc import PhreeqcEngine, speciate
eng = PhreeqcEngine("llnl.dat", database_directory="<dir>")
out = speciate(eng, recipe, {"temp_c": 50.0, "moles": 0.09, "dic": 2e-3})
```

The **recipe** is plain data: `solution` (→ `add_solution`, with `"$port"` placeholders),
`reactants` (phases added by `extent × factor`), `equalize` (phases/targets), and
`extract` (`species` / `pH` / `pe` / `si` / `total` → named outputs).

Reproducibility: pin `viva-phreeqc` by tag; a consumer's run-env capture records the exact
version that produced each result.
