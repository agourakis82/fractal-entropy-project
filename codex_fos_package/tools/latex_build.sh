#!/usr/bin/env bash
set -euo pipefail

MANUSCRIPT_DIR="${1:-fos/manuscript/core}"
MAIN_TEX="${2:-main.tex}"
BIB_STYLE="${3:-sn-chicago}"

cd "$MANUSCRIPT_DIR"

# Auto-switch to sn-basic if sn-chicago.bst missing
if [[ "$BIB_STYLE" == "sn-chicago" && ! -f "sn-chicago.bst" ]]; then
  if [[ -f "sn-basic.bst" ]]; then
    echo ">> [latex_build] sn-chicago.bst not found; falling back to sn-basic.bst"
    sed -E -i.bak 's/\\bibliographystyle\{[^}]+\}/\\bibliographystyle{sn-basic}/' "$MAIN_TEX" || true
  else
    echo "WARN: Neither sn-chicago.bst nor sn-basic.bst found. Please copy one into $MANUSCRIPT_DIR."
  fi
fi

# Ensure class is present
if [[ ! -f "sn-jnl.cls" ]]; then
  echo "WARN: sn-jnl.cls not found in $MANUSCRIPT_DIR. Please copy it from the Springer template."
fi

# First pass
if command -v latexmk >/dev/null; then
  latexmk -C || true
  pdflatex "$MAIN_TEX"
  bibtex main || true
  pdflatex "$MAIN_TEX"
  pdflatex "$MAIN_TEX"
else
  pdflatex "$MAIN_TEX"
  bibtex main || true
  pdflatex "$MAIN_TEX"
  pdflatex "$MAIN_TEX"
fi

echo ">> [latex_build] Done. Output should be main.pdf"
