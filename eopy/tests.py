






# Retrieve geometry
import ogr, osr, gdal, numpy as np
shp = ogr.Open("/Users/leonnill/Documents/Daten/ROIs/ROI_MAI.shp")
lyr = shp.GetLayer()


def single_to_multi(lyr):
    multipolygon = ogr.Geometry(ogr.wkbMultiPolygon)

    for feat in lyr:
        geom = feat.GetGeometryRef()
        multipolygon.AddGeometry(geom)

    return multipolygon


lyr.SetAttributeFilter("class_type = 'wald'")
wald = single_to_multi(lyr)

# Rasterize geometry

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

re = gdal.Open("/Users/leonnill/Documents/Daten/RapidEye_Stacks/re_may_stack.tif")
geom_raster = rasterize_geom(wald, re)
gt = geom_raster.GetGeoTransform()

# Reshape 2D into 1D and create x and y index arrays
geom_array = geom_raster.ReadAsArray()
geom_array = geom_array.astype('bool')
indiy, indix = np.indices((geom_array.shape[0], geom_array.shape[1]))

geom_array_reshape = geom_array.reshape(-1)  # for np.choice
indiy, indix = indiy.reshape(-1), indix.reshape(-1)

#geom_array_true = np.where(geom_array_reshape)
indiy, indix = indiy[geom_array_reshape], indix[geom_array_reshape]

seq = np.arange(0, len(indix), 1)

# Sample random from 'where'-filtered array
min_distance = 0
n_samples = 1000
samples = []
distance_logical = True

while len(samples) < n_samples:

    sample = np.random.choice(seq)
    sample_x = indix[sample] * gt[1] + gt[0] + gt[1] / 2
    sample_y = indiy[sample] * gt[5] + gt[3] + gt[5] / 2

    if (min_distance & len(samples) > 0):
        distance = abs(np.subtract(samples, (sample_x, sample_y)))
        distance_logical = np.all(distance > min_distance)

    if distance_logical:
        samples.append((sample_x, sample_y))

    seq = seq[seq != sample]














