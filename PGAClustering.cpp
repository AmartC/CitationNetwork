
#include <omp.h>

#include <cstdlib>
#include <fstream>
#include <string>
#include <cmath>
#include <vector>
#include <unordered_map>

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

int relabel_comms(int N, int* comms)
{
  int* map = new int[N];
  for (int i = 0; i < N; ++i)
    map[i] = -1;

  int new_num = 0;
  for (int i = 0; i < N; ++i) {
    int comm = comms[i];
    if (map[comm] == -1)
      map[comm] = new_num++;
    comms[i] = map[comm];
  }
  delete [] map;

  return new_num;
}

int* louvain(graph* g)
{
  int max_iter = 35;

  int* final_comms = new int[g->num_verts];
  for (int i = 0; i < g->num_verts; ++i)
    final_comms[i] = i;

  graph* new_g = (graph*)malloc(sizeof(graph));
  copy_graph(g, new_g);

  int changes = 1;
  int outer_iter = 0;
  double Q_change = 1.0;

  printf("\nLouvain start - %d\n", new_g->num_verts);
  while (changes && outer_iter < max_iter && Q_change > 0.000001L)
  {
    printf("%d\n", ++outer_iter);
    Q_change = 0.0;
    changes = 0;

    int* comms = new int[new_g->num_verts];
    int* comm_internal_edges = new int[new_g->num_verts];
    int* comm_external_edges = new int[new_g->num_verts];
    for (int i = 0; i < new_g->num_verts; ++i) {
      comms[i] = i;
      comm_internal_edges[i] = 0;
      comm_external_edges[i] = 0;
      for (int j = 0; j < new_g->degrees[i]; ++j) {
        int out = new_g->edges[i][j];
        if (out == i)
          ++comm_internal_edges[i];
        else
          ++comm_external_edges[i];
      }
    }

    int iter_changes = 1;
    int inner_iter = 0;
    while (iter_changes && inner_iter < max_iter) {
      printf("%d ", ++inner_iter);
      iter_changes = 0;

#pragma omp parallel for schedule(guided) \
      reduction(+:iter_changes) reduction(+:Q_change) reduction(+:changes)
      for (int vert = 0; vert < new_g->num_verts; ++vert) {
        double max_delta_Q = 0.0;
        int max_comm = comms[vert];

        unordered_map<int, int> counts;
        for (int j = 0; j < new_g->degrees[vert]; ++j) {
          int comm_out = comms[new_g->edges[vert][j]];
          if (counts.count(comm_out) == 0)
            counts[comm_out] = 1;
          else
            counts[comm_out] = counts[comm_out] + 1;
        }

        for (int j = 0; j < new_g->degrees[vert]; ++j) {
          int out = new_g->edges[vert][j];
          if (vert != out && comms[out] != comms[vert])
          {
            int comm_out = comms[out];
            double sum_in = (double)comm_internal_edges[comm_out];
            double sum_tot = (double)(comm_internal_edges[comm_out] +
                                        comm_external_edges[comm_out]);
            double k_i = (double)new_g->degrees[vert];
            double k_i_in = (double)counts[comm_out];
            double m = (double)new_g->num_edges;
            double delta_Q =
              ( (sum_in + k_i_in) / m - pow((sum_tot + k_i) / m, 2.0) ) -
              ( (sum_in / m) - pow(sum_tot / m, 2.0) - pow(k_i / m, 2.0));

            if (delta_Q > max_delta_Q) {
              max_delta_Q = delta_Q;
              max_comm = comm_out;
            }
          }
        }

        if (max_comm != comms[vert]) {
          int cur_comm = comms[vert];
          for (int j = 0; j < new_g->degrees[vert]; ++j) {
            int out = new_g->edges[vert][j];
            if (comms[out] == max_comm) {
          #pragma omp atomic
              ++comm_internal_edges[max_comm];
          #pragma omp atomic
              --comm_external_edges[max_comm];
            }
            else if (comms[out] == cur_comm) {
          #pragma omp atomic
              --comm_internal_edges[cur_comm];
          #pragma omp atomic
              ++comm_external_edges[cur_comm];
            }
            else
          #pragma omp atomic
              ++comm_external_edges[max_comm];
          }
          comms[vert] = max_comm;
          ++changes;
          ++iter_changes;
          Q_change += max_delta_Q;
        }
      }
    }
    printf("%lf ", Q_change);

    if (changes && Q_change > 0) {
      int new_num_verts = relabel_comms(new_g->num_verts, comms);
      printf(" -- %d -- ", new_num_verts);
      int new_num_edges = new_g->num_edges;
      int* srcs = new int[new_num_edges];
      int* dsts = new int[new_num_edges];
      int counter = 0;
      for (int vert = 0; vert < new_g->num_verts; ++vert) {
        for (int j = 0; j < new_g->degrees[vert]; ++j) {
          int out = new_g->edges[vert][j];
          srcs[counter] = comms[vert];
          dsts[counter++] = comms[out];
        }
      }
      new_num_edges = counter;

      clear_graph(new_g);
      new_g->num_verts = new_num_verts;
      new_g->num_edges = new_num_edges;
      create_graph(new_g->num_verts, new_g->num_edges,
        srcs, dsts, new_g->degrees, new_g->edges);
      delete [] srcs;
      delete [] dsts;

      for (int i = 0; i < g->num_verts; ++i)
        final_comms[i] = comms[final_comms[i]];
    }

    delete [] comms;
    delete [] comm_internal_edges;
    delete [] comm_external_edges;
    printf("\n");
  }

  return final_comms;
}

int randomize_queue(int* queue, int size)
{
  for (int i = 0; i < size; ++i) {
    int temp_index = (unsigned)rand() % size;
    int temp_val = queue[temp_index];
    queue[temp_index] = queue[i];
    queue[i] = temp_val;
  }

  return 0;
}

int* label_prop(graph* g)
{
  int max_iter = 20;

  int* labels = new int[g->num_verts];
  for (int i = 0; i < g->num_verts; ++i)
    labels[i] = i;

  int* queue = new int[g->num_verts];
  for (int i = 0; i < g->num_verts; ++i)
    queue[i] = i;

  int changes = 1;
  int num_iter = 0;
  printf("\nLP start\n");
  while (changes && num_iter < max_iter)
  {
    printf("%d ", ++num_iter);
    changes = 0;
    randomize_queue(queue, g->num_verts);

#pragma omp parallel for schedule(guided) reduction(+:changes)
    for (int j = 0; j < g->num_verts; ++j) {
      int vert = queue[j];

      std::unordered_map<int, int> label_counts;
      vector<int> max_labels;
      int max_label = 0;

      for (int j = 0; j < g->degrees[vert]; ++j) {
        int out = g->edges[vert][j];
        int out_label = labels[out];
        if (label_counts.count(out_label) == 0)
          label_counts[out_label] = 1;
        else
          label_counts[out_label] = label_counts[out_label] + 1;

        if (label_counts[out_label] > max_label) {
          max_labels.clear();
          max_labels.push_back(out_label);
          max_label = label_counts[out_label];
        }
        else if (label_counts[out_label] == max_label) {
          max_labels.push_back(out_label);
        }
      }

      int max_index = 0;
      if (max_labels.size() > 1)
        max_index = (unsigned)rand() % max_labels.size();
      if (max_labels[max_index] != labels[vert]) {
        ++changes;
        labels[vert] = max_labels[max_index];
      }
    }
  }
  printf("\n");

  return labels;
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

  int* comms = louvain(&g);
  printf("Conductance: %lf\n", eval_conducatance(&g, comms));
  printf("Modularity: %lf\n", eval_modularity(&g, comms));
  std::ofstream louvain_file;
  louvain_file.open(argv[2]);
  for(int i = 0; i < num_verts; i++)
  {
    louvain_file<<i<<" "<<comms[i]<<std::endl;
  }
  louvain_file.close();

  int* comms2 = label_prop(&g);
  printf("Conductance: %lf\n", eval_conducatance(&g, comms2));
  printf("Modularity: %lf\n", eval_modularity(&g, comms2));
  std::ofstream lpa_file;
  lpa_file.open(argv[3]);
  for(int j = 0; j < num_verts; j++)
  {
    lpa_file<<j<<" "<<comms2[j]<<std::endl;
  }
  lpa_file.close();
  clear_graph(&g);

  return 0;
}
