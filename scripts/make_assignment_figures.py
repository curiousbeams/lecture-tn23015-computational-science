"""Draw the figures for the computational assignment handouts, in a light and a dark version.

    .venv/bin/python scripts/make_assignment_figures.py            # all of them
    .venv/bin/python scripts/make_assignment_figures.py chemotaxis # just some

Writes `figures/assignments/<name>.svg` (light, white background) and `<name>-dark.svg`
(transparent background, light ink). The handouts show one or the other with the theme's
Tailwind classes, as in the workshop pages:

    :::{figure} ../../figures/assignments/<name>.svg
    :class: dark:hidden
    :::
    :::{figure} ../../figures/assignments/<name>-dark.svg
    :class: hidden dark:block
    :enumerated: false
    :::

The TA drafts referenced PDF figures that were never committed (and TikZ drawings), so everything
is redrawn here from the models themselves.

**Only model inputs are drawn** -- potentials, geometries, schematics. Nothing a student is asked
to compute appears in a figure, so this script and its output can be public.
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib import patches  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / "figures" / "assignments"
plt.rcParams.update({"font.size": 11, "svg.hashsalt": "tn23015", "axes.spines.top": False,
                     "axes.spines.right": False})

# The book theme's dark page background is Tailwind stone-900. Filled shapes that have to *cover*
# something (the hole of an annulus, the background of a label) are painted in it, so that they
# look transparent on the page while the SVG itself has a transparent background.
STONE_900 = "#1c1917"
THEMES = {
    "light": {
        "suffix": "",
        "colours": dict(BLUE="#1665a8", ORANGE="#c65c15", GREEN="#2e8540", GREY="#888888",
                        INK="black", PAPER="white", MUTED="#555555",
                        MEMBRANE="#d9c7a3", MEMBRANE_TEXT="#6b5a3a",
                        CHEMO=("Greens", 1.6), BACKGROUND="white"),
        "rc": {},
    },
    "dark": {
        "suffix": "-dark",
        "colours": dict(BLUE="#5aa9e6", ORANGE="#f08c4a", GREEN="#5cc27a", GREY="#a8a29e",
                        INK="#e7e5e4", PAPER=STONE_900, MUTED="#a8a29e",
                        MEMBRANE="#8c7a55", MEMBRANE_TEXT="#d6c7a3",
                        CHEMO=(LinearSegmentedColormap.from_list("chemo", [STONE_900, "#2f8a4a"]), 1.0),
                        BACKGROUND="none"),
        "rc": {"text.color": "#e7e5e4", "axes.labelcolor": "#e7e5e4", "axes.edgecolor": "#e7e5e4",
               "xtick.color": "#e7e5e4", "ytick.color": "#e7e5e4", "patch.edgecolor": "#e7e5e4",
               "axes.facecolor": "none", "figure.facecolor": "none",
               "legend.facecolor": STONE_900, "legend.edgecolor": "#57534e", "legend.framealpha": 0.9},
    },
}
# Set per theme by `main` before each figure is drawn.
BLUE = ORANGE = GREEN = GREY = INK = PAPER = MUTED = MEMBRANE = MEMBRANE_TEXT = BACKGROUND = None
CHEMO = None
SUFFIX = ""
FIGURES = {}


def figure(name):
    def register(fn):
        FIGURES[name] = fn
        return fn
    return register


def arrow(**kw):
    """Annotation arrow properties in the current ink colour, unless a colour is given."""
    return {"color": INK, **kw}


def save(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / f"{name}{SUFFIX}.svg", bbox_inches="tight", facecolor=BACKGROUND,
                metadata={"Date": None})
    plt.close(fig)
    print(f"  {name}{SUFFIX}.svg")


@figure("chemotaxis")
def chemotaxis():
    fig, ax = plt.subplots(figsize=(8, 2.6))
    Q, w = 10.0, 4.0
    q = np.linspace(0, Q, 400)
    c = np.exp(-((Q - q) ** 2) / (2 * w**2))
    cmap, vmax = CHEMO
    ax.imshow(c[None, :], extent=(0, Q, 0, 2), aspect="auto", cmap=cmap, vmin=0, vmax=vmax,
              origin="lower")
    ax.add_patch(patches.Rectangle((0, 0), Q, 2, fill=False, lw=1.5, edgecolor=INK))
    for x0, dx, text in [(1.8, 1.6, "improving concentration:\nlower tumble rate"),
                         (8.2, -1.6, "worsening concentration:\nhigher tumble rate")]:
        ax.add_patch(patches.Ellipse((x0, 1.35), 0.55, 0.3, color=ORANGE))
        ax.annotate("", xy=(x0 + dx, 1.35), xytext=(x0 + 0.35 * np.sign(dx), 1.35),
                    arrowprops=arrow(arrowstyle="->", lw=1.5))
        ax.text(x0 + dx / 2, 0.45, text, ha="center", va="center", fontsize=9.5)
    ax.annotate("", xy=(8, 2.3), xytext=(2, 2.3), annotation_clip=False,
                arrowprops=arrow(arrowstyle="->", lw=1.5, color=GREEN))
    ax.text(5, 2.45, "nutrient concentration $c(q)$ increases to the right", ha="center",
            va="bottom")
    ax.text(0, -0.15, "$q = 0$", ha="center", va="top")
    ax.text(Q, -0.15, "$q = Q$", ha="center", va="top")
    ax.set(xlim=(-0.3, Q + 0.3), ylim=(-0.2, 2.9))
    ax.axis("off")
    save(fig, "chemotaxis-channel")


@figure("ising")
def ising():
    L = 4
    fig, axes = plt.subplots(1, 2, figsize=(7.5, 3.8))
    cases = [((1, 2), "an interior site"), ((0, 0), "an edge site: neighbours wrap around")]
    for ax, ((r0, c0), title) in zip(axes, cases):
        steps = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        neighbours = {((r0 + dr) % L, (c0 + dc) % L) for dr, dc in steps}
        for r in range(L):
            for c in range(L):
                colour = ORANGE if (r, c) == (r0, c0) else (BLUE if (r, c) in neighbours else PAPER)
                ax.add_patch(patches.Rectangle((c, L - 1 - r), 1, 1, facecolor=colour,
                                               edgecolor=INK, lw=1, alpha=0.85))
        x0, y0 = c0 + 0.5, L - 1 - r0 + 0.5
        for dr, dc in steps:
            r, c = (r0 + dr) % L, (c0 + dc) % L
            x1, y1 = c + 0.5, L - 1 - r + 0.5
            if 0 <= r0 + dr < L and 0 <= c0 + dc < L:
                ax.plot([x0, x1], [y0, y1], color=INK, lw=2)
                continue
            # Leave the grid through one edge, come back in through the opposite one.
            wrap = arrow(arrowstyle="->", lw=1.5, ls="--")
            ax.annotate("", xy=(x0 + 0.95 * dc, y0 - 0.95 * dr), xytext=(x0 + 0.3 * dc, y0 - 0.3 * dr),
                        arrowprops=wrap, annotation_clip=False)
            ax.annotate("", xy=(x1 - 0.3 * dc, y1 + 0.3 * dr), xytext=(x1 - 0.95 * dc, y1 + 0.95 * dr),
                        arrowprops=wrap, annotation_clip=False)
        ax.set(xlim=(-0.7, L + 0.7), ylim=(-0.7, L + 0.7), aspect="equal")
        ax.set_title(title, fontsize=11)
        ax.axis("off")
    fig.text(0.5, 0.02, "selected spin (orange) and its four nearest neighbours (blue)", ha="center",
             fontsize=10)
    save(fig, "ising-neighbours")


@figure("ion-channel")
def ion_channel():
    fig, axes = plt.subplots(1, 2, figsize=(7.5, 3.0))
    for ax, is_open in zip(axes, [False, True]):
        gap = 0.5 if is_open else 0.0
        for y0 in [0.0, 0.7]:                      # the two leaflets of the membrane
            for x0, x1 in [(-3.0, -0.9 - gap / 2), (0.9 + gap / 2, 3.0)]:
                ax.add_patch(patches.Rectangle((x0, y0), x1 - x0, 0.3, color=MEMBRANE))
        for sign in [-1, 1]:                       # the two halves of the channel protein
            x = sign * (gap / 2 + 0.45)
            ax.add_patch(patches.FancyBboxPatch((x - 0.45, -0.25), 0.9, 1.5,
                                                boxstyle="round,pad=0.05", color=BLUE))
        rng = np.random.default_rng(3)
        ax.plot(rng.uniform(-2.5, 2.5, 9), rng.uniform(1.45, 1.9, 9), "o", color=ORANGE, ms=5)
        ax.plot(rng.uniform(-2.5, 2.5, 3), rng.uniform(-0.75, -0.4, 3), "o", color=ORANGE, ms=5)
        if is_open:
            ax.annotate("", xy=(0, -0.55), xytext=(0, 1.55),
                        arrowprops=arrow(arrowstyle="->", lw=2, color=ORANGE))
        ax.text(0, 2.15, "open, $s = 1$" if is_open else "closed, $s = 0$", ha="center", fontsize=11)
        ax.text(3.1, 0.5, "membrane", fontsize=8.5, va="center", color=MEMBRANE_TEXT)
        ax.set(xlim=(-3.2, 4.2), ylim=(-0.9, 2.4), aspect="equal")
        ax.axis("off")
    save(fig, "ion-channel")


@figure("lennard-jones")
def lennard_jones():
    u = lambda q: q**-12 - 2 * q**-6
    e = -0.5
    q_in, q_out = (1 + np.sqrt(1 + e)) ** (-1 / 6), (1 - np.sqrt(1 + e)) ** (-1 / 6)
    fig, (ax0, ax1) = plt.subplots(1, 2, figsize=(9, 3.4))
    q = np.linspace(0.86, 2.6, 600)
    ax0.plot(q, u(q), color=BLUE, lw=2, label="$u(q) = q^{-12} - 2q^{-6}$")
    ax0.axhline(0, color=GREY, lw=0.8)
    ax0.hlines(e, q_in, q_out, color=ORANGE, lw=2, label="$e = -0.5$")
    for qt, lab in [(q_in, r"$q_\mathrm{in}$"), (q_out, r"$q_\mathrm{out}$")]:
        ax0.plot(qt, e, "o", color=ORANGE)
        ax0.annotate(lab, (qt, e), xytext=(-8 if qt < 1 else 8, -16), textcoords="offset points",
                     ha="right" if qt < 1 else "left")
    ax0.set(xlabel="separation $q$", ylabel="energy", ylim=(-1.15, 1.0), xlim=(0.86, 2.6))
    ax0.legend(loc="upper right", fontsize=9)
    qq = np.linspace(q_in, q_out, 800)
    p = np.sqrt(np.maximum(2 * (e - u(qq)), 0))
    ax1.fill_between(qq, -p, p, color=BLUE, alpha=0.15, label="area $A(e)$")
    ax1.plot(qq, p, color=BLUE, lw=2, label="$p_+(q; e)$")
    ax1.plot(qq, -p, color=BLUE, lw=2, ls="--", label="$p_-(q; e)$")
    ax1.set(xlabel="separation $q$", ylabel="momentum $p$", xlim=(0.86, 1.35))
    ax1.legend(loc="upper right", fontsize=9)
    fig.tight_layout()
    save(fig, "lennard-jones")


@figure("double-well")
def double_well():
    Vb, b = 5.0, 1.0
    x = np.linspace(-2.0, 2.0, 600)
    V = Vb * ((x / b) ** 2 - 1) ** 2
    fig, ax = plt.subplots(figsize=(6.5, 3.2))
    ax.plot(x, V, color=BLUE, lw=2)
    ax.annotate("", xy=(0, Vb), xytext=(0, 0), arrowprops=arrow(arrowstyle="<->", lw=1.3))
    ax.text(0.06, Vb / 2, "$V_b$", va="center")
    ax.annotate("", xy=(b, -0.9), xytext=(-b, -0.9), arrowprops=arrow(arrowstyle="<->", lw=1.3))
    ax.text(0, -1.5, "$2b$", ha="center", va="top")
    for xm in [-b, b]:
        ax.plot([xm, xm], [-0.9, 0], color=GREY, lw=0.8, ls=":")
    ax.axhline(0, color=GREY, lw=0.8)
    ax.set(xlabel="$x$", ylabel="$V(x)$", ylim=(-2.5, 9), xlim=(-2, 2))
    save(fig, "double-well")


@figure("scattering")
def scattering():
    x0, s, k0, V0, a = -24.0, 3.0, 2.0, 2.0, 1.6
    x = np.linspace(-40, 20, 3000)
    psi = (2 * np.pi * s**2) ** -0.25 * np.exp(-((x - x0) ** 2) / (4 * s**2)) * np.exp(1j * k0 * x)
    fig, ax = plt.subplots(figsize=(7.5, 2.8))
    ax.plot(x, np.real(psi), color=BLUE, lw=0.8, alpha=0.5, label=r"Re $\psi(x, 0)$")
    ax.plot(x, np.abs(psi) ** 2, color=BLUE, lw=2, label=r"$|\psi(x, 0)|^2$")
    ax.annotate("", xy=(x0 + 7, 0.38), xytext=(x0 + 1, 0.38), arrowprops=arrow(arrowstyle="->", lw=1.5))
    ax.text(x0 + 8, 0.38, "$k_0$", ha="left", va="center")
    ax.set(xlabel="$x$", ylabel="amplitude / density", ylim=(-0.42, 0.42))
    ax2 = ax.twinx()
    ax2.fill_between(x, 0, np.where(np.abs(x) < a / 2, V0, 0), color=ORANGE, alpha=0.6, step="mid", lw=0, label="barrier $V(x)$")
    ax2.set(ylabel="$V(x)$", ylim=(-2.8, 2.8), yticks=[0, 1, 2])
    ax2.spines["top"].set_visible(False)
    h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc="lower left", fontsize=8.5)
    save(fig, "scattering-setup")


@figure("slits")
def slits():
    fig, ax = plt.subplots(figsize=(7, 3.2))
    for y0, y1 in [(-1.4, -0.75), (-0.35, 0.35), (0.75, 1.4)]:       # opaque parts of the mask
        ax.plot([0, 0], [y0, y1], color=INK, lw=4, solid_capstyle="butt")
    ax.plot([6, 6], [-1.4, 1.4], color=INK, lw=2)                    # the screen
    ax.plot([-1.8, 6.8], [0, 0], color=GREY, lw=0.8, ls="--")
    for y in [-0.55, 0.55]:
        ax.annotate("", xy=(-0.2, y), xytext=(-1.8, y), arrowprops=arrow(arrowstyle="->", lw=1.2))
        ax.plot([0, 6], [y, 0.85], color=GREY, lw=0.8)
    ax.plot(6, 0.85, "o", color=ORANGE)
    ax.annotate("", xy=(6.5, 0.85), xytext=(6.5, 0), arrowprops=arrow(arrowstyle="<->", lw=1))
    ax.text(6.6, 0.42, "$X$", va="center")
    ax.annotate("", xy=(0.45, 0.75), xytext=(0.45, 0.35), arrowprops=arrow(arrowstyle="<->", lw=1))
    ax.text(0.55, 0.55, "$a$", va="center")
    ax.annotate("", xy=(-0.6, 0.55), xytext=(-0.6, -0.55), arrowprops=arrow(arrowstyle="<->", lw=1))
    ax.text(-0.72, 0.0, "$d$", ha="right", va="center", backgroundcolor=PAPER)
    ax.annotate("", xy=(6, -1.85), xytext=(0, -1.85), arrowprops=arrow(arrowstyle="<->", lw=1))
    ax.text(3, -1.95, "$D$", ha="center", va="top")
    ax.text(0, -1.5, "mask", ha="center", va="top", fontsize=9.5)
    ax.text(6, -1.5, "screen", ha="center", va="top", fontsize=9.5)
    ax.text(-1.0, 1.1, "incident\nbeam", ha="center", fontsize=9.5)
    ax.text(0, 1.6, "$x$", ha="center")
    ax.set(xlim=(-2, 7.2), ylim=(-2.3, 1.8), aspect="equal")
    ax.axis("off")
    save(fig, "slits")


@figure("domains")
def domains():
    fig, axes = plt.subplots(1, 3, figsize=(8, 2.9))
    rho, delta = 0.35, 0.35     # delta exaggerated for legibility; the handout says "not to scale"
    for ax, (title, hole) in zip(axes, [("disk", None), ("concentric annulus", 0.0), ("eccentric annulus", delta)]):
        ax.add_patch(patches.Circle((0, 0), 1, facecolor=matplotlib.colors.to_rgba(BLUE, 0.15), edgecolor=INK, lw=1.5))
        if hole is not None:
            ax.add_patch(patches.Circle((hole, 0), rho, facecolor=PAPER, edgecolor=INK, lw=1.5))
        ax.plot(0, 0, ".", color=INK, ms=4)
        ax.set(xlim=(-1.15, 1.15), ylim=(-1.35, 1.15), aspect="equal")
        ax.set_title(title, fontsize=10.5)
        ax.axis("off")
    axes[0].annotate("", xy=(np.cos(0.8), np.sin(0.8)), xytext=(0, 0), arrowprops=arrow(arrowstyle="->", lw=1))
    axes[0].text(0.25, 0.42, "1", fontsize=10)
    axes[1].annotate("", xy=(-rho, 0), xytext=(0, 0), arrowprops=arrow(arrowstyle="->", lw=1))
    axes[1].text(-rho / 2, 0.06, r"$\rho$", ha="center", fontsize=10)
    axes[1].annotate("", xy=(1, 0), xytext=(rho, 0), arrowprops=arrow(arrowstyle="<->", lw=1))
    axes[1].text((1 + rho) / 2, 0.06, "$w$", ha="center", fontsize=10)
    axes[2].plot(delta, 0, ".", color=INK, ms=4)
    axes[2].annotate("", xy=(delta, -0.55), xytext=(0, -0.55), arrowprops=arrow(arrowstyle="<->", lw=1))
    axes[2].plot([0, 0], [0, -0.6], color=GREY, lw=0.7, ls=":"); axes[2].plot([delta, delta], [0, -0.6], color=GREY, lw=0.7, ls=":")
    axes[2].text(delta / 2, -0.62, r"$\delta$", ha="center", va="top", fontsize=10)
    save(fig, "domains")


@figure("yukawa")
def yukawa():
    g, mu, a = 4.0, 1.0, 0.5
    x = np.linspace(-5, 5, 1000)
    ra = np.sqrt(x**2 + a**2)
    V = -g * np.exp(-mu * ra) / ra
    V0 = V[np.argmin(np.abs(x))]
    fig, ax = plt.subplots(figsize=(6.5, 3.2))
    ax.plot(x, V, color=BLUE, lw=2)
    ax.axhline(0, color=GREY, lw=0.8)
    ax.axhline(V0 / 2, color=GREY, lw=0.8, ls=":")
    ax.text(4.9, V0 / 2 + 0.12, "half depth", ha="right", fontsize=9, color=MUTED)
    ax.annotate("", xy=(0, V0), xytext=(0, 0), arrowprops=arrow(arrowstyle="<->", lw=1.2))
    ax.text(-0.12, V0 * 0.14, "$|V_Y(0)|$", ha="right", fontsize=10)
    ax.annotate("", xy=(1 / mu, 0.35), xytext=(0, 0.35), arrowprops=arrow(arrowstyle="<->", lw=1.2))
    ax.text(1 / mu + 0.12, 0.35, r"$1/\mu$", ha="left", va="center", fontsize=10)
    ax.set(xlabel="$x$", ylabel="$V_Y(x)$", ylim=(-5.4, 1.0))
    save(fig, "yukawa-potential")


@figure("brownian")
def brownian():
    fig, (ax0, ax1) = plt.subplots(1, 2, figsize=(8.5, 3.3), gridspec_kw={"width_ratios": [1, 1.15]})

    # Left: a particle in a bath of much smaller molecules. The path behind it is a schematic
    # random walk, drawn with a fixed seed so the figure never changes.
    rng = np.random.default_rng(11)
    path = np.cumsum(rng.normal(0, 0.07, (160, 2)), axis=0)
    path -= path[-1]                                  # the walk ends at the particle
    ax0.plot(path[:, 0], path[:, 1], color=GREY, lw=0.7, alpha=0.55)
    angles = rng.uniform(0, 2 * np.pi, 60)
    radii = rng.uniform(0.55, 1.25, 60)
    mx, my = radii * np.cos(angles), radii * np.sin(angles)
    clear = ~((my < -0.05) & (mx < -0.3)) & ~((my > -0.15) & (my < 0.15))   # room for the arrows and labels
    ax0.plot(mx[clear], my[clear], "o", color=GREY, ms=3, alpha=0.7)
    for ang in [0.6, 2.2, 3.6, 4.9]:                  # a few molecules hitting it: the kicks
        start = 0.85 * np.array([np.cos(ang), np.sin(ang)])
        end = 0.42 * np.array([np.cos(ang), np.sin(ang)])
        ax0.plot(*start, "o", color=GREEN, ms=4)
        ax0.annotate("", xy=end, xytext=start, arrowprops=arrow(arrowstyle="->", lw=1.3, color=GREEN))
    ax0.add_patch(patches.Circle((0, 0), 0.32, facecolor=BLUE, edgecolor=INK, lw=1, zorder=3))
    ax0.annotate("", xy=(1.15, -0.02), xytext=(0.34, -0.02), arrowprops=arrow(arrowstyle="->", lw=1.8), zorder=4)
    ax0.text(1.2, -0.02, "$v$", va="center", fontsize=11)
    ax0.annotate("", xy=(-0.85, -0.02), xytext=(-0.34, -0.02),
                 arrowprops=arrow(arrowstyle="->", lw=1.8, color=ORANGE), zorder=4)
    ax0.text(-0.88, 0.1, r"friction $-\gamma v$", ha="right", va="bottom", fontsize=9.5, color=ORANGE)
    ax0.text(0.75, 1.05, "random kicks", fontsize=9.5, color=GREEN)
    ax0.set(xlim=(-1.9, 1.7), ylim=(-1.4, 1.3), aspect="equal")
    ax0.set_title("a particle in a heat bath at temperature $T$", fontsize=10.5)
    ax0.axis("off")

    # Right: the same particle in the harmonic trap of Part 4.
    x = np.linspace(-2.4, 2.4, 300)
    ax1.plot(x, 0.5 * x**2, color=BLUE, lw=2)
    ax1.plot([-2.5, 2.5], [0, 0], color=GREY, lw=0.8)
    xp = 1.5
    ax1.add_patch(patches.Circle((xp, 0.5 * xp**2 + 0.17), 0.17, facecolor=BLUE, edgecolor=INK, lw=1, zorder=3))
    ax1.annotate("", xy=(xp - 0.9, 0.5 * xp**2 + 0.17), xytext=(xp - 0.2, 0.5 * xp**2 + 0.17),
                 arrowprops=arrow(arrowstyle="->", lw=1.8, color=ORANGE))
    ax1.text(xp - 0.95, 0.5 * xp**2 + 0.3, r"$F = -\kappa x$", ha="right", va="bottom", fontsize=10, color=ORANGE)
    ax1.text(2.0, 2.45, r"$U(x) = \kappa x^2/2$", ha="right", fontsize=10, color=BLUE)
    ax1.annotate("", xy=(2.6, 0), xytext=(-2.6, 0), arrowprops=arrow(arrowstyle="->", lw=0.8, color=GREY))
    ax1.text(2.65, 0, "$x$", va="center", fontsize=10)
    ax1.set(xlim=(-2.7, 2.9), ylim=(-0.3, 3.1))
    ax1.set_title("the same particle in a trap (Part 4)", fontsize=10.5)
    ax1.axis("off")
    fig.tight_layout()
    save(fig, "brownian")


def main(names):
    global SUFFIX
    for theme in THEMES.values():
        globals().update(theme["colours"])
        SUFFIX = theme["suffix"]
        with plt.rc_context(theme["rc"]):
            for name in names or FIGURES:
                FIGURES[name]()


if __name__ == "__main__":
    main(sys.argv[1:])
