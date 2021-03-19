import xarray as xr
import numpy as np
import dask as da

def check(user_variable,
          var_name='variable',
          data_type=None,
          max_dimensions=None,
          min_dimensions=None,
          dimensions=None,
          shape=None,
          is_xarray=None,
          is_none=None,
          comparison=None,
          unchunked_dims=None):
    '''
    Function of data checks for use in wrapper functions.

    user_variable : :class:`xarray.DataArray` or :class:`numpy.ndarray`:
        Variable of interest

    data_type : :class:`type` or :type:`tuple of types`:
        Desired data_type of user_variable
        ex: data_type=np.ndarray

    max_dimensions : :class:`tuple`:
        Maximum number of dimensions needed from user_variable for function
        ex: min_dimensions=(3) or min_dimensions=3

    min_dimensions : :class:`tuple`:
        Minimum number of dimensions needed from user_variable for function
        ex: min_dimensions=(3) or min_dimensions=3

    dimensions : :class:`tuple`:
        Number of dimensions needed from user_variable for function
        ex: min_dimensions=(3) or min_dimensions=3

    shape : :class:`tuple`:
        Checks user_variable's shape
        ex: shape=(3, 3, 3) or shape=(3,3,3)

    is_xarray : :class:`bool`:
        Checking that user_variable is of class xarray.DataArray.
        Valid inputs are True or False

    is_none : :class:`NoneType`:
        Checking that user_variable is of class NoneType.
        Valid input is None

    comparison : :class:`int`:
        Checks that user_variable is the correct type
        ex: check(user_variable, comparison=

    unchunked_dims : :class:`tuple`:
        Checks for unchunked dimensions in user_variable
        ex: check(user_variable, unchunked_dims=[3]) *must include brackets*

    '''
    if data_type is not None:
        if not isinstance(user_variable, data_type):
            raise Exception(var_name + " failed data_type check")

    if dimensions is not None:
        if not (user_variable.ndim == dimensions):
            raise Exception(var_name + " failed dimensions check")

    if shape is not None:
        if not (user_variable.shape == shape):
            raise Exception(var_name + " failed shape check")

    if is_none is not None:
        if is_none is True:
            if user_variable is not None:
                raise Exception(var_name + " is not None")
        if is_none is False:
            if user_variable is None:
                raise Exception(var_name + " is None")

    if min_dimensions is not None:
        if not (user_variable.ndim >= min_dimensions):
            raise Exception(var_name + " failed min_dimensions check")

    if max_dimensions is not None:
        if not (user_variable.ndim <= max_dimensions):
            raise Exception(var_name + " failed max_dimensions check")

    if comparison is not None:
        if not (user_variable == comparison):
            raise Exception(var_name + " failed comparison check")

    #
    # Xarray specific checks
    #

    if is_xarray is not None:
        if is_xarray is True:
            if not isinstance(user_variable, xr.DataArray):
                # print(var_name + " is not xarray.DataArray, reformatting...")
                return False
            else: pass
        if is_xarray is False:
            if isinstance(user_variable, xr.DataArray):
                pass
                # raise Exception(var_name + " is an xarray.DataArray")
            else:
                # print(var_name + " is not xarray.DataArray, reformatting...")
                return True

    if unchunked_dims is not None:
        for dim in unchunked_dims:
            if len(user_variable.chunks[dim]) > 1:
                raise Exception(var_name +
                                " must not be chunked along dimension " +
                                str(dim))

    return True