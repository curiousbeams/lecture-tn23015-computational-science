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
[](#fig-qm5-potential) shows the reference potential, $g = 4$ and $\mu = 1$.
The Hamiltonian is $\hat H = -\tfrac12\, d^2/dx^2 + V_Y(x)$.
Since $V_Y \to 0$ far away, a normalisable state with energy $E < 0$ is a bound state.

:::{figure} ../../figures/assignments/yukawa-potential-dark.svg
:name: fig-qm5-potential-dark
:class: hidden dark:block
:enumerator: QM2.1
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

The potential has two parameters that we vary: $g$ and $\mu$.
They do not act independently, because the depth at the centre,

$$
V_Y(0) = -\frac{g}{a}\,e^{-\mu a} ,
$$

depends on both.
We therefore compare two families of potentials:

1. **Changing the strength at fixed range:** $\mu = 1$, with $g = 1$, $2$ and $4$.
2. **Changing the range at fixed depth:** $\mu = 0.5$, $1$ and $2$, with $g$ no longer free but chosen so that $V_Y(0)$ keeps its value for the reference potential $g = 4$, $\mu = 1$.
   Setting $(g/a)\,e^{-\mu a} = (4/a)\,e^{-a}$ gives

   $$
   g(\mu) = 4\,e^{(\mu - 1)a} ,
   $$

   that is $g = 3.12$, $4$ and $6.59$ for $\mu = 0.5$, $1$ and $2$.

To measure the width of a well, define the half-depth distance $x_{1/2} > 0$ by $V_Y(x_{1/2}) = \tfrac12 V_Y(0)$.
The force on the particle is $F = -dV_Y/dx$, which works out to

$$
F(x) = -g\, e^{-\mu r_a}\, \frac{x\,(\mu r_a + 1)}{r_a^3} .
$$

:::{exercise}
:label: ex-qm5-shape

1. Plot $V_Y$ for the three potentials of the first family, and for the three potentials of the second family.
2. Find $x_{1/2}$ for each potential of the second family with a root-finding method from [](#root-finding_page), and tabulate it next to $1/\mu$.
3. Compute the force of the reference potential with a central finite difference from [](#numerical-differentiation_page), and plot it together with the exact $F(x)$.
4. Find the position where $|F|$ is largest.
5. Explain what changing $g$ does to the potential, what changing $\mu$ does, and why changing $\mu$ at fixed $g$ is not a pure change of range.
   Explain how $x_{1/2}$ compares with $1/\mu$, and where and why the attraction is strongest.
:::

## Part 2: Bound states, and how to trust them

From here on, use the reference potential $g = 4$, $\mu = 1$, unless stated otherwise.

**The Hamiltonian on a grid.**
Represent $\psi$ on $M$ interior points $x_j = -L + jh$, $j = 1, \dots, M$, with spacing $h = 2L/(M + 1)$, and set $\psi = 0$ at the two end points $x = \pm L$.
These zero end values stand in for the decay of $\psi$ at infinity; they are not physical walls.
With the three-point second derivative from [](#numerical-differentiation_page),

$$
(\hat H\psi)_j = -\frac{\psi_{j+1} - 2\psi_j + \psi_{j-1}}{2h^2} + V_Y(x_j)\,\psi_j ,
$$

so $\hat H$ becomes a symmetric tridiagonal $M \times M$ matrix, with diagonal $1/h^2 + V_Y(x_j)$ and off-diagonals $-1/(2h^2)$.
Its eigenvalues are the energies, as in [](#linear-algebra_page).
An eigenvector $u$ comes out with $\sum_j u_j^2 = 1$; the wavefunction $\psi_j = u_j/\sqrt{h}$ then satisfies $\int |\psi|^2\,dx \approx h\sum_j \psi_j^2 = 1$.

**Describing a state.**
Because $V_Y$ is symmetric, every state has a definite *parity*: it is even, $\psi(-x) = \psi(x)$, or odd, $\psi(-x) = -\psi(x)$.
Its *nodes* are the points where $\psi$ changes sign.
For a real, normalised $\psi$, the expectation value of a quantity $A$ is $\langle A \rangle = \int \psi\,\hat A\,\psi\,dx$, which gives

$$
\langle x \rangle = \int x\,|\psi|^2\,dx , \qquad
\Delta x = \sqrt{\langle x^2 \rangle - \langle x \rangle^2} ,
$$

$$
\langle T \rangle = -\frac12 \int \psi\,\psi''\,dx , \qquad
\langle V \rangle = \int V_Y\,|\psi|^2\,dx .
$$

$\Delta x$ measures how far the state is spread out, and the kinetic and potential energies $\langle T \rangle$ and $\langle V \rangle$ add up to $\langle H \rangle = \langle T \rangle + \langle V \rangle$, which equals $E$ for an eigenstate.
On the grid, the integrals become sums times $h$, and $\psi''$ is the same three-point formula as in the Hamiltonian.

:::{exercise}
:label: ex-qm5-states

1. Build the Hamiltonian matrix for $L = 20$ and $h = 0.05$.
2. Compute its six lowest eigenvalues and eigenvectors, for example with `scipy.linalg.eigh_tridiagonal(d, e, select="i", select_range=(0, 5))`, where `d` and `e` hold the diagonal and off-diagonal.
3. Normalise the eigenvectors as wavefunctions, and plot the probability density of every state with $E < 0$.
4. Tabulate, for each of these states, its energy, parity, number of nodes, $\langle x \rangle$, $\Delta x$, $\langle T \rangle$ and $\langle V \rangle$, and verify that $\langle T \rangle + \langle V \rangle = E$.
5. Explain how parity, number of nodes and spatial extent change from one bound state to the next, and why $\langle x \rangle$ must vanish.
   Explain what $\langle T \rangle$ and $\langle V \rangle$ tell you about how tightly each state is bound.
:::

:::{exercise}
:label: ex-qm5-box

1. Repeat the calculation with $L = 30$, and separately with $h = 0.025$.
2. Tabulate how much each of the four lowest energies changes, including the lowest state with $E > 0$.
3. Identify the real bound states: their energies must not change, within your accuracy, when you change the box or the grid.
4. Explain which bound state is most sensitive to $L$, and why.
   Explain what evidence distinguishes the least-bound state from the lowest positive-energy state of the box.
:::

## Part 3: When does a new bound state appear?

A purely attractive well in one dimension always has a bound ground state, however weak.
Excited states are different.
Number the energies from the bottom, $E_0 < E_1 < E_2 < \dots$
In one dimension, state $n$ has exactly $n$ nodes, and for a symmetric potential the states alternate between even and odd, starting with an even ground state.
So $E_1$ always belongs to the odd state with one node, whether it is bound or not.
It becomes bound only once $g$ exceeds a *critical coupling* $g_c$, where $E_1(g_c) = 0$.

In a box of half-width $L$, the same condition $E_1 = 0$ defines $g_c(L)$.
The box pushes energies up, so $g_c(L)$ is too large, and it drifts towards the infinite-line value as $L$ grows.
For large $L$ the drift is approximately

$$
g_c(L) = g_c(\infty) + \frac{A}{L} ,
$$

which lets you extrapolate to $L \to \infty$.

:::{exercise}
:label: ex-qm5-threshold

Keep $\mu = 1$.

1. Plot the three lowest energies against $g$ for $0.5 \leq g \leq 3$, with $L = 30$ and $h = 0.1$, and read off an interval of $g$ in which $E_1$ crosses zero.
2. Find $g_c(L)$ for $L = 20$, $30$, $40$ and $60$ at $h = 0.1$, by bisection on $g$ itself; each evaluation of $E_1(g)$ is one diagonalisation.
3. Repeat the calculation for one value of $L$ at $h = 0.05$.
4. Fit $g_c(L) = g_c(\infty) + A/L$ to your four values, and repeat the fit without the smallest box.
5. Explain what value of $g_c(\infty)$ your data support, and to how many digits.
   Compare the size of the finite-box shift with the effect of the grid spacing, and explain why a single value of $L$ is especially unreliable close to the threshold.
:::

## Part 4: Bound states in momentum space

A state localised in position needs a spread of momenta.
The momentum wavefunction is

$$
\tilde\psi(k) = \frac{1}{\sqrt{2\pi}} \int \psi(x)\, e^{-ikx}\, dx ,
$$

and $|\tilde\psi(k)|^2$ is the probability density of the wavenumber $k$; with $\hbar = 1$, the momentum is $p = k$.
Its moments $\langle k \rangle$ and $\langle k^2 \rangle$, and the spread $\Delta k = \sqrt{\langle k^2 \rangle - \langle k \rangle^2}$, are defined as for $x$, with $|\tilde\psi|^2$ in place of $|\psi|^2$.
Since $T = p^2/2$ with $m = 1$, the kinetic energy of a state can also be computed in momentum space, as $\langle T \rangle = \langle k^2 \rangle / 2$.

:::{exercise}
:label: ex-qm5-momentum

Use the ground state and the least-bound state from Part 2.

1. Compute $\tilde\psi(k)$ for both states with the FFT from [](#fourier-transforms-1_page), with the physical scaling and $k$ axis of the hint below, and verify that $\int |\tilde\psi|^2\,dk = 1$.
2. Plot the position and momentum densities of both states.
3. Compute $\Delta k$ and the product $\Delta x\,\Delta k$ for both states.
4. Compute $\langle k^2 \rangle / 2$ for each state, and compare it with $\langle T \rangle$ of the same state from Part 2.
   Repeat the comparison for the ground state at $h = 0.025$.
5. Explain which state has the larger $\Delta x$ and which the larger $\Delta k$, whether each satisfies $\Delta x\,\Delta k \geq 1/2$, and which comes closer to the limit.
   Explain why the momentum density of a real, odd wavefunction is still symmetric in $k$.
:::

:::{dropdown} Hint: from FFT to $|\tilde\psi(k)|^2$
Take `F = np.fft.fft(psi)` of your $N$ grid values, spaced by $h$.
The wavenumbers are `k = 2 * np.pi * np.fft.fftfreq(N, h)`, spaced by $2\pi/(Nh)$, and the momentum density at those $k$ is

$$
|\tilde\psi(k)|^2 \approx \frac{h^2}{2\pi}\,|F|^2 .
$$

It covers negative and positive $k$ alike: do not fold or double it.
Apply `np.fft.fftshift` to `k` and to the density together, as in [](#fourier-transforms-1_page), to order them from negative to positive $k$.
:::

## Part 5: Open question

Change the potential in one controlled way and investigate one question of your own about how its shape controls the bound states.
Keep everything else, including the solver, the same, and decide which depth or range measure you hold fixed.
Some possible directions:

- **Two centres.**
  Split the attraction over two centres a distance $d$ apart, keeping the total coupling fixed:
  $$
  V_d(x) = -\frac{g}{2}\sum_{\sigma = \pm1} \frac{e^{-\mu\sqrt{(x - \sigma d/2)^2 + a^2}}}{\sqrt{(x - \sigma d/2)^2 + a^2}} ,
  $$
  with $g = 2$, $\mu = 1$ and $d = 0$, $2$, $4$, $6$, $8$; each centre on its own then binds one state.
  How do the two lowest energies, the gap between them, and their densities change as the centres move apart?
- **Unequal centres.**
  Give the two centres of $V_d$ different couplings at a fixed separation, for example $d = 6$.
  How does the imbalance change where the two lowest states are localised?
- **Smoothing.**
  Vary $a$, for example $a = 0.25$, $0.5$ and $1$, while keeping the depth $V_Y(0)$ fixed by adjusting $g$.
  How much does the detailed shape near the centre matter for the bound states?

:::{exercise}
:label: ex-qm5-open

1. Write down your modified potential, the quantity you hold fixed, your question, and your prediction, before you calculate.
2. Compute the lowest energies and densities while you vary one new parameter over a few values.
3. Plot the lowest energies against your parameter, and the densities of the two lowest states at a small, an intermediate and a large value.
4. Include one check, with a larger box or a finer grid, for a representative value of your parameter.
5. Explain whether your results support your prediction.
   Identify which of your observations are controlled mainly by the depth and range of the attraction, and which by the detailed shape or the new length scale.
:::

## What to hand in

See [](#assignments_page) for the deliverables and the check-in.

---

*This assignment was adapted from a draft by Robin Oosterhoff and Filip Sfetcu.*
