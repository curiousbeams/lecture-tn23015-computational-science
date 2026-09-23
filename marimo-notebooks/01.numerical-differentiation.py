import marimo

app = marimo.App(width="medium")

with app.setup:
    import marimo as mo
    import numpy as np
    import matplotlib.pyplot as plt
    from tn23015 import check_answers, given, load_data, md, print, row, show, slider


@app.cell(hide_code=True)
def head_3_01():
    mo.md(
        r"""
        ## Exercise 1.1

        Calculate the derivative of this function analytically (ie. with a pen and paper). Program the two results into two python functions.
        Create variable arrays `y` and `y_prime` with the value $y = f(x)$ and $y' = f'(x)$ respectively, with x in the range $-2 \leq x \leq 2$ and 100 points.
        Make plots of $f(x)$ and its derivative $f'(x)$.
        """
    )


@app.cell
def ex_3_01():
    # Fill these in as you work through the exercise.
    _ax = x = y = y_prime = None

    def f(x):
        return None

    def fp(x):
        return None

    # x = ....
    # y = ....
    # y_prime = ....

    # Now the plot (with labels and legend of course!)
    # _fig, _ax = plt.subplots()
    # ...

    # Do not edit or remove the boiler-plate code below.
    show(_ax, x=x, y=y, y_prime=y_prime, f=f, fp=fp)


@app.cell(hide_code=True)
def check_3_01():
    check_answers(x=x, y=y, y_prime=y_prime, key="answer_3_01")


@app.cell(hide_code=True)
def sol_3_01():
    def f_sol1(x):
        return 1+0.5*np.tanh(2*x)
    def fp_sol1(x):
        return 1/np.cosh(2*x)**2

    x_sol1 = np.linspace(-2,2,100)
    y_sol1 = f_sol1(x_sol1)
    y_prime_sol1 = fp_sol1(x_sol1)

    _fig, _ax = plt.subplots()
    _ax.plot(x_sol1, f_sol1(x_sol1), label='f(x)')
    _ax.plot(x_sol1, fp_sol1(x_sol1), label="f'(x)")
    _ax.legend()
    _ax.set_ylabel("f(x), f'(x)")
    _ax.set_xlabel("x")

    x_sol1 = np.copy(x_sol1)
    y_sol1 = np.copy(y_sol1)
    y_prime_sol1 = np.copy(y_prime_sol1)

    show(_ax)


@app.cell(hide_code=True)
def head_3_02():
    mo.md(
        r"""
        ## Exercise 1.2

        Now, we will write a function to calculate the derivative numerically with a given step size $h$ and compare our numerically calculated derivative with that of the analytical answer.

        Write two functions that calculates the derivative of a function numerically, one using the forward difference method, and once using the central difference method.

        Use these functions calculate $f'(x)$ at $x=1$ for $h=0.5$, and compare your numerically calculated derivatives to the correct answer from the analytical formula.
        """
    )


@app.cell
def ex_3_02():
    # Fill these in as you work through the exercise.
    error_center = error_forward = yd_analytical = yd_center = yd_forward = None

    def diff_forward(f,x,h):
        return None

    def diff_center(f,x,h):
        return None

    x0=1
    h=0.5

    # yd_analytical = 
    # yd_forward = 
    # yd_center = 
    # error_forward = 
    # error_center = 

    # Do not edit or remove the boiler-plate code below.
    if given(
        error_center,
        error_forward,
        yd_analytical,
        yd_center,
        yd_forward,
        diff_forward,
        diff_center,
    ):
        print("Forward:    %f   Error: %f" % (yd_forward, error_forward))
        print("Central:    %f   Error: %f" % (yd_center, error_center))
        print("Analytical: %f" % yd_analytical)

    show(
        error_center=error_center,
        error_forward=error_forward,
        yd_analytical=yd_analytical,
        yd_center=yd_center,
        yd_forward=yd_forward,
        diff_forward=diff_forward,
        diff_center=diff_center,
    )


@app.cell(hide_code=True)
def check_3_02():
    check_answers(
        forward=(yd_forward, error_forward),
        center=(yd_center, error_center),
        yd_analytical=yd_analytical,
        key="answer_3_02",
    )


@app.cell(hide_code=True)
def sol_3_02():
    def diff_forward_sol2(f,x,h):
        return (f(x+h)-f(x))/h
    def diff_center_sol2(f,x,h):
        return (f(x+h/2)-f(x-h/2))/h

    x0_sol2=1
    h_sol2=0.5

    yd_analytical_sol2 = fp_sol1(x0_sol2)
    yd_forward_sol2 = diff_forward_sol2(f_sol1,x0_sol2,h_sol2)
    yd_center_sol2 = diff_center_sol2(f_sol1,x0_sol2,h_sol2)

    error_forward_sol2 = yd_forward_sol2 - yd_analytical_sol2
    error_center_sol2 = yd_center_sol2 - yd_analytical_sol2
    print("Forward:    %f   Error: %f" % (yd_forward_sol2, error_forward_sol2))
    print("Central:    %f   Error: %f" % (yd_center_sol2, error_center_sol2))
    print("Analytical: %f" % yd_analytical_sol2)

    yd_analytical_sol2 = yd_analytical_sol2

    show()


@app.cell(hide_code=True)
def head_3_03():
    mo.md(
        r"""
        ## Exercise 1.3

        Repeat the calculation of Exercise 1.2 but now at $x=0$.
        """
    )


@app.cell
def ex_3_03():
    # Fill these in as you work through the exercise.
    error_center_2 = error_forward_2 = yd_analytical_2 = yd_center_2 = yd_forward_2 = None

    # yd_analytical_2 = 
    # yd_forward_2 = 
    # yd_center_2 = 
    # error_forward_2 = 
    # error_center_2 = 

    # Do not edit or remove the boiler-plate code below.
    if given(error_center_2, error_forward_2, yd_analytical_2, yd_center_2, yd_forward_2):
        print("Forward:    %f   Error: %f" % (yd_forward_2, error_forward_2))
        print("Central:    %f   Error: %f" % (yd_center_2, error_center_2))
        print("Analytical: %f" % yd_analytical_2)

    show(
        error_center=error_center_2,
        error_forward=error_forward_2,
        yd_analytical=yd_analytical_2,
        yd_center=yd_center_2,
        yd_forward=yd_forward_2,
    )


@app.cell(hide_code=True)
def check_3_03():
    check_answers(
        forward=(yd_forward_2, error_forward_2),
        center=(yd_center_2, error_center_2),
        yd_analytical_2=yd_analytical_2,
        key="answer_3_03",
    )


@app.cell(hide_code=True)
def sol_3_03():
    x0_sol3=0
    h_sol3=0.5

    yd_analytical_sol3 = fp_sol1(x0_sol3)
    yd_forward_sol3 = diff_forward_sol2(f_sol1,x0_sol3,h_sol3)
    yd_center_sol3 = diff_center_sol2(f_sol1,x0_sol3,h_sol3)

    error_forward_sol3 = yd_forward_sol3 - yd_analytical_sol3
    error_center_sol3 = yd_center_sol3 - yd_analytical_sol3
    print("Forward:    %f   Error: %f" % (yd_forward_sol3, error_forward_sol3))
    print("Central:    %f   Error: %f" % (yd_center_sol3, error_center_sol3))
    print("Analytical: %f" % yd_analytical_sol3)

    yd_analytical_sol3 = yd_analytical_sol3

    show()


@app.cell(hide_code=True)
def head_3_04():
    mo.md(
        r"""
        ## Exercise 1.4

        Calculate the derivative of the function for a $x$ ranging from $-2 \leq x \leq 2$ with 100 points using the forward and the central difference methods with $h = 0.5$. 

        You can make use of the functions you defined above.

        Make a plot of the forward difference derivative and the central difference derivative vs. x, along with the analytical solution.
        """
    )


@app.cell
def ex_3_04():
    # Fill these in as you work through the exercise.
    _ax = x_2 = yd_analytical_3 = yd_center_3 = yd_forward_3 = None

    # The spacing
    h_2=0.5

    # Our array of points at which to perform the calculations
    # x_2=np.linspace(__,__,__)

    # The derivatives
    # yd_center_3 = ___
    # yd_forward_3 = ___
    # yd_analytical_3 = ____

    # The plot
    # _fig, _ax = plt.subplots()
    # ...

    # Do not edit or remove the boiler-plate code below.
    show(_ax, x=x_2, yd_analytical=yd_analytical_3, yd_center=yd_center_3, yd_forward=yd_forward_3)


@app.cell(hide_code=True)
def check_3_04():
    check_answers(
        x_2=x_2,
        yd_center_3=yd_center_3,
        yd_forward_3=yd_forward_3,
        yd_analytical_3=yd_analytical_3,
        key="answer_3_04",
    )


@app.cell(hide_code=True)
def sol_3_04():
    # The spacing
    h_sol4=0.5

    # Our array of points at which to perform the calculations
    x_sol4=np.linspace(-2,2,100)

    # The derivatives
    yd_center_sol4 = diff_center_sol2(f_sol1,x_sol4,h_sol4)
    yd_forward_sol4 = diff_forward_sol2(f_sol1,x_sol4,h_sol4)
    yd_analytical_sol4 = fp_sol1(x_sol4)

    # The plot
    _fig, _ax = plt.subplots()
    _ax.plot(x_sol4,yd_center_sol4, label='Center')
    _ax.plot(x_sol4,yd_forward_sol4, label='Forward')
    _ax.plot(x_sol4,yd_analytical_sol4, label='Analytical')
    _ax.set_ylabel("Numerical Derivative")
    _ax.set_xlabel("x")
    _ax.legend()

    x_sol4 = np.copy(x_sol4)
    yd_center_sol4 = np.copy(yd_center_sol4)
    yd_forward_sol4 = np.copy(yd_forward_sol4)
    yd_analytical_sol4 = np.copy(yd_analytical_sol4)

    show(_ax)


@app.cell(hide_code=True)
def head_3_05():
    mo.md(
        r"""
        ## Exercise 1.5

        Here, you will make a plot of the error of the forward difference derivative, and also a plot of the function f(x), in two plots beside each other.
        The idea is to try to understand the value of the error (is it large, is it small, is it positive, is it negative) base on the shape of the function.

        Your x-range should extend from -2 to 2 with 100 points. 

        To make two plots beside each other, you will use the matplotlib subplot capabilities:

        Start your subplot using the command `fig, ax = plt.subplots(figsize=(10,4))`.
        To make your left hand plot, run the command `ax = axs[0]` then use the usual plot commands to make your plot. 
        To make a plot in the right hand plot, then use the command `ax = axs[1]` and then add the commands to make the plot in second plot.

        Your left plot should plot the error, defined as the difference between the derivative calculated by the finite difference method, and the analytical answer:

        $$
        \mathrm{error} = 
        \left (\frac{df}{dx} \right)_{\mathrm{fwd}} - 
        \left ( \frac{df}{dx} \right)_{\mathrm{analytical}}
        $$

        In this plot of the error, make a vertical line at $x=0$ using the  `_ax.axvline()` command, and a horizontal line at $y=0$ using the `_ax.axhline()` command. 

        In the right plot, plot the function $f(x)$ as a function of $x$. For this plot, add a vertical line at $x=0$.
        """
    )


@app.cell
def ex_3_05():
    # Fill this in as you work through the exercise.
    _fig = None

    # _fig, _axs = plt.subplots(1, 2, figsize=(12,4))
    # _ax = _axs[0]

    # _ax.plot(....)
    # ....

    # _ax.axvline(0, ls=":", color="grey")
    # _ax.axhline(0, ls=":", color="grey")

    # _ax = _axs[1]
    # _ax.plot(....)
    # ....

    #_ax.axvline(0, ls=":", color="grey")

    # Do not edit or remove the boiler-plate code below.
    show(_fig)


@app.cell(hide_code=True)
def sol_3_05():
    _fig, _axs = plt.subplots(1, 2, figsize=(12,4))
    _ax = _axs[0]

    _ax.plot(x_sol4, yd_forward_sol4-yd_analytical_sol4)
    _ax.set_ylabel("Fwd Derivative Error")
    _ax.set_xlabel("x")
    _ax.axvline(0, ls=":", color="grey")
    _ax.axhline(0, ls=":", color="grey")

    _ax = _axs[1]
    _ax.plot(x_sol4, f_sol1(x_sol4), label='f(x)')
    _ax.set_ylabel("f(x)")
    _ax.set_xlabel("x")
    _ax.axvline(0, ls=":", color="grey")

    show(_fig)


@app.cell(hide_code=True)
def head_3_06():
    mo.md(
        r"""
        ## Exercise 1.6

        Write a loop that calculates the numerical derivative $f'(x)$ at $x=1$, using the forward, center, and backwards difference formulats.
        In your loop, perform your calculation for 100 different values of $h$ spaced evenly spaced on log scale from $h = 1\times10^{-6}$ to $h = 1$.
        For this, you can use the [`geomspace`](https://numpy.org/doc/stable/reference/generated/numpy.geomspace.html) function.

        You can also use [`logspace`](https://numpy.org/doc/stable/reference/generated/numpy.logspace.html) if you want, but it is a bit tricker since using the `logspace` function, you can't specify the endpoints . 

        Make a log-log plot of the error $\epsilon$ vs $h$ for the three techniques (three lines on the same graph), with $\epsilon$ defined as:

        $$
        \epsilon = |f'_{calc}(1) - f'(1)|
        $$

        where $f'_{calc}$ is the numerically calculated derivative and $f'$ is the analytical answer.
        """
    )


@app.cell
def ex_3_06():
    # Fill these in as you work through the exercise.
    _ax = err_backward = err_center = err_forward = h_3 = None

    N = 100

    # Code to define any functions you need, calculate the derivatives
    # for 100 values of h, and make a plot with axis labels.
    # h_3 = ...

    # Your code should produce three numpy arrays:
    # err_forward, err_center, err_backward, along with the array h
    # of points spaced equally on a logarithmic axis

    def diff_backward(f,x,h):
        return None

    # err_forward = ...
    # err_center = ...
    # err_backward = ...

    # It's handy on this plot to have a grid
    # _fig, _ax = plt.subplots()
    # _ax.grid()

    # Do not edit or remove the boiler-plate code below.
    show(
        _ax,
        err_backward=err_backward,
        err_center=err_center,
        err_forward=err_forward,
        h=h_3,
        diff_backward=diff_backward,
    )


@app.cell(hide_code=True)
def check_3_06():
    check_answers(
        h_3=h_3,
        err_forward=err_forward,
        err_center=err_center,
        err_backward=err_backward,
        key="answer_3_06",
    )


@app.cell(hide_code=True)
def sol_3_06():
    N_sol6 = 100
    h_sol6 = np.geomspace(1e-6,1,N_sol6)

    def diff_backward_sol6(f,x,h):
        return (f(x)-f(x-h))/h

    fp_forward_sol6 = np.zeros(N_sol6)
    fp_center_sol6 = np.zeros(N_sol6)
    fp_backward_sol6 = np.zeros(N_sol6)

    for _i in range(N_sol6):
        fp_forward_sol6[_i] = diff_forward_sol2(f_sol1,1,h_sol6[_i])
        fp_center_sol6[_i] = diff_center_sol2(f_sol1,1,h_sol6[_i])
        fp_backward_sol6[_i] = diff_backward_sol6(f_sol1,1,h_sol6[_i])

    err_forward_sol6 = np.abs(fp_forward_sol6 - fp_sol1(1))
    err_center_sol6 = np.abs(fp_center_sol6 - fp_sol1(1))
    err_backward_sol6 = np.abs(fp_backward_sol6 - fp_sol1(1))

    _fig, _ax = plt.subplots()
    _ax.grid()

    _ax.loglog(h_sol6, err_forward_sol6,'.', label="Forward")
    _ax.loglog(h_sol6, err_center_sol6,'.', label="Center")
    _ax.loglog(h_sol6, err_backward_sol6, '.', label="Backward")
    _ax.legend()
    _ax.set_ylabel("Error $\epsilon$")
    _ax.set_xlabel("Step size $h$")

    h_sol6 = h_sol6.copy()
    err_forward_sol6 = err_forward_sol6.copy()
    err_center_sol6 = err_center_sol6.copy()
    err_backward_sol6 = err_backward_sol6.copy()

    show(_ax)


@app.cell(hide_code=True)
def head_3_07():
    mo.md(
        r"""
        ## Exercise 1.7

        Plot the data of a sparsly sampled sinusoid with 25 points between $t = 0$ and $t = 4 \pi$.
        """
    )


@app.cell
def ex_3_07():
    # Fill these in as you work through the exercise.
    data = t = None

    N_2=25
    # t = np.linspace(____)
    # data = ____

    # Do not edit or remove the boiler-plate code below.
    show(data=data, t=t)


@app.cell(hide_code=True)
def check_3_07():
    check_answers(t=t, data=data, key="answer_3_07")


@app.cell(hide_code=True)
def sol_3_07():
    N_sol7=25
    t_sol7 = np.linspace(0,4*np.pi,N_sol7)
    data_sol7 = np.sin(t_sol7)

    _fig, _ax = plt.subplots()
    _ax.plot(t_sol7,data_sol7, '-o')
    _ax.axhline(0,c='grey', ls=':')
    _ax.set_xlabel('t')
    _ax.set_ylabel('f(t)')

    t_sol7 = np.copy(t_sol7)
    data_sol7 = np.copy(data_sol7)

    show(_ax)


@app.cell(hide_code=True)
def head_3_08():
    mo.md(
        r"""
        ## Exercise 1.8

        Calculate and plot forward derivative of the numerical data, along with the correct value from the analytical derivative of a sine function.
        """
    )


@app.cell
def ex_3_08():
    # Fill these in as you work through the exercise.
    analytical_derv = fwd_derv = t_fwd = None

    # fwd_derv = np.zeros(_____)

    # for i in range(_____):
    #     .....

    # We also need to adjust the t vector (do you remember why and how?)   
    # t_fwd = ....

    # analytical_derv = _____

    # Do not edit or remove the boiler-plate code below.
    _ax = None
    if given(analytical_derv, fwd_derv, t_fwd, t):

        # And now a nice plot (for free this time)
        _fig, _ax = plt.subplots()
        _ax.plot(t, analytical_derv, '-o', label = "$\cos(x)$")
        _ax.plot(t_fwd, fwd_derv, '-o', label = "Fwd")
        _ax.legend()
        _ax.set_xlabel('t')
        _ax.set_ylabel("f'(t)")
        _ax.axhline(0,c='grey', ls=':')

    show(_ax, analytical_derv=analytical_derv, fwd_derv=fwd_derv, t_fwd=t_fwd, t=t)


@app.cell(hide_code=True)
def check_3_08():
    check_answers(fwd_derv=fwd_derv, t_fwd=t_fwd, analytical_derv=analytical_derv, key="answer_3_08")


@app.cell(hide_code=True)
def sol_3_08():
    fwd_derv_sol8 = np.zeros(N_sol7-1)

    for _i in range(0,N_sol7-1):
        fwd_derv_sol8[_i] = (data_sol7[_i+1]-data_sol7[_i]) / (t_sol7[_i+1]-t_sol7[_i])

    t_fwd_sol8 = t_sol7[0:N_sol7-1]
    analytical_derv_sol8 = np.cos(t_sol7)

    _fig, _ax = plt.subplots()
    _ax.plot(t_sol7, analytical_derv_sol8, '-o', label = "$\cos(x)$")
    _ax.plot(t_fwd_sol8, fwd_derv_sol8, '-o', label = "Fwd")
    _ax.legend()
    _ax.set_xlabel('t')
    _ax.set_ylabel("f'(t)")
    _ax.axhline(0,c='grey', ls=':')

    fwd_derv_sol8 = np.copy(fwd_derv_sol8)
    t_fwd_sol8 = np.copy(t_fwd_sol8)
    analytical_derv_sol8 = np.copy(analytical_derv_sol8)

    show(_ax)


@app.cell(hide_code=True)
def head_3_09():
    mo.md(
        r"""
        ## Exercise 1.9

        Although the derivative seems on first inspection quite inaccurate, there is actually a small fix that can change this.
        In particular, although the forward derivative calculates the derivative at the sampled time steps relatively inaccurately, it does do a pretty good job at calculating the derivative at times halfway *between* the sampled time points. 

        Write code below so that you calculate the center difference derivative at points halfway between the sampling points.
        Hint: you don't have to do much work!
        But you will need a new time array.

        Calculate the analytical answer $\cos(x)$ for the derivative at these same timesteps, and make a plot showing the two.
        """
    )


@app.cell
def ex_3_09():
    # Fill these in as you work through the exercise.
    analytical_derv_new = t_new = None

    # t_new = ...
    # analytical_derv_new = ...

    # Do not edit or remove the boiler-plate code below.
    _ax = None
    if given(analytical_derv_new, t_new, fwd_derv):

        # now make the plot
        _fig, _ax = plt.subplots()
        _ax.plot(t_new, fwd_derv, '-o', label='Fwd Shifted')
        _ax.plot(t_new, analytical_derv_new, '-o', label='Analytical')
        _ax.legend()
        _ax.set_ylabel("f'(t)")
        _ax.set_xlabel('t')
        _ax.axhline(0,c='grey', ls=':')

    show(_ax, analytical_derv_new=analytical_derv_new, t_new=t_new, fwd_derv=fwd_derv)


@app.cell(hide_code=True)
def check_3_09():
    check_answers(t_new=t_new, analytical_derv_new=analytical_derv_new, key="answer_3_09")


@app.cell(hide_code=True)
def sol_3_09():
    dt_sol9 = t_sol7[1]-t_sol7[0]
    t_new_sol9 = t_fwd_sol8 + dt_sol9/2
    analytical_derv_new_sol9 = np.cos(t_new_sol9)

    _fig, _ax = plt.subplots()
    _ax.plot(t_new_sol9, fwd_derv_sol8, '-o', label='Fwd Shifted')
    _ax.plot(t_new_sol9, analytical_derv_new_sol9, '-o', label='Analytical')
    _ax.legend()
    _ax.set_ylabel("f'(t)")
    _ax.set_xlabel('t')
    _ax.axhline(0,c='grey', ls=':')

    t_new_sol9 = np.copy(t_new_sol9)
    analytical_derv_new_sol9 = np.copy(analytical_derv_new_sol9)

    show(_ax)


@app.cell
def demo_01():
    t_2 = np.linspace(0,10,1000) 
    v = t_2**2
    dvdt = (v[1:]-v[:-1])/(t_2[1:]-t_2[:-1])

    _fig, _axs = plt.subplots(1, 2, figsize=(14,4))
    _ax = _axs[0]
    _ax.plot(t_2,v)
    _ax.set_xlabel("t")
    _ax.set_ylabel("v")
    _ax = _axs[1]

    # Note that we need to pick out only the first N-1 points of the t-array for plotting
    # Otherwise, t and dvdt are not the same size!
    _ax.plot(t_2[:-1], dvdt)
    _ax.set_xlabel("t")
    _ax.set_ylabel("dvdt")
    _fig


@app.cell(hide_code=True)
def head_3_10():
    mo.md(
        r"""
        ## Exercise 1.10

        Write code that uses slicing to calculate the center derivative of a dataset constructed from the function $v = \sin(t)$ for an array `t` that runs from 0 to 10 with 1000 points. 
        Evaluate the center derivative at the positions of original points, not between them, which means that your output array should be two points smaller in size than the input.
        """
    )


@app.cell
def ex_3_10():
    # Fill these in as you work through the exercise.
    dvdt_2 = None

    # dvdt_2 = ...

    # Have a look at the plots to see if your answer looks reasonable
    _fig, _axs = plt.subplots(1, 2, figsize=(14,4))
    _ax = _axs[0]
    _ax.plot(t_2,v)
    _ax.set_xlabel("t")
    _ax.set_ylabel("v")
    _ax.axhline(0,ls=":", c='gray')
    _ax.axvline(0,ls=":", c='gray')

    # Do not edit or remove the boiler-plate code below.
    if given(dvdt_2):
        _ax = _axs[1]

        # Note that with the instructions above, this is the correct time array
        # for plotting the center derivative
        _ax.plot(t_2[1:-1], dvdt_2)
        _ax.set_xlabel("t")
        _ax.set_ylabel("dvdt")
        _ax.axhline(0,ls=":", c='gray')
        _ax.axvline(0,ls=":", c='gray')

    show(_fig, dvdt=dvdt_2)


@app.cell(hide_code=True)
def check_3_10():
    check_answers(dvdt_2=dvdt_2, key="answer_3_10")


@app.cell(hide_code=True)
def sol_3_10():
    t_sol10 = np.linspace(0,10,1000)
    v_sol10 = np.sin(t_sol10)

    dvdt_sol10 = (v_sol10[2:] - v_sol10[:-2])/(t_sol10[2:] - t_sol10[:-2])

    _fig, _axs = plt.subplots(1, 2, figsize=(14,4))
    _ax = _axs[0]
    _ax.plot(t_sol10,v_sol10)
    _ax.set_xlabel("t")
    _ax.set_ylabel("v")
    _ax.axhline(0,ls=":", c='gray')
    _ax.axvline(0,ls=":", c='gray')
    _ax = _axs[1]

    _ax.plot(t_sol10[1:-1], dvdt_sol10)
    _ax.set_xlabel("t")
    _ax.set_ylabel("dvdt")
    _ax.axhline(0,ls=":", c='gray')
    _ax.axvline(0,ls=":", c='gray')

    dvdt_sol10 = dvdt_sol10

    show(_fig)


@app.cell
def demo_02():
    # Derivatives of a vector (1D)

    x_3 = np.linspace(-5,5,100)
    y_2 = np.exp(-x_3**2)

    _fig, _ax = plt.subplots()
    _ax.plot(x_3,y_2, label="y")

    # Note that np.diff(x) is one point shorter! 
    # By choosing to plot against t[0:-1], we are picking the "forward difference" approximation
    _ax.plot(x_3[0:-1], np.diff(y_2), label="dy/dx")

    # A second derivative
    _ax.plot(x_3[0:-2], np.diff(y_2, n=2), label="d$^2$y/dx$^2$")

    _ax.legend()
    _ax.set_xlabel("x")
    _ax


@app.cell
def demo_03():
    # Derivatives of a 2D function

    x_4 = np.linspace(-5,5,100)
    y_3 = np.linspace(-5,5,100)

    X,Y = np.meshgrid(x_4,y_3)
    Z = np.exp(-X**2-Y**2)

    _fig, _axs = plt.subplots(1, 3, figsize=(14,3.5))

    _ax = _axs[0]
    _im1 = _ax.imshow(
        Z,
        aspect='auto',
        cmap="RdBu_r", 
        origin='lower',
        extent=(x_4[0], x_4[-1], y_3[0], y_3[-1])
    )

    _im1.set_clim(-1,1)
    _fig.colorbar(_im1).set_label("Z")
    _ax.set_xlabel("x")
    _ax.set_ylabel("y")

    _ax = _axs[1]
    _im2 = _ax.imshow(
        np.diff(Z,axis=0),
        aspect='auto',
        cmap="RdBu_r", 
        origin='lower',
        extent=(x_4[0], x_4[-1], y_3[0], y_3[-1])
    )
    _fig.colorbar(_im2).set_label("dZ/dy")
    _ax.set_xlabel("x")
    _ax.set_ylabel("y")

    _ax = _axs[2]
    _im3 = _ax.imshow(
        np.diff(Z,axis=1),
        aspect='auto',
        cmap="RdBu_r", 
        origin='lower',
        extent=(x_4[0], x_4[-1], y_3[0], y_3[-1])
    )
    _fig.colorbar(_im3).set_label("dZ/dx")
    _ax.set_xlabel("x")
    _ax.set_ylabel("y")

    _fig.tight_layout()
    _fig


if __name__ == "__main__":
    app.run()
