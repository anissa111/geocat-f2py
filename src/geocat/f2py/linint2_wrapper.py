import numpy as np
import xarray as xr
from dask.array.core import map_blocks
from .errors import (ChunkError, DimensionError, CoordinateError)
from .fortran import (dlinint1, dlinint2, dlinint2pts)
from .missing_values import (fort2py_msg, py2fort_msg)
from .sanity_checks import (sanity_check)

# Dask Wrappers _<funcname>()
# These Wrapper are executed within dask processes, and should do anything that
# can benefit from parallel excution.

def _linint1(xi, fi, xo, icycx, msg_py, shape):
    # ''' signature : fo = dlinint1(xi,fi,xo,[icycx,xmsg,iopt])
    # missing value handling
    fi, msg_py, msg_fort = py2fort_msg(fi, msg_py=msg_py)
    # fortran call
    fo = dlinint1(xi, fi, xo, icycx=icycx, xmsg=msg_fort, )
    # numpy and reshape
    fo = np.asarray(fo)
    fo = fo.reshape(shape)
    # missing value handling
    fi, msg_fort, msg_py = fort2py_msg(fi, msg_fort=msg_fort, msg_py=msg_py)
    fo, msg_fort, msg_py = fort2py_msg(fo, msg_fort=msg_fort, msg_py=msg_py)
    return fo


def _linint2(xi, yi, fi, xo, yo, icycx, msg_py, shape):
    # ''' signature : fo = dlinint2(xi,yi,fi,xo,yo,[icycx,xmsg,iopt])
    # missing value handling
    fi, msg_py, msg_fort = py2fort_msg(fi, msg_py=msg_py)
    # fortran call
    fo = dlinint2(xi, yi, fi, xo, yo, icycx=icycx, xmsg=msg_fort, )
    # numpy and reshape
    fo = np.asarray(fo)
    fo = fo.reshape(shape)
    # missing value handling
    fort2py_msg(fi, msg_fort=msg_fort, msg_py=msg_py)
    fort2py_msg(fo, msg_fort=msg_fort, msg_py=msg_py)
    return fo


def _linint2pts(xi, yi, fi, xo, yo, icycx, msg_py, shape):
    # ''' signature : fo = dlinint2pts(xi,yi,fi,xo,yo,[icycx,xmsg])
    # missing value handling
    fi, msg_py, msg_fort = py2fort_msg(fi, msg_py=msg_py)
    # fortran call
    fo = dlinint2pts(xi, yi, fi, xo, yo, icycx=icycx, xmsg=msg_fort, )
    # numpy and reshape
    fo = np.asarray(fo)
    fo = fo.reshape(shape)
    # missing value handling
    fort2py_msg(fi, msg_fort=msg_fort, msg_py=msg_py)
    fort2py_msg(fo, msg_fort=msg_fort, msg_py=msg_py)
    return fo


# Outer Wrappers <funcname>()
# These Wrappers are excecuted in the __main__ python process, and should be
# used for any tasks which would not benefit from parallel execution.

def linint1(fi, xo, xi=None, icycx=0, msg_py=None):
    # ''' signature : fo = dlinint1(xi,fi,xo,[icycx,xmsg,iopt])

    # ''' Start of boilerplate
    if isinstance(fi, np.ndarray):
        sanity_check(xi, var_name='xi', is_none=False)

        fi = xr.DataArray(
                fi,
            )
        fi_chunk = dict([(k, v) for (k, v) in zip(list(fi.dims), list(fi.shape))])

        fi = xr.DataArray(
            fi.data,
            coords={
                fi.dims[-1]: xi,
            },
            dims=fi.dims,
        ).chunk(fi_chunk)

    xi = fi.coords[fi.dims[-1]]

    # ensure rightmost dimensions of input are not chunked
    sanity_check(fi, var_name="fi", unchunked_dims=[-1])

# fi data structure elements and autochunking
    fi_chunks = list(fi.dims)
    fi_chunks[:-1] = [(k, 1) for (k, v) in zip(list(fi.dims)[:-1], list(fi.chunks)[:-1])]
    fi_chunks[-1:] = [(k, v[0]) for (k, v) in zip(list(fi.dims)[-1:], list(fi.chunks)[-1:])]
    fi_chunks = dict(fi_chunks)
    fi = fi.chunk(fi_chunks)

    # fo datastructure elements
    fo_chunks = list(fi.chunks)
    fo_chunks[-1:] = (xo.shape,)
    fo_chunks = tuple(fo_chunks)
    fo_shape = tuple(a[0] for a in list(fo_chunks))
    fo_coords = {
        k: v for (k, v) in fi.coords.items()
    }
    fo_coords[fi.dims[-1]] = xo
    # ''' end of boilerplate

    fo = map_blocks(
        _linint1,
        xi,
        fi.data,
        xo,
        icycx,
        msg_py,
        fo_shape,
        chunks=fo_chunks,
        dtype=fi.dtype,
        drop_axis=[fi.ndim - 1],
        new_axis=[fi.ndim - 1],
    )

    fo = xr.DataArray(fo.compute(), attrs=fi.attrs, dims=fi.dims, coords=fo_coords)
    return fo


def linint2(fi, xo, yo, xi=None, yi=None, icycx=0, msg_py=None):
    # ''' signature : fo = dlinint2(xi,yi,fi,xo,yo,[icycx,xmsg,iopt])

    '''
    Interpolates a regular grid to a rectilinear one using bi-linear
    interpolation.
    
    linint2 uses bilinear interpolation to interpolate from one
    rectilinear grid to another. The input grid may be cyclic in the x
    direction. The interpolation is first performed in the x direction,
    and then in the y direction.
    
    Args:
        fi (:class:`xarray.DataArray` or :class:`numpy.ndarray`):
            An array of two or more dimensions. If xi is passed in as an
            argument, then the size of the rightmost dimension of fi
            must match the rightmost dimension of xi. Similarly, if yi
            is passed in as an argument, then the size of the second-
            rightmost dimension of fi must match the rightmost dimension
            of yi.
            
            If missing values are present, then linint2 will perform the
            bilinear interpolation at all points possible, but will
            return missing values at coordinates which could not be
            used.
            
            Note:
                This variable must be
                supplied as a :class:`xarray.DataArray` in order to copy
                the dimension names to the output. Otherwise, default
                names will be used.
        
        xo (:class:`xarray.DataArray` or :class:`numpy.ndarray`):
            A one-dimensional array that specifies the X coordinates of
            the return array. It must be strictly monotonically
            increasing, but may be unequally spaced.
            
            For geo-referenced data, xo is generally the longitude
            array.
            
            If the output coordinates (xo) are outside those of the
            input coordinates (xi), then the fo values at those
            coordinates will be set to missing (i.e. no extrapolation is
            performed).
        
        yo (:class:`xarray.DataArray` or :class:`numpy.ndarray`):
            A one-dimensional array that specifies the Y coordinates of
            the return array. It must be strictly monotonically
            increasing, but may be unequally spaced.
            
            For geo-referenced data, yo is generally the latitude array.
            
            If the output coordinates (yo) are outside those of the
            input coordinates (yi), then the fo values at those
            coordinates will be set to missing (i.e. no extrapolation is
            performed).
        
        xi (:class:`numpy.ndarray`):
            An array that specifies the X coordinates of the fi array.
            Most frequently, this is a 1D strictly monotonically
            increasing array that may be unequally spaced. In some
            cases, xi can be a multi-dimensional array (see next
            paragraph). The rightmost dimension (call it nxi) must have
            at least two elements, and is the last (fastest varying)
            dimension of fi.
            
            If xi is a multi-dimensional array, then each nxi subsection
            of xi must be strictly monotonically increasing, but may be
            unequally spaced. All but its rightmost dimension must be
            the same size as all but fi's rightmost two dimensions.
            
            For geo-referenced data, xi is generally the longitude
            array.
            
            Note:
                If fi is of type :class:`xarray.DataArray` and xi is
                left unspecified, then the rightmost coordinate
                dimension of fi will be used. If fi is not of type
                :class:`xarray.DataArray`, then xi becomes a mandatory
                parameter. This parameter must be specified as a keyword
                argument.
       
        yi (:class:`numpy.ndarray`):
            An array that specifies the Y coordinates of the fi array.
            Most frequently, this is a 1D strictly monotonically
            increasing array that may be unequally spaced. In some
            cases, yi can be a multi-dimensional array (see next
            paragraph). The rightmost dimension (call it nyi) must have
            at least two elements, and is the second-to-last dimension
            of fi.
            
            If yi is a multi-dimensional array, then each nyi subsection
            of yi must be strictly monotonically increasing, but may be
            unequally spaced. All but its rightmost dimension must be
            the same size as all but fi's rightmost two dimensions.
            
            For geo-referenced data, yi is generally the latitude array.
            
            Note:
                If fi is of type :class:`xarray.DataArray` and xi is
                left unspecified, then the second-to-rightmost
                coordinate dimension of fi will be used. If fi is not of
                type :class:`xarray.DataArray`, then xi becomes a
                mandatory parameter. This parameter must be specified as
                a keyword argument.
        
        icycx (:obj:`bool`):
            An option to indicate whether the rightmost dimension of fi
            is cyclic. This should be set to True only if you have
            global data, but your longitude values don't quite wrap all
            the way around the globe. For example, if your longitude
            values go from, say, -179.75 to 179.75, or 0.5 to 359.5,
            then you would set this to True.
       
        msg_py (:obj:`numpy.number`):
            A numpy scalar value that represent a missing value in fi.
            This argument allows a user to use a missing value scheme
            other than NaN or masked arrays, similar to what NCL allows.
        
    Returns:
        :class:`xarray.DataArray`: The interpolated grid. If the *meta*
        parameter is True, then the result will include named dimensions
        matching the input array. The returned value will have the same
        dimensions as fi, except for the rightmost two dimensions which
        will have the same dimension sizes as the lengths of yo and xo.
        The return type will be double if fi is double, and float
        otherwise.
    '''

    # ''' Start of boilerplate
    sanity_check(fi, var_name='fi', min_dimensions=2)

    if isinstance(fi, np.ndarray):
        sanity_check(xi, var_name='xi', is_none=False)
        sanity_check(yi, var_name='yi', is_none=False)

        fi = xr.DataArray(
            fi,
        )
        fi_chunk = dict([(k, v) for (k, v) in zip(list(fi.dims), list(fi.shape))])

        fi = xr.DataArray(
            fi.data,
            coords={
                fi.dims[-1]: xi,
                fi.dims[-2]: yi,
            },
            dims=fi.dims,
        ).chunk(fi_chunk)

    xi = fi.coords[fi.dims[-1]]
    yi = fi.coords[fi.dims[-2]]

    # ensure rightmost dimensions of input are not chunked
    sanity_check(fi, var_name="fi", unchunked_dims=[-1,-2])

    # fi data structure elements and autochunking
    fi_chunks = list(fi.dims)
    fi_chunks[:-2] = [(k, 1) for (k, v) in zip(list(fi.dims)[:-2], list(fi.chunks)[:-2])]
    fi_chunks[-2:] = [(k, v[0]) for (k, v) in zip(list(fi.dims)[-2:], list(fi.chunks)[-2:])]
    fi_chunks = dict(fi_chunks)
    fi = fi.chunk(fi_chunks)

    # fo datastructure elements
    fo_chunks = list(fi.chunks)
    fo_chunks[-2:] = (yo.shape, xo.shape)
    fo_chunks = tuple(fo_chunks)
    fo_shape = tuple(a[0] for a in list(fo_chunks))
    fo_coords = {
        k: v for (k, v) in fi.coords.items()
    }
    fo_coords[fi.dims[-1]] = xo
    fo_coords[fi.dims[-2]] = yo
    # ''' end of boilerplate

    fo = map_blocks(
        _linint2,
        yi,
        xi,
        fi.data,
        yo,
        xo,
        icycx,
        msg_py,
        fo_shape,
        chunks=fo_chunks,
        dtype=fi.dtype,
        drop_axis=[fi.ndim - 2, fi.ndim - 1],
        new_axis=[fi.ndim - 2, fi.ndim - 1],
    )
    fo = xr.DataArray(fo.compute(), attrs=fi.attrs, dims=fi.dims, coords=fo_coords)
    return fo


def linint2pts(fi, xo, yo, icycx=0, msg_py=None):
    # ''' signature : fo = dlinint2pts(xi,yi,fi,xo,yo,[icycx,xmsg,iopt])
    
    '''
    Interpolates from a rectilinear grid to an unstructured grid or locations using bilinear interpolation.
    
    Args:
        
        fi (:class:`xarray.DataArray` or :class:`numpy.ndarray`):
            An array of two or more dimensions. The two rightmost
            dimensions (nyi x nxi) are the dimensions to be used in
            the interpolation. If user-defined missing values are
            present (other than NaNs), the value of `msg` must be
            set appropriately.
        
        xo (:class:`xarray.DataArray` or :class:`numpy.ndarray`):
            A One-dimensional array that specifies the X (longitude)
            coordinates of the unstructured grid.
        
        yo (:class:`xarray.DataArray` or :class:`numpy.ndarray`):
            A One-dimensional array that specifies the Y (latitude)
            coordinates of the unstructured grid. It must be the same
            length as `xo`.
        
        icycx (:obj:`bool`):
            An option to indicate whether the rightmost dimension of fi
            is cyclic. This should be set to True only if you have
            global data, but your longitude values don't quite wrap all
            the way around the globe. For example, if your longitude
            values go from, say, -179.75 to 179.75, or 0.5 to 359.5,
            then you would set this to True.
       
        msg_py (:obj:`numpy.number`):
            A numpy scalar value that represent a missing value in fi.
            This argument allows a user to use a missing value scheme
            other than NaN or masked arrays, similar to what NCL allows.

    Returns:
        :class:`numpy.ndarray`: The returned value will have the same
        dimensions as `fi`, except for the rightmost dimension which will
        have the same dimension size as the length of `yo` and `xo`. The
        return type will be double if fi is double, and float otherwise.
    
    Description:
        The inint2_points uses bilinear interpolation to interpolate from
        a rectilinear grid to an unstructured grid.
        
        If missing values are present, then linint2_points will perform the
        piecewise linear interpolation at all points possible, but will return
        missing values at coordinates which could not be used. If one or more
        of the four closest grid points to a particular (xo,yo) coordinate
        pair are missing, then the return value for this coordinate pair will
        be missing.
        
        If the user inadvertently specifies output coordinates (xo,yo) that
        are outside those of the input coordinates (xi,yi), the output value
        at this coordinate pair will be set to missing as no extrapolation
        is performed.
        
        linint2_points is different from linint2 in that `xo` and `yo` are
        coordinate pairs, and need not be monotonically increasing. It is
        also different in the dimensioning of the return array.
        
        This function could be used if the user wanted to interpolate gridded
        data to, say, the location of rawinsonde sites or buoy/xbt locations.
        
        Warning: if xi contains longitudes, then the xo values must be in the
        same range. In addition, if the xi values span 0 to 360, then the xo
        values must also be specified in this range (i.e. -180 to 180 will not work).
    '''
    # Basic sanity checks

    sanity_check(fi, var_name="fi", min_dimensions=2)

    # ''' Start of boilerplate
    if not isinstance(fi, xr.DataArray):
        raise Exception("fi is required to be an xarray.DataArray")

    xi = fi.coords[fi.dims[-1]]
    yi = fi.coords[fi.dims[-2]]

    if xo.shape != yo.shape:
        raise Exception("xo and yo, be be of equal length")

    # ensure rightmost dimensions of input are not chunked
    sanity_check(fi, var_name="fi", unchunked_dims=[-1,-2])

    # fo datastructure elements
    fo_chunks = list(fi.chunks)
    fo_chunks[-2:] = (xo.shape,)
    fo_chunks = tuple(fo_chunks)
    fo_shape = tuple(a[0] for a in list(fo_chunks))
    fo_coords = {
        k: v for (k, v) in fi.coords.items()
    }
    # fo_coords.remove(fi.dims[-1]) # this dimension dissapears
    fo_coords[fi.dims[-1]] = xo  # remove this line omce dims are figured out
    fo_coords[fi.dims[-2]] = yo  # maybe replace with 'pts'
    # ''' end of boilerplate

    fo = map_blocks(
        _linint2pts,
        yi,
        xi,
        fi.data,
        yo,
        xo,
        icycx,
        msg_py,
        fo_shape,
        chunks=fo_chunks,
        dtype=fi.dtype,
        drop_axis=[fi.ndim - 2, fi.ndim - 1],
        new_axis=[fi.ndim - 2],
    )
    fo = xr.DataArray(fo.compute(), attrs=fi.attrs)
    return fo
