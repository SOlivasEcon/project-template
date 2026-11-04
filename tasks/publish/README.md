# publish

Copies the paper's figures and tables from the task outputs into `paper/generated/`, as listed in
`paper/generated_manifest.csv`, and fails if an `\includegraphics` or `\input` in `paper/` or `paper/slides/`
does not resolve. If `SHARED_OUTPUT_ROOT` is set, it also mirrors `paper/generated/` there for coauthors.

`paper/generated/tables/` is tracked by git and `paper/generated/figures/` is not; both are kept by
`python -m SCons -c`. Compile the paper afterwards with `latexmk` in `paper/`.

- **Inputs:** the task outputs listed in `paper/generated_manifest.csv`.
