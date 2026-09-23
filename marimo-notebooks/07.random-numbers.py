import marimo

app = marimo.App(width="medium")

with app.setup:
    import marimo as mo
    import numpy as np
    import matplotlib.pyplot as plt
    from tn23015 import check_answers, given, load_data, md, print, row, show, slider


@app.cell
def demo_01():
    x=np.random.rand(5)
    print(x)

    show()


@app.cell
def demo_02():
    np.random.seed(0)
    x_2=np.random.rand(5)
    print(x_2)

    show()


@app.cell
def demo_03():
    np.random.seed(0)
    x_3=np.random.rand(5)
    print(x_3)
    y=np.random.rand(5)
    print(y)

    show()


@app.cell(hide_code=True)
def head_9_01():
    mo.md(
        r"""
        ## Exercise 7.1

        Create a uniformly distributed random variable between bounds 5 and 8 and draw $N$=100 samples from it, as an array. 
        * Determine the mean of the generated samples and store this to variable `meanx`
        * Determine the variance and store this to variable `varx` (in this case the biased variance with $N$ in the denominator)
        * Check that the mean and variance numbers approximately match the theoretical values as shown above, increase $N$ to see convergence to the theoretical values. 

        Note that you can generate the uniformly distributed random numbers in two ways: from the `uniform()` function and from the standard `rand()` function (with uniform distribution between 0 and 1).
        The latter has to be shifted and scaled to match the interval $a, b$.
        Try them both!
        Also note that you can use numpy functions for computing the mean and variance
        """
    )


@app.cell
def ex_9_01():
    # Fill these in as you work through the exercise.
    meanx = varx = None

    # Use seed to fix random number generation
    np.random.seed(0)

    # Define parameters
    a=5
    b=8
    N=100

    # meanx = ...
    # varx = ...

    # Do not edit or remove the boiler-plate code below.
    show(meanx=meanx, varx=varx)


@app.cell(hide_code=True)
def check_9_01():
    check_answers(meanx=meanx, varx=varx, key="answer_9_01")


@app.cell(hide_code=True)
def sol_9_01():
    # Use seed to fix random number generation
    np.random.seed(0)

    # Define parameters
    a_sol1=5
    b_sol1=8
    N_sol1=100

    # Create random variable
    #x_sol1=a+(b-a)*np.random.rand(N)
    x_sol1=np.random.uniform(a_sol1, b_sol1, N_sol1)

    # Determine statistical properties
    meanx_sol1=np.mean(x_sol1)
    meanxth_sol1=0.5*(a_sol1+b_sol1)
    print('The measured mean is ' + str(meanx_sol1) + ', which is close to the theoretical value of ' + str(meanxth_sol1))
    varx_sol1=np.var(x_sol1, ddof=0)
    varxth_sol1=(1/12)*(b_sol1-a_sol1)**2
    print('The measured variance is ' + str(varx_sol1) + ', which is close to the theoretical value of ' + str(varxth_sol1))
    meanx_sol1 = np.copy(meanx_sol1)
    varx_sol1 = np.copy(varx_sol1)

    show()


@app.cell(hide_code=True)
def head_9_02():
    mo.md(
        r"""
        ## Exercise 7.2

        Create a Gaussian distributed random variable with mean $\mu=10$ and standard deviation of $\sigma=7$ and take $N=100$ samples from it, as an array.
        * Determine the mean of the generated samples and store this to variable `meanxn`
        * Determine the variance and store this to variable `varxn` (in this case the biased variance with $N$ in the denominator)
        * Check that the mean and variance numbers match the theoretical values , increase $N$ to see convergence to the theoretical values. 

        Note that you can generate the Gaussian distributed random numbers with mean $\mu$ and variance $\sigma^2$ in two ways: from the `normal()` function and from the standard normal distribution`randn()` function (with zero mean and variance 1).
        The latter has to be shifted and scaled to match the arbitrary Gaussian.
        Try them both!
        """
    )


@app.cell
def ex_9_02():
    # Fill these in as you work through the exercise.
    meanxn = varxn = None

    # Use seed to fix random number generation
    np.random.seed(0)

    # Define parameters
    mu=10
    sigma=7
    N_2=100

    # meanxn = ...
    # varxn = ...

    # Do not edit or remove the boiler-plate code below.
    show(meanxn=meanxn, varxn=varxn)


@app.cell(hide_code=True)
def check_9_02():
    check_answers(meanxn=meanxn, varxn=varxn, key="answer_9_02")


@app.cell(hide_code=True)
def sol_9_02():
    # Use seed to fix random number generation
    np.random.seed(0)

    # Define parameters
    mu_sol2=10
    sigma_sol2=7
    N_sol2=100

    # Create random variable
    x_sol2=mu_sol2+sigma_sol2*np.random.randn(N_sol2)
    #x_sol2=np.random.normal(mu,sigma,N)

    # Determine statistical properties
    meanxn_sol2=np.mean(x_sol2)
    meanxth_sol2=mu_sol2
    print('The measured mean is ' + str(meanxn_sol2) + ', which is close to the theoretical value of ' + str(meanxth_sol2))
    varxn_sol2=np.var(x_sol2, ddof=0)
    varxth_sol2=sigma_sol2**2
    print('The measured variance is ' + str(varxn_sol2) + ', which is close to the theoretical value of ' + str(varxth_sol2))
    meanxn_sol2 = np.copy(meanxn_sol2)
    varxn_sol2 = np.copy(varxn_sol2)

    show()


@app.cell(hide_code=True)
def head_9_03():
    mo.md(
        r"""
        ## Exercise 7.3

        Generate $N=100$ uniformly distributed random numbers between -1 and 1 for the $x$-coordinates. Do the same for the $y$-coordinates.<br>
        * Plot the random numbers in the $x$-$y$ plane, add a circle according to the given code
        * Make a for loop and iterate over all $N$ points
        * Check for every point whether it is within the unit circle ($x^2+y^2<1$), if so add 1 to a variable that counts the number of points in the unit circle
        * Calculate $\pi$ by dividing the number of points inside the circle by $N$ and multiply by the area of the square surrounding the unit circle, store your value of $\pi$ in the variable `pi_est`.
        """
    )


@app.cell
def ex_9_03():
    # Fill these in as you work through the exercise.
    pi_est = None

    # Use seed to fix random number generation
    np.random.seed(0)

    # Plot circle
    angle = np.linspace(0, 2*np.pi, 100)
    _fig, _ax = plt.subplots()
    _ax.plot(np.cos(angle), np.sin(angle), '--r')

    npoints=100

    # pi_est = ...

    _ax.plot(x_3,y,'ob')
    _ax.set_xlabel('X-coordinate')
    _ax.set_ylabel('Y-coordinate')
    _ax.axis('square')
    _ax.set_xlim([-1.0,1.0])
    _ax.set_ylim([-1.0, 1.0])

    # Do not edit or remove the boiler-plate code below.
    show(_ax, pi_est=pi_est)


@app.cell(hide_code=True)
def check_9_03():
    check_answers(pi_est=pi_est, key="answer_9_03")


@app.cell(hide_code=True)
def sol_9_03():
    # Use seed to fix random number generation
    np.random.seed(0)

    # Plot circle
    angle_sol3 = np.linspace(0, 2*np.pi, 100)
    _fig, _ax = plt.subplots()
    _ax.plot(np.cos(angle_sol3), np.sin(angle_sol3), '--r')

    npoints_sol3=100
    x_sol3=-1+2*np.random.rand(npoints_sol3)
    y_sol3=-1+2*np.random.rand(npoints_sol3)

    cnt_sol3=0
    for _j in range(npoints_sol3):
        if x_sol3[_j]**2 + y_sol3[_j]**2 < 1:
            cnt_sol3 +=1

    # the vectorized version using Boolean indexing        
    # inpoints=x*x+y*y<1  # determine indices for point inside the circle
    # cnt_sol3=float(sum(inpoints))

    pi_est_sol3=4*cnt_sol3/npoints_sol3

    print('The value of pi is '+"{:.10f}".format(pi_est_sol3))
    _ax.plot(x_sol3,y_sol3,'ob')
    _ax.set_xlabel('X-coordinate')
    _ax.set_ylabel('Y-coordinate')
    _ax.axis('square')
    _ax.set_xlim([-1.0,1.0])
    _ax.set_ylim([-1.0, 1.0])

    pi_est_sol3 = np.copy(pi_est_sol3)

    show(_ax)


@app.cell
def demo_04():
    y_2 = np.array([ 0, 2, 4, 8, 16, 32])
    index = np.array([2, 3, 4])
    print(y_2[index])

    show()


@app.cell
def demo_05():
    a_2=2>3
    print(a_2)

    show()


@app.cell(hide_code=True)
def head_9_03b():
    mo.md(
        r"""
        ## Exercise 7.4

        Generate an array `x` of 100 random numbers between 0 and 10 and count using Boolean indexing how many numbers are larger than 5.<br>

        Method 1:
        * Make a Boolean value array `y` for the condition `x>5`
        * Print the variable `y`, the values are Boolean, i.e., `True` or `False`
        * Extract from array `x` the elements that match the condition with `x[y]`
        * Calculate the length of the extracted array
        """
    )


@app.cell
def ex_9_03b():
    # Use seed to fix random number generation
    np.random.seed(0)

    N_3=100
    x_4=10*np.random.rand(N_3)

    # Do not edit or remove the boiler-plate code below.
    show()


@app.cell(hide_code=True)
def sol_9_03b():
    # Use seed to fix random number generation
    np.random.seed(0)

    N_sol4=100
    x_sol4=10*np.random.rand(N_sol4)

    # Method 1: index the array with the Boolean array, then count what comes back
    y_sol4 = (x_sol4 > 5)
    z_sol4 = x_sol4[y_sol4]

    print("y is a %s array of %d Booleans, %d of them True"
          % (y_sol4.dtype, len(y_sol4), y_sol4.sum()))
    print("x[y] keeps only those entries, so it has %d of the original %d"
          % (len(z_sol4), N_sol4))
    print("Numbers larger than 5: %d out of %d" % (len(z_sol4), N_sol4))

    show()


@app.cell(hide_code=True)
def head_9_03c():
    mo.md(
        r"""
        ## Exercise 7.5

        Method 2
        * Make a Boolean variable `y` for the condition `x>5`
        * Take the sum of `y`
        """
    )


@app.cell
def ex_9_03c():
    # Your code here

    # Do not edit or remove the boiler-plate code below.
    show()


@app.cell(hide_code=True)
def sol_9_03c():
    # Method 2: summing the Boolean array directly, with True counting as 1
    y_sol5 = (x_sol4 > 5)
    z_sol5 = sum(y_sol5)

    print("Summing the Booleans gives %d, the same count as method 1" % z_sol5)
    print("This works because True counts as 1 and False as 0 in arithmetic")

    show()


@app.cell(hide_code=True)
def head_9_05():
    mo.md(
        r"""
        ## Exercise 7.6

        In this exercise we are going to calculate the mass of a 3D sphere with linearly increasing density.
        This problem is quite challenging to do analytically, but with Monte Carlo integration it is relatively easy.<br>

        Let's first start with the simple problem of determining the mass of a sphere with uniform density $\rho_0=1.5$ kg/m$^3$.
        The sphere has a radius of 1 meter, and we initially integrate it with $N=100$ points. 
        * Generate an array of $N$ random numbers for the $x$, $y$, and $z$ coordinates. Make sure that all points lie in a cube enclosing the sphere 
        * Generate an index function. This is an array that is equal to 1 for points inside the sphere and 0 outside the sphere. Use the Boolean indexing technique you learned above to do this without using a for loop.
        * Calculate the mass by applying the mean value method, store your mass as variable `msphere`.
        * Do you get a mass of 2$\pi$ kg? And if you increase $N$?
        """
    )


@app.cell
def ex_9_05():
    # Fill these in as you work through the exercise.
    msphere = x_5 = y_3 = z = None

    # Use seed to fix random number generation
    np.random.seed(0)

    # use the following code structure to calculate the x,y,z random points
    # x_5=...np.random.rand(...)...
    # y_3=...np.random.rand(...)...
    # z=...np.random.rand(...)...

    # msphere = ...

    # Do not edit or remove the boiler-plate code below.
    show(msphere=msphere, x=x_5, y=y_3, z=z)


@app.cell(hide_code=True)
def check_9_05():
    check_answers(msphere=msphere, key="answer_9_05")


@app.cell(hide_code=True)
def sol_9_05():
    # Use seed to fix random number generation
    np.random.seed(0)

    # Definition of parameters
    R_sol6=1        # radius of the sphere in m
    rho0_sol6=1.5   # density of the sphere in kg/m^3
    V_sol6=(2*R_sol6)**3 # reference volume of the volume enclosed by the sphere
    N_sol6=100

    # Generation of random points inside the volume
    x_sol6=2*R_sol6*np.random.rand(N_sol6)-R_sol6 # define random numbers in enclosing box
    y_sol6=2*R_sol6*np.random.rand(N_sol6)-R_sol6
    z_sol6=2*R_sol6*np.random.rand(N_sol6)-R_sol6

    # Generation of index function
    inpoints_sol6=x_sol6*x_sol6+y_sol6*y_sol6+z_sol6*z_sol6<R_sol6**2  # determine indices for point inside

    # Calculation of totalmass
    msphere_sol6=(V_sol6/N_sol6)*sum(rho0_sol6*inpoints_sol6)

    print('The mass of the sphere is '+ str(msphere_sol6) + ' kg')

    # for reference the mass is
    # mass=rho0*(4/3)*np.pi*R**3
    # use the following code structure to calculate the x,y,z random points

    msphere_sol6 = np.copy(msphere_sol6)

    show()


@app.cell(hide_code=True)
def head_9_06():
    mo.md(
        r"""
        ## Exercise 7.7

        Now we make it a bit more difficult by adjusting the code.
        Consider a density that is a linear function of the radius according to $\rho(r)=\rho_0 r$.<br>

        Calculate the mass of the sphere for the case of the linear increasing density using the methodology developed in Exercise 7.6 and the same parameters.
        Store your calculated mass for $N=100$ as variable `mspherelin`.
        With some effort we can calculate the analytical answer as 1.5$\pi$, however, as you can see the Monte Carlo integration is a lot easier to implement.
        Increase $N$ to see whether your answer gets close to the analytical answer.
        """
    )


@app.cell
def ex_9_06():
    # Fill these in as you work through the exercise.
    mspherelin = None

    # Use seed to fix random number generation
    np.random.seed(0)

    # mspherelin = ...

    # Do not edit or remove the boiler-plate code below.
    show(mspherelin=mspherelin)


@app.cell(hide_code=True)
def check_9_06():
    check_answers(mspherelin=mspherelin, key="answer_9_06")


@app.cell(hide_code=True)
def sol_9_06():
    # Use seed to fix random number generation
    np.random.seed(0)

    # Defnition of parameters
    R_sol7=1        # radius of the sphere in m
    rho0_sol7=1.5    # density of the sphere in kg/m^3
    V_sol7=(2*R_sol7)**3 # reference volume of the volume enclosed by the sphere
    N_sol7=100

    # Generation of random points inside the volume
    x_sol7=2*R_sol7*np.random.rand(N_sol7)-R_sol7 # define random numbers in enclosing box
    y_sol7=2*R_sol7*np.random.rand(N_sol7)-R_sol7
    z_sol7=2*R_sol7*np.random.rand(N_sol7)-R_sol7

    # Generation of index function
    inpoints_sol7=x_sol7*x_sol7+y_sol7*y_sol7+z_sol7*z_sol7<R_sol7**2  # determine indices for point inside

    # Calculation of totalmass
    mspherelin_sol7=(V_sol7/N_sol7)*sum(rho0_sol7*np.sqrt(x_sol7*x_sol7 + y_sol7*y_sol7 +z_sol7*z_sol7)*inpoints_sol7)

    print('The mass of the sphere is '+ str(mspherelin_sol7) + ' kg')

    # The analytical answer
    # print(1.5*np.pi)
    mspherelin_sol7 = np.copy(mspherelin_sol7)

    show()


if __name__ == "__main__":
    app.run()
