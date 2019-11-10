import gdal


def img_offsets(img, offsets):
    """

    :param img:
    :param offsets:
    :return:
    """
    if isinstance(img, str):
        img = gdal.Open(img)

    gt = img.GetGeoTransform()
    inv_gt = gdal.InvGeoTransform(gt)

    offsets_ul = list(map(int, gdal.ApplyGeoTransform(inv_gt, offsets[0], offsets[1])))
    offsets_lr = list(map(int, gdal.ApplyGeoTransform(inv_gt, offsets[2], offsets[3])))

    return offsets_ul + offsets_lr
