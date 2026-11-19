# Realistic Wheat Simulation Extensions: Groundwater Coupling and Staggered Phenology

This document specifies two extensions to the wheat-only simulation framework based on Hassan et al. (2021):
1. **Finite Groundwater Stock Recharged by Deep Percolation**
2. **Staggered Wheat Growth Stages and Stage-Sensitive Stress**

All irrigation and canal efficiency effects remain consolidated in the single parameter $\beta \ge 1$.

---

## 1. Finite Groundwater Stock Coupled with Percolation

Rather than treating groundwater as infinitely abundant, groundwater is modeled as a finite shared stock $G(t)$ (or farm-accessible groundwater reserve) that is replenished by deep percolation from irrigated fields and depleted by groundwater pumping.

### 1.1 Groundwater Balance Equation

Let $D_n(t) = c_n \theta_n(t)$ be the deep percolation rate leaving farm $n$'s root zone, and let $I_n^{\text{gw}}(t) \ge 0$ be the groundwater pumping inflow applied to farm $n$. Over continuous time, the groundwater stock evolves as:

$$
\frac{dG(t)}{dt} = \eta_{\text{perc}} \sum_{n=1}^{N} D_n(t) A_n l_n - \sum_{n=1}^{N} I_n^{\text{gw}}(t) A_n l_n
$$

Over a discrete simulation time step $\Delta t$, the groundwater stock updates as:

$$
G(t + \Delta t) = \max\left(G_{\min},\; G(t) + \Delta t\left[\eta_{\text{perc}} \sum_{n=1}^{N} D_n(t) A_n l_n - \sum_{n=1}^{N} I_n^{\text{gw}}(t) A_n l_n\right]\right)
$$

* **Recharge Efficiency ($\eta_{\text{perc}} \in (0, 1]$):** Fraction of deep percolation leaving the root zone that successfully reaches the extractable aquifer.
* **Extractable Floor ($G_{\min} \ge 0$):** Minimum non-extractable groundwater threshold below which pumping cannot occur.

### 1.2 Constrained Groundwater Pumping and Drawdown Cost

* **Pumping Capacity Cap:** In any time step $\Delta t$, farm $n$'s groundwater extraction is bounded by its pump capacity $Q_n^{\max}$ and available groundwater above $G_{\min}$:

$$
0 \le I_n^{\text{gw}}(t) A_n l_n \le \min\Big(Q_n^{\max},\; G_{\text{avail}, n}(t)\Big)
$$

* **Supply-Constrained Emergency Pumping:** When soil moisture drops to $\theta_n(t) \le \theta_n^{\min}$ and surface water is unavailable, the farmer attempts to pump groundwater to restore moisture toward $\theta_n^{\max}$, subject to $\beta \ge 1$ and available groundwater stock. If $G(t) \le G_{\min}$ (or aggregate pumping demand exceeds $G(t) - G_{\min}$), groundwater pumping is rationed or capped, leaving the farm with an **unmet water deficit**.
* **Drawdown-Dependent Pumping Cost (Optional):** Unit groundwater pumping cost $C_g(t)$ can increase as groundwater stock declines (reflecting greater pumping lift head):

$$
C_g(t) = C_{g,0} \left(1 + \alpha_g \frac{G(0) - G(t)}{G(0)}\right)
$$

where $C_{g,0}$ is the baseline pumping cost and $\alpha_g \ge 0$ controls cost sensitivity to drawdown.

---

## 2. Staggered Wheat Phenology and Stage-Sensitive Stress

To introduce realistic heterogeneity across farms growing only wheat, each farm $n$ starts the simulation at a different sowing offset / growth stage rather than uniform crop development across the watercourse.

### 2.1 Farm-Specific Growth Stage Indexing

Let $t_0^{(n)}$ denote farm $n$'s sowing time (or initial phenological offset at $t = 0$). Farm $n$'s crop age at simulation time $t$ is:

$$
\tau_n(t) = t - t_0^{(n)}
$$

Farms can be initialized across realistic wheat cohorts (e.g., **early-sown**, **mid-sown**, and **late-sown** wheat), producing asynchronous peak water demands along the shared watercourse.

### 2.2 Stage-Dependent Crop Coefficient and Root Depth

* **Shifted Crop Coefficient $K_{c,n}(t)$:** Each farm follows the wheat crop coefficient trajectory indexed by its own crop age $\tau_n(t)$:

$$
K_{c,n}(t) = K_c^{\text{wheat}}\big(\tau_n(t)\big)
$$

where $K_c^{\text{wheat}}(\tau)$ starts low during germination/emergence, rises through tillering and stem elongation, peaks during heading/anthesis and early grain filling, and declines during ripening/senescence.

* **Stage-Dependent Irrigation / Root Depth $l_n(t)$:** Effective root depth $l_n(\tau_n(t))$ expands from shallow establishment depth to full wheat rooting depth during vegetative growth, entering both the soil moisture balance and water demand equation:

$$
d_n(t) = \beta\big(\theta_n^{\max} - \theta_n(t)\big) A_n l_n\big(\tau_n(t)\big)
$$

### 2.3 Stage-Sensitive Water Stress and Harvest Shutoff

* **Stage Sensitivity Weight $w_n(\tau_n(t))$:** Because wheat yield is much more sensitive to water deficits during **crown root initiation, booting, anthesis, and grain filling** than during late ripening, moisture deficits below $\theta_n^{\min}$ are weighted by a stage sensitivity factor $w_n(\tau_n(t)) \ge 0$:

$$
\text{Stress}_n(t) = w_n\big(\tau_n(t)\big) \cdot \max\Big(0,\; \theta_n^{\min} - \theta_n(t)\Big)
$$

* **Maturity / Harvest Shutoff:** Once farm $n$ reaches physiological maturity ($\tau_n(t) \ge \tau_{\text{harvest}}$), irrigation is stopped so the crop can dry down prior to harvest:

$$
d_n(t) = 0 \quad \text{for } \tau_n(t) \ge \tau_{\text{harvest}}
$$

---

## 3. Summary of Added Parameters and Variables

| Symbol | Meaning | Role in Extension |
| :--- | :--- | :--- |
| $G(t)$ | Shared groundwater stock at time $t$ | Recharged by percolation; depleted by groundwater pumping |
| $G_{\min}$ | Minimum extractable groundwater floor | Prevents extraction below physical/regulatory limit |
| $\eta_{\text{perc}}$ | Percolation recharge efficiency in $(0, 1]$ | Scales root-zone percolation $D_n(t)$ entering $G(t)$ |
| $I_n^{\text{gw}}(t)$ | Groundwater pumping inflow to farm $n$ | Bounded by pump capacity $Q_n^{\max}$ and available $G(t)$ |
| $Q_n^{\max}$ | Maximum pumping rate/volume per step for farm $n$ | Caps instantaneous groundwater extraction |
| $C_g(t)$ | Time-varying groundwater pumping cost | Increases with aquifer drawdown when $\alpha_g > 0$ |
| $\beta$ | Consolidated irrigation and canal efficiency ($\beta \ge 1$) | Retained unchanged to scale water demand $d_n(t)$ |
| $t_0^{(n)}, \tau_n(t)$ | Farm $n$ sowing offset and crop age | Creates staggered wheat growth stages across farms |
| $K_{c,n}(t)$ | Farm-specific wheat crop coefficient | Shifts evapotranspiration demand across growth stages |
| $l_n(\tau_n(t))$ | Stage-dependent wheat rooting/irrigation depth | Scales root-zone volume and demand over crop development |
| $w_n(\tau_n(t))$ | Growth-stage water stress sensitivity weight | Penalizes moisture deficits most heavily at critical stages |
| $\tau_{\text{harvest}}$ | Crop age at physiological maturity / harvest shutoff | Sets $d_n(t) = 0$ once farm $n$ reaches harvest drying |