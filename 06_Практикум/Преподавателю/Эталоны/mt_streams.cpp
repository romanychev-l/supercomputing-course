#include <cstdint>
#include <cerrno>
#include <cstdlib>
#include <iostream>
#include <random>
#ifdef _OPENMP
#include <omp.h>
#endif
int main(int argc,char **argv){
    char *end=nullptr;errno=0;long n=argc==2?std::strtol(argv[1],&end,10):0;
    if(argc!=2||errno||end==argv[1]||*end||n<1||n>10000000)return 2;
    constexpr long block=1024;long blocks=(n+block-1)/block;
    unsigned long long checksum=0;int threads=1;
#ifdef _OPENMP
#pragma omp parallel
    {
#pragma omp single
        threads=omp_get_num_threads();
    }
#pragma omp parallel for schedule(runtime) reduction(^:checksum)
#endif
    for(long b=0;b<blocks;++b){
        /* A stream belongs to a fixed logical block, never to a thread number. */
        std::seed_seq seed{12345u,static_cast<unsigned>(b)};std::mt19937 gen(seed);
        unsigned long long hash=1469598103934665603ULL;
        for(long j=0;j<block && b*block+j<n;++j){hash^=gen();hash*=1099511628211ULL;}
        checksum^=hash;
    }
    std::cout<<"{\"n\":"<<n<<",\"threads\":"<<threads<<",\"checksum\":\""<<checksum<<"\"}\n";
}
