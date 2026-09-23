import marimo

app = marimo.App(width="medium")

with app.setup:
    import marimo as mo
    import numpy as np
    import matplotlib.pyplot as plt
    from numpy import array,empty
    from time import time
    from tn23015 import check_answers, given, load_data, md, print, row, show, slider


@app.cell(hide_code=True)
def head_6_01():
    mo.md(
        r"""
        ## Exercise 4.1

        Write a script for calculating the angle between two vectors in degrees.
        Start with vectors `a` and `b` as input and then find the angle.
        Evaluation of the angle must be done with a single line.
        Note that numpy does not care about the dimensions (column or row) as calculates the inner product for arrays.
        Howeve, take care that the script does not crash in case of faulty input (two vectors of different length for example).
        Output the angle to variable `theta`.
        Test your code with vectors for which you already know the outcome.
        """
    )


@app.cell
def ex_6_01():
    # Fill these in as you work through the exercise.
    theta = None

    a=np.array([1, 0, 0])
    b=np.array([0, 1, 0])

    # theta = ...
    # print(theta)

    # Do not edit or remove the boiler-plate code below.
    show(theta=theta)


@app.cell(hide_code=True)
def sol_6_01():
    a_sol1=np.array([1, 0, 0])
    b_sol1=np.array([0, 1, 0])
    if len(a_sol1)!=len(b_sol1):
        print('The length of the two vectors is not equal')
    elif np.linalg.norm(b_sol1)==0 or np.linalg.norm(a_sol1)==0:
        print('The length of one of the two vectors is equal to zero')
    else:
        theta_sol1=(180/np.pi)*np.arccos(np.inner(a_sol1,b_sol1)/np.linalg.norm(a_sol1)/np.linalg.norm(b_sol1))

    print(theta_sol1)

    show()


@app.cell(hide_code=True)
def head_6_02():
    mo.md(
        r"""
        ## Exercise 4.2

        Write with pen and paper similar equations for the other three junctions with unknown voltages.
        Define the matrix equation relating the four unknown voltages and the known parameters.

        The most straightforward way to solve a set of equations is by means of Gaussian elimination.
        We can multiply any equation by a constant and subtract equations from each other while still obtaining the correct solution.
        This is utilized to make the matrix describing the linear set of equations upper triangular.
        The solution is then easily obtained by back-substitution from the bottom equation to the top.
        The program below can solve the four resulting equations using Gaussian elimination and find the four voltages.
        Use your result obtained above to set-up the correct `A` matrix and `v` vector for your problem.
        Go through it and notice how Python efficiently uses the matrix $A$ storage and works on entire rows by slicing.

        NB: make sure to set up the matrix $A$ such that the solution is on the form `x = [V1, V2, V3, V4]`.
        Also for the Gaussian elimination code to work (with the in-place division `A[m,:] /= div`) setup both $A$ and $v$ containing floats using the `dtype` argument of the numpy array function (or by entering your matrix using floating point numbers like 4.0 instead of 4, which would make it an `int` by default).
        """
    )


@app.cell
def ex_6_02():
    # Fill these in as you work through the exercise.
    A = v = None

    # A = ...
    # v = ...

    # Do not edit or remove the boiler-plate code below.
    N = div = mult = x = None
    if given(A, v):
        N = len(v)

        # Gaussian elimination
        for _m in range(N):

            # Divide by the diagonal element
            div = A[_m,_m]
            A[_m,:] /= div
            v[_m] /= div

            # Now subtract from the lower rows
            for _i in range(_m+1,N):
                mult = A[_i,_m]
                A[_i,:] -= mult*A[_m,:]
                v[_i] -= mult*v[_m]
        print('The matrix after Gaussian elimiation is')
        print(A)

        # Backsubstitution
        x = empty(N,float)
        for _m in range(N-1,-1,-1):
            x[_m] = v[_m]
            for _i in range(_m+1,N):
                x[_m] -= A[_m,_i]*x[_i]

        print('The solution is')
        print(x)

    show(A=A, v=v)


@app.cell(hide_code=True)
def sol_6_02():
    A_sol2 = array([[ 4, -1, -1, -1 ],
               [-1,  3,  0, -1 ],
               [-1,  0,  3, -1 ],
               [-1, -1, -1,  4 ]], float)
    A0_sol2 = A_sol2.copy()
    v_sol2 = array( [ 5,  0,  5,  0 ],float)

    print('The input matrix is')
    print(A_sol2)
    N_sol2 = len(v_sol2)

    # Gaussian elimination
    for _m in range(N_sol2):

        # Divide by the diagonal element
        div_sol2 = A_sol2[_m,_m]
        A_sol2[_m,:] /= div_sol2
        v_sol2[_m] /= div_sol2

        # Now subtract from the lower rows
        for _i in range(_m+1,N_sol2):
            mult_sol2 = A_sol2[_i,_m]
            A_sol2[_i,:] -= mult_sol2*A_sol2[_m,:]
            v_sol2[_i] -= mult_sol2*v_sol2[_m]
    print('The matrix after Gaussian elimiation is')
    print(A_sol2)

    # Backsubstitution
    x_sol2 = empty(N_sol2,float)
    for _m in range(N_sol2-1,-1,-1):
        x_sol2[_m] = v_sol2[_m]
        for _i in range(_m+1,N_sol2):
            x_sol2[_m] -= A_sol2[_m,_i]*x_sol2[_i]

    print('The solution is')
    print(x_sol2)

    show()


@app.cell(hide_code=True)
def head_6_03():
    mo.md(
        r"""
        ## Exercise 4.3

        Calculate the following matrix properties:
        * Inverse of the matrix $A$ using the `inv` function from the numpy linear algebra package. Name the inverse `invA`. 
        * Rank of the matrix `A` with the numpy function `matrix_rank` and save it to parameter `rankA`
        * Matrix determinant with the numpy function `det` and store it to variable `detA`.

        Look in the help for more details on the functions.
        """
    )


@app.cell
def ex_6_03():
    # Fill these in as you work through the exercise.
    detA = invA = rankA = None

    # invA = ...
    # rankA = ...
    # detA = ...

    # Do not edit or remove the boiler-plate code below.
    show(detA=detA, invA=invA, rankA=rankA)


@app.cell(hide_code=True)
def check_6_03():
    check_answers(invA=invA, rankA=rankA, detA=detA, key="answer_6_03")


@app.cell(hide_code=True)
def sol_6_03():
    A_sol3=np.array([[0, 0, 2, 3],[4, 2, 3, 1],[2, 5, 1, 2],[1, 0, 0, 1]])

    invA_sol3=np.linalg.inv(A_sol3)

    N_sol3=A_sol3.shape[1]

    rankA_sol3=np.linalg.matrix_rank(A_sol3)
    detA_sol3=np.linalg.det(A_sol3)

    print('The matrix dimension is ' +str(N_sol3)+ ' and the rank is ' + str(rankA_sol3))
    print('The matrix determinant is ' + str(detA_sol3) + ' and is non zero')
    invA_sol3 = np.copy(invA_sol3)
    rankA_sol3 = np.copy(rankA_sol3)
    detA_sol3 = np.copy(detA_sol3)

    show()


@app.cell(hide_code=True)
def head_6_03b():
    mo.md(
        r"""
        ## Exercise 4.4

        Now see what happens if you lower the rank of the matrix by making last two rows identical.
        Print the matrix rank, matrix determinant to the command line.
        Can you calculate the inverse?
        And what if the rows are copies of each other differing only by a small number close to the machine precision, say 1e-16 or 1e-17.
        Play around and try it for yourself.
        """
    )


@app.cell
def ex_6_03b():
    # Your code here:

    # print(np.linalg.matrix_rank(A))
    # print(np.linalg.det(A))
    # print(np.linalg.inv(A))

    # Do not edit or remove the boiler-plate code below.
    show()


@app.cell(hide_code=True)
def sol_6_03b():
    A_sol3[3,:]=A_sol3[2,:]
    print(np.linalg.matrix_rank(A_sol3))
    print(np.linalg.det(A_sol3))

    eps_sol4=1e-16
    A_sol3[3,:]=(1-eps_sol4)*A_sol3[2,:]
    print(np.linalg.matrix_rank(A_sol3))
    print(np.linalg.det(A_sol3))
    print(np.linalg.inv(A_sol3))

    show()


@app.cell(hide_code=True)
def head_6_04():
    mo.md(
        r"""
        ## Exercise 4.5

        Write a script to evaluate the differences in computational time between the inverse method and the solve method.
        Perform the following steps
        * Generate random  matrices  $A$  of  size  $N\times N$ and random  (column) vectors $b$ of size $N\times 1$ using the `rand` command from the numpy random library. 
        * Compute the solution $x$ to $Ax = b$ using the `inv` method and the `solve` method
        * Compute the time it takes for the computer to finish the calculation for both methods and store the calculation time. Look up lecture 2c for timing the computation time.
        * Make a loop over a range of values for $N$, perform the calculation for every matrix size $N$ and store the computation times in an array. Take a range of values for $N$ between 100 and 1000 in ten steps on a logarithmic scale (e.g. use `np.geomspace` and round off to integer value).
        * Make a plot of both calculation times as a function of $N$. Use a double logarithmic plot with the command `loglog` and `_ax.grid(which='minor')`.  
        * Finally, formulate a hypothesis for the dependence of computational time on $N$, i.e. propose a formula for this dependence. Read from the graph, by what factor is `solve` faster than `inv`.

        In a log-log plot a dependence of $t \propto N^{p}$ corresponds to a linear line log $t=p $log $N$. Hence, the slope of the linear dependence is the exponent $p$. To determine power $p$ divide the number of units on the vertical scale with the number of units on the horizontal scale.
        """
    )


@app.cell
def ex_6_04():
    # Your code here:

    # Do not edit or remove the boiler-plate code below.
    show()


@app.cell(hide_code=True)
def sol_6_04():
    nmin_sol5 = 100;
    nmax_sol5 = 1000;
    n_sol5 = 10;

    Nmatrix_sol5 = np.round(np.geomspace(nmin_sol5,nmax_sol5,n_sol5))

    time_inv_sol5=np.zeros(n_sol5)
    time_solve_sol5=np.zeros(n_sol5)

    for _j in range(n_sol5):
        N_sol5 = int(Nmatrix_sol5[_j])
        B_sol5 = np.random.rand(N_sol5,N_sol5)
        y_sol5 = np.random.rand(N_sol5,1)

        tstart_sol5 = time()
        x_sol5 = np.linalg.inv(B_sol5)@y_sol5
        tend_sol5=time()
        time_inv_sol5[_j] = tend_sol5-tstart_sol5

        tstart_sol5 = time()
        x_sol5 = np.linalg.solve(B_sol5, y_sol5)
        tend_sol5=time()
        time_solve_sol5[_j] = tend_sol5-tstart_sol5

    _fig, _ax = plt.subplots()
    _ax.loglog(Nmatrix_sol5, time_inv_sol5, '-ob', label='inverse')
    _ax.loglog(Nmatrix_sol5, time_solve_sol5, '-or', label='solve')
    _ax.grid(which='minor')        
    _ax.set_xlabel('Matrix size')
    _ax.set_ylabel('Computation time (sec)')
    _ax.legend()

    # linear log-log plot for large N with slope ~2 indicates an N^2 scaling of the computational time
    # solve is close to a factor of two faster

    show(_ax)


@app.cell(hide_code=True)
def head_6_05():
    mo.md(
        r"""
        ## Exercise 4.6

        Use pen and paper to write this system of equation as an eigenvalue problem.
        Keep the derivation next to you -- you will need the matrix you wrote down in the next cell.

        Based on the matrix equation you derived, define in Python the matrix `A` that describes this problem as an eigenvalue problem.
        Fill it with the correct numbers given $T=1$, $m=2$, and $a=b=0.25$. Determine the eigenvalues `eigA` and eigenvectors `eigvA` with the ```eigh``` function of numpy for the system with $T=1$, $m=2$, and $a=b=0.25$.
        """
    )


@app.cell
def ex_6_05():
    # Fill these in as you work through the exercise.
    A_2 = eigA = eigvA = None

    # define parameters
    T=1
    m=2
    a_2=0.25
    b_2=0.25

    # A_2 = ...
    # eigA = ...
    # eigvA = ...

    # Do not edit or remove the boiler-plate code below.
    show(A=A_2, eigA=eigA, eigvA=eigvA)


@app.cell(hide_code=True)
def check_6_05():
    check_answers(A_2=A_2, eigA=eigA, eigvA=eigvA, key="answer_6_05")


@app.cell(hide_code=True)
def sol_6_05():
    # define parameters
    T_sol6=1
    m_sol6=2
    a_sol6=0.25
    b_sol6=0.25

    # setting up the system of equations
    A_sol6 = (1/m_sol6)*np.array([[ (T_sol6/a_sol6 + T_sol6/2/b_sol6),  -T_sol6/2/b_sol6],
               [ -T_sol6/2/b_sol6,  (T_sol6/a_sol6 + T_sol6/2/b_sol6)]], float)

    eigA_sol6,eigvA_sol6=np.linalg.eigh(A_sol6)

    omega1_sol6=np.sqrt(T_sol6/m_sol6/a_sol6)
    print('The analytical answer for omega^2 is ' + str(omega1_sol6**2) + ' and the eigenvalue is ' + str(eigA_sol6[0]))
    omega2_sol6=np.sqrt(T_sol6*(a_sol6+b_sol6)/m_sol6/a_sol6/b_sol6)
    print('The analytical answer for omega^2 is ' + str(omega2_sol6**2) + ' and the eigenvalue is ' + str(eigA_sol6[1]))
    A_sol6 = np.copy(A_sol6)
    eigA_sol6 = np.copy(eigA_sol6)
    eigvA_sol6 = np.copy(eigvA_sol6)

    show()


@app.cell(hide_code=True)
def head_6_06b():
    mo.md(
        r"""
        ## Exercise 4.7

        Compare your eigenvalues to the analytical result.
        Plot the positions of the particles and the string at $t=0$ and $\phi=0$ in a single graph.
        In this graph, create the shapes of the string as shown below

        ![](https://raw.githubusercontent.com/curiousbeams/lecture-tn23015-computational-science/main/figures/particlesonstring.png)

        Use `np.concatenate` to add the fixed side points to the bead positions for plotting the string.<br>

        Why are the eigenvectors from numpy quantitative, whereas the eigenvectors of calculated with numpy are relative $[A, B]$ and $[A, -B]$?
        """
    )


@app.cell
def ex_6_06b():
    # Your code here:

    # Do not edit or remove the boiler-plate code below.
    show()


@app.cell(hide_code=True)
def sol_6_06b():
    _fig, _ax = plt.subplots()
    _ax.plot([a_sol6, a_sol6+2*b_sol6], eigvA_sol6[:,0], 'or', label='mode 1: omega^2=' + str(omega1_sol6**2))
    string1_sol7=np.concatenate(([0], eigvA_sol6[:,0], [0]))
    _ax.plot([0,a_sol6,a_sol6+2*b_sol6,2*(a_sol6+b_sol6)], string1_sol7, '-r')

    _ax.plot([a_sol6, a_sol6+2*b_sol6], eigvA_sol6[:,1], 'og', label='mode 2: omega^2=' + str(omega2_sol6**2))
    string2_sol7=np.concatenate(([0], eigvA_sol6[:,1], [0]))
    _ax.plot([0,a_sol6,a_sol6+2*b_sol6,2*(a_sol6+b_sol6)], string2_sol7, '-g')

    _ax.axhline(0,color='grey', linestyle=':')
    _ax.set_xlim((0,1))
    _ax.grid()
    _ax.legend(loc=2)

    # numpy answer is just as correct any multiplicative factor operating on the eigenvector 
    # results in an eigenvector as well
    # substitution of lowest frequency results in A=B

    show(_ax)


@app.cell(hide_code=True)
def head_6_05b():
    mo.md(
        r"""
        ## Exercise 4.8

        Calculate an array `xt` of dimension `(100,2)` such that `x[n]` corresponds to the position at the time `t[n]` when the starting point is `x0 = [1,0]`.
        Plot the position of both $x_1$ and $x_2$ as function of time in the same plot.
        """
    )


@app.cell
def ex_6_05b():
    # Fill these in as you work through the exercise.
    xt = None

    # xt = ...

    # Do not edit or remove the boiler-plate code below.
    t = v1 = v2 = x0 = None
    if given(xt, eigvA):
        v1 = eigvA[:,0]
        v2 = eigvA[:,1]
        x0 = np.array([1,0])

        t = np.linspace(0,10,100)

    show(xt=xt, eigvA=eigvA)


@app.cell(hide_code=True)
def check_6_05b():
    check_answers(xt=xt, key="answer_6_05", start=4)


@app.cell(hide_code=True)
def sol_6_05b():
    v1_sol8 = eigvA_sol6[:,0]
    v2_sol8 = eigvA_sol6[:,1]
    x0_sol8 = np.array([1,0])

    t_sol8 = np.linspace(0,10,100)
    A_sol8 = np.dot(v1_sol8,x0_sol8)
    B_sol8 = np.dot(v2_sol8,x0_sol8)

    xt_sol8 = np.zeros((100,2))

    xt_sol8[:,0] = A_sol8*np.cos(omega1_sol6*t_sol8)*v1_sol8[0] + B_sol8*np.cos(omega2_sol6*t_sol8)*v2_sol8[0]
    xt_sol8[:,1] = A_sol8*np.cos(omega1_sol6*t_sol8)*v1_sol8[1] + B_sol8*np.cos(omega2_sol6*t_sol8)*v2_sol8[1]

    _fig, _ax = plt.subplots()
    _ax.plot(t_sol8, xt_sol8[:,0], label='x1')
    _ax.plot(t_sol8, xt_sol8[:,1], label='x2')

    _ax.set_xlim((0,10))
    _ax.legend()

    _ax.set_xlabel(r'Time, $t$')
    _ax.set_ylabel(r'Position, $x$')
    xt_sol8 = np.copy(xt_sol8)

    show(_ax)


@app.cell(hide_code=True)
def head_6_06():
    mo.md(
        r"""
        ## Exercise 4.9

        Set up a system of 50 particles on a string at distance $a=1$ relative to each other. _Hint_ : use the numpy function `eye` to quickly fill your matrix with diagonal and off-diagonal elements.
        Find the eigenvalues and eigenvectors.
        Plot the positions of the particles for the first 4 eigenmodes at $t=0$ and $\phi=0$ in a for loop.
        Automatically make a legend indicating the mode number.
        """
    )


@app.cell
def ex_6_06():
    # Your code here:

    # Do not edit or remove the boiler-plate code below.
    show()


@app.cell(hide_code=True)
def sol_6_06():
    N_sol9=50
    a_sol9=1
    A_sol9=(2*T_sol6/a_sol9)*np.eye(N_sol9,N_sol9)-(T_sol6/a_sol9)*np.eye(N_sol9,N_sol9, 1)-(T_sol6/a_sol9)*np.eye(N_sol9,N_sol9, -1)

    # note the sign change in A caused by the double derivative on the left hand side

    x_sol9,V_sol9=np.linalg.eigh(A_sol9)

    # for symmetric matrices (as expected for physics problems) only

    _fig, _ax = plt.subplots()
    for _cnt in range(4):
        legstr_sol9=('mode'+str(_cnt+1))
        _ax.plot(V_sol9[:,_cnt], '-o', label=legstr_sol9)

    _ax.set_xlabel('Particle number i')
    _ax.set_ylabel('Position')
    _ax.grid()
    _ax.legend()

    show(_ax)


if __name__ == "__main__":
    app.run()
