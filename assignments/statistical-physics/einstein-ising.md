---
title: Ising Model
label: sp-einstein-ising_page
authors: [gvarnavides, lathouwers]
numbering:
  enumerator: SP2.%s
---

An isolated system has a fixed total energy, but its parts keep exchanging energy, and the share each part holds fluctuates.
In this assignment you first follow the energy exchange between two Einstein solids, and then let a small magnet exchange energy with a bath of oscillators.
As you make the bath larger and larger, the familiar Boltzmann factor $e^{-E/k_\mathrm{B}T}$ emerges from nothing more than counting microstates.

*How does the number of available bath microstates determine energy exchange, and when does it lead to the Boltzmann weight?*

We use $k_\mathrm{B} = 1$ throughout.

## Part 1: Two Einstein solids

An Einstein solid of $N$ distinguishable oscillators sharing $q$ indistinguishable energy quanta has multiplicity and entropy

$$
\Omega(N, q) = \binom{q + N - 1}{q}, \qquad S(N, q) = \ln \Omega(N, q).
$$

Take the oscillator quantum as the unit of energy, so that energy and number of quanta are the same number.
Two solids A and B exchange quanta while $q_A + q_B = q_\mathrm{tot}$ stays fixed.
Their multiplicities multiply, and every microstate of the combined system is equally likely, so the probability of a particular split is

$$
P(q_A) = \frac{e^{S_\mathrm{tot}(q_A)}}{\sum_{q=0}^{q_\mathrm{tot}} e^{S_\mathrm{tot}(q)}}, \qquad
S_\mathrm{tot}(q_A) = S(N_A, q_A) + S(N_B, q_\mathrm{tot} - q_A).
$$

The temperature of a solid follows from its entropy, $1/T = \partial S/\partial q$.

:::{exercise}
:label: ex-sp3-sharing

Use $N_A = 100$, $N_B = 200$ and $q_\mathrm{tot} = 300$.

1. Compute $S_\mathrm{tot}(q_A)$ for every allowed $q_A$, and plot it.
2. Compute and plot the normalised $P(q_A)$, and find its most probable value, mean and standard deviation.
3. Compute the temperatures $T_A(q_A)$ and $T_B(q_\mathrm{tot} - q_A)$ from your entropy values with a finite-difference method from [](#numerical-differentiation_page), and plot both against $q_A$.
4. Find where the two temperatures are equal with a root-finding method from [](#root-finding_page), interpolating your temperatures between integer $q_A$, and compare it with the maximum of $S_\mathrm{tot}$.
5. Explain where the entropy is largest, and whether equilibrium means equal energies or equal energy per oscillator.
   Explain why the most probable $q_A$, the mean $q_A$ and your equal-temperature point need not coincide exactly in a finite system.
:::

:::{dropdown} Hint: enormous numbers
$\Omega$ overflows a float long before $q = 300$, so work with $\ln\Omega$ throughout, for example with `scipy.special.gammaln`, since $\ln n! = $ `gammaln(n + 1)`.
To turn the entropies into probabilities without overflow, subtract the largest value $S_\mathrm{max}$ of $S_\mathrm{tot}$ first:

$$
P(q_A) = \frac{e^{S_\mathrm{tot}(q_A) - S_\mathrm{max}}}{\sum_q e^{S_\mathrm{tot}(q) - S_\mathrm{max}}} .
$$

The factor $e^{-S_\mathrm{max}}$ cancels between numerator and denominator, so the probabilities are unchanged, and every exponent is now at most zero.
:::

:::{exercise}
:label: ex-sp3-temperature

1. Show that along the line $q_A + q_B = q_\mathrm{tot}$, $dS_\mathrm{tot}/dq_A = 1/T_A - 1/T_B$.
2. Repeat your equal-temperature calculation with a different finite-difference step or formula, and report how much the root moves.
3. Explain why equal temperatures correspond to the maximum of the entropy, and what precision for the equal-temperature point the energy spacing and your derivative approximation support.
:::

## Part 2: Energy exchange by random sampling

Now let the two solids actually exchange energy.
Store the integer occupation of all $N_A + N_B$ oscillators, and start with all $q_\mathrm{tot}$ quanta in A.
In each attempted move, choose a donor and a receiver independently and uniformly from *all* oscillators, empty ones included.
Move one quantum if they are different oscillators and the donor has at least one quantum; otherwise leave everything unchanged.
One Monte Carlo *sweep* is $N_A + N_B$ attempted moves, a counting convention rather than physical time.

:::{exercise}
:label: ex-sp3-proposal

1. Implement the exchange, and verify after a run that no occupation is negative and that the total stays $q_\mathrm{tot}$.
2. Explain why a move with an empty donor must be rejected, and why the donor should *not* be chosen only among the occupied oscillators.
:::

:::{exercise}
:label: ex-sp3-exchange

1. Run for 5000 sweeps, recording $q_A$ and $q_B$ after every sweep, and plot them against sweeps.
2. Plot $S_\mathrm{tot}$ and the two temperatures during the run, using your functions from Part 1.
3. Discard the initial transient, and compute the mean and standard deviation of $q_A$; compare them with Part 1.
4. Repeat the run starting with all quanta in B and a different random seed, and compare the means.
5. Explain what changes during the initial transient and what keeps fluctuating afterwards, and whether $S_\mathrm{tot}$ increases at every step.
:::

## Part 3: A small magnet at fixed temperature

The magnet is an $L \times L$ square lattice of spins $s_i = \pm 1$, each interacting with its four nearest neighbours, with periodic boundaries: the right edge connects to the left edge and the top edge to the bottom edge, as in [](#fig-sp3-neighbours).
Its energy is

$$
E = -J \sum_{\langle i,j \rangle} s_i s_j ,
$$

where the sum runs over all *bonds*, the pairs $\langle i,j \rangle$ of nearest-neighbour spins, each pair counted once.
With periodic boundaries the lattice has $2L^2$ bonds: each spin's bond to its right neighbour and its bond to the neighbour below.
Flipping spin $i$ changes the energy by

$$
\Delta E_i = 2 J s_i \sum_{j \in \mathrm{nn}(i)} s_j ,
$$

where $s_i$ is its value *before* the flip and the sum runs over its four nearest neighbours $\mathrm{nn}(i)$.
$\Delta E_i$ can only be $-8J$, $-4J$, $0$, $4J$ or $8J$.

:::{figure} ../../figures/assignments/ising-neighbours-dark.svg
:name: fig-sp3-neighbours-dark
:class: hidden dark:block
:enumerator: SP2.1
The four nearest neighbours of a spin, without and with the periodic boundaries.
:::

:::{figure} ../../figures/assignments/ising-neighbours.svg
:name: fig-sp3-neighbours
:class: dark:hidden
The four nearest neighbours of a spin, without and with the periodic boundaries.
:::

At a fixed temperature $T$, the *Metropolis algorithm* samples the canonical distribution: choose a spin $i$ at random and flip it with probability $\min(1, e^{-\Delta E_i / T})$.
One sweep is $L^2$ attempted flips.
For $L = 4$ the number of configurations $g(E)$ with each energy is known exactly.
The table lists it for each $|E|$, valid for both $+|E|$ and $-|E|$; energies not listed cannot occur, and the counts sum to $2^{16}$.

| $\lvert E \rvert / J$ | 0 | 4 | 8 | 12 | 16 | 20 | 24 | 32 |
|---|---|---|---|---|---|---|---|---|
| $g(+\lvert E\rvert) = g(-\lvert E\rvert)$ | 20524 | 13568 | 6688 | 1728 | 424 | 64 | 32 | 2 |

:::{exercise}
:label: ex-sp3-ising

Use $J = 1$ and $L = 4$.

1. Compute the energy of the fully aligned lattice, and of one with a single reversed spin.
2. Verify the formula for $\Delta E_i$ against the difference of two full energy calculations, for a few flips that include one at an edge.
3. Explain why each bond must be counted only once in the total energy, and how your checks confirm the periodic neighbours and the sign of $\Delta E_i$.
:::

:::{exercise}
:label: ex-sp3-canonical

1. Implement Metropolis sampling, and run it at $T = 4/\ln 6 \approx 2.23$ for about 10 000 sweeps, starting from one reversed spin.
2. Discard a transient, and plot the histogram of the sampled energies together with the exact canonical prediction $P(E) \propto g(E)\,e^{-E/T}$.
3. Explain how well your sampled distribution agrees with $g(E)\,e^{-E/T}$, and why the probability of an energy is not simply proportional to $e^{-E/T}$.
:::

## Part 4: Where does the Boltzmann factor come from?

In Part 3 the temperature was imposed by hand.
Now replace it with something physical: couple the magnet to an Einstein solid of $N_B$ oscillators with $q_B$ quanta, and keep the combined system isolated.
Give the bath quantum the value $\epsilon_B = 4J$, so that every spin flip exchanges a whole number of quanta, and the total energy $E + \epsilon_B q_B$ is conserved exactly.

A proposed flip of spin $i$ would leave the bath with $q_B' = q_B - \Delta E_i / \epsilon_B$ quanta.
Reject it if $q_B' < 0$, and otherwise accept it with probability

$$
p_\mathrm{acc} = \min\!\left(1, \frac{\Omega(N_B, q_B')}{\Omega(N_B, q_B)}\right),
$$

the ratio of the numbers of bath microstates after and before.
For a finite bath the predicted energy distribution of the magnet is then $P(E) \propto g(E)\,\Omega\!\big(N_B, (E_\mathrm{tot} - E)/\epsilon_B\big)$, including only energies that leave the bath a non-negative number of quanta.

The bath's temperature follows from its entropy, $1/T_B = \partial S(N_B, q_B)/\partial(\epsilon_B q_B)$, which on the integer quanta we evaluate as the forward difference $1/T_B = [S(N_B, q_B + 1) - S(N_B, q_B)]/\epsilon_B$.
Its *relative fluctuation* during a run, $\sigma(T_B)/\langle T_B \rangle$, is the standard deviation of $T_B$ over the run divided by its mean: it measures how far the bath's temperature wanders, as a fraction of its value.

:::{exercise}
:label: ex-sp3-bath

1. Show that for large $N_B$ and $q_B$, the bath temperature is $T_B \approx \epsilon_B / \ln(1 + N_B/q_B)$, so that it depends only on the number of quanta per oscillator.
   Evaluate it for $q_B/N_B = 0.2$.
2. Explain, when $\Delta E_i > 0$, whether the bath gains or loses energy, and why such a flip can still be accepted.
:::

:::{exercise}
:label: ex-sp3-limit

Start every run from one reversed spin and $q_B = 0.2\,N_B$ quanta, so that by item 1 of the previous exercise every bath starts at the same temperature, that of Part 3.

1. Run for about 10 000 sweeps for $N_B = 50$, $200$, $1000$ and $5000$, and verify that $E + \epsilon_B q_B$ never changes.
2. Plot, for each bath, the sampled energy distribution of the magnet together with the finite-bath prediction and the canonical one from Part 3.
3. Compute $T_B$ during each run, and plot $\sigma(T_B)/\langle T_B \rangle$ against $N_B$.
4. Compute the acceptance probability of a flip with $\Delta E_i = 4J$ at $q_B = 0.2\,N_B$ for each bath, and tabulate it next to the canonical value $e^{-4J/T}$ at $T = 4/\ln 6$.
5. Explain why a larger bath changes its temperature less when it exchanges the same energy with the magnet.
   Show, using $S_B(E_B - \Delta E_i) \approx S_B(E_B) - \Delta E_i / T$, how the acceptance rule turns into $\min(1, e^{-\Delta E_i/T})$.
   Identify for which of your baths the acceptance of a $\Delta E_i = 4J$ flip is within 1% of the canonical value, and for which $\sigma(T_B)/\langle T_B\rangle$ is below 1%.
:::

## Part 5: Open question

Use your canonical sampler from Part 3 to investigate one question of your own about the magnet.
Some possible directions:

- **Order and temperature.**
  How does the magnet's order change with temperature on a larger lattice, say $L = 12$ at $T/J = 1.5$, $2.5$ and $4$?
  Look at the energy per spin, at $\langle |M| \rangle / L^2$ with $M = \sum_i s_i$, and at snapshots of the spins.
- **Heat capacity from fluctuations.**
  In the canonical ensemble the heat capacity follows from the energy fluctuations, $C = (\langle E^2 \rangle - \langle E \rangle^2)/T^2$.
  How does $C$ depend on temperature? For $L = 4$ you can compare with an exact calculation from $g(E)$.
- **Finite size.**
  At one temperature near $T/J \approx 2.3$, how does $\langle |M| \rangle / L^2$ change between $L = 4$, $8$ and $16$?

:::{exercise}
:label: ex-sp3-open

1. Write down your question and your prediction before you calculate.
2. Compute the quantities your question needs for a few informative values of one parameter.
3. Plot them against the parameter, and include snapshots or distributions where they help.
4. Include one check that your conclusion is not an artefact of a too-short or too-correlated run, for example a longer run or a second seed.
5. Explain whether your results support your prediction, and what your check establishes.
:::

## What to hand in

See [](#assignments_page) for the deliverables and the check-in.

---

*This assignment was adapted from a draft by Robin Oosterhoff and Filip Sfetcu.*
