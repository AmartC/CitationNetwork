# CitationNetwork
Note: This code is all written in Python2.
In order to create your initial query, run GraphingParser.py
Pass in keywords.txt which is the list of keywords to search through the title and abstract of the papers from MAG
allNodes.txt and allQuery.txt are files which will be created by this program.
Note that the names of the files that are taken in as input can be named anything, these are just suggested names.
keywords.txt and allQuery.txt have been provided to you as a sample here. allNodes.txt is an extremely large file so a truncated version has been given as reference called allNodesExample.txt. Running the command GraphingParser.py will create the allNodes.txt file.

Note, as an example, a simpler example was added for the purpose of files. allNodes1a.txt, allNodes1b.txt, allNodes1c.txt, allNodes1d.txt all are allNodes1.txt split into 4 smaller files because of restrictions on Github for file size. You should merge together the four files 

To concatenate all four files together run this command:
cat allNodes1a.txt allNodes1b.txt allNodes1c.txt allNodes1d.txt > allNodes1.txt
In addition, allQuery1.txt has been provided and Hashed1.txt
1. python GraphingParser.py [allPapers.txt] [keywords.txt] [allNodes1.txt] [allQuery1.txt]

Once the nodes of the initial query have been selected, run an n-hop expansion like this:
Hashed.txt is an adjacency list of all of the nodes that are part of the final query.


2. python GraphProcess.py [allNodes1.txt] [allQuery1.txt] [n] [Hashed1.txt]

For computing the modularity and conductance score of the six algorithms, the following process is applied,

To compute the score for Louvain and Label Propagation, the code PGAClustering.cpp contains the implementation of
both algorithms.

Thus, first we must encode the values of the graph in terms of 0 onwards. This is important because some of the algorithms
such as Infomap and Graclus require the first node to start from 1 instead.

Thus, to encode the nodes for Label Propagation and Louvain cluster analysis:
The 1 in this case is telling the program to output as the first line to the file PGAEdge.txt the number of nodes and edges
as this is required for the Louvain and Label Propagation node parsing.

3.python PGAEncoder.py [Hashed1.txt] [PGAEdge1.txt] [PGAEncode1.txt] 1

4. ./PGAClustering.exe [PGAEdge1.txt] [LouvainCluster1.txt] [LPACluster1.txt]

The files LouvainCluster1.txt and LPACluster1.txt can be used when computing the cosine similarity.


For Infomap, we use the Python script InfomapEncoder.py to encode the nodes in the graph starting from 1 onwards instead of 0.

5. python InfomapEncoder.py Hashed1.txt [InfomapEdge1.txt] [InfomapEncode1.txt] 0

From here, you can run the Infomap command like:
Note that you must create InfomapOutputDirectory before feeding it as a command.
6. ./Infomap [InfomapEdge1.txt] [InfomapOutputDirectory]

From there, go to the InfomapOutputDirectory which you specified and you should find a file called [InfomapEdge1].tree
collect the file and then run InfomapParser.py on it.
7. python InfomapParser.py [InfomapEdge1.tree] [InfomapClusters1.txt]

One thing you must note is that InfomapClusters1.txt begins with the nodes ordered at 1. Thus, in order to run this cluster
on the program which computes modularity and conductance, for each line in the file, the node should have 1 subtracted from it.
One way to do so is to use the program Format.py to subtract 1 from each node.

8. python Format.py [InfomapClusters1.txt] [RevisedInfomapClusters1.txt]
From there run ClusterEvaluation.exe which is compiled from ClusterEvaluation.cpp
You should use the same edge list as before which has the number of nodes and edges listed as before. This is a bit different
than the InfomapEdge.txt so the PGAEdges.txt file is used here. This will compute the modularity and conductance of the clusters
from Infomap.
9. ./ClusterEvaluation.exe PGAEdge11.txt RevisedInfomapClusters1.txt

For Graclus, like Infomap also requires the input nodes to start from 1 instead of 0.

10. python GraclusEncoder.py [Hashed1.txt] [GraclusEdge1.txt] [GraclusEncode1.txt] 1

Next, run the Graclus code which you can download from the project page.

11. ./graclus [GraclusEdge1.txt] [Number of clusters]

Next, we get the cluster assignments for each node. We use the program GraclusClusters.py which will
list the clusters of the nodes from 0 counting onwards.

12. python GraclusCluster.py [GraclusClusteringOutput] [GraclusClusters1.txt]

Next, we run the ClusterEvaluation to get the result:

13. ./ClusterEvaluation.exe PGAEdges1.txt [GraclusClusters1.txt]

The next algorithm run is MCODE. First, encode the graph so it reads as an adjacency list.
Use the program McodeEncoder.py

14. python McodeEncoder.py [McodeHashed.txt] [McodeEdges.txt] [EncodedMcode.txt] 0

Now run the Mcode program.

15. python Mcode.py [McodeEdges.txt] [McodeClusters.txt]

Now, get the clusters for each node starting from number 0.

16. python McodeClustering.py [McodeClusters.txt] [McodeResultClusters.txt]

Then run the ClusterEvaluation executable to compute the conductance and modularity of the clustering done by MCODE.

17. ./ClusterEvaluation.exe [PGAEdges.txt] [McodeResultClusters.txt]

The sixth and final algorithm is IPCA. The process is very similar to how MCODE is run.
In this case, the output from McodeEncoder.py can be used since the encoding technique is the same.
We rename it IpcaEdges.txt to make it easier to follow.

18. python Ipca.py [IpcaEdges.txt] [IpcaClusters.txt]

Next, run get the appropriate clusters.

19. python McodeClustering.py [IpcaClusters.txt] [IpcaResultClusters.txt]

Next, run cluster evaluation.
20. ./ClusterEvaluation.exe [IpcaEdges.txt] [IpcaResultClusters.txt]

Next, we compute the inter-cluster cosine similarity between different clusters.
The file to use is InterClusteringSimilarity.py

In this case, the alignment of beginning with 0 or 1 as the node does not matter as the program takes in the appropriate encoding
and will parse from there.
In addition, the program uses two text files. TitleAbstract.txt and PaperDegree.txt
PaperDegree.txt contains the degree of each paper that is part of the query.
TitleAbstract.txt is a pairing of the id of each paper and the value is the title and the abstract of the paper combined as a long string.

The program TitleHash.py is used to create this TitleAbstract.txt.

21. python TitleHash.py allPapers.txt [EncodedMcode.txt] [TitleAbstract.txt]

We also need to compute the degree of all papers that are part of the program. A short Python script can be written that
computes this from the adjacency matrix.
This is called PaperDegree.txt

From here, we can run the InterClusteringSimilarity.py script.
22. python InterClusteringSimilarity.py [EncodedNodes] [Clusters] [TitleAbstract.txt] [Output File] [PaperDegree.txt] [Path of TitleAbstract.txt and PaperDegree.txt]

We can also compute the Intra-cluster cosine similarity within the nodes in a cluster.

23. python ClusteringSimilarity.py [EncodedNodes] [Clusters] [TitleAbstract.txt] [Output file] [PaperDegree.txt] [Path of TitleAbstract.txt and PaperDegree.txt] [Largest cluster size before changing method of computing average cosine similarity]


