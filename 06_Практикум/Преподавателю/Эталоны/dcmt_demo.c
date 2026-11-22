/* DCMT parameters are serialized field by field, never as a pointer-bearing struct. */
#include "dc.h"
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#ifdef _OPENMP
#include <omp.h>
#endif
static void write_parameters(FILE *f,int id,uint32_t seed,const mt_struct *m){
    fprintf(f,"%d %"PRIu32" %"PRIu32" %d %d %d %d %"PRIu32" %"PRIu32" %"PRIu32" %d %d %d %d %"PRIu32" %"PRIu32"\n",
        id,seed,m->aaa,m->mm,m->nn,m->rr,m->ww,m->wmask,m->umask,m->lmask,m->shift0,m->shift1,m->shiftB,m->shiftC,m->maskB,m->maskC);
}
static mt_struct *read_parameters(FILE *f,int expected_id,uint32_t *seed){
    mt_struct *m=calloc(1,sizeof(*m));if(!m)return NULL;int id;
    int fields=fscanf(f,"%d %"SCNu32" %"SCNu32" %d %d %d %d %"SCNu32" %"SCNu32" %"SCNu32" %d %d %d %d %"SCNu32" %"SCNu32,
        &id,seed,&m->aaa,&m->mm,&m->nn,&m->rr,&m->ww,&m->wmask,&m->umask,&m->lmask,&m->shift0,&m->shift1,&m->shiftB,&m->shiftC,&m->maskB,&m->maskC);
    if(fields!=16||id!=expected_id||m->nn<2||m->nn>4096||m->mm<1||m->mm>=m->nn||m->ww!=32||m->rr<0||m->rr>=32||m->shift0<1||m->shift0>31||m->shift1<1||m->shift1>31||m->shiftB<1||m->shiftB>31||m->shiftC<1||m->shiftC>31){free(m);return NULL;}
    m->state=calloc((size_t)m->nn,sizeof(*m->state));if(!m->state){free(m);return NULL;}return m;
}
int main(int argc,char **argv){
    if(argc==3&&!strcmp(argv[1],"create")){
        mt_struct *m[2]={NULL,NULL};
        for(int i=0;i<2;++i){m[i]=get_mt_parameter_id_st(32,521,i,4172);if(!m[i]){for(int j=0;j<i;++j)free_mt_struct(m[j]);return 3;}}
        FILE *f=fopen(argv[2],"w");if(!f){for(int i=0;i<2;++i)free_mt_struct(m[i]);return 3;}
        fputs("DCMT_PARAMS_V1 2\n",f);for(int i=0;i<2;++i){write_parameters(f,i,i==0?1234u:4567u,m[i]);free_mt_struct(m[i]);}
        if(fclose(f))return 3;puts("{\"streams\":2,\"created\":true}");return 0;
    }
    if(argc!=4||strcmp(argv[1],"run")){fprintf(stderr,"usage: dcmt_demo create FILE | run FILE N\n");return 2;}
    char *end;errno=0;long n=strtol(argv[3],&end,10);if(errno||end==argv[3]||*end||n<1||n>10000000)return 2;
    FILE *f=fopen(argv[2],"r");if(!f)return 2;char magic[32];int count;
    if(fscanf(f,"%31s %d",magic,&count)!=2||strcmp(magic,"DCMT_PARAMS_V1")||count!=2){fclose(f);return 2;}
    mt_struct *m[2]={NULL,NULL};uint32_t seed[2];
    for(int i=0;i<2;++i){m[i]=read_parameters(f,i,&seed[i]);if(!m[i]){for(int j=0;j<i;++j)free_mt_struct(m[j]);fclose(f);return 2;}sgenrand_mt(seed[i],m[i]);}
    fclose(f);uint64_t hashes[2]={0};
#ifdef _OPENMP
#pragma omp parallel for schedule(runtime)
#endif
    for(int i=0;i<2;++i){uint64_t hash=UINT64_C(1469598103934665603);for(long j=0;j<n;++j){hash^=genrand_mt(m[i]);hash*=UINT64_C(1099511628211);}hashes[i]=hash;}
    printf("{\"n_per_stream\":%ld,\"checksums\":[\"%"PRIu64"\",\"%"PRIu64"\"]}\n",n,hashes[0],hashes[1]);
    for(int i=0;i<2;++i)free_mt_struct(m[i]);return 0;
}
