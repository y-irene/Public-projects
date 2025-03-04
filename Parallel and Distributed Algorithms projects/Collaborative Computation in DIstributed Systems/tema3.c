#include "mpi.h"
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <string.h>

#define ROOT0 0 // First cluster parent
#define ROOT1 1 // Second cluster parent
#define ROOT2 2 // Third cluster parent

#define ROOTS 3 // Number of cluster parents

// Function that prints a topology based on the parents array
void print_topology (int rank, int numtasks, int *parent) {
    // Compute children arrays for each cluster parent
    int nchildren0 = 0, nchildren1 = 0, nchildren2 = 0;
    int children0[numtasks], children1[numtasks], children2[numtasks];
    for (int i = 0; i < numtasks; i++) {
        if (parent[i] == 0) {
            children0[nchildren0] = i;
            nchildren0++;
        } else if (parent[i] == 1) {
            children1[nchildren1] = i;
            nchildren1++;
        } else if (parent[i] == 2) {
            children2[nchildren2] = i;
            nchildren2++;
        }
    }

    // Print topology
    printf("%d -> 0:", rank);
    for (int i = 0; i < nchildren0; i++) {
        if (i != nchildren0 - 1) {
            printf("%d,", children0[i]);
        } else {
            printf("%d ", children0[i]);
        }
    }
    printf("1:");
    for (int i = 0; i < nchildren1; i++) {
        if (i != nchildren1 - 1) {
            printf("%d,", children1[i]);
        } else {
            printf("%d ", children1[i]);
        }
    }
    printf("2:");
    for (int i = 0; i < nchildren2; i++) {
        if (i != nchildren2 - 1) {
            printf("%d,", children2[i]);
        } else {
            printf("%d ", children2[i]);
        }
    }
    printf("\n");
}

int main (int argc, char *argv[])
{
    int  numtasks, rank, i, j;
    MPI_Init(&argc, &argv);
    MPI_Comm_size(MPI_COMM_WORLD, &numtasks);
    MPI_Comm_rank(MPI_COMM_WORLD,&rank);

    MPI_Comm roots;
    int *children = NULL, num_children;
    int *children0 = NULL, *children1 = NULL, *children2 = NULL;
    int nchildren0, nchildren1, nchildren2;
    int parent[numtasks];

    // Cluster parents read their topology
    if ((rank == ROOT0) || (rank == ROOT1) || (rank == ROOT2)) {
        FILE *f;
        if (rank == ROOT0) {
            f = fopen("cluster0.txt", "r");
        } else if (rank == ROOT1) {
            f = fopen("cluster1.txt", "r");
        } else if (rank == ROOT2) {
            f = fopen("cluster2.txt", "r");
        }

        fscanf(f, "%d", &num_children);
        children = (int *)calloc(num_children, sizeof(int));

        for (i = 0; i < num_children; i++) {
            fscanf(f, "%d", &(children[i]));
        }

        if (rank == ROOT0) {
            nchildren0 = num_children;
            children0 = children;
        } else if (rank == ROOT1) {
            nchildren1 = num_children;
            children1 = children;
        } else if (rank == ROOT2) {
            nchildren2 = num_children;
            children2 = children;
        }

        // Create a communicator with the cluster parents
        MPI_Comm_split(MPI_COMM_WORLD, 1, rank, &roots);
    } else {
        MPI_Comm_split(MPI_COMM_WORLD, MPI_UNDEFINED, rank, &roots);

    }

    // Cluster parents find out the topology
    if ((rank == ROOT0) || (rank == ROOT1) || (rank == ROOT2)) {
        // Each cluster parents broadcasts its number of children in the cluster
        // parents communicator
        MPI_Bcast(&nchildren0, 1, MPI_INT, ROOT0, roots);
        if (rank == ROOT0) {
            printf("M(0,1)\n");
            printf("M(0,2)\n");
        }
        MPI_Bcast(&nchildren1, 1, MPI_INT, ROOT1, roots);
        if (rank == ROOT1) {
            printf("M(1,0)\n");
            printf("M(1,2)\n");
        }
        MPI_Bcast(&nchildren2, 1, MPI_INT, ROOT2, roots);
        if (rank == ROOT2) {
            printf("M(2,0)\n");
            printf("M(2,1)\n");
        }

        if (rank != ROOT0)
            children0 = (int *)calloc(nchildren0, sizeof(int));
        if (rank != ROOT1)
            children1 = (int *)calloc(nchildren1, sizeof(int));
        if (rank != ROOT2)
            children2 = (int *)calloc(nchildren2, sizeof(int));

        // Each cluster parents broadcasts its children ids in the cluster
        // parents communicator
        MPI_Bcast(children0, nchildren0, MPI_INT, ROOT0, roots);
        if (rank == ROOT0) {
            printf("M(0,1)\n");
            printf("M(0,2)\n");
        }
        MPI_Bcast(children1, nchildren1, MPI_INT, ROOT1, roots);
        if (rank == ROOT1) {
            printf("M(1,0)\n");
            printf("M(1,2)\n");
        }
        MPI_Bcast(children2, nchildren2, MPI_INT, ROOT2, roots);
        if (rank == ROOT2) {
            printf("M(2,0)\n");
            printf("M(2,1)\n");
        }

        // Each cluster parent has the topology now, so they compute the parents
        // array and print the topology
        parent[0] = -1;
        parent[1] = -1;
        parent[2] = -1;
        for (i = 0; i < nchildren0; i++) {
            parent[children0[i]] = 0;
        }
        for (i = 0; i < nchildren1; i++) {
            parent[children1[i]] = 1;
        }
        for (i = 0; i < nchildren2; i++) {
            parent[children2[i]] = 2;
        }
        print_topology(rank, numtasks, parent);
    }

    if ((rank == ROOT0) || (rank == ROOT1) || (rank == ROOT2)) {
        // The cluster parents send the topology to their children
        for (i = 0; i < num_children; i++) {
            MPI_Send(parent, numtasks, MPI_INT, children[i], 0, MPI_COMM_WORLD);
            printf("M(%d,%d)\n", rank, children[i]);
        }
    } else {
        // Workers receive the parents array and print the topology
        MPI_Recv(parent, numtasks, MPI_INT, MPI_ANY_SOURCE, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
        print_topology(rank, numtasks, parent);
    }

    int n;
    int *v = NULL, **values;
    int num_computations[numtasks];
    int num_values;

    if (rank == ROOT0) {
        // The first cluster parent creates the values array
        n = atoi(argv[1]);
        v = (int *)calloc(n, sizeof(int));

        for (i = 0; i < n; i++) {
            v[i] = i;
        }

        // Split the array between all the workers
        int num_comp_per_process = n / (numtasks - ROOTS);
        for (i = 3; i < numtasks; i++) {
            num_computations[i] = num_comp_per_process;
        }
        int rest = n - num_comp_per_process * (numtasks - ROOTS);
        int worker = 3;
        while (rest) {
            num_computations[worker++]++;
            rest--;
        }
        num_values = num_computations[3];
        
        // Split the array into a matrix
        values = (int **)calloc((numtasks - ROOTS), sizeof(int *));
        int offset = 0;
        for (i = 0; i < numtasks - ROOTS; i++) {
            values[i] = (int *)calloc(num_values, sizeof(int));
            for (j = 0; j < num_computations[i + 3]; j++) {
                values[i][j] = v[offset + j];
            }
            offset += num_computations[i + 3];
        }
    }

    if ((rank == ROOT0) || (rank == ROOT1) || (rank == ROOT2)) {
        // The first cluster parent broadcasts the number of values each worker
        // will have to process in the cluster parent communicator
        MPI_Bcast(&num_values, 1, MPI_INT, ROOT0, roots);

        if (rank == ROOT0) {
            printf("M(0,1)\n");
            printf("M(0,2)\n");
        }

        // Each cluster parent sends the number of values each worker has to process
        // to its children workers
        for (i = 0; i < num_children; i++) {
            MPI_Send(&num_values, 1, MPI_INT, children[i], children[i], MPI_COMM_WORLD);
            printf("M(%d,%d)\n", rank, children[i]);
        }
    } else {
        // Workers receive the number of computations they have to do from 
        // their parent
        MPI_Recv(&num_values, 1, MPI_INT, parent[rank], rank, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
    }

    if (rank == ROOT0) {
        // First cluster parent send the values for each worker
        for(i = 3; i < numtasks; i++) {
            if (parent[i] != 0) {
                // To the worker parent, if the worker is not in its cluster
                MPI_Send(values[i - 3], num_values, MPI_INT, parent[i], i, MPI_COMM_WORLD);
                printf("M(%d,%d)\n", rank, parent[i]);
            } else {
                // Directly to the worker, if it is one of its children
                MPI_Send(values[i - 3], num_values, MPI_INT, i, i, MPI_COMM_WORLD);
                printf("M(%d,%d)\n", rank, i);
            }
        }

        int chunk[num_values];
        MPI_Status status;
        int worker;
        // First cluster parent waits to receive all the values from all the
        // workers
        for(i = 3; i < numtasks; i++) {
            MPI_Recv(chunk, num_values, MPI_INT, MPI_ANY_SOURCE, MPI_ANY_TAG, MPI_COMM_WORLD, &status);
            if (status.MPI_TAG == 0)
                // If the tag of the message is 0 (the cluster parent id), it means 
                // that the process that send the message is a children of the 
                // first cluster so the worker id is in the source field of the status
                worker = status.MPI_SOURCE;
            else    
                // Otherwise, it means that the message was sent by another cluster
                // parent for one of its children, so the worker id is in the tag
                // field of the status
                worker = status.MPI_TAG;
            memcpy(values[worker - 3], chunk, num_values * sizeof(int));
        }
    } else if ((rank == ROOT1) || (rank == ROOT2)) {
        int chunk[num_values];
        MPI_Status status;

        // Second and third cluster parents wait for the values for their workers.
        // When they get a message, they look into the message tag to find out
        // the destination worker and then forward it to the them.
        for (i = 0; i < num_children; i++) {
            MPI_Recv(chunk, num_values, MPI_INT, 0, MPI_ANY_TAG, MPI_COMM_WORLD, &status);
            int worker = status.MPI_TAG;
            MPI_Send(chunk, num_values, MPI_INT, worker, worker, MPI_COMM_WORLD);
            printf("M(%d,%d)\n", rank, worker);
        }
        // After that, they wait for the workers to send back the final values.
        // When they get a message, they look into the message source to find out
        // the id of the worker and they forward it to the first cluster parent.
        for (i = 0; i < num_children; i++) {
            MPI_Recv(chunk, num_values, MPI_INT, MPI_ANY_SOURCE, rank, MPI_COMM_WORLD, &status);
            int worker = status.MPI_SOURCE;
            MPI_Send(chunk, num_values, MPI_INT, 0, worker, MPI_COMM_WORLD);
            printf("M(%d,%d)\n", rank, 0);
        }
    } else {
        // The workers receive the values array from their parent, they do the 
        // processing and send them back to the parent.
        int chunk[num_values];
        MPI_Recv(chunk, num_values, MPI_INT, parent[rank], rank, MPI_COMM_WORLD, MPI_STATUS_IGNORE);

        for (i = 0; i < num_values; i++) {
            chunk[i] *= 2;
        }

        MPI_Send(chunk, num_values, MPI_INT, parent[rank], parent[rank], MPI_COMM_WORLD);
        printf("M(%d,%d)\n", rank, parent[rank]);
    }

    if (rank == ROOT0) {
        // In the end, the first cluster parent reassembles the vector and prints it
        int offset = 0;
        for (i = 0; i < numtasks - ROOTS; i++) {
            for (j = 0; j < num_computations[i + 3]; j++) {
                v[offset + j] = values[i][j];
            }
            offset += num_computations[i + 3];
        }

        printf("Rezultat:");
        for (i = 0; i < n; i++) {
            printf(" %d", v[i]);
        }
        printf("\n");

        for (i = 0; i < numtasks - ROOTS; i++) {
            free(values[i]);
        }
        free(values);
        free(v);
    }

    if ((rank == ROOT0) || (rank == ROOT1) || (rank == ROOT2)) {
        free(children0);
        free(children1);
        free(children2);
    }

    MPI_Finalize();
}