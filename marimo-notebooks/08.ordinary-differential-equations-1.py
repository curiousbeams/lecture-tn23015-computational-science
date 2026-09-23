import marimo

app = marimo.App(width="medium")

with app.setup:
    import marimo as mo
    import numpy as np
    import matplotlib.pyplot as plt
    from scipy.integrate import solve_ivp
    from tn23015 import check_answers, given, load_data, md, print, row, show, slider


@app.cell(hide_code=True)
def head_11_01():
    mo.md(
        r"""
        ## Exercise 8.1

        Write code to solve the problem of a charging capacitor with $V_0 = 1$ V, $R = 1$ M$\Omega$, and $C = 1 \mu$F.
        Your calculation should produce an array for $V(t)$ for $t$ from 0 to 10 seconds with 1000 points.
        Make a plot of $V(t)$.
        Does it do what you expect it should?
        """
    )


@app.cell
def ex_11_01():
    # Fill this in as you work through the exercise.
    _ax = None

    N = 1000
    t = np.linspace(0,10,N)
    dt = t[1]-t[0]
    R = 1e6
    C = 1e-6
    V0 = 1

    # Pre-allocating the array is a good idea, in general it is much faster 
    # to fill a pre-allocated array than to use append()
    V = np.empty(N)

    # Initial condition
    # V[0] = ____

    # A function for returning the derivative
    def dVdt(V):
        return None

    # for i in range(___,___):
    #     V[i] = ..

    # Now make a plot (with appropriate labels!)
    # _fig, _ax = plt.subplots()
    # ...

    # Do not edit or remove the boiler-plate code below.
    show(_ax, dVdt=dVdt)


@app.cell(hide_code=True)
def check_11_1():
    check_answers(V=V, key="answer_11_1", when=given(dVdt))


@app.cell(hide_code=True)
def sol_11_01():
    N_sol1 = 1000
    t_sol1 = np.linspace(0,10,N_sol1)
    dt_sol1 = t_sol1[1]-t_sol1[0]
    R_sol1 = 1e6
    C_sol1 = 1e-6
    V0_sol1 = 1

    # Pre-allocating the array is a good idea, in general it is much faster 
    # to fill a pre-allocated array than to use append()
    V_sol1 = np.empty(N_sol1)

    # Initial condition
    V_sol1[0] = 0

    # A function for returning the derivative
    def dVdt_sol1(V):
        return (V0_sol1-V)/R_sol1/C_sol1

    for _i in range(1,N_sol1):
        V_sol1[_i] = V_sol1[_i-1] + dt_sol1*dVdt_sol1(V_sol1[_i-1])

    # Now make a plot (with appropriate labels!)
    _fig, _ax = plt.subplots()
    _ax.plot(t_sol1,V_sol1)
    _ax.set_ylabel("Voltage (V)")
    _ax.set_xlabel("Time (s)")
    V_sol1 = np.copy(V_sol1)

    show(_ax)


@app.cell(hide_code=True)
def head_11_02():
    mo.md(
        r"""
        ## Exercise 8.2

        Use the Euler method to solve for the voltage on the capacitor for the case that the input voltage is not constant for $t>0$ but instead oscillates at a frequency of 1 Hz with an amplitude of 1 Volt for $t>0$: $V(t>0)= \sin(\omega t)$.
        The capacitor is also taken to be uncharged at $t=0$. 

        Note now that your derivative is now not only a function of $V$, but now also explicitly dependent on $t$.

        Your calculation should produce an array for $V(t)$ for $t$ from 0 to 10 seconds with 1000 points.
        Make a plot of $V(t)$.
        Does it do what you expect it should?
        """
    )


@app.cell
def ex_11_02():
    # Fill this in as you work through the exercise.
    _ax = None

    N_2 = 1000
    t_2 = np.linspace(0,10,N_2) # seconds
    dt_2 = t_2[1]-t_2[0]
    R_2 = 1e6 # Ohms
    C_2 = 1e-6 # F
    V0_2 = 1 # V 
    f = 1 # Hz 

    # Pre-allocating the array is a good idea, in general it is much faster 
    # to fill a pre-allocated array than to use append()
    V_2 = np.empty(N_2)

    # Initial condition
    # V[0] = ____

    # A function for returning the derivative
    def dVdt_2(t,V):
        return None

    # for i in range(___,___):
    #     V[i] = ..

    # Now make a plot (with appropriate labels!)
    # _fig, _ax = plt.subplots()
    # ...

    # Do not edit or remove the boiler-plate code below.
    show(_ax, dVdt=dVdt_2)


@app.cell(hide_code=True)
def check_11_2():
    check_answers(V_2=V_2, key="answer_11_2", when=given(dVdt_2))


@app.cell(hide_code=True)
def sol_11_02():
    N_sol2 = 1000
    t_sol2 = np.linspace(0,10,N_sol2) # seconds
    dt_sol2 = t_sol2[1]-t_sol2[0]
    R_sol2 = 1e6 # Ohms
    C_sol2 = 1e-6 # F
    V0_sol2 = 1 # V 
    f_sol2 = 1 # Hz 

    # Pre-allocating the array is a good idea, in general it is much faster 
    # to fill a pre-allocated array than to use append()
    V_sol2 = np.empty(N_sol2)

    # Initial condition
    V_sol2[0] = 0

    # A function for returning the derivative
    def dVdt_sol2(t,V):
        return (V0_sol2*np.sin(2*np.pi*f_sol2*t)-V)/R_sol2/C_sol2

    for _i in range(1,N_sol2):
        V_sol2[_i] = V_sol2[_i-1] + dt_sol2*dVdt_sol2(t_sol2[_i-1],V_sol2[_i-1])

    # Now make a plot (with appropriate labels!)
    _fig, _ax = plt.subplots()
    _ax.plot(t_sol2,V_sol2)
    _ax.set_ylabel("Voltage (V)")
    _ax.set_xlabel("Time (s)")
    V_sol2 = np.copy(V_sol2)

    show(_ax)


@app.cell(hide_code=True)
def head_11_03():
    mo.md(
        r"""
        ## Exercise 8.3

        Calculate $x(t)$ for a mass on a spring.
        Take $m = 1$ kg, $k = 1$ N/m, $x(t=0) = 0$ and $v(t=0) = 1$ m/s.
        Your code should output an array that represent $x(t)$ for $t$ from 0 to 20*$\pi$ seconds (which should give exactly 10 oscillations) with 1000 points.
        Make a plot of $x(t)$.
        Does it do what you expect it should?
        """
    )


@app.cell
def ex_11_03():
    # Fill this in as you work through the exercise.
    _ax = None

    N_3 = 1000
    t_3 = np.linspace(0,10*2*np.pi,N_3)
    dt_3 = t_3[1]-t_3[0]
    m = 1
    k = 1

    # Pre-allocating the array is a good idea, it is much faster 
    # to fill a pre-allocated array than to use append()
    x = np.empty(N_3)
    v = np.empty(N_3)

    # Initial condition
    # v[0] = ___
    # x[0] = ___

    # A function for returning dv/dt = F / m 
    # Note that it is only a function of x in this case
    def dvdt(x):
        return None

    # Note that it is only a function of v in this case
    def dxdt(v):
        return None

    # for i in range(___,___):
    #     x[i] = ... 
    #     v[i] = ...

    # An appropriate plot
    # _fig, _ax = plt.subplots()
    # ...

    # Do not edit or remove the boiler-plate code below.
    show(_ax, dvdt=dvdt, dxdt=dxdt)


@app.cell(hide_code=True)
def check_11_3():
    check_answers(x=x, key="answer_11_3", when=given(dvdt, dxdt))


@app.cell(hide_code=True)
def sol_11_03():
    N_sol3 = 1000
    t_sol3 = np.linspace(0,10*2*np.pi,N_sol3)
    dt_sol3 = t_sol3[1]-t_sol3[0]
    m_sol3 = 1
    k_sol3 = 1

    # Pre-allocating the array is a good idea, it is much faster 
    # to fill a pre-allocated array than to use append()
    x_sol3 = np.empty(N_sol3)
    v_sol3 = np.empty(N_sol3)

    # Initial condition
    v_sol3[0] = 1
    x_sol3[0] = 0

    # A function for returning dv/dt = F / m 
    # Note that it is only a function of x in this case
    def dvdt_sol3(x):
        return -k_sol3*x/m_sol3

    # Note that it is only a function of v in this case
    def dxdt_sol3(v):
        return v

    for _i in range(1,N_sol3):
        x_sol3[_i] = x_sol3[_i-1] + dt_sol3*dxdt_sol3(v_sol3[_i-1])  
        v_sol3[_i] = v_sol3[_i-1] + dt_sol3*dvdt_sol3(x_sol3[_i-1])

    # An appropriate plot
    _fig, _ax = plt.subplots()
    _ax.plot(t_sol3,x_sol3)
    _ax.set_ylabel("x (m)")
    _ax.set_xlabel("t (s)")
    x_sol3 = np.copy(x_sol3)

    show(_ax)


@app.cell(hide_code=True)
def head_11_04():
    mo.md(
        r"""
        ## Exercise 8.4

        Implement your own RK2 integration code for the same problem as specified in Exercise 8.1.
        """
    )


@app.cell
def ex_11_04():
    # Fill this in as you work through the exercise.
    _ax = None

    N_4 = 1000
    t_4 = np.linspace(0,10,N_4)
    dt_4 = t_4[1]-t_4[0]
    R_3 = 1e6
    C_3 = 1e-6
    V0_3 = 1
    f_2 = 1 

    # Pre-allocating the array is a good idea, it is much faster 
    # to fill a pre-allocated array than to use append()
    V_3 = np.empty(N_4)

    # Initial condition
    # V[0] = ....

    # A function for returning the derivative (for generality, make it a
    # function of both V and t, although it may not depend explicitly on t
    # in this case)
    def dVdt_3(V,t):
        return None

    for _i in range(1,N_4):
        ...

    # Now the plot
    # _fig, _ax = plt.subplots()
    # ...

    # Do not edit or remove the boiler-plate code below.
    show(_ax, dVdt=dVdt_3)


@app.cell(hide_code=True)
def check_11_4():
    check_answers(V_3=V_3, key="answer_11_4", when=given(dVdt_3))


@app.cell(hide_code=True)
def sol_11_04():
    N_sol4 = 1000
    t_sol4 = np.linspace(0,10,N_sol4)
    dt_sol4 = t_sol4[1]-t_sol4[0]
    R_sol4 = 1e6
    C_sol4 = 1e-6
    V0_sol4 = 1
    f_sol4 = 1 

    # Pre-allocating the array is a good idea, it is much faster 
    # to fill a pre-allocated array than to use append()
    V_sol4 = np.empty(N_sol4)

    # Initial condition
    V_sol4[0] = 0

    # A function for returning the derivative (for generality, make it a
    # function of both V and t, although it may not depend explicitly on t
    # in this case)
    def dVdt_sol4(V,t):
        return (V0_sol4-V)/R_sol4/C_sol4
    for _i in range(1,N_sol4):

        # First estimate the midpoint function value using Euler
        # The estimated change in V at the midpoint using Euler we call k1
        k1_sol4 = dt_sol4*dVdt_sol4(V_sol4[_i-1], t_sol4[_i-1])

        # Now use our estimated value of V at the midpoint to get a better
        # estimate of the slope and use this to extrapolate to the next
        # timestep
        k2_sol4 = dt_sol4*dVdt_sol4(V_sol4[_i-1]+k1_sol4/2, t_sol4[_i-1]+dt_sol4/2)

        # We're done!
        V_sol4[_i] = V_sol4[_i-1] + k2_sol4

    # Now the plot
    _fig, _ax = plt.subplots()
    _ax.plot(t_sol4,V_sol4)
    _ax.set_xlabel("Time (s)")
    _ax.set_ylabel("Voltage (V)")
    V_sol4 = np.copy(V_sol4)

    show(_ax)


@app.cell(hide_code=True)
def head_11_05():
    mo.md(
        r"""
        ## Exercise 8.5

        Implement the solution to Exercise 8.3 with your own RK2 integration code.
        Does this look more like what you would expect?
        """
    )


@app.cell
def ex_11_05():
    # Fill this in as you work through the exercise.
    _ax = None

    N_5 = 1000
    t_5 = np.linspace(0,10*np.pi*2,N_5)
    dt_5 = t_5[1]-t_5[0]
    m_2 = 1
    k_2 = 1

    # Pre-allocating the array is a good idea, it is much faster 
    # to fill a pre-allocated array than to use append()
    x_2 = np.empty(N_5)
    v_2 = np.empty(N_5)

    # Initial condition
    # v[0] = ....
    # x[0] = ....

    def dvdt_2(x):
        return None

    def dxdt_2(v):
        return None

    for _i in range(1,N_5):
        ...

        # ....
        #x[i] = ....
        #v[i] = .... 

    # And the plot
    # _fig, _ax = plt.subplots()
    # ...

    # Do not edit or remove the boiler-plate code below.
    show(_ax, dvdt=dvdt_2, dxdt=dxdt_2)


@app.cell(hide_code=True)
def check_11_5():
    check_answers(x_2=x_2, key="answer_11_5", when=given(dvdt_2, dxdt_2))


@app.cell(hide_code=True)
def sol_11_05():
    N_sol5 = 1000
    t_sol5 = np.linspace(0,10*np.pi*2,N_sol5)
    dt_sol5 = t_sol5[1]-t_sol5[0]
    m_sol5 = 1
    k_sol5 = 1

    # Pre-allocating the array is a good idea, it is much faster 
    # to fill a pre-allocated array than to use append()
    x_sol5 = np.empty(N_sol5)
    v_sol5 = np.empty(N_sol5)

    # Initial condition
    v_sol5[0] = 1
    x_sol5[0] = 0
    def dvdt_sol5(x):
        return -k_sol5*x/m_sol5
    def dxdt_sol5(v):
        return v
    for _i in range(1,N_sol5):

        # First the k1s to extrapolate the midpoints
        k1x_sol5 = dt_sol5*dxdt_sol5(v_sol5[_i-1])
        k1v_sol5 = dt_sol5*dvdt_sol5(x_sol5[_i-1])

        # Now the k2s
        k2x_sol5 = dt_sol5*dxdt_sol5(v_sol5[_i-1]+0.5*k1v_sol5)
        k2v_sol5 = dt_sol5*dvdt_sol5(x_sol5[_i-1]+0.5*k1x_sol5)

        # Now the values
        x_sol5[_i] = x_sol5[_i-1] + k2x_sol5
        v_sol5[_i] = v_sol5[_i-1] + k2v_sol5  

    # And the plot
    _fig, _ax = plt.subplots()
    _ax.plot(t_sol5,x_sol5)
    _ax.set_ylabel("x (m)")
    _ax.set_xlabel("t (s)")
    x_sol5 = np.copy(x_sol5)

    show(_ax)


@app.cell(hide_code=True)
def head_11_06():
    mo.md(
        r"""
        ## Exercise 8.6

        Implement RK4 integration for the problem of Exercise 8.1.
        """
    )


@app.cell
def ex_11_06():
    # Fill this in as you work through the exercise.
    _ax = None

    N_6 = 1000
    t_6 = np.linspace(0,10,N_6)
    dt_6 = t_6[1]-t_6[0]
    R_4 = 1e6
    C_4 = 1e-6
    V0_4 = 1
    f_3 = 1 

    # Pre-allocating the array is a good idea, it is much faster 
    # to fill a pre-allocated array than to use append()
    V_4 = np.empty(N_6)

    # Initial condition
    # V[0] = ....

    # A function for returning the derivative
    def dVdt_4(V,t):
        return None

    for _i in range(1,N_6):
        ...

        #V[i] = ...
    # And the plot
    # _fig, _ax = plt.subplots()
    # ...

    # Do not edit or remove the boiler-plate code below.
    show(_ax, dVdt=dVdt_4)


@app.cell(hide_code=True)
def check_11_6():
    check_answers(t_6=t_6, V_4=V_4, key="answer_11_6", when=given(dVdt_4))


@app.cell(hide_code=True)
def sol_11_06():
    N_sol6 = 1000
    t_sol6 = np.linspace(0,10,N_sol6)
    dt_sol6 = t_sol6[1]-t_sol6[0]
    R_sol6 = 1e6
    C_sol6 = 1e-6
    V0_sol6 = 1
    f_sol6 = 1 

    # Pre-allocating the array is a good idea, it is much faster 
    # to fill a pre-allocated array than to use append()
    V_sol6 = np.empty(N_sol6)

    # Initial condition
    v_sol5[0] = 0

    # A function for returning the derivative
    def dVdt_sol6(V,t):
        return (V0_sol6-V)/R_sol6/C_sol6
    for _i in range(1,N_sol6):
        k1_sol6 = dt_sol6*dVdt_sol6(V_sol6[_i-1], t_sol6[_i-1])
        k2_sol6 = dt_sol6*dVdt_sol6(V_sol6[_i-1]+k1_sol6/2, t_sol6[_i-1]+dt_sol6/2)
        k3_sol6 = dt_sol6*dVdt_sol6(V_sol6[_i-1]+k2_sol6/2, t_sol6[_i-1]+dt_sol6/2)
        k4_sol6 = dt_sol6*dVdt_sol6(V_sol6[_i-1]+k3_sol6, t_sol6[_i-1]+dt_sol6)

        # We're done!
        V_sol6[_i] = V_sol6[_i-1] + (k1_sol6+2*k2_sol6+2*k3_sol6+k4_sol6)/6

    # And the plot
    _fig, _ax = plt.subplots()
    _ax.plot(t_sol6,x_sol5)
    _ax.set_ylabel("x (m)")
    _ax.set_xlabel("t (s)")
    t_sol6 = np.copy(t_sol6)
    V_sol6 = np.copy(V_sol6)

    show(_ax)


@app.cell(hide_code=True)
def head_11_07():
    mo.md(
        r"""
        ## Exercise 8.7

        Use the `solve_ivp()` routine to solve the problem of the charging capacitor above from Exercise 8.1. 

        You will need to define a function `dVdt(t,V)`.
        By convention, this function should take time (the independent variable) as its first argument and the voltage value as it's second.
        This function you will need to give as the first argument of the `solve_ivp()` function. 

        You will also need to pass a [tuple](https://docs.python.org/3/tutorial/datastructures.html#tuples-and-sequences) as the second argument of `solve_ivp()` to specify the start and end times.

        Finally, you will need to give `solve_ivp()` the initial value of the voltage in the third argument.
        Since `solve_ivp()` is capable of solving multidimensional simultaneous equations, and also higher order ODEs, this argument must be a list of initial values, one for each of the 1st order ODEs it is solving.
        Although the problem we are considering of the RC circuit is only a single first-order ODE, we still have to make our initial condition into an array (for example, a numpy array of size `(1,)`).
        For this case, you can provide a list with one element: `[V0]`, where `V0` is the value $V(t=0)$.

        Plot your solution using points in your plot so that you can see the time steps that the routine chose for you automatically.
        Also, plot on top of the points you get the answer you had from Exercise 8.6 in which you solve with RK4 with 1000 points.
        """
    )


@app.cell
def ex_11_07():
    # Fill these in as you work through the exercise.
    _ax = V_5 = sol = t_7 = None

    R_5 = 1e6
    C_5 = 1e-6
    V0_5 = 1

    def dVdt_5(t,V):
        return None

    #sol = solve_ivp(dVdt, ...., ....)

    # By default, the independent variable is always stored in the name sol.t
    # t_7 = ....

    # By default, the dependent variable is always stored in the name sol.y
    # The shape of sol.y will be (1,N), since this is only a first order equation
    # However, to get this into an array we can plot, we still need to index
    # it using sol.y[0,:]
    # V_5 = ....

    # A plot with the scipy answer and your answer from exercise 5 (with legend)
    # _fig, _ax = plt.subplots()
    # _ax.plot(t,V, 'o', label=....)
    # _ax.plot(t_6, V_4, label=...)

    # Do not edit or remove the boiler-plate code below.
    show(_ax, V=V_5, sol=sol, t=t_7, dVdt=dVdt_5)


@app.cell(hide_code=True)
def check_11_7():
    check_answers(t_7=t_7, V_5=V_5, key="answer_11_7")


@app.cell(hide_code=True)
def sol_11_07():
    R_sol7 = 1e6
    C_sol7 = 1e-6
    V0_sol7 = 1

    def dVdt_sol7(t,V):
        return (V0_sol7-V)/R_sol7/C_sol7
    sol_sol7 = solve_ivp(dVdt_sol7, (0,10), [0])

    # By default, the independent variable is always stored in the name sol.t
    t_sol7 = sol_sol7.t

    # By default, the dependent variable is always stored in the name sol.y
    # The shape of sol.y will be (1,N), since this is only a first order equation
    # However, to get this into an array we can plot, we still need to index
    # it using sol.y[0,:]
    V_sol7 = sol_sol7.y[0,:]

    # A plot with the scipy answer and your answer from exercise 5 (with legend)
    # _ax.plot(t,V, 'o', label=....)
    # _ax.plot(t_6, V_4, label=...)
    _fig, _ax = plt.subplots()
    _ax.plot(t_sol7,V_sol7, 'o', label="Scipy")
    _ax.plot(t_sol6, V_sol6, label="Own RK4")
    _ax.set_xlabel("Time (s)")
    _ax.set_ylabel("Voltage (V)")
    _ax.legend()
    t_sol7 = np.copy(t_sol7)
    V_sol7 = np.copy(V_sol7)

    show(_ax)


@app.cell(hide_code=True)
def head_11_08():
    mo.md(
        r"""
        ## Exercise 8.8

        Use the `t_eval` parameter of the `solve_ivp()` to specify which points in time for which the voltage should be calculated.
        Use a range of 0 of 10 seconds with 1000 points.
        Make a plot of $V(t)$, and a second plot showing the difference between your RK4 calculation in Exercise 8.6 with the values calculated by the default settings of the `solve_ivp()` routine.
        """
    )


@app.cell
def ex_11_08():
    # Fill these in as you work through the exercise.
    V_6 = sol_2 = t_8 = None

    R_6 = 1e6
    C_6 = 1e-6
    V0_6 = 1

    def dVdt_6(t,V):
        return None

    # sol_2 = solve_ivp(dVdt, ...., ...., t_eval=......)
    # t_8 = ...
    # V_6 = ...

    # Fill in the commented lines below, but leave the rest of this block in place.
    _fig = None
    if given(V_6, sol_2, t_8, V_4, dVdt_6):
        _fig, _axs = plt.subplots(1, 2, figsize=(12,4))
        _ax = _axs[0]

        # _ax.plot(t,V_4, '--', linewidth=4, label=...)
        # _ax.plot(t,V, label=...)
        _ax = _axs[1]
        _ax.plot(t_8,V_6-V_4)
        _fig.tight_layout()

    show(_fig, V=V_6, sol=sol_2, t=t_8, V_4=V_4, dVdt=dVdt_6)


@app.cell(hide_code=True)
def check_11_8():
    check_answers(t_8=t_8, V_6=V_6, key="answer_11_8")


@app.cell(hide_code=True)
def sol_11_08():
    R_sol8 = 1e6
    C_sol8 = 1e-6
    V0_sol8 = 1

    def dVdt_sol8(t,V):
        return (V0_sol8-V)/R_sol8/C_sol8
    sol_sol8 = solve_ivp(dVdt_sol8, (0,10), [0], t_eval=np.linspace(0,10,1000))
    t_sol8 = sol_sol8.t
    V_sol8 = sol_sol8.y[0,:]
    _fig, _axs = plt.subplots(1, 2, figsize=(12,4))
    _ax = _axs[0]

    # _ax.plot(t,V_4, '--', linewidth=4, label=...)
    # _ax.plot(t,V, label=...)
    _ax.plot(t_sol8,V_sol6, '--', linewidth=4, label="RK4")
    _ax.plot(t_sol8,V_sol8, label="Scipy")
    _ax = _axs[1]
    _ax.plot(t_sol8,V_sol8-V_sol6)
    _ax.set_xlabel("Time (s)")
    _ax.set_ylabel("Scipy - RK4 solution (V)")
    _fig.tight_layout()

    t_sol8 = np.copy(t_sol8)
    V_sol8 = np.copy(V_sol8)

    show(_fig)


@app.cell(hide_code=True)
def head_11_09():
    mo.md(
        r"""
        ## Exercise 8.9

        Use `solve_ivp()` to solve the problem of Exercise 8.3.
        Use the same sampling in time by choosing the appropriate `t_eval`.
        Make two plots, one showing the resulting solution with your answer from your own RK2 code from Exercise 8.5, and a second plot showing the difference between the two.
        """
    )


@app.cell
def ex_11_09():
    # Fill these in as you work through the exercise.
    sol_3 = v_3 = v0 = x_3 = x0 = None

    N_7 = 1000
    t_9 = np.linspace(0,10*np.pi*2,N_7)
    m_3 = 1
    k_3 = 1

    # The derivative function
    def dydt(t,y):
        return None
        #x_3 = ...
        #v_3 = ...
        #return ...

    # x0 = ...
    # v0 = ...

    # Solve it
    # sol_3 = solve_ivp(dydt, ..., , ..., t_eval=t)

    # Extract the answers
    # t_9 = ...
    # x_3 = ...

    # Fill in the commented lines below, but leave the rest of this block in place.
    _fig = None
    if given(sol_3, v_3, v0, x_3, x0, x_2, dydt):

        #Now your plots
        _fig, _axs = plt.subplots(1, 2, figsize=(12,4))
        _ax = _axs[0]

        # _ax.plot(t,x, label=...)
        # _ax.plot(t,x_2,'--', linewidth=4, label=....)
        # _ax.set_ylabel(...)
        # plt.xlabel...)
        _ax = _axs[1]
        _ax.plot(t_9,x_3-x_2)

        # _ax.set_ylabel(...)
        # _ax.set_xlabel(...)
        _fig.tight_layout()

    show(_fig, sol=sol_3, v=v_3, v0=v0, x=x_3, x0=x0, x_2=x_2, dydt=dydt)


@app.cell(hide_code=True)
def check_11_9():
    check_answers(x_3=x_3, key="answer_11_9")


@app.cell(hide_code=True)
def sol_11_09():
    N_sol9 = 1000
    t_sol9 = np.linspace(0,10*np.pi*2,N_sol9)
    m_sol9 = 1
    k_sol9 = 1

    # The derivative function
    def dydt_sol9(t,y):

        #return ...
        x = y[0]
        v = y[1]
        return [v, -k_sol9*x/m_sol9]
    x0_sol9 = 0
    v0_sol9 = 1

    # Solve it
    sol_sol9 = solve_ivp(dydt_sol9, (0,100), (x0_sol9,v0_sol9), t_eval=t_sol9)

    # Extract the answers
    t_sol9 = sol_sol9.t
    x_sol9 = sol_sol9.y[0,:]

    #Now your plots
    _fig, _axs = plt.subplots(1, 2, figsize=(12,4))
    _ax = _axs[0]

    # _ax.plot(t,x, label=...)
    # _ax.plot(t,x_2,'--', linewidth=4, label=....)
    # _ax.set_ylabel(...)
    # plt.xlabel...)
    _ax.plot(t_sol9,x_sol9, label="Scipy")
    _ax.plot(t_sol9,x_sol5,'--', linewidth=4, label="Own RK2")
    _ax.set_ylabel("x (m)")
    _ax.set_xlabel("t (s)")
    _ax = _axs[1]
    _ax.plot(t_sol9,x_sol9-x_sol5)

    # _ax.set_ylabel(...)
    # _ax.set_xlabel(...)
    _ax.set_ylabel("Scipy - RK2 (m)")
    _ax.set_xlabel("t (s)")
    _fig.tight_layout()

    x_sol9 = np.copy(x_sol9)

    show(_fig)


@app.cell(hide_code=True)
def head_11_09b():
    mo.md(
        r"""
        ## Exercise 8.10

        They look pretty close: which one do you think is more accurate?
        How can you check?
        (Hint: where were things going wrong with Euler?
        At the start or the end?
        And what would we predict for the position of this oscillator at the last timestep in our simulation?)
        """
    )


@app.cell
def ex_11_09b():
    # What is an interesting thing to check to see which one is more accurate?

    # print(...)
    # print(...)

    # Do not edit or remove the boiler-plate code below.
    show()


@app.cell(hide_code=True)
def sol_11_09b():
    # What is an interesting thing to check to see which one is more accurate?

    # print(...)
    # print(...)
    print("My code x[-1] = ", x_sol5[-1])
    print("Scip x[-1]    = ", x_sol9[-1])

    show()


if __name__ == "__main__":
    app.run()
