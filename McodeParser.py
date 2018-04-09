import sys

if __name__ == "__main__":
    tree_file = sys.argv[1]
    tracker = dict()
    with open(tree_file) as t:
        for line in t:
            if line[0] == '#':
                continue
            split_line = line.rstrip().split(" ")
            final_assignment = split_line[0].split(":")[0]
            node_name = int(split_line[3]) - 1
            tracker[node_name] = final_assignment

    output_file = sys.argv[2]
    output_file = open(output_file, 'wb')
    for num in range(0, len(tracker)):
        current_line = str(num) + " " + tracker[num] + "\n"
        output_file.write(current_line)
    output_file.close()
