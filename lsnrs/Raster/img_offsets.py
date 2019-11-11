import gdal


def img_offsets(img, coordinates):
    """
    Calculates image coordinates (offsets) for given real world coordinates. Image and coordinates need to be in the
    same coordinate system.

    :param img: (str, gdal) Filepath of/or GDAL raster object.
    :param coordinates: (list) List of real world coordinates describing a bounding box [upper left x, upper left y,
    lower right x, lower right y]
    :return: List of image coordinates / offsets [upper left x, upper left y, lower right x, lower right y]
    """
    if isinstance(img, str):
        img = gdal.Open(img)

    gt = img.GetGeoTransform()
    inv_gt = gdal.InvGeoTransform(gt)

    offsets_ul = list(map(int, gdal.ApplyGeoTransform(inv_gt, coordinates[0], coordinates[1])))
    offsets_lr = list(map(int, gdal.ApplyGeoTransform(inv_gt, coordinates[2], coordinates[3])))

    return offsets_ul + offsets_lr
