---
title: Ion Channels
label: sp-ion-channels_page
authors: [gvarnavides, lathouwers]
numbering:
  enumerator: SP5.%s
---

An ion channel is a protein in a cell membrane that forms a pore: when it is open, ions can flow through the membrane; when it is closed, they cannot.
Nerve and muscle cells use such channels to control their electrical signals.
A myoglobin molecule in a muscle cell, similarly, either holds an oxygen molecule or it does not.
Each molecule switches between its two states at random, yet a population of them responds to a change in voltage or oxygen pressure in a smooth, predictable way.
In this assignment you connect the equilibrium probabilities of the two states to this random switching, first for ion channels and then, with the same calculation, for oxygen binding.

*How can random switching by individual molecules produce a predictable biological response?*

:::{figure} ../../figures/assignments/ion-channel-dark.svg
:name: fig-sp4-channel-dark
:class: hidden dark:block
:enumerator: SP5.1
A schematic two-state ion channel.
The two blocks are the two halves of the channel protein, which spans the membrane; the dots are ions, more of them on one side than the other.
Closed (left), the protein seals the pore; open (right), ions pass through it.
The voltage across the membrane changes how often the channel opens and closes.
:::

:::{figure} ../../figures/assignments/ion-channel.svg
:name: fig-sp4-channel
:class: dark:hidden
A schematic two-state ion channel.
The two blocks are the two halves of the channel protein, which spans the membrane; the dots are ions, more of them on one side than the other.
Closed (left), the protein seals the pore; open (right), ions pass through it.
The voltage across the membrane changes how often the channel opens and closes.
:::

## The two-state model

[](#fig-sp4-channel) sketches the model: one channel, which at any moment is either closed or open.
The channel is in contact with its surroundings at temperature $T$, so, as for any system in a heat bath, the probability of each state is proportional to its Boltzmann weight $w = e^{-G/k_\mathrm{B}T}$, where $G_O$ and $G_C$ are the free energies of the open and closed states.
Only their difference matters:

$$
\frac{w_O}{w_C} = e^{-\Delta G/k_\mathrm{B}T}, \qquad \Delta G(V) = G_O - G_C = \Delta G_0 - QV .
$$

Here $V$ is the voltage across the membrane, $\Delta G_0$ is the free-energy difference at $V = 0$, and $Q > 0$ is an effective *gating charge*: opening moves charge across the membrane, so a positive voltage lowers the free energy of the open state by $QV$ and favours opening.

With the *half-activation voltage* $V_{1/2} = \Delta G_0 / Q$, the *voltage scale* $V_T = k_\mathrm{B}T / Q$ and $x = (V - V_{1/2})/V_T$, the ratio of weights becomes $w_O / w_C = e^x$.
Since the two probabilities add up to one, the equilibrium probability to be open is

$$
p_\mathrm{eq}(V) = \frac{w_O}{w_O + w_C} = \frac{e^x}{1 + e^x} = \frac{1}{1 + \exp[-(V - V_{1/2})/V_T]} .
$$

Equilibrium weights say nothing about how *fast* the channel switches.
For that we supply opening and closing rates, in units of inverse time:

$$
k_o(V) = k_* e^{x/2}, \qquad k_c(V) = k_* e^{-x/2}.
$$

A closed channel opens in a short interval $\Delta t$ with probability $\approx k_o \Delta t$, and an open one closes with probability $\approx k_c \Delta t$.
Their ratio $k_o/k_c = e^x$ guarantees *detailed balance*: at equilibrium the flow of probability from closed to open, $k_o(1 - p_\mathrm{eq})$, equals the flow back, $k_c\,p_\mathrm{eq}$.

The voltage across a cell membrane is typically between about $-90$ and $+30\ \mathrm{mV}$, with the inside of a resting cell around $-70\ \mathrm{mV}$.
Throughout, use $V_{1/2} = -30\ \mathrm{mV}$, $V_T = 10\ \mathrm{mV}$ and $k_* = 1\ \mathrm{ms}^{-1}$, unless a task says otherwise.
These are illustrative values of the right size, not those of a particular channel.

## Part 1: Equilibrium activation

The *activation curve* $p_\mathrm{eq}(V)$ says which fraction of the time a channel is open, at each voltage.
It rises from 0 at very negative voltages to 1 at very positive ones.
$V_{1/2}$ is the voltage at which it is open half the time, and $V_T$ sets how sharp the switch is: over $V_{1/2} \pm V_T$ the open probability goes from $0.27$ to $0.73$.

:::{exercise}
:label: ex-sp4-activation

1. Plot $p_\mathrm{eq}(V)$ from $-90$ to $+30\ \mathrm{mV}$ for $V_T = 5$, $10$ and $20\ \mathrm{mV}$, at fixed $V_{1/2}$.
2. Show that $dp_\mathrm{eq}/dV = p_\mathrm{eq}(1 - p_\mathrm{eq})/V_T$.
3. Compute $dp_\mathrm{eq}/dV$ with a method from [](#numerical-differentiation_page), and plot it together with this expression.
4. Find the voltage at which $p_\mathrm{eq} = 0.3$ with your own bisection from [](#root-finding_page), and report how much the result changes when you tighten the tolerance.
5. Explain which parameter shifts the activation curve and which sets its width, and how temperature and gating charge enter the width.
   Identify the voltage at which the curve is steepest, and how your plots show it.
   Explain what $p_\mathrm{eq} = 0.3$ means for one channel observed for a long time, and for a large population of channels at one instant.
:::

## Part 2: The average response

Let $p(t)$ be the probability that a channel is open.
Opening adds probability at rate $k_o(1 - p)$ and closing removes it at rate $k_c\,p$, so

$$
\frac{dp}{dt} = k_o (1 - p) - k_c\,p .
$$

At $t = 0$ the voltage is suddenly stepped from $V_\mathrm{before} = -50\ \mathrm{mV}$ to $V_\mathrm{after} = -20\ \mathrm{mV}$: the channels start in equilibrium at the old voltage, $p(0) = p_\mathrm{eq}(V_\mathrm{before})$, but switch with the rates at the new one.
With $K = k_o + k_c$ at the new voltage, the solution relaxes exponentially, with relaxation time $\tau = 1/K$, to $p_\mathrm{eq}(V_\mathrm{after})$.

:::{exercise}
:label: ex-sp4-ode

1. Solve this equation with your RK4 implementation from [](#ordinary-differential-equations-1_page) up to $t = 8\tau$, and plot $p(t)$.
2. Estimate $\tau$ from your numerical curve, for example as the time at which the distance from equilibrium has dropped to $1/e$ of its initial value, and compare it and the late-time value with the predictions.
3. Repeat with half the timestep, and report how much your estimate of $\tau$ changes.
4. Explain what sets the final open probability and what sets how quickly it is reached, and how your timestep check shows that the relaxation you see is physical and not an integration error.
:::

## Part 3: Individual channels

Represent one channel by $s = 0$ (closed) or $s = 1$ (open).
In each timestep, draw one uniform random number for every channel: open a closed channel if it is below $a = k_o\Delta t$, close an open channel if it is below $b = k_c\Delta t$, and otherwise leave it.
Update all channels from their state at the *start* of the step.
This *short-step rule* needs $k_o\Delta t$ and $k_c\Delta t$ to be much smaller than one.

At equilibrium, the channels are open independently, each with probability $p_\mathrm{eq}$.
The number of open channels among $N$, $n_O = \sum_i s_i$, then has mean $\langle n_O \rangle = N p_\mathrm{eq}$; its variance is the subject of the exercise below.

:::{exercise}
:label: ex-sp4-single

1. Plot the trace $s(t)$ of a single channel at a fixed voltage, and one through the voltage step of Part 2.
2. Simulate 5000 independent channels through the voltage step, each starting open with probability $p_\mathrm{eq}(V_\mathrm{before})$, and plot the open fraction together with your ODE solution.
3. Show that the variance of $n_O$ is $N p_\mathrm{eq}(1 - p_\mathrm{eq})$.
   Use that $s_i$ is either 0 or 1, so that $s_i^2 = s_i$, to find the variance of one channel, and that the variances of independent channels add.
4. Test the mean and the variance of $n_O$ at the voltage with $p_\mathrm{eq} = 0.3$, for $N = 25$, $100$, $400$ and $1600$, using many independent populations, and tabulate them next to the predictions.
5. Explain why a single-channel trace looks nothing like the smooth ODE curve, even when both are correct.
   Explain what happens, as $N$ grows, to the fluctuations of the *number* of open channels, of the *fraction* open, and of the number relative to its mean.
:::

The short-step rule is an approximation.
For constant rates, the probabilities

$$
a_\mathrm{exact} = \frac{k_o}{K}\left(1 - e^{-K\Delta t}\right), \qquad b_\mathrm{exact} = \frac{k_c}{K}\left(1 - e^{-K\Delta t}\right)
$$

give the exact distribution of states at the end of each step.
They are the solution of the Part 2 equation over one step, starting from a closed channel ($p = 0$) for $a_\mathrm{exact}$, and from an open one ($p = 1$) for $b_\mathrm{exact}$, which is closed at the end with probability $1 - p$.

:::{exercise}
:label: ex-sp4-timestep

1. Simulate the voltage step with one deliberately coarse timestep, $\Delta t = \tau/4$, once with the short-step rule and once with the exact rule.
2. Plot the open fraction from both rules together with the ODE solution during the whole relaxation.
3. Explain whether agreement with the final equilibrium probability guarantees that the switching *dynamics* are right, and what a smaller timestep fixes and what a larger number of channels fixes.
:::

:::{dropdown} Hint: separating bias from noise
For either rule, the *expected* open fraction obeys $p_{j+1} = (1 - b)\,p_j + a\,(1 - p_j)$, without any random numbers.
Comparing this recursion with the ODE shows the timestep error alone; comparing your simulation with the recursion shows the sampling noise alone.
:::

## Part 4: The same model for myoglobin

Myoglobin has a single binding site for oxygen: it is unbound ($s = 0$) or bound ($s = 1$).
At oxygen pressure $P$ it binds at rate $\kappa_\mathrm{on} P$ and releases at rate $k_\mathrm{off}$, so the probability $Y(t)$ that it is bound obeys

$$
\frac{dY}{dt} = \kappa_\mathrm{on} P\,(1 - Y) - k_\mathrm{off}\,Y,
\qquad Y_\mathrm{eq}(P) = \frac{P}{P_{50} + P}, \qquad P_{50} = \frac{k_\mathrm{off}}{\kappa_\mathrm{on}},
$$

with relaxation time $\tau(P) = 1/(\kappa_\mathrm{on} P + k_\mathrm{off})$.
Use $\kappa_\mathrm{on} = 0.5\ \mathrm{kPa^{-1}\,s^{-1}}$ and $k_\mathrm{off} = 1\ \mathrm{s^{-1}}$.

:::{exercise}
:label: ex-sp4-mapping

1. Plot $Y_\mathrm{eq}(P)$, and find the half-saturation pressure numerically.
2. Step the pressure from $0.3\,P_{50}$ to $3\,P_{50}$, and follow the bound fraction with your ODE and Monte Carlo code from Parts 2 and 3.
3. Compare the late-time value and the relaxation time with the predictions.
4. Identify which quantities of the myoglobin model play the roles of the voltage, the channel state and the open probability.
   Explain which features of the equilibrium and the relaxation follow simply from having two states, and which depend on how the rates depend on voltage or pressure.
:::

:::{exercise}
:label: ex-sp4-affinity

1. Multiply *both* $\kappa_\mathrm{on}$ and $k_\mathrm{off}$ by 3.
2. Plot the equilibrium curve and the pressure-step response together with the original ones, on the same pressure and time axes.
3. Explain which combination of the rate constants sets the oxygen affinity and which sets the response time at fixed pressure, and whether an equilibrium binding curve alone could tell you both rate constants.
:::

## Part 5: Open question

Use your two-state calculations to investigate one question of your own.
Some possible directions:

- **Cooperative binding.**
  Haemoglobin, unlike myoglobin, has four binding sites that influence each other, and its binding curve is approximately $Y_H(P) = P^h / (P_{50}^h + P^h)$ with a Hill coefficient $h > 1$.
  How does a steeper curve, for example $h = 1$, $2$ and $3$, change how much oxygen is released when the pressure drops from the lungs to a working muscle, say from $3P_{50}$ to $0.3P_{50}$?
- **Independent sites.**
  Give each molecule $M$ independent, identical sites, each with the single-site probability $Y_\mathrm{eq}$.
  Does having more sites make the mean binding curve steeper, like cooperative binding does?
- **A changing voltage.**
  Switch the voltage back and forth between $-50$ and $-20\ \mathrm{mV}$ with period $T_p$.
  How well does the open fraction follow the voltage when $T_p$ is much longer than, comparable to, or much shorter than $\tau$, for example $T_p = 20\tau$, $2\tau$ and $0.2\tau$?

:::{exercise}
:label: ex-sp4-open

1. Write down your question and your prediction before you calculate.
2. Compute a quantity that answers your question for a few informative values of one parameter.
3. Plot it against the parameter, together with the curves or traces that explain it.
4. Include one numerical check, for example a finer timestep or a comparison with an exact result.
5. Explain whether your results support your prediction, what new conclusion follows, and what important limitation of the model remains.
:::

## What to hand in

See [](#assignments_page) for the deliverables and the check-in.

---

*This assignment was adapted from a draft by Robin Oosterhoff and Filip Sfetcu.*
