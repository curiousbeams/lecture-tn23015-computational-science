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
We approximate it by the domain $-L \leq x \leq L$ with $\psi(\pm L, t) = 0$, and only trust times at which the packet has negligible probability near the ends of the domain.
[](#fig-qm2-setup) shows the starting packet and the barrier it will meet in Part 3.

:::{figure} ../../figures/assignments/scattering-setup-dark.svg
:name: fig-qm2-setup-dark
:class: hidden dark:block
:enumerator: QM4.1
A Gaussian packet starting at $x_0 = -24$ with width $\sigma_x = 3$ and wavenumber $k_0 = 2$, moving towards a barrier of height $V_0 = 2$ and width $a = 1.6$.
Density and potential have separate vertical scales; the numerical domain extends well beyond this view.
:::

:::{figure} ../../figures/assignments/scattering-setup.svg
:name: fig-qm2-setup
:class: dark:hidden
A Gaussian packet starting at $x_0 = -24$ with width $\sigma_x = 3$ and wavenumber $k_0 = 2$, moving towards a barrier of height $V_0 = 2$ and width $a = 1.6$.
Density and potential have separate vertical scales; the numerical domain extends well beyond this view.
:::

## Part 1: A packet in position and momentum space

A plane wave $e^{ik_0 x}$ has a single, definite momentum $k_0$, but it is spread evenly over the whole line.
A *wave packet* is a localised version: the plane wave multiplied by an envelope that confines it to a region of width $\sigma_x$ around a position $x_0$.
We use a Gaussian envelope,

$$
\psi(x, 0) = A \exp\!\left[-\frac{(x - x_0)^2}{4\sigma_x^2}\right] e^{ik_0 x} .
$$

Confining the wave costs a definite momentum: the packet is a superposition of plane waves with momenta spread around $k_0$.
On the infinite line it has $A = (2\pi\sigma_x^2)^{-1/4}$, mean position $\langle x \rangle = x_0$ and spread $\Delta x = \sigma_x$, and mean momentum $\langle p \rangle = k_0$ with spread $\Delta p = 1/(2\sigma_x)$.
Its product $\Delta x\,\Delta p = 1/2$ is the smallest the uncertainty relation allows.

The position moments are $\langle x \rangle = \int x\,|\psi|^2\,dx$ and $\Delta x = \sqrt{\langle x^2 \rangle - \langle x \rangle^2}$.
The momentum wavefunction is

$$
\tilde\psi(p) = \frac{1}{\sqrt{2\pi}} \int \psi(x)\, e^{-ipx}\, dx ,
$$

and $\langle p \rangle$ and $\Delta p$ are defined in the same way, with $|\tilde\psi(p)|^2$ in place of $|\psi(x)|^2$.

:::{exercise}
:label: ex-qm2-packet

1. Build the packet for $x_0 = -24$, $k_0 = 2$ and $\sigma_x = 3$ on a grid with spacing $h = 0.1$ over $[-110, 110]$, and normalise it numerically.
2. Compute $\langle x \rangle$ and $\Delta x$.
3. Compute the momentum density $|\tilde\psi(p)|^2$ with the FFT from [](#fourier-transforms-1_page), as in the hint below, plot it including negative momenta, and verify that it integrates to one *without* renormalising it.
4. Compute $\langle p \rangle$ and $\Delta p$.
5. Repeat for $\sigma_x = 1.5$ and $6$, and tabulate $\Delta x$, $\Delta p$ and $\Delta x\,\Delta p$ for all three packets next to the Gaussian values.
6. Explain how narrowing the packet in position changes its momentum distribution, and what the normalisation check in momentum space tells you about your FFT scaling.
:::

:::{dropdown} Hint: from FFT to $|\tilde\psi(p)|^2$
Take `F = np.fft.fft(psi)` of your $N$ grid values, spaced by $h$.
The momenta are `p = 2 * np.pi * np.fft.fftfreq(N, h)`, spaced by $2\pi/(Nh)$, and the momentum density at those $p$ is

$$
|\tilde\psi(p)|^2 \approx \frac{h^2}{2\pi}\,|F|^2 .
$$

It covers negative and positive $p$ alike: do not fold or double it.
Apply `np.fft.fftshift` to `p` and to the density together, as in [](#fourier-transforms-1_page), to order them from negative to positive $p$.
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
The total probability $P(t) = \int |\psi|^2\,dx$ should stay equal to one.

:::{exercise}
:label: ex-qm2-free

1. Integrate these equations for the $\sigma_x = 3$ packet up to $t = 10$, with your RK4 from [](#ordinary-differential-equations-1_page) applied to the whole complex array at once and with $\Delta t = 0.005$.
2. Plot the density at $t = 0$, $5$ and $10$.
3. Plot $\langle x(t) \rangle$ and $\Delta x(t)$ together with the exact curves, and plot the momentum densities at $t = 0$ and $t = 10$.
4. Explain how the position distribution can spread while the momentum distribution stays the same, and why a moving packet is not a stationary state.
:::

:::{dropdown} Hint: stability
An explicit method like RK4 becomes unstable if the timestep is too large compared with $h^2$: roughly, it needs $\Delta t \lesssim 1.4\,h^2$.
Refining $h$ therefore requires a smaller $\Delta t$ as well.
:::

:::{exercise}
:label: ex-qm2-settings

1. Compute $P(t)$ during the run, without ever renormalising $\psi$, and the probability in the outer strips $0.9L < |x| < L$.
2. Repeat the run once with $\Delta t = 0.01$, and once with $h = 0.2$.
3. Plot the errors of $\langle x(t) \rangle$ and $\Delta x(t)$, relative to the exact curves, against time for all three runs, and plot $|P(t) - 1|$ in the same way.
4. Explain whether nearly perfect conservation of $P(t)$ guarantees that the motion and the spreading are accurate.
   Identify which of your checks revealed which kind of error, and state which settings you will use for the rest of the assignment.
:::

## Part 3: A collision

Introduce the square barrier

$$
V(x) = \begin{cases} V_0, & |x| < a/2, \\ 0, & |x| > a/2, \end{cases}
$$

with $V_0 = 2$ and $a = 1.6$.
On the grid, give any sample that lies exactly on an edge, $x = \pm a/2$, half the barrier height, $V_0/2$; this keeps the barrier the same width on every grid.
From here on, use the domain $[-130, 130]$, so that even the fastest outgoing packets stay away from its ends.

We label a packet by $E_0 = k_0^2/2$, the kinetic energy of its central momentum.
Its mean energy is slightly higher, $\langle E \rangle = E_0 + \Delta p^2/2 = E_0 + 1/(8\sigma_x^2)$, because of the momentum spread; for $\sigma_x = 3$ the difference is only $0.014$.
With $k_0 = 2$, $E_0$ is exactly $V_0$.

To follow the collision, split the line at $x = -b$ and $x = b$, with $b = 4$: the region between them is wide enough to contain the barrier and the part of the packet that is still interacting with it.

$$
R(t) = \int_{x < -b} |\psi|^2\, dx, \qquad P_\mathrm{mid}(t) = \int_{-b}^{b} |\psi|^2\, dx, \qquad T(t) = \int_{x > b} |\psi|^2\, dx .
$$

$R(t)$ is the reflected probability, $T(t)$ the transmitted probability, and $P_\mathrm{mid}(t)$ the probability still near the barrier.
Once the collision is over, $R(t)$ and $T(t)$ stop changing; we call these final values the reflection and transmission probabilities, $R_\infty$ and $T_\infty$.

:::{exercise}
:label: ex-qm2-collision

1. Follow the $\sigma_x = 3$ packet with $E_0 = V_0$ through the collision, up to $t = 40$.
2. Plot density snapshots before, during and after the collision, with the barrier marked.
3. Plot $R(t)$, $P_\mathrm{mid}(t)$ and $T(t)$ against time, verify that they add up to $P(t)$, and report $R_\infty$ and $T_\infty$.
4. Plot the momentum densities before and after the collision.
5. Explain which outgoing packet corresponds to which sign of momentum, and how your results show that the collision is over.
   Explain why $R_\infty + T_\infty \approx 1$ on its own is not enough to show that the ends of the domain had no influence.
:::

:::{dropdown} Hint: what to store during a run
Storing $\psi$ at every timestep fills your memory quickly: on $[-130, 130]$ one run takes a few hundred megabytes, and more than 1 GB on the finer grid of Part 4.
Store $\psi$ only at the times you want to plot, and compute $R(t)$, $P_\mathrm{mid}(t)$ and $T(t)$ while the run progresses, for example every few timesteps.
:::

## Part 4: Reflection, transmission and tunnelling

A packet with $E_0 < V_0$ is mostly below the barrier, but its spread of momenta means that a small part of it is not.
A momentum component $p$ has kinetic energy $p^2/2$, which exceeds the barrier height when $p > \sqrt{2V_0}$.
Only positive momenta move towards the barrier, so the part of the packet that could pass over the barrier even classically is

$$
W_\mathrm{above} = \int_{\sqrt{2V_0}}^{\infty} |\tilde\psi(p)|^2\, dp .
$$

:::{exercise}
:label: ex-qm2-trends

Keep $\sigma_x = 3$ and $x_0 = -24$, and set $k_0 = \sqrt{2E_0}$.

1. Compute $T_\infty$ for $E_0/V_0 = 0.5$, $0.75$, $1$ and $1.5$, at $a = 1.6$, and plot $T_\infty$ against $E_0/V_0$.
2. *Optional:* compute $T_\infty$ for barrier widths $a = 0.8$, $1.6$ and $2.4$, at $E_0/V_0 = 0.5$, and plot $\ln T_\infty$ against $a$.
3. Repeat the $E_0/V_0 = 0.5$, $a = 1.6$ run on a finer grid, $h = 0.05$ with $\Delta t = 0.0025$, and report the change in $T_\infty$.
4. Explain how the incident energy changes the transmission, and, if you did item 2, how the barrier width does.
   Identify which of your results show tunnelling, and which show reflection *above* a barrier.
:::

:::{exercise}
:label: ex-qm2-tunnelling

1. Compute $W_\mathrm{above}$ for the $E_0/V_0 = 0.5$ packet from its momentum density, as in Part 1.
2. Compare $W_\mathrm{above}$ with the $T_\infty$ of that packet, and with the change in $T_\infty$ you found on the finer grid.
3. Explain why $E_0 < V_0$ alone does not prove that the transmitted part tunnelled, and argue, using $W_\mathrm{above}$ and your numerical uncertainty, whether your sub-barrier transmission is really tunnelling.
:::

:::{dropdown} Hint: a fine momentum spacing
The momentum density falls steeply across $p = \sqrt{2V_0}$, so the FFT's default spacing $2\pi/(Nh)$ is too coarse to integrate the tail accurately.
Append zeros to $\psi$ before the FFT, for example to 16 times its length: this refines the spacing without changing the wavefunction.
:::

## Part 5: Open question

Change the potential in one way of your own choosing and investigate one question about the scattering.
Keep the packet and the numerical settings of Part 4, and compare with the single square barrier.
If some probability is still near the barrier region at the end of a run, call it unresolved rather than reflected or transmitted.
Some possible directions:

- **Two barriers.**
  Replace the barrier by two barriers of width $0.8$, with a gap $d = 0.8$, $1.6$ or $2.4$ between their inner edges, at $E_0/V_0 = 0.75$.
  How does the transmission depend on the gap, and can two barriers transmit *more* than one?
- **A smooth barrier.**
  Round off the edges of the barrier with $V(x) = \tfrac{V_0}{2}\left[\tanh\!\left(\frac{x + a/2}{w}\right) - \tanh\!\left(\frac{x - a/2}{w}\right)\right]$, for edge widths $w = 0.05$, $0.2$ and $0.4$, at $E_0 = V_0$.
  How does the transmission change as the edges soften, and why?
- **A well instead of a barrier.**
  Replace the barrier by a square well of the same width, $V = -V_\mathrm{well}$ for $|x| < a/2$, with depths $V_\mathrm{well} = 1$, $2$ and $4$, at $E_0 = 1$.
  Can a particle be reflected by a dip in the potential?

:::{exercise}
:label: ex-qm2-open

1. Write down your potential, your question and your prediction before you calculate.
2. Compute $R_\infty$ and $T_\infty$, and the unresolved probability, for each value of your parameter.
3. Plot $T_\infty$ against your parameter, together with the single-barrier value, and plot density snapshots for one representative case.
4. Repeat one representative run on a finer grid, and report the change in $T_\infty$.
5. Explain the change you found using the potential and the probability distributions, and whether it supports your prediction.
:::

## What to hand in

See [](#assignments_page) for the deliverables and the check-in.

---

*This assignment was adapted from a draft by Robin Oosterhoff and Filip Sfetcu.*
