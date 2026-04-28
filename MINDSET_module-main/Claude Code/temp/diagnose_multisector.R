library(readxl)
library(dplyr)
library(tidyr)

# Load crosswalk
crosswalk_file <- "C:/Users/festeves/OneDrive - RAND Corporation/Courses/Dissertation/3rd Paper/Data/GLORIA-Eora26 - Crosswalk.xlsx"
crosswalk_raw <- read_excel(crosswalk_file, sheet = "Eora26 - GLORIA")

cat("=== CROSSWALK DIAGNOSIS ===\n\n")

# Get product column and sector columns
product_col <- names(crosswalk_raw)[1]
sector_cols <- names(crosswalk_raw)[-1]

cat("Product column:", product_col, "\n")
cat("Total products:", nrow(crosswalk_raw), "\n")
cat("Sector columns:", length(sector_cols), "\n\n")

# Count sectors per product
crosswalk_raw$n_sectors <- rowSums(crosswalk_raw[, sector_cols], na.rm = TRUE)

cat("Distribution of products by number of sectors:\n")
print(table(crosswalk_raw$n_sectors))
cat("\n")

# Show multi-sector products
multi_sector <- crosswalk_raw %>%
  filter(n_sectors > 1) %>%
  select(1, all_of(sector_cols), n_sectors)

cat("Products linked to multiple sectors:\n")
for (i in 1:nrow(multi_sector)) {
  product_name <- multi_sector[[1]][i]
  n_sects <- multi_sector$n_sectors[i]

  # Find which sectors
  linked_sectors <- names(multi_sector)[2:(ncol(multi_sector)-1)][as.logical(multi_sector[i, 2:(ncol(multi_sector)-1)])]

  cat("\n", i, ". Product:", product_name, "\n")
  cat("   Linked to", n_sects, "sectors:", paste(linked_sectors, collapse = ", "), "\n")
}

# Check for duplicate product names
cat("\n\n=== CHECKING FOR DUPLICATES ===\n")
product_names <- crosswalk_raw[[1]]
cat("Unique products:", length(unique(product_names)), "\n")
cat("Total rows:", length(product_names), "\n")

if (length(unique(product_names)) != length(product_names)) {
  cat("\n⚠ WARNING: Duplicate product names found!\n")
  dupes <- product_names[duplicated(product_names)]
  cat("Duplicates:", paste(unique(dupes), collapse = ", "), "\n")
} else {
  cat("✓ No duplicate product names\n")
}

# Load the output file if it exists
output_file <- "C:/Users/festeves/OneDrive - RAND Corporation/Courses/Dissertation/3rd Paper/Mindset - WB/MINDSET_module-main/MINDSET_module-main/Claude Code/temp/sector_to_product_distribution_allcountries.csv"

if (file.exists(output_file)) {
  cat("\n\n=== OUTPUT FILE DIAGNOSIS ===\n")
  output <- read.csv(output_file)

  cat("Output dimensions:", nrow(output), "×", ncol(output), "\n")
  cat("Unique countries:", n_distinct(output$Country), "\n")
  cat("Unique strategies:", n_distinct(output$strategy_id), "\n")
  cat("Unique products:", n_distinct(output$Product), "\n\n")

  # Calculate expected rows
  expected <- n_distinct(output$Country) * n_distinct(output$strategy_id) * n_distinct(output$Product)
  cat("Expected rows:", expected, "\n")
  cat("Actual rows:", nrow(output), "\n")
  cat("Difference:", nrow(output) - expected, "\n\n")

  # Check if Sectors column has multiple values
  cat("Checking Sectors column:\n")
  multi_sector_in_output <- output %>%
    filter(grepl("\\+", Sectors)) %>%
    distinct(Product, Sectors)

  if (nrow(multi_sector_in_output) > 0) {
    cat("Products with multiple sectors in output:\n")
    print(multi_sector_in_output)
  }

  # Check for any product appearing multiple times for same country-strategy
  cat("\n\nChecking for duplicate rows (same Country-Strategy-Product):\n")
  duplicate_check <- output %>%
    group_by(Country, strategy_id, Product) %>%
    summarise(n = n(), .groups = "drop") %>%
    filter(n > 1)

  if (nrow(duplicate_check) > 0) {
    cat("⚠ Found", nrow(duplicate_check), "products with multiple rows:\n")
    print(head(duplicate_check, 20))

    # Show example
    example <- duplicate_check[1,]
    cat("\nExample duplicates:\n")
    example_rows <- output %>%
      filter(Country == example$Country,
             strategy_id == example$strategy_id,
             Product == example$Product)
    print(example_rows)
  } else {
    cat("✓ No duplicate Country-Strategy-Product combinations\n")
  }

} else {
  cat("\n\n⚠ Output file not found. Run the Rmd file first.\n")
}
