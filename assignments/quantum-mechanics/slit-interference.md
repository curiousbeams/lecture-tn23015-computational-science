---
title: Slit Interference
label: qm-slit-interference_page
authors: [gvarnavides, lathouwers]
numbering:
  enumerator: QM5.%s
---

Opening a second slit can make some places on a screen *less* likely to register a particle.
In this assignment you use spatial Fourier transforms to compute what single particles do behind one and two slits, simulate the arrival of particles one detection at a time, and see how a relative phase between the slits moves the pattern.

*How does adding probability amplitudes produce interference, and how does an interference pattern emerge from individual detections?*

## The model

Non-interacting particles with de Broglie wavelength $\lambda$ illuminate a thin mask.
The slits are long, so we follow only the coordinate $x$ across them; the screen is a distance $D$ behind the mask, and $X$ is the position on it.

:::{figure} ../../figures/assignments/slits-dark.svg
:name: fig-qm3-slits-dark
:class: hidden dark:block
Two slits of width $a$, centre to centre $d$ apart, and a screen at distance $D$.
The lines indicate contributions to the amplitude at one screen position, not paths of particles.
:::

:::{figure} ../../figures/assignments/slits.svg
:name: fig-qm3-slits
:class: dark:hidden
Two slits of width $a$, centre to centre $d$ apart, and a screen at distance $D$.
The lines indicate contributions to the amplitude at one screen position, not paths of particles.
:::

Let $A(x)$ be one inside an opening and zero elsewhere.
Just behind the mask, a transmitted particle has the normalised wavefunction $\psi_0(x) = A(x)/\sqrt{\int |A|^2 dx}$.
Far from the mask, the amplitude on the screen follows from its Fourier transform:

$$
\tilde\psi(f) = \int \psi_0(x)\, e^{-2\pi i f x}\, dx, \qquad
\Phi(X) = \frac{1}{\sqrt{\lambda D}}\,\tilde\psi\!\left(\frac{X}{\lambda D}\right),
$$

and the probability density of a detection at $X$ is $P(X) = |\Phi(X)|^2$, normalised so that $\int P\,dX = 1$.
This far-field relation is valid when $|X| \ll D$ and $D \gg W^2/\lambda$, where $W$ is the total width of the openings.

Use $\lambda = 50\ \mathrm{pm}$, $D = 2\ \mathrm{m}$, slit width $a = 100\ \mathrm{nm}$ and, for two slits, $d = 400\ \mathrm{nm}$, unless a task says otherwise.

## Part 1: Behind one slit

For a single slit of width $a$ centred at $x = 0$ the screen pattern is known exactly,

$$
P_1(X) = \frac{a}{\lambda D}\left[\frac{\sin(\pi a X/\lambda D)}{\pi a X/\lambda D}\right]^2 ,
$$

with its first zeros at $X = \pm\lambda D/a$.

- Plot $P_1(X)$.
- Represent the slit on a grid with spacing $\Delta x = 1\ \mathrm{nm}$ over a total width of $32\ \mu\mathrm{m}$, and compute $P(X)$ with the FFT, with properly labelled physical axes.
  Check that both $\psi_0$ and $P$ are normalised, and compare your $P(X)$ with $P_1$, including the positions of the first zeros.
- Measure the width of the central peak, between its first zeros, for slit widths $a = 50$, $100$ and $200\ \mathrm{nm}$.
- Then make two separate checks for $a = 100\ \mathrm{nm}$: refine the aperture grid, and, separately, enlarge the region of zeros around the slit without changing $\Delta x$.

:::{dropdown} Hint: from FFT to $P(X)$
For a grid $x_j = x_\mathrm{start} + j\Delta x$ and raw FFT coefficients $F_k$ at the signed spatial frequencies $f_k$ (`np.fft.fftfreq`),
$$
\tilde\psi(f_k) \approx \Delta x\, e^{-2\pi i f_k x_\mathrm{start}}\, F_k, \qquad X_k = \lambda D f_k, \qquad P(X_k) = \frac{|\tilde\psi(f_k)|^2}{\lambda D}.
$$
This is a two-sided spatial transform: keep both positive and negative frequencies (the two sides of the screen), without doubling anything.
The spacing of screen samples is $\lambda D / L_x$, where $L_x$ is the total width of your grid.
:::

:::{exercise}
:label: ex-qm3-single

Why does a narrower slit give a wider pattern on the screen?
How well do your measured peak widths agree with $2\lambda D/a$?
:::

:::{exercise}
:label: ex-qm3-grid

What changes when you refine the aperture grid, and what changes when you add zeros around it?
How precisely can you report the width of the central peak, and what limits it?
:::

## Part 2: Opening a second slit

Place two identical slits at $x = \pm d/2$.
Compute the screen amplitudes $\Phi_L$ and $\Phi_R$ of the left and right slit separately, each normalised as in Part 1, on the *same* grid and coordinate origin.
With both slits open and illuminated in phase, the amplitude is $(\Phi_L + \Phi_R)/\sqrt2$.

Compare this with a 50/50 *mixture*: half the particles recorded with only the left slit open, half with only the right one.
Their densities are

$$
P_\mathrm{both} = \frac{|\Phi_L + \Phi_R|^2}{2}, \qquad P_\mathrm{mix} = \frac{|\Phi_L|^2 + |\Phi_R|^2}{2}.
$$

- Work out $P_\mathrm{both} - P_\mathrm{mix}$ by expanding the square, and identify the interference term.
- Plot $P_\mathrm{both}$, $P_\mathrm{mix}$ and their difference, and check that $P_\mathrm{both}$ is also what you get by transforming the two-slit mask directly.
- For $d = 300$, $400$ and $600\ \mathrm{nm}$, measure the spacing of the fine fringes near the centre and compare it with $\lambda D/d$.

:::{exercise}
:label: ex-qm3-interference

How does the interference term explain why opening a second slit can *reduce* the probability of a detection at some positions?
Why is the mixture different, and how is total probability still conserved?
:::

:::{exercise}
:label: ex-qm3-scales

Which length scale sets the broad envelope of the pattern, and which sets the fine fringes?
Why do the positions of the actual maxima differ slightly from multiples of $\lambda D/d$?
:::

## Part 3: One detection at a time

The interference pattern is a probability distribution: each particle arrives at a single, random place.

- Divide the screen into cells $X_j$ of width $\Delta X$, with probabilities proportional to $P(X_j)\,\Delta X$, and draw random detection positions from this distribution using [](#random-numbers_page).
- Show how the record builds up for 50, 500 and 5000 detections, as a strip of individual detection marks and as a histogram compared with $P(X)$ using the same bins and normalisation.
- Repeat one case with the mixture $P_\mathrm{mix}$ and compare the two records.

:::{exercise}
:label: ex-qm3-detections

How does the pattern become visible as detections accumulate, even though each position is random?
How do the fluctuations in your histograms change with the number of detections?
Why can a bin around a dark fringe still contain detections, and do your records tell you which slit each particle went through?
:::

## Part 4: Moving the fringes without moving the slits

Suppose an ideal phase shifter multiplies the wavefunction in the right slit by $e^{i\phi}$, without changing its magnitude:

$$
\psi_\phi(x) = \frac{\psi_L(x) + e^{i\phi}\,\psi_R(x)}{\sqrt2} .
$$

- Predict what happens for $\phi = 0$, $\pi/2$ and $\pi$, then compute the density just behind the mask and the screen pattern for each, and compare them on common axes.
- Plot the screen density at the centre, $P_\phi(0)$, as $\phi$ goes from $0$ to $2\pi$, and explain the curve by adding the two complex amplitudes at $X = 0$.
- Multiply the *whole* wavefunction by a common phase $e^{i\chi}$ instead, and check whether either density changes.

:::{exercise}
:label: ex-qm3-phase

What information does the density just behind the mask lose that the screen pattern reveals?
Use your phase study to explain a dark centre, the unchanged envelope, and why a global phase changes nothing.
:::

## Part 5: Open question

Use your validated FFT calculation to investigate one question of your own about how the openings or their phases shape the pattern.
State the question and a prediction before calculating, vary one parameter over a few values, choose one quantitative measure (for example the probability in a fixed central detector interval), and check one result by refinement.
Some possible directions:

- **A phase plate.**
  A transparent plate whose phase varies across the slits, $\psi_\alpha(x) = \psi_0(x)\,e^{i\alpha\theta(x)}$, with for example $\theta(x) = \sin(2\pi x/a) + 0.35\sin(2\pi x/0.7a + 0.6)$.
  How does the strength $\alpha$ redistribute the detections?
- **A grating.**
  How does the pattern change from two to $N = 3, 4, 6$ equally spaced slits?
- **Unequal slits.**
  Make one slit narrower, or let it transmit only part of the amplitude.
  What happens to the contrast of the fringes?

:::{exercise}
:label: ex-qm3-open

What did you investigate, and what did you predict?
What does your quantitative measure show, and which numerical evidence supports your conclusion?
:::

## What to hand in

See [](#assignments_page) for the deliverables and the check-in.

---

*This assignment was adapted from a draft by Robin Oosterhoff and Filip Sfetcu.*
