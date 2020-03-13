import ogr


def extent_to_geom(ext):
    """
    Converts corner coordinates to a geometry object.

    Args:
        ext: List of corner coordinates as [xmin, ymax, xmax, ymin], i.e. first upper left then lower right coordinates.

    Returns: Geometry object.

    """
    # initialise geometry
    ring = ogr.Geometry(ogr.wkbLinearRing)
    poly = ogr.Geometry(ogr.wkbPolygon)

    # add points to geometry
    ring.AddPoint(ext[0], ext[1])
    ring.AddPoint(ext[2], ext[1])
    ring.AddPoint(ext[2], ext[3])
    ring.AddPoint(ext[0], ext[3])
    ring.AddPoint(ext[0], ext[1])

    poly.AddGeometry(ring)

    return poly
