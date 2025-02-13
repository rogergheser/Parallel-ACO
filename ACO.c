#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <float.h>
#include <time.h>

#define NUM_ANTS 100        // [50, 800]
#define NUM_ITERATIONS 40
#define ALPHA 1.0           // [3.0, 5.0]
#define BETA 2.0            // 3.0
#define EVAPORATION 0.5     // [0.4, 1.0] - 0.8 - Dorigo et al. found 0.99 for TSP
#define Q 100.0
#define DEBUG 0
// char* filename = "./tsplib/fnl4461.tsp";
char* filename = "./tsplib/burma_int14.tsp";
char pheromones_path[50]; // to save pheromones
char ant_tours_path[50]; // to save ants
int num_cities;
double **distance;
double **pheromones; 

double rand_double() {
    return (double)rand() / RAND_MAX;
}

void skip_lines(int lines, FILE *f) {
    char line[100];
    for(int i = 0; i < lines; i++)
        fgets(line, 100, f);
}

void write_int_matrix(int** mat, char* path) { 
    FILE *file = fopen(path, "w+");
    if (!file) {
        perror("Error opening file");
        exit(EXIT_FAILURE);
    }
    for (int i = 0; i < num_cities; i++) {
        for (int j = 0; j < num_cities; j++) {
            fprintf(file, "%d ", mat[i][j]);
        }
        fprintf(file, "\n");
    }
    fclose(file);
}

void write_double_matrix(double** mat, char* path) { 
    FILE *file = fopen(path, "w+");
    if (!file) {
        perror("Error opening file");
        exit(EXIT_FAILURE);
    }
    for (int i = 0; i < num_cities; i++) {
        for (int j = 0; j < num_cities; j++) {
            fprintf(file, "%lf ", mat[i][j]);
        }
        fprintf(file, "\n");
    }
    fclose(file);
}

void init_tsp() {
    FILE *file = fopen(filename, "r");
    if (!file) {
        perror("Error opening file");
        exit(EXIT_FAILURE);
    }

    skip_lines(3, file);    
    fscanf(file, "DIMENSION : %d", &num_cities);  // SOME FILES CONTAIN A SPACE BETWEEN 'DIMENSION' AND ':', OTHERS DO NOT
    skip_lines(5, file);

    // Allocate memory for coordinates and matrices
    double *x_coords = (double *)malloc(num_cities * sizeof(double));
    double *y_coords = (double *)malloc(num_cities * sizeof(double));
    distance = (double **)malloc(num_cities * sizeof(double *));
    pheromones = (double **)malloc(num_cities * sizeof(double *));
    for (int i = 0; i < num_cities; i++) {
        distance[i] = (double *)malloc(num_cities * sizeof(double));
        pheromones[i] = (double *)malloc(num_cities * sizeof(double));
    }
    
    // Read the coordinates
    for (int i = 0; i < num_cities; i++) {
        int index;
        fscanf(file, "%d \t %lf \t %lf", &index, &x_coords[i], &y_coords[i]);
    }
    
    // Compute distances matrix
    for (int i = 0; i < num_cities; i++) {
        for (int j = 0; j < num_cities; j++) {
            if (i == j) {
                distance[i][j] = 0.0;
            } else {
                double dx = x_coords[i] - x_coords[j];
                double dy = y_coords[i] - y_coords[j];
                distance[i][j] = sqrt(dx * dx + dy * dy);
            }
            // Initialize pheromones matrix
            pheromones[i][j] = 1.0;
        }
    }

    free(x_coords);
    free(y_coords);
    fclose(file);
}

// Choose the next city probabilistically
int select_next_city(int current_city, int *visited) {
    double *probabilities = (double *)malloc(num_cities * sizeof(double));
    double sum = 0.0;

    // Calculate probabilities
    for (int i = 0; i < num_cities; i++) {
        if (!visited[i]) {
            double tau = pow(pheromones[current_city][i], ALPHA);
            double eta = pow(1.0 / distance[current_city][i], BETA);
            probabilities[i] = tau * eta;
            sum += probabilities[i];
        } else {
            probabilities[i] = 0.0;
        }
    }

    // Normalize probabilities
    for (int i = 0; i < num_cities; i++) {
        probabilities[i] /= sum;
    }
    
    // Roulette wheel selection
    double r = rand_double();
    double cumulative = 0.0;
    for (int i = 0; i < num_cities; i++) {
        cumulative += probabilities[i];
        if (r <= cumulative) {
            free(probabilities);
            return i;
        }
    }
    
    return -1; // Should not reach here
}

void construct_solution(int *tour) {
    int *visited = (int *)calloc(num_cities, sizeof(int));
    int current_city = rand() % num_cities;
    //printf("I am starting in city %d \n", current_city);
    tour[0] = current_city;
    visited[current_city] = 1;

    for (int step = 1; step < num_cities; step++) {
        int next_city = select_next_city(current_city, visited);
        //printf("I am going to city %d, step %d \n", next_city, step);
        tour[step] = next_city;
        visited[next_city] = 1;
        current_city = next_city;
    }

    free(visited);
}

double evaluate_tour(int *tour) {
    double total_distance = 0.0;
    for (int i = 0; i < num_cities - 1; i++) {
        total_distance += distance[tour[i]][tour[i + 1]];
    }
    total_distance += distance[tour[num_cities - 1]][tour[0]];
    
    return total_distance;
}

void update_pheromones(int **ant_tours, double *ant_costs) {
    for (int i = 0; i < num_cities; i++) {
        for (int j = 0; j < num_cities; j++) {
            pheromones[i][j] *= (1.0 - EVAPORATION);
        }
    }

    // Deposit pheromones
    for (int k = 0; k < NUM_ANTS; k++) {
        double contribution = Q / ant_costs[k];
        for (int i = 0; i < num_cities - 1; i++) {
            int from = ant_tours[k][i];
            int to = ant_tours[k][i + 1];
            pheromones[from][to] += contribution;
            pheromones[to][from] += contribution;
        }
        // Complete the tour
        int from = ant_tours[k][num_cities - 1];
        int to = ant_tours[k][0];
        pheromones[from][to] += contribution;
        pheromones[to][from] += contribution;
    }
}

int main() {
    printf("Starting...\n");
    fflush(stdout);
    init_tsp();
    srand(time(NULL));

    int *best_tour = (int *)malloc(num_cities * sizeof(int));
    double best_cost = DBL_MAX;

    for (int iteration = 0; iteration < NUM_ITERATIONS; iteration++) {
        int **ant_tours = (int **)malloc(NUM_ANTS * sizeof(int *));
        for (int i = 0; i < NUM_ANTS; i++)
            ant_tours[i] = (int *)malloc(num_cities * sizeof(int));
        double ant_costs[NUM_ANTS];
        // For saving values

        sprintf(pheromones_path, "./data/pheromones/%d.txt", iteration);
        sprintf(ant_tours_path, "./data/ant_tours/%d.txt", iteration);
        
        
        // Step 1: Construct solutions
        for (int ant = 0; ant < NUM_ANTS; ant++) {
            //printf("I AM ANT %d \n", ant);
            construct_solution(ant_tours[ant]);
            ant_costs[ant] = evaluate_tour(ant_tours[ant]);
        }
        
        // Step 2: Find the best solution
        for (int ant = 0; ant < NUM_ANTS; ant++) {
            if (ant_costs[ant] < best_cost) {
                best_cost = ant_costs[ant];
                for (int i = 0; i < num_cities; i++) {
                    best_tour[i] = ant_tours[ant][i];
                }
            }
        }

        // Step 3: Update pheromones
        update_pheromones(ant_tours, ant_costs);
        if (DEBUG){
            write_double_matrix(pheromones, pheromones_path);
            write_int_matrix(ant_tours, ant_tours_path);
        }
        printf("Iteration %d: Best Cost = %f\n", iteration + 1, best_cost); // TODO: update best cost

        for (int i = 0; i < NUM_ANTS; i++)
            free(ant_tours[i]);
        free(ant_tours);
    }

    // Output the best tour
    printf("Best tour: ");
    for (int i = 0; i < num_cities; i++) {
        printf("%d ", best_tour[i]);
    }
    printf("\nBest cost: %f\n", best_cost);
    
    return 0;
}
