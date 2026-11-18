# Karma: A Mechanism for Peer-to-Peer Resource Allocation
## Paper Summary (Elokda et al.)

### 1. Core Problem
Traditional resource allocation mechanisms (auctions, markets) require liquid capital (money), which creates barriers for agents with limited budgets. This paper proposes **Karma**, an internal currency system where agents earn and spend "karma points" to allocate shared resources fairly over time, without requiring external money.

### 2. Key Contributions
1. **Budget-free allocation**: Agents use karma (earned through participation) instead of money
2. **Turn-taking fairness**: Agents who consume more today have less karma for tomorrow, naturally enforcing equity
3. **Strategy-proofness under certain conditions**: The PBS (Pay-Bid-Sharing) mechanism incentivizes truthful reporting
4. **Existence of stationary equilibrium**: Proves that a stable bidding policy exists where no agent can improve their expected reward by unilaterally changing strategy

### 3. Mechanism Design

#### Setup
- **N agents** compete for a shared resource each period
- Each agent has:
  - Private state $x_i$ (e.g., urgency, need level)
  - Karma balance $k_i$
  - Policy $\pi_i(x_i, k_i) \rightarrow b_i$ (bid function)

#### Weekly Allocation Process
1. **Bidding**: Each agent $i$ submits bid $b_i \leq k_i$
2. **Scoring**: Agent score $s_i = f(b_i, x_i)$ (e.g., $s_i = b_i \cdot v_i$ where $v_i$ is value/urgency)
3. **Allocation**: Resources allocated to highest scorers until supply exhausted
4. **Payment**: Winners pay their bid $b_i$ into a central pool
5. **Redistribution**: Pool divided equally among ALL agents (winners and losers)

#### Karma Transition
$$k_i^{t+1} = k_i^t - \text{payment}_i^t + \frac{\sum_j \text{payment}_j^t}{N}$$

**Key Property**: Karma is conserved in expectation. The total karma in the system remains constant (minus discretization effects from floor/ceiling operations).

### 4. Mathematical Framework

#### Markov Game Formulation
- **State**: $x_i \in \mathcal{X}$ (private state, e.g., discretized urgency)
- **Action**: $b_i \in \{0, 1, 2, ..., K_{max}\}$ (discrete karma bids)
- **Transition**: $P(x_i^{t+1} | x_i^t, \text{allocation}_i^t)$
- **Reward**: $r_i^t = u_i(\text{allocation}_i^t, x_i^t)$ (utility from received resource)

#### Equilibrium Concept
**Nash Equilibrium**: A set of policies $\{\pi_1^*, \pi_2^*, ..., \pi_N^*\}$ such that for all agents $i$:
$$\pi_i^* = \arg\max_{\pi_i} \mathbb{E}\left[\sum_{t=0}^{\infty} \gamma^t r_i^t | \pi_i, \pi_{-i}^*\right]$$

#### Existence Theorem (Theorem 1)
Under assumptions:
1. Compact state and action spaces
2. Continuous reward functions
3. Karma preservation (total karma conserved)
4. Bounded transitions

**Then**: A stationary Nash equilibrium exists.

**Proof sketch**: Uses Brouwer's fixed-point theorem on the best-response operator.

### 5. Computation: Algorithm 1 (Fictitious Play)
1. Initialize policies $\pi_i^0$ randomly for all agents
2. For iteration $m = 1, 2, ...$:
   - Fix opponents' policies $\pi_{-i}^{m-1}$
   - Solve agent $i$'s MDP via **value iteration** to get $\pi_i^m$
   - Repeat for all agents
3. Stop when policies converge (change < $\epsilon$)

### 6. Key Results

#### Fairness Metrics
- **Access fairness**: Gini coefficient of resource allocation across agents
- **Reward fairness**: Variance in cumulative rewards

#### Efficiency Metrics
- **Social welfare**: Sum of all agents' rewards
- **Resource utilization**: Fraction of supply successfully allocated

#### Comparison with Baselines
| Mechanism | Efficiency | Fairness | Requires Money? |
|-----------|-----------|----------|-----------------|
| **Karma (PBS)** | High | High | No |
| **VCG Auction** | Optimal | Medium | Yes |
| **Equal Split** | Low | High | No |
| **Random Allocation** | Low | Low | No |

### 7. Relevance to Water Allocation Project

**What we adopt:**
- Karma as internal currency for water allocation
- PBS redistribution mechanism (winners pay, pool shared equally)
- Scoring function $s = (b+1) \cdot v$ to prevent "zero karma death trap"
- Equilibrium computation via value iteration

**What we modify:**
- Urgency $v$ is computed by central planner from soil moisture sensors (not reported by agents)
- Partial allocation (farmers can get fraction of demand, not just win/lose)
- Finite population (3 farmers, not mean-field approximation)
- Physical water dynamics (exponential soil moisture decay) integrated with karma economics

### 8. Limitations Acknowledged
- Mean-field approximation assumes large anonymous population (we have N=3)
- Assumes stationary environment (we have seasonal wheat dynamics)
- Discretization of karma and state may introduce approximation errors
- Does not handle collusion between agents

### 9. Key Equations for Implementation

**Score calculation:**
$$s_i = (b_i + 1) \cdot v_i$$

**Karma update:**
$$k_i^{t+1} = k_i^t - b_i \cdot \mathbb{1}[\text{winner}] + \frac{\sum_{j \in \text{winners}} b_j}{N}$$

**Value iteration Bellman equation:**
$$V(x, k) = \max_b \left\{ \mathbb{E}[r + \gamma V(x', k')] \right\}$$

where expectation is over opponent bids (from their policies) and state transitions.