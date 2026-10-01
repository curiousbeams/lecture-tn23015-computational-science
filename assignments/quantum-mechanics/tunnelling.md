---
title: Wave Tunnelling
label: qm-tunnelling_page
authors: [gvarnavides, lathouwers]
numbering:
  enumerator: QM3.%s
---

A particle in a double well can be found on either side of the barrier, even when its energy is below the top of the barrier.
In this assignment you first solve a familiar one-well problem in two independent ways, then use those tools to find the stationary states of a double well.
Combining just two of these states lets you follow a particle as it tunnels back and forth between the wells.

*How does the energy difference between two stationary states set the time it takes a particle to tunnel from one well to the other?*

We use dimensionless units: length in $\sqrt{\hbar/m\omega}$, energy in $\hbar\omega$ and time in $1/\omega$ for a reference frequency $\omega$.
The stationary Schrödinger equation is then

$$
\hat H \psi(x) = E\,\psi(x), \qquad \hat H = -\frac12 \frac{d^2}{dx^2} + V(x),
$$

and we solve it on a finite interval $-L \leq x \leq L$ that stands in for the whole line: its ends are not physical walls.

## Part 1: Stationary states by shooting

For the harmonic oscillator, $V(x) = x^2/2$, the two lowest states are known exactly:

$$
E_0 = \tfrac12, \quad \psi_0(x) = \pi^{-1/4} e^{-x^2/2}, \qquad
E_1 = \tfrac32, \quad \psi_1(x) = \sqrt2\,x\,\psi_0(x).
$$

They are your reference for everything in Parts 1 and 2.

The stationary equation can be written as $\psi'' = (x^2 - 2E)\,\psi$, a second-order ODE that you can rewrite as two first-order ones for $\psi$ and $\psi'$.
Integrating it from $x = 0$ outwards for a *trial* energy $E$ gives a solution that blows up at large $x$ unless $E$ is exactly an energy level: this is the *shooting method* of [](#ordinary-differential-equations-2_page).

- Integrate outward from $x = 0$ to $x = L = 5$ with your RK4 implementation, with step $0.02$, starting from $\psi(0) = 1$, $\psi'(0) = 0$ (an even state).
  Plot the solutions for trial energies $E = 0.3$, $0.5$ and $0.7$.
- The shooting function $F(E) = \psi_E(L)$ changes sign as $E$ passes through an energy level.
  Use your bisection from [](#root-finding_page) on $F$ to find the even ground state, and with $\psi(0) = 0$, $\psi'(0) = 1$, the odd first excited state.
- Extend each solution to $x < 0$ using its parity, normalise it with a numerical integral over $[-L, L]$, and compare energies and wavefunctions with the exact ones.
- Check your result once: halve the integration step, and separately change $L$ from 5 to 4, and report how the energies change.

:::{exercise}
:label: ex-qm1-shooting

Why do trial energies just above and just below the ground-state energy both give a solution that blows up, and with opposite signs?
How do the starting conditions select even and odd states?
:::

:::{exercise}
:label: ex-qm1-precision

How well do your energies and wavefunctions agree with the exact ones?
Which part of the remaining error comes from the integration step, and which from the finite endpoint $L$?
Why does a very narrow final bisection bracket alone not mean that your energy is accurate?
:::

## Part 2: The Hamiltonian as a matrix

Now solve the same problem in a completely different way.
Represent $\psi$ by its values $\psi_i$ on a uniform grid of $N$ points on $[-L, L]$, with spacing $h = 2L/(N-1)$, and set $\psi = 0$ at both ends, so that only the $N-2$ interior values are unknown.
With the second-derivative formula of [](#numerical-differentiation_page),

$$
(\hat H \psi)_i \approx -\frac{\psi_{i+1} - 2\psi_i + \psi_{i-1}}{2h^2} + V(x_i)\,\psi_i ,
$$

the Schrödinger equation becomes a matrix eigenvalue problem $H\vec\psi = E\vec\psi$, which you can solve with the tools of [](#linear-algebra_page).

- Build the matrix $H$ for the oscillator with $L = 5$ and $N = 501$, and find its three lowest eigenvalues and eigenvectors, for example with `scipy.linalg.eigh`.
- Turn each eigenvector into a wavefunction normalised as $\int |\psi|^2 dx = 1$, and restore the zero end values.
- Compare the three lowest energies with $E_n = n + \tfrac12$ and the two lowest with your shooting results, and plot the wavefunctions.

:::{exercise}
:label: ex-qm1-matrix

What are the diagonal and off-diagonal elements of your matrix, and how do the zero boundary values enter the first and last rows?
How did you turn an eigenvector into a normalised wavefunction?
Do the two methods agree with each other and with the exact energies, and what limits the agreement?
:::

## Part 3: Two wells and a small splitting

Replace the oscillator by the symmetric double well

$$
V(x) = V_b \left[\left(\frac{x}{b}\right)^2 - 1\right]^2 ,
$$

with minima at $x = \pm b$ and a central barrier of height $V_b$.
Near each minimum the well is approximately harmonic, $V \approx \tfrac12 \omega_\mathrm{local}^2 (x \mp b)^2$ with $\omega_\mathrm{local} = \sqrt{8V_b}/b$, which suggests energy levels close to $(n + \tfrac12)\,\omega_\mathrm{local}$ in each well.

:::{figure} ../../figures/assignments/double-well-dark.svg
:name: fig-qm1-double-well-dark
:class: hidden dark:block
The double well for $V_b = 5$ and $b = 1$.
:::

:::{figure} ../../figures/assignments/double-well.svg
:name: fig-qm1-double-well
:class: dark:hidden
The double well for $V_b = 5$ and $b = 1$.
:::

- For $V_b = 5$ and $b = 1$, use your Hamiltonian from Part 2 to find the four lowest energies and wavefunctions.
  Plot them, offset by their energies, together with the potential, and check whether the two lowest energies lie below the barrier.
- Calculate the splitting $\Delta E = E_1 - E_0$ for $V_b = 3$, $5$ and $8$ at $b = 1$, and for $b = 0.8$, $1$ and $1.2$ at $V_b = 5$.
- For the case with the smallest splitting, refine the grid and compare the change in $\Delta E$ with $\Delta E$ itself.

:::{exercise}
:label: ex-qm1-pair

Which states are even and which odd?
How does the local harmonic approximation explain why the two lowest energies lie close together, and why are they not exactly equal?
:::

:::{exercise}
:label: ex-qm1-splitting

How does the splitting change when the barrier gets higher, and when the wells move apart?
Relate your answer to what the wavefunctions do inside the barrier.
Is your smallest splitting resolved by your grid?
:::

## Part 4: Tunnelling in time

Each stationary state has a time-independent probability density, but a combination of two of them does not.
For $V_b = 5$ and $b = 1$, with $\phi_0$ and $\phi_1$ the two lowest states,

$$
\psi(x, t) = \frac{1}{\sqrt2}\left[\phi_0(x)\,e^{-iE_0 t} + \phi_1(x)\,e^{-iE_1 t}\right]
$$

solves the time-dependent Schrödinger equation exactly, so you need no new numerical method here.

- Form $\psi(x, 0)$ and check which well holds most of its probability; if necessary, flip the sign of $\phi_1$ so that the particle starts mostly in the left well.
- Compute the probability to be in the left well, $P_L(t) = \int_{-L}^{0} |\psi|^2\,dx$, and in the right well, $P_R(t)$, over a little more than the period $2\pi/\Delta E$, and plot a few snapshots of $|\psi(x,t)|^2$.
- Find the time of the first minimum of $P_L$ and compare it with the prediction $t_\mathrm{transfer} = \pi/\Delta E$; check that $P_L + P_R = 1$ throughout.

:::{exercise}
:label: ex-qm1-dynamics

Why can two stationary states combine into a state whose density moves?
How well localised is your initial state, and do your snapshots and $P_L(t)$ show the predicted transfer and return?
Using Part 3, predict without further calculation how much longer the transfer would take for $V_b = 8$.
:::

## Part 5: Open question

Use your Hamiltonian to investigate one other one-dimensional system of your own choosing.
State your question and a prediction before calculating, compare a small set of parameter values with a reference system, and include one check of the numerical reliability of your conclusion.
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

What did you investigate, and what did you predict?
How do your energies and wavefunctions support or challenge the prediction, and which numerical check supports your conclusion?
:::

## What to hand in

See [](#assignments_page) for the deliverables and the check-in.

---

*This assignment was adapted from a draft by Robin Oosterhoff and Filip Sfetcu.*
