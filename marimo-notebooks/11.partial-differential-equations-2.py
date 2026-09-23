import marimo

app = marimo.App(width="medium")

with app.setup:
    import marimo as mo
    import numpy as np
    import matplotlib.pyplot as plt
    from time import time
    from scipy.fftpack import dst,idst
    from tn23015 import check_answers, given, load_data, md, print, row, show, slider


@app.cell(hide_code=True)
def head_14_01():
    mo.md(
        r"""
        ## Exercise 11.1

        A steel block that is 1 cm thick has an initial temperture of 20 degrees Celcius.
        At time $t=0$, it is sandwiched between a cold bath at a temperature of 0 degrees at $x = 1$ cm, and a hot bath at a temperature of 50 degrees at $x = 0$.
        Calculate the time dependence of the temperature profile inside the steel block. 

        The thermal diffusivity D for steel is $4.25 \times 10^{-6}$ m$^2$/s.
        Perform your computation for a grid of points in spacial coodinate $x$ that runs from 0 to 1 cm with a total of `Nx` = 100 point in space.
        Calculate the profile for times from $t=0$ to $t=2$ seconds with `Nt` = 10$^4$ points in time.
        """
    )


@app.cell
def ex_14_01():
    # Fill these in as you work through the exercise.
    dt = dx = t = t1 = t2 = x = None

    # Physical constants
    D = 4.25e-6

    # Our spatial axis
    L = 0.01 
    Nx = 100

    # x = np.linspace(...)
    # dx = ...

    # Our time axis
    tf = 2
    Nt = int(1e4)

    # t = np.linspace(...,...,...)
    # dt = t[...]

    # A matrix to store the time and spatial dependence
    # of the temperature.
    # This will be a matrix of size (N_t, N_x). 
    # T[i,j] is then T for time t[i] and position x[j]
    T = np.zeros([Nt, Nx])

    # Our initial condibtion (uniform constant temperature)
    # T[...] = 20

    # The temperature at x=0 should be fixed at 50 for all times. 
    # At x=L, the temperature should be fixed at 0 for all times. 
    # T[...] = 50
    # T[...] = 0

    # t1 = time()
    # for i in range(N_t-1):
    #     # Note that we don't update the boundaries at x=0 and x=L
    #     for j in range(...,...):
    #         T[i+1,j] = T[i,j] + ... 
    # t2 = time()

    # Do not edit or remove the boiler-plate code below.
    if given(dt, dx, t, t1, t2, x):
        print("Total calculation time: %.2f seconds" % (t2-t1))

    show(dt=dt, dx=dx, t=t, t1=t1, t2=t2, x=x)


@app.cell(hide_code=True)
def check_14_1():
    check_answers(T=T, key="answer_14_1", when=given(dt, dx, t, t1, t2, x))


@app.cell(hide_code=True)
def sol_14_01():
    # Physical constants
    D_sol1 = 4.25e-6

    # Our spatial axis
    L_sol1 = 0.01 
    Nx_sol1 = 100

    x_sol1 = np.linspace(0,L_sol1,Nx_sol1)
    dx_sol1 = x_sol1[1]

    # Our time axis
    tf_sol1 = 2
    Nt_sol1 = int(1e4)

    t_sol1 = np.linspace(0,tf_sol1,Nt_sol1)
    dt_sol1 = t_sol1[1]

    # A matrix to store the time and spatial dependence
    # of the temperature.
    # This will be a matrix of size (N_t, N_x). 
    # T[i,j] is then T for time t[i] and position x[j]
    T_sol1 = np.zeros([Nt_sol1, Nx_sol1])

    # Our initial condibtion (uniform constant temperature)
    T_sol1[0,:] = 20

    # The temperature at x=0 should be fixed at 50 for all times. 
    # At x=L, the temperature should be fixed at 0 for all times. 
    T_sol1[:,0] = 50
    T_sol1[:,-1] = 0
    # t1_sol1 = time()
    # for i in range(N_t-1):
    #     # Note that we don't update the boundaries at x=0 and x=L
    #     for j in range(...,...):
    # t2_sol1 = time()
    t1_sol1 = time()
    for _i in range(Nt_sol1-1):
        for _j in range(1,Nx_sol1-1):
            T_sol1[_i+1,_j] = T_sol1[_i,_j] + D_sol1*dt_sol1/dx_sol1**2*(T_sol1[_i,_j+1]+T_sol1[_i,_j-1]-2*T_sol1[_i,_j])  
    t2_sol1 = time()
    print("Total calculation time: %.2f seconds" % (t2_sol1-t1_sol1))

    T_sol1 = T_sol1.copy()

    # A few snapshots in time, so the solution shows the result and not only the timing. The slider
    # below the exercise steps through the same data one frame at a time.
    _fig, _ax = plt.subplots()
    for _k in (0, Nt_sol1 // 100, Nt_sol1 // 20, Nt_sol1 // 4, Nt_sol1 - 1):
        _ax.plot(x_sol1, T_sol1[_k, :], label="t = %.2f s" % t_sol1[_k])
    _ax.set_ylabel("T (deg C)")
    _ax.set_xlabel("Distance x (m)")
    _ax.legend()

    show(_ax)


@app.cell
def demo_01():
    # We have 10^4 time steps, but 100 of them is plenty to see what happens.
    frames = 100
    step = slider(0, frames - 1, value=0, label="Time step", show_value=True)

    md("*The slider is shown with the plot below.*")


@app.cell
def demo_02():
    # Do not edit or remove the boiler-plate code below.
    _ax = None
    if given(t, x):
        _i = step.value * (Nt // frames)
        _fig, _ax = plt.subplots()
        _ax.plot(x, T[_i, :])
        _ax.set_ylim(0, 55)
        _ax.set_ylabel("T (deg C)")
        _ax.set_xlabel("Distance x (m)")
        _ax.set_title("t = %.2f seconds" % t[_i])

    show(step, _ax, t=t, x=x)


@app.cell(hide_code=True)
def head_14_02():
    mo.md(
        r"""
        ## Exercise 11.2

        Fill in the code below to solve the wave equation for a vibrating string using the FTCS method.
        Take $c = 1$ m/s and consider a string of length $L$. For your $x$ coordinate, use a grid with `Nx` = 100 points. 

        For you $t$ coordinate, run your simulation for 1.2 seconds with 550 points in your time array.
        Consider an initial displacement $x(x,t=0) = \sin(\pi x/L)$ and an initial velocity $v(x,t=0) = 0$.
        """
    )


@app.cell
def ex_14_02():
    # Fill these in as you work through the exercise.
    t_2 = u = v = x_2 = None

    # The wave velocity in the string
    c = 1 # m/s

    # Positions along the length of the string
    # Let's make it 1 m long
    L_2 = 1
    Nx_2 = 100
    # x_2 = np.linspace(...)

    # t_2 = np.linspace(...)
    # u = np.zeros(...)
    # v = np.zeros(...)

    # Do not edit or remove the boiler-plate code below.
    Nt_2 = dt_2 = dx_2 = t1_2 = t2_2 = tf_2 = None
    if given(t_2, u, v, x_2):
        dx_2 = x_2[1]

        # Our time axis
        # Let's make it 1.2 seconds long
        Nt_2 = 550
        tf_2 = 1.2
        dt_2 = t_2[1]

        # A matrix for tracking the vertical displacement of the string
        # and the vertical velocity v = du/dt

        # Our initial condibtion: a "displaced" string
        # Sine wave in displacement with no initial velocity
        u[0,:] = np.sin(np.pi*x_2/L_2)
        v[0,:] = 0

        # Make sure the boundary conditions are inforced
        u[:,[0,-1]] = 0
        v[:,[0,-1]] = 0

        t1_2 = time()
        for _i in range(Nt_2-1):
            for _j in range(1,Nx_2-1):
                ...

                #u[i+1,j] = ...
                #v[i+1,j] = ...

        t2_2 = time()

        print("Total calculation time: %.2f seconds" % (t2_2-t1_2))

    show(t=t_2, u=u, v=v, x=x_2)


@app.cell(hide_code=True)
def check_14_2():
    check_answers(u=u, v=v, key="answer_14_2")


@app.cell(hide_code=True)
def sol_14_02():
    # The wave velocity in the string
    c_sol2 = 1 # m/s

    # Positions along the length of the string
    # Let's make it 1 m long
    L_sol2 = 1
    Nx_sol2 = 100
    x_sol2 = np.linspace(0,L_sol2,Nx_sol2)
    dx_sol2 = x_sol2[1]

    # Our time axis
    # Let's make it 1.2 seconds long
    Nt_sol2 = 550
    tf_sol2 = 1.2
    t_sol2 = np.linspace(0,tf_sol2,Nt_sol2)
    dt_sol2 = t_sol2[1]

    # A matrix for tracking the vertical displacement of the string
    # and the vertical velocity v = du/dt
    u_sol2 = np.zeros([Nt_sol2, Nx_sol2])
    v_sol2 = np.zeros([Nt_sol2, Nx_sol2])

    # Our initial condibtion: a "displaced" string
    # Sine wave in displacement with no initial velocity
    u_sol2[0,:] = np.sin(np.pi*x_sol2/L_sol2)
    v_sol2[0,:] = 0

    # Make sure the boundary conditions are inforced
    u_sol2[:,[0,-1]] = 0
    v_sol2[:,[0,-1]] = 0

    t1_sol2 = time()
    for _i in range(Nt_sol2-1):
        for _j in range(1,Nx_sol2-1):
            u_sol2[_i+1,_j] = u_sol2[_i,_j] + v_sol2[_i,_j]*dt_sol2
            v_sol2[_i+1,_j] = v_sol2[_i,_j] + c_sol2**2/dx_sol2**2 * \
                (u_sol2[_i,_j-1] + u_sol2[_i,_j+1] - 2*u_sol2[_i,_j])*dt_sol2
    t2_sol2 = time()

    print("Total calculation time: %.2f seconds" % (t2_sol2-t1_sol2))

    u_sol2 = u_sol2.copy()
    v_sol2 = v_sol2.copy()

    # A few snapshots in time. FTCS is unstable for the wave equation, so what this shows is the
    # displacement growing without bound -- which is the point of the exercise.
    _fig, _ax = plt.subplots()
    for _k in (0, Nt_sol2 // 100, Nt_sol2 // 20, Nt_sol2 // 4, Nt_sol2 - 1):
        _ax.plot(x_sol2, u_sol2[_k, :], label="t = %.4f s" % t_sol2[_k])
    _ax.set_ylabel("Displacement u (m)")
    _ax.set_xlabel("Distance x (m)")
    _ax.legend()

    show(_ax)


@app.cell
def demo_03():
    frames_2 = 100
    step_2 = slider(0, frames_2 - 1, value=0, label="Time step", show_value=True)

    md("*The slider is shown with the plot below.*")


@app.cell
def demo_04():
    # Do not edit or remove the boiler-plate code below.
    _ax = None
    if given(Nt_2, t_2, u, x_2):
        _i = step_2.value * (Nt_2 // frames_2)
        _fig, _ax = plt.subplots()
        _ax.plot(x_2, u[_i, :])
        _ax.set_ylim(-1.2, 1.2)
        _ax.set_ylabel("Displacement u (m)")
        _ax.set_xlabel("Distance x (m)")
        _ax.set_title("t = %.4f seconds" % t_2[_i])

    show(step_2, _ax, Nt=Nt_2, t=t_2, u=u, x=x_2)


@app.cell
def demo_05():
    # Notebook code

    def my_dst(u):
        return dst(u[1:-1], type=1)

    def my_idst(uk):
        u = np.zeros(len(uk)+2)
        u[1:-1] = idst(uk, type=1)/2/(len(uk)+1)
        return u

    show()


@app.cell(hide_code=True)
def head_14_03():
    mo.md(
        r"""
        ## Exercise 11.3

        Implement the spectral method to find $u(x,t)$ for the problem of Exercise 11.2. At the end of your code, implement a function that calculates $u(x,t)$, and use this to find $u(x,10)$.
        """
    )


@app.cell
def ex_14_03():
    # Fill these in as you work through the exercise.
    k = uk = uk0 = vk0 = w = None

    # The wave velocity in the string
    c_2 = 1 # m/s

    # Positions along the length of the string
    # Let's make it 1 m long
    L_3 = 1
    Nx_3 = 100
    x_3 = np.linspace(0,L_3,Nx_3)
    dx_3 = x_3[1]

    # Our initial condibtion. u = vertical displacement, v = du/dt
    u0 = np.sin(np.pi*x_3/L_3)
    v0 = np.zeros(Nx_3)

    # Calculate the Fourier coefficients of the initial condition

    # uk0 = my_dst(...)
    # vk0 = my_dst(...)

    # k = ...
    # w = ...

    def calc_u(t):
        #uk = ...
        return my_idst(uk)

    # Do not edit or remove the boiler-plate code below.
    # `calc_u` raises on an unfilled `uk` rather than returning something the checker can recognise
    # as unanswered, so unlike the other answers it has to be gated.
    u_at_10 = calc_u(10) if given(uk) else None

    show(k=k, uk=uk, uk0=uk0, vk0=vk0, w=w)


@app.cell(hide_code=True)
def check_14_3():
    check_answers(
        uk0=uk0,
        vk0=vk0,
        k=k,
        w=w,
        u_at_10=u_at_10,
        key="answer_14_3",
    )


@app.cell(hide_code=True)
def sol_14_03():
    # The wave velocity in the string
    c_sol3 = 1 # m/s

    # Positions along the length of the string
    # Let's make it 1 m long
    L_sol3 = 1
    Nx_sol3 = 100
    x_sol3 = np.linspace(0,L_sol3,Nx_sol3)
    dx_sol3 = x_sol3[1]

    # Our initial condibtion. u = vertical displacement, v = du/dt
    u0_sol3 = np.sin(np.pi*x_sol3/L_sol3)
    v0_sol3 = np.zeros(Nx_sol3)

    # Calculate the Fourier coefficients of the initial condition

    uk0_sol3 = my_dst(u0_sol3)
    vk0_sol3 = my_dst(v0_sol3)
    k_sol3 = np.array(range(len(uk0_sol3)))+1
    w_sol3 = np.pi * c_sol3 * k_sol3 / L_sol3
    def calc_u_sol3(t):
        uk = uk0_sol3*np.cos(w_sol3*t) + vk0_sol3*np.sin(w_sol3*t)
        return my_idst(uk)

    uk0_sol3 = uk0_sol3.copy()
    vk0_sol3 = vk0_sol3.copy()
    k_sol3 = k_sol3.copy()
    w_sol3 = w_sol3.copy()

    # A few snapshots in time. Unlike FTCS above, the spectral solution stays bounded.
    _fig, _ax = plt.subplots()
    for _t in (0.0, 0.25, 0.5, 0.75, 1.0):
        _ax.plot(x_sol3, calc_u_sol3(_t), label="t = %.2f s" % _t)
    _ax.set_ylim(-1.2, 1.2)
    _ax.set_ylabel("Displacement u (m)")
    _ax.set_xlabel("Distance x (m)")
    _ax.legend()

    show(_ax)


@app.cell
def demo_06():
    frames_3 = 100
    t_3 = np.linspace(0, 2, frames_3)
    step_3 = slider(0, frames_3 - 1, value=0, label="Time step", show_value=True)

    md("*The slider is shown with the plot below.*")


@app.cell
def demo_07():
    # Do not edit or remove the boiler-plate code below.
    _ax = None
    if given(uk):
        _fig, _ax = plt.subplots()
        _ax.plot(x_3, calc_u(t_3[step_3.value]))
        _ax.set_ylim(-1.2, 1.2)
        _ax.set_ylabel("Displacement u (m)")
        _ax.set_xlabel("Distance x (m)")
        _ax.set_title("t = %.4f seconds" % t_3[step_3.value])

    show(step_3, _ax, uk=uk)


@app.cell
def demo_08():
    u0_2 = np.exp(-(x_3-0.2)**2*500)
    v0_2 = np.zeros(Nx_3)

    uk0_2 = my_dst(u0_2)
    vk0_2 = my_dst(v0_2)

    # `calc_u` above is tied to the initial condition of exercise 3, and marimo gives each cell its
    # own `uk0`, so this initial condition needs its own version of the same one-liner.
    def calc_u_2(t):
        return my_idst(uk0_2*np.cos(w*t) + vk0_2*np.sin(w*t))

    show(u0=u0_2)


@app.cell
def demo_09():
    frames_4 = 100
    t_4 = np.linspace(0, 2, frames_4)
    step_4 = slider(0, frames_4 - 1, value=0, label="Time step", show_value=True)

    md("*The slider is shown with the plot below.*")


@app.cell
def demo_10():
    # Do not edit or remove the boiler-plate code below.
    _ax = None
    if given(w):
        _fig, _ax = plt.subplots()
        _ax.plot(x_3, calc_u_2(t_4[step_4.value]))
        _ax.set_ylim(-1.2, 1.2)
        _ax.set_ylabel("Displacement u (m)")
        _ax.set_xlabel("Distance x (m)")
        _ax.set_title("t = %.4f seconds" % t_4[step_4.value])

    show(step_4, _ax, w=w)


if __name__ == "__main__":
    app.run()
