# === Makefile: Foundations of Science (Springer) – CODEX ===
SHELL := /bin/bash

# Load config
ifneq (,$(wildcard config.env))
include config.env
export
endif

.PHONY: all clean pdf bib figures sanity package package-pdf docx check deps

all: deps figures pdf sanity

deps:
	@command -v pdflatex >/dev/null || { echo "ERROR: pdflatex not found."; exit 1; }
	@command -v bibtex    >/dev/null || { echo "ERROR: bibtex not found."; exit 1; }
	@command -v latexmk   >/dev/null || { echo "WARN: latexmk not found; will try plain pdflatex flow."; }

figures:
	@echo ">> [figures] Converting images under $(MANUSCRIPT_DIR)/$(FIG_DIR) (if needed)"
	@python3 tools/figconv.py --figdir "$(MANUSCRIPT_DIR)/$(FIG_DIR)" || true

pdf:
	@echo ">> [latex] Building PDF from $(MANUSCRIPT_DIR)/$(MAIN_TEX)"
	@bash tools/latex_build.sh "$(MANUSCRIPT_DIR)" "$(MAIN_TEX)" "$(BIB_STYLE)"

bib:
	@echo ">> [bib] Running BibTeX explicitly"
	@cd "$(MANUSCRIPT_DIR)" && bibtex main

sanity:
	@python3 tools/sanity_check.py --log "$(MANUSCRIPT_DIR)/main.log"

package:
	@echo ">> [pkg] Packaging submission source (without PDF) to $(DIST_DIR)/$(ZIP_SOURCE)"
	@python3 tools/prepare_zip.py --src "$(MANUSCRIPT_DIR)" --dist "$(DIST_DIR)" --zip "$(ZIP_SOURCE)" --with-pdf false

package-pdf:
	@echo ">> [pkg] Packaging review zip (with PDF) to $(DIST_DIR)/$(ZIP_WITH_PDF)"
	@python3 tools/prepare_zip.py --src "$(MANUSCRIPT_DIR)" --dist "$(DIST_DIR)" --zip "$(ZIP_WITH_PDF)" --with-pdf true

docx:
ifneq ($(MAKE_DOCX),true)
	@echo ">> [docx] Skipped (MAKE_DOCX=$(MAKE_DOCX))"
else
	@command -v pandoc >/dev/null || { echo "WARN: pandoc not found; skipping DOCX."; exit 0; }
	@echo ">> [docx] Generating DOCX via pandoc"
	@cd "$(MANUSCRIPT_DIR)" && pandoc "$(MAIN_TEX)" --bibliography="$(BIB_FILE)" --citeproc -o "$(DOCX_NAME)"
endif

check: sanity

clean:
	@echo ">> [clean] latexmk cleanup + dist purge"
	@cd "$(MANUSCRIPT_DIR)" && latexmk -C || true
	@rm -rf "$(DIST_DIR)"
	@mkdir -p "$(DIST_DIR)"
