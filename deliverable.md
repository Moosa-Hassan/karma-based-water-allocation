# First Project Deliverable: Karma-Based Water Allocation

## Project scope

This project simulates weekly irrigation allocation for heterogeneous wheat
farmers sharing canal water and a finite groundwater stock. It compares:

1. **Warabandi:** area-proportional rotational delivery.
2. **Demand-based allocation:** allocation by a social-value ranking.
3. **Proposed Karma allocation:** priority by Karma bid and urgency, followed
   by equal Karma redistribution.

The implemented model is a **non-cooperative repeated game**. Farmers are
separate decision makers. Coalition values and cooperative cost sharing are
not implemented.

## 1. Game formulation

### Players and state

There are \(N\) farmers, \(i \in \{1,\ldots,N\}\). The state at week \(t\)
contains

$$
s_t =
\left(
\theta_{i,t},\theta_i^{wp},\theta_i^{fc},A_i,L_{i,t},
\kappa_{i,t},G_t
\right)_{i=1}^{N},
$$

where:

- \(\theta_{i,t}\) is volumetric soil moisture;
- \(\theta_i^{wp}\) is the farm-specific wilting-point lower bound;
- \(\theta_i^{fc}\) is the farm-specific field-capacity upper bound;
- \(A_i\) is farm area in acres;
- \(L_{i,t}\) is effective wheat root depth;
- \(\kappa_{i,t}\) is the Karma balance; and
- \(G_t\) is shared groundwater stock.

The simulation samples \(A_i\sim U(5,20)\), \(\theta_i^{wp}\sim U(0.08,0.12)\),
and \(\theta_i^{fc}\sim U(0.24,0.30)\). It uses
\(\beta=1.25\), corresponding to 80% application efficiency because
\(\beta=100/80\). Each farmer starts with 10 Karma points.

### Hassan et al. equations implemented in `demand.py`

The following equations are explicitly implemented from Hassan et al. (2021).

**Equation 4: physical water demand**

$$
d_i(t)=
\beta\max\left(0,\theta_i^{fc}(t)-\theta_i(t)\right)A_iL_i(t).
$$

In code, `calculate_demand()` returns demand in acre-mm.

**Equation 6: true per-unit valuation**

$$
v_i(t)=C_g\frac{d_i(t)}{A_i},
$$

where \(C_g\) is the groundwater cost per unit. This is implemented by
`calculate_monetary_willingness()`.

**Equation 7: willingness-to-pay/bid quantity**

$$
p_i(t)=\widehat{v}_i(t)d_i(t).
$$

This is implemented by `calculate_willingness_to_pay()`. The helper
`truthful_bid()` sets \(\widehat{v}_i=v_i\).

These Eq. 6 and Eq. 7 functions are available for the VCG-style valuation
experiment, but the current demand and Karma mechanisms do not use monetary
payments.

### Project welfare extension

The following value is a project extension, not an equation from Hassan et
al. It combines groundwater avoidance with normalized soil-moisture urgency:

$$
\operatorname{value}_i(t)
=
C_g\mathbf{1}_{\{d_i(t)>0\}}
+w_i(t)
\left[
\operatorname{clip}\left(
\frac{\theta_i^{fc}-\theta_i}
{\theta_i^{fc}-\theta_i^{wp}},0,1
\right)
\right]d_i(t).
$$

This is implemented by `calculate_social_value()` and is used in the
reported welfare accounting. The demand mechanism uses a separate allocation
score:

$$
\operatorname{score}_i(t)
=d_i(t)w_i^{stage}(t)+100\mathbf{1}_{\{\text{active}_i(t)\}}.
$$

The function `allocate_social_welfare()` greedily allocates canal water to
the largest scores subject to

$$
0\leq x_i(t)\leq d_i(t),
\qquad
\sum_i x_i(t)\leq S_t.
$$

### Actions and Karma mechanism

The strategic action is an integer Karma bid:

$$
a_i(t)=b_i(t),\qquad 0\leq b_i(t)\leq\kappa_i(t).
$$

The implemented Karma policy uses urgency

$$
u_i(t)=w_i^{stage}(t)
\operatorname{clip}\left(
\frac{\theta_i^{fc}-\theta_i}
{\theta_i^{fc}-\theta_i^{wp}},0,1
\right),
$$

and bids

$$
b_i(t)=
\min\left[
\kappa_i(t),
\left\lfloor0.30u_i(t)\kappa_i(t)\right\rfloor
\right].
$$

Farmers are ordered by descending bid, then urgency, then farmer index.
Canal water is allocated top-down:

$$
x_i(t)=
\min\left[
d_i(t),
\max\left(0,S_t-\sum_{j\text{ before }i}x_j(t)\right)
\right].
$$

For a farmer receiving water, the proportional Karma payment is

$$
p_i^{K}(t)=
\operatorname{round}\left(
b_i(t)\frac{x_i(t)}{\max(d_i(t),10^{-12})}
\right).
$$

The collected pool \(P_t=\sum_i p_i^K(t)\) is redistributed as evenly as
possible across all farmers:

$$
\kappa_i(t+1)=
\max\left(0,\kappa_i(t)-p_i^K(t)+r_i(P_t,N,t)\right),
$$

where \(r_i\) is the integer redistribution share. The implementation rotates
the starting index for any remainder.

### Warabandi allocation

The turn schedule is area proportional:

$$
T_i=
\left(
\frac{168-\sum_iT_{fill,i}+\sum_iT_{drain,i}}
{\sum_iA_i}
\right)A_i
+T_{fill,i}-T_{drain,i}.
$$

The scheduled depth is converted to acre-mm and capped by demand. This is
implemented by `WarabandiMechanism`.

## 2. Wheat and soil-water dynamics

### Wheat development

Crop age is measured in weeks and converted to progress by

$$
\operatorname{progress}_t=\operatorname{clip}\left(\frac{t}{24},0,1\right).
$$

The wheat crop coefficient \(K_c\) follows four FAO-56-inspired stages:

- initial stage: \(K_c=0.4\);
- development: linear ramp from \(0.4\) to \(1.15\);
- mid-season: \(K_c=1.15\);
- late season: linear decline from \(1.15\) to \(0.3\).

Root depth is

$$
L_t=800\operatorname{clip}\left(\frac{t}{8},0.25,1\right)\text{ mm}.
$$

The simulation has synchronized crop age for all farmers. It does not yet
calculate biomass, yield, or profit.

### Soil-water bucket model

The current implementation is in `SoilMoistureModel.update()`. Canal and
groundwater deliveries are first converted from acre-mm to depth:

$$
I_{i,t}=\frac{x_{i,t}+g_{i,t}}{A_i}.
$$

The gross irrigation depth is reduced by application inefficiency:

$$
I^{eff}_{i,t}=\frac{I_{i,t}}{\beta},
\qquad
I^{loss}_{i,t}=I_{i,t}-I^{eff}_{i,t}.
$$

Water in the root zone before drainage is

$$
W_{i,t}^{pre}
=\theta_{i,t}L_{i,t}+I^{eff}_{i,t}+R_t,
$$

where \(R_t\) is rainfall. Drainage above field capacity is

$$
D_{i,t}
=c_d\max\left(0,W_{i,t}^{pre}
-\theta_i^{fc}L_{i,t}\right),
$$

with \(c_d=0.5\). Total drainage recorded for aquifer recharge also includes
application loss:

$$
D_{i,t}^{total}=D_{i,t}+I^{loss}_{i,t}.
$$

The total and readily available water are

$$
TAW_{i,t}=(\theta_i^{fc}-\theta_i^{wp})L_{i,t},
$$

$$
RAW_{i,t}=W_{i,t}^{post}
-\theta_i^{wp}L_{i,t},
$$

where \(W_{i,t}^{post}=W_{i,t}^{pre}-D_{i,t}\).

The water-stress coefficient is

$$
K_{s,i,t}
=\operatorname{clip}\left(
\frac{RAW_{i,t}}{(1-p_{MAD})TAW_{i,t}},0,1
\right),
$$

with \(p_{MAD}=0.55\). Actual evapotranspiration is

$$
ET_{i,t}
=\min\left(
K_{s,i,t}K_{c,t}ET_{0,t},
\max(0,W_{i,t}^{post}-\theta_i^{wp}L_{i,t})
\right),
$$

where

$$
ET_{0,t}=15+\frac{15t}{T}\text{ mm/week}.
$$

Finally,

$$
\theta_{i,t+1}
=\operatorname{clip}\left(
\frac{W_{i,t}^{post}-ET_{i,t}}{L_{i,t}},
\theta_i^{wp},\theta_i^{fc}
\right).
$$

### Groundwater dynamics

Groundwater pumping is limited by unmet demand, pump capacity, and available
stock:

$$
g_{i,t}\leq
\min\left[
\max(0,d_{i,t}-x_{i,t}),
Q_i^{max},
\max(0,G_t-G_{min})
\right].
$$

If aggregate requested pumping exceeds available stock, all individual
requests are scaled proportionally. Groundwater is recharged by total
drainage:

$$
G_{t+1}
=\max\left[
G_{min},
G_t+\eta\sum_iD_{i,t}^{total}A_i-\sum_ig_{i,t}
\right],
$$

where \(G_0=5000\), \(G_{min}=500\), and \(\eta=0.20\).

## 3. Social cost and social welfare

The simulation calculates a drawdown-dependent groundwater price:

$$
C_g(t)=C_{g,0}
\left[
1+\alpha
\operatorname{clip}\left(
\frac{G_0-G_{t+1}}{G_0},0,1
\right)
\right],
$$

with \(C_{g,0}=0.10\) and \(\alpha=0.50\).

Unmet demand is

$$
U_{i,t}^{unmet}
=\max(0,d_{i,t}-x_{i,t}-g_{i,t}),
$$

and the stress penalty is

$$
Z_{i,t}=w_i^{stage}(t)(1-K_{s,i,t}).
$$

The implemented social cost is

$$
\operatorname{SocialCost}
=\sum_t\left[
\sum_i C_g(t)g_{i,t}
+\sum_iU_{i,t}^{unmet}
+\sum_iZ_{i,t}
\right].
$$

The implemented social welfare is

$$
\operatorname{SocialWelfare}
=\sum_t\left[
\sum_i\operatorname{value}_i(t)(x_{i,t}+g_{i,t})
-\sum_iC_g(t)g_{i,t}
-\sum_iU_{i,t}^{unmet}
-\sum_iZ_{i,t}
\right].
$$

## 4. Preliminary equilibrium analysis

The model is a finite-horizon stochastic repeated game. A stationary Nash
equilibrium would require each farmer's policy \(\pi_i\) to satisfy

$$
\pi_i(s)\in
\arg\max_{b_i\in\{0,\ldots,\kappa_i\}}
\mathbb{E}\left[
\sum_{\tau=t}^{T}\delta^{\tau-t}U_{i,\tau}
\mid s_t=s,b_i,\pi_{-i}
\right].
$$

The current code does not compute this fixed point. It evaluates the
deterministic Karma bidding rule and records its resulting allocation,
soil-water transition, Karma balances, and welfare. Therefore the numerical
results are simulation results, not a computed Nash equilibrium or learned
strategy.

## 5. Simulation demonstration

The command-line entry point is `simulate.py`; the simulation engine is
`simulate/run.py`. The following result uses one reproducible constrained
water setup:

| Parameter | Value |
|---|---:|
| Farmers | 24 |
| Decision intervals | 17 weeks |
| Canal supply | 5 mm/week |
| Efficiency | 80% |
| \(\beta\) | 1.25 |
| Initial groundwater | 5000 |
| Groundwater floor | 500 |
| Initial Karma per farmer | 10 |
| Random seed | 42 |

```text
python simulate.py --seed 42 --num-farmers 24 --weeks 17 --canal-supply 5 --mechanism all
```

| Mechanism | Social cost | Social welfare | Groundwater cost | Groundwater used | Unmet demand |
|---|---:|---:|---:|---:|---:|
| Warabandi | 643,077.50 | 2,205,990.01 | 678.79 | 4,738.29 | 642,113.50 |
| Demand-based | 449,865.05 | 40,278,379.99 | 834.42 | 5,838.20 | 448,857.12 |
| Proposed Karma | 456,866.22 | 38,786,475.06 | 832.64 | 5,826.08 | 455,876.98 |

These are preliminary results from one seed. They demonstrate the current
simulation output; they do not establish that one mechanism is optimal.

## Current implementation status

Implemented:

- Hassan et al. Eq. 4, Eq. 6, and Eq. 7 helper functions;
- project social-value extension;
- Warabandi, demand-based, and Karma allocation;
- wheat \(K_c\), root-depth, stress, soil-water, and groundwater dynamics;
- social-cost and social-welfare accounting; and
- reproducible CLI comparison.

Not implemented:

- a learning algorithm;
- a numerical equilibrium solver;
- crop yield or profit dynamics; and
- multi-seed statistical evaluation.
