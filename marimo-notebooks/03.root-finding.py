import marimo

app = marimo.App(width="medium")

with app.setup:
    import marimo as mo
    import numpy as np
    import matplotlib.pyplot as plt
    from tn23015 import check_answers, given, load_data, md, print, row, show, slider


@app.cell(hide_code=True)
def head_5_01():
    mo.md(
        r"""
        ## Exercise 3.1

        Planck's radiation law tells us that the intensity of radiation per unit area and per unit wavelength $\lambda$
        from a black body at temperature $T$ is 

        $$
          I(\lambda) = {2\pi hc^2\lambda^{-5}\over\text{e}^{hc/\lambda k_BT}-1}\,,
        $$

        where $h$ is Planck's constant, $c$ is the speed of light, and $k_B$ is Boltzmann's constant.
        The wavelength $\lambda$ at which the emitted radiation is strongest is the solution of the equation 

        $$
        5 \text{e}^{-hc/\lambda k_BT} + {hc\over\lambda k_BT} - 5 = 0.
        $$

        With the substitution $x=hc/\lambda k_BT$ we find that

        $$
        5 \text{e}^{-x} + x - 5 = 0.
        $$

        From which we find the Wien displacement law

        $$
        \lambda = {b\over T} \, ,
        $$

        where the so-called Wien displacement constant is $b=hc/k_Bx$, and $x$ is the solution to the nonlinear equation.

        Write a program to solve this equation for  $x$ to an accuracy of $\epsilon=10^{-6}$ using the bisection/binary search method.
        Print the values $a$, $b$, the estimate of the root, and the error during the while loop iterations.
        Calculate and print the value for the found displacement constant. 
        Follow the steps below when making this exercise.
        * Make a plot of the function in to get a rough idea what the interval the interval is in which the root is located.
        * Write a Python function for the equation for which you want to find the root
        * Test that your function definition gives the correct function value
        * Chose your interval $[a, b]$ such that the root is inside and that the obvious solution $x$=0 is not included. Make a check in your code that there is actually a root in the interval using an ```if``` statement or otherwise give a warning.
        * Implement the bisection method to find the root
        * Print the values of $a$, $b$, $xsol$, and the error to the command line at every iteration

        Save your final solution as variable `xsol` is is plotted in the same graph.
        This exercise is from the book Computational Physics of Newman.
        """
    )


@app.cell
def ex_5_01():
    # Fill these in as you work through the exercise.
    _ax = xsol = None

    # define accuracy
    eps=1e-6

    # define function
    def f(x):
        return None

    # first make a quick plot of the function over the domain of x
    x=np.linspace(-1,10,100)

    # xsol = ...

    # Do not edit or remove the boiler-plate code below.
    if given(xsol, f):
        _fig, _ax = plt.subplots()
        _ax.set_xlabel('x'), _ax.set_ylabel('f(x)')
        _ax.plot(x,f(x), '-b')
        _ax.grid()

        _ax.plot(xsol,f(xsol), 'or')

    show(_ax, xsol=xsol, f=f)


@app.cell(hide_code=True)
def check_5_01():
    check_answers(xsol=xsol, key="answer_5_01")


@app.cell(hide_code=True)
def sol_5_01():
    # define accuracy
    eps_sol1=1e-6

    # define function
    def f_sol1(x):
        return 5*np.exp(-x)+x-5

    # first make a quick plot of the function over the domain of x
    x_sol1=np.linspace(-1,10,100)
    _fig, _ax = plt.subplots()
    _ax.set_xlabel('x'), _ax.set_ylabel('f(x)')
    _ax.plot(x_sol1,f_sol1(x_sol1), '-b')
    _ax.grid()

    # initial estimate
    a_sol1=2
    b_sol1=8

    if f_sol1(a_sol1)*f_sol1(b_sol1)>0:
        print('The function does not have a root in the given interval')
    else:
        print('The function has a root in the given interval, continuing...')
        error_sol1=1
        while error_sol1>eps_sol1:
            xsol_sol1=0.5*(a_sol1+b_sol1)
            if f_sol1(a_sol1)*f_sol1(xsol_sol1)<0:
                b_sol1=xsol_sol1
            else:
                a_sol1=xsol_sol1
            error_sol1=0.5*np.abs(a_sol1-b_sol1)
            print('{:.2e}|{:.2e}|{:.2e}|{:.2e}'.format(a_sol1, b_sol1, xsol_sol1, error_sol1))
    xsol_sol1=(a_sol1+b_sol1)/2
    _ax.plot(xsol_sol1,f_sol1(xsol_sol1), 'or')

    xsol_sol1 = np.copy(xsol_sol1)

    show(_ax)


@app.cell(hide_code=True)
def head_5_02():
    mo.md(
        r"""
        ## Exercise 3.2

        The wavelength peak in the Sun's emitted radiation occurs at $\lambda=502$ nm.
        Derive from the equations above, your value of $x$, and the wavelength $\lambda$ an estimate of the surface temperature of the Sun and store it in variable `tempsun`.
        """
    )


@app.cell
def ex_5_02():
    # Fill these in as you work through the exercise.
    tempsun = None

    h=6.6e-34
    c=3e8
    kb=1.38e-23

    # tempsun = ...

    # Do not edit or remove the boiler-plate code below.
    show(tempsun=tempsun)


@app.cell(hide_code=True)
def check_5_02():
    check_answers(tempsun=tempsun, key="answer_5_02")


@app.cell(hide_code=True)
def sol_5_02():
    h_sol2=6.6e-34
    c_sol2=3e8
    kb_sol2=1.38e-23
    b_sol2=h_sol2*c_sol2/kb_sol2/xsol_sol1
    print('The displacement constant is {}'.format(b_sol2))

    wavelength_sol2=502e-9
    tempsun_sol2=b_sol2/wavelength_sol2
    print('The temperature is {} Kelvin'.format(tempsun_sol2))
    tempsun_sol2 = np.copy(tempsun_sol2)

    show()


@app.cell(hide_code=True)
def head_5_03():
    mo.md(
        r"""
        ## Exercise 3.3

        Consider the sixth-order polynomial

        $$
        P(x) = 924 x^6 - 2772 x^5 + 3150 x^4 - 1680 x^3 + 420 x^2 - 42 x + 1.
        $$

        There is no general formula for the roots of a sixth-order polynomial, but one can find them easily enough using a computer. 

        Make a function $P(x)$ and plot it from $x=0$ to $x=1$. Inspect the plot and find rough values for the six roots of the polynomial, the points at which the function is zero.
        Put the initial estimates of the roots in an array.

        Write a Python program to solve for the positions of all six roots using Newton's method.
        Calculate your roots to an absolute error that is below $10^{-10}$. Use the absolute difference between successive values as your error. 

        Follow the steps below when making this exercise.

        1. Solve this problem for a single root
        2. Subsequently add a for loop to find all roots and put every root in an array `sol6`.
        """
    )


@app.cell
def ex_5_03():
    # define polynomial
    def P(x):
        return 924*x**6 - 2772*x**5 +3150*x**4 - 1680*x**3 + 420*x**2 - 42*x + 1

    # define derivative
    def Pprime(x):
        return 5544*x**5 - 13860*x**4 + 12600*x**3 - 5040*x**2 + 840*x**1 - 42

    # first make a quick plot

    x_2=np.linspace(0,1,100)
    _fig, _ax = plt.subplots()
    _ax.plot(x_2,P(x_2), '-b')
    _ax.set_xlabel('x'), _ax.set_ylabel('f(x)')
    _ax.grid()

    polyorder=6

    # Fill this in as you work through the exercise.
    sol6 = None

    # Set `unfinished` to False once you have written the code below, so that it can run.
    unfinished = True

    if not unfinished:

        # Make a blank array to store your results
        sol6=np.zeros(polyorder)

        # sol6 = ...

        _ax.plot(sol6,P(sol6), 'or')

    # Do not edit or remove the boiler-plate code below.
    show(_ax)


@app.cell(hide_code=True)
def check_5_03():
    check_answers(sol6=sol6, key="answer_5_03")


@app.cell(hide_code=True)
def sol_5_03():
    # define polynomial
    def P_sol3(x):
        return 924*x**6 - 2772*x**5 +3150*x**4 - 1680*x**3 + 420*x**2 - 42*x + 1

    # define derivative
    def Pprime_sol3(x):
        return 5544*x**5 - 13860*x**4 + 12600*x**3 - 5040*x**2 + 840*x**1 - 42

    # first make a quick plot

    x_sol3=np.linspace(0,1,100)
    _fig, _ax = plt.subplots()
    _ax.plot(x_sol3,P_sol3(x_sol3), '-b')
    _ax.set_xlabel('x'), _ax.set_ylabel('f(x)')
    _ax.grid()

    polyorder_sol3=6

    # Make a blank array to store your results
    sol6_sol3=np.zeros(polyorder_sol3)

    # put estimates in array
    start_sol3=np.array([0, 0.2, 0.4, 0.6, 0.8, 1])

    eps_sol3=1e-10

    print('root|error')

    cnt_sol3=0
    for _xini in start_sol3:
        error_sol3=10
        x_1_sol3=_xini
        while error_sol3>eps_sol3:
            x_2_sol3=x_1_sol3 - (P_sol3(x_1_sol3)/Pprime_sol3(x_1_sol3))
            error_sol3=np.abs(x_2_sol3-x_1_sol3)
            x_1_sol3=x_2_sol3

        print('{:.2e}|{:.2e}'.format(x_2_sol3, error_sol3))
        sol6_sol3[cnt_sol3]=x_2_sol3
        cnt_sol3+=1   
    _ax.plot(sol6_sol3,P_sol3(sol6_sol3), 'or')

    sol6_sol3 = np.copy(sol6_sol3)

    show(_ax)


@app.cell(hide_code=True)
def head_5_04():
    mo.md(
        r"""
        ## Exercise 3.4

        There is a magical point between the Earth and the Moon, called the $L_1$ Lagrange point, at which a satellite will orbit the Earth in perfect synchrony with the Moon, staying always in between the two.
        This works because the inward pull of the Earth and the outward pull of the Moon combine to create exactly the needed centripetal force that keeps the satellite in its orbit. 

        Assuming circular orbits, and assuming that the Earth is much more massive than either the Moon or the satellite the distance $r$ from the center of the Earth to the $L_1$ point satisfies 

        $$
        {GM\over r^2} - {Gm\over(R-r)^2} = \omega^2 r,
        $$

        where $M$ and $m$ are the Earth and Moon masses, $G$ is Newton's gravitational constant, and $\omega$ is the angular velocity of both the Moon and the satellite.

        The equation above is a fifth-order polynomial equation in $r$ (also called a quintic equation).
        Such equations cannot be solved in closed form (i.e. as an equation), but it's straightforward to solve them numerically.
        Write a program that uses Newton's method to solve for the distance $r$ from the Earth to the $L_1$ point.
        Compute a solution accurate to at least four significant figures.

        The values of the various parameters are:

        $$
        \begin{aligned}
        G &= 6.674\times10^{-11}\,\mathrm{m}^3\mathrm{kg}^{-1}\mathrm{s}^{-2}, \\
        M &= 5.974\times10^{24}\,\mathrm{kg}, \\
        m &= 7.348\times10^{22}\,\mathrm{kg}, \\
        R &= 3.844\times10^8\,\mathrm{m}, \\
        \omega &= 2.662\times10^{-6}\,\mathrm{s}^{-1}.
        \end{aligned}
        $$

        You will also need to choose a suitable starting value for $r$.

        Some tips for making this exercise
        * Make a plot of the function and its derivative
        * First check the values of the function and its derivative at the point where you start your search, can you see what the problem is with a straightforward implementation of the given the physical parameters?
        * Implement Newton's method to a modified version of the equation above and find the solution _Hint: write it as standard polynomial in r_

        Store your final solution for $r$ in variable `lagrange`.
        """
    )


@app.cell
def ex_5_04():
    # Fill these in as you work through the exercise.
    lagrange = None

    G=6.674e-11
    M=5.974e24
    m=7.348e22
    R=3.844e8
    omega=2.662e-6

    # lagrange = ...

    # Do not edit or remove the boiler-plate code below.
    show(lagrange=lagrange)


@app.cell(hide_code=True)
def check_5_04():
    check_answers(lagrange=lagrange, key="answer_5_04")


@app.cell(hide_code=True)
def sol_5_04():
    G_sol4=6.674e-11
    M_sol4=5.974e24
    m_sol4=7.348e22
    R_sol4=3.844e8
    omega_sol4=2.662e-6

    # The naive approach is defining the functions directly
    #def f(r):
    #    return G*M*r**(-2) - G*m*(R-r)**(-2) - r*omega**2

    #def fprime(r):
    #    return -2*G*M*r**(-3) + 2*G*m*(2*r-2*R)*(R-r)**(-3)-omega**2
    # The problem with this approach is that the derivative is small. Hence the convergence to the correct x 
    # is extremely slow
    # the solution is to write is a standard polynomial in r

    def f_sol4(r):
        return -omega_sol4**2*r**5 + 2*omega_sol4**2*R_sol4*r**4 - omega_sol4**2*R_sol4**2*r**3 + G_sol4*r**2*(M_sol4-m_sol4) - 2*r*R_sol4*G_sol4*M_sol4 +G_sol4*M_sol4*R_sol4**2

    def fprime_sol4(r):
        return -5*omega_sol4**2*r**4 + 8*omega_sol4**2*R_sol4*r**3 - 3*omega_sol4**2*R_sol4**2*r**2 + 2*G_sol4*r*(M_sol4-m_sol4) - 2*R_sol4*G_sol4*M_sol4

    r_sol4=np.linspace(0.3*R_sol4,0.99*R_sol4,100)

    # first make a quick plot
    _fig, _axs = plt.subplots(1, 2)
    _ax = _axs[0]
    _ax.plot(r_sol4,f_sol4(r_sol4), '-b')
    _ax.set_xlabel('r'), _ax.set_ylabel('f(r)')
    _ax.grid()

    _ax = _axs[1]
    _ax.plot(r_sol4,fprime_sol4(r_sol4), '-b')
    _ax.set_xlabel('r'), _ax.set_ylabel('df/dr')
    _ax.grid()

    eps_sol4=1e-4

    print('root|error|function val')

    error_sol4=10*eps_sol4
    x_1_sol4=3.2e8
    while error_sol4>eps_sol4:
        x_2_sol4=x_1_sol4 - (f_sol4(x_1_sol4)/fprime_sol4(x_1_sol4))
        error_sol4=np.abs(x_2_sol4-x_1_sol4)
        x_1_sol4=x_2_sol4
        print('{:.4e}|{:.4e}|{:.4e}'.format(x_2_sol4, error_sol4, f_sol4(x_2_sol4)))

    lagrange_sol4=x_2_sol4
    lagrange_sol4 = np.copy(lagrange_sol4)

    show(_fig)


if __name__ == "__main__":
    app.run()
