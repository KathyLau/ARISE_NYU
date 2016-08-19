from flask import Flask, render_template, request, redirect, session, url_for, flash
import urllib2, json, urllib, math, time, string
key2 = "AIzaSyDU4DMUAXAnDP6DZ24TyDBcVOIWmOnSa4E"
key="AIzaSyAjRmGMuK_IQ2UUmYLHThc7JBdzZ4N22BQ"
app = Flask(__name__)
app.secret_key="dcb61f28eafb8771213f3e0612422b8d"

@app.route('/', methods=["POST","GET"])
@app.route('/index', methods=["POST","GET"])
def index():
        if request.method=="POST":
                flashed = False
                # read form data
                origin = request.form["origin"]
                destination = request.form["destination"]
                
                if origin != '' and destination != '':
                        # find the latitude and longitude of the origin and destination
                        geo1=geo_loc(origin)
                        geo2=geo_loc(destination)
                        
                        # gets a dictionary corresponding to the closest Citibike station
                        station1 = closestStation(geo1)
                        station2 = closestStation(geo2)
                        
                        # get dictionaries of Google Map route info for walking/bicycling
                        rlist1 = reverse_geo(station1)#getGoogleJSON(urllib.quote_plus(origin),station1,"walking")
                        rlist2 = reverse_geo(station2)#getGoogleJSON(station1,station2,"bicycling")

                        return render_template("maps.html",
                                              org=origin.replace("+", " "),
                                               rlist1=rlist1.replace("+", " ").replace("%2C", ""), 
                                               rlist2=rlist2.replace("+", " ").replace("%2C", ""),
                                               dest=destination.replace("+", " ").replace("%2C", ""))
                        
                else: #Both not filled out
                        flash("Please fill out the required fields.")
                        flashed = True
                        #return redirect("/")
        else: #GET METHOD
                return render_template("index.html")

@app.route('/about')
def about():
    with open('subEntrance.json') as data_file:
        data = json.load(data_file)
    data=data['data'][:30]
    subway_entrances = []
    bike_stations=[]
    for s in data:
        s = s[9][7:-1]
        lon = float(s[:s.find(" ")])
        lat = float(s[s.find(" " ) + 1:])
        subway_entrances.append([lat, lon])
    rand1 = subway_entrances[0]
    rand2 = subway_entrances[2]
    with open('bikeStation.json') as data_file2:
            data = json.load(data_file2)
    data = data['stationBeanList'][40:65]
    for s in data:
            lat = s['latitude']
            lon = s['longitude']
            bike_stations.append([lat, lon])
    rand3 = bike_stations[0]
    rand4 = bike_stations[2]
    return render_template("maps3.html", coords=subway_entrances, coords2=bike_stations)

#given a dictionary with lng and lat to find approximate address
def reverse_geo(ldic):
        googleurl = "https://maps.googleapis.com/maps/api/geocode/json?latlng=%s,%s&key=%s" % (ldic['latitude'], ldic['longitude'], key)
        request = urllib2.urlopen(googleurl)
        result = request.read()
        d = json.loads(result)
        rdic = d['results'][0]
        address = rdic['formatted_address']
        address = urllib.quote_plus(address)
        return address

def closestStation(geo):
# returns the dictionary entry of the closest Citibike station to a given address
        rlist = getCitiJSON()
        distances = [math.sqrt((geo['lng']-r['longitude'])**2 + (geo['lat']-r['latitude'])**2) for r in rlist]
        shortest = min(distances)
        index = distances.index(shortest)
        return rlist[index]

def geo_loc(location):
#finds the longitude and latitude of a given location parameter using Google's Geocode API
#return format is a dictionary with longitude and latitude as keys
        loc = urllib.quote_plus(location)
        googleurl = "https://maps.googleapis.com/maps/api/geocode/json?address=%s&key=%s" % (loc,key)
        request = urllib2.urlopen(googleurl)
        results = request.read()
        gd = json.loads(results) #dictionary
        if gd['status'] != "OK":
                return location+" is a bogus location! What are you thinking?"
        else:
                result_dic = gd['results'][0] #dictionary which is the first element in the results list
                geometry = result_dic['geometry'] #geometry is another dictionary
                loc = geometry['location'] #yet another dictionary
                return loc

def getCitiJSON():
# returns a dictionary of Citibike station information
        url = "http://www.citibikenyc.com/stations/json"
        request = urllib2.urlopen(url)
        result = request.read()
        d = json.loads(result)
        rlist = d['stationBeanList']
        return rlist

def getGoogleJSON(origin, destination, mode):
# returns a dictionary of Google Map route information
        org = origin
        dest = destination
        now = int(time.time())
        if isinstance(origin,dict):
                org = str(origin["latitude"])+","+str(origin["longitude"])
                origin = origin['stationName']
        if isinstance(destination,dict):
                dest = str(destination["latitude"])+","+str(destination["longitude"])
                destination = destination['stationName']
        url = "https://maps.googleapis.com/maps/api/directions/json?origin=%s&destination=%s&mode=%s&departure_time=%s&key=%s" % (org, dest, mode, now, key)
        request = urllib2.urlopen(url)
        result = request.read()
        d = json.loads(result)
        if d['status'] != "OK":
                return "No %s directions exist between %s and %s." %(mode, origin, destination)
        else:
                rlist = d['routes']
                return rlist

if __name__ == '__main__':
    app.run(debug=True)
    app.run('0.0.0.0', port=8000)
