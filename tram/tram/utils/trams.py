import json
import sys
import math
import os
from .graphs import WeightedGraph
from django.conf import settings
TRAM_FILE = os.path.join(settings.BASE_DIR, 'static/tramnetwork.json')

def open_json_file(file):
    with open(file) as json_file:
        data = json.load(json_file)
    return data

class TramNetwork(WeightedGraph):
    def __init__(self, lines = {}, stops = {}, times = {}):
        super().__init__(self.help_init(times))
        self._linedict = lines
        self._stopdict = stops
        self._timedict = times

    def help_init(self, times):
        l = []
        for stop in times:
            for s in times[stop]:
                l.append((stop, s, times[stop][s]))
        return l
    
    def all_lines(self):
        return list(self._linedict.keys())
    
    def all_stops(self):
        return list(self._stopdict.keys())

    def extreme_positions(self):
        stops = self._stopdict.values()
        minlat = min([s._position[0] for s in stops]) # Use getters instead????
        minlon = min([s._position[1] for s in stops])
        maxlon = max([s._position[1] for s in stops])
        maxlat = max([s._position[0] for s in stops])
        return minlat, minlon, maxlat, maxlon

    def geo_distance(self, a, b):

        stop1_pos = self.stop_position(a)
        stop2_pos = self.stop_position(b)

        stop1_lat = math.radians(stop1_pos[0])
        stop1_lon = math.radians(stop1_pos[1])
        stop2_lat = math.radians(stop2_pos[0])
        stop2_lon = math.radians(stop2_pos[1])
            
        R = 6371.009 # radius of the earth in kilometres
        
        delta_lat = stop1_lat - stop2_lat
        delta_lon = stop1_lon - stop2_lon
        mean_lat = (stop1_lat + stop2_lat) / 2

        return R * (math.sqrt(delta_lat**2 + (math.cos(mean_lat) * delta_lon)**2))

    def line_stops(self, line):
        return self._linedict[line].get_stops()

    def remove_lines(self, lines):
        pass

    def stop_lines(self, a):
        lines = []
        for line in self._linedict:
            if a in self._linedict[line].get_stops():
                lines.append(line)
        return lines
    
    def stop_position(self, a):
        return self._stopdict[a].get_position()
    
    def transition_time(self, a, b):
        if a == b: return 0
        return self.get_weight(a,b)

    

class TramLine:
    def __init__(self, num, stops):
        self._number = num
        self._stops = stops
    
    def get_number(self):
        return self._number
    
    def get_stops(self):
        return self._stops

class TramStop:
    def __init__(self, name, lines = None, lat = None, lon = None):
        self._name = name
        self._lines = lines
        self._position = (lat, lon)
    
    def add_line(self, line):
        if self._lines == None:
            self._lines = []
        self._lines.append(line)
    
    def get_lines(self):
        return self._lines
    
    def get_name(self):
        return self._name
    
    def get_position(self):
        return self._position
    
    def set_position(self, lat, lon):
        self._position = (lat, lon)

def readTramNetwork(tramfile=TRAM_FILE):
    data = open_json_file(tramfile)
    lines = {}
    stops = {}


    #build stop objects and stop dict
    # key = string => objekt
    for stop in data["stops"]:
        lat = data["stops"][stop]["lat"]
        lon = data["stops"][stop]["lon"]
        stops[stop] = TramStop(stop, None, lat, lon)
    #build line objects and line dict
    for line in data["lines"]:
        stop_list = []
        for stop in data["lines"][line]:
            stop_list.append(stops[stop])
            
        lines[line] = TramLine(line, stop_list)
        # need to add the TramLine objects to the TramStop objects.
        for stop in stop_list:
            stop.add_line(lines[line])
    return TramNetwork(lines, stops, data["times"])

# # Bonus task 1: take changes into account and show used tram lines

def specialize_stops_to_lines(network):
    new_network = TramNetwork()


    new_network._linedict = network._linedict
    new_network._stopdict = network._stopdict
    new_network._timedict = network._timedict

    #for every line
    #for every stop in that line
    #add a vertex to new network with (stop,line)
    all_lines = network.all_lines()
    for line in all_lines:
        for stop in network._linedict[line].get_stops():
            new_network.add_vertex((stop.get_name(),line))

    #for every edge
    for edge in network.edges():
        # get the common lines between the stops connecting the edges¨
        stop1lines = set(network.stop_lines(network._stopdict[edge[0]]))
        stop2lines = set(network.stop_lines(network._stopdict[edge[1]]))
        lines_between_stop1_stop2 = stop1lines.intersection(stop2lines)
        # add all edges to new network
        for line in lines_between_stop1_stop2:
            new_network.add_edge((edge[0], line), (edge[1], line))

    #add edges between vertex with same stop
    stops = new_network.vertices()
    for stop in stops:
        for stop2 in stops:
            if stop == stop2:
                continue
            if stop[0] == stop2[0]:
                new_network.add_edge(stop, stop2)
            
    return new_network


def specialized_transition_time(spec_network, a, b, changetime=10):
    # TODO: write this function as specified
    #if stop is the same
    if a[0] == b[0]: 
        return changetime
    if a[0] in spec_network._timedict and b[0] in spec_network._timedict[a[0]]:
        return spec_network._timedict[a[0]][b[0]]
    else:
        return spec_network._timedict[b[0]][a[0]]
    


def specialized_geo_distance(spec_network, a, b, changedistance=0.02):
    # TODO: write this function as specified
    #if stop is the same
    if a[0] == b[0]:
        return changedistance
    return spec_network.geo_distance(a[0],b[0])
