# Current Project Deliverable

## Overview

The project currently implements a basic Karma-based water-allocation
simulation for heterogeneous wheat farmers. It extends the demand-based
irrigation model described in `water_demand.md` by replacing the paper's VCG
money auction with Karma bidding and Pay-to-Society (PBS) redistribution.

The current implementation is a working simulation demonstration, but it does
not yet provide a complete formal game formulation, equilibrium analysis, or
learning algorithm.

## 1. Game Problem Formulation

### Completed

The current project identifies the following game components:

- **Players:** Farmers competing for limited canal water.
- **State variables:** Soil moisture, Karma balance, calculated water demand,
  farm area, application efficiency, crop growth rate, and groundwater
  capacity.
- **Actions:** Each farmer submits an integer Karma bid not exceeding their
  current Karma balance.
- **Allocation rule:** Farmers are ranked using:

  ```text
  score_i = (bid_i + 1) * demand_i
  ```

- **Resources:** Canal water is shared and limited; groundwater is available
  individually up to each farmer's pumping capacity.
- **Settlement:** Farmers receiving water pay their bids into a pool. The pool
  is redistributed among all farmers using integer PBS redistribution.
- **Physical dynamics:** Soil moisture changes through percolation,
  evapotranspiration, rainfall, canal water, and groundwater.
- **Heterogeneity:** Farmers have different areas, application efficiencies,
  crop growth rates, initial soil moisture, and groundwater capacities.

These features are implemented in `simulate.py` and described in `README.md`.

### Still Needed

The project needs a formal utility function for each farmer. For example, a
utility function could combine:

```text
utility_i =
    crop benefit
    - groundwater pumping cost
    - soil-moisture stress penalty
    - Karma payment or opportunity cost
```

The formulation must define:

- What each farmer is trying to maximize.
- How water affects crop benefit or yield.
- How groundwater cost enters utility.
- How soil-moisture stress is penalized.
- Whether Karma has direct utility or only represents an opportunity cost.
- Whether the game is non-cooperative or cooperative.

The current model is naturally a **non-cooperative game**. If a cooperative
game is required, the project must additionally define:

- Coalition value `V(S)` for every coalition of farmers.
- The opportunity cost of allocating water to one coalition rather than
  another.
- A cost-sharing or benefit-sharing rule.
- Whether the resulting allocation belongs to the core, Shapley allocation,
  nucleolus, or another solution concept.

At present, groundwater cost is tracked as a metric, but it is not yet part of
an explicit player payoff.

## 2. Preliminary Equilibrium Analysis

### Completed

The project has identified the relevant repeated-game structure:

- Farmers repeatedly choose Karma bids.
- Karma balances change after every allocation.
- A farmer's current bid affects both current water access and future bidding
  power.
- PBS redistribution conserves total Karma while redistributing purchasing
  power over time.

The project documentation also identifies stationary policies, value
iteration, and fictitious play as possible approaches to computing strategies.

### Still Needed

No equilibrium is currently computed by the implementation. The current bid
rule is a fixed heuristic:

```text
bid_i = min(Karma_i, floor(0.3 * urgency_i * Karma_i))
```

The project still needs:

1. A precise definition of equilibrium.

   A suitable definition would be a stationary Nash equilibrium in which no
   farmer can improve expected discounted utility by unilaterally changing
   their bidding policy.

2. A defined state space.

   Soil moisture and Karma will likely need to be discretized into finite
   states.

3. A defined action space.

   Each action can be an integer bid from zero to the farmer's current Karma
   balance.

4. A transition and reward model.

   The transition must include water allocation, soil-moisture evolution,
   groundwater use, Karma settlement, rainfall, and crop growth.

5. An equilibrium-computation method.

   Candidate methods include:

   - Value iteration for a simplified Markov game.
   - Fictitious play over farmer bidding policies.
   - Best-response iteration.
   - Reinforcement learning for larger state spaces.

6. A convergence criterion.

   For example, stop when the maximum change in policy or value function is
   below a specified tolerance.

7. An interpretation of the resulting equilibrium.

   The analysis should explain whether equilibrium produces efficient water
   use, fair access, lower groundwater pumping, or persistent strategic
   underbidding.

The current project has no implemented value iteration, fictitious play,
reinforcement learning, best-response solver, or equilibrium convergence
analysis.

## 3. Simulation Demonstration and Preliminary Results

### Completed

The current simulation provides a basic demonstration with:

- Multiple heterogeneous farmers.
- Weekly soil-moisture evolution.
- Wheat crop coefficients and evapotranspiration.
- Random rainfall.
- Fixed canal supply.
- Individual groundwater pumping limits.
- Demand calculated from soil-moisture deficits.
- Karma bids and score-based canal allocation.
- PBS Karma redistribution.
- Groundwater volume and cost tracking.
- Final soil-moisture variance.
- Plots of soil moisture and Karma balances.

The simulation can be run with different farmer counts, time horizons, canal
supplies, and random seeds.

### Still Needed

The preliminary-results section needs to be expanded into a reproducible
experiment. It should include:

- A clearly specified baseline parameter set.
- Multiple random seeds rather than one illustrative run.
- Mean and standard deviation of results.
- Total groundwater use and cost.
- Total unmet demand.
- Soil-moisture stress over time.
- Water-access inequality, such as a Gini coefficient.
- Karma inequality and convergence behavior.
- Cumulative water received by each farmer.
- Crop benefit or yield if utility includes production.

The project should also implement and compare baseline mechanisms using the
same farmer states, rainfall, canal supply, and random seeds:

1. Karma allocation.
2. Demand-only allocation.
3. Equal splitting.
4. Random allocation.
5. Warabandi rotation.
6. VCG allocation.
7. Omniscient urgency allocation.

The current simulation prints and plots results, but it does not yet produce a
formal comparison table or demonstrate that the Karma strategy is optimal.

## Current Completion Summary

| Requirement | Current status |
|---|---|
| Players and actions | Implemented at a basic level |
| State variables and allocation rule | Implemented |
| Heterogeneous farmer parameters | Implemented |
| Formal utility functions | Not yet implemented |
| Coalition values and cooperative cost sharing | Not implemented |
| Equilibrium definition | Not yet formalized |
| Equilibrium computation | Not implemented |
| Basic simulation demonstration | Implemented |
| Preliminary output | Basic printouts and plots implemented |
| Learning algorithm | Described as future work, not implemented |
| Baseline comparisons | Not implemented |
| Statistical preliminary results | Not implemented |

## Required Next Steps

The most important next steps are:

1. Choose and formalize the farmer utility function.
2. Confirm whether the project is non-cooperative or cooperative.
3. Define the equilibrium concept and state/action discretization.
4. Implement a small equilibrium solver, preferably value iteration or
   fictitious play for the basic setup.
5. Add at least one baseline mechanism.
6. Run repeated experiments across multiple seeds.
7. Report efficiency, fairness, utility, and convergence results.

