import gdal


def array_to_geotiff(inp_array, out_file, inp_img=None, gt=None, pj=None, nodata=None, compress=False):
    """
    Export numpy array to GeoTiff by providing either a reference GDAL raster object or information on the
    image transform and projection.

    Args:
        inp_array: Array to be exported. Array dtype will be the output dtype.
        out_file: Output filename.
        inp_img: (optional) Reference gdal raster object.
        gt: (optional) Geotransform parameters as obtained from .GetGeoTransform()
        pj: (optional) Projection as obtained from .GetProjection()
        nodata: (optional) Output no data value.
        compress: Use compression (COMPRESS=DEFLATE) (default = False).

    Returns: GDAL raster object.

    """
    # datatype lookup dict
    np2gdal_datatype = {
        "bool": 1,
        "uint8": 1,
        "int8": 1,
        "uint16": 2,
        "int16": 3,
        "uint32": 4,
        "int32": 5,
        "int64": 6,
        "float32": 6,
        "float64": 7,
        "complex64": 10,
        "complex128": 11,
    }

    # get array dimensions
    if len(inp_array.shape) > 2:
        xdim = inp_array.shape[2]
        ydim = inp_array.shape[1]
        zdim = inp_array.shape[0]
    else:
        xdim = inp_array.shape[1]
        ydim = inp_array.shape[0]
        zdim = 1

    # check for reference image and retrieve transform and projection
    if inp_img:
        gt = inp_img.GetGeoTransform()
        pj = inp_img.GetProjection()

    # translate array datatype to GDAL datatype
    dtype = np2gdal_datatype[str(inp_array.dtype)]

    # initialise driver
    driver = gdal.GetDriverByName('GTiff')

    # check if output .tif should be compressed and create output data source
    if compress:
        dst_dataset = driver.Create(out_file, xdim, ydim, zdim, dtype, options=['COMPRESS=DEFLATE'])
    else:
        dst_dataset = driver.Create(out_file, xdim, ydim, zdim, dtype)

    # set transform and projection
    dst_dataset.SetGeoTransform(gt)
    dst_dataset.SetProjection(pj)

    # write data to disc
    # if multi-band iterate over z-dimension
    if zdim > 1:
        for i in range(zdim):
            w_array = inp_array[i, :, :]
            out_band = dst_dataset.GetRasterBand(i+1)
            #if nodata:
            out_band.SetNoDataValue(nodata)
            out_band.WriteArray(w_array)
    else:
        out_band = dst_dataset.GetRasterBand(1)
        #if nodata:
        out_band.SetNoDataValue(nodata)
        out_band.WriteArray(inp_array)

    dst_dataset = out_band = None

    return gdal.Open(out_file)
