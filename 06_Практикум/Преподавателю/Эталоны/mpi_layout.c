#include <mpi.h>
#include <stdio.h>
#include <stdlib.h>
int main(int argc,char **argv){
    MPI_Init(&argc,&argv);int r,p,ok=1;MPI_Comm_rank(MPI_COMM_WORLD,&r);MPI_Comm_size(MPI_COMM_WORLD,&p);
    /* A column [1,5,9] is received as a contiguous vector. */
    double matrix[12],column[3]={0};for(int i=0;i<12;++i)matrix[i]=i;
    MPI_Datatype col;MPI_Type_vector(3,1,4,MPI_DOUBLE,&col);MPI_Type_commit(&col);
    if(p==1)MPI_Sendrecv(matrix+1,1,col,0,7,column,3,MPI_DOUBLE,0,7,MPI_COMM_WORLD,MPI_STATUS_IGNORE);
    else if(r==0)MPI_Send(matrix+1,1,col,1,7,MPI_COMM_WORLD);
    else if(r==1)MPI_Recv(column,3,MPI_DOUBLE,0,7,MPI_COMM_WORLD,MPI_STATUS_IGNORE);
    if(p==1||r==1)for(int i=0;i<3;++i)if(column[i]!=1+4*i)ok=0;
    int bytes;MPI_Aint lb,extent;MPI_Type_size(col,&bytes);MPI_Type_get_extent(col,&lb,&extent);
    if(bytes!=3*(int)sizeof(double)||lb!=0||extent!=9*(MPI_Aint)sizeof(double))ok=0;
    MPI_Type_free(&col);
    /* Split: sum original ranks within each parity group. */
    MPI_Comm part;MPI_Comm_split(MPI_COMM_WORLD,r%2,r,&part);int s=0,expected=0;
    MPI_Allreduce(&r,&s,1,MPI_INT,MPI_SUM,part);
    for(int i=r%2;i<p;i+=2)expected+=i;if(s!=expected)ok=0;MPI_Comm_free(&part);
    /* Cartesian periodic ring. */
    MPI_Comm ring;int dims[]={p},periods[]={1},left,right,got=-1;
    MPI_Cart_create(MPI_COMM_WORLD,1,dims,periods,0,&ring);MPI_Cart_shift(ring,0,1,&left,&right);
    MPI_Sendrecv(&r,1,MPI_INT,right,3,&got,1,MPI_INT,left,3,ring,MPI_STATUS_IGNORE);
    if(got!=(r+p-1)%p)ok=0;MPI_Comm_free(&ring);
    /* Correct cumulative index for a star of any size, including p=1. */
    int *index=malloc((size_t)p*sizeof(int)),*edges=malloc((size_t)(p>1?2*(p-1):1)*sizeof(int));
    if(!index||!edges)MPI_Abort(MPI_COMM_WORLD,3);
    int pos=0;for(int i=0;i<p;++i){if(i==0){for(int j=1;j<p;++j)edges[pos++]=j;}else edges[pos++]=0;index[i]=pos;}
    MPI_Comm star;MPI_Graph_create(MPI_COMM_WORLD,p,index,edges,0,&star);
    int degree;MPI_Graph_neighbors_count(star,r,&degree);if(degree!=(r==0?p-1:1))ok=0;
    int *neighbors=malloc((size_t)(degree?degree:1)*sizeof(int));if(!neighbors)MPI_Abort(MPI_COMM_WORLD,3);
    MPI_Graph_neighbors(star,r,degree,neighbors);
    for(int i=0;i<degree;++i)if(neighbors[i]!=(r==0?i+1:0))ok=0;
    MPI_Comm_free(&star);free(neighbors);free(index);free(edges);
    int global;MPI_Allreduce(&ok,&global,1,MPI_INT,MPI_MIN,MPI_COMM_WORLD);
    if(!r)printf("{\"processes\":%d,\"ok\":%s,\"column\":[1,5,9],\"type_size\":%d,\"extent\":%lld}\n",p,global?"true":"false",bytes,(long long)extent);
    MPI_Finalize();return global?0:1;
}
