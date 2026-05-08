suppressPackageStartupMessages({
  library(dplyr)
  library(tidyr)
  library(ggplot2)
  library(readr)
})

# --- Load data ---
eigengenes <- read_csv("08_module_eigengenes_samples_leaf.csv", show_col_types = FALSE)
ps_meta    <- readRDS("04_photosynthetic_index/data/leaf_metadata_ps_index.rds")

# Output directory (served as static resources)
dir.create("module_plots", showWarnings = FALSE)

# --- Reshape eigengenes to long format and join ps_index ---
eigen_long <- eigengenes %>%
  pivot_longer(-sample_id, names_to = "module_col", values_to = "eigengene") %>%
  mutate(module_label = sub("^ME_", "", module_col)) %>%
  left_join(ps_meta %>% select(sample_id, ps_index, week), by = "sample_id") %>%
  filter(!is.na(ps_index))

# Module color palette (must match WGCNA output colors)
umap_df <- read.csv("09_TOM_UMAP_embedding_leaf.csv", stringsAsFactors = FALSE)

# Build mapping: module_label (e.g. "m2_blue") -> ME column (e.g. "ME_blue") -> color hex
module_info <- umap_df %>%
  select(module_label, color) %>%
  distinct() %>%
  mutate(me_col = paste0("ME_", sub("^m[0-9]+_", "", module_label)))

cat("Module mapping:\n")
print(module_info)

modules <- module_info$module_label
cat("\nGenerating plots for", length(modules), "modules...\n")

for (mod in modules) {
  # Get the matching ME column name and hex color
  row      <- module_info %>% filter(module_label == mod)
  me_col   <- row$me_col
  mod_color <- row$color
  
  # Filter eigengene data for this module's ME column
  mod_data <- eigen_long %>% filter(module_col == me_col)
  if (nrow(mod_data) == 0) {
    cat("  Skipping", mod, "(no eigengene data)\n")
    next
  }
  
  n_libs <- n_distinct(mod_data$sample_id)
  
  p <- ggplot(mod_data, aes(x = ps_index, y = eigengene)) +
    geom_point(alpha = 0.25, size = 1.2, color = mod_color) +
    geom_smooth(method = "loess", span = 0.4, se = TRUE,
                color = mod_color, fill = mod_color, alpha = 0.2, linewidth = 1.2) +
    geom_hline(yintercept = 0, linetype = "dashed", color = "grey50", linewidth = 0.5) +
    scale_x_reverse(
      limits = c(1, 0),
      breaks = seq(1, 0, by = -0.25),
      labels = c("1\n(Photosynthesis)", "0.75", "0.50", "0.25", "0\n(Senescence)")
    ) +
    labs(
      title    = paste0("Module: ", mod),
      subtitle = paste0("Eigengene vs. Photosynthetic Index  |  n = ", n_libs, " libraries"),
      x        = "Photosynthetic Index",
      y        = "Module Eigengene"
    ) +
    theme_classic(base_size = 11) +
    theme(
      plot.title    = element_text(face = "bold", color = mod_color, size = 13),
      plot.subtitle = element_text(color = "grey40", size = 9),
      axis.title    = element_text(size = 10),
      plot.margin   = margin(10, 15, 10, 10)
    )
  
  out_path <- file.path("module_plots", paste0("module_", mod, ".png"))
  ggsave(out_path, plot = p, width = 5, height = 3.2, dpi = 120)
  cat("  Saved:", out_path, "\n")
}

cat("Done! Generated", length(modules), "module plots in ./module_plots/\n")
