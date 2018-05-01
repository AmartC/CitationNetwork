import sys
import json
import unicodedata

if __name__ == "__main__":
    all_documents = sys.argv[1]
    encoded_values = sys.argv[2]
    document_hash= sys.argv[3]
    encoded_set = set()
    documents = []
    with open(encoded_values, 'rb') as encoded:
        for line in encoded:
            line = line.rstrip().split(" ")
            encoded_set.add(line[1])
    with open(all_documents) as a:
        for line in a:
            documents.append(line.rstrip())
    overall = 0
    written_doc = open(document_hash, 'wb')
    for doc in documents:
        with open(doc) as f:
            for line in f:
                parsed_json = json.loads(line)
                paper_id = parsed_json["id"]
                if not paper_id in encoded_set:
                    continue
                paper_title = parsed_json["title"].lower()
                paper_abstract = ""
                if "abstract" in parsed_json:
                    paper_abstract = parsed_json["abstract"].lower()
                combined = paper_title + " " + paper_abstract
                z = unicodedata.normalize("NFKD", combined).encode('ascii','ignore').replace('\n','')
                z = z.replace('\t', '')
                current_line = paper_id + " " + z + "\n"
                written_doc.write(current_line)
                overall += 1
                if overall % 1000000 == 0:
                    print overall
    written_doc.close()
