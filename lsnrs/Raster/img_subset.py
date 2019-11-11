import gdal
from .img_offsets import img_offsets
from .array_to_gtiff import array_to_geotiff


def img_subset(img, extent, coordinates=True, write=False, filename=None):
    """
    Reads in image subsets as numpy array based on a user defined bounding box of real world or image coordinates.

    :param img: (str, gdal) Filepath of/or GDAL raster object.
    :param extent: (list) List of real world coordinates or image offsets describing a bounding box as follows:
    [upper left x, upper left y, lower right x, lower right y]
    :param coordinates: (bool) Is 'extent' parameter provided as real world coordinates (default to True).
    :param write: (bool) Write image subset as GeoTiff (default to False).
    :param filename: (str) If 'write' parameter is set to True, provide filename with extension, e.g. 'subset.tif'
    :return: Numpy array of image subset.
    """
    if isinstance(img, str):
        img = gdal.Open(img)

    if coordinates:
        extent = img_offsets(img, extent)

    img_array = img.ReadAsArray(extent[0], extent[1],
                                extent[2] - extent[0],
                                extent[3] - extent[1])

    if write:
        if filename is not None:
            img_gt = img.GetGeoTransform()
            img_proj = img.GetProjection()
            subset_ulx, subset_uly = gdal.ApplyGeoTransform(
                img_gt, extent[0], extent[1])
            gt = list(img_gt)
            gt[0] = subset_ulx
            gt[3] = subset_uly
            array_to_geotiff(img_array, filename, gt=gt, pj=img_proj)
        else:
            print('Output filename not defined!')

    return img_array
