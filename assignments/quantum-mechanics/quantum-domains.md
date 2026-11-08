---
title: Quantum Domains
label: qm-quantum-domains_page
authors: [gvarnavides, lathouwers]
numbering:
  enumerator: QM1.%s
---

The shape of a hard wall decides which standing waves fit inside it.
In this assignment you calculate the states of a particle confined to a disk and to a ring, first from their exact radial solutions, which are Bessel functions, and then numerically on a square grid.
The grid lets you study shapes that radial solutions cannot describe, such as a ring with an off-centre hole.

*How do a region's size, its narrowest widths, and its symmetries set its energies and wavefunctions?*

## The model

A particle of mass $m$ moves in a two-dimensional region with hard walls: the potential is zero inside and infinite outside, so the wavefunction must vanish on every boundary.
Inside the region, the time-independent Schrödinger equation is $-\frac{\hbar^2}{2m}\nabla^2\psi = E\psi$.
Measuring lengths in units of the outer radius $R_\mathrm{out}$, and energies in units of $\hbar^2/(2mR_\mathrm{out}^2)$, it becomes

$$
-\nabla^2 \psi = \epsilon\,\psi ,
$$

where $\epsilon$ is the dimensionless energy and the disk has radius 1.
An annulus also has an inner wall of radius $\rho$, leaving a ring of width $w = 1 - \rho$.
Moving the centre of the inner circle by $\delta$ along $x$ gives an eccentric annulus; keep $|\delta| + \rho < 1$, so that the hole stays inside the disk.
[](#fig-qm4-domains) shows the three regions.

:::{figure} ../../figures/assignments/domains-dark.svg
:name: fig-qm4-domains-dark
:class: hidden dark:block
:enumerator: QM1.1
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

The disk looks the same from every angle, so we use polar coordinates $(r, \phi)$, in which

$$
\nabla^2\psi = \frac{\partial^2\psi}{\partial r^2} + \frac{1}{r}\frac{\partial\psi}{\partial r} + \frac{1}{r^2}\frac{\partial^2\psi}{\partial\phi^2} .
$$

We look for solutions that separate into a radial and an angular part,

$$
\psi(r, \phi) = R(r)\,\frac{e^{i\ell\phi}}{\sqrt{2\pi}} .
$$

The wavefunction must return to the same value after a full turn, $\phi \to \phi + 2\pi$, so $\ell$ is an integer, $\ell = 0, \pm 1, \pm 2, \dots$; it is the angular momentum in units of $\hbar$.
Substituting this form into $-\nabla^2\psi = \epsilon\psi$, the angular derivative gives a factor $-\ell^2$, and dividing out $e^{i\ell\phi}$ leaves the radial equation

$$
R'' + \frac{1}{r}R' + \left(\epsilon - \frac{\ell^2}{r^2}\right)R = 0 .
$$

With $k = \sqrt{\epsilon}$, this is Bessel's equation in the variable $kr$, and its general solution is

$$
R(r) = A\,J_{|\ell|}(kr) + B\,Y_{|\ell|}(kr) ,
$$

where $J_{|\ell|}$ and $Y_{|\ell|}$ are the Bessel functions of the first and second kind, available as `scipy.special.jv` and `scipy.special.yv`.
Two boundary conditions then fix the constants and the energy:

1. **The wavefunction is finite at the centre.**
   $Y_{|\ell|}(kr)$ diverges as $r \to 0$, so the disk requires $B = 0$.
2. **The wavefunction vanishes at the wall.**
   $R(1) = A\,J_{|\ell|}(k) = 0$ with $A \neq 0$, so $k$ must be a zero of $J_{|\ell|}$.

Each $J_{|\ell|}$ has infinitely many positive zeros; call the $n$-th one $j_{|\ell|,n}$, with $n = 1, 2, 3, \dots$
A state of the disk therefore carries two labels, $\ell$ for its motion around the centre and $n$ for its radial structure, and has

$$
\epsilon_{\ell,n} = j_{|\ell|,n}^2 , \qquad R_{\ell,n}(r) = A\,J_{|\ell|}\!\left(j_{|\ell|,n}\,r\right) .
$$

The constant $A$ follows from the normalisation $\int_0^1 |R|^2\, r\,dr = 1$, and the factor $r$ comes from the area element $r\,dr\,d\phi$ since the angular factor is already normalised.

:::{exercise}
:label: ex-qm4-disk

1. Plot $J_0$, $J_1$ and $J_2$ for $0 \leq k \leq 12$, a range that shows their first two zeros, and plot $Y_0$ for $0 < k \leq 2$.
2. Find $j_{0,1}$, $j_{1,1}$, $j_{2,1}$ and $j_{0,2}$ with your own bisection from [](#root-finding_page), using brackets read off your plots.
3. Tabulate the corresponding energies in increasing order, each with its $(|\ell|, n)$ label.
4. Normalise $R_{0,1}$ and $R_{1,1}$ using [](#numerical-integration_page), and plot their radial probability densities $r|R|^2$.
5. Explain how $\ell$ and $n$ show up in the shape of a state, and why increasing either one raises its energy.
   Explain why $+\ell$ and $-\ell$ have the same energy, and how the $\ell^2/r^2$ term accounts for the difference between the two radial probabilities you plotted.
:::

## Part 2: Opening a hole

Now remove a concentric disk of radius $\rho$ from the centre.
The region still looks the same from every angle, so the separation, the integer $\ell$ and the radial equation from Part 1 all carry over.
Only the boundary conditions change:

1. **The centre is no longer part of the region**, so nothing forbids $Y_{|\ell|}$, and both terms of $R(r) = A\,J_{|\ell|}(kr) + B\,Y_{|\ell|}(kr)$ are allowed.
2. **There are now two walls**, so $R(\rho) = 0$ and $R(1) = 0$.

The two wall conditions are two linear equations for $A$ and $B$:

$$
\begin{pmatrix} J_{|\ell|}(k\rho) & Y_{|\ell|}(k\rho) \\ J_{|\ell|}(k) & Y_{|\ell|}(k) \end{pmatrix}
\begin{pmatrix} A \\ B \end{pmatrix} = 0 .
$$

They always have the solution $A = B = 0$, which is no wavefunction at all.
A nonzero solution exists only for the $k$ at which the determinant of the matrix vanishes,

$$
D_\ell(k) = J_{|\ell|}(k\rho)\,Y_{|\ell|}(k) - Y_{|\ell|}(k\rho)\,J_{|\ell|}(k) = 0 .
$$

This replaces the disk's condition $J_{|\ell|}(k) = 0$.
Its positive roots, again numbered $n = 1, 2, \dots$ in increasing order, give the energies $\epsilon_{\ell,n} = k^2$.
At a root, the radial function is

$$
R_{\ell,n}(r) = A\left[J_{|\ell|}(kr)\,Y_{|\ell|}(k\rho) - Y_{|\ell|}(kr)\,J_{|\ell|}(k\rho)\right] ,
$$

which vanishes at $r = \rho$ by construction, and at $r = 1$ because $D_\ell(k) = 0$.
It is normalised with $\int_\rho^1 |R|^2\, r\,dr = 1$.

:::{exercise}
:label: ex-qm4-hole

Use a hole of radius $\rho = 0.35$.

1. Plot $D_\ell(k)$ for $\ell = 0, 1, 2$ over $0 < k \leq 12$.
2. Find the lowest root of each $D_\ell$ with your bisection, and convert the roots to energies.
3. Normalise $R_{0,1}$ and $R_{1,1}$, and plot their radial probability densities together with the disk's from Part 1.
4. Draw a level diagram that compares the disk and the annulus: one column for each of $|\ell| = 0, 1, 2$, with a short horizontal line at each energy.
5. Explain why opening the hole raises every energy level, rather than lowering some of them.
   Identify which of the lowest $|\ell| = 0, 1, 2$ levels rises most, and explain why using the disk's radial probabilities.
:::

:::{dropdown} Hint: finding the roots of $D_\ell$
Avoid $k = 0$ itself, where $Y_{|\ell|}$ diverges.
The size of $D_\ell$ varies a lot with $k$, but only its sign matters: evaluate it on a fine grid of $k$ values, look for sign changes between neighbouring points, and refine each one with bisection.
A grid that is too coarse can step over two nearby roots and miss both, so check the roots you found against your plot.
:::

:::{exercise} Optional
:label: ex-qm4-width

1. Compute the energies of the four levels $(|\ell|, n) = (0, 1)$, $(1, 1)$, $(2, 1)$ and $(0, 2)$ for holes of radius $\rho = 0.25$, $0.35$ and $0.45$.
   The level $(0, 2)$ is the second root of $D_0$.
2. Plot each of the four energies against the ring width $w = 1 - \rho$.
3. Explain how the angular excitations $(1, 1)$ and $(2, 1)$ and the radial excitation $(0, 2)$ respond differently as the ring gets narrower.
   Identify which degeneracies survive when the hole is opened or widened, and the symmetry that protects them.
:::

## Part 3: A Hamiltonian on a square grid

An off-centre hole destroys the rotational symmetry, so the radial method no longer works.
Instead, represent $\psi$ on a square grid that covers $[-1, 1]^2$, with an odd number $N$ of points per axis, spacing $h = 2/(N - 1)$ and coordinates $x_i = \left(i - \tfrac{N-1}{2}\right)h$, the same for $y$.
Opposite grid points must have *exactly* opposite coordinates (see the hint below).
Mark the allowed points with a Boolean mask: $x^2 + y^2 < 1$ for the disk, and additionally $(x - \delta)^2 + y^2 > \rho^2$ for an annulus.

The five-point formula from [](#partial-differential-equations-1_page) gives

$$
-\nabla^2\psi_{i,j} \approx \frac{4\psi_{i,j} - \psi_{i+1,j} - \psi_{i-1,j} - \psi_{i,j+1} - \psi_{i,j-1}}{h^2} ,
$$

where a neighbour outside the region has $\psi = 0$.
Numbering the allowed points one after the other turns this into a symmetric matrix eigenvalue problem, as in [](#linear-algebra_page).
Each level with $|\ell| \geq 1$ is a pair of states, $+\ell$ and $-\ell$, so the five lowest eigenvalues of the disk or the concentric annulus belong to $(0, 1)$, then $(1, 1)$ twice, then $(2, 1)$ twice.

:::{exercise}
:label: ex-qm4-grid

1. Build the matrix for the disk, and for the annulus with $\rho = 0.35$ and $\delta = 0$, on grids with $N = 41$ and $N = 61$.
2. Verify that each matrix is symmetric.
3. Compute the ten lowest eigenvalues and eigenvectors of each matrix, for example with `scipy.linalg.eigh(H, subset_by_index=[0, 9])`, and verify that the states are normalised.
4. Tabulate the five lowest eigenvalues of each shape on both grids next to the values from Parts 1 and 2, with their relative errors.
   As a guide, on the $N = 61$ grid the ground-state energy should agree with the exact value to about 2% for the disk and about 6% for the annulus.
5. Explain how the energies change as the grid is refined, and why the error is larger for the annulus than for the disk.
   Explain why refining the grid does not remove the error from a curved wall built out of square cells as quickly as you might expect.
:::

:::{dropdown} Hint: building the matrix
Give each allowed point an index with `index = -np.ones((N, N), int); index[mask] = np.arange(mask.sum())`.
Then loop over the allowed points: put $4/h^2$ on the diagonal, and $-1/h^2$ in the column of every neighbour that is itself allowed.
A neighbour outside the region simply contributes nothing.
Keep $N \leq 61$; for $N = 61$ the disk has about 2800 unknowns, which a dense eigensolver handles in seconds.

`eigh` returns eigenvectors $u$ with $\sum_p |u_p|^2 = 1$.
The wavefunction on the grid is $\psi = u/h$, so that $\sum |\psi|^2 h^2 = 1$ approximates $\int |\psi|^2\,dA = 1$.

Why the exactly symmetric coordinates matter: some grid points lie exactly on a wall.
If $x$ and $-x$ differ in their last digit, such a point can be kept on one side and dropped on the other, and the region silently loses its symmetry.
:::

:::{exercise}
:label: ex-qm4-doublets

1. Plot the probability densities of the four lowest states of the annulus on the $N = 61$ grid.
2. Compute the splitting within each of the two lowest degenerate pairs, for the disk and the annulus on both grids.
3. Explain how well the grid reproduces the degenerate pairs.
   Explain why the two states of a degenerate pair can come out with different orientations, even when their energies agree.
:::

## Part 4: Moving the hole

Return to $\rho = 0.35$ on the $N = 61$ grid, and move the inner circle along $x$ by $\delta = 0$, $0.10$ and $0.20$.
The reflection $y \to -y$ is still a symmetry, but rotations are not.
The ground state's mean position on the grid is $\langle x \rangle = \sum x\,|\psi|^2 h^2$.

:::{exercise}
:label: ex-qm4-eccentric

1. Predict, before calculating, which side of the ring gets wider, where the ground state will sit, and what will happen to the lowest degenerate pair.
2. Compute, for each $\delta$, the five lowest energies, the ground state's $\langle x \rangle$, and the splitting of the two levels that came from the lowest $|\ell| = 1$ pair.
3. Plot the signed wavefunctions of those two levels at $\delta = 0.20$, and classify each as even or odd under $y \to -y$.
4. Repeat the $\delta = 0.20$ calculation on the $N = 41$ grid, and compare its splitting and $\langle x \rangle$ with $N = 61$.
5. Explain where the ground-state probability concentrates, and why.
   Explain why moving the hole splits the degenerate pair while opening the concentric hole did not, and state what would change, and what would stay the same, if the hole moved to the other side.
   Identify which features of your results could come from the grid.
:::

## Part 5: Open question

Use your grid Hamiltonian to investigate one new hard-wall shape and one question about its length scales or symmetries.
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

1. Draw your shape with its relevant lengths, and state your question and a prediction before you calculate.
2. Compute the quantities your question needs while you vary one shape parameter over a few values.
3. Include one numerical check that shows your result is not an artefact of the grid.
4. Explain whether your result supports your prediction, using the length scales and symmetries of your shape.
   In particular, compare the energy cost of squeezing the particle across a narrow width with the spacing of the excitations along a long direction.
:::

## What to hand in

See [](#assignments_page) for the deliverables and the check-in.

---

*This assignment was adapted from a draft by Robin Oosterhoff and Filip Sfetcu.*
