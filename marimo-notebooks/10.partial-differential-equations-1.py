import marimo

app = marimo.App(width="medium")

with app.setup:
    import marimo as mo
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib import colors
    from time import time
    from tn23015 import check_answers, given, load_data, md, print, row, show, slider


@app.cell
def demo_01():
    def visualise(array, normalisation=0.5, line_cut_y=80, autoscale=False):
        fig, axes = plt.subplots(1, 2, figsize=(14,6))

        lims = [0, len(array[0])-1] # Assumes square matrix
        zlims = [np.min(array), np.max(array)]
        assert line_cut_y < lims[-1], "The line_cut_y that you ask for should be less than the size of the array"
        assert isinstance(line_cut_y, int), "The line_cut_y that you ask for should be a whole number (integer)"

        norm = colors.PowerNorm(gamma=normalisation, vmin=np.min(array), vmax=np.max(array))
        im = axes[0].imshow(array, cmap='RdBu_r', origin='lower',aspect='auto', norm=norm)
        axes[0].hlines(y=line_cut_y, xmin=0, xmax=len(array[0]), color='black', linestyle='--')
        plt.colorbar(im, ax=axes[0], cmap='RbBu_r', label='z')

        axes[0].set_ylim(*lims)
        axes[0].set_xlim(*lims)
        axes[0].set_xlabel('x')
        axes[0].set_ylabel('y')

        axes[1].plot(array[line_cut_y], color='black', linestyle='--')
        axes[1].set_xlabel('x')
        axes[1].set_ylabel('z')
        if autoscale:
            axes[1].relim()
            axes[1].autoscale_view()
        else:
            axes[1].set_ylim(*zlims)
            axes[1].autoscale_view()
        return fig

    show()


@app.cell(hide_code=True)
def head_13_01():
    mo.md(
        r"""
        ## Exercise 10.1

        Consider a square box with the left, right, and bottom sides grounded, and the top side set to a voltage of 1V.
        In our finite element technique, we will divide the two-dimensional $x-y$ space into an $M \times M$ grid, illustrated here for $M = 11$: 

        ![](https://raw.githubusercontent.com/curiousbeams/lecture-tn23015-computational-science/main/figures/box.png)

        The outer boundary points are fixed by the boundary condition, and are not updated when we are solving for $\phi$: instead they remain at a fixed potential.
        We need to keep track of this so that we do not accidentally update any points that should correspond to a fixed external potential. 

        Note that our update equation above does not depend on the spacing between our grid points: the Laplace equation has the same solution regardless if the size of the box in 1 meter of 1 nm!
        For the Laplace equation, we do not have to keep track what the spacing between our points is.

        Your task is to fill in the code below to use Jacobi's method to calculate $\phi(x,y)$.

        During your calculation, keep track of the absolute value of the largest change `delta_max` in $\phi$ during that iteration in a list so that we can plot later the convergence as a function of the number of iterations.
        Use a threshold of 0.1 mV for $\phi$.

        To benchmark the computational speed of our simulation, we will keep track of the running time and the code speed.
        """
    )


@app.cell
def ex_13_01():
    target_accuracy = 1e-4

    # The size of the simulation grid
    M = 101
    phi = np.zeros([M,M])
    phi[-1,1:-1] = 1

    # A second matrix for storing the values calculated for the next
    # iteration
    phinew = phi.copy()

    # A matrix to keep track of which points in our simulation 
    # are fixed voltages. In this case, it is only the boundaries
    # of the simulation
    fixed = np.empty([M,M]) 
    fixed[:,:] = False # interior points are not fixed, they should be iterated
    fixed[0,:] = True
    fixed[-1,:] = True
    fixed[:,0] = True
    fixed[:,-1] = True

    # Keep track of the biggest update. 
    # When this is smaller than our target accuracy, 
    # we will stop iterating
    delta_max = 1
    delta_max_list = []

    t1 = time()

    # Set `unfinished` to False once you have written the code below, so that it can run.
    unfinished = True

    t2 = None
    if not unfinished:
        while delta_max > target_accuracy:
            for _i in range(M):
                for _j in range(M):
                    if fixed[_i,_j]:
                        ...

                        #phinew[i,j] = ...
                    else:
                        ...

                        #phinew[i,j] = ....
            #delta_max =....
            delta_max_list.append(delta_max)
            print("N_iter %d delta_max %e\r" % (len(delta_max_list), delta_max), end='')

            # Now that we're done, phi becomes phinew. A sneaky trick: if we swap the two, 
            # we don't need to copy the whole array! 
            phi,phinew = phinew,phi
        t2 = time()

        print("\nTotal running time: %.2f min" % ((t2-t1)/60))
        print("Code speed: %.1f iterations per second" %(len(delta_max_list)/(t2-t1)))

    # Do not edit or remove the boiler-plate code below.
    show()


@app.cell(hide_code=True)
def check_13_1a():
    check_answers(phi=phi, delta_max_list=delta_max_list, key="answer_13_1a", when=not unfinished)


@app.cell(hide_code=True)
def sol_13_01():
    target_accuracy_sol1 = 1e-4

    # The size of the simulation grid
    M_sol1 = 101
    phi_sol1 = np.zeros([M_sol1,M_sol1])
    phi_sol1[-1,1:-1] = 1

    # A second matrix for storing the values calculated for the next
    # iteration
    phinew_sol1 = phi_sol1.copy()

    # A matrix to keep track of which points in our simulation 
    # are fixed voltages. In this case, it is only the boundaries
    # of the simulation
    fixed_sol1 = np.empty([M_sol1,M_sol1]) 
    fixed_sol1[:,:] = False # interior points are not fixed, they should be iterated
    fixed_sol1[0,:] = True
    fixed_sol1[-1,:] = True
    fixed_sol1[:,0] = True
    fixed_sol1[:,-1] = True

    # Keep track of the biggest update. 
    # When this is smaller than our target accuracy, 
    # we will stop iterating
    delta_max_sol1 = 1
    delta_max_list_sol1 = []

    t1_sol1 = time()
    while delta_max_sol1 > target_accuracy_sol1:
        for _i in range(M_sol1):
            for _j in range(M_sol1):
                if fixed_sol1[_i,_j]:
                    phinew_sol1[_i,_j] = phi_sol1[_i,_j]
                else:
                    phinew_sol1[_i,_j] = (phi_sol1[_i+1,_j] + phi_sol1[_i-1,_j] + phi_sol1[_i,_j+1] + phi_sol1[_i,_j-1])/4
        delta_max_sol1 = np.max(np.abs(phinew_sol1-phi_sol1))
        delta_max_list_sol1.append(delta_max_sol1)
        print("N_iter %d delta_max %e\r" % (len(delta_max_list_sol1), delta_max_sol1), end='')

        # Now that we're done, phi becomes phinew. A sneaky trick: if we swap the two, 
        # we don't need to copy the whole array! 
        phi_sol1,phinew_sol1 = phinew_sol1,phi_sol1
    t2_sol1 = time()

    print("\nTotal running time: %.2f min" % ((t2_sol1-t1_sol1)/60))
    print("Code speed: %.1f iterations per second" %(len(delta_max_list_sol1)/(t2_sol1-t1_sol1)))

    phi_sol1 = phi_sol1.copy()
    delta_max_list_sol1 = delta_max_list_sol1.copy()

    show()


@app.cell
def demo_02():
    # Do not edit or remove the boiler-plate code below.
    fig = None
    if given(phi):
        fig = visualise(phi, normalisation=0.5, line_cut_y=80)
        fig.show()

    show(phi=phi)


@app.cell(hide_code=True)
def head_13_02():
    mo.md(
        r"""
        ## Exercise 10.2

        Make a plot of `delta_max` as a function of the iteration number.
        The y-axis should be a log scale.
        As always, your plot should have appropriate labels with units where applicable.
        """
    )


@app.cell
def ex_13_02():
    # Your code here:

    # Do not edit or remove the boiler-plate code below.
    show()


@app.cell(hide_code=True)
def sol_13_02():
    _fig, _ax = plt.subplots()
    _ax.plot(delta_max_list_sol1)
    _ax.set_yscale('log')
    _ax.set_ylabel("$\Delta \phi_{max}$ (V)")
    _ax.set_xlabel("Iteration number")

    show(_ax)


@app.cell(hide_code=True)
def head_13_03():
    mo.md(
        r"""
        ## Exercise 10.3

        Perform the calculation of Exercise 10.1, part (a), with the Gauss-Seidel method.
        """
    )


@app.cell
def ex_13_03():
    target_accuracy_2 = 1e-4

    M_2 = 101
    phi_2 = np.zeros([M_2,M_2])
    delta = phi_2.copy()
    phi_2[-1,1:-1] = 1

    # A matrix to keep track of which points in our simulation 
    # are fixed voltages. In this case, it is only the boundaries
    # of the simulation
    fixed_2 = np.empty([M_2,M_2])
    fixed_2[:,:] = False
    fixed_2[0,:] = True
    fixed_2[-1,:] = True
    fixed_2[:,0] = True
    fixed_2[:,-1] = True

    # Keep track of the biggest update. 
    # When this is smaller than our target accuracy, 
    # we will stop iterating
    delta_max_2 = 1
    delta_max_list_2 = []

    t1_2 = time()

    # Set `unfinished_2` to False once you have written the code below, so that it can run.
    unfinished_2 = True

    t2_2 = None
    if not unfinished_2:
        while delta_max_2 > target_accuracy_2:
            for _i in range(M_2):
                for _j in range(M_2):
                    if not fixed_2[_i,_j]:
                        ...

                        #delta[i,j] = ...
            delta_max_2 = np.max(np.abs(delta))
            delta_max_list_2.append(delta_max_2)
            print("N_iter %d delta_max %e\r" % (len(delta_max_list_2), delta_max_2), end='')   
        t2_2 = time()
        print("\nTotal running time: %.2f min" % ((t2_2-t1_2)/60))
        print("Code speed: %.1f iterations per second" %(len(delta_max_list_2)/(t2_2-t1_2)))

    # Do not edit or remove the boiler-plate code below.
    show()


@app.cell(hide_code=True)
def check_13_2a():
    check_answers(phi_2=phi_2, delta_max_list_2=delta_max_list_2, key="answer_13_2a", when=not unfinished_2)


@app.cell(hide_code=True)
def sol_13_03():
    target_accuracy_sol3 = 1e-4

    M_sol3 = 101
    phi_sol3 = np.zeros([M_sol3,M_sol3])
    delta_sol3 = phi_sol3.copy()
    phi_sol3[-1,1:-1] = 1

    # A matrix to keep track of which points in our simulation 
    # are fixed voltages. In this case, it is only the boundaries
    # of the simulation
    fixed_sol3 = np.empty([M_sol3,M_sol3])
    fixed_sol3[:,:] = False
    fixed_sol3[0,:] = True
    fixed_sol3[-1,:] = True
    fixed_sol3[:,0] = True
    fixed_sol3[:,-1] = True

    # Keep track of the biggest update. 
    # When this is smaller than our target accuracy, 
    # we will stop iterating
    delta_max_sol3 = 1
    delta_max_list_sol3 = []

    t1_sol3 = time()
    while delta_max_sol3 > target_accuracy_sol3:
        for _i in range(M_sol3):
            for _j in range(M_sol3):
                if not fixed_sol3[_i,_j]:
                    delta_sol3[_i,_j] = (phi_sol3[_i+1,_j] + phi_sol3[_i-1,_j] + phi_sol3[_i,_j+1] + phi_sol3[_i,_j-1])/4 - phi_sol3[_i,_j]
                    phi_sol3[_i,_j] += delta_sol3[_i,_j]
        delta_max_sol3 = np.max(np.abs(delta_sol3))
        delta_max_list_sol3.append(delta_max_sol3)
        print("N_iter %d delta_max %e\r" % (len(delta_max_list_sol3), delta_max_sol3), end='')   
    t2_sol3 = time()
    print("\nTotal running time: %.2f min" % ((t2_sol3-t1_sol3)/60))
    print("Code speed: %.1f iterations per second" %(len(delta_max_list_sol3)/(t2_sol3-t1_sol3)))

    phi_sol3 = phi_sol3.copy()
    delta_max_list_sol3 = delta_max_list_sol3.copy()

    show()


@app.cell
def demo_03():
    # Do not edit or remove the boiler-plate code below.
    fig_2 = None
    if given(phi_2):

        # Notebook code
        fig_2 = visualise(phi_2, normalisation=0.5, line_cut_y=80)
        fig_2.show()

    show(phi_2=phi_2)


@app.cell(hide_code=True)
def head_13_04():
    mo.md(
        r"""
        ## Exercise 10.4

        Plot `delta_max` vs iteration number for both the Jacobi method and the Gauss-Seidel method.
        Use a logscale for the y-axis.
        """
    )


@app.cell
def ex_13_04():
    # Your code here:

    # Do not edit or remove the boiler-plate code below.
    show()


@app.cell(hide_code=True)
def sol_13_04():
    _fig, _ax = plt.subplots()
    _ax.plot(delta_max_list_sol1, label="Jacobi")
    _ax.plot(delta_max_list_sol3, label="Gauss-Seidel")
    _ax.set_yscale('log')
    _ax.set_ylabel("$\Delta \phi_{max}$ (V)")
    _ax.set_xlabel("Iteration number")
    _ax.legend()

    show(_ax)


@app.cell(hide_code=True)
def head_13_05():
    mo.md(
        r"""
        ## Exercise 10.5

        Modify your code from 2(a) to implement SOR.
        Use an SOR parameter of 1.95, which works well by trial-and-error.
        """
    )


@app.cell
def ex_13_05():
    # Fill these in as you work through the exercise.
    delta_max_list_3 = phi_3 = None

    SOR_parameter = 1.95
    target_accuracy_3 = 1e-4

    # phi_3 = ...
    # delta_max_list_3 = ...

    # Do not edit or remove the boiler-plate code below.
    if given(delta_max_list_3, phi_3, t2_2):
        print("\nTotal running time: %.2f min" % ((t2_2-t1_2)/60))
        print("Code speed: %.1f iterations per second" %(len(delta_max_list_3)/(t2_2-t1_2)))

    show(delta_max_list=delta_max_list_3, phi=phi_3, t2=t2_2)


@app.cell(hide_code=True)
def check_13_3a():
    check_answers(phi_3=phi_3, delta_max_list_3=delta_max_list_3, key="answer_13_3a")


@app.cell(hide_code=True)
def sol_13_05():
    SOR_parameter_sol5 = 1.95
    target_accuracy_sol5 = 1e-4
    M_sol5 = 101
    phi_sol5 = np.zeros([M_sol5,M_sol5])
    delta_sol5 = phi_sol5.copy()
    phi_sol5[-1,1:-1] = 1

    # A matrix to keep track of which points in our simulation 
    # are fixed voltages. In this case, it is only the boundaries
    # of the simulation
    fixed_sol5 = np.empty([M_sol5,M_sol5])
    fixed_sol5[:,:] = False
    fixed_sol5[0,:] = True
    fixed_sol5[-1,:] = True
    fixed_sol5[:,0] = True
    fixed_sol5[:,-1] = True

    # Keep track of the biggest update. 
    # When this is smaller than our target accuracy, 
    # we will stop iterating
    delta_max_sol5 = 1
    delta_max_list_sol5 = []

    t1_sol5 = time()
    while delta_max_sol5 > target_accuracy_sol5:
        for _i in range(M_sol5):
            for _j in range(M_sol5):
                if not fixed_sol5[_i,_j]:
                    delta_sol5[_i,_j] = (phi_sol5[_i+1,_j] + phi_sol5[_i-1,_j] + phi_sol5[_i,_j+1] + phi_sol5[_i,_j-1])/4 - phi_sol5[_i,_j]
                    phi_sol5[_i,_j] += SOR_parameter_sol5*delta_sol5[_i,_j]
        delta_max_sol5 = np.max(np.abs(delta_sol5))
        delta_max_list_sol5.append(delta_max_sol5)
        print("N_iter %d delta_max %e\r" % (len(delta_max_list_sol5), delta_max_sol5), end='')

    t2_sol5 = time()
    print("\nTotal running time: %.2f min" % ((t2_sol5-t1_sol5)/60))
    print("Code speed: %.1f iterations per second" %(len(delta_max_list_sol5)/(t2_sol5-t1_sol5)))

    phi_sol5 = phi_sol5.copy()
    delta_max_list_sol5 = delta_max_list_sol5.copy()

    show()


@app.cell
def demo_04():
    # Do not edit or remove the boiler-plate code below.
    fig_3 = None
    if given(phi_3):

        # Notebook code 
        fig_3 = visualise(phi_3, normalisation=0.5, line_cut_y=80)
        fig_3.show()

    show(phi_3=phi_3)


@app.cell(hide_code=True)
def head_13_06():
    mo.md(
        r"""
        ## Exercise 10.6

        Make a plot of `delta_max` vs iteration number for the three techniques.
        """
    )


@app.cell
def ex_13_06():
    # Your code here:

    # Do not edit or remove the boiler-plate code below.
    show()


@app.cell(hide_code=True)
def sol_13_06():
    _fig, _ax = plt.subplots()
    _ax.plot(delta_max_list_sol1, label="Jacobi")
    _ax.plot(delta_max_list_sol3, label="Gauss-Seidel")
    _ax.plot(delta_max_list_sol5, label="SOR")
    _ax.set_yscale('log')
    _ax.set_ylabel("$\Delta \phi_{max}$ (V)")
    _ax.set_xlabel("Iteration number")
    _ax.legend()

    show(_ax)


@app.cell(hide_code=True)
def head_13_07():
    mo.md(
        r"""
        ## Exercise 10.7

        Peform a simulation of a 2d "point source" consisting of a single pixel at position `i,j = 50,50` with charge `rho = 1`.
        (Note that our "point source" 2D simulation actually corresponds to the voltage around a thin, infinitely long wire.) Use the metallic boundary condition V=0 at the boundaries. 

        To match the numerical answer values of the reference solution, use SOR with an SOR parameter of 1.95.
        """
    )


@app.cell
def ex_13_07():
    # Fill these in as you work through the exercise.
    phi_4 = None

    target_accuracy_4 = 1e-4
    M_3 = 101
    SOR_parameter_2 = 1.95

    # Our fixed charge input matrix
    rho_fixed = np.zeros([M_3,M_3])
    rho_fixed[M_3//2,M_3//2] = 1

    # phi_4 = ...

    # Do not edit or remove the boiler-plate code below.
    show(phi=phi_4)


@app.cell(hide_code=True)
def check_13_4a():
    check_answers(phi_4=phi_4, rho_fixed=rho_fixed, key="answer_13_4a", when=given(phi_4))


@app.cell(hide_code=True)
def sol_13_07():
    target_accuracy_sol7 = 1e-4
    M_sol7 = 101
    SOR_parameter_sol7 = 1.95

    # Our fixed charge input matrix
    rho_fixed_sol7 = np.zeros([M_sol7,M_sol7])
    rho_fixed_sol7[M_sol7//2,M_sol7//2] = 1
    phi_sol7 = np.zeros([M_sol7,M_sol7])
    delta_sol7 = phi_sol7.copy()

    # A matrix to keep track of which points in our simulation 
    # are fixed voltages. In this case, it is only the boundaries
    # of the simulation
    fixed_sol7 = np.zeros([M_sol7,M_sol7])
    fixed_sol7[:,:] = False
    fixed_sol7[[0,-1],:] = True
    fixed_sol7[:,[0,-1]] = True

    delta_max_sol7 = 1
    delta_max_list_sol7 = []

    t1_sol7 = time()

    while delta_max_sol7 > target_accuracy_sol7:
        for _i in range(M_sol7):
            for _j in range(M_sol7):
                if not fixed_sol7[_i,_j]:
                    delta_sol7[_i,_j] = (phi_sol7[_i+1,_j] + phi_sol7[_i-1,_j] + phi_sol7[_i,_j+1] + phi_sol7[_i,_j-1])/4 \
                        + rho_fixed_sol7[_i,_j]/4 - phi_sol7[_i,_j]
                    phi_sol7[_i,_j] += delta_sol7[_i,_j]*SOR_parameter_sol7
        delta_max_sol7 = np.max(np.abs(delta_sol7))
        delta_max_list_sol7.append(delta_max_sol7)
        print("N_iter %d delta_max %e\r" % (len(delta_max_list_sol7), delta_max_sol7), end='')

    t2_sol7 = time()
    print("\nTotal running time: %.2f min" % ((t2_sol7-t1_sol7)/60))
    print("Code speed: %.1f iterations per second" %(len(delta_max_list_sol7)/(t2_sol7-t1_sol7)))
    phi_sol7 = phi_sol7.copy()
    rho_fixed_sol7 = rho_fixed_sol7.copy()

    show()


@app.cell
def demo_05():
    # Do not edit or remove the boiler-plate code below.
    fig_4 = None
    if given(phi_4):

        # Notebook code
        fig_4 = visualise(phi_4, normalisation=0.5, line_cut_y=80)
        fig_4.show()

    show(phi_4=phi_4)


@app.cell(hide_code=True)
def head_13_08():
    mo.md(
        r"""
        ## Exercise 10.8

        Implement Exercise 10.4, part (a), with an extra boundary grid point on all sides.
        """
    )


@app.cell
def ex_13_08():
    target_accuracy_5 = 1e-4
    M_4 = 103

    phi_5 = np.zeros([M_4,M_4])
    delta_2 = phi_5.copy()

    # A matrix to keep track of which points in our simulation 
    # are fixed voltages. In this case, it is only the boundaries
    # of the simulation
    fixed_3 = np.zeros([M_4,M_4])
    fixed_3[:,:] = False

    # fixed[[___,___,___,___],:] = True
    # fixed[:,[___,___,___,___]] = True

    # The external fixed charge
    rho_fixed_2 = np.zeros([M_4,M_4])

    # rho_fixed[___,___] = 1

    # Set `unfinished_3` to False once you have written the code below, so that it can run.
    unfinished_3 = True

    # Do not edit or remove the boiler-plate code below.
    show()


@app.cell(hide_code=True)
def check_13_5a():
    check_answers(rho_fixed_2=rho_fixed_2, phi_5=phi_5, key="answer_13_5a", when=not unfinished_3)


@app.cell(hide_code=True)
def sol_13_08():
    target_accuracy_sol8 = 1e-4
    M_sol8 = 103

    phi_sol8 = np.zeros([M_sol8,M_sol8])
    delta_sol8 = phi_sol8.copy()

    # A matrix to keep track of which points in our simulation 
    # are fixed voltages. In this case, it is only the boundaries
    # of the simulation
    fixed_sol8 = np.zeros([M_sol8,M_sol8])
    fixed_sol8[:,:] = False
    fixed_sol8[[0,1,-1,-2],:] = True
    fixed_sol8[:,[0,1,-1,-2]] = True

    # The external fixed charge
    rho_fixed_sol8 = np.zeros([M_sol8,M_sol8])
    rho_fixed_sol8[M_sol8//2,M_sol8//2] = 1

    # Keep track of the biggest update. 
    # When this is smaller than our target accuracy, 
    # we will stop iterating
    delta_max_sol8 = 1
    delta_max_list_sol8 = []

    t1_sol8 = time()
    SOR_parameter_sol8 = 1.95

    while delta_max_sol8 > target_accuracy_sol8:
        for _i in range(M_sol8):
            for _j in range(M_sol8):
                if not fixed_sol8[_i,_j]:
                    delta_sol8[_i,_j] = (phi_sol8[_i+1,_j] + phi_sol8[_i-1,_j] + phi_sol8[_i,_j+1] + phi_sol8[_i,_j-1])/4 \
                        + rho_fixed_sol8[_i,_j]/4 - phi_sol8[_i,_j]
                    phi_sol8[_i,_j] += delta_sol8[_i,_j]*SOR_parameter_sol8
        delta_max_sol8 = np.max(np.abs(delta_sol8))
        delta_max_list_sol8.append(delta_max_sol8)
        print("N_iter %d delta_max %e\r" % (len(delta_max_list_sol8), delta_max_sol8), end='')

    t2_sol8 = time()
    print("\nTotal running time: %.2f min" % ((t2_sol8-t1_sol8)/60))
    print("Code speed: %.1f iterations per second" %(len(delta_max_list_sol8)/(t2_sol8-t1_sol8)))
    rho_fixed_sol8 = rho_fixed_sol8.copy()
    phi_sol8 = phi_sol8.copy()

    show()


@app.cell(hide_code=True)
def head_13_09():
    mo.md(
        r"""
        ## Exercise 10.9

        Calculate the (dimensionless) charge density for the simulation in question 5(a).
        """
    )


@app.cell
def ex_13_09():
    # The potential you found in the previous exercise is in `phi_5`.
    rho_calc = np.zeros([M_4,M_4])

    # Do not edit or remove the boiler-plate code below.
    show(rho_calc=rho_calc)


@app.cell(hide_code=True)
def check_13_5b():
    check_answers(rho_calc=rho_calc, key="answer_13_5b", when=not unfinished_3)


@app.cell(hide_code=True)
def sol_13_09():
    rho_calc_sol9 = np.zeros([M_sol8,M_sol8])
    phi_sol9 = phi_sol8
    for _i in range(1,M_sol8-1):
        for _j in range(1,M_sol8-1):
            rho_calc_sol9[_i,_j] = \
                (phi_sol9[_i+1,_j] + phi_sol9[_i-1,_j] + phi_sol9[_i,_j+1] + phi_sol9[_i,_j-1] - 4*phi_sol9[_i,_j])
    rho_calc_sol9 = np.copy(rho_calc_sol9)

    show(rho_calc=rho_calc_sol9)


@app.cell
def demo_06():
    # Do not edit or remove the boiler-plate code below.
    _ax = None
    if given(rho_calc):
        _fig, _ax = plt.subplots()
        _im1 = _ax.imshow(rho_calc, cmap="RdBu")
        _fig.colorbar(_im1)
        _im1.set_clim(vmax=-np.min(rho_calc)-2e-6)

    show(_ax, rho_calc=rho_calc)


@app.cell
def demo_07():
    # Do not edit or remove the boiler-plate code below.
    fig_5 = None
    if given(rho_calc):
        fig_5 = visualise(-rho_calc, normalisation=0.148, line_cut_y=1, autoscale=True)
        fig_5.show()

    show(rho_calc=rho_calc)


@app.cell
def demo_08():
    # Do not edit or remove the boiler-plate code below.
    if given(rho_calc):
        np.sum(rho_calc)

    show(rho_calc=rho_calc)


if __name__ == "__main__":
    app.run()
