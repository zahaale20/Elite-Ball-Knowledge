# Decision & Game Theory — Optimal Choices Against Nature and Adversaries

> **Why this exists.** Autonomy is decision-making under uncertainty, and in the defense domain the uncertainty is often *adversarial* — a thinking opponent who anticipates your strategy. A planner that assumes a static world will be exploited; a pursuit algorithm that ignores the evader's best response will lose; an auction for sensor tasking that ignores incentives will be gamed. Decision theory gives you the calculus of rational choice against indifferent nature; game theory extends it to choice against opponents who choose back. Together they are the mathematics of *strategy* — the layer above control and planning where intentions, not just trajectories, are optimized.

> **What mastering it makes you.** The engineer who can frame a sensor-tasking problem as a Bayesian decision, compute a minimax strategy for a pursuit-evasion engagement, recognize when an equilibrium is exploitable, and design a mechanism whose incentives produce the outcome you want. You become the person who reasons about the adversary's reasoning — the indispensable skill in contested autonomy.

This module sits atop the planning and decision algorithms of [29-autonomy-planning-decision.md](../autonomy/29-planning-decision.md) and the optimal-control machinery of [101-foundations-control-advanced.md](101-control-advanced.md) (pursuit-evasion is a *differential game*). The probability and optimization foundations come from [03-foundations-mathematics.md](../foundations/03-mathematics.md); the algorithmic complexity of computing equilibria connects to [106-foundations-complexity-and-algorithms.md](106-complexity-and-algorithms.md). The systems framing of objectives-as-utilities echoes [01_first_principles_systems_engineering.md](../foundations/01-first_principles_systems_engineering.md), and adversarial information dynamics link to [34-information-operations-history-defense.md](../information-environment/34-information-operations-history-defense.md).

---

## 1. Utility — the axioms of rational preference

Before strategy comes the question: what does "best" mean? Von Neumann and Morgenstern proved that any preference relation satisfying four axioms — completeness, transitivity, continuity, and independence — can be represented by a **utility function** $u(\cdot)$ such that the agent acts to maximize *expected* utility:

$$
\text{choose } a^\star = \arg\max_a \; \mathbb{E}[u(\text{outcome} \mid a)] = \arg\max_a \sum_s p(s)\,u(o(a,s)).
$$

This is the foundational theorem: **rationality = expected-utility maximization.** Risk attitude is encoded in the *curvature* of $u$ — concave $u$ means risk-averse (a guaranteed outcome beats a fair gamble of equal mean). For autonomy, $u$ encodes mission value, and the curvature encodes how much you fear catastrophic loss.

---

## 2. Decision under uncertainty — choosing against nature

When the "opponent" is indifferent nature, we have a one-player decision problem. Three criteria, in increasing use of information:

| Criterion | Rule | When to use |
|---|---|---|
| Maximin | maximize the worst-case payoff | no probabilities, risk-averse |
| Minimax regret | minimize the worst-case regret | avoid hindsight loss |
| **Bayes** | maximize expected utility under prior | probabilities available |

### 2.1 Bayesian decision and the value of information

With prior $p(s)$ and observation $z$ with likelihood $p(z\mid s)$, update by Bayes:

$$
p(s\mid z) = \frac{p(z\mid s)\,p(s)}{\sum_{s'} p(z\mid s')\,p(s')},
$$

then act to maximize posterior expected utility. The **Expected Value of Perfect Information** quantifies what a sensor is worth:

$$
\text{EVPI} = \mathbb{E}_s\!\big[ \max_a u(a,s) \big] - \max_a \mathbb{E}_s\big[ u(a,s) \big] \;\ge 0.
$$

This is the principled answer to "should I spend fuel/time to get a better look before deciding?" — directly relevant to active-perception and sensor-tasking in [29-autonomy-planning-decision.md](../autonomy/29-planning-decision.md).

### 2.2 Sequential decisions — MDPs

When decisions chain over time, we have a **Markov Decision Process** $(S, A, P, R, \gamma)$. The optimal value function satisfies the **Bellman equation**:

$$
V^\star(s) = \max_a \Big[ R(s,a) + \gamma \sum_{s'} P(s'\mid s,a)\, V^\star(s') \Big].
$$

This is the discrete-time analogue of the HJB equation in optimal control ([101-foundations-control-advanced.md](101-control-advanced.md)) — decision theory and optimal control are again the same mathematics. POMDPs extend this to hidden state, the formal model for acting under partial observability.

---

## 3. Games — when the opponent chooses back

A **normal-form game** is $(N, \{A_i\}, \{u_i\})$: players $i$, action sets $A_i$, payoffs $u_i(a_1,\dots,a_n)$. The crucial shift: your best action depends on *their* action, which depends on *your* action. We need an equilibrium concept.

### 3.1 Dominance and the Prisoner's Dilemma

An action is **strictly dominated** if another action does better regardless of opponents. Rational players never play dominated actions. The Prisoner's Dilemma shows the sting:

| | Cooperate | Defect |
|---|---|---|
| **Cooperate** | $(3,3)$ | $(0,5)$ |
| **Defect** | $(5,0)$ | $(1,1)$ |

Defect dominates Cooperate for both, so the unique equilibrium is $(\text{Defect}, \text{Defect}) = (1,1)$ — *worse for both* than mutual cooperation. Individual rationality yields collective irrationality. This single matrix explains arms races, tragedy of the commons, and why coalition design is hard.

### 3.2 Nash equilibrium

A strategy profile $\sigma^\star$ is a **Nash equilibrium** if no player can improve by unilateral deviation:

$$
u_i(\sigma_i^\star, \sigma_{-i}^\star) \ge u_i(\sigma_i, \sigma_{-i}^\star) \quad \forall \sigma_i, \forall i.
$$

**Nash's theorem (1950):** every finite game has at least one equilibrium in *mixed* (randomized) strategies. The proof uses the Brouwer fixed-point theorem — the best-response map must have a fixed point. Mixed strategies matter operationally: a predictable patrol route is exploitable; the equilibrium is to randomize, and game theory tells you *with what probabilities*.

---

## 4. Zero-sum games and the minimax theorem

In a **zero-sum** game, $u_1 = -u_2$ — one player's gain is the other's loss, the canonical model of pure conflict. Von Neumann's **minimax theorem** says the game has a *value* $v$:

$$
v = \max_{\sigma_1} \min_{\sigma_2} u_1(\sigma_1,\sigma_2) = \min_{\sigma_2} \max_{\sigma_1} u_1(\sigma_1,\sigma_2).
$$

The order of optimization does not matter — there is a saddle point. Crucially, the optimal (security) strategy is computable by **linear programming**, linking strategy to the optimization of [106-foundations-complexity-and-algorithms.md](106-complexity-and-algorithms.md). The minimax strategy guarantees value $v$ *no matter what the opponent does* — exactly the robustness mindset of $\mathcal{H}_\infty$ control ([101-foundations-control-advanced.md](101-control-advanced.md)).

### 4.1 Worked example — matching pennies

| | Heads | Tails |
|---|---|---|
| **Heads** | $(+1,-1)$ | $(-1,+1)$ |
| **Tails** | $(-1,+1)$ | $(+1,-1)$ |

No pure equilibrium (whatever you pick, the opponent counters). The unique equilibrium is to play 50/50, giving value $v=0$. The lesson: against an adaptive adversary, *unpredictability is optimal* — and the precise mixing probabilities are the answer, not a heuristic.

---

## 5. Differential games — pursuit and evasion

When the game plays out in continuous time over a dynamical system, it is a **differential game** — the adversarial generalization of optimal control. State $\dot x = f(x, u, v)$, where $u$ is the pursuer's control and $v$ the evader's. Each optimizes a cost; the saddle-point value $V(x)$ obeys the **Hamilton–Jacobi–Isaacs (HJI)** equation:

$$
\min_u \max_v \Big[ \nabla V^\top f(x,u,v) + L(x,u,v) \Big] = 0.
$$

### 5.1 The homicidal chauffeur and missile guidance

Isaacs' canonical problems (the "homicidal chauffeur," the "lady in the lake") established the field. The practical payoff is **guidance law design**: proportional navigation — turn at a rate proportional to the line-of-sight rotation, $a = N\, V_c\, \dot\lambda$ — is the (near-)optimal pursuit strategy against a maneuvering target, derivable from the differential-game formulation. This is the adversarial core of [28-autonomy-gnc.md](../autonomy/28-gnc.md): interception is a game, not a tracking problem. The reachability sets computed from HJI also bound *whether* capture is even possible — the "capturability" question.

---

## 6. Repeated games and the shadow of the future

One-shot Prisoner's Dilemma says defect. But **repeated** interaction changes everything. The **Folk Theorem** states that in an infinitely repeated game with sufficiently patient players (discount factor $\delta$ near 1), any feasible payoff above the minimax can be sustained as an equilibrium — including cooperation — via *trigger strategies* ("cooperate until you defect, then punish forever").

The cooperation threshold: cooperate is sustainable when

$$
\underbrace{\frac{R}{1-\delta}}_{\text{cooperate forever}} \;\ge\; \underbrace{T + \frac{\delta\, P}{1-\delta}}_{\text{defect once, then punished}},
$$

which rearranges to $\delta \ge (T-R)/(T-P)$. Patience (high $\delta$) and harsh punishment enable cooperation. This is the theory behind deterrence, alliance stability, and multi-agent autonomy where vehicles must cooperate without a central enforcer. Axelrod's tournaments showed *tit-for-tat* — nice, retaliatory, forgiving, clear — wins robustly.

---

## 7. Mechanism design — engineering the game

Game theory analyzes given games; **mechanism design** ("reverse game theory") *designs* the rules so that self-interested agents, acting in equilibrium, produce a desired outcome. The crown jewel is the **Vickrey–Clarke–Groves (VCG)** mechanism for allocation.

### 7.1 The second-price auction

To allocate a scarce resource (sensor time, comms bandwidth, a strike asset) truthfully: each agent bids its private value, the highest bidder wins but pays the *second-highest* bid. The remarkable property — **truthful bidding is a dominant strategy**:

$$
\text{For any agent, bidding true value } v_i \text{ maximizes utility regardless of others' bids.}
$$

Proof sketch: bidding above $v_i$ risks winning at a price above value (loss); bidding below risks losing a profitable win — neither helps, and truth-telling is weakly best. This makes decentralized resource allocation in multi-agent systems *incentive-compatible* — agents have no reason to lie, so the planner gets true valuations. Market-based task allocation for drone swarms is built on exactly this.

```python
def vcg_second_price(bids):
    """Second-price (Vickrey) auction: winner pays the second-highest bid.
    Truthful bidding is a dominant strategy, so bids reveal true values."""
    ranked = sorted(enumerate(bids), key=lambda kv: kv[1], reverse=True)
    winner, _ = ranked[0]
    price = ranked[1][1] if len(ranked) > 1 else 0.0
    return winner, price

print(vcg_second_price([10, 7, 4]))   # winner 0 pays 7 -> truthful incentive
```

---

## 8. Bringing it together — the strategy stack of autonomy

| Layer | Tool | Question answered |
|---|---|---|
| Single decision | expected utility, EVPI | best act vs. nature; worth of a sensor |
| Sequential | MDP / Bellman | best policy over time |
| Static conflict | Nash / minimax | best vs. a strategic opponent |
| Dynamic conflict | differential game / HJI | best pursuit/evasion law |
| Repeated | Folk theorem | sustaining cooperation/deterrence |
| Designing rules | VCG / mechanism design | aligning selfish agents |

Each layer answers a sharper question about strategy. The progression mirrors the control stack of [101-foundations-control-advanced.md](101-control-advanced.md) — and indeed the bottom layers *are* control theory, while the top layers add the adversary. The unifying thread: **plan for the opponent's best response, not their convenient one.** That single discipline — assuming a smart adversary — is what separates robust autonomy from systems that work only on the training distribution.

---

## Sources & further study

- Osborne, *An Introduction to Game Theory* — the clean, rigorous standard.
- Osborne & Rubinstein, *A Course in Game Theory* — graduate-level depth.
- Fudenberg & Tirole, *Game Theory* — the comprehensive reference; repeated games, refinements.
- Başar & Olsder, *Dynamic Noncooperative Game Theory* — differential games, the rigorous source.
- Isaacs, *Differential Games* — the founding text; pursuit-evasion.
- Russell & Norvig, *Artificial Intelligence: A Modern Approach* — decision theory, MDPs, game-playing.
- Nisan, Roughgarden, Tardos & Vazirani, *Algorithmic Game Theory* — mechanism design and computation.

> Framing note: Decision theory teaches you to be rational against an indifferent universe; game theory teaches you to be rational against opponents who are being rational about you. Autonomy in contested space is fundamentally the second problem. The engineer who frames every adversarial encounter as a game — and computes the equilibrium rather than guessing a heuristic — builds systems that an enemy cannot cheaply exploit. The minimax strategy is not pessimism; it is the only guarantee you get when the other side is trying to win.
