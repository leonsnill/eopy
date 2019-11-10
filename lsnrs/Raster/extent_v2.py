import gdal


def extentv(rasterPathlist):
    # create empty lists for the bounding coordinates and the overlap extent
    ul_x_list = []
    ul_y_list = []
    lr_x_list = []
    lr_y_list = []
    overlap_extent = []
    for path in rasterPathlist:
        raster = gdal.Open(path)

        gt = raster.GetGeoTransform() # get geo transform data
        ul_x = gt[0] # upper left x coordinate
        ul_y = gt[3] # upper left y coordinate
        lr_x = ul_x + (gt[1] * raster.RasterXSize) # upper left x coordinate + number of pixels * pixel size
        lr_y = ul_y + (gt[5] * raster.RasterYSize) # upper left y coordinate + number of pixels * pixel size
        #append bbox of every raster to the lists
        ul_x_list.append(ul_x)
        ul_y_list.append(ul_y)
        lr_x_list.append(lr_x)
        lr_y_list.append(lr_y)
    #calculate the bounding box coorinates
    overlap_extent.append(max(ul_x_list))
    overlap_extent.append(min(ul_y_list))
    overlap_extent.append(min(lr_x_list))
    overlap_extent.append(max(lr_y_list))

    return overlap_extent