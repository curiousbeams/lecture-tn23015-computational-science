---
title: Slit Interference
label: qm-slit-interference_page
authors: [gvarnavides, lathouwers]
numbering:
  enumerator: QM5.%s
---

In a double-slit experiment, particles such as electrons, neutrons or even large molecules are sent one at a time towards a plate with two narrow openings, and a screen behind it records where each one arrives.
Each particle lands at a single, random spot, yet together they build up a pattern of bright and dark fringes, and opening the second slit makes some spots on the screen *less* likely to register a particle.
The reason is that quantum mechanics adds *amplitudes*, not probabilities.
In this assignment you compute the pattern behind one and two slits with spatial Fourier transforms, simulate the arrival of particles one detection at a time, and see how a relative phase between the slits moves the fringes.

*How does adding probability amplitudes produce interference, and how does an interference pattern emerge from individual detections?*

## The model

Non-interacting particles with de Broglie wavelength $\lambda$ arrive head-on at a thin, opaque mask with one or two narrow openings, the slits.
A screen at a distance $D$ behind the mask records where each particle lands, as sketched in [](#fig-qm3-slits).
The slits are much longer than they are wide, so the wave does not change along their length, and only the coordinate across them matters.
We use two such coordinates, in two different planes: $x$ across the mask, on the scale of the slits (nanometres), and $X$ across the screen, on the scale of the pattern (millimetres).

:::{figure} ../../figures/assignments/slits-dark.svg
:name: fig-qm3-slits-dark
:class: hidden dark:block
:enumerator: QM5.1
Two slits of width $a$, centre to centre $d$ apart, and a screen at distance $D$.
The lines indicate contributions to the amplitude at one screen position, not paths of particles.
:::

:::{figure} ../../figures/assignments/slits.svg
:name: fig-qm3-slits
:class: dark:hidden
Two slits of width $a$, centre to centre $d$ apart, and a screen at distance $D$.
The lines indicate contributions to the amplitude at one screen position, not paths of particles.
:::

**Just behind the mask.**
Let the aperture function $A(x)$ be one inside an opening and zero elsewhere.
Just behind the mask, a particle that got through has the normalised wavefunction $\psi_0(x) = A(x)/\sqrt{\int |A|^2\,dx}$.

**On the screen.**
Every point $x$ of the openings contributes to the amplitude at a screen position $X$.
For a distant screen, the path from $x$ to $X$ is shorter than the path from $x = 0$ by about $xX/D$, which gives that contribution an extra phase $-2\pi xX/(\lambda D)$.
Adding up all the contributions is therefore a Fourier transform, at the spatial frequency $f = X/(\lambda D)$:

$$
\tilde\psi(f) = \int \psi_0(x)\, e^{-2\pi i f x}\, dx, \qquad
\Phi(X) = \frac{1}{\sqrt{\lambda D}}\,\tilde\psi\!\left(\frac{X}{\lambda D}\right) .
$$

This is Fraunhofer diffraction, as in [](#fourier-transforms-2_page).
The probability density of a detection at $X$ is $P(X) = |\Phi(X)|^2$.
The factor $1/\sqrt{\lambda D}$ makes it normalised: since $dX = \lambda D\,df$, Parseval's theorem gives $\int P\,dX = \int |\tilde\psi|^2\,df = \int |\psi_0|^2\,dx = 1$.
The relation holds when the screen is far away compared with the openings, $D \gg W^2/\lambda$ where $W$ is their total width, and for $|X| \ll D$.

Use $\lambda = 50\ \mathrm{pm}$, $D = 2\ \mathrm{m}$, slit width $a = 100\ \mathrm{nm}$ and, for two slits, centre-to-centre distance $d = 400\ \mathrm{nm}$, unless a task says otherwise.

## Part 1: Behind one slit

For a single slit of width $a$ centred at $x = 0$, the screen pattern is known exactly,

$$
P_1(X) = \frac{a}{\lambda D}\left[\frac{\sin(\pi a X/\lambda D)}{\pi a X/\lambda D}\right]^2 ,
$$

with its first zeros at $X = \pm\lambda D/a$.

**The grid.**
Represent the mask on a grid of $N$ points $x_j$ with spacing $\Delta x$, centred on $x = 0$ and with a total width $L_x = N\Delta x$ much larger than the slits; $\psi_0$ is zero outside the openings.
Mark a slit centred at $c$ as the samples with $c - a/2 \leq x_j < c + a/2$, so that it contains exactly $a/\Delta x$ samples and has width $a$ on the grid.
The FFT then gives the screen amplitude at the positions $X = \lambda D f$, with $f$ from `np.fft.fftfreq`, as in the hint below.
$X = 0$ is the point on the screen straight behind $x = 0$.
The screen samples are spaced by $\Delta X = \lambda D/L_x$ and reach out to $|X| = \lambda D/(2\Delta x)$.
So the grid spacing $\Delta x$ sets how far out on the screen you can see, and the total width $L_x$, including the zeros around the slit, sets how finely the screen is sampled.

:::{exercise}
:label: ex-qm3-single

1. Plot $P_1(X)$.
2. Build $\psi_0$ for a single slit on a grid with $\Delta x = 1\ \mathrm{nm}$ and $L_x = 32\ \mu\mathrm{m}$, and verify that it is normalised.
3. Compute $P(X)$ with the FFT, verify that $\int P\,dX = 1$, and plot it together with $P_1(X)$, with $X$ in millimetres.
4. Measure the width of the central peak, between its first zeros, for slit widths $a = 50$, $100$ and $200\ \mathrm{nm}$, and tabulate it next to $2\lambda D/a$.
5. Explain why a narrower slit gives a wider pattern on the screen, and how well your measured widths agree with $2\lambda D/a$.
:::

:::{dropdown} Hint: from FFT to $P(X)$
Take `F = np.fft.fft(psi0)` of your $N$ aperture values, spaced by $\Delta x$.
The spatial frequencies are `f = np.fft.fftfreq(N, dx)`, the screen positions are $X = \lambda D f$, and the density on the screen is

$$
P(X) \approx \frac{(\Delta x)^2}{\lambda D}\,|F|^2 .
$$

Positive and negative frequencies are the two sides of the screen: keep both, without doubling anything.
`fftfreq` puts $f = 0$, and so $X = 0$, first; apply `np.fft.fftshift` to $X$ and $P$ together to put it in the middle and plot them in order.
:::

:::{exercise}
:label: ex-qm3-grid

Use $a = 100\ \mathrm{nm}$.

1. Refine the grid: compute $P(X)$ for $\Delta x = 5$, $2$, $1$ and $0.5\ \mathrm{nm}$ at fixed $L_x = 32\ \mu\mathrm{m}$, and tabulate the largest difference between $P$ and $P_1$ for $|X| < 5\ \mathrm{mm}$.
2. Add zeros around the slit: compute $P(X)$ for $L_x = 4$, $8$, $32$ and $128\ \mu\mathrm{m}$ at fixed $\Delta x = 1\ \mathrm{nm}$, and tabulate the screen spacing $\Delta X$ and the measured width of the central peak.
3. Explain what each of these two changes does to the slit and to the pattern on the screen, and how precisely you can report the width of the central peak.
:::

## Part 2: Opening a second slit

Place two identical slits at $x = \pm d/2$, and let $\Phi_L$ and $\Phi_R$ be the screen amplitudes of the left and right slit, each computed on its own and normalised as in Part 1.
With both slits open and the particle arriving in phase at both, the amplitude is $(\Phi_L + \Phi_R)/\sqrt2$.

Compute $\Phi_L$ and $\Phi_R$ on the *same* grid, with each slit at its true position.
Moving a slit sideways by $s$ multiplies its amplitude on the screen by a phase $e^{-2\pi i f s}$; the difference between these phases for the two slits is what makes the fringes.
Recentring each slit before its FFT would throw that information away.

Compare the two open slits with a 50/50 *mixture*: half the particles recorded with only the left slit open, and half with only the right one.
The two densities are

$$
P_\mathrm{both} = \frac{|\Phi_L + \Phi_R|^2}{2}, \qquad P_\mathrm{mix} = \frac{|\Phi_L|^2 + |\Phi_R|^2}{2} .
$$

:::{exercise}
:label: ex-qm3-interference

1. Show, by expanding the square, that $P_\mathrm{both} - P_\mathrm{mix} = \mathrm{Re}\left(\Phi_L^*\,\Phi_R\right)$, the interference term.
2. Compute $\Phi_L$ and $\Phi_R$, and plot $P_\mathrm{both}$, $P_\mathrm{mix}$ and the interference term.
3. Verify that $P_\mathrm{both}$ and $P_\mathrm{mix}$ both integrate to one, and that $P_\mathrm{both}$ agrees with the pattern you get by transforming the two-slit aperture directly.
4. Explain how the interference term lets a second slit *reduce* the probability of a detection at some positions, why the mixture is different, and how total probability is still conserved.
:::

:::{exercise}
:label: ex-qm3-scales

1. Compute $P_\mathrm{both}$ for $d = 300$, $400$ and $600\ \mathrm{nm}$.
2. Find the position of the first maximum next to the central one, and tabulate it next to $\lambda D/d$.
3. Explain which length scale sets the broad envelope of the pattern and which sets the fine fringes, and why the maxima lie slightly off the multiples of $\lambda D/d$.
:::

## Part 3: One detection at a time

The interference pattern is a probability distribution: each particle arrives at a single, random place.
Use the screen samples from your FFT as detector cells $X_j$ of width $\Delta X$; a particle lands in cell $j$ with probability $P(X_j)\,\Delta X$.

:::{exercise}
:label: ex-qm3-detections

1. Draw 50, 500 and 5000 random detection positions from $P_\mathrm{both}$, using [](#random-numbers_page).
2. Plot each record as a strip of individual detection marks, and as a histogram normalised as a density, on top of $P_\mathrm{both}(X)$.
3. Draw 5000 detections from $P_\mathrm{mix}$ instead, and plot that record next to the one for both slits.
4. Explain how the pattern becomes visible as detections accumulate, even though each position is random, and how the fluctuations in your histograms change with the number of detections.
   Explain why a bin around a dark fringe can still contain detections, and whether your records tell you which slit each particle went through.
:::

## Part 4: Moving the fringes without moving the slits

Put a thin transparent plate in front of the right slit.
It delays the wave passing through that slit, which multiplies its part of the wavefunction by a phase $e^{i\phi}$, without absorbing anything:

$$
\psi_\phi(x) = \frac{\psi_L(x) + e^{i\phi}\,\psi_R(x)}{\sqrt2} ,
$$

where $\psi_L$ and $\psi_R$ are the normalised single-slit wavefunctions.
By contrast, a *global* phase multiplies the whole wavefunction, both slits alike, by the same factor $e^{i\chi}$.

:::{exercise}
:label: ex-qm3-phase

1. Predict, before calculating, how the density just behind the mask, $|\psi_\phi|^2$, and the screen pattern change when $\phi$ goes from $0$ to $\pi/2$ to $\pi$: does each one move, change shape, or stay the same?
2. Compute both densities for $\phi = 0$, $\pi/2$ and $\pi$, and plot each set on common axes.
3. Plot the density at the centre of the screen, $P_\phi(0)$, as $\phi$ goes from $0$ to $2\pi$.
4. Show that $P_\phi(0) = 2\,|\Phi_L(0)|^2 \cos^2(\phi/2)$, using $\Phi_L(0) = \Phi_R(0)$, and compare it with your curve.
5. Multiply the whole two-slit wavefunction by a global phase $e^{i\chi}$, and verify whether either density changes.
6. Explain what information the density just behind the mask loses that the screen pattern reveals.
   Use your results to explain a dark centre, the unchanged envelope, and why a global phase changes nothing.
:::

## Part 5: Open question

Use your FFT calculation to investigate one question of your own about how the openings, or the phases across them, shape the pattern.
Some possible directions:

- **A phase plate.**
  Cover both slits with a transparent plate whose thickness, and so the phase delay it adds, varies across each slit: $\psi_\alpha(x) = \psi_0(x)\,e^{i\alpha\theta(x)}$, with for example $\theta(x) = \sin(2\pi x/a) + 0.35\sin(2\pi x/0.7a + 0.6)$ and strengths $\alpha = 0$, $1$ and $2.5$.
  How does the strength redistribute the detections?
  A useful measure is the probability $p_c$ of landing in a central detector, $|X| < \lambda D/(2d)$.
- **A grating.**
  How does the pattern change from two to $N = 3$, $4$ and $6$ equally spaced slits, a distance $d$ apart?
- **Unequal slits.**
  Let the right slit transmit only a fraction $t = 1$, $0.5$ or $0.2$ of the amplitude.
  What happens to the contrast of the fringes, measured by the visibility $(P_\mathrm{max} - P_\mathrm{min})/(P_\mathrm{max} + P_\mathrm{min})$ near the centre?

:::{exercise}
:label: ex-qm3-open

1. Write down your aperture function, your question and your prediction before you calculate.
2. Choose one quantitative measure of the pattern, such as $p_c$ or the visibility, and compute it for each value of your parameter.
3. Plot the screen patterns for your parameter values on common axes, and plot your measure against the parameter.
4. Repeat one representative case on a finer grid, and report the change in your measure.
5. Explain whether your results support your prediction, using the aperture and the amplitudes that add on the screen.
:::

## What to hand in

See [](#assignments_page) for the deliverables and the check-in.

---

*This assignment was adapted from a draft by Robin Oosterhoff and Filip Sfetcu.*
