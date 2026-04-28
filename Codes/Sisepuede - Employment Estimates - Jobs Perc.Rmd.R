
install.packages("rstudioapi") # uploading packages   
install.packages("reshape")
install.packages("dplyr")
install.packages("data.table")
install.packages("tidyverse")
install.packages("ggplot2")
install.packages("openxlsx")
install.packages("readxl")
install.packages("writexl")
install.packages("tabr")
install.packages("stringr")
install.packages("summarytools")
install.packages("gridExtra")

library(rstudioapi) # uploading packages   
library(reshape)
library(dplyr)
library(data.table)
library(tidyverse)
library(ggplot2)
library(openxlsx)
library(readxl)
library(writexl)
library(tabr)
library(stringr)
library(summarytools)
library(gridExtra)

setwd("C:/Users/festeves/OneDrive - RAND Corporation/Courses/Dissertation/3rd Paper/Uganda/ssp_uganda_data/employment_estimates")

employment_estimates <- read.xlsx("Sisepuede - Employment Results - WB (SECTOR).xlsx")

employment_estimates <- employment_estimates %>% group_by(Country,Strategy_id,Strategy) %>% mutate(Total_Jobs_perc=Total_Jobs/sum(Total_Jobs,na.rm = T))

write.xlsx(employment_estimates,"C:/Users/festeves/OneDrive - RAND Corporation/Courses/Dissertation/3rd Paper/Github/ssp_uganda_data/ssp_uganda_data/employment_estimates/Sisepuede - Employment Results - WB (SECTOR).xlsx")