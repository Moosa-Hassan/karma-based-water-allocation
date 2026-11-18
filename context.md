# Karma-Based Demand Water Allocation Simulation

## 1. Mechanism Design
We extend the demand-based water allocation model (Hassan et al., 2021) by replacing the VCG money auction with a Karma (PBS) mechanism to ensure fairness and turn-taking without requiring farmers to have liquid capital.

### Weekly Loop
1. **State Observation:** The central planner reads soil moisture sensors $\theta_{n,t}$ for all $N$ farmers.
2. **Demand Computation:** The planner computes the true water demand to prevent manipulation:
   $$d_{n,t} = \beta (\theta_{max} - \theta_{n,t}) A_n l_n$$
3. **Value Computation:** The planner computes the urgency value (cost of groundwater per unit area):
   $$v_{n,t} = \frac{C_g \cdot d_{n,t}}{A_n}$$
4. **Bidding:** Farmers observe their state and submit a karma bid $b_{n,t} \le k_{n,t}$.
5. **Scoring & Allocation:** The planner scores farmers: $s_{n,t} = (b_{n,t} + 1) \cdot v_{n,t}$. 
   Surface water $S_t$ is allocated sequentially to the highest scorers until $S_t$ runs out.
6. **Groundwater Pumping:** If allocated surface water $W_{n,t} < d_{n,t}$, the farmer pumps the difference from groundwater at cost $C_g$.
7. **Karma Settlement:** Winners pay their bid $b_{n,t}$ into the pool. The pool is redistributed equally among all $N$ farmers.

## 2. Physical Model (Wheat)
- **Soil Moisture Dynamics:** Follows Hassan et al. (Eq 3). Without irrigation, moisture decays exponentially due to deep percolation: $\theta_{t+1} \approx \theta_t e^{-c \Delta t} + \text{inflows}$.
- **Crop:** Wheat (Rabi season, 12-week critical growth simulation).
- **Parameters:** $\theta_{max} = 0.25$, $\theta_{min} = 0.10$, $C_g = 1$ (normalized).

## 3. Evaluation Baselines
1. **Warabandi:** Fixed rotational turns (Hassan's baseline).
2. **DICT (Omniscient Dictator):** Gives all water to the most urgent farmer (theoretical max efficiency, zero fairness).
3. **Karma Mechanism:** Our proposed $(b+1)v$ scoring with PBS redistribution.

## 4. Metrics
- Total Groundwater Pumped
- Total Surface Water Wasted
- Fairness Index (Variance in final soil moisture / crop yield across farmers)