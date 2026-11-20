```markdown
# Karma-Based Water Allocation Simulation

## Overview

This project is a **discrete-time, agent-based simulation** of irrigation water allocation for wheat cultivation in the Punjab canal commands of Pakistan. It extends the demand-based allocation framework of **Hassan et al. (2021)** by introducing a **Karma-based allocation mechanism** and comparing it against two baselines:

1. **Warabandi** — the traditional area-proportional rotational schedule used in Pakistan's Indus Basin Irrigation System.
2. **Demand-based (Social Welfare)** — the VCG-inspired mechanism from Hassan et al. that ranks farmers by marginal social value.
3. **Proposed (Karma)** — a novel mechanism where farmers bid Karma points (earned through past cooperation) to prioritize water during scarcity.

The simulation tracks **soil moisture dynamics**, **groundwater depletion**, **crop stress**, and **social welfare** over a 17-week wheat season to evaluate which mechanism best balances equity, efficiency, and aquifer sustainability.

---

## Project Context

- **Course Project** extending the demand-based water allocation paper with a Karma mechanism.
- **Geographic focus**: Punjab, Pakistan (Punjab loam/silty-clay-loam soils, Nov–Apr wheat season).
- **Research angle**: Can a reputation-based (Karma) mechanism outperform both rigid rotation and pure welfare maximization when groundwater is a shared commons?

---

## Architecture & File Breakdown

The codebase follows a **modular design** where the core physics engine is decoupled from the allocation logic.

```text
simulate.py          ← CLI entry point (Root directory)
└── simulate/        ← Core simulation package
    ├── __init__.py
    ├── run.py              ← Simulation engine (physics, accounting, weekly loop)
    ├── soil_moisture.py    ← FAO-56 soil-water bucket model & crop parameters
    ├── warabandi.py        ← Warabandi mechanism (turn schedule & allocation)
    ├── demand.py           ← Hassan et al. demand equations & social valuation
    └── proposed.py         ← Proposed Karma mechanism & social welfare allocator
```

### Detailed File Descriptions

#### `simulate.py` (Root)
The command-line interface (CLI) entry point. It uses `argparse` to accept simulation parameters (`--num-farmers`, `--weeks`, `--canal-supply`, `--seed`, `--mechanism`). It iterates through the selected mechanisms, calls the simulation engine, and prints a formatted comparison table of key metrics (Social cost, Welfare, Groundwater cost, Groundwater used, Unmet demand).

#### `simulate/run.py`
The core simulation engine. It is responsible for:
- **Initialization**: Setting up heterogeneous farmers (randomized area, soil thresholds, pump capacities), the aquifer, and initial Karma scores.
- **Weekly Loop**: For each week, it generates weather (rainfall), calculates crop age/root depth, and computes physical water demand.
- **Delegation**: Routes the canal supply to the chosen allocation mechanism (`warabandi`, `demand`, or `proposed`).
- **Groundwater Pumping**: Calculates unmet demand after surface allocation and simulates tubewell pumping, constrained by pump capacity and aquifer availability.
- **Soil & Aquifer Dynamics**: Updates soil moisture (theta) based on losses (ET, percolation) and gains (irrigation, rain), and updates the groundwater stock based on pumping and recharge.
- **Accounting**: Tracks cumulative social cost, social welfare, and groundwater costs over the season.

#### `simulate/soil_moisture.py`
Defines the `SoilMoistureModel` dataclass, which encapsulates the physical and agronomic parameters of the wheat crop and soil. It includes:
- **Crop Coefficients ($K_c$)**: Implements the FAO-56 four-stage wheat growth curve (initial, development, mid-season, late).
- **Dynamic Root Depth**: Calculates effective root depth based on crop age (growing from 200mm to 800mm).
- **Stress Weights**: Defines yield sensitivity to moisture stress during critical growth stages (e.g., higher weight during flowering/grain filling).
- **Soil Update (`update` method)**: Applies the discrete water-balance equation, handling percolation decay, evapotranspiration, and irrigation application efficiency ($\beta$).

#### `simulate/warabandi.py`
Implements the traditional **Warabandi** rotational system.
- `calculate_turn_schedule`: Computes the weekly turn hours for each farmer strictly proportional to their land area, accounting for canal filling/draining delays.
- `allocate_warabandi`: Allocates water based on the fixed turn hours and the canal's discharge rate. Water is delivered regardless of the farmer's actual soil moisture deficit, leading to potential runoff if the soil is already wet.

#### `simulate/demand.py`
Implements the mathematical foundation from **Hassan et al. (2021)**.
- `calculate_demand`: Computes physical water demand (Eq. 4) based on the deficit to field capacity, scaled by the irrigation efficiency coefficient $\beta$.
- `calculate_monetary_willingness` & `calculate_willingness_to_pay`: Implements Eq. 6 and 7 for VCG-style bidding.
- `calculate_social_value`: A project extension that calculates a per-farm welfare weight combining the avoided cost of groundwater with a normalized moisture-stress urgency.

#### `simulate/proposed.py`
Contains the allocation algorithms for the **Demand-based** and **Proposed Karma** mechanisms.
- `allocate_social_welfare`: Solves the linear welfare problem by ranking farmers by their marginal social value and allocating water greedily until the canal supply is exhausted.
- `allocate_karma`: Implements the proposed reputation-based mechanism. Farmers bid a fraction of their Karma weighted by their urgency. Allocation is prioritized by (bid, urgency). The paid Karma is pooled and redistributed equally among all farmers (with a rotating starting index to ensure fairness over time), creating a self-enforcing social contract.

---

## The Three Mechanisms

### 1. Warabandi
The **status quo**. Each farmer receives a fixed weekly turn proportional to their land area:
$$T_n = \frac{168 - \sum T_{fill} + \sum T_{drain}}{A_{command}} \cdot A_n + T_{fill,n} - T_{drain,n}$$
Water is delivered on a rigid schedule regardless of crop need.

### 2. Demand-based (Social Welfare)
Based on **Hassan et al. (2021)**. Farmers report demand:
$$d_n = \beta \cdot (\theta_{max,n} - \theta_n) \cdot A_n \cdot l_n$$
where $\beta = 100 / \text{efficiency}$ (e.g., $\beta = 1.25$ for 80% efficiency). Allocation maximizes social welfare by ranking farmers by marginal value.

### 3. Proposed Karma
A **reputation-based** mechanism. Each farmer starts with 10 Karma points. Each week:
1. Farmers compute **urgency** from soil moisture deficit and crop stage:
   $$u_n = w_{stage} \cdot \frac{\theta_{max} - \theta}{\theta_{max} - \theta_{min}}$$
2. They bid up to 30% of their Karma, weighted by urgency.
3. Allocation is prioritized by (bid, urgency).
4. Paid Karma is **pooled and redistributed equally** to reward cooperation.

---

## Soil Moisture Model

A **weekly FAO-56 bucket model** tracking volumetric soil moisture ($\theta$):

| Component | Formulation |
|---|---|
| Root depth | Dynamic: $L_t = 800 \cdot \min(1, \max(0.25, \text{age}/8))$ mm |
| Crop coefficient $K_c$ | 4-stage wheat curve (initial 0.3 → development ramp → mid 1.15 → late decline) |
| Reference ET $ET_0$ | $15 + 15 \cdot \text{week}/\text{total}$ mm/week (seasonal ramp) |
| Percolation | Exponential decay: $\theta_{after} = \theta \cdot e^{-k_{perc}}$ |
| Actual ET | $ET_a = K_c \cdot ET_0$, converted to $\theta$ reduction |

### Default Soil Parameters
| Parameter | Value | Source |
|---|---|---|
| $\theta_{min}$ | 0.08–0.12 (per-farmer) | Wilting point |
| $\theta_{max}$ | 0.22–0.28 (per-farmer) | Field capacity |
| $\beta$ | 0.8 (run.py) / 1.25 (demand.py) | Application efficiency |
| Percolation rate | 0.01 | Calibrated |

---

## Accounting & Metrics

Each week, `run.py` computes:
- **Groundwater cost**: $C_g(t) = C_{g,0} \cdot (1 + \alpha \cdot \text{drawdown}(t))$
- **Unmet demand**: $\max(0, d_n - \text{surface}_n - \text{GW}_n)$
- **Moisture stress**: $w_{stage} \cdot \max(0, \theta_{min} - \theta)$
- **Social cost** = $\sum C_g \cdot GW + \sum \text{unmet} + \sum \text{stress}$
- **Social welfare** = $\sum v_n \cdot \text{water}_n - \text{social cost}$

---

## Usage

### CLI

```bash
# Run all three mechanisms and compare
python simulate.py --num-farmers 24 --weeks 17 --canal-supply 30.0 --seed 42 --mechanism all

# Run only the Karma mechanism
python simulate.py --mechanism proposed

# Stress-test with scarce water
python simulate.py --canal-supply 10 --num-farmers 50
```

### Arguments

| Argument | Default | Description |
|---|---|---|
| `--num-farmers` | 24 | Number of heterogeneous farmers |
| `--weeks` | 17 | Season length (weeks) |
| `--canal-supply` | 30.0 | Canal water depth (mm/week) |
| `--seed` | 42 | RNG seed for reproducibility |
| `--mechanism` | `all` | `warabandi` / `demand` / `proposed` / `all` |

### Output

```text
Mechanism comparison
System          Social cost      Welfare      GW cost      GW used        Unmet
warabandi           1234.56      -5678.90       234.56     2345.67      1234.56
demand               987.65      -4321.09       198.76     1987.65       987.65
proposed             876.54      -3987.65       176.54     1765.43       876.54
```

---

## Known Limitations & Future Work

1. **Season length**: Simulation runs 17 weeks but wheat $K_c$ curve is parameterized for 24 weeks.
2. **ET₀ seasonality**: Linear ramp is a coarse approximation of Lahore's actual Nov–Apr ET₀ curve.
3. **Missing processes**: No capillary rise from shallow water table, no effective-rainfall partitioning.
4. **Karma mechanism**: The 30%-bid cap and equal redistribution are stylized. A formal mechanism-design analysis would strengthen the paper.
5. **Unit consistency**: The current codebase has a known divergence in the definition of $\beta$ between `run.py` (0.8 as a divisor) and `demand.py` (1.25 as a multiplier). Unifying this is a priority for future refactoring.

---

## References

1. Hassan, Manzoor, Jaleel, Muhammad. *"Demand-based water allocation in irrigation systems using mechanism design: A case study from Pakistan."* Agricultural Water Management 256 (2021): 107075.
2. Allen, R.G. et al. *"Crop evapotranspiration: Guidelines for computing crop water requirements."* FAO Irrigation and Drainage Paper 56 (1998).
3. Punjab Irrigation Department. *Warabandi operating manual.*
```
