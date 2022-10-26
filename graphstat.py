import csv

from sympy import im
import matplotlib.pyplot as plt
from GraphStat.NetworkBuilder import *
from GraphStat.Visualization import *

NUM=10000 #测试数量

Nodes_path = 'E:/code-Python/week4/large_twitch_features.csv'
Edge_path = 'E:/code-Python/week4/large_twitch_edges.csv'
Out_path = 'E:/code-Python/week4/matrix.txt'
def main():
    plt.figure(num=7)
    nodes_lis=node.init_node(Nodes_path)
    with open (Edge_path,'r',encoding='utf-8')as f:
        edges=list(csv.reader(f))[1:]
        f.close()
    net_graph=graph.init_graph(len(nodes_lis),edges)#测试时第一个参数为NUM，实际应为len(nodes_lis)
    node.print_node(nodes_lis,6)
    plotgraph.plot_ego(net_graph,6)
    print(stat.get_node_number(net_graph))
    plotgraph.plotdgree_distribution(stat.cal_dgree_distribution(len(nodes_lis),net_graph))
    plotnodes.plot_nodes_attr(nodes_lis,'mature','affiliate','views','life_time','language')
    print(stat.cal_average_dgree(len(nodes_lis),net_graph))
    net_matrix=graph.save_graph(net_graph)
    graph.load_graph(net_matrix,Out_path)
main()