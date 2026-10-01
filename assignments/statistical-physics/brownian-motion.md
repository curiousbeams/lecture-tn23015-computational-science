---
title: Brownian Motion
label: sp-brownian_page
authors: [gvarnavides, lathouwers]
numbering:
  enumerator: SP3.%s
---

A small particle in a fluid feels two things from the molecules around it: a steady friction that slows it down, and irregular collisions that kick it around.
In this assignment you model both effects with one simple update rule, use the particles' velocities as a thermometer, follow how their positions spread, and finally confine them in a potential to recover the Boltzmann distribution.

*How do friction and thermal kicks together produce equilibrium velocities, diffusion, and the Boltzmann distribution?*

## The model

We follow the position $x$ and velocity $v$ of a particle in a heat bath at temperature $T$, along one coordinate.
The particles in an ensemble are independent copies that do not interact.
We use units in which the particle mass and Boltzmann's constant are $m = k_\mathrm{B} = 1$, so temperature is measured in units of energy.

Without the molecular collisions, the particle obeys

$$
\frac{dx}{dt} = v, \qquad \frac{dv}{dt} = -\gamma v + F(x), \qquad F(x) = -\frac{dU}{dx},
$$

where $\gamma > 0$ is a friction rate (units of inverse time) and $U(x)$ is the potential energy.
Until Part 4 there is no potential, so $F = 0$.

The collisions are added as a random velocity kick in every timestep.
We supply the update rule, a first-order *drift-and-kick* step:

$$
x_{n+1} = x_n + v_n\,\Delta t, \qquad
v_{n+1} = v_n + \left[-\gamma v_n + F(x_n)\right]\Delta t + \sqrt{2\gamma T\Delta t}\;\xi_n,
$$

where every $\xi_n$ is an independent random number drawn from a normal distribution with mean zero and variance one, a fresh one for every particle and every step.
Both right-hand sides use the *old* state $(x_n, v_n)$.

The kick scales as $\sqrt{\Delta t}$ rather than $\Delta t$ because the *variances* of independent kicks add up in proportion to the elapsed time.
Friction removes energy, while the kicks supply it on average.
The particular kick strength $\sqrt{2\gamma T}$ balances the two so that $T$ becomes the equilibrium energy scale; this is the *fluctuation–dissipation relation*.

:::{figure} ../../figures/assignments/brownian-dark.svg
:name: fig-sp1-model-dark
:class: hidden dark:block
Left: the molecules of the bath slow the particle down (friction) and knock it about at random (kicks); we follow only its $x$ coordinate.
Right: in Part 4 the particle is also held in a harmonic trap, which pulls it back towards the centre.
:::

:::{figure} ../../figures/assignments/brownian.svg
:name: fig-sp1-model
:class: dark:hidden
Left: the molecules of the bath slow the particle down (friction) and knock it about at random (kicks); we follow only its $x$ coordinate.
Right: in Part 4 the particle is also held in a harmonic trap, which pulls it back towards the centre.
:::

## Part 1: Friction and thermal kicks

With friction alone, $dv/dt = -\gamma v$ has the solution $v(t) = v_0 e^{-\gamma t}$, which decays on the timescale $\tau_\gamma = 1/\gamma$.

- Solve this equation with your RK4 implementation from [](#ordinary-differential-equations-1_page), for $\gamma = 1$, $v_0 = 2$ and $\Delta t = 0.1$ up to $t = 5$, and compare with the exact solution.
  Halve the timestep once and report how the maximum error changes.
- Write a function that advances an *ensemble* of $N$ particles, stored as NumPy arrays `x` and `v`, by one step of the drift-and-kick rule, for a given force function $F(x)$.
  You will reuse this function in every part of the assignment.
- For $\gamma = T = 1$, $v_0 = 2$, $\Delta t = 0.01$ and a duration of 10, plot single-particle velocity traces for three cases: friction only, kicks only, and both together.
  For "kicks only", drop the friction term but keep the kick strength $\sqrt{2\gamma T\Delta t}$ at its reference value.

:::{dropdown} Hint: random numbers
Create one generator, `rng = np.random.default_rng(seed)`, and draw `rng.standard_normal(N)` in every step, so that each particle gets its own independent kick.
Fixing the `seed` makes a run reproducible; changing it gives an independent run.
:::

:::{exercise}
:label: ex-sp1-rk4

By what factor did the RK4 error change when you halved the timestep?
Is that what you expect for a fourth-order method?
:::

:::{exercise}
:label: ex-sp1-effects

What does each effect do to the velocity and the kinetic energy, and why does their combination keep the particle moving forever?
Why is "the kicks supply energy" a statement about averages, and not about every individual step?
:::

## Part 2: A thermometer from particle motion

In thermal equilibrium the velocities follow the Boltzmann distribution

$$
P(v) = \frac{1}{Z_v} e^{-v^2/(2T)}, \qquad Z_v = \int_{-\infty}^{\infty} e^{-v^2/(2T)}\, dv,
$$

and equipartition gives a mean kinetic energy $\langle E_k \rangle = \langle v^2 \rangle / 2 = T/2$.
For particles that start at rest, the model predicts

$$
\langle E_k(t) \rangle = \frac{T}{2}\left(1 - e^{-2\gamma t}\right).
$$

- Start an ensemble of $N = 2000$ particles at rest, with $\gamma = T = 1$ and $\Delta t = 0.01$, and plot $\langle E_k(t) \rangle$ up to $t = 8$ against this prediction.
- Once the ensemble has equilibrated, compare a histogram of the velocities with $P(v)$.
  Compute the normalisation $Z_v$ numerically, with a method from [](#numerical-integration_page), over a range that includes the tails.
- Use $T_\mathrm{meas} = \langle v^2 \rangle$ as a thermometer: measure it for imposed temperatures $T = 0.5$, $1$ and $2$ and collect the results in a table.
- At $T = 1$, repeat the measurement in 10 independent runs for $N = 200$ and for $N = 2000$, and compare the spread of $T_\mathrm{meas}$ between the two ensemble sizes.

:::{dropdown} Hint: comparing a histogram with a density
`np.histogram(v, bins=..., density=True)` returns probability *per unit velocity*, which is what $P(v)$ describes.
Plot it at the bin centres, or with `ax.stairs`.
:::

:::{exercise}
:label: ex-sp1-relaxation

How does the kinetic energy approach its equilibrium value?
Compare its relaxation time with the velocity-decay time $\tau_\gamma$ from Part 1, and explain the difference.
:::

:::{exercise}
:label: ex-sp1-thermometer

Does the velocity distribution support the thermal model?
How precisely can you infer the bath temperature from $N = 200$ and from $N = 2000$ particles, and is the change in precision what you would expect?
Which kind of error does *not* shrink when you add more particles?
:::

## Part 3: From velocity memory to diffusion

Friction limits how fast a particle moves, but it does not confine its position: a free particle wanders off.
We measure this with the mean-squared displacement

$$
\mathrm{MSD}(t) = \left\langle \left[x(t) - x(0)\right]^2 \right\rangle.
$$

For particles that start with thermal velocities, the model predicts two limits:

$$
\mathrm{MSD}(t) \simeq T t^2 \quad (t \ll \tau_\gamma), \qquad
\mathrm{MSD}(t) \simeq 2 D t \quad (t \gg \tau_\gamma), \qquad D = \frac{T}{\gamma}.
$$

- First equilibrate the velocities as in Part 2.
  Then set every position to zero and restart the clock, keeping the velocities.
- With $T = 1$, $\Delta t = 0.01$, $N = 2000$ and a duration of 40, plot the MSD on log-log axes together with both limits, for $\gamma = 1$.
- Determine $D$ by fitting a straight line (with an intercept) to the MSD at long times, say $t \geq 5/\gamma$.
  Do this for $\gamma = 0.5$, $1$ and $2$, and compare your values with $T/\gamma$.

:::{exercise}
:label: ex-sp1-msd

Why does the MSD grow as $t^2$ at short times and as $t$ at long times?
Use your plot to estimate the time at which the behaviour changes, and relate it to $\tau_\gamma$.
:::

:::{exercise}
:label: ex-sp1-diffusion

Report your measured $D$ for the three friction rates next to $T/\gamma$.
Why does stronger friction reduce diffusion at fixed temperature, even though it leaves the equilibrium velocity distribution unchanged?
:::

## Part 4: A particle in a harmonic trap

Now add the confining potential $U(x) = \kappa x^2 / 2$, with force $F(x) = -\kappa x$.
In equilibrium the positions should follow the Boltzmann distribution, and the energy should be shared equally:

$$
P(x) = \frac{1}{Z_x} e^{-\kappa x^2/(2T)}, \qquad
\langle E_k \rangle = \langle U \rangle = \frac{T}{2}, \qquad \langle x \rangle = 0.
$$

- Use $T = \kappa = 1$, $N = 2000$, $\Delta t = 0.005$ and a duration of 40, and start all particles at $x = 3$, $v = 0$.
  For $\gamma = 0.5$, $1$ and $4$, plot $\langle x(t) \rangle$, $\langle E_k(t) \rangle$ and $\langle U(t) \rangle$, and tabulate the late-time energies.
- For one of the friction rates, compare a histogram of the final positions with the numerically normalised $P(x)$.
- Check the timestep: for $\gamma = 4$, repeat the run with $\Delta t = 0.08$, $0.04$ and $0.02$, keeping everything else fixed, and compare the late-time $\langle E_k \rangle$ and $\langle U \rangle$ with your $\Delta t = 0.005$ result.
  Estimate the sampling uncertainty of each mean from the spread over the particles, as the standard error $\sigma/\sqrt{N}$.

:::{exercise}
:label: ex-sp1-trap

How does friction change the way the particles approach equilibrium?
Do the equilibrium distribution and energies depend on friction in the same way?
Support both answers with your results.
:::

:::{exercise}
:label: ex-sp1-timestep

Which of your timesteps give equilibrium energies that differ from $T/2$ by more than the sampling uncertainty?
What does this tell you about choosing $\Delta t$, and why can a simulation that is stable still give the wrong equilibrium?
:::

## Part 5: Open question

Use your trap simulation to investigate one question of your own about Brownian motion in a potential.
State the question and a prediction before you calculate.
Vary one parameter over three to five values, and include one check that shows your result is not a numerical artefact.
Some possible directions:

- **An anharmonic trap.**
  How does the width of the position distribution change when the trap is stiffened at large $x$, with $U(x) = \kappa x^2/2 + \lambda x^4/4$?
  Compare the simulated $\langle x^2 \rangle$ with the Boltzmann prediction $\langle x^2 \rangle_\mathrm{B} = \int x^2 e^{-U/T}\,dx \big/ \int e^{-U/T}\,dx$, evaluated numerically.
- **Hopping between two wells.**
  In a double well such as $U(x) = U_0 \left[(x/b)^2 - 1\right]^2$, how does temperature change how often a particle hops from one well to the other?
  Count a hop only when the particle arrives in the opposite well, not every time it crosses the top of the barrier.
- **The frequencies of thermal motion.**
  The Fourier transform of a long velocity record shows how fast the thermal fluctuations are, not just how large (see [](#fourier-transforms-1_page)).
  How does the velocity power spectrum of a free particle change with friction?
  Compare with the prediction $S_v(f) = 4\gamma T / \left[\gamma^2 + (2\pi f)^2\right]$.

:::{exercise}
:label: ex-sp1-open

What did you investigate, and what did you predict?
Does your result support the prediction, and what does your numerical check establish?
:::

## What to hand in

See [](#assignments_page) for the deliverables and the check-in.

---

*This assignment was adapted from a draft by Robin Oosterhoff and Filip Sfetcu.*
