---
title: Ising Model
label: sp-einstein-ising_page
authors: [gvarnavides, lathouwers]
numbering:
  enumerator: SP2.%s
---

An isolated system has a fixed total energy, but its parts keep exchanging energy and fluctuating.
In this assignment you first follow the energy exchange between two Einstein solids, then let a small magnet exchange energy with a bath of oscillators.
Making that bath larger and larger, you will see the familiar Boltzmann factor $e^{-E/k_\mathrm{B}T}$ emerge from counting microstates.

*How does the number of available bath microstates determine energy exchange, and when does it lead to the Boltzmann weight?*

We use $k_\mathrm{B} = 1$ throughout.

## Part 1: Two Einstein solids

An Einstein solid of $N$ distinguishable oscillators sharing $q$ indistinguishable energy quanta has multiplicity and entropy

$$
\Omega(N, q) = \binom{q + N - 1}{q}, \qquad S(N, q) = \ln \Omega(N, q).
$$

Take the oscillator quantum as the unit of energy, so that energy and number of quanta are the same number.
Two solids A and B exchange quanta while $q_A + q_B = q_\mathrm{tot}$ stays fixed.
Their multiplicities multiply, so the probability of a particular split is

$$
P(q_A) = \frac{e^{S_\mathrm{tot}(q_A)}}{\sum_{q=0}^{q_\mathrm{tot}} e^{S_\mathrm{tot}(q)}}, \qquad
S_\mathrm{tot}(q_A) = S(N_A, q_A) + S(N_B, q_\mathrm{tot} - q_A).
$$

- For $N_A = 100$, $N_B = 200$ and $q_\mathrm{tot} = 300$, compute and plot $S_\mathrm{tot}(q_A)$ for every allowed $q_A$, and the normalised $P(q_A)$ with its mean and standard deviation.
- The temperature of a solid follows from $1/T = \partial S / \partial q$.
  Estimate this derivative from your entropy values with your own finite-difference function, using [](#numerical-differentiation_page): central differences inside the range and one-sided differences at its ends.
  Plot $T_A(q_A)$ and $T_B(q_\mathrm{tot} - q_A)$.
- Find where the two temperatures are equal with a root-finding method from [](#root-finding_page), interpolating the discrete temperatures between integers, and compare it with the maximum of $S_\mathrm{tot}$.

:::{dropdown} Hint: enormous numbers
$\Omega$ overflows a float long before $q = 300$.
Work with $\ln\Omega$ throughout, for example with `scipy.special.gammaln` (since $\ln n! = $ `gammaln(n + 1)`), and subtract the largest $S_\mathrm{tot}$ before exponentiating: this does not change the normalised probabilities.
:::

:::{exercise}
:label: ex-sp3-sharing

Where is the entropy largest?
Does equilibrium mean equal energies, or equal energy per oscillator?
How do the most probable $q_A$, the mean $q_A$ and your equal-temperature root compare, and why need they not coincide exactly in a finite system?
:::

:::{exercise}
:label: ex-sp3-temperature

Why does equal temperature correspond to the entropy maximum?
What precision for the equal-temperature point do the energy spacing and your derivative approximation support?
:::

## Part 2: Energy exchange by random sampling

Now let the two solids actually exchange energy.
Store the integer occupation of all $N_A + N_B$ oscillators, and start with all $q_\mathrm{tot}$ quanta in A.
In each attempted move, choose a donor and a receiver independently and uniformly from *all* oscillators, empty ones included.
Move one quantum if they are different oscillators and the donor has at least one quantum; otherwise leave everything unchanged.
One Monte Carlo *sweep* is $N_A + N_B$ attempted moves, a counting convention rather than physical time.

- Run for 5000 sweeps, recording $q_A$ and $q_B$ after every sweep, and check that no occupation becomes negative and the total stays fixed.
- Plot $q_A$ and $q_B$ against sweeps, and use your functions from Part 1 to follow $S_\mathrm{tot}$ and the two temperatures.
- Discard the initial transient and compare the mean and standard deviation of $q_A$ with Part 1.
  Check that your mean is stable by repeating the run from the opposite starting split (all quanta in B) with a different seed.

:::{exercise}
:label: ex-sp3-proposal

Why must a move with an empty donor be rejected, and why should the donor *not* be chosen only among the occupied oscillators?
:::

:::{exercise}
:label: ex-sp3-exchange

What changes during the initial transient, and what keeps fluctuating afterwards?
Does $S_\mathrm{tot}$ increase at every step?
How well do the stationary mean and fluctuations agree with Part 1?
:::

## Part 3: A small magnet at fixed temperature

The magnet is an $L \times L$ square lattice of spins $s_i = \pm 1$, each interacting with its four nearest neighbours, with periodic boundaries: the right edge connects to the left edge and the top edge to the bottom edge.
Its energy is

$$
E = -J \sum_{\langle i,j \rangle} s_i s_j,
$$

where each bond is counted once.
Flipping spin $i$ changes the energy by $\Delta E = 2 J s_i \sum_{j \in \mathrm{nn}(i)} s_j$, which can only be $-8J$, $-4J$, $0$, $4J$ or $8J$.

:::{figure} ../../figures/assignments/ising-neighbours-dark.svg
:name: fig-sp3-neighbours-dark
:class: hidden dark:block
The four nearest neighbours of a spin, without and with the periodic boundaries.
:::

:::{figure} ../../figures/assignments/ising-neighbours.svg
:name: fig-sp3-neighbours
:class: dark:hidden
The four nearest neighbours of a spin, without and with the periodic boundaries.
:::

At a fixed temperature $T$, the Metropolis algorithm samples the canonical distribution: choose a spin at random and flip it with probability $\min(1, e^{-\Delta E / T})$.
One sweep is $L^2$ attempted flips.
For $L = 4$ the number of configurations $g(E)$ with each energy is known exactly.
The table lists it for each $|E|$, valid for both $+|E|$ and $-|E|$; energies not listed cannot occur, and the counts sum to $2^{16}$.

| $\lvert E \rvert / J$ | 0 | 4 | 8 | 12 | 16 | 20 | 24 | 32 |
|---|---|---|---|---|---|---|---|---|
| $g(+\lvert E\rvert) = g(-\lvert E\rvert)$ | 20524 | 13568 | 6688 | 1728 | 424 | 64 | 32 | 2 |

- Use $J = 1$ and $L = 4$.
  Calculate the energy of the fully aligned lattice and of one with a single reversed spin, and check the $\Delta E$ formula against the difference of two full energy calculations for a few flips, including one at an edge.
- Implement Metropolis sampling and run it at $T = 4/\ln 6 \approx 2.23$, starting from one reversed spin, for about 10 000 sweeps.
  Discard a transient and compare the histogram of the sampled energies with the exact canonical prediction $P(E) \propto g(E)\,e^{-E/T}$.

:::{exercise}
:label: ex-sp3-ising

Why must each bond be counted only once in the total energy, and how did your checks confirm the periodic neighbours and the sign of $\Delta E$?
:::

:::{exercise}
:label: ex-sp3-canonical

How well does your sampled energy distribution agree with $g(E)\,e^{-E/T}$?
Why is the probability of an energy not simply proportional to $e^{-E/T}$?
:::

## Part 4: Where does the Boltzmann factor come from?

In Part 3 the temperature was imposed by hand.
Now replace it with something physical: couple the magnet to an Einstein solid of $N_B$ oscillators with $q_B$ quanta, and keep the combined system isolated.
Give the bath quantum the value $\epsilon_B = 4J$, so that every spin flip exchanges a whole number of quanta, and the total energy $E + \epsilon_B q_B$ is conserved exactly.
A proposed flip with energy change $\Delta E$ would leave the bath with $q_B' = q_B - \Delta E / \epsilon_B$ quanta.
Reject it if $q_B' < 0$, and otherwise accept it with probability

$$
p_\mathrm{acc} = \min\!\left(1, \frac{\Omega(N_B, q_B')}{\Omega(N_B, q_B)}\right),
$$

the ratio of the numbers of bath microstates after and before.
For a finite bath the predicted energy distribution of the magnet is then $P(E) \propto g(E)\,\Omega\!\big(N_B, (E_\mathrm{tot} - E)/\epsilon_B\big)$, including only energies that leave the bath a non-negative number of quanta.

- Start from one reversed spin and $q_B = 0.2\,N_B$ quanta, and run for about 10 000 sweeps for $N_B = 50$, $200$, $1000$ and $5000$.
  Check that $E + \epsilon_B q_B$ never changes.
- For each bath, compare the sampled energy distribution with the finite-bath prediction and with the canonical one from Part 3.
- Follow the bath temperature during each run, using the forward difference $1/T_B = [S(N_B, q_B + 1) - S(N_B, q_B)]/\epsilon_B$, and plot its relative fluctuation $\sigma(T_B) / \langle T_B \rangle$ against $N_B$.
- Compare the acceptance probability of a flip with $\Delta E = 4J$ at $q_B = 0.2\,N_B$ for each bath with the canonical value $e^{-4J/T}$ at $T = 4/\ln 6$.

:::{exercise}
:label: ex-sp3-bath

When $\Delta E > 0$, does the bath gain or lose energy, and why can such a flip still be accepted?
:::

:::{exercise}
:label: ex-sp3-limit

Why does a larger bath change its temperature less when it exchanges the same energy with the magnet?
Using $S_B(E_B - \Delta E) \approx S_B(E_B) - \Delta E / T$, explain how the acceptance rule turns into $\min(1, e^{-\Delta E/T})$.
For which of your baths is the acceptance of a $\Delta E = 4J$ flip within 1% of the canonical value, and for which is $\sigma(T_B)/\langle T_B\rangle$ below 1%?
:::

## Part 5: Open question

Use your canonical sampler from Part 3 to investigate one question of your own about the magnet.
State your question and a prediction before calculating, vary one parameter over a few informative values, and include one check that your conclusion is not an artefact of a too-short or too-correlated run.
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

What did you investigate, and what did you predict?
How do your results support or challenge the prediction, and what does your check establish?
:::

## What to hand in

See [](#assignments_page) for the deliverables and the check-in.

---

*This assignment was adapted from a draft by Robin Oosterhoff and Filip Sfetcu.*
