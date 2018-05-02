import sys

if __name__ == "__main__":
    first_file = sys.argv[1]
    output_file = sys.argv[2]
    opened_output = open(output_file, 'wb')
    with open(first_file, 'rb') as first:
        for line in first:
            line = line.rstrip().split(" ")
            first_val = int(line[0]) - 1
            cluster = line[1]
            str_line = str(first_val) + " " + cluster + "\n"
            opened_output.write(str_line)
    opened_output.close()
