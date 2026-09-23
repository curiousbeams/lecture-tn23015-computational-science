import marimo

app = marimo.App(width="medium")

with app.setup:
    import marimo as mo
    import numpy as np
    import matplotlib.pyplot as plt
    from tn23015 import check_answers, given, load_data, md, print, row, show, slider


@app.cell(hide_code=True)
def head_4_01():
    mo.md(
        r"""
        ## Exercise 2.1

        Modify the code below to produce a plot of the integrand in the range of 0 to 2 with 100 points.
        """
    )


@app.cell
def ex_4_01():
    # Fill these in as you work through the exercise.
    npts = x = y = None

    # Define the function f(x) 

    # First, make the arrays of x and y values for the plot
    # npts = ______
    # x = np.linspace(____,____,npts)
    # y = _____

    # Now plot it and add x and y labels

    _fig, _ax = plt.subplots()
    # A zero axis line is handy. "ls" is a shortcut for "linestyle" and "lw" is a shortcut for "linewidth"
    _ax.axhline(0,color='grey', linestyle=':')

    # _ax.plot(___,___)
    # ...

    # Do not edit or remove the boiler-plate code below.
    show(_ax, npts=npts, x=x, y=y)


@app.cell(hide_code=True)
def check_4_01():
    check_answers(x=x, y=y, key="answer_4_01")


@app.cell(hide_code=True)
def sol_4_01():
    # Define the function f(x) 
    def f_sol1(x):
        return x**4 - 2*x + 1

    # First, make the arrays of x and y values for the plot
    npts_sol1 = 100
    x_sol1 = np.linspace(0,2,npts_sol1)
    y_sol1 = f_sol1(x_sol1)

    _fig, _ax = plt.subplots()
    _ax.plot(x_sol1,y_sol1)
    _ax.set_xlabel("x")
    _ax.set_ylabel("Integrand")
    _ax.axhline(0,color='grey', linestyle=':')

    x_sol1 = np.copy(x_sol1)
    y_sol1 = np.copy(y_sol1)

    show(_ax)


@app.cell(hide_code=True)
def head_4_02():
    mo.md(
        r"""
        ## Exercise 2.2

        Write code to calculate the integral using the trapezoidal rule with $n = 11$ points in the range (10 "steps").
        """
    )


@app.cell
def ex_4_02():
    # Fill these in as you work through the exercise.
    trapezoidal_integral = None

    # trapezoidal_integral = ...

    # Do not edit or remove the boiler-plate code below.
    show(trapezoidal_integral=trapezoidal_integral)


@app.cell(hide_code=True)
def check_4_02():
    check_answers(trapezoidal_integral=trapezoidal_integral, key="answer_4_02")


@app.cell(hide_code=True)
def sol_4_02():
    # The number of points, and the starting and end points
    N_sol2 = 10
    a_sol2 = 0.0
    b_sol2 = 2.0

    # The step size
    h_sol2 = (b_sol2-a_sol2)/N_sol2

    # s is our running sum
    s_sol2 = 0.5*f_sol1(a_sol2) + 0.5*f_sol1(b_sol2)
    for _k in range(1,N_sol2):
        s_sol2 += f_sol1(a_sol2+_k*h_sol2)

    # The integral is then given by h*s
    trapezoidal_integral_sol2 = h_sol2*s_sol2
    trapezoidal_integral_sol2 = trapezoidal_integral_sol2

    show(trapezoidal_integral=trapezoidal_integral_sol2)


@app.cell(hide_code=True)
def head_4_03():
    mo.md(
        r"""
        ## Exercise 2.3

        Use a `while` loop to find the minimum value of $N$ you need to get the correct answer to [relative error](https://en.wikipedia.org/wiki/Approximation_error#Formal_Definition) of less than $10^{-6}$ = one part per million (ppm).

        The definition of relative error is as follows: if $v$ is the correct answer and $v_{\rm approx}$ is the approximate answer, the relative error $\eta$ is defined as:

        $$
        \eta = \left| \frac{v - v_{\rm approx}}{v} \right|
        $$

        Your while loop should have an "emergency exit" test that stops the loop with a `break` statement if $N$ exceeds 10,000.

        _Tip:_ If you have trouble with your exit condition on your while loop, it might be handy to include a code line `print("N %d eta %e" % (N,eta))` to keep track of what is going on in your code.
        This is an [elementary form](https://pythondebugging.com/articles/python-debugging-with-print-statements) of [debugging](https://en.wikipedia.org/wiki/Debugging).
        """
    )


@app.cell
def ex_4_03():
    # Fill these in as you work through the exercise.
    N = eta = integral = None

    # N = ...
    # integral = ...
    # eta = ...

    # Do not edit or remove the boiler-plate code below.
    show(N=N, eta=eta, integral=integral)


@app.cell(hide_code=True)
def check_4_03():
    check_answers(N=N, integral=integral, eta=eta, key="answer_4_03")


@app.cell(hide_code=True)
def sol_4_03():
    def f_sol3(x):
        return x**4 - 2*x + 1

    # We should start with something bigger than the exit condition
    eta_sol3 = 1

    # Start with a guess (could start with N=1 if we want)
    N_sol3 = 10

    while eta_sol3 > 1e-6:
        a_sol3 = 0.0
        b_sol3 = 2.0
        h_sol3 = (b_sol3-a_sol3)/N_sol3

        s_sol3 = 0.5*f_sol3(a_sol3) + 0.5*f_sol3(b_sol3)
        for _k in range(1,N_sol3):
            s_sol3 += f_sol3(a_sol3+_k*h_sol3)

        integral_sol3 = h_sol3*s_sol3
        eta_sol3 = np.abs((integral_sol3 - 4.4)/4.4)
        if (N_sol3 > 10000):
            print("N = 10000 and didn't reach eta < 1e-6")
        N_sol3 += 1

    print("N = %d: Integral is %f Relative error %e" % (N_sol3, integral_sol3, eta_sol3))
    N_sol3 = N_sol3
    integral_sol3 = integral_sol3
    eta_sol3 = eta_sol3

    show()


@app.cell(hide_code=True)
def head_4_04():
    mo.md(
        r"""
        ## Exercise 2.4

        Write code to implement Simpson's rule for the same integral as Exercise 2.1, using 11 points (10 steps).
        """
    )


@app.cell
def ex_4_04():
    # Fill these in as you work through the exercise.
    integral_simpson = None

    # integral_simpson = ...

    # Do not edit or remove the boiler-plate code below.
    if given(integral_simpson):
        print("Integral with Simpson's rule is %f" % integral_simpson)

    show(integral_simpson=integral_simpson)


@app.cell(hide_code=True)
def check_4_04():
    check_answers(integral_simpson=integral_simpson, key="answer_4_04")


@app.cell(hide_code=True)
def sol_4_04():
    N_sol4 = 10
    a_sol4 = 0.0
    b_sol4 = 2.0
    h_sol4 = (b_sol4-a_sol4)/N_sol4

    # Our running sum (we'll multiply by h/3 at the end)
    s_sol4 = f_sol3(a_sol4) + f_sol3(b_sol4)

    # First the odd terms
    for _k in range(1,N_sol4,2):
        s_sol4 += 4*f_sol3(a_sol4+_k*h_sol4)

    # Now the even terms
    for _k in range(2,N_sol4,2):
        s_sol4 += 2*f_sol3(a_sol4+_k*h_sol4)

    # The answer is then the sum*h/3
    integral_simpson_sol4 = s_sol4*h_sol4/3.0
    print("Integral with Simpson's rule is %f" % integral_simpson_sol4)

    integral_simpson_sol4 = integral_simpson_sol4

    show()


@app.cell(hide_code=True)
def head_4_05():
    mo.md(
        r"""
        ## Exercise 2.5

        Rewrite your calculation of the integral using Simpson's rule from Exercise 2.4 to be vectorised using numpy slicing and the function `np.sum()`. 
        > **Hint** — It may be useful to look back at the introduction notebooks on how to perform slicing with steps different than 1...
        """
    )


@app.cell
def ex_4_05():
    # Fill these in as you work through the exercise.
    integral_simpson_vector = None

    # Write your VECTORISED Simpson's rule code here
    # integral_simpson_vector = ...

    # Do not edit or remove the boiler-plate code below.
    if given(integral_simpson_vector):
        print("Integral with vectorised Simpson's rule is %f" % integral_simpson_vector)

    show(integral_simpson_vector=integral_simpson_vector)


@app.cell(hide_code=True)
def check_4_05():
    check_answers(integral_simpson_vector=integral_simpson_vector, key="answer_4_05")


@app.cell(hide_code=True)
def sol_4_05():
    # Write your VECTORISED Simpson's rule code here
    x_sol5 = np.linspace(0,2,11) # 10 steps is equivalent to 11 points 
    h_sol5 = x_sol5[1]-x_sol5[0]
    y_sol5 = f_sol3(x_sol5)
    integral_sol5 = (f_sol3(x_sol5[0])+f_sol3(x_sol5[-1]))
    integral_sol5 += 4*np.sum(y_sol5[1:-1:2]) # the odd terms
    integral_sol5 += 2*np.sum(y_sol5[2:-1:2]) # the even terms, excluding the end points
    integral_sol5 *= h_sol5/3.0

    integral_simpson_vector_sol5 = integral_sol5
    print("Integral with vectorised Simpson's rule is %f" % integral_simpson_vector_sol5)

    integral_simpson_vector_sol5 = integral_simpson_vector_sol5

    show()


@app.cell(hide_code=True)
def head_4_06():
    mo.md(
        r"""
        ## Exercise 2.6

        Read in the data and, using the trapezoidal rule, calculate from them the approximate distance traveled by the particle in the $x$ direction as a function of time.  

        _Hint_ This is a cumulative integral, a bit different from the definite integrals handled above.
        Your integral code should produce an array not a number!
        If $f(t)$ is the function describing the velocity as a function of time, then the answer $g(t)$ is given by:

        $$
        g(t) = \int_0^t h(\tau) d\tau
        $$

        Every element in your output array is then conceptually defined by computing an integral from $\tau=0$ to $\tau = t$. 

        (Of course, there may be cleaver and more computationally efficient ways to do it as well, but that is not the focus right now...)

        _Recommendation_ "[Modularize](https://en.wikipedia.org/wiki/Modular_programming)" your code by creating a function that does the trapezoidal integration of an array, this will make your code easier to write and use.
        """
    )


@app.cell
def ex_4_06():
    # Fill these in as you work through the exercise.
    d = t = v = y_2 = z = None

    # Load the data
    data = load_data("velocities.dat")
    # t = ...
    # v = ...

    # A function for calculating the trapezoidal integral of an array:
    def trapezoid(x):
        return None

    #y_2=[v[0],v[1]] 
    #z=trapezoid(y)

    # Now calculate the cumulative integral: 
    # d = ...

    # Do not edit or remove the boiler-plate code below.
    show(d=d, t=t, v=v, y=y_2, z=z, trapezoid=trapezoid)


@app.cell(hide_code=True)
def check_4_06():
    check_answers(d=d, key="answer_4_06")


@app.cell(hide_code=True)
def sol_4_06():
    # Load the data
    data_sol6 = load_data("velocities.dat")
    t_sol6 = data_sol6[:,0]
    v_sol6 = data_sol6[:,1]

    # The number of points in the array we read in
    N_sol6 = len(v_sol6)

    # It is specified that the time step is constant and is 1 second. (We could check this by checking if the
    # time data is a straight line, but I will trust the author.)
    h_sol6 = 1

    # n will be the last point of our cumulative integral. range(len(v)) will give a range list 
    # running from 0 to N-1 (v[N-1] being the last element in array v) 
    # A function for calculating the trapezoidal integral of an array:
    def trapezoid_sol6(x):
        N = len(x)
        if N == 1:
            return 0
        s = (x[0]+x[-1])/2 
        s += np.sum(x[1:-1])
        return s*h_sol6
    #y_sol5=[v[0],v[1]] 
    #z=trapezoid(y)

    # Now calculate the cumulative integral: 
    # Our desired output is not just the total distance travelled, but actually an 
    # array that shows the distance as a function of time. This is a bit different
    # to what we've been doing above since we will be calculating a _cumulative_ integral

    # The output array of distance vs. time
    d_sol6 = np.empty(N_sol6)

    # Note that it does not make sense to calculate the integral for the first point, since in zero 
    # time, no distance has been travelled. 
    d_sol6[0] = 0

    # There may be a numpy cumulative integral function (google would tell us quickly), but we'll
    # implement it ourselves here with a for loop.

    # Note it's not obvious that range() shoud start at two, but you must remember that v[0:2] 
    # gives an array [v[0], v[1]]

    for _i in range(1,N_sol6):
        d_sol6[_i] = trapezoid_sol6(v_sol6[0:_i+1])
    d_sol6 = np.copy(d_sol6)

    show(d=d_sol6)


@app.cell(hide_code=True)
def head_4_07():
    mo.md(
        r"""
        ## Exercise 2.7

        Make a plot with velocity on the left-hand y-axis and distance travelled in the right-hand y-axis. 

        To plot data with a second y-axis, you need a bit more matplotlib code:

        ```
        # First, initialize your plot with the plt.subplots() command, which returns an axis object you will need
        fig, ax1 = plt.subplots()

        # You then use the twinx() function to make a second axis object with it's x-axis linked to the original x-axis
        ax2 = ax1.twinx()

        # Now you can use the plot() commands of each axis objects: ax.plot(...). 
        ax1.plot(t,d, 'g-', label="d")
        ax1.set_ylabel("my axis (my units)", color='g')
        ax2.plot(...)
        ```

        You can also use the `axhline()` command to add horizontal lines.
        For example, this will add a grey dashed horizontal line:

        ```
        ax2.axhline(0, color='grey', linestyle=":")
        ```
        """
    )


@app.cell
def ex_4_07():
    # Your solution here

    # Do not edit or remove the boiler-plate code below.
    show()


@app.cell(hide_code=True)
def sol_4_07():
    # To make a second axis, we need to use the subplots() command to get access to the 
    # "axis" object variable of our plot
    fig_sol7, ax1_sol7 = plt.subplots()

    # Once we have it, we can use the twinx() function to make a second y axis
    ax2_sol7 = ax1_sol7.twinx()

    # And now we use plot commands associated with the two axis "objects" we have
    ax1_sol7.plot(t_sol6,d_sol6, 'g-', label="d")
    ax1_sol7.set_ylabel("Distance travelled (m)", color='g')
    ax1_sol7.axhline(0, color='g', linestyle=":")

    ax2_sol7.plot(t_sol6,v_sol6, 'b-', label="v")
    ax2_sol7.set_ylabel("Velocity (m/s)", color='b')
    ax2_sol7.axhline(0, color='b', linestyle=":")
    ax1_sol7.set_xlabel("Time (s)")
    ax1_sol7.legend(loc=2)

    show(ax2_sol7.legend(loc=0))


if __name__ == "__main__":
    app.run()
