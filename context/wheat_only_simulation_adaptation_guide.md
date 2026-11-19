# Adapting the Simulation for a Wheat-Only Setup

To adapt the framework in Hassan et al. (2021) from a multi-crop *Kharif* setup (July–October) to a **wheat-only** simulation, the core mathematical structure—soil moisture dynamics, demand calculation, priority surface water allocation, and VCG pricing—remains the same, while seasonal inputs, crop- and soil-specific parameters, and simulation boundaries must be updated for wheat.

## 1. Season, Timeline, and Data Series Changes

* **Cropping Window:** Replace the *Kharif* simulation window (July–October, 17 weekly intervals in the paper) with a wheat cropping cycle (for example, *Rabi* sowing around late October/November through harvesting around March/April). Keep the decision slot duration $T$ (e.g., weekly intervals) aligned with your irrigation scheduling loop.
* **Crop Coefficient (**$K_c(t)$**):** In the paper, $K_c(t)$ is estimated from Sentinel-2 NDVI using:
  $$K_c(t) = 1.457(\text{NDVI}(t)) - 0.01725$$
  For wheat, replace *Kharif* NDVI/crop coefficients with wheat-specific time series over the wheat growth cycle—starting low during germination/emergence, rising through vegetative/tillering and peaking around heading/grain filling, and declining during ripening/pre-harvest drying. If planting dates vary across farms $n$, index $K_c$ by farm/plot as well: $K_{c,n}(t)$.
* **Evapotranspiration (**$ET_0(t)$**), Rainfall (**$R_n(t)$**), and Surface Water Supply:** Swap out *Kharif* time series for wheat-season data from the same sources (USGS FEWS NET for $ET_0(t)$, CHRS/NASA for rainfall $R_n(t)$, and watercourse/canal flow records for surface water supply). Account for seasonal differences such as lower monsoon rainfall peaks and different canal availability patterns.

## 2. Agronomic, Soil, and Cost Parameter Updates

* **Soil Moisture Thresholds (**$\theta_n^{\min}, \theta_n^{\max}$**):** The paper notes that thresholds depend on soil properties and must avoid water stress below $\theta_n^{\min}$ and nutrient leaching/growth hindrance above $\theta_n^{\max}$. For wheat, calibrate $\theta_n^{\min}$ and $\theta_n^{\max}$ to your actual soil texture and wheat root-zone moisture limits rather than reusing the paper's nominal $[0.10, 0.25]$ without verification. Use farm-specific thresholds if soil types or rooting zones vary across farms $n$.
* **Irrigation Depth (**$l_n$**):** In the paper, $l_n$ depends on soil type and crop root depth (set to $100\text{ mm}$ for loamy soil and deep-rooted *Kharif* crops). Re-estimate $l_n$ for wheat's rooting depth and your target soil layer using a standard agronomic method (such as Brouwer et al., 1989, cited in the paper).
* **Deep Percolation Constant (**$c_n$**):** Re-estimate or sample $c_n$ to reflect the soil texture and percolation behavior of the wheat fields/watercourse being simulated.
* **Irrigation Efficiency Coefficient (**$\beta \ge 1$**):** Set $\beta$ to reflect the actual or target application efficiency of the wheat irrigation practice ($\beta = \frac{100}{x}$ for $x\%$ efficiency, with $\beta = 1$ corresponding to $100\%$ efficiency).
* **Groundwater Pumping Cost (**$C_g$**):** Update $C_g$ to match current pumping costs (electricity, diesel, or pump operation cost) during the wheat season, since $C_g$ directly enters each farmer's valuation:
  $$v_n(k) = \frac{C_g\, d_n(k)}{A_n}$$

## 3. Watercourse, Demand, and Auction Loop Adjustments

* **Demand and Valuation Heterogeneity:** Even with a single crop (wheat), farmers on the same watercourse can still generate distinct demands $d_n(k)$ and valuations $v_n(k)$ in interval $k$ due to differences in farm size $A_n$, current soil moisture $\theta_n(k)$, planting/growth timing, or deep percolation $c_n$.
* **Bidding, Allocation, and VCG Pricing:** Preserve the interval-$k$ loop:
  1. Each farmer submits $b_n(k) = \big(\hat{v}_n(k),\, d_n(k)\big)$.
  2. The central planner computes willingness to pay $p_n(k) = \hat{v}_n(k)d_n(k)$, sorts bids in decreasing order, and allocates surface water top-down up to available supply (respecting minimum watercourse flow $S_{\min}$).
  3. Each farmer's VCG charge $C_n$ is computed from the externality on other farmers (remaining $0$ when surface water is abundant or when a farmer receives $0$ surface water).
* **Groundwater Fallback Rule:** Retain the rule where farmers pump groundwater to cover unmet demand when surface water is insufficient and soil moisture reaches or falls below $\theta_n^{\min}$ (either mid-interval or at the start of interval $k$).
* **Baseline Comparison (*Warabandi*):** If comparing against *Warabandi*, keep the watercourse's fixed rotational roster ($A_n$, $C$, filling time $t_f^n$, draining time $t_d^n$, and discharge capacity) unchanged so differences come from the allocation/pricing mechanism rather than altered physical infrastructure.

## 4. Practical Checks Before Running Wheat Simulations

* **Growth-Stage & Drying Sensitivity:** Verify how your simulation handles early establishment/crown-root stages and late-season maturation/harvest drying so irrigation demand does not trigger unwanted late-stage wetting when the crop needs to dry down.
* **Unit Consistency:** Check that units across soil moisture $\theta_n(t)$, water balance inflows/outflows, farm area $A_n$, irrigation depth $l_n$, demand $d_n(k)$, surface water supply, and groundwater pumping are consistently converted before running time-step updates or Monte-Carlo trials.
* **Scarcity Behavior in Monte-Carlo Runs:** As shown in the paper's Monte-Carlo simulations, when surface water supply is tight relative to aggregate demand, high-priority bidders capture limited canal water while other farmers incur higher groundwater pumping or higher VCG charges; inspect both average and worst-case wheat-season scenarios.