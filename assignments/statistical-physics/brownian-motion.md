---
title: Brownian Motion
label: sp-brownian_page
authors: [gvarnavides, lathouwers]
numbering:
  enumerator: SP3.%s
---

A small particle in a fluid feels two things from the molecules around it: a steady friction that slows it down, and irregular collisions that kick it around.
In this assignment you model both effects with one simple update rule, use the particles' velocities as a thermometer, follow how their positions spread, and finally hold them in a potential to recover the Boltzmann distribution.

*How do friction and thermal kicks together produce equilibrium velocities, diffusion, and the Boltzmann distribution?*

## The model

We follow the position $x$ and velocity $v$ of a particle in a heat bath at temperature $T$, along one coordinate, as sketched in [](#fig-sp1-model).
The particles in an ensemble are independent copies that do not interact.
We use units in which the particle mass and Boltzmann's constant are $m = k_\mathrm{B} = 1$, so temperature is measured in units of energy, and a force is the same as the acceleration it causes.

Without the molecular collisions, the particle obeys

$$
\frac{dx}{dt} = v, \qquad \frac{dv}{dt} = -\gamma v + F(x), \qquad F(x) = -\frac{dU}{dx},
$$

where $\gamma > 0$ is a friction rate (units of inverse time), $U(x)$ is a potential energy, and $F(x)$ is the force it exerts on the particle.
Until Part 4 there is no potential, so $F = 0$.

The collisions are added as a random velocity kick in every timestep.
We supply the update rule, a first-order *drift-and-kick* step:

$$
x_{n+1} = x_n + v_n\,\Delta t, \qquad
v_{n+1} = v_n + \left[-\gamma v_n + F(x_n)\right]\Delta t + \sqrt{2\gamma T\Delta t}\;\xi_n,
$$

where every $\xi_n$ is an independent random number drawn from a normal distribution with zero mean and unit variance, a fresh one for every particle and every step.
Both right-hand sides use the *old* state $(x_n, v_n)$.
Without the kick term, this is just Euler's method for the equations above.

The kick scales as $\sqrt{\Delta t}$ rather than $\Delta t$ because the *variances* of independent kicks add up in proportion to the elapsed time.
Friction removes energy, while the kicks supply it on average.
The particular kick strength $\sqrt{2\gamma T}$ balances the two so that $T$ becomes the equilibrium energy scale; this is the *fluctuation–dissipation relation*.

:::{figure} ../../figures/assignments/brownian-dark.svg
:name: fig-sp1-model-dark
:class: hidden dark:block
:enumerator: SP3.1
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
This deterministic part of the model is an ordinary ODE, which RK4 solves very accurately.
The kicks are random, and RK4 is not designed for them, so the full model is always advanced with the drift-and-kick rule above.
The first exercise compares the two on the friction-only problem; the second adds the kicks.

:::{exercise}
:label: ex-sp1-rk4

Use $\gamma = 1$ and $v_0 = 2$.

1. Solve $dv/dt = -\gamma v$ with your RK4 implementation from [](#ordinary-differential-equations-1_page), with $\Delta t = 0.1$ up to $t = 5$, and plot it together with the exact solution.
2. Repeat with $\Delta t = 0.05$, and tabulate the maximum error for both timesteps.
3. Repeat both runs with the drift-and-kick rule without its kick term, and tabulate its maximum errors next to those of RK4.
4. Explain by what factor each method's error changed when you halved the timestep, and whether that is what you expect for each.
:::

:::{exercise}
:label: ex-sp1-effects

1. Write a function that advances an *ensemble* of $N$ particles, stored as NumPy arrays `x` and `v`, by one step of the drift-and-kick rule, for a given force function $F(x)$.
   You will reuse this function in every part of the assignment.
2. Plot single-particle velocity traces for $\gamma = T = 1$, $v(0) = 2$, $\Delta t = 0.01$ and a duration of 10, for three cases: friction only, kicks only, and both together.
   For "kicks only", drop the friction term but keep the kick strength $\sqrt{2\gamma T\Delta t}$ at its value for $\gamma = T = 1$.
3. Explain what each effect does to the velocity and the kinetic energy, and why their combination keeps the particle moving forever.
   Explain why "the kicks supply energy" is a statement about averages, and not about every individual step.
:::

:::{dropdown} Hint: random numbers
Create one generator, `rng = np.random.default_rng(seed)`, and draw `rng.standard_normal(N)` in every step, so that each particle gets its own independent kick.
Fixing the `seed` makes a run reproducible; changing it gives an independent run.
:::

## Part 2: A thermometer from particle motion

In thermal equilibrium the velocities follow the Boltzmann distribution

$$
P(v) = \frac{1}{Z_v} e^{-v^2/(2T)}, \qquad Z_v = \int_{-\infty}^{\infty} e^{-v^2/(2T)}\, dv,
$$

where the normalisation $Z_v$ makes $\int P(v)\,dv = 1$.
Equipartition gives a mean kinetic energy $\langle E_k \rangle = \langle v^2 \rangle / 2 = T/2$.
For particles that start at rest, with $v(0) = 0$, the model predicts

$$
\langle E_k(t) \rangle = \frac{T}{2}\left(1 - e^{-2\gamma t}\right).
$$

Conversely, $T_\mathrm{meas} = \langle v^2 \rangle$ measured over an equilibrated ensemble is a thermometer for the bath.

:::{exercise}
:label: ex-sp1-relaxation

1. Start an ensemble of $N = 2000$ particles with $x(0) = v(0) = 0$, and run it with $\gamma = T = 1$ and $\Delta t = 0.01$ up to $t = 8$.
2. Plot $\langle E_k(t) \rangle$ together with the prediction.
3. Explain how the kinetic energy approaches its equilibrium value, and compare its relaxation time with the velocity-decay time $\tau_\gamma$ from Part 1.
:::

:::{exercise}
:label: ex-sp1-thermometer

1. Compute $Z_v$ numerically for $T = 1$, with a method from [](#numerical-integration_page), over a range that includes the tails.
2. Plot a histogram of the velocities at $t = 8$ from the previous exercise together with $P(v)$.
3. Measure $T_\mathrm{meas}$ at $t = 8$ for imposed temperatures $T = 0.5$, $1$ and $2$, and tabulate it next to $T$.
4. Repeat the $T = 1$ measurement in 10 independent runs, for $N = 200$ and for $N = 2000$, and compute the spread (standard deviation) of $T_\mathrm{meas}$ for each ensemble size.
5. Explain whether the velocity distribution supports the thermal model, how precisely you can infer the bath temperature from $N = 200$ and from $N = 2000$ particles, and whether the change in precision is what you would expect.
   Identify which kind of error does *not* shrink when you add more particles.
:::

:::{dropdown} Hint: comparing a histogram with a density
`np.histogram(v, bins=..., density=True)` returns probability *per unit velocity*, which is what $P(v)$ describes.
Plot it at the bin centres, or with `ax.stairs`.
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
\mathrm{MSD}(t) \simeq 2 D t \quad (t \gg \tau_\gamma), \qquad D = \frac{T}{\gamma} ,
$$

where $D$ is the diffusion coefficient.

:::{exercise}
:label: ex-sp1-msd

Use $T = 1$, $\Delta t = 0.01$ and $N = 2000$.

1. Equilibrate the velocities of a free ensemble with $\gamma = 1$ by running it for $t = 10/\gamma$, ten velocity-decay times.
2. Set every position to zero and restart the clock, keeping the velocities, and run for a further time of 40.
3. Plot the MSD on log-log axes together with both limits.
4. Explain why the MSD grows as $t^2$ at short times and as $t$ at long times, and estimate from your plot the time at which the behaviour changes; relate it to $\tau_\gamma$.
:::

:::{exercise}
:label: ex-sp1-diffusion

1. Repeat the MSD run for $\gamma = 0.5$ and $2$.
2. Find $D$ for each of the three friction rates by fitting a straight line, with an intercept, to the MSD at long times, say $t \geq 5/\gamma$.
3. Tabulate your measured $D$ next to $T/\gamma$.
4. Explain why stronger friction reduces diffusion at fixed temperature, even though it leaves the equilibrium velocity distribution unchanged.
:::

## Part 4: A particle in a harmonic trap

Now add the confining potential $U(x) = \kappa x^2/2$, which exerts the force $F(x) = -\kappa x$.
In equilibrium the positions should follow the Boltzmann distribution in $x$,

$$
P(x) = \frac{1}{Z_x} e^{-U(x)/T}, \qquad Z_x = \int_{-\infty}^{\infty} e^{-U(x)/T}\, dx ,
$$

where $Z_x$ normalises it just as $Z_v$ did for the velocities.
The energy should be shared equally between motion and potential, $\langle E_k \rangle = \langle U \rangle = T/2$, and $\langle x \rangle = 0$.

:::{exercise}
:label: ex-sp1-trap

Use $T = \kappa = 1$, $N = 2000$ and $\Delta t = 0.005$, and start all particles at $x(0) = 3$, $v(0) = 0$.

1. Run up to $t = 40$ for $\gamma = 0.5$, $1$ and $4$, and plot $\langle x(t) \rangle$, $\langle E_k(t) \rangle$ and $\langle U(t) \rangle$.
2. Tabulate $\langle E_k \rangle$ and $\langle U \rangle$ at the end of each run, averaged over the particles, together with their standard errors $\sigma/\sqrt{N}$.
3. Compute $Z_x$ numerically, and plot a histogram of the final positions for one of the friction rates together with $P(x)$.
4. Explain how friction changes the way the particles approach equilibrium, and whether the equilibrium distribution and energies depend on friction in the same way.
   Support both answers with your results.
:::

:::{exercise}
:label: ex-sp1-timestep

1. Repeat the $\gamma = 4$ run with $\Delta t = 0.08$, $0.04$ and $0.02$, keeping everything else fixed.
2. Tabulate $\langle E_k \rangle$ and $\langle U \rangle$ at the end of each run, with their standard errors, next to your $\Delta t = 0.005$ result.
3. Identify which timesteps give equilibrium energies that differ from $T/2$ by more than the sampling uncertainty.
4. Explain what this tells you about choosing $\Delta t$, and why a simulation that is stable can still give the wrong equilibrium.
:::

## Part 5: Open question

Use your simulation to investigate one question of your own about Brownian motion.
Some possible directions:

- **An anharmonic trap.**
  Stiffen the trap at large $x$, with $U(x) = \kappa x^2/2 + \lambda x^4/4$, for example for $\lambda = 0$, $0.5$, $1$ and $2$.
  How does the width of the position distribution change?
  Compare the simulated $\langle x^2 \rangle$ with the Boltzmann prediction $\langle x^2 \rangle_\mathrm{B} = \int x^2 e^{-U/T}\,dx \big/ \int e^{-U/T}\,dx$, evaluated numerically.
- **The frequencies of thermal motion.**
  The Fourier transform of a long velocity record shows how fast the thermal fluctuations are, not just how large (see [](#fourier-transforms-1_page)).
  How does the velocity power spectrum of a free particle change with friction, for example for $\gamma = 1$ and $2$?
  Compare with the prediction $S_v(f) = 4\gamma T / \left[\gamma^2 + (2\pi f)^2\right]$.

:::{exercise}
:label: ex-sp1-open

1. Write down your question and your prediction before you calculate.
2. Compute the quantities your question needs for three to five values of one parameter.
3. Plot them against the parameter, together with any prediction you can calculate.
4. Include one check that your result is not a numerical artefact, for example a smaller $\Delta t$, a second seed or a longer run.
5. Explain whether your results support your prediction, and what your check establishes.
:::

## What to hand in

See [](#assignments_page) for the deliverables and the check-in.

---

*This assignment was adapted from a draft by Robin Oosterhoff and Filip Sfetcu.*
