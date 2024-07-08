import heapq

def dist_between_two_lat_lon(*args):
    from math import asin, cos, radians, sin, sqrt
    lat1, lat2, long1, long2 = map(radians, args)

    dist_lats = abs(lat2 - lat1)
    dist_longs = abs(long2 - long1)
    a = sin(dist_lats/2)**2 + cos(lat1) * cos(lat2) * sin(dist_longs/2)**2
    c = asin(sqrt(a)) * 2
    radius_earth = 6378 # the "Earth radius" R varies from 6356.752 km at the poles to 6378.137 km at the equator.
    return c * radius_earth

def get_nearest_location(data, v):
    try:
        return heapq.nsmallest(3, data, key=lambda p: dist_between_two_lat_lon(v['lat'],p['coordinate_lat'],v['lon'],p['coordinate_lon']))
    except TypeError:
        print('Not a list or not a number.')

# city = {'lat_key': value, 'lon_key': value}  # type:dict()
# new_york = {'lat': 40.712776, 'lon': -74.005974, "address": "ny"}
# washington = {'lat': 47.751076,  'lon': -120.740135, "address": "ws"}
# san_francisco = {'lat': 37.774929, 'lon': -122.419418, "address": "sf"}
# moscow = {'lat': 55.8023694, 'lon': 37.5940776, "address": "moscow"}
#
# city_list = [san_francisco, moscow]
#
# city_to_find = {'lat': 40.712776, 'lon': -74.005974, "address": "ny"}  # Houston
# print(find_closest_lat_lon(city_list, city_to_find)["address"])