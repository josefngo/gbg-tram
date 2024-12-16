from queue import PriorityQueue
import sys
import graphviz
class Graph:
    def __init__(self, start = None, values = None, directed = False):
        self._adjlist = {}
        if values is None:
            values = {}
        self._valuelist =  values
        self._isdirected = directed
        if start is not None:
            for edge in start:
                self.add_edge(edge[0], edge[1])
            

    def add_edge(self, a, b):
        "Add an edge, and the vertices if needed."
        if a not in self._adjlist:
            self._adjlist[a] = set()
        self._adjlist[a].add(b)
        if b not in self._adjlist:
            self._adjlist[b] = set()
        self._adjlist[b].add(a)

    def add_vertex(self, vertex):
        "Add a vertex"
        if vertex not in self._adjlist:
            self._adjlist[vertex] = set()

    def vertices(self):
        "Lists all vertices."
        return self._adjlist.keys()
    
    def edges(self):
        "Lists all edges in one direction, a <= b"
        eds = []
        for a in self._adjlist.keys():
            for b in self._adjlist[a]:
                if a <= b:
                    eds.append((a, b))
        return eds

    def __str__(self):
        "Shows the adjacency list."
        return str(self._adjlist)

    def neighbors(self, v):
        "Gives the neighbours of vertex v."
        return self._adjlist[v]

    def __len__(self):
        return len(self._adjlist)

    def remove_vertex(self, vertex):
        self._adjlist.pop(vertex, None)
        for v in self._adjlist:
            if vertex in self._adjlist[v]:
                self._adjlist[v].remove(vertex)

    def remove_edge(self, vertex1, vertex2):
        self._adjlist[vertex1].remove(vertex2)
        self._adjlist[vertex2].remove(vertex1)

    def get_vertex_value(self, vertex):
        return self._valuelist.get(vertex)

    def set_vertex_value(self, vertex, val):
        self._valuelist[vertex] = val

def dijkstra(graph, source, cost=lambda u,v: 1):
    dist = {}
    prev = {}

    dist[source] = 0
    Q = PriorityQueue()
    Q.put((0, source))
    prev[source] = {"path": [source], "cost": 0}

#Instead of filling the priority queue with all nodes in the initialization phase,
#it is also possible to initialize it to contain only source; then, inside the if alt < dist[v] block, the decrease_priority() 
#becomes an add_with_priority() operation if the node is not already in the queue.

    while PriorityQueue.qsize(Q):
        u = Q.get()[1] # Remove and return best vertex
        for neighbor in graph.neighbors(u):
            alt = dist[u] + cost(u, neighbor)
            if neighbor not in dist or alt < dist[neighbor]:
                dist[neighbor] = alt
                prev[neighbor] = {
                    "path": prev[u]["path"].copy() + [neighbor],
                    "cost": alt
                }
                Q.put((alt, neighbor))
    return prev
                

class WeightedGraph(Graph):
    def __init__(self, start = None, values = None, directed = None):
        super().__init__(start, values, directed)
        self._weightlist = {}
        for t in start:
            self.set_weight(t[0], t[1], t[2])

    def get_weight(self, a, b):
        return self._weightlist[a][b]['weight']

    def set_weight(self, a,b, weight):
        if a not in self._weightlist:
            self._weightlist[a] = {}
        if b not in self._weightlist:
            self._weightlist[b] = {}
        self._weightlist[a][b] =  {
            'weight': weight
        }
        self._weightlist[b][a] =  {
            'weight': weight
        }

def visualize(graph, view='view', nodecolors=None):
    graphv = graphviz.Graph(engine = 'dot')
    for vertex in graph.vertices():
        if nodecolors and str(vertex) in nodecolors:
            graphv.node(name = str(vertex), color = nodecolors[str(vertex)])
        else:
            graphv.node(name = str(vertex))
    for src, dest in graph.edges():
        graphv.edge(str(src), str(dest))
    graphv.render('mygraph.gv', view=True) 

def view_shortest(G, source, target, cost=lambda u,v: 1):
        path = dijkstra(G, source, cost)[target]['path']
        colormap = {str(v): 'orange' for v in path}
        visualize(G, view='view', nodecolors=colormap)

def network_graphviz(network, colors=None, positions=None):
    gbg_linecolors = {
    1: 'gray', 2: 'yellow', 3: 'blue', 4: 'green', 5: 'red',
    6: 'orange', 7: 'brown', 8: 'purple', 9: 'blue',
    10: 'lightgreen', 11: 'black', 13: 'pink'}
    dot = graphviz.Graph(engine='fdp', graph_attr={'size': '12,12'})

    for stop in network.all_stops():
        
        x, y = network.stop_position(stop)
        if positions:
            x, y = positions((x, y))
        pos_x, pos_y = str(x), str(y)
        
        if colors:
            col = colors(stop)
        else:
            col = 'white'
        
    for line in network.all_lines():
        stops = network.line_stops(line)
        for i in range(len(stops)-1):
            dot.edge(stops[i], stops[i+1],
                         color=gbg_linecolors[int(line)], penwidth=str(2))
            
    dot.render(view=True)



if __name__ == "__main__":
    pass