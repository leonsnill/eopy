import osr
import ogr
import gdal


def rasterize_geom(geometry, target_raster):

    # create target data source
    ds_target = gdal.GetDriverByName('MEM').Create(
        '', target_raster.RasterXSize, target_raster.RasterYSize, 1, gdal.GDT_Byte)

    img_crs = osr.SpatialReference()
    img_crs.ImportFromWkt(target_raster.GetProjectionRef()) # raster crs

    # set transform and projection
    ds_target.SetGeoTransform(target_raster.GetGeoTransform())
    ds_target.SetProjection(target_raster.GetProjectionRef())

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

