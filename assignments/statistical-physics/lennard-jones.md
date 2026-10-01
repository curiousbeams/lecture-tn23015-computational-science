---
title: Phase-Space Geometry
label: sp-lennard-jones_page
authors: [gvarnavides, lathouwers]
numbering:
  enumerator: SP1.%s
---

Two bound atoms vibrate back and forth while their total energy stays fixed.
In this assignment you connect that motion to a closed orbit in position–momentum space, and then use the area enclosed by the orbit to count states.
From the count follow an entropy and temperature of the system.

*How does the geometry of a bound orbit connect its period to the entropy and temperature of a dimer?*

## The model

Two identical atoms of mass $m$ interact through the Lennard-Jones potential

$$
U(r) = 4\varepsilon\left[\left(\frac{\sigma}{r}\right)^{12} - \left(\frac{\sigma}{r}\right)^{6}\right].
$$

We ignore the motion of the centre of mass and rotation, and follow only the separation $r$, with reduced mass $\mu = m/2$.
Measuring separation in units of the equilibrium distance $r_\mathrm{min} = 2^{1/6}\sigma$, energy in units of $\varepsilon$, and time in units of $r_\mathrm{min}\sqrt{\mu/\varepsilon}$, the dimensionless energy, or Hamiltonian, and the equations of motion are

$$
h(q, p) = \frac{p^2}{2} + u(q), \qquad u(q) = q^{-12} - 2q^{-6}, \qquad
\frac{dq}{d\tau} = p, \qquad \frac{dp}{d\tau} = F(q) = 12\left(q^{-13} - q^{-7}\right).
$$

The minimum is $u(1) = -1$.
For energies $-1 < e < 0$ the dimer is bound and vibrates periodically; at $e = 0$ it can fly apart.

:::{figure} ../../figures/assignments/lennard-jones-dark.svg
:name: fig-sp5-orbit-dark
:class: hidden dark:block
Left: the potential and the turning points of an orbit with $e = -0.5$.
Right: the same orbit in phase space; the shaded region, with energy below $e$, has area $A(e)$.
:::

:::{figure} ../../figures/assignments/lennard-jones.svg
:name: fig-sp5-orbit
:class: dark:hidden
Left: the potential and the turning points of an orbit with $e = -0.5$.
Right: the same orbit in phase space; the shaded region, with energy below $e$, has area $A(e)$.
:::

## Part 1: The well and its turning points

- Plot $u(q)$ and $F(q)$ over a range that shows the repulsive wall, the minimum and the attractive tail.
  Check the analytic force against $-du/dq$ computed with a method from [](#numerical-differentiation_page).
- For $e = -0.95$, $-0.5$ and $-0.1$, find the inner and outer turning points, where $u(q) = e$, with a root-finding method from [](#root-finding_page), and compare them with the exact
  $$
  q_\mathrm{in} = \left(1 + \sqrt{1 + e}\right)^{-1/6}, \qquad q_\mathrm{out} = \left(1 - \sqrt{1 + e}\right)^{-1/6}.
  $$
- Estimate the curvature $u''(1)$ numerically.
  A harmonic approximation $u \approx -1 + \tfrac12 u''(1)(q-1)^2$ then predicts a small-oscillation period $2\pi/\sqrt{u''(1)}$, which you will compare with later.

:::{exercise}
:label: ex-sp5-turning

Why are there exactly two turning points for $-1 < e < 0$, and what happens to each of them as $e \to 0^-$?
Which side of the well allows the larger displacement from equilibrium, and what does this suggest about the average separation of a hotter dimer?
:::

## Part 2: Vibrations and their period

- Integrate the equations of motion with your RK4 from [](#ordinary-differential-equations-1_page), starting at a turning point with $p = 0$.
  Plot $q(\tau)$, $p(\tau)$ and the energy error $h(\tau) - e$ over several oscillations for the three energies of Part 1.
- The period $T(e)$ is the time after which the state $(q, p)$ repeats; going from one turning point to the other is only half of it.
  Measure the period, for example from successive times at which $q$ crosses 1 with $p > 0$, and plot $T(e)$ for about 15 energies between $-0.99$ and $-0.03$, together with the harmonic prediction.
- For the most demanding energy, halve the timestep and report how much the period and the maximum energy error change.

:::{dropdown} Hint: choosing a timestep
The steep inner wall is where the force changes fastest.
A timestep of about $10^{-3}$ resolves it well; check by halving it.
Near $e \to 0$ the orbit becomes very long, so you need many steps per period.
:::

:::{exercise}
:label: ex-sp5-period

How do the position and momentum traces change as the energy rises, and why does the period grow so strongly near dissociation?
Does the period approach the harmonic prediction near $e = -1$?
What shows that the change in period is physical and not caused by numerical energy drift?
:::

## Part 3: Counting states in phase space

The orbit of energy $e$ is the closed curve $h(q, p) = e$, made of the two branches $p_\pm(q; e) = \pm\sqrt{2[e - u(q)]}$ between the turning points.
The area it encloses,

$$
A(e) = 2\int_{q_\mathrm{in}}^{q_\mathrm{out}} \sqrt{2[e - u(q)]}\, dq ,
$$

counts the states with energy *up to* $e$: divided by a fixed phase-space cell, it is the number of such states.
Its derivative $g(e) = dA/de$ is the density of states, the number of states per unit energy.

- Overlay the branches $p_\pm$ on a few of your numerical orbits from Part 2.
- Calculate $A(e)$ on a grid of a few hundred energies in $-1 < e < 0$, avoiding the end points, with a method from [](#numerical-integration_page).
  Check representative values by refining the integration.
- Differentiate your $A(e)$ numerically to obtain $g(e)$, and compare it with the periods $T(e)$ from Part 2.

:::{dropdown} Hint: the turning points
The integrand goes to zero like a square root at both turning points, where its slope is infinite, so a straight quadrature converges slowly.
Substituting $q = c + a\sin z$, with $c = (q_\mathrm{in} + q_\mathrm{out})/2$, $a = (q_\mathrm{out} - q_\mathrm{in})/2$ and $-\pi/2 \leq z \leq \pi/2$, gives a smooth integrand; remember $dq = a\cos z\,dz$.
:::

:::{exercise}
:label: ex-sp5-area

Why must $A(e)$ increase with energy, and which end of the energy range is the hardest to compute accurately?
Your $g(e)$ should agree with the period $T(e)$. Explain why: what does differentiating the area with respect to energy have to do with the time spent going around the orbit?
:::

## Part 4: Entropy and temperature

Use the *Gibbs entropy*, which counts all states with energy below $e$: relative to a reference energy $e_\mathrm{ref}$,

$$
s_G(e) - s_G(e_\mathrm{ref}) = \ln\frac{A(e)}{A(e_\mathrm{ref})}, \qquad
\frac{1}{\theta_G} = \frac{ds_G}{de} = \frac{g(e)}{A(e)} ,
$$

with $\theta_G = k_\mathrm{B}T_G/\varepsilon$ the dimensionless temperature.

- Plot $s_G(e)$ and $\theta_G(e) = A/g$ over the energies where your $A$ and $g$ are reliable.
- Locate the maximum of $\theta_G$ and check how it changes when you refine your energy grid.
- A completely independent check comes from the dynamics: averaged over one full orbit, $\langle p^2 \rangle_\mathrm{time} = A(e)/T(e)$, which should equal $\theta_G$.
  Verify this at three energies with your trajectories from Part 2.

:::{exercise}
:label: ex-sp5-gibbs

Why does $\theta_G$ go to zero at both ends of the energy range, so that it has a maximum in between?
Beyond that maximum, adding energy *lowers* the temperature: the heat capacity is negative.
What happens there to the mean kinetic energy, and why is this not a phase transition?
:::

## Part 5: Open question

Use your calculation of $A$, $g$ and $\theta_G$ to investigate one question of your own about how the shape of the potential changes the thermodynamics of the dimer.
State the question and a prediction before calculating, compare a few informative cases, and repeat one of them at higher numerical accuracy.
Some possible directions:

- **A different power law.**
  The family $u_n(q) = q^{-2n} - 2q^{-n}$ keeps the depth and position of the minimum fixed but changes the curvature and the tail; $n = 6$ is Lennard-Jones.
  How do the height and position of the maximum of $\theta_G$ change for, say, $n = 4$, $6$ and $8$?
- **A different kind of bond.**
  Compare with a Morse potential, $u(q) = \left(1 - e^{-\alpha(q-1)}\right)^2 - 1$, whose tail decays exponentially.
- **A rotating dimer.**
  A dimer with angular momentum feels an extra centrifugal term $\lambda/q^2$ in its potential.
  How does a small $\lambda$ change the orbits and the temperature curve? (The turning points then have to be found numerically.)

:::{exercise}
:label: ex-sp5-open

What did you investigate, and what did you predict?
Which features of the temperature curve persist when the potential changes, and which depend on its shape?
Does your refinement check support the conclusion?
:::

## What to hand in

See [](#assignments_page) for the deliverables and the check-in.

---

*This assignment was adapted from a draft by Robin Oosterhoff and Filip Sfetcu.*
