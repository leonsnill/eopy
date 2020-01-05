import numpy as np
import gdal
import ogr


def sample_random(target_geom, n_samples=50, within=False, nodata=None,
                  buffer=None, grid_ref=None, grid_size=None, min_distance=None):
    """
    Stratified random sampling of n-samples for a target geometry.

    :param target_geom:     Geometry to sample in. Can be of type gdal.Dataset and ogr.DataSource.
    :param n_samples:       Number of samples.
    :param within:          Check, wether samples should lie within the polygon or valid raster data (True) or just the
                            bounding box of the target geometry. Default to False.
    :param nodata:          Nodata value of raster file. Only needed if within = True to check if sampled pixel is on
                            valid pixel.
    :param buffer:
    :param grid_ref:        (list) List containing x and y coordinates of a reference point, e.g. [x, y]
    :param grid_size:       (int/flt) Grid size / pixel size of reference code.
    :param min_distance:    (int/flt) Minimum distance between sample points.
    :return:                List of tuples with coordinates of sample points (x,y).
    """

    if isinstance(target_geom, ogr.DataSource):
        xmin, xmax, ymin, ymax = target_geom.GetEnvelope()
        is_vector = True

    elif isinstance(target_geom, gdal.Dataset):
        gt = target_geom.GetGeoTransform()
        ndims = target_geom.RasterCount
        xdim = target_geom.RasterXSize
        ydim = target_geom.RasterYSize

        xmin = gt[0]
        ymax = gt[3]
        xmax = xmin + gt[1] * xdim
        ymin = ymax + gt[5] * ydim
        is_vector = False

    if grid_ref:
        x_ref = grid_ref[0]
        y_ref = grid_ref[1]

        xmin = x_ref + (int((xmin - x_ref) / grid_size)) * grid_size
        xmax = x_ref + (int((xmax - x_ref) / grid_size)) * grid_size
        ymin = y_ref + (int((ymin - y_ref) / grid_size)) * grid_size
        ymax = y_ref + (int((ymax - y_ref) / grid_size)) * grid_size

    # --------------------------------------------------
    # Vector data
    # --------------------------------------------------
    if is_vector:

        # Initialise variables
        samples = []
        distance_logical = False

        while len(samples) < n_samples:
            sample_x = np.random.choice(np.arange(xmin, xmax, grid_size))
            sample_y = np.random.choice(np.arange(ymin, ymax, grid_size))

            if min_distance & len(samples) > 0:
                distance = abs(np.subtract(samples, (sample_x, sample_y)))
                distance_logical = np.any(distance < min_distance)

            if not distance_logical:

                if within:
                    # construct geometry of random point
                    point_geometry = ogr.Geometry(ogr.wkbPoint)
                    point_geometry.AddPoint(sample_x, sample_y)

                    if buffer:
                        point_geometry = point_geometry.Buffer(buffer)

                    if point_geometry.Within(target_geom):
                        samples.append((sample_x, sample_y))

                else:
                    samples.append((sample_x, sample_y))

    # --------------------------------------------------
    # Raster data
    # --------------------------------------------------
    else:
        target_array = target_geom.ReadAsArray()

        if min_distance:
            sample_mask = np.zeros((ydim, xdim), dtype=bool)
            sample_mask[::min_distance, ::min_distance] = True
        else:
            sample_mask = np.ones((ydim, xdim), dtype=bool)

        if within:
            target_array = np.where(target_array == nodata, False, True)
            if ndims > 1:
                target_array = np.prod(target_array, axis=0)
            sample_mask = np.where(target_array * sample_mask)

        sample = np.random.choice(np.arange(0, len(sample_mask[0]), 1), size=n_samples, replace=False)
        sample_x = sample_mask[1][sample] * gt[1] + gt[0]
        sample_y = sample_mask[0][sample] * gt[5] + gt[3]

        # correct to pixel center
        sample_x = sample_x + gt[1]/2
        sample_y = sample_y + gt[5] / 2

        samples = list(map(tuple, np.array((sample_x, sample_y)).T))

    return samples

