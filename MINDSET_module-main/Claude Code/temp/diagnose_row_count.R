library(readxl)
library(dplyr)
library(tidyr)

cat("=== DIAGNOSING ROW COUNT ISSUE ===\n\n")

# 1. Check crosswalk
crosswalk_file <- "C:/Users/festeves/OneDrive - RAND Corporation/Courses/Dissertation/3rd Paper/Data/GLORIA-Eora26 - Crosswalk.xlsx"
crosswalk_raw <- read_excel(crosswalk_file, sheet = "Eora26 - GLORIA")

product_col <- names(crosswalk_raw)[1]
sector_cols <- names(crosswalk_raw)[-1]

cat("CROSSWALK:\n")
cat("  Total products:", nrow(crosswalk_raw), "\n")
cat("  Unique products:", n_distinct(crosswalk_raw[[product_col]]), "\n")
cat("  Product column name: '", product_col, "'\n", sep="")

# Check for whitespace issues
products_trimmed <- trimws(crosswalk_raw[[product_col]])
cat("  After trimming whitespace:", n_distinct(products_trimmed), "\n\n")

# Count multi-sector products
crosswalk_raw$n_sectors <- rowSums(crosswalk_raw[, sector_cols], na.rm = TRUE)
cat("  Products by number of sectors:\n")
print(table(crosswalk_raw$n_sectors))

multi_prods <- crosswalk_raw %>% filter(n_sectors > 1)
cat("\n  Multi-sector products:\n")
for(i in 1:nrow(multi_prods)) {
  pname <- multi_prods[[product_col]][i]
  nsec <- multi_prods$n_sectors[i]
  cat("    -", pname, "(", nsec, "sectors )\n")
}

# 2. Check one country file
cat("\n\nCOUNTRY FILE (MEX):\n")
mex_file <- "C:/Users/festeves/OneDrive - RAND Corporation/Courses/Dissertation/3rd Paper/Data/Cost Structure/cost_str_MEX.xlsx"
mex <- read_excel(mex_file)

cat("  Rows:", nrow(mex), "\n")
cat("  Unique sectors:", n_distinct(mex$Sector), "\n")
cat("  Unique strategies:", n_distinct(mex$strategy_id), "\n")

# 3. Quick simulation of the merge
cat("\n\nSIMULATION:\n")

# Create long crosswalk
crosswalk_long <- crosswalk_raw %>%
  pivot_longer(
    cols = all_of(sector_cols),
    names_to = "Sector",
    values_to = "linked"
  ) %>%
  filter(linked == 1) %>%
  select(-linked, -n_sectors) %>%
  rename(Product = all_of(product_col))

cat("  Crosswalk long format:", nrow(crosswalk_long), "rows\n")
cat("    (should be 120 + extra rows for multi-sector products)\n")

# Count products per sector
prod_per_sector <- crosswalk_long %>%
  group_by(Sector) %>%
  summarise(n = n())

cat("  Products per sector (first 5):\n")
print(head(prod_per_sector))

# Merge with MEX data
merged <- mex %>%
  inner_join(crosswalk_long, by = "Sector")

cat("\n  After merge with MEX:", nrow(merged), "rows\n")
cat("  Expected: 67 strategies ×", nrow(crosswalk_long), "product-sector pairs\n")
cat("  Calculated:", 67 * nrow(crosswalk_long), "\n")

# Aggregate by Product
aggregated <- merged %>%
  group_by(strategy_id, Product) %>%
  summarise(n_rows = n(), .groups = "drop")

cat("\n  After aggregation by (strategy_id, Product):", nrow(aggregated), "rows\n")
cat("  Expected: 67 strategies × 120 products =", 67 * 120, "\n")
cat("  Difference:", nrow(aggregated) - (67 * 120), "\n")

# Check if any products have different counts
weird_products <- aggregated %>%
  count(Product) %>%
  filter(n != 67)

if(nrow(weird_products) > 0) {
  cat("\n  ⚠ Products appearing", colnames(weird_products)[2], "!= 67 times:\n")
  print(weird_products)
} else {
  cat("\n  ✓ All products appear exactly 67 times (once per strategy)\n")
}

# Count unique products
cat("\n  Unique products in final data:", n_distinct(aggregated$Product), "\n")

# Expected final rows for all countries
n_countries <- 7
n_strategies <- 67
n_products <- n_distinct(aggregated$Product)
expected_total <- n_countries * n_strategies * n_products

cat("\n\nFINAL CALCULATION:\n")
cat("  Countries:", n_countries, "\n")
cat("  Strategies:", n_strategies, "\n")
cat("  Products:", n_products, "\n")
cat("  Expected total rows:", expected_total, "\n")
cat("  User reported:", 56749, "\n")
cat("  Difference:", 56749 - expected_total, "\n")
