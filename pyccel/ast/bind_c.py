# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------------------#
# This file is part of Pyccel which is released under MIT License. See the LICENSE file or #
# go to https://github.com/pyccel/pyccel/blob/master/LICENSE for full license details.     #
#------------------------------------------------------------------------------------------#
"""
Module describing all elements of the AST needed to represent elements which appear in a Fortran-C binding
file.
"""

from pyccel.ast.basic import PyccelAstNode
from pyccel.ast.core import Module
from pyccel.ast.core import FunctionDef, ClassDef
from pyccel.ast.core import FunctionDefArgument, FunctionDefResult
from pyccel.ast.datatypes import DataType, NativeInteger
from pyccel.ast.variable import Variable

__all__ = (
    'BindCArrayVariable',
    'BindCClassDef',
    'BindCFunctionDef',
    'BindCFunctionDefArgument',
    'BindCFunctionDefResult',
    'BindCModule',
    'BindCPointer',
    'BindCVariable',
    'CLocFunc',
    'C_F_Pointer',
)

# =======================================================================================
#                                    Datatypes
# =======================================================================================

class BindCPointer(DataType):
    """
    Datatype representing a C pointer in Fortran.

    Datatype representing a C pointer in Fortran. This data type is defined
    in the iso_c_binding module.
    """
    __slots__ = ()
    _name = 'bindcpointer'

# =======================================================================================
#                                   Wrapper classes
# =======================================================================================


class BindCFunctionDef(FunctionDef):
    """
    Represents the definition of a C-compatible function.

    Contains the C-compatible version of the function which is
    used for the wrapper.
    As compared to a normal FunctionDef, this version contains
    arguments for the shape of arrays. It should be generated by
    calling `codegen.wrapper.FortranToCWrapper.wrap`.

    Parameters
    ----------
    *args : list
        See FunctionDef.

    original_function : FunctionDef
        The function from which the C-compatible version was created.

    **kwargs : dict
        See FunctionDef.

    See Also
    --------
    pyccel.ast.core.FunctionDef
        The class from which BindCFunctionDef inherits which contains all
        details about the args and kwargs.
    """
    __slots__ = ('_original_function',)
    _attribute_nodes = (*FunctionDef._attribute_nodes, '_original_function')

    def __init__(self, *args, original_function, **kwargs):
        self._original_function = original_function
        super().__init__(*args, **kwargs)
        assert self.name == self.name.lower()
        assert all(isinstance(a, BindCFunctionDefArgument) for a in self._arguments)
        assert all(isinstance(a, BindCFunctionDefResult) for a in self._results)

    @property
    def original_function(self):
        """
        The function which is wrapped by this BindCFunctionDef.

        The original function which would be printed in pure Fortran which is not
        compatible with C.
        """
        return self._original_function

    @property
    def bind_c_arguments(self):
        """
        Get the BindCFunctionDefArguments of the function.

        Return a list of all the arguments passed to the function.
        These objects all have the type BindCFunctionDefArgument so
        shapes and strides are hidden.
        """
        return self._arguments

    @property
    def bind_c_results(self):
        """
        Get the BindCFunctionDefResults of the function.

        Return a list of all the results returned by the function.
        These objects all have the type BindCFunctionDefResult so
        shapes and strides are hidden.
        """
        return self._results

    @property
    def results(self):
        """
        List of all objects returned by the function.

        A list of all objects returned by the function including variables
        which contain array metadata.
        """
        return [ai for a in self._results for ai in a.get_all_function_def_results()]

    @property
    def arguments(self):
        """
        List of all arguments passed to the function.

        List of all arguments passed to the function including variables
        which contain array metadata.
        """
        return [ai for a in self._arguments for ai in a.get_all_function_def_arguments()]

# =======================================================================================


class BindCFunctionDefArgument(FunctionDefArgument):
    """
    Stores all the information necessary to expose an argument to C code.

    Arguments of a C-compatible function may need additional information
    in order to fully construct the object. This class is mostly important
    for array objects. These objects must pass not only the data, but also
    meta-data. Namely the shape and strides for the array in each dimension.
    This information is stored in this class.

    Parameters
    ----------
    var : Variable
        The variable being passed as an argument (with a C-compatible type).

    scope : pyccel.parser.scope.Scope
        The scope in which any arguments to the function should be declared.
        This is used to create the shape and stride variables.

    original_arg_var : Variable
        The variable which was passed to the function currently being wrapped
        in a C-Fortran interface. This variable may have a type which is not
        compatible with C.

    **kwargs : dict
        See FunctionDefArgument.

    See Also
    --------
    pyccel.ast.core.FunctionDefArgument
        The class from which BindCFunctionDefArgument inherits which
        contains all details about the args and kwargs.
    """
    __slots__ = ('_shape', '_strides', '_original_arg_var', '_rank')
    _attribute_nodes = FunctionDefArgument._attribute_nodes + \
                        ('_shape', '_strides', '_original_arg_var')

    def __init__(self, var, scope, original_arg_var, **kwargs):
        name = var.name
        self._rank = original_arg_var.rank
        shape   = [scope.get_temporary_variable(NativeInteger(),
                            name=f'{name}_shape_{i+1}')
                   for i in range(self._rank)]
        strides = [scope.get_temporary_variable(NativeInteger(),
                            name=f'{name}_stride_{i+1}')
                   for i in range(self._rank)]
        self._shape = shape
        self._strides = strides
        self._original_arg_var = original_arg_var
        super().__init__(var, **kwargs)

    @property
    def original_function_argument_variable(self):
        """
        The argument which was passed to the function currently being wrapped.

        The Variable which was passed to the function currently being wrapped
        in a C-Fortran interface. This variable may have a type which is not
        compatible with C.
        """
        return self._original_arg_var

    @property
    def shape(self):
        """
        The shape of the array argument in each dimension.

        A tuple containing the variables which describe the number of
        elements along each dimension of an array argument. These values
        must be passed to any C-compatible function taking an array as an
        argument.
        """
        return self._shape

    @property
    def strides(self):
        """
        The strides of the array argument in each dimension.

        A tuple containing the variables which describe the strides of
        an array argument in each dimension. These values must be passed to
        any C-compatible function taking an array as an argument.
        """
        return self._strides

    def get_all_function_def_arguments(self):
        """
        Get all argument variables which must be printed to fully describe this argument.

        Get a list of all the arguments to the C-compatible function which are
        required in order to fully describe this argument. This includes the data
        for the object itself as well as any sizes or strides necessary to
        define arrays.

        Returns
        -------
        list
            A list of FunctionDefArguments which will be arguments of a BindCFunctionDef.
        """
        args = [self]
        args += [FunctionDefArgument(size) for size in self.shape]
        args += [FunctionDefArgument(stride) for stride in self.strides]
        return args

    def __repr__(self):
        if self.has_default:
            argument = str(self.name)
            value = str(self.value)
            return f'BindCFunctionDefArgument({argument}={value}, inout={self.inout})'
        else:
            return f'BindCFunctionDefArgument({repr(self.name)}, inout={self.inout})'

    @property
    def inout(self):
        """
        Indicates whether the argument may be modified by the function.

        True if the argument may be modified in the function. False if
        the argument remains constant in the function. For array arguments
        the inout status of the sizes and strides are also returned.
        """
        if self._rank:
            return [False] + [False, False]*self._rank
        else:
            return super().inout

# =======================================================================================


class BindCFunctionDefResult(FunctionDefResult):
    """
    Stores all the information necessary to expose a result to C code.

    Results of a C-compatible function may need additional information
    in order to fully construct the object. This class is mostly important
    for array objects. These objects must describe not only the data, but also
    meta-data. Namely the shape for the array in each dimension.
    This information is stored in this class.

    Parameters
    ----------
    var : Variable
        The variable being returned (with a C-compatible type).

    original_res_var : Variable
        The variable which was returned by the function currently being wrapped
        in a C-Fortran interface. This variable may have a type which is not
        compatible with C.

    scope : pyccel.parser.scope.Scope
        The scope in which any arguments to the function should be declared.
        This is used to create the shape and stride variables.

    **kwargs : dict
        See FunctionDefResult.

    See Also
    --------
    pyccel.ast.core.FunctionDefResult
        The class from which BindCFunctionDefResult inherits which
        contains all details about the args and kwargs.
    """
    __slots__ = ('_shape', '_original_res_var')
    _attribute_nodes = FunctionDefResult._attribute_nodes + \
                        ('_shape', '_original_res_var')

    def __init__(self, var, original_res_var, scope, **kwargs):
        name = original_res_var.name
        self._shape   = [scope.get_temporary_variable(NativeInteger(),
                            name=f'{name}_shape_{i+1}')
                         for i in range(original_res_var._rank)]
        self._original_res_var = original_res_var
        super().__init__(var, **kwargs)

    @property
    def original_function_result_variable(self):
        """
        The result returned by the function currently being wrapped.

        The variable which was returned by the function currently being wrapped
        in a C-Fortran interface. This variable may have a type which is not
        compatible with C.
        """
        return self._original_res_var

    @property
    def shape(self):
        """
        The shape of the array result in each dimension.

        A tuple containing the variables which describe the number of
        elements along each dimension of an array result. These values
        must be returned by any C-compatible function returning an array.
        """
        return self._shape

    def get_all_function_def_results(self):
        """
        Get all result variables which must be printed to fully describe this result.

        Get a list of all the results of the C-compatible function which are
        required in order to fully describe this result. This includes the data
        for the object itself as well as any sizes necessary to
        define arrays.

        Returns
        -------
        list
            A list of FunctionDefResults which will be results of a BindCFunctionDef.
        """
        res = [self]
        res += [FunctionDefResult(size) for size in self.shape]
        return res

# =======================================================================================

class BindCModule(Module):
    """
    Represents a Module which only contains functions compatible with C.

    Represents a Module which provides the C-Fortran interface to another module.
    Both functions and module variables are wrapped in order to be compatible with
    C.

    Parameters
    ----------
    *args : tuple
        See `pyccel.ast.core.Module`.

    original_module : Module
        The Module being wrapped.

    variable_wrappers : list of BindCFunctionDef
        A list containing all the functions which expose module variables to C.

    removed_functions : list of FunctionDef
        A list of any functions which weren't translated to BindCFunctionDef
        objects (e.g. private functions).

    **kwargs : dict
        See `pyccel.ast.core.Module`.

    See Also
    --------
    pyccel.ast.core.Module
        The class from which BindCModule inherits which contains all details
        about the args and kwargs.
    """
    __slots__ = ('_orig_mod','_variable_wrappers', '_removed_functions')
    _attribute_nodes = Module._attribute_nodes + ('_orig_mod','_variable_wrappers', '_removed_functions')

    def __init__(self, *args, original_module, variable_wrappers = (), removed_functions = None, **kwargs):
        self._orig_mod = original_module
        self._variable_wrappers = variable_wrappers
        self._removed_functions = removed_functions
        super().__init__(*args, **kwargs)

    @property
    def original_module(self):
        """
        The module which was wrapped.

        The original module for which this object provides the C-Fortran interface.
        """
        return self._orig_mod

    @property
    def variable_wrappers(self):
        """
        Get the wrappers which expose module variables to C.

        Get a list containing all the BindCFunctionDefs which expose module variables to C.
        """
        return self._variable_wrappers

    @property
    def removed_functions(self):
        """
        Get the functions which weren't translated to BindCFunctionDef objects.

        Get a list of the functions which weren't translated to BindCFunctionDef objects.
        This includes private functions and objects for which wrapper support is lacking.
        """
        return self._removed_functions

    @property
    def declarations(self):
        """
        Get the declarations of all module variables.

        In the case of a BindCModule no variables should be declared. Basic variables
        are used directly from the original module and more complex variables require
        wrapper functions.
        """
        return ()

# =======================================================================================

class BindCVariable(Variable):
    """
    A class which wraps a compatible variable from Fortran to make it available in C.

    A class which wraps a compatible variable from Fortran to make it available in C.
    A compatible variable is a variable which can be exposed to C simply using
    iso_c_binding (i.e. no wrapper function is required).

    Parameters
    ----------
    *args : tuple
        See Variable.

    **kwargs : dict
        See Variable.

    See Also
    --------
    Variable : The super class.
    """
    __slots__ = ('_f_name',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._f_name = self._name.lower()

    @property
    def name(self):
        """
        The name of the external variable that should be printed in C.

        The name of the external variable that should be printed in C.
        In order to be compatible with Fortran the name must be printed
        in lower case letters.
        """
        return self._f_name

    @property
    def indexed_name(self):
        """
        The name under which the variable is indexed in the scope.

        The name under which the variable is indexed in the scope. This is
        important in order to be able to collect the original Python name
        used by the user in case of collisions.
        """
        return self._name

# =======================================================================================

class BindCArrayVariable(Variable):
    """
    A class which wraps an array from Fortran to make it available in C.

    A class which wraps an array from Fortran to make it available in C.

    Parameters
    ----------
    *args : tuple
        See Variable.

    wrapper_function : FunctionDef
        The function which can be used to access the array.

    original_variable : Variable
        The original variable in the Fortran code.

    **kwargs : dict
        See Variable.

    See Also
    --------
    Variable : The super class.
    """
    __slots__ = ('_wrapper_function', '_original_variable')
    _attribute_nodes = ('_wrapper_function', '_original_variable')
    def __init__(self, *args, wrapper_function, original_variable, **kwargs):
        self._original_variable = original_variable
        self._wrapper_function = wrapper_function
        super().__init__(*args, **kwargs)

    @property
    def original_variable(self):
        """
        The original variable in the Fortran code.

        The original variable in the Fortran code. This is important in
        order to access the correct type and other details about the
        Variable.
        """
        return self._original_variable

    @property
    def wrapper_function(self):
        """
        The function which can be used to access the array.

        The function which can be used to access the array. The function
        must return the pointer to the raw data and information about
        the shape.
        """
        return self._wrapper_function

# =======================================================================================

class BindCClassDef(ClassDef):
    """
    Represents a class which is compatible with C.

    Represents a class which is compatible with C. This means that it stores
    C-compatible versions of class methods and getters and setters for class
    variables.

    Parameters
    ----------
    original_class : ClassDef
        The class being wrapped.

    **kwargs : dict
        See ClassDef.
    """
    __slots__ = ('_original_class',)

    def __init__(self, original_class, **kwargs):
        self._original_class = original_class
        super().__init__(original_class.name, **kwargs)

# =======================================================================================
#                                   Utility functions
# =======================================================================================

class CLocFunc(PyccelAstNode):
    """
    Creates a C-compatible pointer to the argument.

    Class representing the iso_c_binding function cloc which returns a valid
    C pointer to the location where an object can be found.

    Parameters
    ----------
    argument : Variable
        The object which should be pointed to.

    result : Variable of dtype BindCPointer
        The variable where the C-compatible pointer should be stored.
    """
    __slots__ = ('_arg', '_result')
    _attribute_nodes = ()

    def __init__(self, argument, result):
        self._arg = argument
        self._result = result
        assert result.dtype is BindCPointer()
        super().__init__()

    @property
    def arg(self):
        """
        Pointer target.

        Object which will be pointed at by the result pointer.
        """
        return self._arg

    @property
    def result(self):
        """
        The variable where the C-compatible pointer should be stored.

        The variable where the C-compatible pointer of dtype BindCPointer
        should be stored.
        """
        return self._result

# =======================================================================================

class C_F_Pointer(PyccelAstNode):
    """
    Creates a Fortran array pointer from a C pointer and size information.

    Represents the iso_c_binding function C_F_Pointer which takes a pointer
    to an object in C (with dtype BindCPointer) and a list of sizes and returns
    a Fortran array pointer.

    Parameters
    ----------
    c_expr : Variable of dtype BindCPointer
        The Variable containing the C pointer.

    f_expr : Variable
        The Variable containing the resulting array.

    shape : list of Variables
        A list describing the Variables which dictate the size of the array in each dimension.
    """
    __slots__ = ('_c_expr', '_f_expr', '_shape')
    _attribute_nodes = ('_c_expr', '_f_expr', '_shape')

    def __init__(self, c_expr, f_expr, shape = ()):
        self._c_expr = c_expr
        self._f_expr = f_expr
        self._shape = shape
        super().__init__()

    @property
    def c_pointer(self):
        """
        The Variable containing the C pointer.

        The Variable of dtype BindCPointer which contains the C pointer.
        """
        return self._c_expr

    @property
    def f_array(self):
        """
        The Variable containing the resulting array.

        The Variable where the array pointer will be stored.
        """
        return self._f_expr

    @property
    def shape(self):
        """
        A list of the sizes of the array in each dimension.

        A list describing the Variables which are passed as arguments, in order to
        determine the size of the array in each dimension.
        """
        return self._shape
