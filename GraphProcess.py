import json
import sys
import numpy as np
import time
from optparse import OptionParser
import logging
#from py2neo import authenticate, Graph, Path, Node, Relationship, cypher, Subgraph
#from nltk.classify import PositiveNaiveBayesClassifier
from collections import deque
import networkx as nx
import array
import random

#import community
#from mcl_clustering import mcl
#community detection methods.
#implement markov chain clustering based on citations
#goal is to graph cluster with structured attributes.


if __name__ == "__main__":
    count = 0
    #g = Graph('http://localhost:7474/db/data/', user = 'neo4j', password = 'graphs32')
    #papers_subgraph = None
    #tx = g.begin()
    all_nodes_file = sys.argv[1]
    query_nodes_file = sys.argv[2]
    num_hops = int(sys.argv[3])
    written_file = sys.argv[4]
    original_query_nodes = set()
    modified_query_nodes = set()
    added_during_hops = set()
    with open(query_nodes_file) as q:
        for line in q:
            original_query_nodes.add(line.rstrip())
            modified_query_nodes.add(line.rstrip())

    for a in range(0, num_hops):
        #count = 0
        added_during_hops = set()
        original_query_nodes = set(modified_query_nodes)
        with open(all_nodes_file) as all_nodes:
            for each in all_nodes:
                result = each.rstrip().split(" ")
                set_result = set(result)
                if len(set_result.intersection(original_query_nodes)) > 0:
                    if result[0] in original_query_nodes:
                        for r in set_result:
                            if not r in original_query_nodes:
                                added_during_hops.add(r)
                    else:
                        #print "added", result[0]
                        added_during_hops.add(result[0])

        for node in added_during_hops:
            modified_query_nodes.add(node)

    num_nodes = 0
    query_hash = dict()
    for query_node in modified_query_nodes:
        query_hash[query_node] = set()
        num_nodes += 1
    node_count = 0
    edges_added = 0
    with open(all_nodes_file) as all_n:
        for each in all_n:
            result = each.rstrip().split(" ")
            paper_id = result[0]
            if paper_id in query_hash:
                for each in range(1, len(result)):
                    if result[each] in query_hash:
                        query_hash[paper_id].add(result[each])
            node_count += 1
            if node_count % 1000000 == 0:
                print node_count
    print "finished adding nodes, total amount is",num_nodes
    new_file = open(written_file, 'wb')
    node_count = 0
    for each in query_hash:
        paper_line = each[:]
        for a in query_hash[each]:
            paper_line += (" " + a)
        paper_line += "\n"
        new_file.write(paper_line)
        node_count += 1
        if node_count % 1000000 == 0:
            print node_count
    new_file.close()
    print "Done adding everything"
