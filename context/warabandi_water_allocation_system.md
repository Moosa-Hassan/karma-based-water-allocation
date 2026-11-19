# Warabandi Water Allocation System

**Warabandi** is the traditional, supply-based rotational water distribution mechanism practiced along watercourses (*Khalas*) in the Indus Basin Irrigation System (IBIS). Introduced in 1873, it allocates surface water in fixed turns proportional to farm size rather than responding to real-time crop water demand.

---

## 1. How Warabandi Works

* **Fixed Rotational Roster:** The cropping season is divided into repeating cycles—typically **7 days (168 hours)** per week, or occasionally 10 days—where each farmer receives a scheduled turn during every cycle.
* **Proportional to Land Area:** Water access is determined by farm size ($A_n$) relative to the cultivable command area ($C$), rather than soil moisture levels or crop type.
* **Open-Loop (Supply-Driven) Operation:** Because water delivery is pre-scheduled regardless of actual on-farm demand, the system does not adapt to rainfall, varying crop growth stages, or soil moisture deficits.

---

## 2. Warabandi Equations

### Unit Irrigation Time ($t_u$)
For a weekly (168-hour) rotation across $N$ farms, the unit irrigation time $t_u$ (in **hours per acre**) is identical for all farmers:

$$t_u = \frac{168 - \sum_{n=1}^{N} t_f^n + \sum_{n=1}^{N} t_d^n}{C}$$

### Farmer's Turn Time ($t_t$)
Each farmer's net allotted turn time $t_t$ (in **hours**) scales with their farm size $A_n$ and adjusts for channel filling and draining delays:

$$t_t = t_u \times A_n + t_f^n - t_d^n$$

### Parameter Definitions

| Symbol | Meaning | Notes |
| :--- | :--- | :--- |
| $t_u$ | Unit irrigation time (hr/acre) | Common rate per acre across the watercourse |
| $t_t$ | Farmer's net turn time (hr) | Actual scheduled turn duration received by farm $n$ |
| $A_n$ | Farm size of farmer $n$ | Measured in acres in the paper's dataset |
| $C$ | Cultivable command area | Total cultivable area served by the watercourse |
| $t_f^n$ | Filling time (*Khal bharai*) | Delay required for water to fill the watercourse branch leading to farm $n$ |
| $t_d^n$ | Draining time (*Nikal*) | Time farm $n$ continues receiving residual water after upstream flow is diverted |

### Interpreting the Numerator Sums in $t_u$
* **$-\sum_{n=1}^{N} t_f^n$:** Filling time represents channel storage delay before water reaches a farm's outlet. Because each farmer is compensated with $+t_f^n$ in their personal turn time $t_t$, the total filling time across all farms is subtracted from the 168-hour weekly pool before dividing by $C$.
* **$+\sum_{n=1}^{N} t_d^n$:** Draining time represents residual water a farm still receives after upstream flow is shut off/diverted. Because $-t_d^n$ is deducted from that farmer's personal turn time $t_t$, those reclaimed hours are added back into the shared 168-hour pool to be distributed across $C$.

Summing $t_t$ over all $N$ farms (where $\sum_{n=1}^{N} A_n = C$) confirms that the individual adjustments balance out to the full 168-hour week:

$$\sum_{n=1}^{N} t_t = t_u \sum_{n=1}^{N} A_n + \sum_{n=1}^{N} t_f^n - \sum_{n=1}^{N} t_d^n = 168\text{ hours}$$

To convert turn time $t_t$ into water volume delivered, multiply $t_t$ by the watercourse discharge capacity.

---

## 3. Key Inefficiencies Identified in the Paper

* **Surface Water Wastage (Run-off):** Farmers still receive their fixed turn during periods of low or zero demand (such as rainy weeks), leading to unused water lost as run-off.
* **Groundwater Pumping or Yield Loss:** If a farmer's water requirement exceeds their fixed turn or soil moisture drops to the lower threshold ($\theta_n^{\min}$) between turns, they face lower crop yields or must pump groundwater to meet demand.