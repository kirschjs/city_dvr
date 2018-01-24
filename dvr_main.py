import matplotlib.pyplot as plt
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import eigsh
import matplotlib.pyplot as plt

from dvr import calc_grid, calc_Ekin, calc_potential, calc_mhamilton
from physics import NUCLEON_MASS, PLANCS_CONSTANT, C, JOULE_PER_EV, HBARC, eigenvalues_harmonic_osci
from util import benchmark

np.set_printoptions(linewidth=300, suppress=True, precision=5)

# single-particle parameters and other physical constants
MASS = NUCLEON_MASS

# isotropic harmonic oscillator
<<<<<<< Updated upstream
OMEGA_BASIS = .2
OMEGA_TRAP = 0.5
LEC_HOINT = 100.
X_EQ = 0.
POT_HO = ['HO', X_EQ, MASS / HBARC, OMEGA_TRAP]
POT_HOINT = ['HOINT', LEC_HOINT]

# lattice set-up
PARTNBR = 2  # number of particles
SPACEDIMS = 3  # spatial coordinate dimensions (e.g. Cartesian x,y,z)
BASIS_DIM = 4  # (dim of variational basis) = (nbr of grid points) = (nbr of segments - 1)

# specify the variational basis
BOX_SIZE = 10  #BASIS_DIM + 0  # physical length of one spatial dimension (in Fermi); relevant for specific bases, only!
BOX_ORIGIN = -BOX_SIZE / 2.
BASIS_SINE = ['SINE', [SPACEDIMS, BOX_SIZE, BOX_ORIGIN, MASS / HBARC]]
BASIS_HO = ['HO', [SPACEDIMS, X_EQ, (MASS / HBARC), OMEGA_BASIS]]
# each axis is devided into = (number of grid points) - 1

N_EIGENV = 10  # number of eigenvalues to be calculated with <eigsh>
=======
OMEGA_INT = 2.4
X_EQ = 0.
POT_HO = ['HO', X_EQ, MASS / HBARC, OMEGA_INT]
POT_HO_INTER = ['HOINT', MASS / HBARC * OMEGA_INT**2]

# lattice set-up
PARTNBR = 2  # number of particles
SPACEDIMS = 2  # spatial coordinate dimensions (e.g. Cartesian x,y,z)
BASIS_DIM = 7  # (dim of variational basis) = (nbr of grid points) = (nbr of segments - 1)

N_EIGENV = 4  # number of eigenvalues to be calculated with <eigsh>
POT = POT_HO_INTER


def calc_mhamilton(n_part, dim_space, dim_bas, spec_bas, spec_pot):
    """ Function returns the Hamilton matrix; 

        :n_part: number of particles
        :dim_space: spatial (Cartesian) dimensions
        :dim_bas: variational-basis dim = number of segments each coordinate is divided into
        :spec_pot: parameters specifying the interaction potential
        :spec_bas: parameters specifying the basis

        :return: full Hamilton matrix in D(iscrete) V(ariable) R(epresentation)
    """
    # dimension of a single coordinate point; e.g., 2D 2Part: (x1,y1,x2,y2)
    # D spatial dimensions for each of the N particles;
    dim_grdpoint = n_part * dim_space
    # each component of a grid point takes dim_bas discrete values
    # e.g. x1 \in {x_1,...,x_dim_bas} where x_1 is an eigenvalue of the position matrix
    dim_h = dim_bas**dim_grdpoint

    # initialize empty matrices (might have to be "sparsed" for larger dim. problems)
    mpotential = np.zeros((dim_h, dim_h))
    mkinetic = np.zeros((dim_h, dim_h))
    mhamilton = np.zeros((dim_h, dim_h))

    # obtain eigensystem of the position operator in the basis of choice
    # eigenvalues '=' grid points ; transformation matrix necessary for Ekin
    # STATUS: one basis for all coordinates (future: xy->HO, z->SINE)
    coordOP_evSYS = calc_grid(dim_bas, spec_bas)

    # calculate potential and kinetic-energy matrices for a chosen basis
    # STATUS: for each additional basis, the matrices need to be specified in this function!
    mkinetic = calc_Ekin(dim_bas, n_part, spec_bas, coordOP_evSYS)
    # STATUS: the potential matrix is assumed to be diagonal (future: OPE+B => potential has non-zero offdiagonal elements)
    mpotential = np.diag(
        calc_potential(n_part, dim_space, spec_pot, coordOP_evSYS))

    mhamilton = (mkinetic + mpotential)
    return mhamilton


>>>>>>> Stashed changes
""" main section of the program
    1. set up the Hamiltonian
    2. full Diagonalization
    3. approximate Diagonalization (extract only the N_EIGENV lowest EV's)
"""

eigenvalue_container = []
ham = []
<<<<<<< Updated upstream
with benchmark("Matrix filling"):
    evs = []
    for cycl in range(2):
        LEC = [100, 1000]
        POT_HOINT = ['HOINT', LEC[cycl]]
        ham = calc_mhamilton(PARTNBR, SPACEDIMS, BASIS_DIM, BASIS_HO,
                             POT_HOINT)
        evals_small, evecs_small = eigsh(
            coo_matrix(ham), N_EIGENV, which='SA', maxiter=50000)
        evs.append(evals_small[:N_EIGENV])
    fig = plt.figure()
    ax1 = fig.add_subplot(211)

    ax1.set_xlabel(r'$n$')
    ax1.set_ylabel(r'$E_n$ [MeV]')
    [plt.plot(evs[n], label=r'n=%d' % n) for n in range(len(evs))]
    ax1.legend(loc='lower right')
    ax1 = fig.add_subplot(212)

    ax1.set_xlabel(r'$n$')
    ax1.set_ylabel(r'$E_n(C_{1000})-E_n(C_{100})$ [MeV]')
    [
        plt.plot(evs[n + 1] - evs[n], label=r'$E(C_%d)-E(C_%d)$' % (n + 1, n))
        for n in range(2)
    ]
    ax1.legend(loc='lower right')
    plt.show()
    exit()

sparsimonius = True  # False '=' full matrix diagonalization; True '=' approximate determination of the lowest <N_EIGEN> eigenvalues

if sparsimonius:
    with benchmark("Diagonalization -- sparse matrix structure (DVR)"):
        # calculate the lowest N eigensystem of the matrix in sparse format
        evals_small, evecs_small = eigsh(
            coo_matrix(ham), N_EIGENV, which='SA', maxiter=5000)
        for e in evals_small[:N_EIGENV]:
            print('%8.8f,' % e, end='')
        exit()
        print('Hamilton ( %d X %d ) matrix: %d/%d = %3.2f%% non-zero entries' %
              (np.shape(ham)[0], np.shape(ham)[1], coo_matrix(ham).nnz,
               (BASIS_DIM**
                (SPACEDIMS * PARTNBR))**2, 100. * coo_matrix(ham).nnz / float(
                    (BASIS_DIM**(SPACEDIMS * PARTNBR))**2)))
        print('DVR-sparse:\nE_n         = ',
              evals_small[:min(N_EIGENV,
                               np.shape(ham)[1])])
        print('E_n+1 - E_n = ',
              np.diff(evals_small[:min(N_EIGENV,
                                       np.shape(ham)[1])]))
else:
    with benchmark("Diagonalization -- full matrix structure (DVR)"):
        # calculate the eigenvalues of the sum of the Hamilton matrix (Hermitian)
        EV = np.sort(np.linalg.eigvalsh(ham))
        for e in EV[:N_EIGENV]:
            print('%8.8f,' % e, end='')
        exit()
        print('Hamilton (%dX%d) matrix: %d/%d = %3.2f%% non-zero entries\n' %
              (np.shape(ham)[0], np.shape(ham)[1], coo_matrix(ham).nnz,
               (BASIS_DIM**
                (SPACEDIMS * PARTNBR))**2, 100. * coo_matrix(ham).nnz / float(
                    (BASIS_DIM**(SPACEDIMS * PARTNBR))**2)))
        print('DVR-full:\nE_n         = ', np.real(EV)[:N_EIGENV])
        print('E_n+1 - E_n = ', np.diff(EV[:min(N_EIGENV, np.shape(ham)[1])]))

with benchmark("Calculate %d-particle %d-dimensional HO ME analytically" %
               (PARTNBR, SPACEDIMS)):
    nmax = 20
    # E_n = (n_1x + ... + n_Nz + (D+N)/2) * hbarc * omega
    # N non-interacting particles in HO trap:
    #DIM = PARTNBR * SPACEDIMS
    #OM = OMEGA_TRAP
    # 2-particle system with relative HO interaction:
    DIM = SPACEDIMS
    OM = 2 * np.sqrt(LEC_HOINT / MASS)
    anly_ev = eigenvalues_harmonic_osci(OM, nmax, DIM)[:max(N_EIGENV, 10)]
    print('E_n         = ', anly_ev)
    print('E_n+1 - E_n = ', np.diff(anly_ev))
=======
parint = np.linspace(1.3, 2.4, num=10)
for n in parint:

    # specify the variational basis
    BOX_SIZE = n  #BASIS_DIM + 0  # physical length of one spatial dimension (in Fermi); relevant for specific bases, only!
    BOX_ORIGIN = -BOX_SIZE / 2.
    BASIS_SINE = ['SINE', [SPACEDIMS, BOX_SIZE, BOX_ORIGIN, MASS / HBARC]]

    OMEGA_BAS = n
    BASIS_HO = ['HO', [SPACEDIMS, X_EQ, (MASS / HBARC), OMEGA_BAS]]
    # each axis is devided into = (number of grid points) - 1
    DVR_BASIS = BASIS_SINE

    with benchmark("Matrix filling"):
        ham = calc_mhamilton(PARTNBR, SPACEDIMS, BASIS_DIM, DVR_BASIS, POT)

    sparsimonius = False  # False '=' full matrix diagonalization; True '=' approximate determination of the lowest <N_EIGEN> eigenvalues

    if sparsimonius:
        with benchmark("Diagonalization -- sparse matrix structure (DVR)"):
            # calculate the lowest N eigensystem of the matrix in sparse format
            evals_small, evecs_small = eigsh(
                coo_matrix(ham), N_EIGENV, which='SA', maxiter=5000)
            print(
                'Hamilton ( %d X %d ) matrix: %d/%d = %3.2f%% non-zero entries\n'
                % (np.shape(ham)[0], np.shape(ham)[1], coo_matrix(ham).nnz,
                   (BASIS_DIM**(SPACEDIMS * PARTNBR))**2,
                   100. * coo_matrix(ham).nnz / float(
                       (BASIS_DIM**(SPACEDIMS * PARTNBR))**2)))
            print('DVR-sparse:\n', evals_small[:min(N_EIGENV,
                                                    np.shape(ham)[1])])
            eigenvalue_container.append(
                evals_small[:min(N_EIGENV,
                                 np.shape(ham)[1])])
    else:
        with benchmark("Diagonalization -- full matrix structure (DVR)"):
            # calculate the eigenvalues of the sum of the Hamilton matrix (Hermitian)
            EV = np.sort(np.linalg.eigvalsh(ham))
            print('Hamilton (%dX%d) matrix: %d/%d non-zero entries\n' %
                  (np.shape(ham)[0], np.shape(ham)[1], coo_matrix(ham).nnz,
                   (BASIS_DIM**(SPACEDIMS * PARTNBR))**2))
            print('DVR-full:\n', np.real(EV)[:N_EIGENV])
            eigenvalue_container.append(np.real(EV)[:N_EIGENV])

fig = plt.figure()
ax1 = fig.add_subplot(121)
ax1.set_xlabel(r'eigenvalue number')
ax1.set_ylabel(r'eigenvalue')
ax1.plot(
    eigenvalue_container[0],
    'o-',
    label=r'DVR -- %s with smallest variational parameter' % DVR_BASIS[0])
[ax1.plot(evals) for evals in eigenvalue_container[1:]]
ax1.set_title(
    r'$\omega_{int} = %4.2f MeV\;\;\;,\;\;\;var\in[%4.2f,%4.2f]\;\;\;,\;\;\;\vert Basis\vert = %d$'
    % (OMEGA_INT, parint[0], parint[-1], BASIS_DIM))

with benchmark("Calculate %d-particle %d-dimensional HO ME analytically" %
               (PARTNBR, SPACEDIMS)):
    nmax = 5
    analytical_ev = eigenvalues_harmonic_osci(OMEGA_INT, nmax,
                                              1 * SPACEDIMS)[:N_EIGENV]
    print(np.sqrt(2) * analytical_ev)
ax1.plot(np.sqrt(2) * analytical_ev, 'ro-', label=r'analytical')
leg = ax1.legend(loc='best')
ax1 = fig.add_subplot(122)
ax1.plot(parint, [d[0] for d in eigenvalue_container] /
         (np.sqrt(2) * analytical_ev[0]))
plt.show()
>>>>>>> Stashed changes
