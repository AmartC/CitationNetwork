import sys

if __name__ == "__main__":
    query_file = sys.argv[1]
    query_nodes = sys.argv[2]
    node_degree = dict()
    query_degree = dict()
    output_file = sys.argv[3]

    all_query_nodes = set()
    with open(query_nodes, 'rb') as r:
        for line in r:
            line = line.rstrip()
            all_query_nodes.add(line)
    with open(query_file, 'rb') as q:
        for line in q:
            line = line.rstrip().split(" ")
            if not line[0] in node_degree:
                node_degree[line[0]] = set()
            for other in range(1, len(line)):
                node_degree[line[0]].add(line[other])
                if not line[other] in node_degree:
                    node_degree[line[other]] = set()
                node_degree[line[other]].add(line[0])

    for node in all_query_nodes:
        query_degree[node] = len(node_degree[node])

    current = open(output_file, 'wb')
    for node in query_degree:
        current_line = node + " " + str(query_degree[node]) + "\n"
        current.write(current_line)
    current.close()
