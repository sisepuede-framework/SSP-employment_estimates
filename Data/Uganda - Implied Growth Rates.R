
library(splines)
library(ggplot2)
library(dplyr)

implied_growth <- read.xlsx("C:/Users/festeves/OneDrive - RAND Corporation/Courses/Dissertation/3rd Paper/Data/Uganda - Agriculture and Industrial Implied Growth Rate.xlsx")

implied_growth <- melt(implied_growth, id.vars = "Implied.sector.real.growth.rates", 
                       variable.name = "Year", 
                       value.name = "Value")

implied_growth <- data.table(implied_growth)
implied_growth <- dcast(implied_growth,Year ~ Implied.sector.real.growth.rates,value.var = "Value",fun.aggregate = sum)

implied_growth$Year <- as.numeric(as.character(implied_growth$Year))

years_pred <- 2025:2040

group <- c("Agriculture, forestry and fishing","Agro_processing","Cash crops","Construction","Dairy farming","Electricity and water","Fishing","Food crops","Industry","Livestock","Mining and Quarrying","Other Agriculture","Other Manufacturing")

group_name <- gsub("[ ,]", "", group)

# for(i in 1:16){
# 
# # Spline interpolation using data frame columns
# 
#   eval(parse(text = paste0("spline_fit <- spline(implied_growth$Year,implied_growth$",group[i],",xout = years_pred, method = 'natural')")))
#  
#   #spline_fit <- spline(implied_growth$Year,implied_growth$`Agriculture, forestry & fishing`, xout = years_pred, method = "natural")
# 
#   eval(parse(text = paste0("predicted_growth_",group_name[i]," <- spline_fit$y"))) 
# 
#   eval(parse(text = paste0("results_",group_name[i]," <- data.frame(Year = years_pred,
#   GrowthRatePercent = predicted_growth_",group_name[i],")")))
#   
# }  
  
# spline_fit <- spline(x=implied_growth$Year,y=implied_growth$`Agriculture, forestry and fishing`, xout = years_pred, method = "natural")

# Create results data frame
 # results <- data.frame(
 #   Year = years_pred,
 #   GrowthRatePercent = spline_fit$y
 # )
 
 
 sector_cols <- setdiff(names(implied_growth), "Year")
 years_pred <- 2025:2040
 
 results_list <- list()
 for (sector in sector_cols) {
   spline_fit <- spline(
     x = implied_growth$Year,
     y = implied_growth[[sector]],
     xout = years_pred,
     method = "natural"
   )
   results_list[[sector]] <- data.frame(
     Year = years_pred,
     Sector = sector,
     PredictedGrowth = spline_fit$y
   )
 }
 final_results <- do.call(rbind, results_list)
 row.names(final_results) <- NULL
 
 final_results <- final_results %>% mutate("Country"="Uganda") %>% relocate(Country,.before = Year)
 
write.xlsx(final_results,"C:/Users/festeves/OneDrive - RAND Corporation/Courses/Dissertation/3rd Paper/Data/Uganda - Agriculture and Industrial Implied Growth Rate_ESTIMATED.xlsx")
 