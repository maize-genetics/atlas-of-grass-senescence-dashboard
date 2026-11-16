# Grass Senescence Atlas dashboard

Interactive companion to Ojeda-Rivera et al. (2026) *The Plant Cell*, doi:[10.1093/plcell/koag345](https://doi.org/10.1093/plcell/koag345).
Live site: https://maize-genetics.github.io/atlas-of-grass-senescence-dashboard/

The app is a Shiny app that runs entirely in the browser (shinylive / webR). Its code is the
`{shinylive-r}` block in `index.qmd`; `index.html` + `index_files/` are the rendered output.

## Render and preview locally

```sh
quarto preview index.qmd    # opens http://localhost:<port>/ ; data files are read from this folder
quarto render index.qmd     # writes index.html for deployment
```

Requires Quarto and the shinylive extension (bundled in `_extensions/`).

## Data files

| File | Used for | Built by |
|---|---|---|
| `metadata.rds` | sample metadata (season, tissue, week, date) | analysis repo |
| `mapping_full_xz.rds` | gene ID → orthogroup | analysis repo |
| `expr_shards/` | VST expression, fetched one shard per gene | `data_prep/build_expression_shards.py vst_full_xz.rds expr_shards` |
| `weather_daily.csv` | NEWA daily weather (°C, GDD) for both seasons | `data_prep/build_weather.py newa_data_23.txt newa_data_24.txt weather_daily.csv` |
| `ps_index.csv` | photosynthetic index per library (alternative time axis) | `data_prep/build_ps_index.py ../04_photosynthetic_index/data ps_index.csv` |
| `09_*`, `*_maizeminedescription.txt`, `module_plots*/` | WGCNA networks | `extract_underground_assets.R`, `generate_module_plots*.R` |

`expr_shards/shard_NNN.bin` hold 50 orthogroups each as uint16 little-endian, row-major,
value = round(VST × 1000) (lossless: the source VST has 3 decimals). `index.csv` maps
orthogroup → shard and row; `samples.txt` gives the column order.
