# Water Allocation Simulation

The main simulation compares three wheat irrigation systems using the same
farm properties, rainfall, canal supply, groundwater stock, and random seed:

1. **Warabandi**: fixed area-proportional rotations.
2. **Demand-based**: water is ranked by wheat demand and critical-stage need.
3. **Proposed Karma system**: Karma bids score social value, and winners make
   proportional Karma payments redistributed equally across all farmers.

The proposed system implements the PBS equations in
`context/karma_bid_payment_and_societal_redistribution_mechanism.md`.
Physical wheat behavior follows
`context/realistic_wheat_simulation_extensions.md`, including staggered sowing,
harvest shutoff, stage-sensitive stress, and a finite groundwater stock.

The simulation applies one irrigation efficiency percentage to every farm.
The implementation converts it to application loss with:

```text
beta_n = 100 / irrigation_efficiency_percent_n
```

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
--efficiency    Irrigation efficiency percentage x (default: 80)
```

The implementation converts efficiency to the paper's coefficient:

```text
beta = 100 / x
```

For example, `--efficiency 70` gives `beta = 1.428571`, and
`--efficiency 100` gives `beta = 1.0`.

The comparison reports social welfare, groundwater cost and use, cumulative
unmet demand, and water-received Gini inequality.
