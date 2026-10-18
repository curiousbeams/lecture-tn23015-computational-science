---
title: Phase-Space Geometry
label: sp-lennard-jones_page
authors: [gvarnavides, lathouwers]
numbering:
  enumerator: SP1.%s
---

Two bound atoms vibrate back and forth while their total energy stays fixed.
In this assignment you connect that motion to a closed orbit in position–momentum space, and then use the area enclosed by the orbit to count states.
From that count follow an entropy and a temperature of the system.

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
\frac{dq}{d\tau} = p, \qquad \frac{dp}{d\tau} = F(q) = 12\left(q^{-13} - q^{-7}\right),
$$

where $q$ is the scaled separation, $p$ its conjugate momentum, and $\tau$ the scaled time.
These units are chosen so that the well has its minimum at $q = 1$, the equilibrium separation, with depth $u(1) = -1$.
For energies $-1 < e < 0$ the dimer is bound and vibrates periodically; at $e = 0$ it can fly apart.

At any moment the dimer's state is the pair $(q, p)$, a point in the *phase space* of all such pairs.
As the dimer vibrates at fixed energy $e$, this point traces a closed curve, the *orbit* $h(q, p) = e$, shown in [](#fig-sp5-orbit).
The orbit turns around at the *turning points* $q_\mathrm{in}$ and $q_\mathrm{out}$, where $p = 0$ and so $u(q) = e$.

:::{figure} ../../figures/assignments/lennard-jones-dark.svg
:name: fig-sp5-orbit-dark
:class: hidden dark:block
:enumerator: SP1.1
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

Near its minimum the well is approximately harmonic, $u \approx -1 + \tfrac12 u''(1)\,(q - 1)^2$, which predicts small oscillations with period $T_\mathrm{harm} = 2\pi/\sqrt{u''(1)}$.

:::{exercise}
:label: ex-sp5-turning

1. Plot $u(q)$ and $F(q)$ over a range that shows the repulsive wall, the minimum and the attractive tail.
2. Compute $-du/dq$ with a method from [](#numerical-differentiation_page), and compare it with the exact force $F(q)$.
3. Show, by substituting $y = q^{-6}$ into $u(q) = e$, that the turning points are

   $$
   q_\mathrm{in} = \left(1 + \sqrt{1 + e}\right)^{-1/6}, \qquad q_\mathrm{out} = \left(1 - \sqrt{1 + e}\right)^{-1/6} .
   $$

4. Find the turning points for $e = -0.95$, $-0.5$ and $-0.1$ with a root-finding method from [](#root-finding_page), and tabulate them next to the exact values.
5. Compute $u''(1)$ with a finite difference, and from it $T_\mathrm{harm}$.
6. Explain why there are exactly two turning points for $-1 < e < 0$, and what happens to each of them as $e \to 0^-$.
   Identify which side of the well allows the larger displacement from equilibrium, and explain what this suggests about the average separation of a more energetic dimer.
:::

## Part 2: Vibrations and their period

The period $T(e)$ is the time after which the state $(q, p)$ repeats.
Going from one turning point to the other is only half of it.

:::{exercise}
:label: ex-sp5-period

1. Integrate the equations of motion with your RK4 from [](#ordinary-differential-equations-1_page), starting at a turning point with $p = 0$, for the three energies of Part 1.
2. Plot $q(\tau)$, $p(\tau)$ and the energy error $h(\tau) - e$ over several oscillations.
3. Measure the period, for example from successive times at which $q$ crosses 1 with $p > 0$, for about 15 energies between $-0.99$ and $-0.03$, and plot $T(e)$ together with $T_\mathrm{harm}$.
4. Repeat the run at $e = -0.03$, the most demanding energy, with half the timestep, and report how much the period and the maximum energy error change.
5. Explain how the position and momentum traces change as the energy rises, and why the period grows so strongly near dissociation.
   Explain whether the period approaches $T_\mathrm{harm}$ near $e = -1$, and what shows that the change in period is physical and not caused by numerical energy drift.
:::

:::{dropdown} Hint: choosing a timestep
The steep inner wall is where the force changes fastest.
A timestep of about $10^{-3}$ resolves it well; check by halving it.
Near $e \to 0$ the orbit becomes very long, so you need many steps per period.
:::

## Part 3: Counting states in phase space

The orbit of energy $e$ consists of two branches, $p_\pm(q; e) = \pm\sqrt{2[e - u(q)]}$, between the turning points.
Every state with energy *below* $e$ lies inside it, and the area it encloses is

$$
A(e) = \oint p\,dq = 2\int_{q_\mathrm{in}}^{q_\mathrm{out}} \sqrt{2[e - u(q)]}\, dq .
$$

This area is how statistical mechanics counts states.
Quantum mechanics gives each state of one degree of freedom the same fixed area in phase space, Planck's constant $h$ in physical units, so the number of states with energy below $e$ is $A(e)$ divided by that cell area.
The cell area is a constant, so it drops out of everything we compute from $A(e)$ below, and we work with $A(e)$ itself.
Its derivative,

$$
g(e) = \frac{dA}{de} ,
$$

is the *density of states*: the number of states per unit energy, again up to the constant cell area.

:::{exercise}
:label: ex-sp5-area

1. Plot the branches $p_\pm(q; e)$ on top of your numerical orbits from Part 2.
2. Compute $A(e)$ on a grid of a few hundred energies in $-1 < e < 0$, avoiding the end points, with a method from [](#numerical-integration_page), and verify representative values by refining the integration.
3. Compute $g(e)$ by differentiating your $A(e)$ numerically, and plot it together with your periods $T(e)$ from Part 2.
4. Show that $g(e) = T(e)$.
   Differentiate $A(e)$ under the integral sign (the integrand vanishes at the turning points, so moving them adds nothing), and use $dq/d\tau = p$ to recognise $\oint dq/|p|$ as a time.
5. Explain why $A(e)$ must increase with energy, and which end of the energy range is the hardest to compute accurately.
:::

:::{dropdown} Hint: integrating up to the turning points
The integrand of $A(e)$ goes to zero like a square root at both turning points, where its slope is infinite, so a plain trapezoid rule in $q$ converges slowly.
That matters here, because you differentiate $A(e)$ afterwards, which amplifies small errors.
Substituting $q = c + a\sin z$, with $c = (q_\mathrm{in} + q_\mathrm{out})/2$, $a = (q_\mathrm{out} - q_\mathrm{in})/2$ and $-\pi/2 \leq z \leq \pi/2$, gives a smooth integrand; remember $dq = a\cos z\,dz$.
:::

## Part 4: Entropy and temperature

Use the *Gibbs entropy*, which counts all states with energy below $e$, and the temperature that follows from it.
Relative to a reference energy $e_\mathrm{ref}$,

$$
s_G(e) - s_G(e_\mathrm{ref}) = \ln\frac{A(e)}{A(e_\mathrm{ref})}, \qquad
\frac{1}{\theta_G(e)} = \frac{ds_G}{de} = \frac{g(e)}{A(e)} ,
$$

with $\theta_G = k_\mathrm{B}T_G/\varepsilon$ the dimensionless temperature.

The dynamics gives an independent check.
Since $dq = p\,d\tau$, the integral of $p^2$ over one period is $\oint p\,dq = A(e)$, so the time average over one orbit is $\langle p^2 \rangle_\mathrm{time} = A(e)/T(e)$, which, with $g(e) = T(e)$, equals $\theta_G(e)$.

:::{exercise}
:label: ex-sp5-gibbs

1. Plot $s_G(e)$ and $\theta_G(e) = A(e)/g(e)$ over the energies where your $A(e)$ and $g(e)$ are reliable.
2. Find the energy and the height of the maximum of $\theta_G(e)$, and report how they change when you refine your energy grid.
3. Compute $\langle p^2 \rangle_\mathrm{time}$ over one full orbit at $e = -0.95$, $-0.5$ and $-0.05$, using your trajectories from Part 2, and tabulate it next to $\theta_G(e)$.
4. Explain why $\theta_G(e)$ goes to zero at both ends of the energy range, so that it has a maximum in between.
   Beyond that maximum, adding energy *lowers* the temperature, so the heat capacity is negative: explain what happens there to the mean kinetic energy, and why this is not a phase transition.
:::

## Part 5: Open question

Use your calculation of $A(e)$, $g(e)$ and $\theta_G(e)$ to investigate one question of your own about how the shape of the potential changes the thermodynamics of the dimer.
Some possible directions:

- **A different power law.**
  The family $u_n(q) = q^{-2n} - 2q^{-n}$ keeps the depth and position of the minimum fixed but changes the curvature and the tail; $n = 6$ is Lennard-Jones.
  How do the height and position of the maximum of $\theta_G(e)$ change for $n = 4$, $6$ and $8$?
- **A different kind of bond.**
  Compare with a Morse potential, $u(q) = \left(1 - e^{-\alpha(q-1)}\right)^2 - 1$, whose tail decays exponentially; $\alpha = 6$ gives it the same curvature at the minimum as Lennard-Jones.
  Which parts of the temperature curve change?
- **A rotating dimer.**
  A dimer with angular momentum feels an extra centrifugal term, $u_\lambda(q) = q^{-12} - 2q^{-6} + \lambda q^{-2}$.
  How does a small $\lambda$, for example $0.1$ and $0.3$, change the orbits and the temperature curve? The turning points then have to be found numerically.

:::{exercise}
:label: ex-sp5-open

1. Write down your potential, what it keeps fixed compared with Lennard-Jones, your question and your prediction, before you calculate.
2. Compute $A(e)$, $g(e)$ and $\theta_G(e)$ for each potential you compare.
3. Plot the temperature curves $\theta_G(e)$ together, and tabulate the height and position of each maximum.
4. Repeat one of the calculations with a finer quadrature and energy grid, and report the change in the maximum.
5. Explain whether your results support your prediction.
   Identify which features of the temperature curve persist when the potential changes, and which depend on its shape.
:::

## What to hand in

See [](#assignments_page) for the deliverables and the check-in.

---

*This assignment was adapted from a draft by Robin Oosterhoff and Filip Sfetcu.*
