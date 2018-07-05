import matplotlib.pyplot as plt
from shapely.geometry.polygon import LinearRing
from shapely.geometry import LineString
import random
import numpy as np
import csv
from func import *
import scipy.stats as stats
import os
header = __import__("problem2-simple-header")

index = 0

polygon_csv = open(header.DATA_DIR + "polygon.csv",
                   'w', encoding='utf-8', newline='')
polygon_writer = csv.writer(polygon_csv)

while index < header.DATA_NUMBER:
    numSides = random.randrange(header.NUM_SIDES[0], header.NUM_SIDES[-1])
    polygon_coords = make_random_polygon(numSides, header.WHOLE_RANGE)
    polygon = Polygon(polygon_coords)
    ring = LinearRing(polygon_coords)
    if not ring.is_simple:
        continue

    convex_hull = polygon.convex_hull
    if convex_hull.area < 2.0:
        continue

    # draw_polygon(polygon)

    '''
    convex_ratio, numOfSides, [polygon_coords]
    '''
    polygon_row = ["{0:.4f}".format(polygon.area / convex_hull.area), numSides]
    polygon_row.extend([item for sublist in polygon_coords for item in sublist])
    polygon_writer.writerow(polygon_row)
    index += 1
polygon_csv.close()
