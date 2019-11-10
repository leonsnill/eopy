import gdal
from .img_offsets import img_offsets
from .array_to_gtiff import array_to_geotiff


def img_subset(img, extent, coordinates=True, write=False, filename=None):
    """

    :param img:
    :param extent:
    :param coordinates:
    :param write:
    :param filename:
    :return:
    """
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
            array_to_geotiff(img_array, filename, trans=gt, proj=img_proj)
        else:
            print('Output filename not defined!')

    return img_array