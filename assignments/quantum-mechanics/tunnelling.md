---
title: Wave Tunnelling
label: qm-tunnelling_page
authors: [gvarnavides, lathouwers]
numbering:
  enumerator: QM3.%s
---

A *double well* is a potential with two minima separated by a barrier.
Classically, a particle whose energy is below the top of the barrier stays in the well where it starts.
Quantum mechanically it does not: it can *tunnel* through the barrier, and its probability moves back and forth between the two wells.
In this assignment you first solve a familiar one-well problem, the harmonic oscillator, in two independent ways, then use those tools to find the stationary states of a double well.
Combining just two of these states lets you follow a particle as it tunnels from one well to the other.

*How does the energy difference between two stationary states set the time it takes a particle to tunnel from one well to the other?*

## The model

We measure length in units of $\sqrt{\hbar/m\omega}$, energy in units of $\hbar\omega$, and time in units of $1/\omega$, where $\omega$ is the angular frequency of the harmonic oscillator of Parts 1 and 2.
Every quantity below, including $x$, $L$, $V_b$ and $b$, is dimensionless.
The stationary Schrödinger equation is then

$$
\hat H \psi(x) = E\,\psi(x), \qquad \hat H = -\frac12 \frac{d^2}{dx^2} + V(x),
$$

and we solve it on a finite interval $-L \leq x \leq L$ that stands in for the whole line: its ends are not physical walls.

Parts 1 and 2 use the harmonic oscillator, $V(x) = x^2/2$.
Parts 3 and 4 use the double well

$$
V(x) = V_b \left[\left(\frac{x}{b}\right)^2 - 1\right]^2 ,
$$

which has minima at $x = \pm b$ and a central barrier of height $V_b$ at $x = 0$, as in [](#fig-qm1-double-well).

:::{figure} ../../figures/assignments/double-well-dark.svg
:name: fig-qm1-double-well-dark
:class: hidden dark:block
:enumerator: QM3.1
The double well for $V_b = 5$ and $b = 1$.
:::

:::{figure} ../../figures/assignments/double-well.svg
:name: fig-qm1-double-well
:class: dark:hidden
The double well for $V_b = 5$ and $b = 1$.
:::

Both potentials are real and symmetric, $V(-x) = V(x)$.
As a result, every stationary state can be chosen to be a real function that is either even, $\psi(-x) = \psi(x)$, or odd, $\psi(-x) = -\psi(x)$.

## Part 1: Stationary states by shooting

For the harmonic oscillator, the two lowest states are known exactly:

$$
E_0 = \tfrac12, \quad \psi_0(x) = \pi^{-1/4} e^{-x^2/2}, \qquad
E_1 = \tfrac32, \quad \psi_1(x) = \sqrt2\,x\,\psi_0(x).
$$

They are your reference for Parts 1 and 2.

The stationary equation for the oscillator can be written as

$$
\psi'' = (x^2 - 2E)\,\psi ,
$$

a second-order ODE that can be integrated from $x = 0$ outwards for any trial energy $E$; by symmetry, $x \geq 0$ is enough.
An even state has $\psi'(0) = 0$, and an odd state has $\psi(0) = 0$.
The other starting value only sets the overall scale, because the equation is linear, so take $\psi(0) = 1$ for an even state and $\psi'(0) = 1$ for an odd one, and normalise afterwards.

Far from the centre, where $x^2 > 2E$, the equation has two kinds of solution: one that grows roughly like $e^{+x^2/2}$ and one that decays like $e^{-x^2/2}$.
A solution started at $x = 0$ is in general a mixture of the two, and the growing part dominates at large $x$, so $\psi$ blows up.
Only when $E$ is exactly an energy level does the growing part vanish, leaving a normalisable state.
As $E$ passes through a level, the coefficient of the growing part changes sign, and so does the *shooting function*

$$
F(E) = \psi_E(L) ,
$$

the value of the trial solution at the end of the interval.
Each energy level is therefore a root of $F$, which you can find with bisection: this is the *shooting method* of [](#ordinary-differential-equations-2_page).

:::{exercise}
:label: ex-qm1-shooting

1. Write the oscillator equation as two first-order ODEs for $\psi$ and $\psi'$.
2. Integrate the even case from $x = 0$ to $x = L = 5$ with your RK4 implementation, with step $0.02$, for the trial energies $E = 0.3$, $0.5$ and $0.7$, and plot the three solutions.
3. Find the even ground state and the odd first excited state by applying your bisection from [](#root-finding_page) to $F(E)$, with brackets around the exact energies.
4. Extend each solution to $x < 0$ using its parity, normalise it with a numerical integral over $[-L, L]$, and plot it together with the exact wavefunction.
5. Tabulate your two energies, the width of the final bisection bracket, and the difference from the exact energy.
6. Explain, using the nodes of your three trial solutions, why $F(E)$ has opposite signs just below and just above $E_0$.
   Explain why a very narrow final bisection bracket alone does not mean that your energy is accurate.
:::

## Part 2: The Hamiltonian as a matrix

Now solve the same problem in a completely different way.
Represent $\psi$ by its values $\psi_i$ on a uniform grid of $N$ points on $[-L, L]$, with spacing $h = 2L/(N - 1)$, and set $\psi = 0$ at both ends, so that only the $N - 2$ interior values are unknown.
With the second-derivative formula of [](#numerical-differentiation_page),

$$
(\hat H \psi)_i \approx -\frac{\psi_{i+1} - 2\psi_i + \psi_{i-1}}{2h^2} + V(x_i)\,\psi_i ,
$$

the Schrödinger equation becomes a matrix eigenvalue problem $H\vec\psi = E\vec\psi$, which you can solve with the tools of [](#linear-algebra_page).
$H$ is a real symmetric matrix, so its eigenvectors are real, like the stationary states they represent; their overall sign is arbitrary.
An eigenvector $u$ comes out with $\sum_i u_i^2 = 1$, and the wavefunction $\psi_i = u_i/\sqrt{h}$ then satisfies $\int \psi^2\,dx \approx h\sum_i \psi_i^2 = 1$.

:::{exercise}
:label: ex-qm1-matrix

1. Write down the diagonal and off-diagonal elements of $H$, and the first and last rows, where the zero end values enter.
2. Build $H$ for the oscillator with $L = 5$ and $N = 501$, and compute its three lowest eigenvalues and eigenvectors, for example with `scipy.linalg.eigh`.
3. Normalise each eigenvector as a wavefunction, restore the zero end values, and plot the three wavefunctions.
4. Tabulate the three lowest energies next to the exact $E_n = n + \tfrac12$ and, for the two lowest, your shooting results.
5. Explain whether the two methods agree with each other and with the exact energies, and what limits the accuracy of each.
:::

## Part 3: Two wells and a small splitting

Near each of its minima, the double well looks like a harmonic oscillator with some local frequency $\omega_\mathrm{local}$.
Each well on its own would then have energy levels close to $(n + \tfrac12)\,\omega_\mathrm{local}$.

:::{exercise}
:label: ex-qm1-pair

1. Show, by expanding $V$ to second order around $x = b$, that $V \approx \tfrac12\,\omega_\mathrm{local}^2\,(x - b)^2$ with $\omega_\mathrm{local} = \sqrt{8V_b}/b$.
2. Compute the four lowest energies and wavefunctions for $V_b = 5$ and $b = 1$ with your Hamiltonian from Part 2.
3. Plot the four wavefunctions, offset by their energies, together with the potential, and identify each as even or odd.
4. Verify that the two lowest energies lie below the barrier, and compare them with $\tfrac12\,\omega_\mathrm{local}$.
5. Explain how the local harmonic approximation accounts for the two lowest energies lying close together, and why they are not exactly equal.
:::

:::{exercise}
:label: ex-qm1-splitting

1. Compute the splitting $\Delta E = E_1 - E_0$ for $V_b = 3$, $5$ and $8$ at $b = 1$, and for $b = 0.8$, $1$ and $1.2$ at $V_b = 5$.
2. Repeat the case with the smallest splitting on a finer grid, $N = 1001$, and compare the change in $\Delta E$ with $\Delta E$ itself.
3. Explain how the splitting changes when the barrier gets higher and when the wells move apart, and relate this to what the wavefunctions do inside the barrier.
   State whether your smallest splitting is resolved by your grid.
:::

## Part 4: Tunnelling in time

Each stationary state has a time-independent probability density, but a combination of two of them does not.
For $V_b = 5$ and $b = 1$, with $\phi_0$ and $\phi_1$ the two lowest states from Part 3, consider

$$
\psi(x, t) = \frac{1}{\sqrt2}\left[\phi_0(x)\,e^{-iE_0 t} + \phi_1(x)\,e^{-iE_1 t}\right] .
$$

In our units the time-dependent Schrödinger equation is $i\,\partial\psi/\partial t = \hat H\psi$.
The probability to find the particle in the left well is $P_L(t) = \int_{-L}^{0} |\psi(x, t)|^2\,dx$, and $P_R(t)$ is the same integral over the right half.

:::{exercise}
:label: ex-qm1-dynamics

1. Show that $\psi(x, t)$ solves the time-dependent Schrödinger equation, and that its density is $|\psi|^2 = \tfrac12\left[\phi_0^2 + \phi_1^2 + 2\phi_0\phi_1\cos(\Delta E\,t)\right]$.
2. Form $\psi(x, 0)$, flipping the sign of $\phi_1$ if necessary so that the particle starts mostly in the left well, and compute $P_L(0)$.
3. Compute $P_L(t)$ and $P_R(t)$ over a little more than one period $2\pi/\Delta E$, verify that $P_L + P_R = 1$ throughout, and plot $|\psi(x, t)|^2$ at a few times.
4. Find the time of the first minimum of $P_L$, and compare it with the prediction $t_\mathrm{transfer} = \pi/\Delta E$.
5. Explain why $P_L(0)$ is not exactly 1, and whether your snapshots and $P_L(t)$ show the predicted transfer and return.
   Predict, using Part 3 and without further calculation, how much longer the transfer would take for $V_b = 8$.
:::

## Part 5: Open question

Use your Hamiltonian to investigate one other one-dimensional system of your own choosing, and compare it with a reference system such as the symmetric double well.
Some possible directions:

- **An asymmetric double well.**
  Add a tilt, $V(x) = V_b[(x/b)^2 - 1]^2 + \eta\,x/b$, so that one well is deeper than the other.
  How does breaking the symmetry change the spectrum, the localisation of the lowest states, and tunnelling?
- **A triple well.**
  How do the lowest states spread over three wells, and how does the spectrum compare with the double well?
- **A different shape.**
  A finite square well or a Morse potential: how does the shape of the potential set the bound-state energies and wavefunctions?
  Where the potential allows the particle to escape, be careful to tell real bound states from states of the finite box.

:::{exercise}
:label: ex-qm1-open

1. Write down your potential, your question and your prediction before you calculate.
2. Compute the lowest energies and wavefunctions for a small set of parameter values, and for your reference system.
3. Plot the spectrum against your parameter, and the wavefunctions at representative values.
4. Include one check, with a larger interval or a finer grid, that supports your conclusion.
5. Explain whether your energies and wavefunctions support your prediction.
:::

## What to hand in

See [](#assignments_page) for the deliverables and the check-in.

---

*This assignment was adapted from a draft by Robin Oosterhoff and Filip Sfetcu.*
