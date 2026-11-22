#include <stdio.h>
#include <omp.h>

int main(void) {
    int threads = 1;
#pragma omp parallel
    {
#pragma omp single
        threads = omp_get_num_threads();
    }
    printf("threads=%d\n", threads);
    return 0;
}
