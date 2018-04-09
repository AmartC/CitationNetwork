from __future__ import division
import sys
import re
import math
import json
import os
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def iterative_levenshtein(s, t):
    """
        iterative_levenshtein(s, t) -> ldist
        ldist is the Levenshtein distance between the strings
        s and t.
        For all i and j, dist[i,j] will contain the Levenshtein
        distance between the first i characters of s and the
        first j characters of t
    """
    rows = len(s)+1
    cols = len(t)+1
    dist = [[0 for x in range(cols)] for x in range(rows)]
    # source prefixes can be transformed into empty strings
    # by deletions:
    for i in range(1, rows):
        dist[i][0] = i
    # target prefixes can be created from an empty source string
    # by inserting the characters
    for i in range(1, cols):
        dist[0][i] = i

    for col in range(1, cols):
        for row in range(1, rows):
            if s[row-1] == t[col-1]:
                cost = 0
            else:
                cost = 1
            dist[row][col] = min(dist[row-1][col] + 1,      # deletion
                                 dist[row][col-1] + 1,      # insertion
                                 dist[row-1][col-1] + cost) # substitution
    return dist[row][col]

if __name__ == "__main__":
    encoded_values = sys.argv[1]
    cluster_assignments = sys.argv[2]
    cluster_assigned = dict()
    titleAbstact = sys.argv[3]
    node_degrees = sys.argv[5]
    documents = []
    encoded_dict = dict()
    encoded_set = set()
    title_abstract_dict = dict()
    cluster_title_dict = dict()
    paper_degrees = dict()
    path = sys.argv[6]
    max_size_cluster = int(sys.argv[7])
    with open(encoded_values, 'rb') as encoded:
        for line in encoded:
            line = line.rstrip().split(" ")
            encoded_dict[int(line[0])] = line[1]
            encoded_set.add(line[1])


    with open(cluster_assignments, 'rb') as assigned:
        for line in assigned:
            line = line.rstrip().split(" ")
            cluster = line[1]
            node = int(line[0])
            if not cluster in cluster_assigned:
                cluster_assigned[cluster] = []
            cluster_assigned[cluster].append(encoded_dict[node])
    os.chdir(path)

    with open(node_degrees, 'rb') as n:
        for line in n:
            line = line.rstrip().split(" ")
            paper_degrees[line[0]] = int(line[1])


    with open(titleAbstact, 'rb') as t:
        for line in t:
            line = line.rstrip().split(" ", 1)
            if len(line) > 1:
                title_abstract_dict[line[0]] = line[1]
            else:
                title_abstract_dict[line[0]] = ""

    cosine_sim_output = sys.argv[4]
    cosine_sim = open(cosine_sim_output, 'wb')
    print "Total number of clusters is", len(cluster_assigned)
    for cluster in cluster_assigned:
        avg_cosine_similarity = 0.0
        size_cluster = len(cluster_assigned[cluster])
        print "Size of this cluster is",size_cluster
        if size_cluster == 1:
            line_write = str(1.0) + " " + str(size_cluster) + "\n"
            cosine_sim.write(line_write)
            continue
        if size_cluster > max_size_cluster:
            partial_dict = dict()
            counter = 0
            for each in cluster_assigned[cluster]:
                partial_dict[each] = paper_degrees[each]
            largest_degree_nodes = sorted(partial_dict.items(), key = lambda x:x[1], reverse=True)
            total_comparisons = 0.0
            for c in range(0, 5):
                for d in range(c + 1, 5):
                    vocab = title_abstract_dict[largest_degree_nodes[c][0]].split(" ")
                    vocab = set(vocab)
                    for each in title_abstract_dict[largest_degree_nodes[d][0]].split(" "):
                        vocab.add(each)
                    sklearn_tfidf = TfidfVectorizer(norm='l2',min_df=0, use_idf=True, smooth_idf=False, sublinear_tf=True, vocabulary = vocab)
                    sklearn_representation = sklearn_tfidf.fit_transform([title_abstract_dict[largest_degree_nodes[c][0]], title_abstract_dict[largest_degree_nodes[d][0]]])
                    cosine_sim_results = cosine_similarity(sklearn_representation)
                    avg_cosine_similarity += cosine_sim_results[0][1]
                    total_comparisons += 1
            for a in range(0, 5):
                for b in range(5, size_cluster):
                    vocab = title_abstract_dict[largest_degree_nodes[a][0]].split(" ")
                    vocab = set(vocab)
                    for each in title_abstract_dict[largest_degree_nodes[b][0]].split(" "):
                        vocab.add(each)
                    sklearn_tfidf = TfidfVectorizer(norm='l2',min_df=0, use_idf=True, smooth_idf=False, sublinear_tf=True, vocabulary = vocab)
                    sklearn_representation = sklearn_tfidf.fit_transform([title_abstract_dict[largest_degree_nodes[a][0]], title_abstract_dict[largest_degree_nodes[b][0]]])
                    cosine_sim_results = cosine_similarity(sklearn_representation)
                    avg_cosine_similarity += cosine_sim_results[0][1]
                    total_comparisons += 1

            avg_cosine_similarity /= total_comparisons
            line_write = str(avg_cosine_similarity) + " " + str(size_cluster) + "\n"
            cosine_sim.write(line_write)
        else:
            total_comparisons = 0.0
            for a in range(0, size_cluster - 1):
                for b in range(a + 1, size_cluster):
                    vocab = title_abstract_dict[cluster_assigned[cluster][a]].split(" ")
                    vocab = set(vocab)
                    for each in title_abstract_dict[cluster_assigned[cluster][b]].split(" "):
                        vocab.add(each)
                    sklearn_tfidf = TfidfVectorizer(norm='l2',min_df=0, use_idf=True, smooth_idf=False, sublinear_tf=True, vocabulary = vocab)
                    sklearn_representation = sklearn_tfidf.fit_transform([title_abstract_dict[cluster_assigned[cluster][a]], title_abstract_dict[cluster_assigned[cluster][b]]])
                    cosine_sim_results = cosine_similarity(sklearn_representation)
                    avg_cosine_similarity += cosine_sim_results[0][1]
                    total_comparisons += 1.0
            avg_cosine_similarity /= total_comparisons
            line_write = str(avg_cosine_similarity) + " " + str(size_cluster) + "\n"
            cosine_sim.write(line_write)
    cosine_sim.close()
