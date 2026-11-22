#define _POSIX_C_SOURCE 200809L
#include <errno.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#ifdef _OPENMP
#include <omp.h>
#endif

static double wall(void) {
#ifdef _OPENMP
    return omp_get_wtime();
#else
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec + t.tv_nsec * 1e-9;
#endif
}
int main(int argc, char **argv) {
    if (argc != 3) { fprintf(stderr, "usage: kernels sum|dot|pi|matvec|tri|maxmin N\n"); return 2; }
    char *end; errno = 0; long v = strtol(argv[2], &end, 10);
    if (errno || *end || end == argv[2] || v < 1 || v > 10000000) return 2;
    int n = (int)v, threads = 1;
    const char *mode = argv[1];
    if (strcmp(mode,"sum") && strcmp(mode,"dot") && strcmp(mode,"pi") &&
        strcmp(mode,"matvec") && strcmp(mode,"tri") && strcmp(mode,"maxmin")) return 2;
    if ((!strcmp(mode,"matvec") || !strcmp(mode,"tri") || !strcmp(mode,"maxmin")) && n > 4096) return 2;
#ifdef _OPENMP
#pragma omp parallel
    {
#pragma omp single
        threads = omp_get_num_threads();
    }
#endif
    double value = 0.0, *a = NULL, *x = NULL, *y = NULL;
    if (!strcmp(mode, "matvec")) {
        a = malloc((size_t)n*n*sizeof(*a)); x = malloc((size_t)n*sizeof(*x)); y = malloc((size_t)n*sizeof(*y));
        if (!a || !x || !y) { free(a); free(x); free(y); return 3; }
        for (int j=0;j<n;++j) x[j]=j+1;
        for (int i=0;i<n;++i) for (int j=0;j<n;++j) a[(size_t)i*n+j]=(i==j?2.0:1.0);
    }
    double t=wall();
    if (!strcmp(mode,"sum")) {
#ifdef _OPENMP
#pragma omp parallel for reduction(+:value) schedule(runtime)
#endif
        for (int i=0;i<n;++i) value+=(i%97)-48;
    } else if (!strcmp(mode,"dot")) {
#ifdef _OPENMP
#pragma omp parallel for reduction(+:value) schedule(runtime)
#endif
        for (int i=0;i<n;++i) value+=(double)(i+1)*((i%7)-3);
    } else if (!strcmp(mode,"pi")) {
#ifdef _OPENMP
#pragma omp parallel for reduction(+:value) schedule(runtime)
#endif
        for (int i=0;i<n;++i) { double z=(i+0.5)/n; value+=4.0/(1.0+z*z); }
        value/=n;
    } else if (!strcmp(mode,"matvec")) {
#ifdef _OPENMP
#pragma omp parallel for schedule(runtime)
#endif
        for (int i=0;i<n;++i) { double s=0; for (int j=0;j<n;++j) s+=a[(size_t)i*n+j]*x[j]; y[i]=s; }
        /* Checksum is part of the reported kernel interval in both builds. */
        for (int i=0;i<n;++i) value+=y[i];
    } else if (!strcmp(mode,"tri")) {
#ifdef _OPENMP
#pragma omp parallel for reduction(+:value) schedule(runtime)
#endif
        for (int i=0;i<n;++i) { double s=0; for(int j=i;j<n;++j) s+=((i+j)%17)-8; value+=s; }
    } else {
        value=-INFINITY;
#ifdef _OPENMP
#pragma omp parallel for reduction(max:value) schedule(runtime)
#endif
        for(int i=0;i<n;++i) { double m=INFINITY; for(int j=0;j<n;++j) { double z=((17*i+13*j)%101)-50; if(z<m)m=z; } if(m>value)value=m; }
    }
    double elapsed=wall()-t;
    printf("{\"mode\":\"%s\",\"n\":%d,\"threads\":%d,\"value\":%.17g,\"seconds\":%.9g}\n",mode,n,threads,value,elapsed);
    free(a);free(x);free(y);return 0;
}
