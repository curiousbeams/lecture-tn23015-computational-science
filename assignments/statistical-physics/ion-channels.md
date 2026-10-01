---
title: Ion Channels
label: sp-ion-channels_page
authors: [gvarnavides, lathouwers]
numbering:
  enumerator: SP5.%s
---

An ion channel in a cell membrane is either closed or open; a myoglobin molecule in a muscle cell either holds an oxygen molecule or it does not.
Each molecule switches between its two states at random, yet a population of them responds to a change in voltage or oxygen pressure in a smooth, predictable way.
In this assignment you connect equilibrium statistical weights to this random switching, and then reuse the same two-state calculation for oxygen binding.

*How can random switching by individual molecules produce a predictable biological response?*

:::{figure} ../../figures/assignments/ion-channel-dark.svg
:name: fig-sp4-channel-dark
:class: hidden dark:block
A schematic two-state channel: closed, it blocks the ions; open, it lets them through.
The voltage across the membrane changes how often it opens and closes.
:::

:::{figure} ../../figures/assignments/ion-channel.svg
:name: fig-sp4-channel
:class: dark:hidden
A schematic two-state channel: closed, it blocks the ions; open, it lets them through.
The voltage across the membrane changes how often it opens and closes.
:::

## The two-state model

The channel is in contact with its surroundings at temperature $T$.
The free-energy difference between its open and closed states is $\Delta G(V) = \Delta G_0 - QV$, where $V$ is the voltage across the membrane and $Q > 0$ is an effective gating charge that measures how strongly voltage favours opening.
The equilibrium statistical weights of the two states have the ratio $w_O / w_C = e^{-\Delta G / k_\mathrm{B}T}$.
With the half-activation voltage $V_{1/2} = \Delta G_0 / Q$, the voltage scale $V_T = k_\mathrm{B}T / Q$ and $x = (V - V_{1/2})/V_T$, this gives $w_O / w_C = e^x$, so the equilibrium probability to be open is

$$
p_\mathrm{eq}(V) = \frac{e^x}{1 + e^x} = \frac{1}{1 + \exp[-(V - V_{1/2})/V_T]} .
$$

Equilibrium weights say nothing about how *fast* the channel switches.
For that we supply opening and closing rates, in units of inverse time:

$$
k_o(V) = k_* e^{x/2}, \qquad k_c(V) = k_* e^{-x/2}.
$$

A closed channel opens in a short interval $\Delta t$ with probability $\approx k_o \Delta t$, and an open one closes with probability $\approx k_c \Delta t$.
Their ratio $k_o/k_c = e^x$ guarantees *detailed balance*: at equilibrium the flow of probability from closed to open, $k_o(1 - p_\mathrm{eq})$, equals the flow back, $k_c\,p_\mathrm{eq}$.

Throughout, use $V_{1/2} = -30\ \mathrm{mV}$, $V_T = 10\ \mathrm{mV}$ and $k_* = 1\ \mathrm{ms}^{-1}$, unless a task says otherwise.
These are illustrative values, not those of a particular channel.

## Part 1: Equilibrium activation

- Plot $p_\mathrm{eq}(V)$ from $-90$ to $+30\ \mathrm{mV}$, and compare $V_T = 5$, $10$ and $20\ \mathrm{mV}$ at fixed $V_{1/2}$.
- Calculate $dp_\mathrm{eq}/dV$ numerically with a method from [](#numerical-differentiation_page) and compare it with $p_\mathrm{eq}(1 - p_\mathrm{eq})/V_T$.
- Find the voltage at which $p_\mathrm{eq} = 0.3$ with your own bisection from [](#root-finding_page), and check how much the result changes when you tighten the tolerance.

:::{exercise}
:label: ex-sp4-activation

Which parameter shifts the activation curve, and which sets its width?
How do temperature and gating charge enter the width?
At which voltage is the curve steepest, and how do your plots show it?
If $p_\mathrm{eq} = 0.3$, what does that mean for one channel observed for a long time, and for a large population of channels at one instant?
:::

## Part 2: The average response

Let $p(t)$ be the probability that a channel is open.
Opening adds probability at rate $k_o(1 - p)$ and closing removes it at rate $k_c\,p$, so

$$
\frac{dp}{dt} = k_o (1 - p) - k_c\,p .
$$

At $t = 0$ the voltage is suddenly stepped from $V_\mathrm{before} = -50\ \mathrm{mV}$ to $V_\mathrm{after} = -20\ \mathrm{mV}$: the channels start in equilibrium at the old voltage, $p(0) = p_\mathrm{eq}(V_\mathrm{before})$, but switch with the rates at the new one.
With $K = k_o + k_c$ at the new voltage, the solution relaxes exponentially, with relaxation time $\tau = 1/K$, to $p_\mathrm{eq}(V_\mathrm{after})$.

- Solve this equation with your RK4 implementation from [](#ordinary-differential-equations-1_page) up to $t = 8\tau$, and plot $p(t)$.
- Estimate $\tau$ from your numerical curve, for example as the time at which the distance from equilibrium has dropped to $1/e$ of its initial value, and compare it and the late-time value with the predictions.
- Halve the timestep and report how much your estimate of $\tau$ changes.

:::{exercise}
:label: ex-sp4-ode

What sets the final open probability, and what sets how quickly it is reached?
How does your timestep check show that the relaxation you see is physical and not an integration error?
:::

## Part 3: Individual channels

Represent one channel by $s = 0$ (closed) or $s = 1$ (open).
In each timestep, draw one uniform random number for every channel: open a closed channel if it is below $a = k_o\Delta t$, close an open channel if it is below $b = k_c\Delta t$, and otherwise leave it.
Update all channels from their state at the *start* of the step.
This short-step rule needs $k_o\Delta t$ and $k_c\Delta t$ to be much smaller than one.

- Plot the trace of a single channel at a fixed voltage, and one through the voltage step of Part 2.
- Simulate 5000 independent channels through the voltage step, each starting open with probability $p_\mathrm{eq}(V_\mathrm{before})$, and compare the open fraction with your ODE solution.
- At equilibrium, the number $n_O$ of open channels among $N$ has mean $N p_\mathrm{eq}$ and variance $N p_\mathrm{eq}(1 - p_\mathrm{eq})$.
  Test both predictions at the voltage with $p_\mathrm{eq} = 0.3$, for $N = 25$, $100$, $400$ and $1600$, using many independent populations.
- The short-step rule is an approximation.
  For constant rates, the probabilities $a_\mathrm{exact} = \frac{k_o}{K}\left(1 - e^{-K\Delta t}\right)$ and $b_\mathrm{exact} = \frac{k_c}{K}\left(1 - e^{-K\Delta t}\right)$ give the exact distribution of states at the end of each step.
  For one deliberately coarse step, $\Delta t = \tau/4$, compare the open fraction from both rules with the ODE solution during the whole relaxation.

:::{dropdown} Hint: separating bias from noise
For either rule, the *expected* open fraction obeys $p_{j+1} = (1 - b)\,p_j + a\,(1 - p_j)$, without any random numbers.
Comparing this recursion with the ODE shows the timestep error alone; comparing your simulation with the recursion shows the sampling noise alone.
:::

:::{exercise}
:label: ex-sp4-single

Why does a single-channel trace look nothing like the smooth ODE curve, even when both are correct?
As $N$ grows, what happens to the fluctuations of the *number* of open channels, of the *fraction* open, and of the number relative to its mean?
:::

:::{exercise}
:label: ex-sp4-timestep

Does agreement with the final equilibrium probability guarantee that the switching *dynamics* are right?
What does a smaller timestep fix, and what does a larger number of channels fix?
:::

## Part 4: The same model for myoglobin

Myoglobin has a single binding site for oxygen: it is unbound ($s = 0$) or bound ($s = 1$).
At oxygen pressure $P$ it binds at rate $\kappa_\mathrm{on} P$ and releases at rate $k_\mathrm{off}$, so the bound probability $Y(t)$ obeys

$$
\frac{dY}{dt} = \kappa_\mathrm{on} P\,(1 - Y) - k_\mathrm{off}\,Y,
\qquad Y_\mathrm{eq}(P) = \frac{P}{P_{50} + P}, \qquad P_{50} = \frac{k_\mathrm{off}}{\kappa_\mathrm{on}},
$$

with relaxation time $\tau(P) = 1/(\kappa_\mathrm{on} P + k_\mathrm{off})$.
Use $\kappa_\mathrm{on} = 0.5\ \mathrm{kPa^{-1}\,s^{-1}}$ and $k_\mathrm{off} = 1\ \mathrm{s^{-1}}$.

- Plot $Y_\mathrm{eq}(P)$ and find the half-saturation pressure numerically.
- Step the pressure from $0.3\,P_{50}$ to $3\,P_{50}$.
  Reuse your ODE and Monte Carlo code from Parts 2 and 3 to follow the bound fraction, and compare the late-time value and relaxation time with the predictions.
- Multiply *both* $\kappa_\mathrm{on}$ and $k_\mathrm{off}$ by 3, and compare the equilibrium curve and the pressure-step response with the original, on the same pressure and time axes.

:::{exercise}
:label: ex-sp4-mapping

Which quantities of the myoglobin model play the roles of the voltage, the channel state and the open probability?
Which features of the equilibrium and the relaxation follow simply from having two states, and which depend on how the rates depend on voltage or pressure?
:::

:::{exercise}
:label: ex-sp4-affinity

Which combination of the rate constants sets the oxygen affinity, and which sets the response time at fixed pressure?
Could an equilibrium binding curve alone tell you both rate constants?
:::

## Part 5: Open question

Use your two-state calculations to investigate one question of your own.
State the question and a prediction before calculating, compare a few informative values of one parameter, and check one result numerically.
Some possible directions:

- **Cooperative binding.**
  Haemoglobin, unlike myoglobin, has four binding sites that influence each other, and its binding curve is approximately $Y_H(P) = P^h / (P_{50}^h + P^h)$ with a Hill coefficient $h > 1$.
  How does a steeper curve change how much oxygen is released when the pressure drops from the lungs to a working muscle, say from $3P_{50}$ to $0.3P_{50}$?
- **Independent sites.**
  Give each molecule $M$ independent, identical sites, each with the single-site probability $Y_\mathrm{eq}$.
  Does having more sites make the mean binding curve steeper, like cooperative binding does?
- **A changing voltage.**
  Switch the voltage back and forth between $-50$ and $-20\ \mathrm{mV}$ with period $T_p$.
  How well does the open fraction follow the voltage when $T_p$ is much longer than, comparable to, or much shorter than $\tau$?

:::{exercise}
:label: ex-sp4-open

What did you investigate, and what did you predict?
What new conclusion follows from your results, which numerical check supports it, and what important limitation of the model remains?
:::

## What to hand in

See [](#assignments_page) for the deliverables and the check-in.

---

*This assignment was adapted from a draft by Robin Oosterhoff and Filip Sfetcu.*
