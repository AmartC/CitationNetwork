# CitationNetwork
Steps:
To access the Microsoft Academic Graph databse, go to the website https://www.openacademic.ai/oag/ and download the Microsoft Academic Graph zipfile.
1. python GraphingParser.py allPapers.txt keywords.txt allNodes.txt allQuery.txt
2. python GraphProcess.py allNodes.txt allQuery.txt 1 Hashed.txt
3. First for Louvain/Label propagation which are in the same code file,
python PGAEncoder.py Hashed.txt PGAEncoded.txt 1

4. ./PGAClustering.exe PGAEncoded.txt LouvainClusters.txt LPAClusters.txt
This will get the modularity and conductance for the label propagation and louvain and also will give the assignment of the clusters that each node belongs to for the Louvain and LPA clusters.

5. For Graclus
python GraclusEncoder.py Hashed.txt GraclusEncoded.txt 1
./graclus Hashed.txt 1000

6. Once the results from Graclus are obtained:
python GraclusClustering.py OutputFile GraclusResults.txt

7. ./ClusterEvaluation.exe GraclusResults.txt
This will give modularity and conductance for Graclus clustering

8. For Infomap
python InfomapEncoder.py Hashed.txt InfomapEncoded.txt 0
Then run Infomap 

run InfomapClustering.py on it

Then run ClusterEvaluation with the results

Then do same for MCODE and IPCA.

To compute the Inter-cluster cosine similarity:
python InterClusteringSimilarity.py Encoded.txt Clusters.txt TitleAbstract.txt [Output] PaperDegree.txt [Path of TitleAbstract.txt and PaperDegree.txt]


