import marimo

app = marimo.App(width="medium")

with app.setup:
    import marimo as mo
    import numpy as np
    import matplotlib.pyplot as plt
    from scipy.integrate import solve_ivp
    from scipy.signal import find_peaks
    from tn23015 import check_answers, given, load_data, md, print, row, show, slider


@app.cell(hide_code=True)
def head_12_01():
    mo.md(
        r"""
        ## Exercise 9.1

        Consider the case in which the mass is at rest and is at position $x=0$ at $t=0$, and a driving force at frequency $w = w_0$.
        Use the `solve_ivp()` routine to calculate $x(t)$ for $t$ from 0 to 200 seconds with 1000 points.
        Make a plot of your solution and discuss if it behaves in the way that you would expect.
        """
    )


@app.cell
def ex_12_01():
    # Fill these in as you work through the exercise.
    _ax = sol = x = None

    m = 1
    k = 1
    c = 0.1
    F0 = 1
    w = 1

    # I will chose y[0] = x and y[1] = v 
    def dydt(t,y):
        return None

    T = 200
    N = 1000
    t = np.linspace(0,T,N)

    x0 = 0
    v0 = 0

    # sol = solve_ivp(....)
    # t = ...
    # x = ...

    # Now a plot
    # _fig, _ax = plt.subplots()
    # ...

    # Do not edit or remove the boiler-plate code below.
    show(_ax, sol=sol, x=x, dydt=dydt)


@app.cell(hide_code=True)
def check_12_1a():
    check_answers(x=x, key="answer_12_1a")


@app.cell(hide_code=True)
def sol_12_01():
    m_sol1 = 1
    k_sol1 = 1
    c_sol1 = 0.1
    F0_sol1 = 1
    w_sol1 = 1

    # I will chose y[0] = x and y[1] = v 
    def dydt_sol1(t,y):
        x = y[0]
        v = y[1]
        return [v, -k_sol1*x/m_sol1 - c_sol1*v/m_sol1 + F0_sol1*np.cos(w_sol1*t)/m_sol1]
    T_sol1 = 200
    N_sol1 = 1000
    t_sol1 = np.linspace(0,T_sol1,N_sol1)

    x0_sol1 = 0
    v0_sol1 = 0

    sol_sol1 = solve_ivp(dydt_sol1, (0,T_sol1), (x0_sol1,v0_sol1), t_eval=t_sol1)
    t_sol1 = sol_sol1.t
    x_sol1 = sol_sol1.y[0,:]

    # Now a plot
    _fig, _ax = plt.subplots()
    _ax.plot(t_sol1,x_sol1)
    _ax.set_xlabel("t (s)")
    _ax.set_ylabel("x (m)")
    x_sol1 = np.copy(x_sol1)

    show(_ax)


@app.cell(hide_code=True)
def head_12_02():
    mo.md(
        r"""
        ## Exercise 9.2

        Find the steady state amplitude of the calculated time trace by finding the value of the amplitude of the last peak in the trace.
        For this, you can use the [`scipy.signal.find_peaks`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.find_peaks.html) routine to find all of the peaks of the oscillations.
        Make a plot of the peak values vs. time, and then extract an estimate of the steady state amplitude using the value of the last peak. 

        Does it agree with the prediction of the analytical formulas above?
        To check this, create a function `amp(w, m, c, k, F0)` (with `w` as $\omega$) to calculate the amplitude from the formula above.
        Use this to calculate the theoretically predicted amplitude based on the parameters you have used in the simulation.
        """
    )


@app.cell
def ex_12_02():
    # Fill these in as you work through the exercise.
    _ax = amp_calc = amp_theory = t_p = x_p = None

    def amp(w, m, c, k, F0):
        return None

    # peak_indices, _ = ....
    # t_p = ...
    # x_p = ...

    # A plot
    # _fig, _ax = plt.subplots()
    # ...

    # Extract the calculated amplitude
    # amp_calc = ....

    # Calculate the theory prediction
    # amp_theory = ....

    # Do not edit or remove the boiler-plate code below.
    if given(amp_calc, amp_theory, t_p, x_p, amp):
        print("Calculated steady state amplitude: ", amp_calc)
        print("Predicted steady state amplitude : ", amp_theory)

    show(_ax, amp_calc=amp_calc, amp_theory=amp_theory, t_p=t_p, x_p=x_p, amp=amp)


@app.cell(hide_code=True)
def check_12_1b():
    check_answers(amp_calc=amp_calc, amp_theory=amp_theory, key="answer_12_1b")


@app.cell(hide_code=True)
def sol_12_02():
    def amp_sol2(w, m, c, k, F0):
        gam = c/m
        w0 = np.sqrt(k/m)
        return F0/m/np.sqrt(gam**2*w**2 + (w**2 - w0**2)**2)

    # peak_indices, _ = ....
    peak_indices_sol2, _ = find_peaks(x_sol1)
    t_p_sol2 = t_sol1[peak_indices_sol2]
    x_p_sol2 = x_sol1[peak_indices_sol2]

    # A plot
    _fig, _ax = plt.subplots()
    _ax.plot(t_p_sol2, x_p_sol2)

    # Extract the calculated amplitude
    amp_calc_sol2 = x_p_sol2[-1]

    # Calculate the theory prediction
    amp_theory_sol2 = amp_sol2(1, m_sol1, c_sol1, k_sol1, F0_sol1)
    print("Calculated steady state amplitude: ", amp_calc_sol2)
    print("Predicted steady state amplitude : ", amp_theory_sol2)

    amp_calc_sol2 = amp_calc_sol2
    amp_theory_sol2 = amp_theory_sol2

    show(_ax)


@app.cell(hide_code=True)
def head_12_03():
    mo.md(
        r"""
        ## Exercise 9.3

        Calculate the power spectrum of the second half of the calculated DDHO response trace calculated in 1(a).
        Make a plot of the power spectrum with a logarithmic scale on the y-axis, and find the frequency in the data corresponding to the highest spectral power. 

        In your power spectrum, keep only the part of the spectrum at positive frequencies.
        """
    )


@app.cell
def ex_12_03():
    # Fill these in as you work through the exercise.
    _ax = Tss = f = fmax = fmax_expected = max_index = xss = None

    # Pick out the second half of the trace to analyze for the steady state
    # xss = ...
    # Tss = ...
    # power = ...
    # f = ...

    # Now keep only the positive frequencies
    end = int(N/4)

    # fmax = ...
    # fmax_expected = ...

    # Fill in the commented lines below, but leave the rest of this block in place.
    f_pow = power = None
    if given(Tss, f, fmax, fmax_expected, max_index, xss):
        f_pow = f[0:end]
        power = power[0:end]

        # Make a plot
        # _fig, _ax = plt.subplots()
        # ...

        # Find the frequency of the peak

        print("Calculated frequency:  %.5f Hz (%.5f Rad/s)" %(f[max_index], f[max_index]*2*np.pi))
        print("Theoretical frequency: %.5f Hz (%.5f Rad/s)" % (1/2/np.pi, 1))

    show(_ax, Tss=Tss, f=f, fmax=fmax, fmax_expected=fmax_expected, max_index=max_index, xss=xss)


@app.cell(hide_code=True)
def check_12_1c():
    check_answers(power=power, f_pow=f_pow, fmax=fmax, key="answer_12_1c")


@app.cell(hide_code=True)
def sol_12_03():
    # Pick out the second half of the trace to analyze for the steady state
    xss_sol3 = x_sol1[int(N_sol1/2):]
    Tss_sol3 = T_sol1/2
    print(Tss_sol3)
    fs_sol3 = 1/(t_sol1[1]-t_sol1[0])
    xss_t_sol3 = np.fft.fft(xss_sol3)
    power_sol3 = 2*np.abs(xss_t_sol3)**2/(fs_sol3*Tss_sol3)**2
    f_sol3 = np.fft.fftfreq(len(xss_sol3), 1/fs_sol3)

    # Now keep only the positive frequencies
    end_sol3 = int(N_sol1/4)
    f_pow_sol3 = f_sol3[0:end_sol3]
    power_sol3 = power_sol3[0:end_sol3]

    # Make a plot
    _fig, _ax = plt.subplots()
    _ax.plot(f_pow_sol3,power_sol3)
    _ax.set_ylabel("Power spectrum of $x$ (m$^2$)")
    _ax.set_xlabel("Frequency (Hz)")
    _ax.set_yscale('log')

    # Find the frequency of the peak
    pmax_sol3 = 0;
    max_index_sol3 = 0;
    for _i in range(len(f_pow_sol3)):
        if power_sol3[_i] > pmax_sol3:
            pmax_sol3 = power_sol3[_i]
            max_index_sol3 = _i
    fmax_sol3 = f_sol3[max_index_sol3]
    print("Calculated frequency:  %.5f Hz (%.5f Rad/s)" %(f_sol3[max_index_sol3], f_sol3[max_index_sol3]*2*np.pi))
    print("Theoretical frequency: %.5f Hz (%.5f Rad/s)" % (1/2/np.pi, 1))

    power_sol3 = power_sol3
    f_pow_sol3 = f_pow_sol3
    fmax_sol3 = fmax_sol3

    show(_ax)


@app.cell(hide_code=True)
def head_12_04():
    mo.md(
        r"""
        ## Exercise 9.4

        Perform the calculation from Exercise 9.1, part (a), with an initial condition $x(0) = 30$.
        Make a plot of $x(t)$.
        Write a function `find_ss_amp(x)` to find the steady state amplitude as we did above in 1(b) by finding the peak value of the last peak.
        Use this function to find the steady state amplitude and show that this is the same (or at least close) to the value for $x(0) = 0$.
        """
    )


@app.cell
def ex_12_04():
    # Fill these in as you work through the exercise.
    _ax = sol_2 = t_2 = x_2 = None

    def find_ss_amp(x):
        return None

    x0_2 = 30
    v0_2 = 0
    # sol_2 = solve_ivp(....)
    # t_2 = ...
    # x_2 = ...

    # Make a plot
    # _fig, _ax = plt.subplots()
    # ...

    # Do not edit or remove the boiler-plate code below.
    if given(sol_2, t_2, x_2, find_ss_amp):
        print("Calculated steady state amplitude: ", find_ss_amp(x_2))

    show(_ax, sol=sol_2, t=t_2, x=x_2, find_ss_amp=find_ss_amp)


@app.cell(hide_code=True)
def check_12_1d():
    check_answers(x_2=x_2, key="answer_12_1d")


@app.cell(hide_code=True)
def sol_12_04():
    def find_ss_amp_sol4(x):
        peak_indices, _ = find_peaks(x)
        return x[peak_indices[-1]]
    x0_sol4 = 30
    v0_sol4 = 0
    sol_sol4 = solve_ivp(dydt_sol1, (0,T_sol1), (x0_sol4,v0_sol4), t_eval=t_sol1)
    t_sol4 = sol_sol4.t
    x_sol4 = sol_sol4.y[0,:]

    # Make a plot
    _fig, _ax = plt.subplots()
    _ax.plot(t_sol4,x_sol4)
    _ax.set_xlabel("Time (s)")
    _ax.set_xlabel("Position (m)")
    print("Calculated steady state amplitude: ", find_ss_amp_sol4(x_sol4))

    x_sol4 = np.copy(x_sol4)

    show(_ax)


@app.cell
def demo_01():
    # Do not edit or remove the boiler-plate code below.
    if given(x_2):
        x_2.shape

    show(x=x_2)


@app.cell(hide_code=True)
def head_12_05():
    mo.md(
        r"""
        ## Exercise 9.5

        Consider a ball with mass $m = 0.1$ kg thrown upwards into the air with an initial velocity of 1 m/s.
        Use `solve_ivp()` to calculate how long it takes for the ball to reach the ground again.
        Assume that the $g = 9.81$ m/s$^2$.
        For the numerical integration, you need to pick a time endpoint that will be longer than the time it will take for the ball to come back down.
        A time limit of 100 seconds should probably be fine.
        """
    )


@app.cell
def ex_12_05():
    # Fill these in as you work through the exercise.
    sol_3 = None

    m_2=0.1
    g = 9.81 

    # y[0] is height (which I will call "x"), y[1] is velocity ("v")
    def myevent(t,y):
        return None

    def dydt_2(t,y):
        return None

    vi = 1
    # sol_3 = solve_ivp(....)

    # Do not edit or remove the boiler-plate code below.
    t_f = None
    if given(sol_3, myevent, dydt_2):
        t_f = sol_3.t_events[0][0]

        print("An initial velocity of 1 m/s gave a total time of %f seconds" % t_f)

    show(sol=sol_3, myevent=myevent, dydt=dydt_2)


@app.cell(hide_code=True)
def check_12_2a():
    check_answers(t_f=t_f, key="answer_12_2a")


@app.cell(hide_code=True)
def sol_12_05():
    m_sol5=0.1
    g_sol5 = 9.81 

    # y[0] is height (which I will call "x"), y[1] is velocity ("v")
    def myevent_sol5(t,y):
        return y[0]
    myevent_sol5.terminal = True
    myevent_sol5.direction = -1
    def dydt_sol5(t,y):
        x = y[0]
        v = y[1]
        return [v, -g_sol5]
    vi_sol5 = 1
    sol_sol5 = solve_ivp(dydt_sol5, (0,100), [0,vi_sol5], events=myevent_sol5)
    t_f_sol5 = sol_sol5.t_events[0][0]

    print("An initial velocity of 1 m/s gave a total time of %f seconds" % t_f_sol5)

    t_f_sol5 = t_f_sol5

    show()


@app.cell(hide_code=True)
def head_12_06():
    mo.md(
        r"""
        ## Exercise 9.6

        Implement binary search to find the initial velocity needed to have $t_f = 10$ seconds with a target accuracy of 1 ms.
        For your initial search range, choose $v_i$ = 1 m/s and 100 m/s.
        Compare to what you would expect theoretically from the acceleration due to gravity with no air resistance.
        """
    )


@app.cell
def ex_12_06():
    # Fill these in as you work through the exercise.
    vi_2 = vi_theory = None

    def find_tf(vi):
        return None

    v1 = 1

    # vi_2 = ...
    # vi_theory = ...

    # Do not edit or remove the boiler-plate code below.
    t1 = t2 = target = v2 = None
    if given(vi_2, vi_theory, find_tf):
        t1 = find_tf(v1)
        v2 = 200
        t2 = find_tf(v2)
        target = 1e-3

        # while np.abs(t2-t1) > target:

        print(vi_2)
        print(vi_theory)

    show(vi=vi_2, vi_theory=vi_theory, find_tf=find_tf)


@app.cell(hide_code=True)
def check_12_2b():
    check_answers(vi_2=vi_2, vi_theory=vi_theory, key="answer_12_2b")


@app.cell(hide_code=True)
def sol_12_06():
    def find_tf_sol6(vi):
        sol = solve_ivp(dydt_sol5, (0,100), [0,vi], events=myevent_sol5)
        return sol.t_events[0][0]
    v1_sol6 = 1
    t1_sol6 = find_tf_sol6(v1_sol6)
    v2_sol6 = 200
    t2_sol6 = find_tf_sol6(v2_sol6)
    target_sol6 = 1e-3

    # while np.abs(t2-t1) > target:
    while np.abs(t2_sol6-t1_sol6) > target_sol6:
        vp_sol6 = (v1_sol6+v2_sol6)/2
        tp_sol6 = find_tf_sol6(vp_sol6)
        if (t1_sol6-10)*(tp_sol6-10) > 0:
            v1_sol6 = vp_sol6
            t1_sol6 = tp_sol6
        else:
            v2_sol6 = vp_sol6
            t2_sol6 = tp_sol6
    vi_sol6 = (v1_sol6+v2_sol6)/2
    vi_theory_sol6 = 9.81*5
    print(vi_sol6)
    print(vi_theory_sol6)

    vi_sol6 = vi_sol6
    vi_theory_sol6 = vi_theory_sol6

    show()


@app.cell(hide_code=True)
def head_12_07():
    mo.md(
        r"""
        ## Exercise 9.7

        We will now add air resistance to our calculation.
        To make life simple, we will assume that the [drag coefficient](https://en.wikipedia.org/wiki/Drag_coefficient) of our ball results in a friction force with the magnitude:

        $$
        |F_f| = Cv^2
        $$

        For a 3 cm diameter sphere, Gary's estimate of the constant $C$ in this equation (based on the formulas on wikipedia) is that it has a value on the order of $C = 10^{-3}$ Ns$^2$/m$^2$.
        Since the force always opposes the direction of the velocity, we have to somehow account for its sign before incorporating it into an equation of motion.
        One way to do this is as follows:

        $$
        F_f = - \frac{Cv^3}{|v|}
        $$

        Repeat question 2(a) but now including air resistance in your calculation.

        Before you start: do you think it will take less time or more time for the ball to fall for the same velocity? 

        On the one hand, when falling, the ball will move more slowly because the air resistance is holding it back.
        On the other hand, the ball will not go as high with air resistance. 

        (Give your `dydt` function with air resistance a different name so we can compare the two in the next question...)
        """
    )


@app.cell
def ex_12_07():
    # Fill these in as you work through the exercise.
    sol_4 = None

    your_guess = "comes back in less time /OR/ takes more time to come back (delete one!)"

    g_2 = 9.81 
    m_3 = 0.1
    C = 1e-3

    # y[0] is height (which I will call "x"), y[1] is velocity ("v")
    def myevent_2(t,y):
        return None

    def dydt2(t,y):
        return None

    vi_3 = 1

    # sol_4 = solve_ivp(....)

    # Do not edit or remove the boiler-plate code below.
    t_f_2 = None
    if given(sol_4, myevent_2, dydt2):
        t_f_2 = sol_4.t_events[0][0]

        print("An initial velocity of 1 m/s gave a total time of %f seconds" % t_f_2)

    show(sol=sol_4, myevent=myevent_2, dydt2=dydt2)


@app.cell(hide_code=True)
def check_12_2c():
    check_answers(t_f_2=t_f_2, key="answer_12_2c")


@app.cell(hide_code=True)
def sol_12_07():
    your_guess_sol7 = "comes back in less time /OR/ takes more time to come back (delete one!)"

    g_sol7 = 9.81 
    m_sol7 = 0.1
    C_sol7 = 1e-3

    # y[0] is height (which I will call "x"), y[1] is velocity ("v")
    def myevent_sol7(t,y):
        return y[0]
    myevent_sol7.terminal = True
    myevent_sol7.direction = -1
    def dydt2_sol7(t,y):
        x = y[0]
        v = y[1]
        return [v, -g_sol7 - C_sol7*v**3/np.abs(v)/m_sol7]
    vi_sol7 = 1
    sol_sol7 = solve_ivp(dydt2_sol7, (0,100), [0,vi_sol7], events=myevent_sol7)
    t_f_sol7 = sol_sol7.t_events[0][0]

    print("An initial velocity of 1 m/s gave a total time of %f seconds" % t_f_sol7)

    t_f_sol7 = t_f_sol7

    show()


@app.cell(hide_code=True)
def head_12_08():
    mo.md(
        r"""
        ## Exercise 9.8

        Make a calculation of the two times as a function of the initial velocity, with $v_i$ varying from 1 m/s to 200 m/s (720 km/h!) with 100 points.
        Make a plot of $t_f$ vs $v_i$ for the two cases.
        """
    )


@app.cell
def ex_12_08():
    Ni = 200
    vi_4 = np.linspace(1,200,Ni)
    tf1 = np.empty(Ni)
    tf2 = np.empty(Ni)

    # Set `unfinished` to False once you have written the code below, so that it can run.
    unfinished = True

    if not unfinished:
        for _i in range(Ni):
            ...

            # ... dydt

        for _i in range(Ni):
            ...

            # ... dydt2

        # Make some plots

    # Do not edit or remove the boiler-plate code below.
    show()


@app.cell(hide_code=True)
def check_12_2d():
    check_answers(vi_4=vi_4, tf1=tf1, tf2=tf2, key="answer_12_2d", when=not unfinished)


@app.cell(hide_code=True)
def sol_12_08():
    Ni_sol8 = 200
    vi_sol8 = np.linspace(1,200,Ni_sol8)
    tf1_sol8 = np.empty(Ni_sol8)
    tf2_sol8 = np.empty(Ni_sol8)

    for _i in range(Ni_sol8):
        sol_sol8 = solve_ivp(dydt_sol5, (0,100), [0,vi_sol8[_i]], events=myevent_sol7)
        tf1_sol8[_i] = sol_sol8.t_events[0][0]
    for _i in range(Ni_sol8):
        sol_sol8 = solve_ivp(dydt2_sol7, (0,100), [0,vi_sol8[_i]], events=myevent_sol7)
        tf2_sol8[_i] = sol_sol8.t_events[0][0]

    # Make some plots
    _fig, _ax = plt.subplots()
    _ax.plot(vi_sol8, tf1_sol8, label="Frictionless")
    _ax.plot(vi_sol8, tf2_sol8, label="With air resistance")
    _ax.set_xlabel("Initial velocity v$_i$ (m/s)")
    _ax.set_ylabel("Total time t$_f$ (s)")
    vi_sol8 = vi_sol8.copy()
    tf1_sol8 = tf1_sol8.copy()
    tf2_sol8 = tf2_sol8.copy()

    show(_ax)


@app.cell(hide_code=True)
def head_12_09():
    mo.md(
        r"""
        ## Exercise 9.9

        Calculate the initial velocity required to achieve $t_f$ of 10 seconds including air resistance.
        """
    )


@app.cell
def ex_12_09():
    # Fill these in as you work through the exercise.
    vi_5 = None

    def find_tf2(vi):
        return None

    v1_2 = 1

    # vi_5 = ...

    # Do not edit or remove the boiler-plate code below.
    t1_2 = t2_2 = target_2 = v2_2 = None
    if given(vi_5, find_tf2):
        t1_2 = find_tf2(v1_2)
        v2_2 = 200
        t2_2 = find_tf2(v2_2)
        target_2 = 1e-3

        # while np.abs(...) > target:

        print(vi_5)

    show(vi=vi_5, find_tf2=find_tf2)


@app.cell(hide_code=True)
def check_12_2e():
    check_answers(vi_5=vi_5, key="answer_12_2e")


@app.cell(hide_code=True)
def sol_12_09():
    def find_tf2_sol9(vi):
        sol = solve_ivp(dydt2_sol7, (0,100), [0,vi], events=myevent_sol7)
        return sol.t_events[0][0]
    v1_sol9 = 1
    t1_sol9 = find_tf2_sol9(v1_sol9)
    v2_sol9 = 200
    t2_sol9 = find_tf2_sol9(v2_sol9)
    target_sol9 = 1e-3

    # while np.abs(...) > target:
    while np.abs(t2_sol9-t1_sol9) > target_sol9:
        vp_sol9 = (v1_sol9+v2_sol9)/2
        tp_sol9 = find_tf2_sol9(vp_sol9)
        if (t1_sol9-10)*(tp_sol9-10) > 0:
            v1_sol9 = vp_sol9
            t1_sol9 = tp_sol9
        else:
            v2_sol9 = vp_sol9
            t2_sol9 = tp_sol9
    vi_sol9 = (v1_sol9+v2_sol9)/2
    vi_t_sol9 = 9.81*5
    print(vi_sol9)

    vi_sol9 = vi_sol9

    show()


@app.cell(hide_code=True)
def head_12_10():
    mo.md(
        r"""
        ## Exercise 9.10

        Including air resistance, does the ball spend more time on the upwards trajectory, on the downward tragectory, or does it spend the same amount of time going up as it does going down?

        Use the `solve_ivp()` routine to calculate the time going up and the time going down for the initial velocity you found in 2(e). 

        _Hint:_ an easy way to do this is to create an additional `terminal = False` event function that checks when the velocity crosses zero!
        """
    )


@app.cell
def ex_12_10():
    # Fill these in as you work through the exercise.
    sol_5 = None

    # y[0] is height (which I will call "x"), y[1] is velocity ("v")
    def myevent_3(t,y):
        return None

    def myevent2(t,y):
        return None

    # sol_5 = solve_ivp(..., events=[myevent2, myevent])

    # Do not edit or remove the boiler-plate code below.
    t1_3 = t2_3 = t_down = None
    if given(sol_5, myevent_3, myevent2):
        t1_3 = sol_5.t_events[0][0]
        t2_3 = sol_5.t_events[1][0]
        t_down = t2_3-t1_3

        print("Time up:   %f" % t1_3)
        print("Time down: %f" % (t2_3-t1_3))

    show(sol=sol_5, myevent=myevent_3, myevent2=myevent2)


@app.cell(hide_code=True)
def check_12_2f():
    check_answers(t1_3=t1_3, t_down=t_down, key="answer_12_2f")


@app.cell(hide_code=True)
def sol_12_10():
    # y[0] is height (which I will call "x"), y[1] is velocity ("v")
    def myevent_sol10(t,y):
         return y[0]
    myevent_sol10.terminal = True
    myevent_sol10.direction = -1
    def myevent2_sol10(t,y):
        return y[1]
    myevent2_sol10.terminal = False
    myevent2_sol10.direction = -1
    sol_sol10 = solve_ivp(dydt2_sol7, (0,200), [0,vi_sol9], events=[myevent2_sol10, myevent_sol10])
    t1_sol10 = sol_sol10.t_events[0][0]
    t2_sol10 = sol_sol10.t_events[1][0]
    t_down_sol10 = t2_sol10-t1_sol10

    print("Time up:   %f" % t1_sol10)
    print("Time down: %f" % (t2_sol10-t1_sol10))

    t1_sol10 = t1_sol10
    t_down_sol10 = t_down_sol10

    show()


if __name__ == "__main__":
    app.run()
