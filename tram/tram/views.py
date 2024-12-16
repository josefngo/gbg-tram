from django.shortcuts import render
from .forms import RouteForm
from django.shortcuts import redirect

from .utils.tramviz import show_shortest

def tram_net(request):
    return render(request, 'tram/home.html', {})


def find_route(request):
    form = RouteForm()
    if request.method == "POST":
        form = RouteForm(request.POST)
        if form.is_valid():
            route = form.data
            timepath, geopath = show_shortest(route['dep'], route['dest'])
            return render(request, 'tram/show_route.html',
                {'dest': form.instance.__str__(), 'route': route['dep'] + "-" + route['dest'], 'timepath': format_route("Quickest", timepath), 'geopath': format_route("Shortest", geopath)})
    else:
        form = RouteForm()
    return render(request, 'tram/find_route.html', {'form': form})

def format_route(prefix, path):
    output = prefix + ": "
    for stop in path["path"]:
        if type(stop) == tuple:
            output += stop[0] + " - "
        else:
            output += stop + " - "
    output += str(round(path["cost"], 3)) + " "
    if prefix == "Quickest":
        output += "minutes"
    elif prefix == "Shortest":
        output += "km"
    return output