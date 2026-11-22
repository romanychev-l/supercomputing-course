DOC ?= template
DOCS := $(patsubst %/main.tex,%,$(wildcard */main.tex))
.PHONY: all pdf clean $(addprefix doc-,$(DOCS))
all: $(addprefix doc-,$(DOCS))
$(addprefix doc-,$(DOCS)): doc-%:
	$(MAKE) pdf DOC=$*
pdf:
	cd "$(DOC)" && latexmk -xelatex -interaction=nonstopmode -halt-on-error -file-line-error -outdir="../build/$(DOC)" main.tex
clean:
	cd "$(DOC)" && latexmk -C -outdir="../build/$(DOC)" main.tex
