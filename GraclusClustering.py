import sys

if __name__ == "__main__":
    tree_file = sys.argv[1]
    tracker = dict()
    counter = 1
    with open(tree_file) as t:
        for line in t:
            line = line.rstrip()
            tracker[counter] = line
            counter += 1

    output_file = sys.argv[2]
    output_file = open(output_file, 'wb')
    for num in range(1, len(tracker) + 1):
        current_line = str(num) + " " + tracker[num] + "\n"
        output_file.write(current_line)
    output_file.close()
