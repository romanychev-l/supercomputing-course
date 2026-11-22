CC = cc
CXX = c++
MPICC = mpicc
CFLAGS = -O2 -std=c11 -Wall -Wextra -Wpedantic
CXXFLAGS = -O2 -std=c++17 -Wall -Wextra -Wpedantic
OMPFLAGS = -fopenmp
REF = Преподавателю/Эталоны
BUILD = build

.PHONY: all serial openmp mpi dcmt check
all: serial openmp mpi dcmt
serial: $(BUILD)/kernels_seq $(BUILD)/mt_seq
openmp: $(BUILD)/kernels_omp $(BUILD)/mt_omp
mpi: $(BUILD)/mpi_sum_pi $(BUILD)/mpi_halo $(BUILD)/mpi_layout
DCMT = Внешние_библиотеки/dcmt0.6.2
dcmt: $(BUILD)/dcmt_seq $(BUILD)/dcmt_omp
$(DCMT)/lib/libdcmt.a:
	$(MAKE) -C $(DCMT)/lib lib CC="$(CC)"
$(BUILD)/dcmt_seq: $(REF)/dcmt_demo.c $(DCMT)/lib/libdcmt.a | $(BUILD)
	$(CC) $(CFLAGS) -I$(DCMT)/include $< $(DCMT)/lib/libdcmt.a -o $@
$(BUILD)/dcmt_omp: $(REF)/dcmt_demo.c $(DCMT)/lib/libdcmt.a | $(BUILD)
	$(CC) $(CFLAGS) $(OMPFLAGS) -I$(DCMT)/include $< $(DCMT)/lib/libdcmt.a -o $@
$(BUILD):
	mkdir -p $(BUILD)
$(BUILD)/kernels_seq: $(REF)/kernels.c | $(BUILD)
	$(CC) $(CFLAGS) $< -lm -o $@
$(BUILD)/kernels_omp: $(REF)/kernels.c | $(BUILD)
	$(CC) $(CFLAGS) $(OMPFLAGS) $< -lm -o $@
$(BUILD)/mt_seq: $(REF)/mt_streams.cpp | $(BUILD)
	$(CXX) $(CXXFLAGS) $< -o $@
$(BUILD)/mt_omp: $(REF)/mt_streams.cpp | $(BUILD)
	$(CXX) $(CXXFLAGS) $(OMPFLAGS) $< -o $@
$(BUILD)/mpi_%: $(REF)/mpi_%.c | $(BUILD)
	$(MPICC) $(CFLAGS) $< -lm -o $@
check: all
	python3 Инструменты/verify.py
	python3 Инструменты/verify_dcmt.py
