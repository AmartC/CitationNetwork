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



if __name__ == "__main__":
    count = 0
    query_nodes = set()
    all_documents = sys.argv[1]
    keywords_file = sys.argv[2]
    nodes_file = sys.argv[3]
    query_file = sys.argv[4]
    documents = []
    with open(all_documents) as a:
        for line in a:
            documents.append(line.rstrip())
    keywords = []
    with open(keywords_file) as k:
        for line in k:
            keywords.append(line.rstrip().lower())

    overall = 0
    topic_count = 0
    node_file = open(nodes_file, 'w')
    for doc in documents:
        topic_count = 0
        with open(doc) as f:
            for line in f:
                parsed_json = json.loads(line)
                paper_title = parsed_json["title"].lower()
                paper_id = parsed_json["id"]
                paper_references = []
                paper_abstract = ""
                if "abstract" in parsed_json:
                    paper_abstract = parsed_json["abstract"].lower()
                if "references" in parsed_json:
                    paper_references = parsed_json["references"]
                paper_line = paper_id
                if len(paper_references) > 0:
                    for each in paper_references:
                        paper_line += (" " + each)
                paper_line += "\n"
                node_file.write(paper_line)
                if len(paper_references) == 0:
                    continue
                combined = paper_title + " " + paper_abstract
                for keyword in keywords:
                    if keyword in combined:
                        query_nodes.add(parsed_json["id"])
                        break
                overall += 1
                if overall % 1000000 == 0:
                    print overall
    node_file.close()
    query_file = open(query_file, 'w')
    for each in query_nodes:
        query_file.write(each)
        query_file.write("\n")
    query_file.close()
