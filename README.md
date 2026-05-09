# Grass Senescence Atlas

Repo for rendering dashboard.

## Setup

The build environment (R, Quarto, plus all required R packages) is pinned in
[`pixi.toml`](pixi.toml). Install [pixi](https://pixi.sh) and:

```bash
pixi install     # materialize .pixi/envs/default from pixi.lock
pixi run render  # render index.qmd -> index.html
pixi run preview # live-reloading preview server
pixi run clean   # remove Quarto build artifacts
```

> [!NOTE]
> `pixi run render` automatically runs the `setup` task on first use, which
> CRAN-installs `shinylive` (not on conda-forge) and adds the
> `quarto-ext/shinylive` Quarto extension into `_extensions/`. Run
> `pixi task list` for the full task list.
