#include <mpi.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int main(int argc,char **argv) {
    MPI_Init(&argc,&argv);
    int rank,p;MPI_Comm_rank(MPI_COMM_WORLD,&rank);MPI_Comm_size(MPI_COMM_WORLD,&p);
    char *end=NULL;errno=0;long n=(argc==3?strtol(argv[2],&end,10):0);
    int valid=argc==3 && !errno && end!=argv[2] && !*end && n>0 && n<=10000000 &&
        (!strcmp(argv[1],"sum") || !strcmp(argv[1],"pi"));
    if(!valid){if(!rank)fprintf(stderr,"usage: mpi_sum_pi sum|pi N (1..10000000)\n");MPI_Finalize();return 2;}
    long q=n/p,rem=n%p,count=q+(rank<rem),start=rank*q+(rank<rem?rank:rem);
    MPI_Barrier(MPI_COMM_WORLD);double t=MPI_Wtime(),local=0.0,total=0.0;
    if(!strcmp(argv[1],"sum"))for(long i=start;i<start+count;++i)local+=(i%97)-48;
    else for(long i=start;i<start+count;++i){double x=(i+0.5)/n;local+=4.0/(1+x*x)/n;}
    MPI_Reduce(&local,&total,1,MPI_DOUBLE,MPI_SUM,0,MPI_COMM_WORLD);
    double elapsed=MPI_Wtime()-t,max_time=0;
    MPI_Reduce(&elapsed,&max_time,1,MPI_DOUBLE,MPI_MAX,0,MPI_COMM_WORLD);
    if(!rank)printf("{\"mode\":\"%s\",\"n\":%ld,\"processes\":%d,\"value\":%.17g,\"seconds\":%.9g}\n",argv[1],n,p,total,max_time);
    MPI_Finalize();return 0;
}
