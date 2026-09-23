import marimo

app = marimo.App(width="medium")

with app.setup:
    import marimo as mo
    import numpy as np
    import matplotlib.pyplot as plt
    from tn23015 import check_answers, given, load_data, md, print, row, show, slider


@app.cell
def demo_01():
    # Notebook code 
    tau = 1
    _fig, _ax = plt.subplots(figsize=(12,3))
    t = np.linspace(-5,5,1000)
    h = np.exp(-t/tau)*(t>=0)
    _ax.plot(t,h)
    _ax.set_ylabel("Impulse response h(t)")
    _ax.set_xlabel("Time");

    _ax


@app.cell
def demo_02():
    # Notebook code 
    fig, ax = plt.subplots(figsize=(12,3))
    vin = np.random.normal(size=len(t))*0.05
    plt.plot(t,vin,'.', color='grey', label=r"$V_{in}$")
    plt.plot(t,np.exp(t)*(t<0),'r', label=r"Impulse response")
    plt.fill_between(t,np.exp(t)*(t<0), alpha=0.1, color='r')
    plt.xlabel("Relative Time")
    ax.get_yaxis().set_visible(False)
    plt.legend()

    plt.title('Illustration of the convolution integral')


@app.cell
def demo_03():
    # Notebook code 
    tau_2 = 1
    w = np.geomspace(1e-3,1e3, 100)
    h_2 = 1/(1+1j*w*tau_2)

    _fig, _axs = plt.subplots(1, 2, figsize=(12,4))
    _ax = _axs[0]
    _ax.plot(w,np.abs(h_2))
    _ax.set_xlabel("$\omega$")
    _ax.set_ylabel("$|h(\omega)|$")
    _ax.set_xscale('log')
    _ax.set_yscale('log')
    _ax.grid()

    _ax = _axs[1]
    _ax.plot(w, np.angle(h_2)/np.pi*180)
    _ax.set_xscale('log')
    _ax.set_xlabel("$\omega$")
    _ax.set_ylabel(r"Phase angle of $\tilde h$ (degrees)")
    _ax.grid()
    _ax.set_yticks(np.arange(-90,1,15));

    _fig


@app.cell(hide_code=True)
def head_8_01():
    mo.md(
        r"""
        ## Exercise 6.1

        Make a square voltage pulse:  

        $$
        V(t) = 
        \begin{cases}
        0 &  \text{for } 0 <t <=50 \text{ s}\\
        1 &  \text{for } 50 <t <=100 \text{ s} \\
        0 &  \text{for } 100 <t <=150 \text{ s}
        \end{cases}
        $$

        Your pulse should include 1000 points
        """
    )


@app.cell
def ex_8_01():
    # Fill these in as you work through the exercise.
    t_2 = v = None

    # t_2 = np.linspace(...)

    # If you are well versed with vectorized comparison operators, you
    # can create v in one line! Otherwise, a for loop is OK too...
    # v = ....

    # Do not edit or remove the boiler-plate code below.
    _ax = None
    if given(t_2, v):
        _fig, _ax = plt.subplots()
        _ax.plot(t_2,v)
        _ax.set_ylabel("Voltage (V)")
        _ax.set_xlabel("Time (s)")

    show(_ax, t=t_2, v=v)


@app.cell(hide_code=True)
def check_8_1a():
    check_answers(t_2=t_2, v=v, key="answer_8_1a")


@app.cell(hide_code=True)
def sol_8_01():
    t_sol1 = np.linspace(0,150,1000)

    # If you are well versed with vectorized comparison operators, you
    # can create v in one line! Otherwise, a for loop is OK too...
    v_sol1 = (t_sol1 > 50) * (t_sol1 <= 100)
    _fig, _ax = plt.subplots()
    _ax.plot(t_sol1,v_sol1)
    _ax.set_ylabel("Voltage (V)")
    _ax.set_xlabel("Time (s)")

    t_sol1 = np.copy(t_sol1)
    v_sol1 = np.copy(v_sol1)

    show(_ax)


@app.cell(hide_code=True)
def head_8_02():
    mo.md(
        r"""
        ## Exercise 6.2

        Write a function to use a FFT to apply a low-pass filter to the data.
        You filter should have a time constant $\tau = 5$ seconds.
        The cell includes code to make a plot of the original data along with the filtered data. 

        _Note:_ When using `np.fft.ifft()`, it will return a complex-valued array even if the data has no imaginary component (as it should if you have done your filtering correctly).
        For plotting, you will need to use `np.real()` to convert your array to real values before plotting (if you forget, matplotlib will give you a warning messgae).
        You should therefore have your `low_pass` function return only the real-valued part of the filtered data.
        """
    )


@app.cell
def ex_8_02():
    def low_pass(v, tau, dt):
        return None

    # Do not edit or remove the boiler-plate code below.
    _ax = vfilt = None
    if given(t_2, v, low_pass):
        vfilt = low_pass(v, 5, t_2[1]-t_2[0])

        _fig, _ax = plt.subplots()
        _ax.plot(t_2,v, label="$V_{in}$")
        _ax.set_ylabel("Voltage (V)")
        _ax.set_xlabel("Time (s)")
        _ax.plot(t_2, vfilt, label="$V_{out}$");
        _ax.legend()

    show(_ax, t=t_2, v=v, low_pass=low_pass)


@app.cell(hide_code=True)
def check_8_1b():
    check_answers(vfilt=vfilt, key="answer_8_1b")


@app.cell(hide_code=True)
def sol_8_02():
    def low_pass_sol2(v, tau, dt):
        v_t = np.fft.fft(v)
        f = np.fft.fftfreq(len(v), d=dt)
        h = 1/(1+1j*2*np.pi*f*tau)
        vfilt_t = v_t*h

        # When we invert the FFT, we should have a real number
        # But since the np.fft.fft() function is designed to 
        # also work with complex valued data, we need to take 
        # the real part. 
        vfilt = np.real(np.fft.ifft(vfilt_t))
        return vfilt
    vfilt_sol2 = low_pass_sol2(v_sol1, 5, t_sol1[1]-t_sol1[0])

    _fig, _ax = plt.subplots()
    _ax.plot(t_sol1,v_sol1, label="$V_{in}$")
    _ax.set_ylabel("Voltage (V)")
    _ax.set_xlabel("Time (s)")
    _ax.plot(t_sol1, vfilt_sol2, label="$V_{out}$");
    _ax.legend()

    vfilt_sol2 = np.copy(vfilt_sol2)

    show(_ax)


@app.cell(hide_code=True)
def head_8_03():
    mo.md(
        r"""
        ## Exercise 6.3

        Use your function to apply a low pass filter with $\tau = 20$ seconds.
        As usual, your plot should have appropriate axis labels, and a legend.
        """
    )


@app.cell
def ex_8_03():
    # Fill these in as you work through the exercise.
    _ax = vfilt_2 = None

    # vfilt_2 = low_pass(....)
    # _fig, _ax = plt.subplots()
    # _ax.plot(....)
    # .....

    # Do not edit or remove the boiler-plate code below.
    show(_ax, vfilt=vfilt_2)


@app.cell(hide_code=True)
def check_8_1c():
    check_answers(vfilt_2=vfilt_2, key="answer_8_1c")


@app.cell(hide_code=True)
def sol_8_03():
    # _ax.plot(....)
    vfilt_sol3 = low_pass_sol2(v_sol1, 20, t_sol1[1]-t_sol1[0])
    _fig, _ax = plt.subplots()
    _ax.plot(t_sol1,v_sol1, label="$V_{in}$")
    _ax.set_ylabel("Voltage (V)")
    _ax.set_xlabel("Time (s)")
    _ax.plot(t_sol1, vfilt_sol3, label="$V_{out}$");
    _ax.legend()
    vfilt_sol3 = np.copy(vfilt_sol3)

    show(_ax)


@app.cell(hide_code=True)
def head_8_04():
    mo.md(
        r"""
        ## Exercise 6.4

        We can solve the problem we saw in Exercise 6.1, part (c), by using zero-padding of the array during the Fourier transform.
        Read the documentation page of [`np.fft.fft`](https://numpy.org/doc/stable/reference/generated/numpy.fft.fft.html) to learn how to do this.

        Write a new version of the low pass function `low_pass2()` function, this time padding this signal you are filtering with as many points as it already contains.
        If you do this correctly, it will eliminate the "boundary" effects from your FFT we saw above.
        The ploting code to make a plot of your low-pass filtered data after filtering with the new function.
        """
    )


@app.cell
def ex_8_04():
    def low_pass2(v, tau, dt):
        return None

    # Do not edit or remove the boiler-plate code below.
    _ax = vfilt2 = None
    if given(t_2, v, low_pass2):
        vfilt2 = low_pass2(v, 20, t_2[1]-t_2[0])
        _fig, _ax = plt.subplots()
        _ax.plot(t_2,v, label="$V_{in}$")
        _ax.set_ylabel("Voltage (V)")
        _ax.set_xlabel("Time (s)")
        _ax.plot(t_2, vfilt2, label="$V_{out}$");
        _ax.legend()

    show(_ax, t=t_2, v=v, low_pass2=low_pass2)


@app.cell(hide_code=True)
def check_8_1d():
    check_answers(vfilt2=vfilt2, key="answer_8_1d")


@app.cell(hide_code=True)
def sol_8_04():
    def low_pass2_sol4(v, tau, dt):
        n = 2*len(v)
        v_t = np.fft.fft(v, n=n)
        f = np.fft.fftfreq(n, d=dt)
        h = 1/(1+1j*2*np.pi*f*tau)
        vfilt_t = v_t*h
        vfilt = np.real(np.fft.ifft(vfilt_t, n=n))
        return vfilt[0:len(v)]
    vfilt2_sol4 = low_pass2_sol4(v_sol1, 20, t_sol1[1]-t_sol1[0])
    _fig, _ax = plt.subplots()
    _ax.plot(t_sol1,v_sol1, label="$V_{in}$")
    _ax.set_ylabel("Voltage (V)")
    _ax.set_xlabel("Time (s)")
    _ax.plot(t_sol1, vfilt2_sol4, label="$V_{out}$");
    _ax.legend()

    vfilt2_sol4 = np.copy(vfilt2_sol4)

    show(_ax)


@app.cell
def demo_04():
    N = 2000

    # Lower case letters correspond to the 1D array of coordinates in the two directions
    x = np.linspace(-N/2,N/2,N+1)
    y = np.linspace(-N/2,N/2,N+1)

    # Upper case letters correspont to the 2D matrices containing the X or Y coordinates
    X, Y = np.meshgrid(x, y)

    # This we need to tell python what the range of the image plot are
    extent = [x[0],x[-1], y[0], y[-1]]

    # We will use the subplots command to make two plots beside each other
    _fig, _axs = plt.subplots(1, 2, figsize=(10,3.5))
    _ax = _axs[0]
    _im1 = _ax.imshow(X,origin='lower',extent=extent)
    _ax.set_xlabel("X")
    _ax.set_ylabel("Y")
    _fig.colorbar(_im1)
    _ax = _axs[1]
    _im2 = _ax.imshow(Y,origin='lower', extent=extent)
    _ax.set_xlabel("X")
    _ax.set_ylabel("Y")
    _fig.colorbar(_im2)
    _fig.tight_layout()

    _fig


@app.cell(hide_code=True)
def head_8_06():
    mo.md(
        r"""
        ## Exercise 6.5

        Use your X and Y matrices to make a mask matrix M in which all points should be 1, except for points with a radius of $r > 50$ points from the center of the array, which should be zero.
        The code will make two plots of your mask: one of the full matrix, and one zoomed into the range of a 200x200 pixel zoom at the center of the image.
        The mask value of 1 will indicate where the light will be transmitted, and a mask value of 0 will indicate where the light will be blocked, and so this corresponds to the diffraction through a circular aperture.
        """
    )


@app.cell
def ex_8_06():
    # Fill these in as you work through the exercise.
    _fig = M = None

    # It seems like this is magic, but using the right matrices, it does just work!
    # M =  _____ < 50

    exts = [x[0], x[-1], y[-1], y[0]]

    # Do not edit or remove the boiler-plate code below.
    M_zoom = end = exts_zoom = start = zoom = None
    if given(M):
        _fig, _axs = plt.subplots(1, 2, figsize=(10,3.5))

        # The full plot
        _ax = _axs[0]
        _ax.imshow(M, extent=exts)
        _ax.set_xlabel("x (nm)")
        _ax.set_ylabel("y (nm)")

        # The zoom
        _ax = _axs[1]
        zoom = 200
        start = int(len(x)/2-zoom/2)
        end = start + zoom
        M_zoom = M[start:end,start:end]
        exts_zoom = [x[start], x[end], y[start], y[end]]
        _ax.imshow(M_zoom, extent=exts_zoom)
        _ax.set_xlabel("x")
        _ax.set_ylabel("y")

    show(_fig, M=M)


@app.cell(hide_code=True)
def check_8_2b():
    check_answers(M=M, key="answer_8_2b")


@app.cell(hide_code=True)
def sol_8_06():
    # It seems like this is magic, but using the right matrices, it does just work!
    M_sol5 =  np.sqrt(X**2 + Y**2) < 50
    _fig, _axs = plt.subplots(1, 2, figsize=(10,3.5))

    # The full plot
    _ax = _axs[0]
    exts_sol5 = [x[0], x[-1], y[-1], y[0]]
    _ax.imshow(M_sol5, extent=exts_sol5)
    _ax.set_xlabel("x (nm)")
    _ax.set_ylabel("y (nm)")

    # The zoom
    _ax = _axs[1]
    zoom_sol5 = 200
    start_sol5 = int(len(x)/2-zoom_sol5/2)
    end_sol5 = start_sol5 + zoom_sol5
    M_zoom_sol5 = M_sol5[start_sol5:end_sol5,start_sol5:end_sol5]
    exts_zoom_sol5 = [x[start_sol5], x[end_sol5], y[start_sol5], y[end_sol5]]
    _ax.imshow(M_zoom_sol5, extent=exts_zoom_sol5)
    _ax.set_xlabel("x")
    _ax.set_ylabel("y")

    M_sol5 = np.copy(M_sol5)

    show(_fig)


@app.cell(hide_code=True)
def head_8_07():
    mo.md(
        r"""
        ## Exercise 6.6

        Now calculate and plot the diffraction pattern from your mask.
        Plot a zoom in of the diffraction pattern around the center 200 pixels of the image.
        Your axis labels on your diffraction pattern should correspond to wavenumbers with the appropriate units.
        (Hint: make sure to use fftshift, which also works on 2D arrays!)
        """
    )


@app.cell
def ex_8_07():
    # Fill these in as you work through the exercise.
    diffraction_pattern = end_2 = extent_zoom = k_max = k_zoom = start_2 = None

    # diffraction_pattern = ....
    # start_2=....
    # end_2=....
    # k_max = ....
    # k_zoom = k_max * zoom / len(x)
    # extent_zoom = [ , , , ]

    # Fill in the commented lines below, but leave the rest of this block in place.
    Mt = _ax = zoom_2 = None
    if given(diffraction_pattern, end_2, extent_zoom, k_max, k_zoom, start_2, M):

        # First, we take the FFT of the mask
        Mt = np.fft.fft2(M)

        # Now translate this into a diffraction pattern

        # Calculate the zoom 
        zoom_2=100

        # Extents: this one we have to think about carefully! 
        # A good trick: what is the largest wave number k_max? 
        # Your full image will then run from -k_max to k_max. From this,
        # you can work out the extents 

        # Now the 
        _fig, _ax = plt.subplots()
        _im1 = _ax.imshow(diffraction_pattern, extent=exts)

        # _ax.set_xlabel(...)
        # _ax.set_ylabel(...)
        _fig.colorbar(_im1)

    show(
        _ax,
        diffraction_pattern=diffraction_pattern,
        end=end_2,
        extent_zoom=extent_zoom,
        k_max=k_max,
        k_zoom=k_zoom,
        start=start_2,
        M=M,
    )


@app.cell(hide_code=True)
def check_8_2c():
    check_answers(
        diffraction_pattern=diffraction_pattern,
        k_max=k_max,
        k_zoom=k_zoom,
        extent_zoom=extent_zoom,
        key="answer_8_2c",
    )


@app.cell(hide_code=True)
def sol_8_07():
    # First, we take the FFT of the mask
    Mt_sol6 = np.fft.fft2(M_sol5)

    # Now translate this into a diffraction pattern
    diffraction_pattern_sol6 = np.abs(np.fft.fftshift(Mt_sol6))**2

    # Calculate the zoom 
    zoom_sol6=100
    start_sol6 = int(len(x)/2-zoom_sol6/2)
    end_sol6 = start_sol6+zoom_sol6

    # Extents: this one we have to think about carefully! 
    # A good trick: what is the largest wave number k_max? 
    # Your full image will then run from -k_max to k_max. From this,
    # you can work out the extents 

    # k_zoom_sol6 = k_max * zoom / len(x)
    # extent_zoom_sol6 = [ , , , ]
    k_max_sol6 = 1/(x[1]-x[0])/2 # the nyquist frequency
    k_zoom_sol6 = k_max_sol6 * zoom_sol6 / len(x)
    extent_zoom_sol6 = [ -k_zoom_sol6 , k_zoom_sol6, -k_zoom_sol6, k_zoom_sol6]

    # Now the 
    _fig, _ax = plt.subplots()
    _im1 = _ax.imshow(diffraction_pattern_sol6, extent=exts_sol5)

    # _ax.set_xlabel(...)
    # _ax.set_ylabel(...)
    _ax.set_xlabel("k$_x$ (nm$^{-1}$)")
    _ax.set_ylabel("k$_y$ (nm$^{-1})$")
    _fig.colorbar(_im1)

    diffraction_pattern_sol6 = np.copy(diffraction_pattern_sol6)
    k_max_sol6 = k_max_sol6
    k_zoom_sol6 = k_zoom_sol6
    extent_zoom_sol6 = np.copy(extent_zoom_sol6)

    show(_ax)


@app.cell(hide_code=True)
def head_8_08():
    mo.md(
        r"""
        ## Exercise 6.7

        Here, you will make an interactive zoom of your diffraction pattern.
        Fill in the code below to
        show the central `zoom.value` pixels of the image.

        Two sliders let you adjust the zoom and the maximum of the colormap (in logarithmic
        intervals).
        They are defined in their own cell — a marimo UI element has to be *read* by a
        different cell from the one that creates it, and that is what makes the image redraw by itself
        as you drag.

        It is quite cool to zoom out and take the vmax to the lowest value in the array, particularly if
        you make the figure very big by using `plt.subplots(figsize=(10, 10))` (or some size that fills
        your screen nicely).
        """
    )


@app.cell
def ex_8_08():
    # Sliders for the zoom level and the colour scale. They are displayed with the image below.
    zoom_3 = slider(20, 1000, step=10, value=1000, label="Zoom (pixels)")
    v_index = slider(1, 19, step=1, value=19, label="Colour scale")
    controls = row(zoom_3, v_index)

    # Do not edit or remove the boiler-plate code below.
    show(md("*The sliders are shown with the image below.*"))


@app.cell
def ex_8_08b():
    # Fill these in as you work through the exercise.
    end_3 = exts_2 = k_zoom_2 = start_3 = None

    # To really be able to tweak the colormap over a large range,
    # we will make an array of maximum colour values that is geometrically spaced
    N_2 = 20
    vmax_array = np.geomspace(1e1, 6e7, N_2)
    vmax = vmax_array[v_index.value]

    # Show the central `zoom_3.value` pixels of the diffraction pattern.
    # start_3 = ...
    # end_3 = ...
    # k_zoom_2 = ...
    # exts_2 = ...

    # Do not edit or remove the boiler-plate code below.
    _ax = None
    if given(end_3, exts_2, k_zoom_2, start_3):
        _fig, _ax = plt.subplots(figsize=(8, 8))
        _ax.imshow(diffraction_pattern[start_3:end_3, start_3:end_3], extent=exts_2, vmax=vmax)
        _ax.set_xlabel("k$_x$ (nm$^{-1}$)")
        _ax.set_ylabel("k$_y$ (nm$^{-1}$)")

    show(controls, _ax, end=end_3, exts=exts_2, k_zoom=k_zoom_2, start=start_3)


@app.cell(hide_code=True)
def sol_8_08():
    # Sliders for the zoom level and the colour scale. They are displayed with the image below.
    zoom_sol7 = slider(20, 1000, step=10, value=1000, label="Zoom (pixels)")
    v_index_sol7 = slider(1, 19, step=1, value=19, label="Colour scale")
    controls_sol7 = row(zoom_sol7, v_index_sol7)

    show(md("*The sliders are shown with the image below.*"))


@app.cell(hide_code=True)
def sol_8_08b():
    # To really be able to tweak the colormap over a large range,
    # we will make an array of maximum colour values that is geometrically spaced
    N_sol8 = 20
    vmax_array_sol8 = np.geomspace(1e1, 6e7, N_sol8)
    vmax_sol8 = vmax_array_sol8[v_index_sol7.value]

    start_sol8 = int(len(x) / 2 - zoom_sol7.value / 2)
    end_sol8 = start_sol8 + zoom_sol7.value
    k_zoom_sol8 = k_max_sol6 * zoom_sol7.value / len(x)
    exts_sol8 = [-k_zoom_sol8, k_zoom_sol8, -k_zoom_sol8, k_zoom_sol8]

    _fig, _ax = plt.subplots(figsize=(8, 8))
    _im = _ax.imshow(
        diffraction_pattern_sol6[start_sol8:end_sol8, start_sol8:end_sol8],
        extent=exts_sol8,
        vmax=vmax_sol8,
    )
    _ax.set_xlabel("k$_x$ (nm$^{-1}$)")
    _ax.set_ylabel("k$_y$ (nm$^{-1}$)")
    _fig.colorbar(_im)

    show(controls_sol7, _ax)


if __name__ == "__main__":
    app.run()
