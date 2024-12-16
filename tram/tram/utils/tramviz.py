# baseline tram visualization for Lab 3, modified to work with Django

from .trams import readTramNetwork, specialize_stops_to_lines, specialized_geo_distance, specialized_transition_time
from .graphs import dijkstra
import graphviz
import json
import os
from django.conf import settings
import requests
from bs4 import BeautifulSoup

# to be defined in Bonus task 1, but already included as mock-up
# from .trams import specialize_stops_to_lines, specialized_geo_distance, specialized_transition_time

SHORTEST_PATH_SVG = os.path.join(settings.BASE_DIR,
                        'tram/templates/tram/images/shortest_path.svg')
GBG_SVG = os.path.join(settings.BASE_DIR,
                        'tram/templates/tram/images/gbg_tramnet.svg')

# assign colors to lines, indexed by line number; not quite accurate
gbg_linecolors = {
    1: 'gray', 2: 'yellow', 3: 'blue', 4: 'green', 5: 'red',
    6: 'orange', 7: 'brown', 8: 'purple', 9: 'blue',
    10: 'lightgreen', 11: 'black', 13: 'pink'}


def scaled_position(network):

    # compute the scale of the map
    minlat, minlon, maxlat, maxlon = network.extreme_positions()
    size_x = maxlon - minlon
    scalefactor = len(network)/4  # heuristic
    x_factor = scalefactor/size_x
    size_y = maxlat - minlat
    y_factor = scalefactor/size_y
    
    return lambda xy: (x_factor*(xy[0]-minlon), y_factor*(xy[1]-minlat))

# Bonus task 2: redefine this so that it returns the actual traffic information
def html_parser():
    file = "static/tram-url.json"
    html = requests.get("https://www.vasttrafik.se/reseplanering/hallplatslista/")
    soup = BeautifulSoup(html.content, 'html.parser')
    link_dict = {}
    for link in soup.find_all('a'): # extract all links
        if 'Zon A' in link.get_text(): # filter links for stops + only stops in Zone A
            name = link.get_text().split(",")
            name = [n.strip() for n in name]
            
            url = link.get('href') # get url for stop
            id = url.split("/")[-2] # extract id number
            link_dict[name[0]] = id
    with open(file, "w") as outfile:
        json.dump(link_dict, outfile, indent=4)


def stop_url(stop, link_dict):
    timetable_url = 'https://avgangstavla.vasttrafik.se/?source=vasttrafikse-stopareadetailspage&stopAreaGid='
    
    return timetable_url + link_dict[stop]


# You don't probably need to change this

def network_graphviz(network, outfile, colors=None, positions=scaled_position):
    dot = graphviz.Graph(engine='fdp', graph_attr={'size!': '12,12'})

    with open("static/tram-url.json") as json_file:
        link_dict = json.load(json_file)
        
    for stop in network.all_stops():

        y, x = network.stop_position(stop)
        if positions:
            x, y = positions(network)((x, y))
        pos_x, pos_y = str(x), str(y)
        
        if colors:
            col = colors(stop) # set this to white to create gbg_tramnet.svg
        else:
            col = 'white'
        
        dot.node(stop, label=stop, shape='rectangle', pos=pos_x + ',' + pos_y +'!',
            fontsize='8pt', width='0.4', height='0.05',
            URL=stop_url(stop, link_dict),
            fillcolor=col, style='filled')
        
    for line in network.all_lines():
        stops = network.line_stops(line)
        for i in range(len(stops)-1):
            dot.edge(stops[i].get_name(), stops[i+1].get_name(),
                         color=gbg_linecolors[int(line)], penwidth=str(2))

    dot.format = 'svg'
    s = dot.pipe().decode('utf-8')
    with open(outfile, 'w') as file:
        file.write(s)


def colors(stop, time, geo):
    if stop in time and stop in geo:
        return 'cyan'
    if stop in time:
        return 'orange'
    if stop in geo:
        return 'green'
    return 'white'

def spec_colors(stop, spec_time, spec_geo):
    time = [stop for stop,line in spec_time]
    geo = [stop for stop,line in spec_geo]
    return colors(stop, time, geo)

def show_shortest(dep, dest):
    network = readTramNetwork()
    spec_network = specialize_stops_to_lines(network)
    #html_parser()
    #network_graphviz(network, GBG_SVG)

    #timepath = dijkstra(network, dep, cost=lambda u,v: network.transition_time(u,v))[dest]
    #geopath = dijkstra(network, dep, cost=lambda u,v: network.geo_distance(u,v))[dest]

    stops = spec_network.vertices()
    deps = []
    dests = []
    for stop in stops:
        if stop[0] == dep:
            deps.append(stop)
    for d in stops:
        if d[0] == dest:
            dests.append(d)

    paths = {}
    for d in deps:
        for d2 in dests:
            path = dijkstra(spec_network, d, cost=lambda u,v: specialized_transition_time(spec_network, u,v))[d2]
            paths[path["cost"]] = path
    timepath = paths[min(paths.keys())]

    paths = {}
    for d in deps:
        for d2 in dests:
            path = dijkstra(spec_network, d, cost=lambda u,v: specialized_geo_distance(spec_network, u,v))[d2]
            paths[path["cost"]] = path
    geopath = paths[min(paths.keys())]



    #timepath = dijkstra(spec_network, dep, cost=lambda u,v: specialized_transition_time(spec_network, u,v))[dest]
    #geopath = dijkstra(spec_network, dep, cost=lambda u,v: specialized_geo_distance(spec_network, u,v))[dest]
    
    network_graphviz(network, SHORTEST_PATH_SVG, colors=lambda stop: spec_colors(stop, timepath["path"], geopath["path"]))
    
    return timepath, geopath