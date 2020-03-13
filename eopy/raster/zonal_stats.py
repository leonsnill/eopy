import gdal
import osr
import ogr
from tqdm import tqdm
import numpy as np
from eopy.raster import extent_to_geom, extent


def zonal_stats(shp, img, stats=None, percentiles=None, attributes=None, img_scale=None):
    """
    Calculates zonal statistics.

    Args:
        shp: Polygon vector file.
        img: Image to calculate statistics on.
        stats: (optional) List of numpy based statistical operations, e.g. 'mean', 'std', 'median'
        percentiles: (optional) List of percentiles to calculate, e.g. [10, 90]
        attributes: (optional) Attribute fields to append to list
        img_scale: (optional) Scale factor of image, e.g. 10000 -> img = img/10000

    Returns: List of zonal statistics.

    """

    # read data
    if isinstance(img, str):
        img = gdal.Open(img)

    if isinstance(shp, str):
        shp = ogr.Open(shp)

    lyr = shp.GetLayer()

    # retrieve image georeference info and extent
    gt = img.GetGeoTransform()
    ext_img = extent(img)
    ext_img_geom = extent_to_geom(ext_img)

    # check Coordinate Reference System
    lyr_crs = lyr.GetSpatialRef()  # shp crs
    img_crs = osr.SpatialReference()
    img_crs.ImportFromWkt(img.GetProjectionRef()) # raster crs

    # GDAL 3.0 requires
    lyr_crs.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
    img_crs.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)

    # crs transform object
    coordTrans = osr.CoordinateTransformation(lyr_crs, img_crs)

    # any percentiles?
    perc_name = []
    if percentiles:
        perc_name = ['p' + str(p) for p in percentiles]

    # initialise return
    l_result = [attributes + ['area'] + stats + perc_name]

    # iterate over features in layer
    for feat in tqdm(lyr):

        # retrieve geometry
        geom = feat.GetGeometryRef().Clone()

        # calculate area
        geom_area = round(geom.GetArea()/1e6, 3)  # m2 to km2

        # apply geo-transform if crs are different
        geom.Transform(coordTrans)

        # retrieve spatial extent of geometry object
        xmin, xmax, ymin, ymax  = geom.GetEnvelope()

        # retrieve values from specified fields in shp
        l_values = [feat.GetField(a) for a in attributes]
        l_stats = [None]*len(stats)

        # check overlap 1: outside extent of rasterfile (raster extent smaller than polygon)
        if geom.Within(ext_img_geom):

            # retrieve image offsets, rows and columns to read
            off_ul = gdal.ApplyGeoTransform(gdal.InvGeoTransform(gt), xmin, ymax)
            off_lr = gdal.ApplyGeoTransform(gdal.InvGeoTransform(gt), xmax, ymin)
            off_ulx, off_uly = map(int, off_ul)  # cast to int
            off_lrx, off_lry = map(int, off_lr)
            # columns and rows to read from ul coordinate
            xcount = off_lrx - off_ulx + 1
            ycount = off_lry - off_uly + 1

            # create target data source
            ds_target = gdal.GetDriverByName('MEM').Create('', xcount, ycount, 1, gdal.GDT_Byte)

            # snap to target raster (results in more accurate results that using the xmin, ymax of polygon)
            xmin_snap, ymax_snap = gdal.ApplyGeoTransform(gt, off_ulx, off_uly)

            # set transform and projection
            ds_target.SetGeoTransform((xmin_snap, gt[1], gt[2], ymax_snap, gt[4], gt[5]))
            ds_target.SetProjection(img_crs.ExportToWkt())

            # create memory layer
            mem_ds_source = ogr.GetDriverByName('Memory').CreateDataSource('')  # data source
            mem_lyr_source = mem_ds_source.CreateLayer('', img_crs, geom_type=ogr.wkbPolygon)  # create layer
            mem_feat = ogr.Feature(mem_lyr_source.GetLayerDefn())  # initialise feature
            mem_feat.SetGeometry(geom)  # populate feature with geometry
            mem_lyr_source.CreateFeature(mem_feat)  # add feature to layer

            # rasterize memory layer with burn value set to 1
            gdal.RasterizeLayer(ds_target, [1], mem_lyr_source, burn_values=[1])

            # read in arrays
            img_value = img.GetRasterBand(1)
            img_arr = img_value.ReadAsArray(off_ulx, off_uly, xcount, ycount)  # value raster
            img_nodata = img_value.GetNoDataValue()  # no data value
            mask_arr = ds_target.GetRasterBand(1).ReadAsArray(0, 0, xcount, ycount)  # mask raster

            # scale image values if specified
            if img_scale:
                img_arr = img_arr / img_scale

            # mask img array
            m_img_arr = np.ma.masked_array(img_arr, np.logical_not(mask_arr))

            # check that there are only valid pixels (overlap with no data areas)
            if not ((np.any(mask_arr) == img_nodata) | (m_img_arr.mask.all())):
                # re-initialise stats list
                l_stats = []
                # calculate stats
                for stat in stats:
                    l_stats.append(round(getattr(np, stat)(m_img_arr), 3))
                # calculate percentiles
                for perc in percentiles:
                    l_stats.append(round(np.percentile(m_img_arr, perc), 3))

                # close files
            del ds_target, mem_lyr_source, mem_ds_source, mem_feat

        # append shp values and stats to df
        l_result.append(l_values + [geom_area] + l_stats)

    return l_result

