# Soil Moisture Dynamics and Farm Water Demand

In Hassan et al. (2021), on-farm water demand is driven by the **soil moisture level** $\theta_n(t)$ of each farm $n \in \{1, 2, \dots, N\}$, defined as the dimensionless ratio of absorbed water volume to total soil volume under consideration, where $\theta_n(t) \in [0, 1]$.

## 1. Optimal Soil Moisture Thresholds

To maximize crop yield and avoid irrigation inefficiencies, each farm $n$ must keep its soil moisture within a soil-specific range defined by lower and upper thresholds:

$$
\theta_n(t) \in (\theta_n^{\min}, \theta_n^{\max}), \quad \text{with } 0 < \theta_n^{\min} < \theta_n^{\max} < 1
$$

* **Below** $\theta_n^{\min}$ **(Under-Irrigation):** Applies water stress to the crop, forcing plants to draw water from greater soil depths.

* **Above** $\theta_n^{\max}$ **(Over-Irrigation):** Hinders plant growth and yield by leaching essential nutrients below the root zone.

* **Case Study Values:** Because the case study site has uniform loamy soil across a small area, the authors set $\theta_n^{\min} = 0.10$ and $\theta_n^{\max} = 0.25$ for all farms.

## 2. Soil Moisture Balance Equations

### General Water Balance Equation (Equation 1)

The rate of change of soil moisture $\dot{\theta}_n(t)$ equals total water inflows minus total water outflows:

$$
\dot{\theta}_n(t) = I_n(t) + R_n(t) - E_n(t) - D_n(t)
$$

### Crop Evapotranspiration (Equation 2)

Crop evapotranspiration $E_n(t)$—combined water loss from soil evaporation and plant transpiration—is modeled as:

$$
E_n(t) = K_c(t) \times ET_0(t)
$$

In the case study, $K_c(t)$ is derived from Sentinel-2 satellite imagery via NDVI:

$$
K_c(t) = 1.457(\text{NDVI}(t)) - 0.01725, \quad \text{where } \text{NDVI}(t) = \frac{\text{NIR} - \text{R}}{\text{NIR} + \text{R}}
$$

### Deep Percolation

Deep percolation $D_n(t)$—downward water drainage below the root zone—is modeled as linearly proportional to the current soil moisture level:

$$
D_n(t) = c_n \theta_n(t)
$$

### Expanded Soil Moisture Dynamics Equation (Equation 3)

Substituting $E_n(t)$ and $D_n(t)$ into the water balance gives the governing differential equation *(note: the original paper drops the over-dot on the left-hand side due to a typesetting typo)*:

$$
\dot{\theta}_n(t) = I_n(t) + R_n(t) - K_c(t)ET_0(t) - c_n\theta_n(t)
$$

### Discrete-Time Update (Simulation Form)

Over a discrete time step $\Delta t$, the updated soil moisture level is computed as:

$$
\theta_n(t + \Delta t) = \theta_n(t) + \Delta t\Big(I_n(t) + R_n(t) - K_c(t)ET_0(t) - c_n\theta_n(t)\Big)
$$

## 3. Farm Water Demand Model (Equation 4)

The instantaneous water demand $d_n(t)$ required to restore farm $n$'s soil moisture back to its optimal upper threshold $\theta_n^{\max}$ is:

$$
d_n(t) = \beta(\theta_n^{\max} - \theta_n(t))A_n l_n
$$

* **Irrigation Coefficient (**$\beta \ge 1$**):** Accounts for irrigation application inefficiency, where $\beta = 1$ represents $100\%$ irrigation efficiency and $\beta > 1$ represents inefficiency ($\beta = \frac{100}{x}$ for $x\%$ efficiency).

* **Groundwater Trigger:** If surface water is unavailable when $\theta_n(t) \le \theta_n^{\min}$ (either mid-week or due to an insufficient surface water allocation at the start of the week), the farmer pumps groundwater to satisfy demand.

## 4. Key Modeling and Simulation Assumptions

### Model Structure Assumptions
* **Water Balance Formulation:** Soil moisture dynamics follow a water balance model adapted from Lozoya et al. (2014), tracking inflows from irrigation ($I_n(t) \ge 0$) and rainfall ($R_n(t) \ge 0$) minus losses from crop evapotranspiration ($E_n(t) \ge 0$) and deep percolation ($D_n(t) \ge 0$).
* **Proportional Deep Percolation:** Deep percolation is assumed to scale linearly with current soil moisture ($D_n(t) = c_n\theta_n(t)$, with $c_n \ge 0$) due to differential pressure effects as soil moisture rises or falls.
* **Physically Realizable Moisture Bounds:** Soil moisture is constrained within $\theta_n(t) \in [0, 1]$ across all times $t$, with optimal crop performance occurring inside $(\theta_n^{\min}, \theta_n^{\max})$.
* **Abundant Groundwater Supply:** Groundwater is assumed to be abundantly available so farmers can pump according to their demand whenever surface water does not cover their needs or moisture reaches $\theta_n^{\min}$.

### Spatial, Parameter, and Simulation Assumptions
* **Spatial Resolution Alignment for $ET_0(t)$:** Coarse $1\text{ km} \times 1\text{ km}$ reference evapotranspiration pixels (USGS FEWS NET) are assumed to have uniform values across all finer $10\text{ m} \times 10\text{ m}$ crop coefficient pixels (Sentinel-2 NDVI) within each pixel.
* **Deep Percolation Constant ($c_n$) Variation:** A baseline value of $0.15 \times 10^{-4}$ is estimated from a single soil moisture sensor, while per-farm values in simulations are drawn uniformly from $[0.5 \times 10^{-4}, 2 \times 10^{-4}]$ to represent soil heterogeneity across farms.
* **Uniform Moisture Thresholds in Case Study:** Although thresholds depend on soil type in general, the case study assumes constant values ($\theta_n^{\max} = 0.25$ and $\theta_n^{\min} = 0.10$) across all 24 farms given the small area and uniform loamy soil.
* **Initial Soil Moisture Distribution:** Each farm's initial soil moisture $\theta_n(0)$ at the beginning of the 17-week Kharif simulation (July–October 2018) is drawn from a uniform distribution over $[0.10, 0.25]$.

## 5. Parameter Definitions

| Symbol | Meaning | Case Study Value / Source | 
| ----- | ----- | ----- | 
| $\theta_n(t)$ | Soil moisture level of farm $n$ at time $t$ | Dimensionless ratio in $[0, 1]$; $\theta_n(0) \sim \mathcal{U}[0.10, 0.25]$ | 
| $\theta_n^{\min}, \theta_n^{\max}$ | Lower and upper soil moisture thresholds | $\theta_n^{\min} = 0.10$, $\theta_n^{\max} = 0.25$ | 
| $I_n(t)$ | Irrigation water inflow (surface or groundwater) | $I_n(t) \ge 0$ | 
| $R_n(t)$ | Rainfall inflow | $R_n(t) \ge 0$ (daily CHRS precipitation data) | 
| $E_n(t)$ | Crop evapotranspiration loss rate | $E_n(t) \ge 0$ | 
| $K_c(t)$ | Crop coefficient | Estimated from $10\text{ m} \times 10\text{ m}$ Sentinel-2 NDVI | 
| $ET_0(t)$ | Reference evapotranspiration | $1\text{ km} \times 1\text{ km}$ USGS FEWS NET data | 
| $D_n(t)$ | Deep percolation loss rate | $D_n(t) \ge 0$ | 
| $c_n$ | Deep percolation constant for farm $n$ | Sensor baseline $0.15 \times 10^{-4}$; simulated in $[0.5 \times 10^{-4}, 2 \times 10^{-4}]$ | 
| $d_n(t)$ | Water demand of farm $n$ | Proportional to moisture deficit, area, and root depth | 
| $\beta$ | Irrigation coefficient ($\beta \ge 1$) | $\beta = 1$ at $100\%$ efficiency | 
| $A_n$ | Farm size of farmer $n$ | Measured in acres (total area $= 444.43\text{ acres}$) | 
| $l_n$ | Irrigation depth (soil & crop root dependent) | $100\text{ mm}$ for loamy soil and deep-rooted crops | 