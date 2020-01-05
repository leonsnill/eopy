import gdal
import ogr


def extract(img, points):

    if isinstance(img, str):
        img = gdal.Open(img)

    gt = img.GetGeoTransform()
    values = []

    if isinstance(points, list):
        for point in points:
            mx, my = point[0], point[1]
            px = int((mx - gt[0]) / gt[1])  # x pixel
            py = int((my - gt[3]) / gt[5])  # y pixel
            values.append(img.ReadAsArray(px, py, 1, 1))

    else:
        if isinstance(points, str):
            points = ogr.Open(points)

        points = points.GetLayer()

        for feat in points:
            geom = feat.GetGeometryRef()
            mx, my = geom.GetX(), geom.GetY()
            px = int((mx - gt[0]) / gt[1])  # x pixel
            py = int((my - gt[3]) / gt[5])  # y pixel
            values.append(img.ReadAsArray(px, py, 1, 1))

    return values

