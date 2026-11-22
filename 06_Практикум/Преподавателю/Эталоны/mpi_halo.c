#include <mpi.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
static int number(const char *s,int max){char *e;errno=0;long v=strtol(s,&e,10);return errno||e==s||*e||v<1||v>max?-1:(int)v;}
int main(int argc,char **argv){
    MPI_Init(&argc,&argv);int rank,p;MPI_Comm_rank(MPI_COMM_WORLD,&rank);MPI_Comm_size(MPI_COMM_WORLD,&p);
    int n=argc==3?number(argv[1],1000000):-1,steps=argc==3?number(argv[2],10000):-1;
    if(n<p||steps<1){if(!rank)fprintf(stderr,"usage: mpi_halo N STEPS; require 1<=p<=N\n");MPI_Finalize();return 2;}
    int *counts=malloc((size_t)p*sizeof(int)),*displs=malloc((size_t)p*sizeof(int));
    if(!counts||!displs)MPI_Abort(MPI_COMM_WORLD,3);
    for(int r=0;r<p;++r){counts[r]=n/p+(r<n%p);displs[r]=r*(n/p)+(r<n%p?r:n%p);}
    int k=counts[rank];double *old=calloc((size_t)k+2,sizeof(double)),*next=calloc((size_t)k+2,sizeof(double));
    double *all=rank==0?malloc((size_t)n*sizeof(double)):NULL;
    if(!old||!next||(!rank&&!all))MPI_Abort(MPI_COMM_WORLD,3);
    for(int i=1;i<=k;++i)old[i]=displs[rank]+i;
    int dims[]={p},periods[]={0};MPI_Comm cart;MPI_Cart_create(MPI_COMM_WORLD,1,dims,periods,0,&cart);
    int left,right;MPI_Cart_shift(cart,0,1,&left,&right);
    MPI_Barrier(cart);double t=MPI_Wtime();
    for(int step=0;step<steps;++step){
        old[0]=old[k+1]=0.0;MPI_Request req[4];
        MPI_Irecv(&old[0],1,MPI_DOUBLE,left,11,cart,&req[0]);
        MPI_Irecv(&old[k+1],1,MPI_DOUBLE,right,22,cart,&req[1]);
        MPI_Isend(&old[k],1,MPI_DOUBLE,right,11,cart,&req[2]);
        MPI_Isend(&old[1],1,MPI_DOUBLE,left,22,cart,&req[3]);
        for(int i=2;i<k;++i)next[i]=.25*old[i-1]+.5*old[i]+.25*old[i+1];
        MPI_Waitall(4,req,MPI_STATUSES_IGNORE);
        next[1]=.25*old[0]+.5*old[1]+.25*old[2];
        if(k>1)next[k]=.25*old[k-1]+.5*old[k]+.25*old[k+1];
        double *swap=old;old=next;next=swap;
    }
    double dt=MPI_Wtime()-t,mt;MPI_Reduce(&dt,&mt,1,MPI_DOUBLE,MPI_MAX,0,cart);
    MPI_Gatherv(old+1,k,MPI_DOUBLE,all,counts,displs,MPI_DOUBLE,0,cart);
    if(!rank){printf("{\"n\":%d,\"steps\":%d,\"processes\":%d,\"seconds\":%.9g,\"values\":[",n,steps,p,mt);for(int i=0;i<n;++i)printf("%s%.17g",i?",":"",all[i]);puts("]}");}
    MPI_Comm_free(&cart);free(counts);free(displs);free(old);free(next);free(all);MPI_Finalize();return 0;
}
