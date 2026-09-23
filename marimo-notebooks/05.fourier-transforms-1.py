import marimo

app = marimo.App(width="medium")

with app.setup:
    import marimo as mo
    import numpy as np
    import matplotlib.pyplot as plt
    from tn23015 import check_answers, given, load_data, md, print, row, show, slider


@app.cell(hide_code=True)
def head_7_01():
    mo.md(
        r"""
        ## Exercise 5.1

        Create a an array representing of an oscillation voltage in the form of a 1 Hz sine wave that runs for 10 seconds and is sampled at 100 Hz.
        """
    )


@app.cell
def ex_7_01():
    # Fill these in as you work through the exercise.
    f0 = fs = t = y = None

    # Exercise 1

    # The frequency in Hz
    # f0 = ___

    # The sampling frequency (100 Hz, 1 point per millisecond)
    # fs = ___

    # The time array (look up the help for the np.arange() function)
    # t = np.arange(___, ___, 1/___)

    # And now the y values
    #y = ....

    # Do not edit or remove the boiler-plate code below.
    show(f0=f0, fs=fs, t=t, y=y)


@app.cell(hide_code=True)
def check_7_01():
    check_answers(t=t, y=y, key="answer_7_01")


@app.cell(hide_code=True)
def sol_7_01():
    # Exercise 1

    # The frequency in Hz
    f0_sol1 = 1

    # The sampling frequency (100 Hz, 1 point per millisecond)
    fs_sol1 = 100

    # The time array (look up the help for the np.arange() function)
    t_sol1 = np.arange(0,10,1/fs_sol1)

    # And now the y values
    y_sol1 = np.sin(2*np.pi*f0_sol1*t_sol1)

    print("Signal frequency:   %g Hz" % f0_sol1)
    print("Sampling frequency: %g Hz" % fs_sol1)
    print("t: %d points from %.2f s to %.2f s, spaced %g s apart"
          % (len(t_sol1), t_sol1[0], t_sol1[-1], t_sol1[1] - t_sol1[0]))

    t_sol1 = np.copy(t_sol1)
    y_sol1 = np.copy(y_sol1)

    show()


@app.cell(hide_code=True)
def head_7_02():
    mo.md(
        r"""
        ## Exercise 5.2

        Make a plot of your sine wave (it should have 10 periods and 100 points per oscillation).
        """
    )


@app.cell
def ex_7_02():
    # Exercise 2

    # Fill this in as you work through the exercise.
    _ax = None

    # _fig, _ax = plt.subplots()
    # _ax.set_xticks(range(11));
    # _ax.grid()

    # Use lines and circles to be able to see the points
    # _ax.plot(_____,____,'o-')
    # _ax.set_ylabel("______")
    # _ax.set_xlabel("______")

    # Do not edit or remove the boiler-plate code below.
    show(_ax)


@app.cell(hide_code=True)
def sol_7_02():
    # Exercise 2

    # Use lines and circles to be able to see the points
    _fig, _ax = plt.subplots()
    _ax.plot(t_sol1,y_sol1,'o-')
    _ax.set_xticks(range(11));
    _ax.grid()

    _ax.set_ylabel("Voltage (V)")
    _ax.set_xlabel("Time (s)")

    show(_ax)


@app.cell(hide_code=True)
def head_7_03():
    mo.md(
        r"""
        ## Exercise 5.3

        Take the FFT of your sine wave using the `np.fft.fft()` function.
        Make a plot of the absolute values of the FFT vs index number of the Fourier transform array. 

        You can make plots of the values in an array vs index number by giving the `plot()` command just one array: `_ax.plot(y)` for example will plot the values of y on the y-axis and using the point number in the array as the x-axis. 

        Use plot style `'o-'` to plot both points and lines.
        """
    )


@app.cell
def ex_7_03():
    # Fill these in as you work through the exercise.
    _ax = yt = None

    # The FFT-ed array
    # yt = _____

    # _fig, _ax = plt.subplots()
    # _ax.set_ylabel("|FFT of y(t)|")
    # _ax.set_xlabel("Point number")

    # _ax.plot(np.____(yt), 'o-')

    # Do not edit or remove the boiler-plate code below.
    show(_ax, yt=yt)


@app.cell(hide_code=True)
def check_7_03():
    check_answers(yt=yt, key="answer_7_03")


@app.cell(hide_code=True)
def sol_7_03():
    # The FFT-ed array
    yt_sol3 = np.fft.fft(y_sol1)
    _fig, _ax = plt.subplots()
    _ax.plot(np.abs(yt_sol3), 'o-')
    _ax.set_ylabel("|FFT of y(t)|")
    _ax.set_xlabel("Point number")

    yt_sol3 = np.copy(yt_sol3)

    show(_ax)


@app.cell(hide_code=True)
def head_7_04():
    mo.md(
        r"""
        ## Exercise 5.4

        Modify the code below to use fftfreq to get the frequency array, and then make the same plot as the previous exercise but with frequency on the x-axis.
        """
    )


@app.cell
def ex_7_04():
    # Fill these in as you work through the exercise.
    f = None

    # f = np.fft.fftfreq(_____, ____)

    # Do not edit or remove the boiler-plate code below.
    _ax = None
    if given(f, yt):
        _fig, _ax = plt.subplots()
        _ax.plot(f, np.abs(yt), 'o-')
        _ax.set_ylabel("|FFT of y(t)|")
        _ax.set_xlabel("Frequency (Hz)")

    show(_ax, f=f, yt=yt)


@app.cell(hide_code=True)
def check_7_04():
    check_answers(f=f, key="answer_7_04")


@app.cell(hide_code=True)
def sol_7_04():
    f_sol4 = np.fft.fftfreq(len(y_sol1), 1/fs_sol1)
    _fig, _ax = plt.subplots()
    _ax.plot(f_sol4, np.abs(yt_sol3), 'o-')
    _ax.set_ylabel("|FFT of y(t)|")
    _ax.set_xlabel("Frequency (Hz)")

    f_sol4 = np.copy(f_sol4)

    show(_ax)


@app.cell
def demo_01():
    # Do not edit or remove the boiler-plate code below.
    _ax = None
    if given(f):
        _fig, _ax = plt.subplots()
        _ax.plot(f,'o-')
        _ax.set_ylabel("Frequency (Hz)")
        _ax.set_xlabel("Point number")

    show(_ax, f=f)


@app.cell
def demo_02():
    # Do not edit or remove the boiler-plate code below.
    _ax = None
    if given(f):
        _fig, _ax = plt.subplots()
        _ax.plot(np.fft.fftshift(f), 'o-')
        _ax.set_ylabel("FFT shift-ed Frequency (Hz)")
        _ax.set_xlabel("Point number");

    show(_ax, f=f)


@app.cell
def demo_03():
    # Handy trick to make this shorter to save too much typing when plotting 
    # everything with fftshift...

    s = np.fft.fftshift

    # Do not edit or remove the boiler-plate code below.
    _ax = None
    if given(f, yt):
        _fig, _ax = plt.subplots()
        _ax.plot(s(f), s(np.abs(yt)), 'o-')
        _ax.set_ylabel("FFT shift-ed Frequency")
        _ax.set_xlabel("Frequency (Hz)")

    show(_ax, f=f, yt=yt)


@app.cell(hide_code=True)
def head_7_05():
    mo.md(
        r"""
        ## Exercise 5.5

        Adjust the plot so that it zoom so you zoom in on the range from 0 to 2 Hz.
        Set x-ticks of your graph to a spacing of 0.1 by using the command `_ax.set_xticks(np.arange(0,2,0.1))`, and turn on the grid.
        """
    )


@app.cell
def ex_7_05():
    # Your code here:

    # Do not edit or remove the boiler-plate code below.
    show()


@app.cell(hide_code=True)
def sol_7_05():
    _fig, _ax = plt.subplots()
    _ax.plot(s(f_sol4), s(np.abs(yt_sol3)), 'o-')
    _ax.set_ylabel("|FFT of y(t)|")
    _ax.set_xlabel("Frequency (Hz)")
    _ax.set_xlim(0,2)
    _ax.set_xticks(np.arange(0,2,0.1));
    _ax.grid()

    show(_ax)


@app.cell
def demo_04():
    # Do not edit or remove the boiler-plate code below.
    if given(yt):
        print("Real %.2f Imaginary %.2f" % (np.real(yt[10]), np.imag(yt[10])))

    show(yt=yt)


@app.cell
def demo_05():
    # Do not edit or remove the boiler-plate code below.
    y2 = y2t = None
    if given(f0, t):
        y2 = np.cos(2*np.pi*f0*t)
        y2t = np.fft.fft(y2)
        print("Real %.2f Imaginary %.2f" % (np.real(y2t[10]), np.imag(y2t[10])))

    show(f0=f0, t=t)


@app.cell
def demo_06():
    # Angle in degrees
    ang = 55

    # Do not edit or remove the boiler-plate code below.
    y2_2 = y2t_2 = None
    if given(f0, t):
        y2_2 = np.cos(2*np.pi*f0*t + ang/180*np.pi)
        y2t_2 = np.fft.fft(y2_2)
        print("Real %.2f Imaginary %.2f" % (np.real(y2t_2[10]), np.imag(y2t_2[10])))
        print("Angle in complex plane %.2f degrees" % (np.angle(y2t_2[10])/np.pi*180))

    show(f0=f0, t=t)


@app.cell(hide_code=True)
def head_7_06():
    mo.md(
        r"""
        ## Exercise 5.6

        Use the arrays above to create a signal that consists of a sum of 1 Hz cosine wave of amplitude 1 and a 0.5 Hz sine wave with amplitude 0.5.
        Make a plot of the absolute value of the FFT.
        """
    )


@app.cell
def ex_7_06():
    # Fill these in as you work through the exercise.
    y_2 = yt_2 = None

    # Exercise 6

    # y_2 = .....
    # yt_2 = .....

    # Do not edit or remove the boiler-plate code below.
    _ax = None
    if given(y_2, yt_2, f):
        _fig, _ax = plt.subplots()
        _ax.plot(s(f), s(np.abs(yt_2)), 'o-')
        _ax.set_ylabel("np.abs(yt)")
        _ax.set_xlabel("Frequency (Hz)")
        _ax.set_xlim(0,2)
        _ax.set_xticks(np.arange(0,2,0.1));
        _ax.grid()

    show(_ax, y=y_2, yt=yt_2, f=f)


@app.cell(hide_code=True)
def check_7_06():
    check_answers(y_2=y_2, yt_2=yt_2, key="answer_7_06")


@app.cell(hide_code=True)
def sol_7_06():
    # Exercise 6

    y_sol6 = np.cos(2*np.pi*1.0*t_sol1) + 0.5*np.sin(2*np.pi*0.5*t_sol1)
    yt_sol6 = np.fft.fft(y_sol6)
    _fig, _ax = plt.subplots()
    _ax.plot(s(f_sol4), s(np.abs(yt_sol6)), 'o-')
    _ax.set_ylabel("np.abs(yt)")
    _ax.set_xlabel("Frequency (Hz)")
    _ax.set_xlim(0,2)
    _ax.set_xticks(np.arange(0,2,0.1));
    _ax.grid()

    y_sol6 = np.copy(y_sol6)
    yt_sol6 = np.copy(yt_sol6)

    show(_ax)


@app.cell
def demo_07():
    tspan=10

    # Do not edit or remove the boiler-plate code below.
    _ax = f1 = f2 = t1 = t2 = y1 = y1t = y2_3 = y2t_3 = None
    if given(fs):
        t1 = np.arange(0,tspan,1/fs)
        y1 = np.cos(2*np.pi*1.0*t1) 
        y1t = np.fft.fft(y1)
        f1 = np.fft.fftfreq(len(y1), 1/fs)

        tspan=5
        t2 = np.arange(0,tspan,1/fs)
        y2_3 = np.cos(2*np.pi*1.0*t2) 
        y2t_3 = np.fft.fft(y2_3)
        f2 = np.fft.fftfreq(len(y2_3), 1/fs)

        _fig, _ax = plt.subplots()
        _ax.plot(s(f1), s(np.abs(y1t)), 'o-', label="T = 10 s")
        _ax.plot(s(f2), s(np.abs(y2t_3)), 'o-', label="T = 5 s")
        _ax.set_ylabel("np.abs(yt)")
        _ax.set_xlabel("Frequency (Hz)")
        _ax.set_xlim(0,2)
        _ax.set_xticks(np.arange(0,2,0.1));
        _ax.grid()
        _ax.legend()

    show(_ax, fs=fs)


@app.cell(hide_code=True)
def head_7_07():
    mo.md(
        r"""
        ## Exercise 5.7

        Check that that the scaling factor we propose works and produces the same height of peak in the power spectrum for the sine wave independent of your choise of the sampling frequency or the total time trace length.
        """
    )


@app.cell
def ex_7_07():
    # Fill these in as you work through the exercise.
    f1_2 = f2_2 = power1 = power2 = t1_2 = t2_2 = y1t_2 = y2t_4 = None

    # Exercise 7

    T1 = 10

    # t1_2 = np.arange(___,___,___)

    # y1t_2 = _____
    # f1_2 = np.fft.fftfreq(___,____)
    # power1 = ____
    # t2_2 = np.arange(___,___,___)
    # y2t_4 = ___
    # f2_2 = np.fft.fftfreq(___, ___)
    # power2 = ____

    # Do not edit or remove the boiler-plate code below.
    T2 = _ax = y1_2 = y2_4 = None
    if given(f1_2, f2_2, power1, power2, t1_2, t2_2, y1t_2, y2t_4):
        y1_2 = np.cos(2*np.pi*1.0*t1_2) 

        T2 = 5

        y2_4 = np.cos(2*np.pi*1.0*t2_2) 

        _fig, _ax = plt.subplots()
        _ax.plot(s(f1_2), s(power1), 'o-', label="T = 10 s")
        _ax.plot(s(f2_2), s(power2), 'o-', label="T = 5 s")
        _ax.set_ylabel("Spectral Power ($V^2$)")
        _ax.set_xlabel("Frequency (Hz)")
        _ax.set_xlim(0,2)
        _ax.set_xticks(np.arange(0,2,0.1));
        _ax.grid()
        _ax.legend()

    show(_ax, f1=f1_2, f2=f2_2, power1=power1, power2=power2, t1=t1_2, t2=t2_2, y1t=y1t_2, y2t=y2t_4)


@app.cell(hide_code=True)
def check_7_07():
    check_answers(f1_2=f1_2, power1=power1, f2_2=f2_2, power2=power2, key="answer_7_07")


@app.cell(hide_code=True)
def sol_7_07():
    # Exercise 7

    T1_sol7 = 10

    t1_sol7 = np.arange(0,T1_sol7,1/fs_sol1)
    y1_sol7 = np.cos(2*np.pi*1.0*t1_sol7) 

    y1t_sol7 = np.fft.fft(y1_sol7)
    f1_sol7 = np.fft.fftfreq(len(y1_sol7), 1/fs_sol1)
    power1_sol7 = 2*np.abs(y1t_sol7)**2/(fs_sol1*T1_sol7)**2
    T2_sol7 = 5
    t2_sol7 = np.arange(0,T2_sol7,1/fs_sol1)
    y2_sol7 = np.cos(2*np.pi*1.0*t2_sol7) 

    y2t_sol7 = np.fft.fft(y2_sol7)
    f2_sol7 = np.fft.fftfreq(len(y2_sol7), 1/fs_sol1)
    power2_sol7 = 2*np.abs(y2t_sol7)**2/(fs_sol1*T2_sol7)**2
    _fig, _ax = plt.subplots()
    _ax.plot(s(f1_sol7), s(power1_sol7), 'o-', label="T = 10 s")
    _ax.plot(s(f2_sol7), s(power2_sol7), 'o-', label="T = 5 s")
    _ax.set_ylabel("Spectral Power ($V^2$)")
    _ax.set_xlabel("Frequency (Hz)")
    _ax.set_xlim(0,2)
    _ax.set_xticks(np.arange(0,2,0.1));
    _ax.grid()
    _ax.legend()

    f1_sol7 = np.copy(f1_sol7)
    power1_sol7 = np.copy(power1_sol7)

    f2_sol7 = np.copy(f2_sol7)
    power2_sol7 = np.copy(power2_sol7)

    show(_ax)


@app.cell(hide_code=True)
def head_7_08():
    mo.md(
        r"""
        ## Exercise 5.8

        The dataset "data.dat" for lecture 7 contains two columns.
        The second column represents a measured voltage in Volts, and the first column represents the time of the measurement in seconds.
        The data points are measured at a constant sampling rate.
        Load the dataset and make a plot voltage vs. time.

        note: The path to the data.dat file is: "data.dat"
        """
    )


@app.cell
def ex_7_08():
    # Fill these in as you work through the exercise.
    _ax = data = t_2 = v = None

    # Exercise 8

    # data = load_data(_____)
    # t_2 = data[___,___]
    # v = data[___,___]

    # _fig, _ax = plt.subplots()
    # _ax.set_ylabel("Voltage (V)")
    # _ax.set_xlabel("Time (s)")

    # _ax.plot(___,___)

    # Do not edit or remove the boiler-plate code below.
    show(_ax, data=data, t=t_2, v=v)


@app.cell(hide_code=True)
def check_7_08():
    check_answers(t_2=t_2, v=v, key="answer_7_08")


@app.cell(hide_code=True)
def sol_7_08():
    # Exercise 8

    data_sol8 = load_data("data.dat")
    t_sol8 = data_sol8[:,0]
    v_sol8 = data_sol8[:,1]

    _fig, _ax = plt.subplots()
    _ax.plot(t_sol8,v_sol8)
    _ax.set_ylabel("Voltage (V)")
    _ax.set_xlabel("Time (s)")

    t_sol8 = np.copy(t_sol8)
    v_sol8 = np.copy(v_sol8)

    show(_ax)


@app.cell(hide_code=True)
def head_7_09():
    mo.md(
        r"""
        ## Exercise 5.9

        Calculate and plot the power spectrum of the data.
        Limit your plot to positive frequencies, and plot the data with a log scale on the y-axis.
        """
    )


@app.cell
def ex_7_09():
    # Fill these in as you work through the exercise.
    T = dt = f_2 = fs_2 = power = None

    # T = ___-___
    # dt = ___ - ____
    # fs_2 = ___
    # f_2 = np.fft.fftfreq(___, ___)
    # power = _____

    # Do not edit or remove the boiler-plate code below.
    _ax = end = vt = None
    if given(T, dt, f_2, fs_2, power, v):

        # The Fourier transform of the voltage
        vt = np.fft.fft(v)

        # The total time of the trace, the time step, and the sampling frequency

        # The frequency vector, and the spectral power

        # We want only the positive frequencies. If we don't fftshift, this corresponds 
        # only to the first half of the array.
        end = int(len(f_2)/2)
        _fig, _ax = plt.subplots()
        _ax.plot(f_2[:end], power[:end])
        _ax.set_yscale('log')
        _ax.set_ylabel("Spectral Power ($V^2$)")
        _ax.set_xlabel("Frequency(Hz)")

    show(_ax, T=T, dt=dt, f=f_2, fs=fs_2, power=power, v=v)


@app.cell(hide_code=True)
def check_7_09():
    check_answers(f_2=f_2, power=power, key="answer_7_09")


@app.cell(hide_code=True)
def sol_7_09():
    # The Fourier transform of the voltage
    vt_sol9 = np.fft.fft(v_sol8)

    # The total time of the trace, the time step, and the sampling frequency
    T_sol9 = t_sol8[-1]-t_sol8[0]
    dt_sol9 = t_sol8[1] - t_sol8[0]
    fs_sol9 = 1/dt_sol9

    # The frequency vector, and the spectral power
    f_sol9 = np.fft.fftfreq(len(v_sol8), d=dt_sol9)
    power_sol9 = 2*np.abs(vt_sol9)**2/(fs_sol9*T_sol9)**2

    # We want only the positive frequencies. If we don't fftshift, this corresponds 
    # only to the first half of the array.
    end_sol9 = int(len(f_sol9)/2)
    _fig, _ax = plt.subplots()
    _ax.plot(f_sol9[:end_sol9], power_sol9[:end_sol9])
    _ax.set_yscale('log')
    _ax.set_ylabel("Spectral Power ($V^2$)")
    _ax.set_xlabel("Frequency(Hz)")

    f_sol9 = np.copy(f_sol9)
    power_sol9 = np.copy(power_sol9)

    show(_ax)


@app.cell(hide_code=True)
def head_7_10():
    mo.md(
        r"""
        ## Exercise 5.10

        : Find the frequency of the sine wave by looking for the frequency at which the peak occurs. (we would recommend just using a `for` loop for this, but there might be another way if you are clever.) Print out both the frequency of the sine wave, along with it's spectral power.
        """
    )


@app.cell
def ex_7_10():
    # Exercise 10
    # (Use `f` from the previous exercise)

    # Fill these in as you work through the exercise.
    peak_frequency = peak_power = None

    # The power is always bigger than zero, so this is a good starting point
    Pmax=-1

    # The array index corresponding the max power
    max_index = 0

    # Set `unfinished` to False once you have written the code below, so that it can run.
    unfinished = True

    if not unfinished and given(end, f_2):
        for _i in range(0,end):
            ...

            #if ____ > ____:
            #    max_index = ___
            #    Pmax = ____

        peak_frequency = f_2[max_index]
        peak_power = Pmax

        print("The frequency of the sine wave is %f Hz" % peak_frequency)
        print("The spectral power of the sine wave is is %f V^2" % peak_power)

    # Do not edit or remove the boiler-plate code below.
    show(end=end, f=f_2)


@app.cell(hide_code=True)
def check_7_10():
    check_answers(peak_frequency=peak_frequency, peak_power=peak_power, key="answer_7_10")


@app.cell(hide_code=True)
def sol_7_10():
    # Exercise 10

    # The power is always bigger than zero, so this is a good starting point
    Pmax_sol10=-1

    # The array index corresponding the max power
    max_index_sol10 = 0

    for _i in range(0,end_sol9):

        if power_sol9[_i] > Pmax_sol10:
            max_index_sol10 = _i
            Pmax_sol10 = power_sol9[_i]
    print("The frequency of the sine wave is %f Hz" % f_sol9[max_index_sol10])
    print("The spectral power of the sine wave is is %f V^2" % Pmax_sol10)

    Pmax_sol10 = Pmax_sol10

    show()


@app.cell(hide_code=True)
def head_7_11():
    mo.md(
        r"""
        ## Exercise 5.11

        Plot a sine wave on top of the data with the amplitude and frequency based on the frequency and power of the peak you found in the power spectrum.
        Set the x-limits of your plot to show the first 30 milliseconds.
        """
    )


@app.cell
def ex_7_11():
    # Fill these in as you work through the exercise.
    _ax = A = v_sine = None

    # Exercise 11

    # Calculate the amplitude based on the spectral power peak value
    # A = _____

    # Now make a sine wave vs time using the frequency and amplitude that we found
    # v_sine = _____

    # _fig, _ax = plt.subplots()
    # _ax.set_ylabel("Voltage (V)")
    # _ax.set_xlabel("Time (s)")

    # Now the plot
    # _ax.plot(___,___, label='Data')
    # _ax.plot(___,___, 'r', label="Sine wave")
    # _ax.set_xlim(____, ____)

    # Do not edit or remove the boiler-plate code below.
    if given(A, v_sine):
        print("The amplitude is %f V" % A)

    show(_ax, A=A, v_sine=v_sine)


@app.cell(hide_code=True)
def check_7_11():
    check_answers(A=A, v_sine=v_sine, key="answer_7_11")


@app.cell(hide_code=True)
def sol_7_11():
    # Exercise 11

    # Calculate the amplitude based on the spectral power peak value
    A_sol11 = np.sqrt(2*Pmax_sol10)

    # Now make a sine wave vs time using the frequency and amplitude that we found
    v_sine_sol11 = A_sol11*np.sin(2*np.pi*f_sol9[max_index_sol10]*t_sol8)

    # Now the plot
    _fig, _ax = plt.subplots()
    _ax.plot(t_sol8,v_sol8, label='Data')
    _ax.plot(t_sol8,v_sine_sol11, 'r', label="Sine wave")
    _ax.set_xlim(0,0.03)
    _ax.set_ylabel("Voltage (V)")
    _ax.set_xlabel("Time (s)")
    print("The amplitude is %f V" % A_sol11)

    A_sol11 = A_sol11
    v_sine_sol11 = np.copy(v_sine_sol11)

    show(_ax)


if __name__ == "__main__":
    app.run()
