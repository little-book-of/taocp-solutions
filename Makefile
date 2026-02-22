SHELL := /bin/bash

QUARTO ?= quarto
QUARTO_VERSION ?= 1.7.32
QUARTO_DIR ?= .tools/quarto
QUARTO_BIN := $(QUARTO_DIR)/bin/quarto
PYTHON ?= python3

.PHONY: help install-deps check-quarto install-quarto preview render render-en render-zh translate-zh clean

help:
	@echo "Targets:"
	@echo "  make install-deps    - Install Python deps (deep-translator)"
	@echo "  make install-quarto  - Download Quarto CLI locally into .tools/quarto"
	@echo "  make check-quarto    - Print Quarto version"
	@echo "  make translate-zh    - Translate source book content into zh/"
	@echo "  make preview         - Run local preview (English profile)"
	@echo "  make render          - Render English + Chinese sites (HTML)"
	@echo "  make render-en       - Render default site (HTML)"
	@echo "  make render-zh       - Render Chinese site config (HTML)"
	@echo "  make clean           - Remove generated docs"

install-deps:
	$(PYTHON) -m pip install --upgrade deep-translator

check-quarto:
	@command -v $(QUARTO) >/dev/null 2>&1 || { echo "Quarto not found in PATH. Run 'make install-quarto' or install globally."; exit 1; }
	@$(QUARTO) --version

install-quarto:
	@set -euo pipefail; \
	mkdir -p .tools; \
	if [[ "$$(uname -s)" != "Linux" ]]; then \
	  echo "Automatic install target currently supports Linux only."; \
	  echo "Please install Quarto from https://quarto.org/docs/get-started/"; \
	  exit 1; \
	fi; \
	ARCH="$$(uname -m)"; \
	if [[ "$$ARCH" == "x86_64" ]]; then ARCH="amd64"; fi; \
	if [[ "$$ARCH" == "aarch64" || "$$ARCH" == "arm64" ]]; then ARCH="arm64"; fi; \
	PKG="quarto-$(QUARTO_VERSION)-linux-$$ARCH.tar.gz"; \
	URL="https://github.com/quarto-dev/quarto-cli/releases/download/v$(QUARTO_VERSION)/$$PKG"; \
	echo "Downloading $$URL"; \
	curl -fsSL "$$URL" -o .tools/$$PKG; \
	rm -rf $(QUARTO_DIR); \
	tar -xzf .tools/$$PKG -C .tools; \
	mv .tools/quarto-$(QUARTO_VERSION) $(QUARTO_DIR); \
	rm -f .tools/$$PKG; \
	$(QUARTO_BIN) --version

translate-zh:
	$(PYTHON) scripts/translate_to_zh.py

preview: check-quarto
	$(QUARTO) preview

render: check-quarto render-en render-zh

render-en: check-quarto
	$(QUARTO) render --to html

render-zh: check-quarto
	$(QUARTO) render _quarto-zh.yml --to html

clean:
	rm -rf docs
