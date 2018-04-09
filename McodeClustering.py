import sys

if __name__ == "__main__":
    tree_file = sys.argv[1]
    total_size = 1983837
    tracker = dict()
    counter = 0
    num_times = 0
    already_added = set()
    with open(tree_file) as t:
        for line in t:
            split_line = line.rstrip().split(" ")
            for node in split_line:
                if not node in already_added:
                    already_added.add(node)
                    tracker[int(node)] = counter
                    num_times += 1
            counter += 1

    counter += 1
    num_not_included = 0
    print num_times
    for a in range(0, total_size):
        if not a in tracker:
            tracker[a] = counter
            counter += 1

    print num_not_included
    print counter
    all_clusters = set()
    print min(tracker.keys())
    print len(tracker)
    output_file = sys.argv[2]
    output_file = open(output_file, 'wb')
    for num in range(0, len(tracker)):
        all_clusters.add(tracker[num])
        current_line = str(num) + " " + str(tracker[num]) + "\n"
        output_file.write(current_line)
    output_file.close()
    print len(all_clusters)
