# The Little Book of the Art of Computer Programming Solutions

A concise, structured companion of worked solutions and annotations to exercises from *The Art of Computer Programming*.

## Formats

* [Download PDF](docs/book.pdf) — print-ready
* [Download EPUB](docs/book.epub) — e-reader friendly
* [View LaTeX](docs/book-latex/book.tex) — `.tex` source
* [Read on GitHub Pages](https://little-book-of.github.io/taocp-solutions/) — online website
* [Read in Chinese (draft)](https://little-book-of.github.io/taocp-solutions/zh/) — Chinese website

## Build it yourself (Quarto)

Install Quarto: [https://quarto.org/docs/get-started/](https://quarto.org/docs/get-started/)

Preview locally (auto-reload):

```bash
quarto preview
```

Render outputs:

```bash
# All configured formats
quarto render

# Individual formats
quarto render --to html     # site into docs/
quarto render --to pdf      # docs/book.pdf
quarto render --to epub     # docs/book.epub
quarto render --to latex    # docs/book-latex/book.tex

# Chinese site (into docs/zh/)
quarto render --profile zh
```

## Contributing

All contributions are welcome—small fixes, new solutions, clarifications, figures, exercises, or larger structural improvements.

**How to contribute**

1. Open an issue to describe the change (or reference an existing one).
2. Fork the repository and create a branch for your work.
3. Keep commits focused, with short explanations in messages or the PR description.
4. Submit a pull request; include the section(s) you changed and a brief rationale.

**Style guidelines (brief)**

* Prefer concise, rigorous solutions with plain explanations.
* Keep notation consistent with *TAOCP*.
* Provide both reasoning and final answers where appropriate.
* Use LaTeX/MathJax for math; keep equations readable.

## Citation

Nguyen, Duc-Tam (2025). *The Little Book of the Art of Computer Programming Solutions (v0.1.0).*

```
@book{Nguyen2025TLBoTAOCPS,
  author = {Duc-Tam Nguyen},
  title  = {The Little Book of the Art of Computer Programming Solutions},
  year   = {2025},
  note   = {Version 0.1.0},
  url    = {https://github.com/little-book-of/taocps}
}
```

## License

This work is licensed under **CC BY-NC-SA 4.0**. See [LICENSE](LICENSE) for the full text.


## Multilingual site

This repository now ships two Quarto builds:

- default config (`_quarto.yml`) for the English site (`docs/`)
- zh profile (`_quarto-zh.yml`) for the Chinese site (`docs/zh/`)

On GitHub Pages, both are published together from `docs`, so the Chinese site is available at `/zh/`.
