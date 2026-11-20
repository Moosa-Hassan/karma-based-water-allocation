# Pure Karma Wheat Allocation with Soil Heterogeneity and Finite Groundwater

This document specifies a clean, self-contained water allocation model for a **wheat-only** canal watercourse featuring:

1. **Single-crop wheat cultivation** with **synchronized harvest timing** across all farms.
2. **Farmer heterogeneity** modeled via distinct soil moisture bounds $(\theta_n^{\min}, \theta_n^{\max})$.
3. **A pure karma economy** (no monetary payments or VCG charges) with proportional winner payment and equal societal redistribution.
4. **Finite groundwater** coupled with deep percolation and bounded extraction.

## 1. System Setup and Farmer Heterogeneity

Consider $N$ farms $\{1, 2, \dots, N\}$ along a shared canal watercourse simulated over discrete time intervals $k = 0, 1, \dots, K-1$ (e.g., weekly steps of duration $\Delta t$):

* **Wheat-Only & Synchronized Harvest:** All farms grow wheat over the same seasonal horizon and transition to harvest together at harvest step $k_{\text{harvest}}$. For $k \ge k_{\text{harvest}}$, irrigation demand drops to zero across all farms simultaneously.
* **Soil Moisture Bounds $(\theta_n^{\min}, \theta_n^{\max})$:** Each farm $n$ has its own minimum allowable soil moisture floor $\theta_n^{\min}$ and maximum soil moisture ceiling $\theta_n^{\max}$ (with $\theta_n^{\min} < \theta_n^{\max}$). Different ranges $(\theta_n^{\max} - \theta_n^{\min})$ create heterogeneous water storage buffers and urgency profiles across farms.
* **Efficiency Parameter:** Let $\beta > 0$ represent the consolidated irrigation and canal efficiency factor, and let $A_n$ and $l_n$ denote farm $n$'s cultivated area and effective root-zone depth. The simulation fixes $\beta = 0.8$ for every farm.

## 2. Soil Moisture, Demand, and Finite Groundwater Dynamics

### 2.1 Soil Moisture Update

In each interval $k$ prior to harvest ($k < k_{\text{harvest}}$), farm $n$'s soil moisture $\theta_n(k)$ evolves from surface canal allocation $D_n^{\text{canal}}(k)$ and any supplemental groundwater extraction $D_n^{\text{gw}}(k)$, offset by wheat evapotranspiration $E_n^{\text{wheat}}(k)$ and percolation/drainage loss $P_n(k)$:

$$
\theta_n(k+1) = \text{clip}\!\left(\theta_n(k) + \Delta\theta_n^{\text{in}}(k) - E_n^{\text{wheat}}(k) - P_n(k),\; \theta_n^{\min},\; \theta_n^{\max}\right)
$$

where:

* **Wheat Evapotranspiration:** $E_n^{\text{wheat}}(k) = K_c^{\text{wheat}}(k)\, ET_0(k)$ uses the wheat crop coefficient trajectory and reference evapotranspiration.
* **Percolation / Drainage:** $P_n(k) = c_n\,\theta_n(k)$ (scaled as appropriate to the time step and moisture units), representing drainage out of the root zone.
* **Effective Moisture Gain:** $\Delta\theta_n^{\text{in}}(k)$ reflects water added to the root zone from received surface water and groundwater pumping (accounting for $\beta$, $A_n$, and $l_n$).

### 2.2 Surface Water Demand

Prior to synchronized harvest ($k < k_{\text{harvest}}$), farm $n$'s requested surface water demand is:

$$
d_n(k) = \max\!\Big(0,\; \beta\, A_n\, l_n\, \big(\theta_n^{\max} - \theta_n(k)\big)\Big)
$$

At or after harvest ($k \ge k_{\text{harvest}}$), $d_n(k) = 0$ for all farms.

### 2.3 Finite Groundwater Stock and Extraction Limits

Rather than assuming abundant groundwater, let $G(k)$ denote the shared finite groundwater stock at the start of interval $k$, bounded below by a minimum non-extractable floor $G_{\min} \ge 0$:

* **Available Groundwater:** $\Delta G_{\text{avail}}(k) = \max\!\big(0,\; G(k) - G_{\min}\big)$.
* **Groundwater Pumping:** When canal water is insufficient (or when a farm's moisture approaches $\theta_n^{\min}$), farm $n$ may extract groundwater up to its pump capacity $Q_n^{\max}$ and available aquifer stock, yielding actual groundwater supply $D_n^{\text{gw}}(k) \ge 0$ with $\sum_{n=1}^N D_n^{\text{gw}}(k) \le \Delta G_{\text{avail}}(k)$.
* **Groundwater Stock Transition:** Percolation from the farms recharges the aquifer with efficiency $\eta_{\text{perc}} \in (0, 1]$, while total groundwater pumping depletes it:

$$
G(k+1) = \max\!\left(G_{\min},\; G(k) + \eta_{\text{perc}} \sum_{n=1}^N P_n(k)\, A_n\, l_n - \sum_{n=1}^N D_n^{\text{gw}}(k)\right)
$$

## 3. Pure Karma Bidding, Allocation, and Equal Redistribution

There are **no monetary payments or VCG charges** in this mechanism; all priority and settlement occur in karma.

### 3.1 Karma Bids

Each farmer $n$ holds a non-negative karma balance $\kappa_n(k) \ge 0$ and submits a karma bid $\hat{\kappa}_n(k)$ subject to:

$$
0 \le \hat{\kappa}_n(k) \le \kappa_n(k)
$$

(with $\hat{\kappa}_n(k) = 0$ whenever $d_n(k) = 0$).

### 3.2 Priority Ranking and Top-Down Canal Allocation

Farmers are sorted in **descending order** of their karma bid $\hat{\kappa}_n(k)$ (using a deterministic tie-breaker such as moisture deficit $\theta_n^{\max} - \theta_n(k)$ or farm index when bids are equal):

$$
\hat{\kappa}_{n_1}(k) \ge \hat{\kappa}_{n_2}(k) \ge \dots \ge \hat{\kappa}_{n_N}(k)
$$

Available canal water supply $S(k)$ is allocated top-down to the winning set $\mathcal{W}(k) = \{n_1, \dots, n_m\}$:

$$
D_{n_l}^{\text{canal}}(k) = \begin{cases} d_{n_l}(k), & 1 \le l \le m-1 \\ \hat{d} \in [S_{\min},\, d_{n_m}(k)], & l = m \\ 0, & l > m \end{cases}
$$

### 3.3 Proportional Karma Payment and Equal Societal Redistribution

* **Winner Karma Payment:** Each winner with $D_n^{\text{canal}}(k) > 0$ and $d_n(k) > 0$ pays karma in proportion to the share of requested demand met:

$$
\text{KarmaPaid}_n(k) = \begin{cases} \hat{\kappa}_n(k)\,\dfrac{D_n^{\text{canal}}(k)}{d_n(k)}, & \text{if } D_n^{\text{canal}}(k) > 0 \text{ and } d_n(k) > 0 \\ 0, & \text{otherwise} \end{cases}
$$

* **Collected Karma Pool:**

$$
K_{\text{pool}}(k) = \sum_{n=1}^N \text{KarmaPaid}_n(k)
$$

* **Equal Redistribution to All $N$ Farmers:** The collected pool is split equally across every farmer on the watercourse:

$$
\Delta \kappa_n^{\text{share}}(k) = \frac{K_{\text{pool}}(k)}{N}, \qquad \forall n \in \{1, \dots, N\}
$$

* **Karma Balance Update:**

$$
\kappa_n(k+1) = \kappa_n(k) - \text{KarmaPaid}_n(k) + \frac{K_{\text{pool}}(k)}{N}
$$

Because $\sum_{n=1}^N \Delta \kappa_n^{\text{share}}(k) = K_{\text{pool}}(k)$, total karma across the watercourse is conserved across every step ($\sum_{n=1}^N \kappa_n(k+1) = \sum_{n=1}^N \kappa_n(k)$).

## 4. Summary of Key Variables and Parameters

| Symbol | Meaning | Role in Model |
| :--- | :--- | :--- |
| $(\theta_n^{\min}, \theta_n^{\max})$ | Farm-specific soil moisture floor and ceiling | Heterogeneity in moisture buffer and urgency |
| $k_{\text{harvest}}$ | Synchronized harvest time step | Sets $d_n(k) = 0$ across all farms simultaneously |
| $\beta$ | Irrigation and canal efficiency factor ($\beta > 0$) | Fixed at 0.8 for every farm in the simulation |
| $S(k)$ | Available canal water supply in interval $k$ | Allocated top-down by karma bid order |
| $G(k), G_{\min}$ | Finite groundwater stock and extraction floor | Caps groundwater supply; recharged by percolation |
| $\eta_{\text{perc}}$ | Percolation recharge efficiency in $(0, 1]$ | Converts root-zone percolation into aquifer recharge |
| $Q_n^{\max}$ | Farm $n$ maximum groundwater pumping capacity | Caps single-step groundwater extraction |
| $\kappa_n(k), \hat{\kappa}_n(k)$ | Karma balance and karma bid of farmer $n$ | Determines priority rank and karma payment |
| $K_{\text{pool}}(k)$ | Total karma collected from winners | Redistributed equally ($\frac{K_{\text{pool}}(k)}{N}$) to all $N$ farmers |
