library(tidyverse)
library(matrixStats)

# Create output directory
dir.create("dashboard_data", showWarnings = FALSE)

# 1. Load data
cat("Loading metadata and counts...\n")
metadata <- readRDS("remob_explorer/metadata.rds")
vst_counts <- readRDS("remob_explorer/vst_counts_precomputed.rds")
gene_og_mapping <- readRDS("remob_explorer/gene_og_mapping.rds")

# 2. Summarize Expression Data
# We want to group by all variables that might be used for filtering/coloring
cat("Summarizing expression data (this may take a minute)...\n")

# Convert VST matrix to long format is too memory intensive for 16k x 2k
# Instead, we'll iterate through groups or use a more efficient way.
# Actually, 16k * 2k = 42M values. Tidyverse can handle this if we are careful.

# Let's define the groups first
group_vars <- c("species", "accession", "tissue", "week", "life_history")

# Create a sample-to-group mapping
sample_groups <- metadata %>%
  select(sample_id, all_of(group_vars))

# Function to summarize a chunk of OGs to avoid OOM
summarize_vst_chunk <- function(vst_subset, sample_groups) {
  vst_subset %>%
    as.data.frame() %>%
    rownames_to_column("OG") %>%
    pivot_longer(-OG, names_to = "sample_id", values_to = "expression") %>%
    inner_join(sample_groups, by = "sample_id") %>%
    group_by(OG, species, accession, tissue, week, life_history) %>%
    summarise(
      mean_expr = mean(expression, na.rm = TRUE),
      se_expr = sd(expression, na.rm = TRUE) / sqrt(n()),
      n = n(),
      .groups = "drop"
    )
}

# Process in chunks of 2000 OGs
all_ogs <- rownames(vst_counts)
chunk_size <- 2000
num_chunks <- ceiling(length(all_ogs) / chunk_size)

summary_list <- list()

for (i in 1:num_chunks) {
  start <- (i-1) * chunk_size + 1
  end <- min(i * chunk_size, length(all_ogs))
  cat(sprintf("Processing chunk %d/%d (OGs %d to %d)...\n", i, num_chunks, start, end))
  
  chunk_vst <- vst_counts[start:end, , drop = FALSE]
  summary_list[[i]] <- summarize_vst_chunk(chunk_vst, sample_groups)
}

expression_summary <- bind_rows(summary_list)

# 3. Save Summary
cat("Saving summarized expression data...\n")
saveRDS(expression_summary, "dashboard_data/expression_summary.rds")

# 4. Save Mapping (Filtered to OGs in VST)
cat("Saving gene mapping...\n")
gene_og_map_filtered <- gene_og_mapping %>%
  filter(Orthogroup %in% all_ogs)

saveRDS(gene_og_map_filtered, "dashboard_data/gene_og_map.rds")

# 5. Save simplified Metadata for the app
cat("Saving simplified metadata...\n")
saveRDS(metadata, "dashboard_data/metadata_simplified.rds")

cat("Pre-processing complete!\n")
