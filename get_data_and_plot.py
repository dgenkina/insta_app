# -*- coding: utf-8 -*-
"""
Created on Fri Jun  7 11:58:08 2019

@author: dng5
"""

from bokeh.plotting import figure, output_file, show
from bokeh.resources import CDN
from bokeh.embed import file_html
from itertools import combinations
import pickle

import networkx as nx

from bokeh.io import show, output_file
from bokeh.plotting import figure
from bokeh.models import Plot, Range1d, MultiLine, Circle, HoverTool, TapTool, BoxSelectTool
from bokeh.models.graphs import from_networkx, NodesAndLinkedEdges, EdgesAndLinkedNodes
from bokeh.models.annotations import LabelSet
from bokeh.palettes import Spectral4
from bokeh.models import ColumnDataSource


savename = 'instagraph_all/instagraph_all'

with open(savename, 'rb') as f:
    graph = pickle.load(f)
    
def nodes_connected(graph, u, v):
     return u in graph.neighbors(v)
 
def make_sub_graph(center_tag,graph,occurence_cutoff = 0, number = 10):
    sub_graph = nx.Graph()
    sub_graph.add_node(center_tag, 
                       success = graph.nodes[center_tag]['success'],
                       occurence = graph.nodes[center_tag]['occurence'],
                       ss = graph.nodes[center_tag]['success']/graph.nodes[center_tag]['occurence'])
    
    ss_list = []
    for tag in graph.neighbors(center_tag):
        if graph.nodes[tag]['occurence']>occurence_cutoff:
            ss_list.append((tag, graph.nodes[tag]['success']/graph.nodes[tag]['occurence']))
    
    ss_top = sorted(ss_list, key = lambda x: -x[1])[:10]
    
    for tag, ss in ss_top: 
            sub_graph.add_node(tag,
                       success = graph.nodes[tag]['success'],
                       occurence = graph.nodes[tag]['occurence'],
                       ss = graph.nodes[tag]['success']/graph.nodes[tag]['occurence'])
        
    for a,b in combinations(sub_graph.nodes,2):
        if nodes_connected(graph,a,b):
            sub_graph.add_edge(a,b,weight = graph[a][b]['weight'])
        
    return sub_graph

def get_sub_graph_sizes(sub_graph):
    node_size_list = []
    occurence_list = []
    for node in sub_graph.nodes:
        node_size_list.append(sub_graph.nodes[node]['ss'])
        occurence_list.append(sub_graph.nodes[node]['occurence'])
        
    edge_width_list = []
    for a,b in sub_graph.edges:
        occ_a = sub_graph.nodes[a]['occurence']
        occ_b = sub_graph.nodes[b]['occurence']
        edge_width_list.append(float(sub_graph[a][b]['weight'])/float(occ_a)/float(occ_b))
        
    return node_size_list, occurence_list, edge_width_list


def plot_sub_graph(center_tag,graph=graph):
    if center_tag in graph.nodes:
        sub_graph = make_sub_graph(center_tag,graph,occurence_cutoff = 100, number = 10)
        
        recommended = []
        for tag in sub_graph.nodes:
            if sub_graph.nodes[tag]['ss'] > sub_graph.nodes[center_tag]['ss']:
                recommended.append('#'+str(tag))
                
        node_size_list, occurence_list, edge_width_list = get_sub_graph_sizes(sub_graph)
        
        plot = Plot(plot_width=400, plot_height=400, 
                    x_range=Range1d(-1.1,1.1), y_range=Range1d(-1.1,1.1))

        plot.title.text = "Hashtag graph"                                      
                                                
        
        plot.add_tools(HoverTool(tooltips=None), TapTool(), BoxSelectTool())
        
        
        pos = nx.circular_layout(sub_graph)
        x,y=zip(*pos.values())
        
        source = ColumnDataSource({'x':x,'y':y,'#':['#'+str(node) for node in sub_graph.nodes]})
        labels = LabelSet(x='x', y='y', text='#', source=source)


        graph_renderer = from_networkx(sub_graph, nx.circular_layout, scale=1, center=(0,0))
        node_size_list = [n/10.0 for n in node_size_list]
        graph_renderer.node_renderer.data_source.add(node_size_list, "size")
        graph_renderer.node_renderer.data_source.add([node for node in sub_graph.nodes], "node_name")
        graph_renderer.node_renderer.glyph = Circle(size="size", tags = [node for node in sub_graph.nodes])
#        graph_renderer.node_renderer.
        graph_renderer.edge_renderer.glyph = MultiLine(line_color="#CCCCCC", line_alpha=0.8, line_width=5)
        
        plot.renderers.append(graph_renderer)
        plot.renderers.append(labels)
#        
#        output_file("networkx_graph.html")
#        show(plot)
        html = file_html(plot, CDN, plot.title)
        return html, recommended
    else:
        html = "Unfortunaetly, that hashtag is not in our database. Please try again"
        return html, recommended

