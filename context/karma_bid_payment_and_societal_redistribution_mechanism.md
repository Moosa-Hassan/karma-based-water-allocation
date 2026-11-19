# Karma Bid Payment and Societal Redistribution Mechanism

This document specifies a **karma-augmented priority, payment, and societal-redistribution extension** built on top of the demand-based surface water allocation framework in Hassan et al. (2021). Farmers submit a karma bid $\hat{\kappa}_n(k)$ alongside their monetary valuation and water demand to boost their allocation priority score $S_n(k)$. Winning farmers who bid karma pay in proportion to their demand met, and the collected pool is **redistributed equally across all farmers ("society")**. If a farmer does not bid karma, their payment falls back to the baseline paper's VCG monetary externality charge.

## 1. Bid Structure and Karma Balances

At the start of each time interval $k$ (e.g., weekly slot $T$), each farmer $n \in \{1, 2, \dots, N\}$ holds an available karma balance $\kappa_n(k) \ge 0$ and submits a three-part bid:

$$
b_n(k) = \big(\hat{v}_n(k),\, d_n(k),\, \hat{\kappa}_n(k)\big)
$$

* $\hat{v}_n(k)$: Claimed per-unit monetary valuation of surface water in interval $k$.
* $d_n(k)$: Demanded quantity of surface water in interval $k$.
* $\hat{\kappa}_n(k)$: Karma points farmer $n$ bids to expedite priority for their full requested demand $d_n(k)$ in interval $k$, constrained by available balance:

$$
0 \le \hat{\kappa}_n(k) \le \kappa_n(k)
$$

## 2. Karma-Augmented Priority Water Allocation Rule

Instead of ranking farmers strictly by monetary willingness to pay $p_n(k) = \hat{v}_n(k)d_n(k)$, the central planner (**principal-agent**) computes each farmer's **effective priority score** $S_n(k)$:

$$
S_n(k) = \hat{v}_n(k)\, d_n(k) + \alpha\, \hat{\kappa}_n(k)
$$

where $\alpha > 0$ is the **karma exchange weight** converting 1 karma point into an equivalent monetary priority boost. When $\hat{\kappa}_n(k) = 0$, the score reduces directly to the baseline monetary willingness to pay $\hat{v}_n(k) d_n(k)$.

Bids are sorted in **decreasing order** of priority score:

$$
S_{n_1}(k) > S_{n_2}(k) > \dots > S_{n_N}(k)
$$

Surface water is allocated top-down against available supply to the first $m$ farmers ($D_{n_l}(k) > 0$ for $1 \le l \le m$):

* **Full allocation for** $1 \le l \le m-1$:

$$
D_{n_l}(k) = d_{n_l}(k)
$$

* **Marginal allocation for** $l = m$:

$$
D_{n_m}(k) = \hat{d}, \quad \text{where } S_{\min} \le \hat{d} \le d_{n_m}(k)
$$

* **Zero surface water** for remaining farmers (or farmers with $d_n(k) = 0$). Let $\mathcal{W}(k) = \{n_1, \dots, n_m\}$ denote the winning set with $D_n(k) > 0$.

## 3. Hybrid Payment Rules: Karma vs. VCG Monetary Fallback

For each farmer $n$, payment depends on whether they received positive surface water ($D_n(k) > 0$) and whether they submitted a positive karma bid ($\hat{\kappa}_n(k) > 0$).

### 3.1 Karma Payment (Proportional to Demand Met)

Winners who bid positive karma ($\hat{\kappa}_n(k) > 0$) pay karma scaled by the fraction of their demand met, $\frac{D_n(k)}{d_n(k)}$, and incur zero VCG monetary charge:

$$
\text{KarmaPaid}_n(k) = \begin{cases} \hat{\kappa}_n(k)\,\dfrac{D_n(k)}{d_n(k)}, & \text{if } D_n(k) > 0 \text{ and } \hat{\kappa}_n(k) > 0 \\[10pt] 0, & \text{otherwise} \end{cases}
$$

* When a winner receives their full demand ($D_n(k) = d_n(k)$), they pay their full bid $\hat{\kappa}_n(k)$.
* When the marginal winner receives a partial allocation ($D_{n_m}(k) < d_{n_m}(k)$), they pay only for the fraction of demand met.

### 3.2 Monetary VCG Charge (Fallback When No Karma Is Bid)

If a winning farmer omits karma ($\hat{\kappa}_n(k) = 0$), their payment falls back to the baseline paper's VCG externality formula—measuring the utility loss imposed on other farmers $j \ne n$ when farmer $n$ participates under the active priority ranking rule $S_j(k)$:

$$
C_n(k) = \begin{cases} \displaystyle\sum_{j \ne n} u_j\big(D_{j,-n}(k),\, \hat{v}_j(k),\, d_j(k)\big) - \sum_{j \ne n} u_j\big(D(k),\, \hat{v}_j(k),\, d_j(k)\big), & \text{if } D_n(k) > 0 \text{ and } \hat{\kappa}_n(k) = 0 \\[12pt] 0, & \text{otherwise} \end{cases}
$$

where $D_{-n}(k)$ is the counterfactual surface water allocation obtained by re-sorting the remaining farmers $\{j \ne n\}$ in decreasing order of $S_j(k)$ without farmer $n$.

## 4. Pool Collection, Equal Societal Redistribution, and Balance Update

### 4.1 Total Collected Karma Pool

The central planner aggregates all karma paid by karma-bidding winners into a shared societal karma pool:

$$
K_{\text{pool}}(k) = \sum_{n=1}^{N} \text{KarmaPaid}_n(k) = \sum_{n \in \mathcal{W}(k) \,:\, \hat{\kappa}_n(k) > 0} \hat{\kappa}_n(k)\,\frac{D_n(k)}{d_n(k)}
$$

### 4.2 Equal Redistribution to Society (All $N$ Farmers)

The collected pool $K_{\text{pool}}(k)$ is split equally across all $N$ farmers on the watercourse:

$$
\Delta \kappa_n^{\text{share}}(k) = \frac{K_{\text{pool}}(k)}{N}, \qquad \forall n \in \{1, \dots, N\}
$$

### 4.3 Karma Balance State Transition

At the end of interval $k$, each farmer's karma balance entering interval $k+1$ updates as:

$$
\kappa_n(k+1) = \kappa_n(k) - \text{KarmaPaid}_n(k) + \frac{K_{\text{pool}}(k)}{N}
$$

## 5. Mechanism Properties and Calibration

* **Real Allocative Power:** Including $\alpha \hat{\kappa}_n(k)$ in $S_n(k)$ ensures bidding karma directly advances a farmer's position in the water allocation queue during critical crop growth stages.
* **Closed-Loop Conservation of Total Karma:** Because every point paid by winners is split equally across all $N$ farmers, total karma across the watercourse is strictly conserved across intervals:

$$
\sum_{n=1}^{N} \kappa_n(k+1) = \sum_{n=1}^{N} \kappa_n(k)
$$

* **Smallholder Equity & Intertemporal Smoothing:** Splitting $K_{\text{pool}}(k)$ equally ($\frac{K_{\text{pool}}(k)}{N}$) gives smaller farms the same weekly karma dividend as larger farms, enabling them to expedite water during critical windows. Under staggered wheat sowing dates, karma spent by early-sown farms flows back into the shared pool to replenish late-sown farms ahead of their own peak demand.
* **Calibrating $\alpha$:** To prevent karma from either acting as a negligible tie-breaker ($\alpha \kappa_{\max} \ll \hat{v}_n d_n$) or completely overriding physical water valuations ($\alpha \kappa_{\max} \gg \hat{v}_n d_n$), calibrate $\alpha$ relative to the spread in baseline willingness to pay across farms:

$$
\alpha \approx \frac{\text{Std}\big(\hat{v}_n d_n\big)}{\bar{\kappa}}
$$

where $\bar{\kappa}$ is the initial per-farm karma endowment.

## 6. Parameter and Variable Summary

| Symbol | Meaning | Role in Mechanism |
| :--- | :--- | :--- |
| $\kappa_n(k)$ | Karma balance of farmer $n$ at start of interval $k$ | Caps karma bid via $0 \le \hat{\kappa}_n(k) \le \kappa_n(k)$ |
| $\hat{\kappa}_n(k)$ | Karma points bid by farmer $n$ for demand $d_n(k)$ | Boosts priority score $S_n(k)$; paid proportionally if winning |
| $\alpha$ | Karma exchange weight ($\alpha > 0$) | Scales $\hat{\kappa}_n(k)$ into monetary priority units in $S_n(k)$ |
| $S_n(k)$ | Effective priority score of farmer $n$ | Determines top-down surface water allocation order |
| $\mathcal{W}(k)$ | Set of farmers receiving positive surface water | Determines winning set ($D_n(k) > 0$) |
| $\text{KarmaPaid}_n(k)$ | Karma deducted from farmer $n$ in interval $k$ | $\hat{\kappa}_n(k)\,\frac{D_n(k)}{d_n(k)}$ if $D_n(k) > 0$ and $\hat{\kappa}_n(k) > 0$; $0$ otherwise |
| $C_n(k)$ | Monetary VCG charge for farmer $n$ in interval $k$ | Counterfactual externality charge when $D_n(k) > 0$ and $\hat{\kappa}_n(k) = 0$ |
| $K_{\text{pool}}(k)$ | Total karma collected from karma-bidding winners | Pool split equally across all $N$ farmers |
| $\Delta \kappa_n^{\text{share}}(k)$ | Karma received by farmer $n$ from equal redistribution | Equals $\frac{K_{\text{pool}}(k)}{N}$ for every farmer |