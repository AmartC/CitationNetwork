import sys

if __name__ == "__main__":
    file_name = sys.argv[1]
    modified_edge_list = sys.argv[2]
    encoded_data = sys.argv[3]
    add_first = int(sys.argv[4])
    encoder = dict()
    reverse_encoder = dict()
    edge_dict = dict()
    placed = set()
    counter = 0
    num_edges = 0
    with open(file_name) as f:
        for line in f:
            result = line.rstrip().split(" ")
            for a in range(0, len(result)):
                if result[a] not in reverse_encoder:
                    encoder[counter] = result[a]
                    reverse_encoder[result[a]] = counter
                    counter += 1
            edge_dict[reverse_encoder[result[0]]] = set()
            for b in range(1, len(result)):
                num_edges += 1
                edge_dict[reverse_encoder[result[0]]].add(reverse_encoder[result[b]])

    new_edges = open(modified_edge_list, 'wb')
    a = edge_dict.keys()
    a.sort()
    if add_first == 1:
        first_line = str(len(encoder))
        first_line += (" " + str(num_edges) + "\n")
        new_edges.write(first_line)

    for c in a:
        current_line = str(c)
        for d in edge_dict[c]:
            current_line += " " + str(d)
        current_line += "\n"
        new_edges.write(current_line)
    new_edges.close()

    coded_data = open(encoded_data, 'wb')
    for c in range(0, len(encoder)):
        current_line = str(c)
        current_line += (" " + encoder[c] + "\n")
        coded_data.write(current_line)
    coded_data.close()
