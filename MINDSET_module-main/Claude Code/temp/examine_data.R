library(readxl)

# Examine MEX cost structure file
cat("=== MEX COST STRUCTURE FILE ===\n\n")
mex <- read_excel("C:/Users/festeves/OneDrive - RAND Corporation/Courses/Dissertation/3rd Paper/Data/Cost Structure/cost_str_MEX.xlsx")
cat("Dimensions:", dim(mex), "\n")
cat("Column names:", names(mex), "\n\n")
cat("First 10 rows:\n")
print(head(mex, 10))
cat("\n\nUnique sectors:", length(unique(mex$Sector)), "\n")
cat("Sectors:", paste(unique(mex$Sector), collapse=", "), "\n\n")
cat("Unique strategies:", length(unique(mex$strategy_id)), "\n")
cat("Strategy range:", min(mex$strategy_id), "to", max(mex$strategy_id), "\n\n")

# Check if values sum to 1 per strategy
library(dplyr)
sum_check <- mex %>%
  group_by(strategy_id) %>%
  summarise(total = sum(value)) %>%
  pull(total)
cat("Values sum to 1 per strategy? Min:", min(sum_check), "Max:", max(sum_check), "\n\n")

# Examine crosswalk
cat("\n=== CROSSWALK FILE ===\n\n")
crosswalk <- read_excel("C:/Users/festeves/OneDrive - RAND Corporation/Courses/Dissertation/3rd Paper/Data/GLORIA-Eora26 - Crosswalk.xlsx",
                       sheet = "Eora26 - GLORIA")
cat("Dimensions:", dim(crosswalk), "\n")
cat("Column names:", names(crosswalk), "\n\n")
cat("First 5 rows:\n")
print(head(crosswalk, 5))
cat("\n\nProducts column name:", names(crosswalk)[1], "\n")

# Count how many sectors each product is linked to
sector_cols <- names(crosswalk)[-1]
crosswalk$n_sectors <- rowSums(crosswalk[, sector_cols], na.rm = TRUE)
cat("\nProducts linked to multiple sectors:\n")
print(table(crosswalk$n_sectors))
cat("\nExample multi-sector products:\n")
print(crosswalk[crosswalk$n_sectors > 1, 1:5])
