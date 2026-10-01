---
title: Computational Assignments
short_title: Overview
label: assignments_page
authors: [gvarnavides, lathouwers]
numbering:
  heading_2: false
---

Alongside the weekly exercises, TN23015 has two computational group assignments: one in statistical physics and one in quantum mechanics.

You will work in groups of four for one to two weeks, to complete one quantum mechanics assignment and one statistical Physics assignment.
The schedule and groups are on the [Brightspace](https://brightspace.tudelft.nl/) page.

## The assignments

**Quantum mechanics**

- [](#qm-quantum-domains_page): how the shape of a hard-wall region sets its energies and standing waves.
- [](#qm-yukawa_page): bound states of a short-range attraction model.
- [](#qm-tunnelling_page): stationary states by shooting and by diagonalisation, and tunnelling between two wells.
- [](#qm-scattering_page): a wave packet that moves, spreads, and splits at a barrier.
- [](#qm-slit-interference_page): interference from adding amplitudes, and how a pattern builds up one detection at a time.

**Statistical physics**

- [](#sp-lennard-jones_page): the orbit of a bound dimer in phase space, and the entropy and temperature it defines.
- [](#sp-einstein-ising_page): energy exchange between Einstein solids, and how a large bath turns into the Boltzmann factor for a small magnet.
- [](#sp-brownian_page): friction, thermal kicks, diffusion, and the Boltzmann distribution, using stochastic update rules.
- [](#sp-chemotaxis_page): from random walks to diffusion, illustrating how bacteria swim towards food without seeing it.
- [](#sp-ion-channels_page): random switching of single molecules, and the predictable response of a population of molecules.

## Assignments structure

Every assignment has four core parts and ends with one open question.

The first part usually builds the functions that the rest of the assignment reuses, so it is worth doing together as a group.
After that, many teams find it works well to divide the middle parts between them and come back together for the open question.
How you divide the work is up to you, and the natural split differs from one assignment to the next.

Each part ends with numbered exercises.
Answer these in your report, supported by your own figures and numbers.

There's also an open question at the end.
The handout suggests a few directions, but you may also propose your own.
State your question and a prediction before you calculate, then investigate it, and decide whether your prediction holds.

## Deliverables

Submit the following on the Brightspace group assignment:

- **A Jupyter or marimo notebook**, executed, so that every figure and number in your report can be traced back to the code that produced it.
- **A short PDF report** answering the numbered exercises and presenting your open question.

In the exercise class immediately after the deadline, each team will have a 5-minute check-in with one of the teaching staff, where the whole team needs to be present.
Expect to talk about your results, the choices you made, and your open question.

## Packages

Use Python with NumPy, SciPy, and Matplotlib, i.e. the same packages as in the rest of the book, on your own computer.
Where a part asks you to use a method from the book, such as your own bisection or RK4 implementation, write and use it there.
Elsewhere, library routines such as `scipy.integrate.solve_ivp` or `scipy.linalg.eigh` are fine.

## A note on using AI

An AI assistant can write a lot of the code in these assignments.
As with the exercises in this book, we are not going to pretend otherwise.

But the assignments are about more than working code: they ask you to decide whether a result can be trusted, and to explain what it means.
This is also what the in-person check-in will assess.
A team that has let an LLM do the thinking will find five minutes of questions about its report surprisingly long.

## Acknowledgements

These assignments were adapted from drafts written by Robin Oosterhoff and Filip Sfetcu, teaching assistants for this course.
