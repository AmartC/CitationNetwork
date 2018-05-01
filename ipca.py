import sys
from itertools import combinations
from collections import defaultdict

T_IN = 0.5
# SP = 2 # hard-coded, mostly for efficiency

# dictionary type that returns zero for missing values
# used here in 'edges' dictionary
class zerodict(dict):
	def __missing__(self, k):
		return 0

def ipca(filename, cluster_files):
	data = defaultdict(set) # node id => neighboring node ids

	# read in graph
	with open(filename, 'r') as f:
		for line in f:
			current = line.rstrip().split(" ")
			for a in range(1, len(current)):
				data[current[0]].add(current[a])
				data[current[a]].add(current[0])

	weights = defaultdict(int)
	for a in data:
		for b in data[a]:
			shared = len(data[a] & data[b])
			weights[a] += shared
			weights[b] += shared

	print "Done with the weights"

	unvisited = set(data)
	num_clusters = 0
	cluster_files = open(cluster_files, 'wb')

	seed_nodes = sorted(data,key=lambda k: (weights[k],len(data[k])),reverse=True)

	for seed in seed_nodes: # get highest degree node
		if seed not in unvisited: continue

		cluster = set((seed,iter(data[seed]).next())) # seed and random neighbor

		while True:
			# rank neighbors by the number of edges between the node and cluster nodes
			frontier = sorted((len(data[p] & cluster),p) for p in
				set.union(*((data[n] - cluster) for n in cluster)))

			# do this until IN_vk < T_IN, SP <= 2 is met, or no frontier nodes left
			found = False
			while frontier and not found:
				m_vk,p = frontier.pop()
				if m_vk < T_IN * len(cluster): break
				c_2neighbors = data[p] & cluster
				c_2neighbors.update(*(data[c] & cluster for c in c_2neighbors))
				if cluster == c_2neighbors:
				 	found = True
				 	break

			if not found: break

			# otherwise, add the node to the cluster
			cluster.add(p)

		unvisited -= cluster
		cluster_line = ' '.join(cluster)
		cluster_line += "\n"
		cluster_files.write(cluster_line)
		num_clusters += 1
		current_line = str(num_clusters) + " " + str(len(unvisited))
		print current_line

		if not unvisited:
			break

if __name__ == '__main__':
	ipca(sys.argv[1], sys.argv[2])
