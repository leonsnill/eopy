import osr
import ogr
import gdal


def rasterize_geom(geometry, target_raster=None, gt=None, proj=None):

    if target_raster:
        xdim = target_raster.RasterXSize
        ydim = target_raster.RasterYSize
        gt = target_raster.GetGeoTransform()
        proj = target_raster.GetProjectionRef()

    else:
        envelope = geometry.GetEnvelope()
        xdim = int((envelope[3] - envelope[2]) / gt[1])
        ydim = int((envelope[1] - envelope[0]) / abs(gt[5]))


    # create target data source
    ds_target = gdal.GetDriverByName('MEM').Create(
        '', xdim, ydim, 1, gdal.GDT_Byte)

    # set transform and projection
    ds_target.SetGeoTransform(gt)
    ds_target.SetProjection(proj)

    img_crs = osr.SpatialReference()
    img_crs.ImportFromWkt(proj) # raster crs

    # create memory layer
    mem_ds_source = ogr.GetDriverByName('Memory').CreateDataSource('')  # data source
    mem_lyr_source = mem_ds_source.CreateLayer('', img_crs, geom_type=ogr.wkbPolygon)  # create layer
    mem_feat = ogr.Feature(mem_lyr_source.GetLayerDefn())  # initialise feature
    mem_feat.SetGeometry(geometry)  # populate feature with geometry
    mem_lyr_source.CreateFeature(mem_feat)  # add feature to layer

    # rasterize memory layer with burn value set to 1
    gdal.RasterizeLayer(ds_target, [1], mem_lyr_source, burn_values=[1])

    mem_ds_source = mem_lyr_source = None

    return ds_target

