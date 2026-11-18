# Demand-based Water Allocation in Irrigation Systems Using Mechanism Design
## Paper Summary (Hassan et al., 2021)
### A Case Study from Pakistan

### 1. Core Problem
Pakistan's Indus Basin Irrigation System (IBIS) uses **Warabandi** (fixed rotational schedule) for surface water allocation, which ignores actual crop water demand. This leads to:
- **Over-irrigation** by some farmers (wasting water)
- **Under-irrigation** by others (reducing yield)
- **Excessive groundwater pumping** (depleting aquifers, increasing costs)

The paper proposes a **demand-based allocation mechanism** using VCG (Vickrey-Clarke-Groves) auction to improve efficiency while maintaining fairness.

### 2. Study Area & Data
- **Location**: Chhajra distributary, Punjab, Pakistan
- **Farmers**: 24 farmers along the canal
- **Crops**: Kharif season (July-October) - mainly rice, maize, cotton
- **Data**: Soil moisture sensors, canal flow measurements, groundwater pumping records

### 3. Physical Model

#### Soil Moisture Dynamics (Equation 3)
$$\dot{\theta}_n(t) = I_n(t) + R_n(t) - K_c(t)ET_0(t) - c_n\theta_n(t)$$

Where:
- $\theta_n(t)$: Soil moisture of farmer $n$ at time $t$ (volumetric, 0-1)
- $I_n(t)$: Irrigation inflow (surface + groundwater)
- $R_n(t)$: Rainfall
- $K_c(t)$: Crop coefficient (varies by growth stage)
- $ET_0(t)$: Reference evapotranspiration
- $c_n$: Deep percolation constant

**Discretized weekly:**
$$\theta_n^{t+1} = \theta_n^t \cdot e^{-c_n \Delta t} + \frac{I_n^t + R_n^t}{Z_r} - \frac{K_c^t ET_0^t}{Z_r}$$

Where $Z_r$ is root zone depth (mm).

#### Water Demand (Equation 4)
$$d_n(t) = \beta (\theta_{max} - \theta_n(t)) A_n l_n$$

Where:
- $\theta_{max}$: Maximum soil moisture threshold (field capacity)
- $A_n$: Farm area
- $l_n$: Irrigation efficiency factor
- $\beta$: Inefficiency coefficient (accounts for application losses)

**Interpretation**: Demand is proportional to the soil moisture deficit. Drier soil → higher demand.

#### Groundwater Cost
$$\text{Cost}_n = C_g \cdot \max(0, d_n - W_n)$$

Where:
- $W_n$: Surface water allocated
- $C_g$: Cost per unit of groundwater pumping (energy + maintenance)

### 4. Mechanism Design

#### VCG Auction Framework
Each farmer reports:
- **Demand** $d_n$ (water needed)
- **Valuation** $v_n = C_g \cdot d_n / A_n$ (cost of pumping groundwater per unit area)

**Allocation**:
1. Sort farmers by valuation $v_n$ (descending)
2. Allocate surface water $S$ sequentially until exhausted
3. Marginal farmer gets partial allocation

**Payment (VCG)**:
Farmer $n$ pays:
$$p_n = \sum_{m \neq n} v_m \cdot W_m^{-n} - \sum_{m \neq n} v_m \cdot W_m$$

Where:
- $W_m$: Allocation to farmer $m$ with $n$ present
- $W_m^{-n}$: Allocation to farmer $m$ if $n$ were absent

**Key Property**: Truthful reporting is a dominant strategy (strategy-proof).

### 5. Comparison Mechanisms

#### 1. Warabandi (Baseline)
- Fixed rotational turns based on farm area
- Ignores actual demand/soil moisture
- Formula: Turn duration $\propto A_n$

#### 2. VCG Auction (Proposed)
- Demand-based allocation
- Farmers bid money (or report valuation)
- VCG payment rule ensures truthfulness

#### 3. Omniscient Dictator (DICT)
- Planner knows all soil moisture levels
- Allocates to maximize total welfare (give all water to most urgent farmer)
- Theoretical upper bound on efficiency, but highly unfair

### 6. Simulation Setup

#### Parameters (from paper)
| Parameter | Value | Unit |
|-----------|-------|------|
| Number of farmers | 24 | - |
| Farm area | 5-20 | acres |
| $\theta_{max}$ | 0.25 | volumetric |
| $\theta_{min}$ | 0.10 | volumetric |
| $Z_r$ | 600 | mm |
| $C_g$ | 10 | PKR/m³ |
| $\beta$ | 1.2 | - |
| $c_n$ | 1.5e-4 | per day |
| Canal efficiency | 75% | - |

#### Crop Parameters (Kharif)
- **Rice**: $K_c$ peaks at 1.2 (mid-season)
- **Maize**: $K_c$ peaks at 1.15
- **Cotton**: $K_c$ peaks at 1.1

#### Supply Scenarios
- **Abundant**: $S > \sum d_n$ (no rationing needed)
- **Scarce**: $S < \sum d_n$ (rationing required)
- **Uncertain**: $S$ drawn from historical distribution

### 7. Key Results

#### Efficiency (Groundwater Pumping)
| Mechanism | Avg GW Pumped (mm) | Reduction vs Warabandi |
|-----------|-------------------|------------------------|
| Warabandi | 450 | Baseline |
| VCG | 280 | -38% |
| DICT | 220 | -51% |

#### Equity (Variance in Yield)
| Mechanism | Yield Variance | Gini Coefficient |
|-----------|----------------|------------------|
| Warabandi | High | 0.35 |
| VCG | Medium | 0.18 |
| DICT | Very High | 0.52 |

#### Cost Savings
- VCG reduces total cost (groundwater pumping) by **35%** compared to Warabandi
- DICT reduces cost by **48%** but creates extreme inequality

### 8. Limitations Identified by Authors
1. **Requires liquid capital**: Farmers must have money to bid in VCG auction
2. **Assumes truthful reporting**: VCG is strategy-proof for money, but not for other currencies
3. **Ignores canal hydraulics**: Assumes water allocated is instantly available
4. **Static crop model**: Does not account for yield response to water stress timing
5. **No intertemporal consideration**: Each week is independent (no savings/borrowing)

### 9. Relevance to Karma Extension

**What we keep from Hassan et al.:**
- Physical soil moisture dynamics (exponential decay)
- Demand calculation from sensor data
- Groundwater cost as the objective to minimize
- Evaluation metrics (GW pumped, surface water used, fairness variance)
- Wheat/Rabi season parameters (adapted from their Kharif setup)

**What we replace:**
- VCG money auction → Karma PBS mechanism
- Farmers report demand → Planner computes demand from sensors
- Single-period allocation → Intertemporal karma budgeting

**Why this extension matters:**
- Removes the "requires liquid capital" barrier
- Adds turn-taking fairness (karma forces high-urgency farmers to ration)
- Maintains efficiency while improving equity
- More realistic for smallholder farmers in Pakistan who lack cash but can participate in karma systems

### 10. Key Equations for Implementation

**Demand calculation:**
$$d_n = \beta (\theta_{max} - \theta_n) A_n l_n$$

**Value (urgency):**
$$v_n = \frac{C_g \cdot d_n}{A_n} = C_g \cdot \beta (\theta_{max} - \theta_n) l_n$$

**Soil moisture update:**
$$\theta_n^{t+1} = \theta_n^t e^{-c \Delta t} + \frac{W_n^t + GW_n^t + R^t}{Z_r} - \frac{K_c^t ET_0^t}{Z_r}$$

**Groundwater pumped:**
$$GW_n^t = \max(0, d_n^t - W_n^t)$$

**Cost incurred:**
$$\text{Cost}_n = C_g \cdot \sum_t GW_n^t$$

### 11. Data Sources (from paper)
- **Soil moisture**: TDR sensors at 30cm depth, weekly readings
- **Canal flow**: Flumes at distributary head
- **Groundwater**: Pump meters on tube wells
- **Weather**: Pakistan Meteorological Department stations
- **Crop area**: Land records from irrigation department

### 12. Policy Implications
- Demand-based allocation can save **35-40%** of groundwater pumping costs
- Requires investment in soil moisture sensors (~$50/farm)
- VCG mechanism is theoretically optimal but practically difficult (requires money)
- Alternative mechanisms (like Karma) needed for cash-constrained farmers