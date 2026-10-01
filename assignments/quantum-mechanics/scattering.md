---
title: Wave Scattering
label: qm-scattering_page
authors: [gvarnavides, lathouwers]
numbering:
  enumerator: QM4.%s
---

A localised quantum particle moves, spreads out, and, when it hits a barrier, splits into a reflected and a transmitted part.
In this assignment you describe a Gaussian wave packet in position and momentum space, set up a numerical time evolution and test it against an exact result, and then use it to study scattering from a barrier.

*How does a localised particle scatter from a barrier, and how can we tell quantum effects from numerical errors?*

## The model

We use units with $\hbar = m = 1$, so momentum and wavenumber are the same number, $p = k$.
The wavefunction obeys the time-dependent Schrödinger equation

$$
i\frac{\partial \psi}{\partial t} = -\frac12 \frac{\partial^2 \psi}{\partial x^2} + V(x)\,\psi, \qquad \int |\psi(x, t)|^2\,dx = 1 .
$$

The physical line is infinite.
We approximate it by $-L \leq x \leq L$ with $\psi(\pm L, t) = 0$, and only trust times at which the packet has negligible probability near these artificial walls.

:::{figure} ../../figures/assignments/scattering-setup-dark.svg
:name: fig-qm2-setup-dark
:class: hidden dark:block
A Gaussian packet starting at $x_0 = -24$ with width $\sigma_x = 3$ and wavenumber $k_0 = 2$, moving towards a barrier of height $V_0 = 2$ and width $a = 1.6$.
Density and potential have separate vertical scales; the numerical box extends well beyond this view.
:::

:::{figure} ../../figures/assignments/scattering-setup.svg
:name: fig-qm2-setup
:class: dark:hidden
A Gaussian packet starting at $x_0 = -24$ with width $\sigma_x = 3$ and wavenumber $k_0 = 2$, moving towards a barrier of height $V_0 = 2$ and width $a = 1.6$.
Density and potential have separate vertical scales; the numerical box extends well beyond this view.
:::

## Part 1: A packet in position and momentum space

Start with the Gaussian packet

$$
\psi(x, 0) = A \exp\!\left[-\frac{(x - x_0)^2}{4\sigma_x^2}\right] e^{ik_0 x},
$$

which on the infinite line has $A = (2\pi\sigma_x^2)^{-1/4}$, $\langle x \rangle = x_0$, $\Delta x = \sigma_x$, $\langle p \rangle = k_0$ and $\Delta p = 1/(2\sigma_x)$.

- On a grid with spacing $h = 0.1$ over $[-110, 110]$, build and numerically normalise the packet for $x_0 = -24$, $k_0 = 2$ and $\sigma_x = 3$, and calculate $\langle x \rangle$ and $\Delta x$ from integrals of $x$ and $x^2$ weighted by $|\psi|^2$.
- Use the FFT from [](#fourier-transforms-1_page) to compute the momentum wavefunction $\tilde\psi(p) = (2\pi)^{-1/2}\int \psi(x)\, e^{-ipx}\,dx$, and plot $|\tilde\psi(p)|^2$ including negative momenta.
  Check that it integrates to one *without* renormalising it.
- Calculate $\langle p \rangle$ and $\Delta p$, and compare three widths, $\sigma_x = 1.5$, $3$ and $6$.

:::{dropdown} Hint: from FFT to $\tilde\psi(p)$
For samples $x_j = x_\mathrm{start} + jh$, $j = 0, \dots, N-1$, with raw FFT $F_m = \sum_j \psi(x_j)\,e^{-2\pi i jm/N}$,
$$
\tilde\psi(p_m) \approx \frac{h}{\sqrt{2\pi}}\, e^{-ip_m x_\mathrm{start}}\, F_m, \qquad p_m = 2\pi f_m,
$$
with $f_m$ from `np.fft.fftfreq(N, h)`; the momentum spacing is $2\pi/(Nh)$.
If your grid includes both endpoints, leave out the right one so that the FFT sees $[-L, L)$, and apply `np.fft.fftshift` to $\tilde\psi$ and to $p$ together.
:::

:::{exercise}
:label: ex-qm2-packet

How does narrowing the packet in position change its momentum distribution?
Compare your $\Delta x$, $\Delta p$ and their product with the Gaussian values.
What does the normalisation check in momentum space tell you about your FFT scaling?
:::

## Part 2: Free motion, and a numerical method you can trust

With $V = 0$ the packet's centre and width are known exactly:

$$
\langle x(t) \rangle = x_0 + k_0 t, \qquad \Delta x(t) = \sigma_x \sqrt{1 + \left(\frac{t}{2\sigma_x^2}\right)^2} ,
$$

and its momentum distribution does not change at all.

On the grid, the second derivative becomes the three-point formula of [](#numerical-differentiation_page), and the Schrödinger equation turns into a large set of coupled ODEs for the complex values $\psi_j(t)$, as in [](#partial-differential-equations-2_page):

$$
\frac{d\psi_j}{dt} = -i\left[-\frac{\psi_{j+1} - 2\psi_j + \psi_{j-1}}{2h^2} + V_j\,\psi_j\right],
$$

with the end values held at zero.

- Integrate these equations with your RK4 from [](#ordinary-differential-equations-1_page), applied to the whole complex array at once, with $\Delta t = 0.005$, for the $\sigma_x = 3$ packet up to $t = 10$.
- Plot a few density snapshots, and compare $\langle x(t) \rangle$ and $\Delta x(t)$ with the exact curves; compare the initial and final momentum distributions.
- Monitor $P(t) = \int |\psi|^2 dx$ without ever renormalising, and the probability in an outer strip $0.9L < |x| < L$.
- Check your settings: repeat once with $\Delta t = 0.01$, and once with $h = 0.2$, and report how the errors in centre, width and norm at $t = 10$ change.

:::{dropdown} Hint: stability
An explicit method like RK4 becomes unstable if the timestep is too large compared with $h^2$: roughly, it needs $\Delta t \lesssim 1.4\,h^2$.
Refining $h$ therefore requires a smaller $\Delta t$ as well.
:::

:::{exercise}
:label: ex-qm2-free

How can the position distribution spread while the momentum distribution stays the same?
How well do your centre and width follow the exact curves, and why is a moving packet not a stationary state?
:::

:::{exercise}
:label: ex-qm2-settings

Does nearly perfect conservation of $P(t)$ guarantee that the motion and spreading are accurate?
Which of your checks revealed which kind of error, and which settings will you use for the rest of the assignment?
:::

## Part 3: A collision

Introduce the square barrier

$$
V(x) = \begin{cases} V_0, & |x| < a/2, \\ 0, & |x| \geq a/2, \end{cases}
$$

with $V_0 = 2$ and $a = 1.6$.
The characteristic energy of the packet is $E_0 = k_0^2/2$; with $k_0 = 2$ this is exactly $V_0$, although the packet contains a spread of energies.

- Follow the $\sigma_x = 3$ packet through the collision up to $t = 40$.
  Show density snapshots before, during and after it, with the barrier marked, and compare the initial and final momentum distributions.
- With $b = 4$, compute the probabilities to the left of, inside, and to the right of the barrier region:
  $$
  R(t) = \int_{x < -b} |\psi|^2 dx, \qquad P_\mathrm{mid}(t) = \int_{-b}^{b} |\psi|^2 dx, \qquad T(t) = \int_{x > b} |\psi|^2 dx .
  $$
  Plot them against time and check that they add up to $P(t)$.

:::{exercise}
:label: ex-qm2-collision

Which outgoing packet corresponds to which sign of momentum?
How do your snapshots, momentum distributions and three probabilities show that the collision is over?
Why is $R + T \approx 1$ on its own not enough to show that the artificial walls have no influence?
:::

## Part 4: Reflection, transmission and tunnelling

- Keeping $V_0$ and $a$ fixed, compute the final $T$ for $E_0/V_0 = 0.5$, $0.75$, $1$ and $1.5$, and plot $T$ against $E_0/V_0$.
- At $E_0/V_0 = 0.5$, compute $T$ for barrier widths $a = 0.8$, $1.6$ and $2.4$, and plot $T$ and $\ln T$ against $a$.
- A packet with $E_0 < V_0$ still has a small part of its momentum distribution above the barrier.
  For the $E_0/V_0 = 0.5$ packet, estimate the weight above the barrier, $W_\mathrm{above} = \int_{\sqrt{2V_0}}^{\infty} |\tilde\psi(p)|^2\,dp$, from your FFT of Part 1, and compare it with your $T$.
- Repeat one of these runs on a finer grid (keeping the physical barrier the same) and report the change in $T$.

:::{exercise}
:label: ex-qm2-trends

How do the incident energy and the barrier width change the transmission?
Which of your results show tunnelling, and which show reflection *above* a barrier?
:::

:::{exercise}
:label: ex-qm2-tunnelling

Why does $E_0 < V_0$ alone not prove that the transmitted part tunnelled?
Use $W_\mathrm{above}$ and your numerical uncertainty to argue whether your sub-barrier transmission is really tunnelling.
:::

## Part 5: Open question

Change the potential in one way of your own choosing and investigate one physical question about the scattering.
State your question and a prediction before calculating, compare a few values of one new parameter, and check one result by refinement.
If some probability stays trapped in the barrier region at the end, call it unresolved rather than reflected or transmitted.
Some possible directions:

- **Two barriers.**
  How does the transmission through two identical barriers depend on the gap between them?
  Can two barriers transmit *more* than one?
- **A smooth barrier.**
  Round off the edges of the square barrier while keeping its height and width fixed.
  How does the transmission change, and why?
- **A well instead of a barrier.**
  Can a particle be reflected by a dip in the potential ($V_0 < 0$)?

:::{exercise}
:label: ex-qm2-open

What did you investigate, and what did you predict?
Explain the change you found using the potential and the probability distributions.
What remains the same as for a single square barrier, and what limits the reliability of your conclusion?
:::

## What to hand in

See [](#assignments_page) for the deliverables and the check-in.

---

*This assignment was adapted from a draft by Robin Oosterhoff and Filip Sfetcu.*
