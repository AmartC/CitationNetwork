from __future__ import division
import sys
import re
import math
import json
import os
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

#def compute_average_cosine(first, second):


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
    largest_degree_clusters = []
    for cluster in cluster_assigned:
        if len(cluster_assigned[cluster]) < 25:
            continue
        partial_dict = dict()
        for each in cluster_assigned[cluster]:
            partial_dict[each] = paper_degrees[each]
        largest_degree_nodes = sorted(partial_dict.items(), key = lambda x:x[1], reverse=True)[:10]
        largest_degree_clusters.append(largest_degree_nodes)

    print "Total number of clusters evaluated here with length of at least 25 papers is", len(largest_degree_clusters)

    for c in range(0, len(largest_degree_clusters) - 1):
        for d in range(c + 1, len(largest_degree_clusters)):
            avg_cosine_similarity = 0.0
            total_comparisons = 0.0
            for e in range(0, len(largest_degree_clusters[c])):
                if not largest_degree_clusters[c][e][0] in title_abstract_dict:
                    continue
                for f in range(0, len(largest_degree_clusters[d])):
                    if not largest_degree_clusters[c][f][0] in title_abstract_dict:
                        continue
                    vocab = title_abstract_dict[largest_degree_clusters[c][e][0]].split(" ")
                    vocab = set(vocab)
                    for each in title_abstract_dict[largest_degree_clusters[d][f][0]].split(" "):
                        vocab.add(each)
                    sklearn_tfidf = TfidfVectorizer(norm='l2',min_df=0, use_idf=True, smooth_idf=False, sublinear_tf=True, vocabulary = vocab)
                    sklearn_representation = sklearn_tfidf.fit_transform([title_abstract_dict[largest_degree_clusters[c][e][0]], title_abstract_dict[largest_degree_clusters[d][f][0]]])
                    cosine_sim_results = cosine_similarity(sklearn_representation)
                    avg_cosine_similarity += cosine_sim_results[0][1]
                    total_comparisons += 1.0
            if total_comparisons == 0.0:
                total_comparisons = 1.0
            final_result = avg_cosine_similarity / total_comparisons
            written_line = largest_degree_clusters[c][0][0] + " " + largest_degree_clusters[d][0][0] + " " + str(final_result) + "\n"
            cosine_sim.write(written_line)

    cosine_sim.close()
