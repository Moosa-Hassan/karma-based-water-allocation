# Demand-Based Water Distribution and VCG Pricing

In Hassan et al. (2021), the **demand-based water distribution mechanism** replaces fixed, open-loop *Warabandi* schedules with a closed-loop allocation and pricing framework managed by a central planner (**principal-agent**). At the start of each time slot, the planner collects farmers' water demands and valuations, allocates scarce surface water by priority, and computes payments using a **Vickrey–Clarke–Groves (VCG)** auction.

## 1. Time Intervals and Bidding Process

The cropping season is divided into equal time intervals of fixed duration $T$, with the $k$-th interval given by $((k-1)T, kT]$ for $k \in \{0, 1, 2, \dots\}$ (in the case study simulation, $T = 1\text{ week}$ over 17 weeks).

* **Bid Submission:** At the start of interval $k$, each farmer $n$ submits a bid pair:

$$
b_n(k) = \big(\hat{v}_n(k),\, d_n(k)\big)
$$

  where $d_n(k)$ is the requested water demand in interval $k$ and $\hat{v}_n(k)$ is the per-unit surface water valuation claimed by farmer $n$.

* **Actual Valuation (Equation 6):** Farmer $n$'s underlying valuation $v_n(k)$ depends on groundwater pumping cost $C_g$, current demand $d_n(k)$, and farm size $A_n$:

$$
v_n(k) = \frac{C_g\, d_n(k)}{A_n}
$$

* **Groundwater Fallback:** Surface water is delivered at the beginning of interval $k$, while groundwater can be pumped if surface water does not satisfy demand when soil moisture reaches or drops below $\theta_n^{\min}$.

## 2. Water Allocation Rule

### Willingness to Pay (Equation 7)

The principal-agent evaluates each farmer's total willingness to pay $p_n(k)$ as:

$$
p_n(k) = \hat{v}_n(k)\, d_n(k)
$$

### Priority Ordering and Allocation Vector (Equation 10)

Farmers are ranked in **decreasing order** of willingness to pay:

$$
p_{n_1}(k) > p_{n_2}(k) > \dots > p_{n_N}(k)
$$

Let $D(k) = [D_1(k), D_2(k), \dots, D_N(k)]$ be the surface water allocation vector decided by the principal-agent. Suppose available surface water is enough to supply the top $m$ farmers ($D_{n_l}(k) > 0$ for $1 \le l \le m$):

* **First $m-1$ farmers:** Receive their full requested demand:

$$
D_{n_l}(k) = d_{n_l}(k), \quad \text{for } 1 \le l \le m-1
$$

* **Marginal farmer ($l = m$):** Receives the remaining available surface water $\hat{d}$, bounded by minimum watercourse flow $S_{\min}$ and requested demand:

$$
D_{n_m}(k) = \hat{d}, \quad \text{where } S_{\min} \le \hat{d} \le d_{n_m}(k)
$$

* **Remaining farmers:** Receive $0$ surface water if supply is exhausted or if their demand is zero.

### Farmer Utility (Equation 8)

Farmer $n$'s utility in interval $k$ is modeled as:

$$
u_n\big(D_n(k), v_n(k), d_n(k)\big) = v_n(k)D_n(k) + v_n(k)\big(d_n(k) - D_n(k)\big)
$$

where $d_n(k) - D_n(k)$ represents unmet surface water demand covered through groundwater pumping.

## 3. VCG Pricing Mechanism

Rather than maximizing central planner revenue, the mechanism uses **VCG pricing** so that truthful valuation reporting is incentive-compatible and payments reflect the **social impact (externality)** a farmer's participation has on other farmers.

### General Payment Formula (Equation 9)

Let $D(k)$ be the allocation with all bidders present, and $D_{-n}(k)$ be the hypothetical allocation if farmer $n$ did not participate. Farmer $n$'s payment $C_n(\hat{v}_n(k), \hat{v}_{-n}(k))$ is:

$$
C_n\big(\hat{v}_n(k), \hat{v}_{-n}(k)\big) = \sum_{j \ne n} u_j\big(D_{j,-n}(k), \hat{v}_j(k), d_j(k)\big) - \sum_{j \ne n} u_j\big(D(k), \hat{v}_j(k), d_j(k)\big)
$$

### Zero Payment Condition & Externality Among Winners (Equations 11–13)

* **No water received:** If $D_n(k) = 0$, farmer $n$ pays nothing.
* **No impact on higher-priority winners (Equation 11):** Removing bidder $n_l$ (among the $m$ winners) frees up $D_{n_l}(k)$ units of surface water, which does not change the full-demand allocations of farmers $n_1, \dots, n_{m-1}$:

$$
u_j\big(D_{-n_l}(k), \hat{v}_{n_j}(k)\big) - u_j\big(D(k), \hat{v}_{n_j}(k)\big) = 0, \quad \text{for } j \in \{1, \dots, l-1, l+1, \dots, m-1\}
$$

* **Impact on marginal and subsequent farmers (Equations 12–13):** The freed water $D_{n_l}(k)$ first goes toward fulfilling farmer $n_m$'s remaining demand (up to $d_{n_m}(k)$):

$$
D_{n_m, -n_l}(k) =
\begin{cases}
d_{n_m}(k), & \text{if } D_{n_l}(k) \ge d_{n_m}(k) \\
D_{n_m}(k) + D_{n_l}(k), & \text{otherwise}
\end{cases}
$$

  If $D_{n_l}(k) > \big(d_{n_m}(k) - D_{n_m}(k)\big) + S_{\min}$, additional lower-priority farmers $n_{m+1}, \dots, n_{m+p}$ can also receive water, giving farmer $n_l$'s charge:

$$
C_{n_l}\big(\hat{v}_n(k), \hat{v}_{-n}(k)\big) = \sum_{j=n_m}^{n_{m+p}} \Big[ u_j\big(D_{-n_l}(k), \hat{v}_j(k)\big) - u_j\big(D(k), \hat{v}_j(k)\big) \Big]
$$

* **Abundance vs. Scarcity:** When surface water supply exceeds total demand, no farmer displaces another, so social impact is zero and **charged surface water prices are zero**. When supply is scarce, winners pay a positive VCG charge (never exceeding their bid).

## 4. Parameter Definitions

| Symbol | Meaning | Notes / Case Study Context | 
| ----- | ----- | ----- | 
| $T$ | Fixed duration of each allocation time slot | $1\text{ week}$ in the 17-week simulation | 
| $k$ | Time interval index | $((k-1)T, kT]$, $k \in \{0, 1, 2, \dots\}$ | 
| $b_n(k)$ | Bid submitted by farmer $n$ in interval $k$ | Pair $\big(\hat{v}_n(k), d_n(k)\big)$ | 
| $\hat{v}_n(k)$ | Claimed per-unit valuation of surface water | Used with $d_n(k)$ to rank bids | 
| $v_n(k)$ | True per-unit valuation of surface water | Computed via $\frac{C_g d_n(k)}{A_n}$ | 
| $C_g$ | Groundwater pumping cost | Set to $0.10\text{ PKR}$ in the case study simulation | 
| $p_n(k)$ | Willingness to pay of farmer $n$ | Computed as $\hat{v}_n(k) d_n(k)$ | 
| $D(k)$ | Surface water allocation vector across all $N$ farms | Elements $D_n(k)$ with $S_{\min} \le D_{n_m}(k) \le d_{n_m}(k)$ | 
| $S_{\min}$ | Minimum watercourse flow required to serve a farmer | Lower bound for partial allocation $\hat{d}$ | 
| $u_n(k)$ | Utility of farmer $n$ in interval $k$ | Combines served demand and groundwater-covered unmet demand | 
| $C_n(\cdot)$ | VCG payment charged to farmer $n$ | Equals $0$ when $D_n(k) = 0$ or when water is abundant | 

## 5. Summary of Simulation Findings

* **Eliminates Run-off Wastage:** Unlike *Warabandi*, zero-demand periods (such as rainy weeks) do not result in unneeded surface water deliveries and run-off waste.

* **Reduces Groundwater Pumping in Most Scenarios:** Across $10{,}000$ Monte-Carlo simulations, total groundwater pumping is lower under the demand-based scheme in the majority of runs, though extreme scarcity cases can cause higher pumping for lower-priority bidders (worst-case difference: $-1.601 \times 10^6\text{ cusec}$).

* **Scarcity-Driven Cost Differences:** Total costs can be lower when abundant surface water avoids groundwater pumping and VCG fees are zero, but higher during scarcity when VCG charges apply (worst-case cost difference: $-8.56 \times 10^5\text{ PKR}$).