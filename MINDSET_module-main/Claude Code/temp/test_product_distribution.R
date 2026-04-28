# Test Script - Product Distribution Dataset Builder
# This runs the key logic to spot errors before full processing

library(tidyverse)
library(readxl)

# Paths
DATA_PATH <- "C:/Users/festeves/OneDrive - RAND Corporation/Courses/Dissertation/3rd Paper/Data"
COST_STRUCTURE_PATH <- file.path(DATA_PATH, "Cost Structure")
CROSSWALK_FILE <- file.path(DATA_PATH, "GLORIA-Eora26 - Crosswalk.xlsx")
COUNTRIES <- c("BGR", "BLZ", "EGY", "LBY", "MAR", "MEX", "UGA")

cat("="*80, "\n", sep = "")
cat("TESTING PRODUCT DISTRIBUTION DATASET BUILDER\n")
cat("="*80, "\n", sep = "")

# ==============================================================================
# TEST 1: Load Crosswalk
# ==============================================================================
cat("\nTEST 1: Loading Crosswalk\n")
cat("-"*80, "\n", sep = "")

tryCatch({
  crosswalk_wide <- read_excel(CROSSWALK_FILE, sheet = "Eora26 - GLORIA")
  cat("SUCCESS: Loaded crosswalk\n")
  cat("  Dimensions:", nrow(crosswalk_wide), "rows ×", ncol(crosswalk_wide), "columns\n")
  cat("  Column names:", paste(names(crosswalk_wide)[1:5], collapse = ", "), "...\n")

  # Identify sector columns
  product_col <- "Products"
  sector_cols <- setdiff(names(crosswalk_wide), c(product_col, "Codes", "Lfd_Nr"))
  cat("  Sector columns identified:", length(sector_cols), "\n")
  cat("  Sectors:", paste(head(sector_cols, 5), collapse = ", "), "...\n")

}, error = function(e) {
  cat("ERROR loading crosswalk:", e$message, "\n")
  stop()
})

# ==============================================================================
# TEST 2: Transform Crosswalk to Long
# ==============================================================================
cat("\nTEST 2: Transform Crosswalk to Long Format\n")
cat("-"*80, "\n", sep = "")

tryCatch({
  crosswalk_long <- crosswalk_wide %>%
    select(Products, all_of(sector_cols)) %>%
    pivot_longer(
      cols = all_of(sector_cols),
      names_to = "Sector",
      values_to = "linked"
    ) %>%
    filter(linked == 1) %>%
    select(Products, Sector)

  cat("SUCCESS: Transformed to long format\n")
  cat("  Rows:", nrow(crosswalk_long), "(Product-Sector pairs)\n")
  cat("  Unique products:", n_distinct(crosswalk_long$Products), "\n")
  cat("  Unique sectors:", n_distinct(crosswalk_long$Sector), "\n")

  cat("\nSample Product-Sector links:\n")
  print(head(crosswalk_long, 10))

  # Count products per sector
  products_per_sector <- crosswalk_long %>%
    group_by(Sector) %>%
    summarize(n_products = n(), .groups = "drop")

  cat("\nProducts per sector:\n")
  print(products_per_sector)

  # Add to crosswalk
  crosswalk_long <- crosswalk_long %>%
    left_join(products_per_sector, by = "Sector")

}, error = function(e) {
  cat("ERROR transforming crosswalk:", e$message, "\n")
  stop()
})

# ==============================================================================
# TEST 3: Load Distribution Files (Test with 1 country first)
# ==============================================================================
cat("\n", "="*80, "\n", sep = "")
cat("TEST 3: Loading Distribution Files\n")
cat("-"*80, "\n", sep = "")

# Function to load one country
load_country_distribution <- function(country) {
  file_path <- file.path(COST_STRUCTURE_PATH, paste0("cost_str_", country, ".xlsx"))

  if (!file.exists(file_path)) {
    cat("  WARNING: File not found:", file_path, "\n")
    return(NULL)
  }

  cat("  Loading:", basename(file_path), "\n")

  df <- read_excel(file_path) %>%
    mutate(Country = country) %>%
    select(Country, everything())

  return(df)
}

# Test with first country
test_country <- COUNTRIES[1]
cat("Testing with:", test_country, "\n")

tryCatch({
  test_dist <- load_country_distribution(test_country)

  if (!is.null(test_dist)) {
    cat("SUCCESS: Loaded distribution file\n")
    cat("  Dimensions:", nrow(test_dist), "rows ×", ncol(test_dist), "columns\n")
    cat("  Columns:", paste(names(test_dist), collapse = ", "), "\n")

    cat("\nFirst 10 rows:\n")
    print(head(test_dist, 10))

    # Check required columns
    required_cols <- c("Sector", "strategy_id", "value")
    missing <- setdiff(required_cols, names(test_dist))

    if (length(missing) > 0) {
      cat("\nERROR: Missing required columns:", paste(missing, collapse = ", "), "\n")
      stop()
    } else {
      cat("\nSUCCESS: All required columns present\n")
    }

    # Check unique values
    cat("\n  Unique strategies:", n_distinct(test_dist$strategy_id), "\n")
    cat("  Unique sectors:", n_distinct(test_dist$Sector), "\n")
    cat("  Value range:", min(test_dist$value), "to", max(test_dist$value), "\n")

    # Check sums
    sum_check <- test_dist %>%
      group_by(strategy_id) %>%
      summarize(total = sum(value), .groups = "drop")

    cat("\n  Sum of values per strategy:\n")
    print(summary(sum_check$total))

    if (any(abs(sum_check$total - 1.0) > 1e-6)) {
      cat("\n  WARNING: Some strategies don't sum to 1.0\n")
      bad <- sum_check %>% filter(abs(total - 1.0) > 1e-6)
      print(head(bad))
    }
  }

}, error = function(e) {
  cat("ERROR loading distribution:", e$message, "\n")
  stop()
})

# ==============================================================================
# TEST 4: Check Sector Name Matching
# ==============================================================================
cat("\n", "="*80, "\n", sep = "")
cat("TEST 4: Check Sector Name Matching\n")
cat("-"*80, "\n", sep = "")

tryCatch({
  sectors_crosswalk <- unique(crosswalk_long$Sector)
  sectors_distribution <- unique(test_dist$Sector)

  cat("Sectors in crosswalk:", length(sectors_crosswalk), "\n")
  cat("Sectors in distribution:", length(sectors_distribution), "\n")

  in_crosswalk_not_dist <- setdiff(sectors_crosswalk, sectors_distribution)
  in_dist_not_crosswalk <- setdiff(sectors_distribution, sectors_crosswalk)

  if (length(in_crosswalk_not_dist) > 0) {
    cat("\nWARNING: Sectors in crosswalk but NOT in distribution:\n")
    print(in_crosswalk_not_dist)
  }

  if (length(in_dist_not_crosswalk) > 0) {
    cat("\nWARNING: Sectors in distribution but NOT in crosswalk:\n")
    print(in_dist_not_crosswalk)
  }

  if (length(in_crosswalk_not_dist) == 0 && length(in_dist_not_crosswalk) == 0) {
    cat("\nSUCCESS: All sector names match perfectly!\n")
  }

}, error = function(e) {
  cat("ERROR checking sector names:", e$message, "\n")
})

# ==============================================================================
# TEST 5: Test Merge and Allocation (Small Sample)
# ==============================================================================
cat("\n", "="*80, "\n", sep = "")
cat("TEST 5: Test Merge and Allocation\n")
cat("-"*80, "\n", sep = "")

tryCatch({
  # Test with first strategy only
  test_strategy <- test_dist$strategy_id[1]
  cat("Testing with strategy:", test_strategy, "\n")

  test_subset <- test_dist %>%
    filter(strategy_id == test_strategy)

  # Merge with crosswalk
  test_merge <- test_subset %>%
    left_join(
      crosswalk_long,
      by = c("Sector" = "Sector"),
      relationship = "many-to-many"
    ) %>%
    filter(!is.na(Products)) %>%
    mutate(
      value_sector = value,
      value_product = value_sector / n_products
    )

  cat("SUCCESS: Merged and allocated\n")
  cat("  Merged rows:", nrow(test_merge), "\n")
  cat("  Unique products:", n_distinct(test_merge$Products), "\n")

  cat("\nSample allocated values:\n")
  print(head(test_merge %>% select(Country, strategy_id, Products, Sector, n_products, value_product), 15))

  # Check sum
  total_value_product <- sum(test_merge$value_product)
  cat("\nTotal Value_Product for this strategy:", total_value_product, "\n")
  cat("Should be 1.0. Difference:", abs(total_value_product - 1.0), "\n")

  if (abs(total_value_product - 1.0) < 1e-6) {
    cat("SUCCESS: Values sum to 1.0!\n")
  } else {
    cat("WARNING: Values do NOT sum to 1.0\n")
  }

}, error = function(e) {
  cat("ERROR during merge/allocation:", e$message, "\n")
  traceback()
})

# ==============================================================================
# TEST 6: Check Multi-Sector Products
# ==============================================================================
cat("\n", "="*80, "\n", sep = "")
cat("TEST 6: Check Multi-Sector Products\n")
cat("-"*80, "\n", sep = "")

tryCatch({
  # Check for products appearing multiple times
  multi_check <- test_merge %>%
    group_by(Products) %>%
    summarize(
      n_sectors = n(),
      sectors = paste(Sector, collapse = " + "),
      total_value = sum(value_product),
      .groups = "drop"
    ) %>%
    filter(n_sectors > 1)

  if (nrow(multi_check) > 0) {
    cat("Found", nrow(multi_check), "products linked to multiple sectors\n")
    print(multi_check)

    cat("\nAfter summing, these products will have higher values\n")
  } else {
    cat("No multi-sector products found in this test\n")
  }

}, error = function(e) {
  cat("ERROR checking multi-sector:", e$message, "\n")
})

# ==============================================================================
# TEST 7: Load All Countries (Quick Check)
# ==============================================================================
cat("\n", "="*80, "\n", sep = "")
cat("TEST 7: Check All Country Files\n")
cat("-"*80, "\n", sep = "")

for (country in COUNTRIES) {
  file_path <- file.path(COST_STRUCTURE_PATH, paste0("cost_str_", country, ".xlsx"))

  if (file.exists(file_path)) {
    cat("  ", country, ": FOUND\n")
  } else {
    cat("  ", country, ": NOT FOUND (", file_path, ")\n")
  }
}

# ==============================================================================
# SUMMARY
# ==============================================================================
cat("\n", "="*80, "\n", sep = "")
cat("TEST SUMMARY\n")
cat("="*80, "\n", sep = "")

cat("\nAll critical tests completed.\n")
cat("\nNext steps:\n")
cat("  1. Review any warnings above\n")
cat("  2. If all looks good, run the full Rmd file\n")
cat("  3. Check final output for validation\n")
cat("\n", "="*80, "\n", sep = "")
