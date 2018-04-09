#include <omp.h>
#include <cstdlib>
#include <fstream>
#include <string>
#include <cmath>
#include <vector>
#include <unordered_map>
#include <map>

struct graph {
  int num_verts;
  int num_edges;

  int* degrees;
  int** edges;
} ;
#define out_degree(g, v) (g->degrees[v])
#define out_edges(g, v) (g->edges[v])
#define out_edge(g, v, i) (g->edges[v][i])

typedef int vertex;
typedef int edge;

using namespace std;

void read_edge(char* filename,
  int& num_verts, int& num_edges,
  int*& srcs, int*& dsts)
{
  ifstream infile;
  string line;
  infile.open(filename);

  getline(infile, line, ' ');
  num_verts = atoi(line.c_str());
  getline(infile, line);
  num_edges = atoi(line.c_str());

  int src, dst;
  int counter = 0;

  num_edges *= 2;
  srcs = new int[num_edges];
  dsts = new int[num_edges];
  for (unsigned i = 0; i < num_edges/2; ++i)
  {
    getline(infile, line, ' ');
    src = atoi(line.c_str());
    getline(infile, line);
    dst = atoi(line.c_str());

    srcs[counter] = src;
    dsts[counter] = dst;
    ++counter;
    srcs[counter] = dst;
    dsts[counter] = src;
    ++counter;
  }

  infile.close();
}

void create_graph(int num_verts, int num_edges,
  int* srcs, int* dsts,
  int*& degrees, int**& edges)
{
  degrees = new int[num_verts];
  edges = new int*[num_verts];

  for (int i = 0; i < num_verts; ++i)
    degrees[i] = 0;
  for (int i = 0; i < num_edges; ++i)
    ++degrees[srcs[i]];
  for (int i = 0; i < num_verts; ++i)
    edges[i] = new int[degrees[i]];
  for (int i = 0; i < num_verts; ++i)
    degrees[i] = 0;
  for (int i = 0; i < num_edges; ++i)
    edges[srcs[i]][degrees[srcs[i]]++] = dsts[i];

  int max_degree = 0;
  for (int i = 0; i < num_verts; ++i)
    if (degrees[i] > max_degree)
      max_degree = degrees[i];

  printf("max %d\n", max_degree);
}

void clear_graph(graph* g)
{
  delete [] g->degrees;
  for (int i = 0; i < g->num_verts; ++i)
    delete [] g->edges[i];
  delete [] g->edges;

  g->num_verts = 0;
  g->num_edges = 0;
}

void copy_graph(graph* g, graph* new_g)
{
  new_g->num_verts = g->num_verts;
  new_g->num_edges = g->num_edges;
  new_g->degrees = new int[g->num_verts];
  std::copy(g->degrees, g->degrees+g->num_verts, new_g->degrees);

  new_g->edges = new int*[g->num_verts];
  for (int i = 0; i < g->num_verts; ++i) {
    new_g->edges[i] = new int[g->degrees[i]];
    std::copy(g->edges[i], g->edges[i]+g->degrees[i], new_g->edges[i]);
  }
}


double eval_conducatance(graph* g, int* comms)
{
  int* ext_edges = new int[g->num_verts];
  int* int_edges = new int[g->num_verts];
  for (int i = 0; i < g->num_verts; ++i) {
    ext_edges[i] = 0;
    int_edges[i] = 0;
  }

  for (int vert = 0; vert < g->num_verts; ++vert) {
    for (int j = 0; j < g->degrees[vert]; ++j) {
      int out = g->edges[vert][j];
      if (comms[out] != comms[vert])
        ++ext_edges[comms[vert]];
      else
        ++int_edges[comms[vert]];
    }
  }

  double total_conductance = 0.0;
  int num_comms = 0;
  for (int i = 0; i < g->num_verts; ++i) {
    if (ext_edges[i] > 0 || int_edges[i] > 0) {
      total_conductance += (double)ext_edges[i] / (double)(ext_edges[i] + int_edges[i]);
      ++num_comms;
    }
  }

  total_conductance /= (double)num_comms;

  return total_conductance;
}


double eval_modularity(graph* g, int* comms)
{
  double modularity = 0.0;

  for (int vert = 0; vert < g->num_verts; ++vert) {
    for (int j = 0; j < g->degrees[vert]; ++j) {
      int out = g->edges[vert][j];
      if (comms[out] == comms[vert])
        modularity += (1.0 - (double)(g->degrees[vert]*g->degrees[out]) / (double)(g->num_edges) );
    }
  }

  modularity /= (double)(g->num_edges);

  return modularity;
}

int main(int argc, char** argv)
{
  setbuf(stdout, NULL);
  int* srcs;
  int* dsts;
  int num_verts;
  int num_edges;
  int* degrees;
  int** edges;

  read_edge(argv[1], num_verts, num_edges, srcs, dsts);
  create_graph(num_verts, num_edges, srcs, dsts,
    degrees, edges);
  graph g = {num_verts, num_edges, degrees, edges};
  delete [] srcs;
  delete [] dsts;
  int* comms = new int[num_verts];
  map<int, int> vertex_assignments;
  std::ifstream cluster_assignment(argv[2], std::ios::in);
  int node_num;
  int cluster_given;
  while(cluster_assignment >> node_num >> cluster_given)
  {
    vertex_assignments[node_num] = cluster_given;
  }
  for(int i = 0; i < num_verts; i++)
  {
    comms[i] = vertex_assignments[i];
  }


  //int* comms = louvain(&g);
  printf("Conductance: %lf\n", eval_conducatance(&g, comms));
  printf("Modularity: %lf\n", eval_modularity(&g, comms));

  //int* comms2 = label_prop(&g);
  //printf("Conductance: %lf\n", eval_conducatance(&g, comms2));
  //printf("Modularity: %lf\n", eval_modularity(&g, comms2));
  clear_graph(&g);

  return 0;
}
