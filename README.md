# Water Allocation Simulation

The main simulation compares three wheat irrigation systems using the same
farm properties, rainfall, canal supply, groundwater stock, and random seed:

1. **Warabandi**: fixed area-proportional rotations.
2. **Demand-based**: water is ranked by wheat demand and critical-stage need.
3. **Proposed pure-Karma system**: Farms rank by Karma bids, winners make
   proportional Karma payments, and the pool is redistributed equally across
   all farmers.

The proposed system implements the pure-Karma equations in
`context/pure_karma_wheat_allocation_with_soil_heterogeneity_and_finite_groundwater.md`.
Physical wheat behavior follows
the synchronized wheat season, stage-sensitive stress, and finite groundwater
stock described in the pure-Karma model.

The simulation uses `beta = 0.8` for every farm. Heterogeneity is limited to
farm-specific minimum and maximum soil-moisture bounds; all crops start at the
same time and use the same initial relative moisture.

The groundwater pumping cost uses `C_g = 0.10 PKR` per unit, matching the
original demand-based paper. Drawdown increases this cost using the optional
time-varying factor described in the realistic wheat extension.

## Run

Compare all three systems:

```bash
python simulate.py
```

Run one system:

```bash
python simulate.py --mechanism proposed
python simulate.py --mechanism demand
python simulate.py --mechanism warabandi
```

Options:

```text
--num-farmers   Number of wheat farms
--weeks         Wheat-season decision intervals
--canal-supply  Average canal supply depth in mm/week (default: 30)
--seed          Shared random seed
The simulation fixes `beta = 0.8` for all farms; it is not a CLI option.
```

The comparison reports social cost, social welfare, groundwater cost and use,
and cumulative unmet demand for all three systems. Social cost includes
groundwater cost, unmet demand, and moisture stress.
