import urllib2, json, urllib, math, time, string
from pprint import pprint

def listify():
    with open('subEntrance.json') as data_file:
        data = json.load(data_file)
    data=data['data']
    subway_entrances = []
    for s in data:
        s = s[9][7:-1]
        lat = s[:s.find(" ")]
        lon = s[s.find(" " ) + 1:]
        subway_entrances.append([lat, lon])
    return subway_entrances

def listify2():
    bike_stations=[]
    with open('bikeStation.json') as data_file2:
            data = json.load(data_file2)
    data = data['stationBeanList']
    for s in data:
            lat = s['latitude']
            lon = s['longitude']
            bike_stations.append([lat, lon])
    return bike_stations
print listify2()


