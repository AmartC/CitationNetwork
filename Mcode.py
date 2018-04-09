import sys
from collections import defaultdict

WEIGHT_THRESHOLD = 0.2

##
WEIGHT_THRESHOLD = 1 - WEIGHT_THRESHOLD

def mcode(filename, cluster_files):
  edges = defaultdict(set) # node id => neighboring node ids

  # read in graph
  counter = 0
  with open(filename, 'r') as f:
      for line in f:
          current = line.rstrip().split(" ")
          for a in range(1, len(current)):
              edges[current[0]].add(current[a])
              edges[current[a]].add(current[0])
          counter += 1
          if counter % 1000000 == 0:
              print counter
  print >> sys.stderr, 'graph loaded; %i nodes' % (len(edges),)

  # Stage 1: Vertex Weighting
  print >> sys.stderr, 'vertex weighting...'
  weights = dict((v,1.) for v in edges)
  for i,v in enumerate(edges):
    neighborhood = set((v,)) | edges[v]
    # if node has only one neighbor, we know everything we need to know
    if len(neighborhood) <= 2: continue

    # see if larger k-cores exist
    k = 1 # highest valid k-core
    while neighborhood:
      k_core = neighborhood.copy()
      invalid_nodes = True
      while invalid_nodes and neighborhood:
        invalid_nodes = set(
          n for n in neighborhood if len(edges[n] & neighborhood) <= k)
        neighborhood -= invalid_nodes
      k += 1 # on exit, k will be one greater than we want
    # vertex weight = k-core number * density of k-core
    weights[v] = (k-1) * (sum(len(edges[n] & k_core) for n in k_core) /
      (2. * len(k_core)**2))

  # Stage 2: Molecular Complex Prediction
  print >> sys.stderr, 'molecular complex prediction'
  unvisited = set(edges)
  num_clusters = 0
  cluster_files = open(cluster_files, 'wb')
  for seed in sorted(weights, key=weights.get, reverse=True):
    if seed not in unvisited: continue

    cluster, frontier = set((seed,)), set((seed,))
    w = weights[seed] * WEIGHT_THRESHOLD
    while frontier:
      cluster.update(frontier)
      unvisited -= frontier
      frontier = set(
        n for n in set.union(*(edges[n] for n in frontier)) & unvisited
        if weights[n] > w)

    # haircut: only keep 2-core complexes
    invalid_nodes = True
    while invalid_nodes and cluster:
      invalid_nodes = set(n for n in cluster if len(edges[n] & cluster) < 2)
      cluster -= invalid_nodes

    if cluster:
      # fluff never really seems to improve anything...
      #cluster.update(
      # n for n in set.union(*(edges[c] for c in cluster)) & unvisited
      # if densities[n] > FLUFF_THRESHOLD)

      current_cluster = ' '.join(cluster)
      current_cluster += "\n"
      cluster_files.write(current_cluster)
      num_clusters += 1
      #current_line = "Cluster " + str(num_clusters) + "\n"
      #cluster_files.write(current_line)
      #misc_data = str(num_clusters) + " " + str(len(cluster)) + " "  + str(seed) + "\n"
      #cluster_files.write(misc_data)
      #print >> sys.stderr, num_clusters, len(cluster), seed
  cluster_files.close()

if __name__ == '__main__':
  mcode(sys.argv[1], sys.argv[2])
