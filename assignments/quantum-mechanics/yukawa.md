---
title: Quantum Bound States
label: qm-yukawa_page
authors: [gvarnavides, lathouwers]
numbering:
  enumerator: QM2.%s
---

The Yukawa potential describes an attraction that decays exponentially with distance, like the force between nucleons carried by a massive particle.
In this assignment you study a one-dimensional, smoothed version of it.
You find its bound states, then locate the coupling strength at which a new bound state appears and look at the bound states in momentum space.

*How do the strength and range of a short-range attraction determine its bound states, and how can we tell real bound states from numerical artefacts?*

## The model

We use units with $\hbar = m = 1$ and the regularised Yukawa-like potential

$$
V_Y(x) = -g\,\frac{e^{-\mu r_a(x)}}{r_a(x)}, \qquad r_a(x) = \sqrt{x^2 + a^2}, \qquad g, \mu, a > 0 .
$$

The coupling $g$ sets the overall strength, $\mu$ the exponential decay, and $a$ smooths the potential at the origin; use $a = 0.5$ throughout.
The Hamiltonian is $\hat H = -\tfrac12\, d^2/dx^2 + V_Y(x)$.
Since $V_Y \to 0$ far away, a normalisable state with energy $E < 0$ is a bound state.

:::{figure} ../../figures/assignments/yukawa-potential-dark.svg
:name: fig-qm5-potential-dark
:class: hidden dark:block
The potential for $g = 4$ and $\mu = 1$.
The decay length $1/\mu$ describes how fast the tail falls off; it is not a sharp edge.
:::

:::{figure} ../../figures/assignments/yukawa-potential.svg
:name: fig-qm5-potential
:class: dark:hidden
The potential for $g = 4$ and $\mu = 1$.
The decay length $1/\mu$ describes how fast the tail falls off; it is not a sharp edge.
:::

## Part 1: Strength, range and force

The depth at the centre is $V_Y(0) = -(g/a)\,e^{-\mu a}$, so changing $\mu$ at fixed $g$ changes both the range and the depth.
To compare ranges at a *fixed depth*, choose $g(\mu) = 4\,e^{(\mu - 1)a}$, which keeps $V_Y(0)$ equal to its value for $g = 4$, $\mu = 1$.

- Plot $V_Y$ for $g = 1$, $2$, $4$ at $\mu = 1$, and for $\mu = 0.5$, $1$, $2$ at fixed depth.
- For the three fixed-depth potentials, find the half-depth distance $x_{1/2} > 0$, where $V_Y(x_{1/2}) = \tfrac12 V_Y(0)$, with a root-finding method from [](#root-finding_page), and compare it with $1/\mu$.
- Compute the force $F = -dV_Y/dx$ with a finite difference from [](#numerical-differentiation_page), compare it with
  $$
  F(x) = -g\, e^{-\mu r_a}\, \frac{x\,(\mu r_a + 1)}{r_a^3},
  $$
  and find where $|F|$ is largest.

:::{exercise}
:label: ex-qm5-shape

What does changing $g$ do to the potential, and what does changing $\mu$ do?
Why is changing $\mu$ at fixed $g$ not a pure change of range?
How does $x_{1/2}$ compare with $1/\mu$, and where is the attraction strongest?
:::

## Part 2: Bound states, and how to trust them

Represent the Hamiltonian on a grid as in the other quantum assignments: $M$ interior points with spacing $h$ on $[-L, L]$, $\psi = 0$ at the two ends, and the three-point second derivative.
The zero end values stand in for the decay of $\psi$ at infinity; they are not physical walls.

- For $g = 4$, $\mu = 1$, $L = 20$ and $h = 0.05$, find the lowest few eigenvalues and eigenvectors with the tools of [](#linear-algebra_page).
  Turn the eigenvectors into wavefunctions normalised as $\int |\psi|^2 dx = 1$.
- For every state with $E < 0$, plot the probability density and determine its parity, number of nodes, $\langle x \rangle$ and $\Delta x$, and the kinetic and potential energies $\langle T \rangle$ and $\langle V \rangle$; check that $\langle T \rangle + \langle V \rangle = E$.
- Repeat with $L = 30$, and separately with $h = 0.025$, and decide which states are real bound states: their energies must not change, within your accuracy, when you change the box.

:::{dropdown} Hint: a tridiagonal matrix
The Hamiltonian only couples neighbouring points, so it is a symmetric tridiagonal matrix: diagonal $1/h^2 + V(x_i)$, off-diagonals $-1/(2h^2)$.
`scipy.linalg.eigh_tridiagonal(d, e, select="i", select_range=(0, 5))` uses exactly that structure and is fast even for thousands of points.
:::

:::{exercise}
:label: ex-qm5-states

How do parity, number of nodes and spatial extent change from one bound state to the next?
Why must $\langle x \rangle$ vanish for these states?
Use $\langle T \rangle$ and $\langle V \rangle$ to describe how tightly each state is bound.
:::

:::{exercise}
:label: ex-qm5-box

Which state is most sensitive to $L$, and why?
What evidence tells you the least-bound state from the first positive-energy state of the box?
:::

## Part 3: When does a new bound state appear?

A purely attractive well in one dimension always has a bound ground state, however weak.
The first *excited* state, odd with one node, only becomes bound once $g$ exceeds a critical coupling $g_c$, where its energy crosses zero.

- At $\mu = 1$, follow the energies of the lowest states as a function of $g$, and choose an interval in which the odd state crosses $E = 0$.
- Find $g_c(L)$, the coupling at which the odd state's energy is zero in a box of half-width $L$, by applying bisection to $g$ itself: each evaluation is a full diagonalisation.
  Do this for $L = 20$, $30$, $40$ and $60$ at $h = 0.1$, and check one $L$ at $h = 0.05$.
- A finite box always pushes energies up, so $g_c(L)$ is too large and drifts with $L$.
  Fit $g_c(L) = g_c(\infty) + A/L$ to estimate the critical coupling on the infinite line, and test the estimate by leaving out the smallest box.

:::{exercise}
:label: ex-qm5-threshold

What value of $g_c(\infty)$ do your data support, and to how many digits?
How large is the finite-box shift compared with the effect of the grid spacing, and why is a single value of $L$ especially unreliable close to the threshold?
:::

## Part 4: Bound states in momentum space

A state localised in position needs a spread of momenta.
The momentum wavefunction is $\tilde\psi(k) = (2\pi)^{-1/2} \int \psi(x)\, e^{-ikx}\, dx$.

- For the ground state and the least-bound state of Part 2, compute $\tilde\psi(k)$ with the FFT from [](#fourier-transforms-1_page), with the correct physical scaling and $k$ axis, and check that $\int |\tilde\psi|^2 dk = 1$.
- Calculate $\Delta k$ and the product $\Delta x\,\Delta k$ for both states, and plot their position and momentum densities.
- Compare $\langle k^2 \rangle / 2$ with $\langle T \rangle$ from Part 2, and check whether the difference shrinks when you refine the grid.

:::{dropdown} Hint: from FFT to $\tilde\psi(k)$
For samples $x_j = x_\mathrm{start} + jh$, $j = 0, \dots, N - 1$, with raw FFT $F_m$,
$$
\tilde\psi(k_m) \approx \frac{h}{\sqrt{2\pi}}\, e^{-ik_m x_\mathrm{start}}\, F_m, \qquad k_m = 2\pi f_m ,
$$
with $f_m$ from `np.fft.fftfreq(N, h)`.
Sample $[-L, L)$, i.e. include the left end point but not the right, and shift $\tilde\psi$ and $k$ together if you want $k = 0$ in the middle.
:::

:::{exercise}
:label: ex-qm5-momentum

Which state has the larger $\Delta x$, and which the larger $\Delta k$?
Does each satisfy $\Delta x\,\Delta k \geq 1/2$, and which one comes closer to the limit?
Why is the momentum density of a real, odd wavefunction still symmetric in $k$?
:::

## Part 5: Open question

Change the potential in one controlled way and investigate one question of your own.
State the question and a prediction before calculating, say which depth or range measure you keep fixed, vary one new parameter over a few values, and include one numerical check.
Some possible directions:

- **Two centres.**
  Split the attraction over two centres a distance $d$ apart, keeping the total coupling fixed:
  $$
  V_d(x) = -\frac{g}{2}\sum_{\sigma = \pm1} \frac{e^{-\mu\sqrt{(x - \sigma d/2)^2 + a^2}}}{\sqrt{(x - \sigma d/2)^2 + a^2}} ,
  $$
  for example with $g = 2$ and $d = 0$, $2$, $4$, $6$, $8$.
  How do the lowest energies, their splitting and the densities change as the centres move apart?
- **Unequal centres.**
  Make one of the two centres deeper than the other.
  What happens to the localisation of the lowest states?
- **Smoothing.**
  Vary $a$ while keeping the depth $V_Y(0)$ fixed.
  How much does the detailed shape near the centre matter for the bound states?

:::{exercise}
:label: ex-qm5-open

What did you investigate, and what did you predict?
Which of your observations are controlled mainly by the depth and range, and which by the detailed shape or the new length scale?
Which numerical check supports your conclusion?
:::

## What to hand in

See [](#assignments_page) for the deliverables and the check-in.

---

*This assignment was adapted from a draft by Robin Oosterhoff and Filip Sfetcu.*
