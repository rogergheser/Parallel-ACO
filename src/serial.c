#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
#include <math.h>
#include <float.h>
#include <sys/time.h>
#include <string.h>

#define NUM_ANTS 1024        // [50, 800]
#define NUM_ITERATIONS 10
#define ALPHA 4.0           // [3.0, 5.0]
#define BETA 3.0            // 3.0
#define EVAPORATION 0.9     // [0.4, 1.0] - 0.8 - Dorigo et al. found 0.99 for TSP
#define Q 100.0
#define NUM_CITIES 2048      // 783
#define MATRIX_DIM ((NUM_CITIES * (NUM_CITIES - 1)) / 2) // Triangular matrix size

char* filename = "./pACO/tsplib/d15112.tsp";
int num_cities;
double* distance;
double* pheromones;
int visited[NUM_CITIES];
double probabilities[NUM_CITIES];

typedef struct {
    int tour[NUM_CITIES];
    double tourLength;
} AntTour;

double rand_double() {
    return (double)rand() / RAND_MAX;
}

void skip_lines(int lines, FILE *f) {
    char line[100];
    int i;
    for(i = 0; i < lines; i++)
        fgets(line, 100, f);
}

int getIndex(int i, int j) {
    if (i >= j) {
        fprintf(stderr, "Invalid access: i (%d) should be less than j (%d)\n", i, j);
        exit(EXIT_FAILURE);
    }
    return (i * (2 * NUM_CITIES - i - 1)) / 2 + (j - i - 1);
}

void init_tsp() {
    FILE *file = fopen(filename, "r");
    int i, j, idx;
    if (!file) {
        perror("Error opening file");
        exit(EXIT_FAILURE);
    }

    skip_lines(6, file);    
    //fscanf(file, "DIMENSION : %d", &num_cities);  // SOME FILES CONTAIN A SPACE BETWEEN 'DIMENSION' AND ':', OTHERS DO NOT
    //skip_lines(5, file);

    // Allocate memory for coordinates and matrices
    double *x_coords = (double *)malloc(NUM_CITIES * sizeof(double));
    double *y_coords = (double *)malloc(NUM_CITIES * sizeof(double));
    distance = (double *)malloc(MATRIX_DIM * sizeof(double));
    pheromones = (double *)malloc(MATRIX_DIM * sizeof(double));

    if (!distance || !pheromones || !x_coords || !y_coords) {
        perror("Memory allocation failed");
        exit(EXIT_FAILURE);
    }
    
    // Read the coordinates
    for (i = 0; i < NUM_CITIES; i++) {
        int index;
        fscanf(file, "%d %lf %lf", &index, &x_coords[i], &y_coords[i]);
    }
    
    // Compute distances matrix
    for (i = 0; i < NUM_CITIES; i++) {
        for (j = i + 1; j < NUM_CITIES; j++) {
            double dx, dy;
            idx = getIndex(i, j);
            dx = x_coords[i] - x_coords[j];
            dy = y_coords[i] - y_coords[j];
            distance[idx] = sqrt(dx * dx + dy * dy);
            pheromones[idx] = 1.0;
        }
    }

    free(x_coords);
    free(y_coords);
    fclose(file);
}

int select_next_city(int current_city, int *visited) {
    int i;
    double sum = 0.0;
    double r, cumulative;
    
    for (i = 0; i < NUM_CITIES; i++)
        probabilities[i] = 0.0;
    
    for (i = 0; i < NUM_CITIES; i++) {
        if (!visited[i] && current_city != i) {
            int idx = (current_city < i) ? getIndex(current_city, i) : getIndex(i, current_city);
            double tau = pow(pheromones[idx], ALPHA);
            double eta = pow(1.0 / distance[idx], BETA);
            probabilities[i] = tau * eta;
            sum += probabilities[i];
        }
    }

    // Normalize probabilities
    for (i = 0; i < NUM_CITIES; i++) {
        probabilities[i] /= sum;
    }
    
    // Roulette wheel selection
    r = rand_double();
    cumulative = 0.0;
    for (i = 0; i < NUM_CITIES; i++) {
        cumulative += probabilities[i];
        if (r <= cumulative) {
            return i;
        }
    }
    
    // Should not reach here
    return -1; 
}

void construct_solution(int *tour) {
    int i, step, current_city, next_city;
    for (i = 0; i < NUM_CITIES; i++)
        visited[i] = 0;
    current_city = rand() % NUM_CITIES;
    tour[0] = current_city;
    visited[current_city] = 1;

    for (step = 1; step < NUM_CITIES; step++) {
        next_city = select_next_city(current_city, visited);
        tour[step] = next_city;
        visited[next_city] = 1;
        current_city = next_city;
    }
}

double evaluate_tour(int *tour) {
    double total_distance = 0.0;
    int i, idx;
    
    for (i = 0; i < NUM_CITIES - 1; i++) {
        idx = (tour[i] < tour[i + 1]) ? getIndex(tour[i], tour[i + 1]) : getIndex(tour[i + 1], tour[i]);
        total_distance += distance[idx];
    }
    idx = (tour[NUM_CITIES - 1] < tour[0]) ? getIndex(tour[NUM_CITIES - 1], tour[0]) : getIndex(tour[0], tour[NUM_CITIES - 1]);
    total_distance += distance[idx];

    return total_distance;
}

void update_pheromones(AntTour* ant_tours) {
    int i, j, k, idx, from, to, temp;
    double contribution;
    
    for (i = 0; i < NUM_CITIES; i++) {
        for (j = i + 1; j < NUM_CITIES; j++) {
            idx = getIndex(i, j);
            pheromones[idx] *= (1.0 - EVAPORATION);
        }
    }

    for (k = 0; k < NUM_ANTS; k++) {
        contribution = Q / ant_tours[k].tourLength;

        for (i = 0; i < NUM_CITIES; i++) {
            from = ant_tours[k].tour[i];
            to = ant_tours[k].tour[(i + 1) % NUM_CITIES];
            
            if (from > to) {
                temp = from;
                from = to;
                to = temp;
            }
            if (from != to) {
                idx = getIndex(from, to);
                pheromones[idx] += contribution;
            }
        }
    }
}

int main() {
    struct timeval start, end;
    int best_tour[NUM_CITIES];
    double best_cost = DBL_MAX;
    int iter, i;
    AntTour* ant_tours;

    init_tsp();
    srand(time(NULL));

    ant_tours = (AntTour *)malloc(NUM_ANTS * sizeof(AntTour));

    gettimeofday(&start, NULL);

    for (iter = 0; iter < NUM_ITERATIONS; iter++) {
        for (i = 0; i < NUM_ANTS; i++) {
            construct_solution(ant_tours[i].tour);
            ant_tours[i].tourLength = evaluate_tour(ant_tours[i].tour);
        }
        
        for (i = 0; i < NUM_ANTS; i++) {
            if (ant_tours[i].tourLength < best_cost) {
                best_cost = ant_tours[i].tourLength;
                memcpy(best_tour, ant_tours[i].tour, NUM_CITIES * sizeof(int));
            }
        }
        //printf("Iteration %d: Best Cost = %f\n", iter + 1, best_cost);

        update_pheromones(ant_tours);
    }

    gettimeofday(&end, NULL);
    double elapsed = (end.tv_sec - start.tv_sec) + (end.tv_usec - start.tv_usec) / 1e6;

    //printf("Best Tour Length: %lf\n", best_cost);
    /*
    printf("Best Tour Path: ");
    for (i = 0; i < NUM_CITIES; i++) {
        printf("%d ", best_tour[i]);
    }
    printf("\n");
    */
    //printf("Time: %.6f \n", elapsed);
    printf("SERIAL,%d,%d,1,1,%.6f,%lf\n", NUM_CITIES, NUM_ANTS, elapsed, best_cost);
    
    free(ant_tours);
    free(distance);
    free(pheromones);
    return 0;
}