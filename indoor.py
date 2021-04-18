from exif import Image
from datetime import date, datetime, timedelta
from os import chdir, listdir
from itertools import combinations
from pyproj import Proj, transform
import shapefile
import math
import csv


def GetAzimuth(shape, s):
    radian = math.atan((shape[s][2][1][0] - shape[s][2][0][0])/(shape[s][2][1][1] - shape[s][2][0][1]))
    degrees = math.degrees(radian)
    if degrees < 0:
        shape[s].append(degrees + 360) 
    else:
        shape[s].append(degrees)


def Projection(X_in, Y_in, inProj='epsg:3395', outProj='epsg:4326'):
    inProj = Proj(init=inProj)
    outProj = Proj(init=outProj)
    y_out, x_out = transform(inProj, outProj, X_in, Y_in)
    return x_out, y_out


# from .shp get [id, timestamp, (Point1, Point2), azimuth]
shape_attr = []
shape = shapefile.Reader('360.shp')
geom = shape.shapes()
fields = shape.records()
for s in range(len(geom)):
    #new_t = attr['t'].replace('-', ':').replace('T', ':')[:attr['t'].find('.')]
    utc_dt = datetime.strptime(fields[s][1], '%Y-%m-%dT%H:%M:%S.%f')
    timestamp = (utc_dt - datetime(1970, 1, 1) - timedelta(hours=1)).total_seconds()
    shape_attr.append([fields[s][0], timestamp, geom[s].points[:]])
    GetAzimuth(shape_attr, s)
#print(shape_attr)


# from EXIF get [Name.jpg, timestamp]
chdir('processed')
exif_data = []
for photo in listdir():
    with open(photo, 'rb') as img:
        my_image = Image(img)
        utc_dt_1 = datetime.strptime(my_image.DateTime, '%Y:%m:%d %H:%M:%S')
        exif_timestamp = (utc_dt_1 - datetime(1970, 1, 1)).total_seconds()
        exif_data.append([photo, exif_timestamp])
#print(exif_data)



# Just 2 lists: .shp(timestamps) and EXIF(timestamps)
point_time = [shape_attr[x][1] for x in range(len(shape_attr))]
#print(point_time)
exif_time = [exif_data[x][1] for x in range(len(exif_data))]
#print(exif_time)


# Build .shp and EXIF to directions.csv list(id, Name.jpg, azimuth, Lat, Lon, H)
directions_list =[]
for t in point_time:
    i = point_time.index(t)
    min_d = min((abs(t - y), (i, j)) for (j,y) in enumerate(exif_time))[1]
    x_out, y_out = Projection(shape_attr[i][2][0][0], shape_attr[i][2][0][1])
    directions_list.append([i, exif_data[min_d[1]][0], 
                                float('{:.3f}'.format(shape_attr[i][3])), 
                                        float('{:.8f}'.format(x_out)), float('{:.8f}'.format(y_out)), 155])


# with open('directions.csv','wb') as f:
    # wr = csv.writer(f, quoting=csv.QUOTE_ALL)
    # for i in range(len(directions_list)):
        # wr.writerow(directions_list[i])




