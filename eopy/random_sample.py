import ogr
import osr
import gdal
import numpy as np
from .vector.rasterize_geom import rasterize_geom
from .vector.coords_to_points import coords_to_points

def random_sample(target, n_samples=10, type='list', min_distance=None, img_ref=None):

    # Geometry Part
    if isinstance(target, ogr.Geometry):
        if img_ref:
            target = rasterize_geom(target, img_ref)
        else:
            print("No reference image provided!")

    # Array Part
    gt = target.GetGeoTransform()

    # reshape 2D into 1D and create x and y index arrays
    geom_array = target.ReadAsArray()

    # get/set nodata value
    nodata = target.GetRasterBand(1).GetNoDataValue()
    if nodata:
        geom_array = np.where(geom_array == nodata, 0, geom_array)

    geom_array = geom_array.astype('bool')
    indiy, indix = np.indices((geom_array.shape[0], geom_array.shape[1]))

    geom_array_reshape = geom_array.reshape(-1)  # for np.choice
    indiy, indix = indiy.reshape(-1), indix.reshape(-1)

    # geom_array_true = np.where(geom_array_reshape)
    indiy, indix = indiy[geom_array_reshape], indix[geom_array_reshape]

    seq = np.arange(0, len(indix), 1)

    # Sample random from 'where'-filtered array
    samples = []
    distance_logical = True

    if min_distance:
        while len(samples) < n_samples:

            sample = np.random.choice(seq)
            sample_x = indix[sample] * gt[1] + gt[0] + gt[1] / 2
            sample_y = indiy[sample] * gt[5] + gt[3] + gt[5] / 2

            if len(samples) > 0:
                distance = abs(np.subtract(samples, (sample_x, sample_y)))
                distance_logical = np.all(distance > min_distance)

            if distance_logical:
                samples.append((sample_x, sample_y))

            seq = seq[seq != sample]

    else:
        samples = np.random.choice(seq, size=n_samples, replace=False)
        sample_x = indix[samples] * gt[1] + gt[0] + gt[1] / 2
        sample_y = indiy[samples] * gt[5] + gt[3] + gt[5] / 2
        samples = list(map(tuple, np.array((sample_x, sample_y)).T))

    if type == 'point':
        epsg_int = int(osr.SpatialReference(wkt=target.GetProjection()).GetAuthorityCode(None))
        samples = coords_to_points(samples, epsg=epsg_int)

    return samples

