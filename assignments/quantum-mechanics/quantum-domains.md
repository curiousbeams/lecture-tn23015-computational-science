---
title: Quantum Domains
label: qm-quantum-domains_page
authors: [gvarnavides, lathouwers]
numbering:
  enumerator: QM1.%s
---

The shape of a hard wall decides which standing waves fit inside it.
In this assignment you calculate the states of a particle confined to a disk and to a ring, first analytically with Bessel functions and then numerically on a square grid.
The grid lets you study shapes that radial solutions cannot describe, such as a ring with an off-centre hole.

*How do a region's size, its narrowest widths, and its symmetries set its energies and wavefunctions?*

## The model

A particle of mass $m$ moves in a two-dimensional region with hard walls: the potential is zero inside and infinite outside, so the wavefunction vanishes on every boundary.
Measuring lengths in units of the outer radius $R_\mathrm{out}$ and energy in units of $\hbar^2/(2mR_\mathrm{out}^2)$, the Schrödinger equation inside the region becomes

$$
-\nabla^2 \psi = \epsilon\,\psi .
$$

The disk has radius 1.
An annulus also has an inner wall of radius $\rho$, leaving a ring of width $w = 1 - \rho$; moving the centre of the inner circle by $\delta$ along $x$ gives an eccentric annulus, with $|\delta| + \rho < 1$.

:::{figure} ../../figures/assignments/domains-dark.svg
:name: fig-qm4-domains-dark
:class: hidden dark:block
The three regions; the shaded part is where the particle can be.
Not to scale.
:::

:::{figure} ../../figures/assignments/domains.svg
:name: fig-qm4-domains
:class: dark:hidden
The three regions; the shaded part is where the particle can be.
Not to scale.
:::

## Part 1: The disk

For a circular boundary the wavefunction separates as $\psi = R_\ell(r)\,e^{i\ell\phi}/\sqrt{2\pi}$, with $\ell = 0, \pm1, \pm2, \dots$, and the radial part obeys

$$
R_\ell'' + \frac{1}{r}R_\ell' + \left(\epsilon - \frac{\ell^2}{r^2}\right)R_\ell = 0 .
$$

Its solutions are the Bessel functions $J_{|\ell|}(kr)$ and $Y_{|\ell|}(kr)$ with $k = \sqrt\epsilon$, available as `scipy.special.jv` and `scipy.special.yv`.
Inside the disk only $J_{|\ell|}$ is allowed, and the wall at $r = 1$ requires $J_{|\ell|}(k) = 0$: the allowed energies are $\epsilon = k^2$ at the zeros of $J_{|\ell|}$.

- Plot $J_0$, $J_1$ and $J_2$ over a range showing their first two zeros, and $Y_0$ near zero.
- Use the plots to choose brackets, and find the first zero for $|\ell| = 0, 1, 2$ and the second for $\ell = 0$ with your own bisection from [](#root-finding_page).
  Convert them to energies and order them, keeping their $(\ell, n)$ labels.
- Normalise the lowest $\ell = 0$ and $|\ell| = 1$ radial states with $\int_0^1 |R_\ell|^2 r\,dr = 1$ using [](#numerical-integration_page), and plot the radial probabilities $r|R_\ell|^2$.

:::{exercise}
:label: ex-qm4-disk

How do the zeros of the Bessel functions select the allowed energies, and why must $Y_0$ be excluded from the disk?
Why do $+\ell$ and $-\ell$ have the same energy, and how does the $\ell^2/r^2$ term explain the difference between the two radial probabilities you plotted?
:::

## Part 2: Opening a hole

Now the origin is outside the region, so both Bessel functions are allowed.
The radial function

$$
R_\ell(r) \propto J_{|\ell|}(kr)\,Y_{|\ell|}(k\rho) - Y_{|\ell|}(kr)\,J_{|\ell|}(k\rho)
$$

vanishes at the inner wall $r = \rho$ by construction, and it also vanishes at $r = 1$ when

$$
D_\ell(k) = J_{|\ell|}(k\rho)\,Y_{|\ell|}(k) - Y_{|\ell|}(k\rho)\,J_{|\ell|}(k) = 0 .
$$

- For $\rho = 0.35$, plot $D_\ell(k)$ for $\ell = 0, 1, 2$ and find the lowest root of each, making sure your scan does not miss a lower one.
- Normalise the lowest $\ell = 0$ and $|\ell| = 1$ annulus states with $\int_\rho^1 |R_\ell|^2 r\,dr = 1$, and compare disk and annulus in an energy-level diagram and in their radial probabilities.
- Repeat the energy calculation for $\rho = 0.25$ and $0.45$, and plot how the lowest $\ell = 0$, $|\ell| = 1$ and $|\ell| = 2$ energies, and the second $\ell = 0$ level, depend on the width $w$.

:::{exercise}
:label: ex-qm4-hole

Why can the annulus contain a $Y_\ell$ part when the disk cannot?
Which of the lowest $|\ell| = 0, 1, 2$ levels rises most when the hole is opened, and how does the disk's radial probability explain it?
:::

:::{exercise}
:label: ex-qm4-width

How do radial and angular excitations respond differently as the ring gets narrower?
Which degeneracies survive when the hole is opened or widened, and which symmetry protects them?
:::

## Part 3: A Hamiltonian on a square grid

An off-centre hole destroys the rotational symmetry, so the radial method no longer works.
Instead, represent $\psi$ on a square grid that covers $[-1, 1]^2$, with an odd number $N$ of points per axis, spacing $h = 2/(N - 1)$ and coordinates $x_i = \left(i - \tfrac{N-1}{2}\right)h$, the same for $y$.
Check that opposite grid points have *exactly* opposite coordinates.
Mark the allowed points with a Boolean mask: $x^2 + y^2 < 1$ for the disk, and additionally $(x - \delta)^2 + y^2 > \rho^2$ for an annulus.

The five-point formula from [](#partial-differential-equations-1_page) gives

$$
-\nabla^2\psi_{i,j} \approx \frac{4\psi_{i,j} - \psi_{i+1,j} - \psi_{i-1,j} - \psi_{i,j+1} - \psi_{i,j-1}}{h^2} ,
$$

where a neighbour outside the region has $\psi = 0$.
Numbering the allowed points one after the other turns this into a symmetric matrix eigenvalue problem, as in [](#linear-algebra_page).

- Build the matrix for the disk and for the annulus with $\rho = 0.35$, $\delta = 0$, for $N = 41$ and $N = 61$, and find their lowest eigenvalues and eigenvectors, for example with `scipy.linalg.eigh(H, subset_by_index=[0, 9])`.
- Compare the lowest five disk energies, and the lowest annulus energies, with Parts 1 and 2 on both grids.
- Check that your matrix is symmetric and your states are normalised, and plot a few probability densities on the grid.

:::{dropdown} Hint: building the matrix
Give each allowed point an index with `index = -np.ones((N, N), int); index[mask] = np.arange(mask.sum())`.
Then loop over the allowed points: put $4/h^2$ on the diagonal, and $-1/h^2$ in the column of every neighbour that is itself allowed.
A neighbour outside the region simply contributes nothing.
Keep $N \leq 61$; for $N = 61$ the disk has about 2800 unknowns, which a dense eigensolver handles in seconds.

Why the exactly symmetric coordinates matter: some grid points lie exactly on a wall.
If $x$ and $-x$ differ in their last digit, such a point can be kept on one side and dropped on the other, and the region silently loses its symmetry.
:::

:::{exercise}
:label: ex-qm4-grid

How do the energies change as the grid is refined, and why is the error larger for the annulus than for the disk?
Why does refining the grid not remove the error from a curved wall built out of square cells as quickly as you might expect?
:::

:::{exercise}
:label: ex-qm4-doublets

How well does the grid reproduce the degenerate pairs of the disk?
Why can the two states of a degenerate pair come out with different orientations, even when their energies agree?
:::

## Part 4: Moving the hole

Return to $\rho = 0.35$ and move the inner circle along $x$ by $\delta = 0$, $0.10$ and $0.20$.
The reflection $y \to -y$ is still a symmetry, but rotations are not.

- Before calculating, predict which side of the ring gets wider, where the ground state will sit, and what will happen to the lowest degenerate pair.
- For each $\delta$, compute the lowest five energies, the ground state's $\langle x \rangle$, and the splitting of the two levels that came from the lowest $|\ell| = 1$ pair.
- At $\delta = 0.20$, plot the signed wavefunctions of those two levels and classify them as even or odd under $y \to -y$.
- Repeat $\delta = 0.20$ on the $N = 41$ grid and compare the splitting and $\langle x \rangle$ with $N = 61$.

:::{exercise}
:label: ex-qm4-eccentric

Where does the ground-state probability concentrate, and why?
Why does moving the hole split the degenerate pair, while changing the width did not?
What would change, and what would stay the same, if the hole moved to the other side?
Which features of your results could come from the grid?
:::

## Part 5: Open question

Use your grid Hamiltonian to investigate one new hard-wall shape and one question about its length scales or symmetries.
Draw the shape with its relevant lengths, state your question and a prediction, vary one shape parameter over a few values, and include one numerical check.
Keep the whole shape inside $[-1, 1]^2$.
Some possible directions:

- **A rectangle.**
  How do the lowest energies and the spacing of the excitations change with the aspect ratio of a rectangle of fixed area, and does the longest side always control the ground state?
- **Two rooms and a corridor.**
  Join two wide regions by a neck.
  How does the width of the neck change the lowest pair of states?
- **A shape of your own**, with a clearly stated question.

:::{exercise}
:label: ex-qm4-open

What did you investigate, and what did you predict?
How do the length scales and symmetries of your shape explain the result?
In particular, how does the energy cost of squeezing the particle across a narrow width compare with the spacing of excitations along a long direction?
:::

## What to hand in

See [](#assignments_page) for the deliverables and the check-in.

---

*This assignment was adapted from a draft by Robin Oosterhoff and Filip Sfetcu.*
