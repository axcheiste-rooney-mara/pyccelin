"""
Module responsible for the creation of the json files containing the default configuration for each available compiler.
This module only needs to be imported once. Once the json files have been generated they can be used directly thus
avoiding the need for a large number of imports
"""
import glob
import os
import sys
import sysconfig
from numpy import get_include as get_numpy_include
from pyccel import __version__ as pyccel_version

gfort_info = {'exec' : 'gfortran',
              'mpi_exec' : 'mpif90',
              'language': 'fortran',
              'module_output_flag': '-J',
              'debug_flags': ("-fcheck=bounds","-g","-O0"),
              'release_flags': ("-O3","-funroll-loops",),
              'general_flags' : ('-fPIC',),
              'standard_flags' : ('-std=f2003',),
              'mpi': {
                  },
              'openmp': {
                  'flags' : ('-fopenmp',),
                  'libs'  : ('gomp',),
                  },
              'openacc': {
                  'flags' : ("-ta=multicore", "-Minfo=accel"),
                  },
              'family': 'GNU',
              }
if sys.platform == "win32":
    gfort_info['mpi_exec'] = 'gfortran'
    gfort_info['mpi']['flags']    = ('-D','USE_MPI_MODULE')
    gfort_info['mpi']['libs']     = ('msmpi',)
    gfort_info['mpi']['includes'] = (os.environ["MSMPI_INC"].rstrip('\\'),)
    gfort_info['mpi']['libdirs']  = (os.environ["MSMPI_LIB64"].rstrip('\\'),)

#------------------------------------------------------------
ifort_info = {'exec' : 'ifort',
              'mpi_exec' : 'mpiifort',
              'language': 'fortran',
              'module_output_flag': '-module',
              'debug_flags': ("-check=bounds","-g","-O0"),
              'release_flags': ("-O3","-funroll-loops",),
              'general_flags' : ('-fPIC',),
              'standard_flags' : ('-std=f2003',),
              'openmp': {
                  'flags' : ('-fopenmp','-nostandard-realloc-lhs'),
                  'libs'  : ('iomp5',),
                  },
              'openacc': {
                  'flags' : ("-ta=multicore", "-Minfo=accel"),
                  },
              'family': 'intel',
              }

#------------------------------------------------------------
pgfortran_info = {'exec' : 'pgfortran',
              'mpi_exec' : 'pgfortran',
              'language': 'fortran',
              'module_output_flag': '-module',
              'debug_flags': ("-Mbounds","-g","-O0"),
              'release_flags': ("-O3","-Munroll",),
              'general_flags' : ('-fPIC',),
              'standard_flags' : ('-Mstandard',),
              'openmp': {
                  'flags' : ('-mp',),
                  },
              'openacc': {
                  'flags' : ("-acc"),
                  },
              'family': 'PGI',
              }

#------------------------------------------------------------
nvfort_info = {'exec' : 'nvfort',
              'mpi_exec' : 'mpifort',
              'language': 'fortran',
              'module_output_flag': '-module',
              'debug_flags': ("-Mbounds","-g","-O0"),
              'release_flags': ("-O3","-Munroll",),
              'general_flags' : ('-fPIC',),
              'standard_flags' : ('-Mstandard',),
              'openmp': {
                  'flags' : ('-mp',),
                  },
              'openacc': {
                  'flags' : ("-acc"),
                  },
              'family': 'nvidia',
              }

#------------------------------------------------------------
gcc_info = {'exec' : 'gcc',
            'mpi_exec' : 'mpicc',
            'language': 'c',
            'debug_flags': ("-g","-O0"),
            'release_flags': ("-O3","-funroll-loops",),
            'general_flags' : ('-fPIC',),
            'standard_flags' : ('-std=c99',),
            'mpi': {
                },
            'openmp': {
                'flags' : ('-fopenmp',),
                'libs'  : ('gomp',),
                },
            'openacc': {
                'flags' : ("-ta=multicore", "-Minfo=accel"),
                },
            'family': 'GNU',
            }
if sys.platform == "darwin":
    gcc_info['openmp']['flags'] = ("-Xpreprocessor",'-fopenmp')
    gcc_info['openmp']['libs'] = ('omp',)
    gcc_info['openmp']['libdirs'] = ('/usr/local/opt/libomp/lib',)
    gcc_info['openmp']['includes'] = ('/usr/local/opt/libomp/include',)
elif sys.platform == "win32":
    gcc_info['mpi_exec'] = 'gcc'
    gcc_info['mpi']['flags']    = ('-D','USE_MPI_MODULE')
    gcc_info['mpi']['libs']     = ('msmpi',)
    gcc_info['mpi']['includes'] = (os.environ["MSMPI_INC"].rstrip('\\'),)
    gcc_info['mpi']['libdirs']  = (os.environ["MSMPI_LIB64"].rstrip('\\'),)

#------------------------------------------------------------
icc_info = {'exec' : 'icx',
            'mpi_exec' : 'mpicc',
            'language': 'c',
            'debug_flags': ("-g","-O0"),
            'release_flags': ("-O3","-funroll-loops",),
            'general_flags' : ('-fPIC',),
            'standard_flags' : ('-std=c99',),
            'openmp': {
                'flags' : ('-fopenmp',),
                },
            'openacc': {
                'flags' : ("-ta=multicore", "-Minfo=accel"),
                },
            'family': 'intel',
            }

#------------------------------------------------------------
pgcc_info = {'exec' : 'pgcc',
            'mpi_exec' : 'pgcc',
            'language': 'c',
            'debug_flags': ("-g","-O0"),
            'release_flags': ("-O3","-Munroll",),
            'general_flags' : ('-fPIC',),
            'standard_flags' : ('-std=c99',),
            'openmp': {
                'flags' : ('-mp',),
                },
            'openacc': {
                'flags' : ("-acc"),
                },
            'family': 'PGI',
            }

#------------------------------------------------------------
nvc_info = {'exec' : 'nvc',
            'mpi_exec' : 'mpicc',
            'language': 'c',
            'debug_flags': ("-g","-O0"),
            'release_flags': ("-O3","-Munroll",),
            'general_flags' : ('-fPIC',),
            'standard_flags' : ('-std=c99',),
            'openmp': {
                'flags' : ('-mp',),
                },
            'openacc': {
                'flags' : ("-acc"),
                },
            'family': 'nvidia',
            }

#------------------------------------------------------------
def change_to_lib_flag(lib):
    """
    Convert a library to a library flag.

    Take a library file and return the associated library
    flag by stripping the library suffix. If the file does
    not begin with the expected 'lib' prefix then it is returned
    unchanged.

    Parameters
    ----------
    lib : str
        The library file.

    Returns
    -------
    str
        The library flag.
    """
    if lib.startswith('lib'):
        end = len(lib)
        if lib.endswith('.a'):
            end = end-2
        if lib.endswith('.so'):
            end = end-3
        if lib.endswith('.dylib'):
            end = end-5
        return '-l{}'.format(lib[3:end])
    else:
        return lib

config_vars = sysconfig.get_config_vars()

python_info = {
        "libs" : config_vars.get("LIBM","").split(), # Strip -l from beginning
        'python': {
            'flags' : config_vars.get("CFLAGS","").split()\
                + config_vars.get("CC","").split()[1:],
            'includes' : [*config_vars.get("INCLUDEPY","").split(), get_numpy_include()],
            "shared_suffix" : config_vars['EXT_SUFFIX'],
            }
        }

if sys.platform == "win32":
    expected_dir = config_vars["prefix"]
    version = config_vars["VERSION"]
    python_libs = glob.glob(f"{expected_dir}/python{version}.dll")
    if python_libs:
        python_info['python']['dependencies'] = tuple(python_libs)
    else:
        python_info['python']['libs'] = (f'python{version}',)
        python_info['python']['libdirs'] = config_vars.get("installed_base","").split()

else:
    # Collect library according to python config file
    expected_dir = config_vars["LIBDIR"]
    version = config_vars["VERSION"]
    python_shared_libs = glob.glob(f"{expected_dir}/libpython{version}*")

    # Collect a list of all possible libraries matching the name in the configs
    # which can be found on the system
    shared_ending = '.dylib' if sys.platform == "darwin" else '.so'
    possible_shared_lib = [l for l in python_shared_libs if shared_ending in l]
    possible_static_lib = [l for l in python_shared_libs if '.a' in l]

    # Prefer saving the library as a dependency where possible to avoid
    # unnecessary libdirs which may lead to the wrong versions being linked
    # for other libraries
    # Prefer a shared library as it requires less memory
    if possible_shared_lib:
        if len(possible_shared_lib)>1:
            preferred_lib = [l for l in possible_shared_lib if l.endswith(shared_ending)]
            if preferred_lib:
                possible_shared_lib = preferred_lib

        python_info['python']['dependencies'] = (possible_shared_lib[0],)
    elif possible_static_lib:
        if len(possible_static_lib)>1:
            preferred_lib = [l for l in possible_static_lib if l.endswith('.a')]
            if preferred_lib:
                possible_static_lib = preferred_lib
        python_info['python']['dependencies'] = (possible_static_lib[0],)
    else:
        # If the proposed library does not exist use different config flags
        # to specify the library
        linker_flags = [change_to_lib_flag(l) for l in
                        config_vars.get("LDSHARED","").split() + \
                        config_vars.get("LIBRARY","").split()[1:]]
        python_info['python']['libs'] = [l[2:] for l in linker_flags if l.startswith('-l')]
        python_info['python']['libdirs'] = [l[2:] for l in linker_flags if l.startswith('-L')] + \
                            config_vars.get("LIBPL","").split()+config_vars.get("LIBDIR","").split()

#------------------------------------------------------------
gcc_info.update(python_info)
gfort_info.update(python_info)
icc_info.update(python_info)
ifort_info.update(python_info)
pgcc_info.update(python_info)
pgfortran_info.update(python_info)
nvc_info.update(python_info)
nvfort_info.update(python_info)

available_compilers = {('GNU', 'c') : gcc_info,
                       ('GNU', 'fortran') : gfort_info,
                       ('intel', 'c') : icc_info,
                       ('intel', 'fortran') : ifort_info,
                       ('PGI', 'c') : pgcc_info,
                       ('PGI', 'fortran') : pgfortran_info,
                       ('nvidia', 'c') : nvc_info,
                       ('nvidia', 'fortran') : nvfort_info}

vendors = ('GNU','intel','PGI','nvidia')
