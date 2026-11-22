#include <stdio.h>
#include <mpi.h>

int main(int argc, char **argv) {
    MPI_Init(&argc, &argv);
    int rank, count, length;
    char name[MPI_MAX_PROCESSOR_NAME];
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &count);
    MPI_Get_processor_name(name, &length);
    printf("rank=%d processes=%d host=%.*s\n", rank, count, length, name);
    MPI_Finalize();
    return 0;
}
