import sys

if __name__ == "__main__":
    query_file = sys.argv[1]
    node_degree = dict()
    query_degree = dict()
    output_file = sys.argv[2]
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

    for node in node_degree:
        query_degree[node] = len(node_degree[node])

    current = open(output, 'wb')
    for node in query_degree:
        current_line = node + " " + str(query_degree[node]) + "\n"
        current.write(current_line)
    current.close()
