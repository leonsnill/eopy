import gdal, gdalconst


def reproject_raster(inp, resAlg, out, ref=None, dstSRS=None, srcNoData=None, dstNodata=None):
    """

    :param inp:
    :param resAlg:
    :param out:
    :param ref:
    :param dstSRS:
    :param srcNoData:
    :param dstNodata:
    :return:
    """

    GDAL_resAlg = {
        "near": gdalconst.GRA_NearestNeighbour,
        "bilinear": gdalconst.GRA_Bilinear,
        "average": gdalconst.GRA_Average,
        "cubic": gdalconst.GRA_Cubic,
        "mode": gdalconst.GRA_Mode
    }

    if ref is not None:
        src_proj = inp.GetProjection()
        src_trans = inp.GetGeoTransform()

        ref_proj = ref.GetProjection()
        ref_trans = ref.GetGeoTransform()
        xdim = ref.RasterXSize
        ydim = ref.RasterYSize
        bands = inp.RasterCount

        # check datatype:
        if resAlg == 'near':
            dtype = inp.GetRasterBand(1).DataType
        else:
            dtype = 6  # Float32

        resAlg = GDAL_resAlg[resAlg]

        dst = gdal.GetDriverByName('GTiff').Create(out, xdim, ydim, bands, dtype, options=['COMPRESS=DEFLATE'])
        dst.SetGeoTransform(ref_trans)
        dst.SetProjection(ref_proj)

        # check NoData value:
        if srcNoData is not None:
            inp.GetRasterBand(1).SetNoDataValue(srcNoData)
        if dstNodata is not None:
            dst.GetRasterBand(1).SetNoDataValue(dstNodata)
            dst.GetRasterBand(1).Fill(dstNodata)
            gdal.ReprojectImage(inp, dst, src_proj, ref_proj, resAlg)
        else:
            gdal.ReprojectImage(inp, dst, src_proj, ref_proj, resAlg)

        del dst

        return gdal.Open(out)

    else:
        # check NoData value:
        if dstNodata is not None:
            fil = gdal.Warp(out, inp, dstSRS=dstSRS, resampleAlg=resAlg, dstNodata=dstNodata)
        else:
            fil = gdal.Warp(out, inp, dstSRS=dstSRS, resampleAlg=resAlg)

        del fil
        return gdal.Open(out)

