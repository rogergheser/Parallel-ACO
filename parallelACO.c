// Do not use it is just for reference
// It does work but we are no longer interested
#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
#include <math.h>
#include <float.h>
#include <time.h>
#include <string.h>
#include <mpi.h>
// TODO: in includes, possibly use openmp

#define NUM_ANTS 500        // [50, 800]
#define NUM_ITERATIONS 10
#define ALPHA 4.0           // [3.0, 5.0]
#define BETA 3.0            // 3.0
#define EVAPORATION 0.9     // [0.4, 1.0] - 0.8 - Dorigo et al. found 0.99 for TSP
#define Q 100.0
#define NUM_CITIES 783      // 783
#define MATRIX_DIM ((NUM_CITIES * (NUM_CITIES - 1)) / 2) // Triangular matrix size

char* filename = "./tsplib/rat783.tsp";  //rat783
double *distance;
double *pheromones; 

typedef struct {
    int tour[NUM_CITIES];
    double tourLength;
} AntTour;

void defineAntTourMPIType(MPI_Datatype *antTourType) {
    int blockLengths[2] = {NUM_CITIES, 1};
    MPI_Datatype types[2] = {MPI_INT, MPI_DOUBLE};
    MPI_Aint displacements[2];

    displacements[0] = offsetof(AntTour, tour);
    displacements[1] = offsetof(AntTour, tourLength);

    MPI_Type_create_struct(2, blockLengths, displacements, types, antTourType);
    MPI_Type_commit(antTourType);
}

double rand_double() {
    return (double)rand() / RAND_MAX;
}

void skip_lines(int lines, FILE *f) {
    char line[100];
    for(int i = 0; i < lines; i++)
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
    if (!file) {
        perror("Error opening file");
        exit(EXIT_FAILURE);
    }

    skip_lines(6, file);    
    //fscanf(file, "DIMENSION : %d", &num_cities);  // SOME FILES CONTAIN A SPACE BETWEEN 'DIMENSION' AND ':', OTHERS DO NOT
    //skip_lines(3, file);

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
    for (int i = 0; i < NUM_CITIES; i++) {
        int index;
        fscanf(file, "%d %lf %lf", &index, &x_coords[i], &y_coords[i]);
    }
    
    // Compute distances matrix
    for (int i = 0; i < NUM_CITIES; i++) {
        for (int j = i + 1; j < NUM_CITIES; j++) {
            int idx = getIndex(i, j);
            double dx = x_coords[i] - x_coords[j];
            double dy = x_coords[i] - y_coords[j];
            distance[idx] = sqrt(dx * dx + dy * dy);
            pheromones[idx] = 1.0;
        }
    }

    free(x_coords);
    free(y_coords);
    fclose(file);
}

int select_next_city(int current_city, int *visited) {
    double *probabilities = (double *)malloc(NUM_CITIES * sizeof(double));
    double sum = 0.0;
    // Calculate probabilities
    for (int i = 0; i < NUM_CITIES; i++) {
        if (!visited[i] && current_city != i) {
            int idx = (current_city < i) ? getIndex(current_city, i) : getIndex(i, current_city);
            double tau = pow(pheromones[idx], ALPHA);
            double eta = pow(1.0 / distance[idx], BETA);
            probabilities[i] = tau * eta;
            sum += probabilities[i];
        } else {
            probabilities[i] = 0.0;
        }
    }

    // Normalize probabilities
    for (int i = 0; i < NUM_CITIES; i++) {
        probabilities[i] /= sum;
    }
    
    // Roulette wheel selection
    double r = rand_double();
    double cumulative = 0.0;
    for (int i = 0; i < NUM_CITIES; i++) {
        cumulative += probabilities[i];
        if (r <= cumulative) {
            free(probabilities);
            return i;
        }
    }
    
    // Should not reach here
    free(probabilities);
    return -1; 
}

void construct_solution(int *tour) {
    int *visited = (int *)calloc(NUM_CITIES, sizeof(int));
    int current_city = rand() % NUM_CITIES;
    //printf("I am starting in city %d \n", current_city);
    tour[0] = current_city;
    visited[current_city] = 1;

    for (int step = 1; step < NUM_CITIES; step++) {
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
    for (int i = 0; i < NUM_CITIES - 1; i++) {
        int idx = (tour[i] < tour[i + 1]) ? getIndex(tour[i], tour[i + 1]) : getIndex(tour[i + 1], tour[i]);
        total_distance += distance[idx];
    }

    int idx = (tour[NUM_CITIES - 1] < tour[0]) ? getIndex(tour[NUM_CITIES - 1], tour[0]) : getIndex(tour[0], tour[NUM_CITIES - 1]);
    total_distance += distance[idx];

    return total_distance;
}
/* Old function
void update_pheromones(int **ant_tours, double *ant_costs) {
    for (int i = 0; i < MATRIX_DIM; i++) {
        pheromones[i] *= (1.0 - EVAPORATION);
    }

    for (int k = 0; k < NUM_ANTS; k++) {
        double contribution = Q / ant_costs[k];
        for (int i = 0; i < NUM_CITIES - 1; i++) {
            int from = ant_tours[k][i];
            int to = ant_tours[k][i + 1];
            int idx = (from < to) ? getIndex(from, to) : getIndex(to, from);
            pheromones[idx] += contribution;
        }
        int from = ant_tours[k][NUM_CITIES - 1];
        int to = ant_tours[k][0];
        int idx = (from < to) ? getIndex(from, to) : getIndex(to, from);
        pheromones[idx] += contribution;
    }
}
*/

void update_pheromones(AntTour *ant_tours, int num_ants) {
    // Evaporate pheromones
    for (int i = 0; i < NUM_CITIES; i++) {
        for (int j = i + 1; j < NUM_CITIES; j++) {  // Only update upper triangular part
            int idx = getIndex(i, j);
            pheromones[idx] *= (1.0 - EVAPORATION);
        }
    }
    
    // Deposit pheromones based on ant tours
    for (int k = 0; k < num_ants; k++) {
        double contribution = Q / ant_tours[k].tourLength;

        for (int i = 0; i < NUM_CITIES - 1; i++) {
            int from = ant_tours[k].tour[i];
            int to = ant_tours[k].tour[i + 1];
            //printf("%d, %d, From: %d - To: %d\n", k, i, from, to);
            // Ensure from < to before getting index
            if (from > to) {
                int temp = from;
                from = to;
                to = temp;
            }
            
            int idx = getIndex(from, to);
            pheromones[idx] += contribution;
        }
        
        // Complete the tour (return to starting city)
        int from = ant_tours[k].tour[NUM_CITIES - 1];
        int to = ant_tours[k].tour[0];
        
        // Ensure from < to before getting index
        if (from > to) {
            int temp = from;
            from = to;
            to = temp;
        }
        if (from != to) {
            int idx = getIndex(from, to);
            pheromones[idx] += contribution;
        }
    }
}

int main() {
    int comm_size, comm_rank;
    double start_time, end_time;

    MPI_Init(NULL, NULL);
    MPI_Comm_size(MPI_COMM_WORLD, &comm_size);
    MPI_Comm_rank(MPI_COMM_WORLD, &comm_rank);

    init_tsp();
    srand(time(NULL) + comm_rank); // Different seed for each process
    
    int ants_per_proc = NUM_ANTS / (comm_size - 1);
    int num_ants = ants_per_proc * (comm_size - 1);
    
    AntTour *ant_tours = (AntTour *)malloc(ants_per_proc * sizeof(AntTour));

    MPI_Datatype tourType;
    defineAntTourMPIType(&tourType);

    int best_tour[NUM_CITIES];
    double best_cost = DBL_MAX;

    if (comm_rank == comm_size - 1) 
        start_time = MPI_Wtime();

    for (int iter = 0; iter < NUM_ITERATIONS; iter++) {
        if (comm_rank != 0) {
            // Worker processes construct solutions
            for (int i = 0; i < ants_per_proc; i++) {
                construct_solution(ant_tours[i].tour);
                ant_tours[i].tourLength = evaluate_tour(ant_tours[i].tour);
                //printf("%d %d %f\n", comm_rank, i, ant_tours[i].tourLength);
            }
            // Send results to the master (rank 0)
            MPI_Send(ant_tours, ants_per_proc, tourType, 0, 0, MPI_COMM_WORLD);
        } else {
            // Master process collects all results
            AntTour *all_tours = (AntTour *)malloc(num_ants * sizeof(AntTour));

            for (int p = 1; p < comm_size; p++) {
                MPI_Recv(&all_tours[(p - 1) * ants_per_proc], ants_per_proc, tourType, p, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
            }
            
            // Find best tour in current iteration
            for (int i = 0; i < num_ants; i++) {
                if (all_tours[i].tourLength < best_cost) {
                    best_cost = all_tours[i].tourLength;
                    memcpy(best_tour, all_tours[i].tour, NUM_CITIES * sizeof(int));
                }
            }
            printf("Iteration %d: Best Cost = %f\n", iter + 1, best_cost);

            // Update pheromones
            update_pheromones(all_tours, num_ants);

            free(all_tours);
        }
        // Broadcast new pheromone matrix to all workers
        MPI_Bcast(pheromones, MATRIX_DIM, MPI_DOUBLE, 0, MPI_COMM_WORLD);
        // Sync processes before next iteration
        MPI_Barrier(MPI_COMM_WORLD);
    }

    if (comm_rank == 0) {
        end_time = MPI_Wtime();
        printf("Best Tour Length: %lf\n", best_cost);
        printf("Best Tour Path: ");
        for (int i = 0; i < NUM_CITIES; i++) {
            printf("%d ", best_tour[i]);
        }
        printf("\n");
        printf("Time: %lf\n", end_time - start_time); //TODO: adjust time taken
    }

    MPI_Finalize();
    free(ant_tours);
    free(distance);
    free(pheromones);
    return 0;
}
