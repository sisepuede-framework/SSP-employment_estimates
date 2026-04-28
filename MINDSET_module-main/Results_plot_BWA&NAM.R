# ------- Employment plots ----------------------------------------------

# INPUTS FROM PREVIOUS:
#   results
#   scenariofile

# LOADED INPUTS:
#   GLORIAtoNACE
#   Countries_USDAtoGLORIA

# OUTPUTS:
#   Plots per taxed country in pdf

## First specify the packages of interest
packages = c("tidyverse","openxlsx", "stringr","dplyr","here","data.table",
             "dtplyr","rstudioapi","ggplot2")

## Now load or install&load all
package.check = lapply(
  packages,
  FUN = function(x) {
    if (!require(x, character.only = TRUE)) {
      install.packages(x, dependencies = TRUE)
      library(x, character.only = TRUE)
    }
  }
)

setwd("C://Users//wb619071//OneDrive - WBG//Documents//MINDSET//MINDSET//MINDSET_module//")

files <- list.files(path="GLORIA_results//.", pattern="FullResults_.*.xlsx", full.names=TRUE, recursive=FALSE)
# files <- files[1:2]
for(f in files){
  
  # results_name = readline(prompt = "Enter results filename: ")
  # title = readline(prompt = "Enter scenario description: ")
  
  results_name = f
  title = str_replace(str_c(str_split(f, "_")[[1]][4:7], collapse=', '), ".xlsx", "")
  
  results_loc <- results_name
  results_output <- read.xlsx(results_loc, sheet = "output")
  results_employment <- read.xlsx(results_loc, sheet = "employment")
  results_gdp <- read.xlsx(results_loc, sheet = "gdp")
  
  results_output <- results_output[,2:(dim(results_output)[2])]
  results_employment <- results_employment[,2:(dim(results_employment)[2])]
  results_gdp <- results_gdp[,2:(dim(results_gdp)[2])]
  
  sector_data <- read.xlsx("GLORIA_template//modelinputdata//Sectors_USDAtoGLORIA.xlsx")
  
  colors = c("#0072CC", "#75B2DD", "#BA55D3", # c("#FFFFFF", "#696969", "#FF8C00", 
             "#F0AA98", "#32CD32", "#6B8E23",  
             "#FC9303", "#FDB515")#, "#C0C0C0", "#A65628", "#DEB887")
  
  #Load scenario file and take taxed countries to loop
  # tax_countries=results_employment$Reg_ID
  # tax_countries=unique(tax_countries)
  tax_countries <- c("NAM","BWA")
  
  #Load MRIO results
  employ_data = results_employment %>% rename(
    "PROD_COMM" = "Sec_ID", "REG_imp" = "Reg_ID")
  output_data = results_output %>% rename(
    "PROD_COMM" = "Sec_ID", "REG_imp" = "Reg_ID")
  gdp_data = results_gdp %>% rename(
    "PROD_COMM" = "Sec_ID", "REG_imp" = "Reg_ID")
  
  employ_data_2 = employ_data
  employ_data_GLORIA = employ_data
  
  output_data_2 = output_data
  output_data_GLORIA = output_data
  
  gdp_data_2 = gdp_data
  gdp_data_GLORIA = gdp_data
  
  for(i in 1:length(tax_countries)) {
    
    i_country <- tax_countries[i] 
    
    #Load NACE
    GLORIA2NACE = read.xlsx("GLORIA_template/modelinputdata/GLORIA_ISIC.xlsx",
                            sheet = "1-digit")
    GLORIA2NACE1=GLORIA2NACE[,c(1,3,4)]
    GLORIA2NACE1=unique(GLORIA2NACE1)
    names(GLORIA2NACE1) <- c("PROD_COMM", "NACE1", "NACE1_name")
    GLORIA2NACE1$weights = 1
    GLORIA2NACE1[GLORIA2NACE1$NACE1=="U", "weights"] = 0
    
    #Linear weighting to disaggregate GTAP sector to NACE 1
    GLORIA2NACE1=GLORIA2NACE1%>%
      group_by(PROD_COMM)%>%
      mutate(weights=weights/sum(weights))
    
    country_name<- read.xlsx("GLORIA_template/modelinputdata/Countries_USDAtoGLORIA.xlsx")%>%
      filter(Country_Code==i_country)
    
    country_name = country_name$GLORIA_Country
    
    #Load output outcome for country i
    output_data_i <- output_data[output_data$REG_imp==i_country,]
    
    #Merge it with GTAP2NACE
    output_data_i <- (merge(output_data_i, GLORIA2NACE1, by = 'PROD_COMM')) 
    output_data_i_weights = output_data_i[,c(5:(length(output_data_i)-3))]*output_data_i$weights
    output_data_i[,c(5:(length(output_data_i)-3))]=output_data_i_weights
    
    #Aggregate according to NACE sectors
    output_data_i <- aggregate(. ~ NACE1, data=output_data_i[,5:(length(output_data_i)-2)], sum)
    output_data_i <- output_data_i %>% arrange(NACE1)
    
    #Putting names to Sectors
    output_data_i['NACE_name']=
      c("A. Agriculture, forestry\n and fishing", "B. Mining and\n quarrying", "C. Manufacturing",
        "D. Electricity\n and gas", "E. Water supply and\n waste management", "F. Construction",
        "G. Wholesale and\n retail trade ", "H. Transportation and\n storage",
        "I. Accommodation and\n food service activities", "J. Information and\n communication",
        "K. Financial and\n insurance activities", "L. Real estate\n activities",
        "M. Professional, scientific\n and technical activities",
        "N. Administration and\n support service ", "O. Public administration and\n defence",
        "P. Education", "Q. Health and\n social work", "R. Arts, entertainment\n and recreation",
        "S. Other Service", "T. Activities of households\n as employers",
        "U. Activities of extra-\nterritorial organisations")
    
    overall_output_change_in_per=sum(output_data_i['dq_total'])/sum(output_data_i['q_base'])*100
    output_data_i$dq_total_rel <- output_data_i$dq_total / output_data_i$q_base
    
    output_data_i <- output_data_i[complete.cases(output_data_i),]
    
    coe_output_tot=(max(output_data_i["dq_total"])-min(output_data_i["dq_total"]))*1000/(
      max(output_data_i['dq_total_rel'])-min(output_data_i['dq_total_rel']))
    
    #Load output outcome for country i
    employ_data_i <- employ_data[employ_data$REG_imp==i_country,]
    
    #Merge it with GTAP2NACE
    employ_data_i <- (merge(employ_data_i, GLORIA2NACE1, by = 'PROD_COMM')) 
    employ_data_i_weights = employ_data_i[,c(5:(length(employ_data_i)-3))]*employ_data_i$weights
    employ_data_i[,c(5:(length(employ_data_i)-3))]=employ_data_i_weights
    
    #Aggregate according to NACE sectors
    employ_data_i <- aggregate(. ~ NACE1, data=employ_data_i[,5:(length(employ_data_i)-2)], sum)
    employ_data_i <- employ_data_i %>% arrange(NACE1)
    
    #Putting names to Sectors
    employ_data_i['NACE_name']=
      c("A. Agriculture, forestry\n and fishing", "B. Mining and\n quarrying", "C. Manufacturing",
        "D. Electricity\n and gas", "E. Water supply and\n waste management", "F. Construction",
        "G. Wholesale and\n retail trade ", "H. Transportation and\n storage",
        "I. Accommodation and\n food service activities", "J. Information and\n communication",
        "K. Financial and\n insurance activities", "L. Real estate\n activities",
        "M. Professional, scientific\n and technical activities",
        "N. Administration and\n support service ", "O. Public administration and\n defence",
        "P. Education", "Q. Health and\n social work", "R. Arts, entertainment\n and recreation",
        "S. Other Service", "T. Activities of households\n as employers",
        "U. Activities of extra-\nterritorial organisations")
    
    overall_employ_change_in_per=sum(employ_data_i['dempl_total'])/sum(employ_data_i['empl_base'])*100
    employ_data_i$dempl_total_rel <- employ_data_i$dempl_total / employ_data_i$empl_base
    
    employ_data_i <- employ_data_i[complete.cases(employ_data_i),]
    
    coe_employ_tot=(max(employ_data_i["dempl_total"])-min(employ_data_i["dempl_total"]))*1000/(
      max(employ_data_i['dempl_total_rel'])-min(employ_data_i['dempl_total_rel']))
    
    #Load GDP outcome for country i
    gdp_data_i <- gdp_data[gdp_data$REG_imp==i_country,]
    
    #Merge it with GTAP2NACE
    gdp_data_i <- (merge(gdp_data_i, GLORIA2NACE1, by = 'PROD_COMM')) 
    gdp_data_i_weights = gdp_data_i[,c(5:(length(gdp_data_i)-3))]*gdp_data_i$weights
    gdp_data_i[,c(5:(length(gdp_data_i)-3))]=gdp_data_i_weights
    
    #Aggregate according to NACE sectors
    gdp_data_i <- aggregate(. ~ NACE1, data=gdp_data_i[,5:(length(gdp_data_i)-2)], sum)
    gdp_data_i <- gdp_data_i %>% arrange(NACE1)
    
    #Putting names to Sectors
    gdp_data_i['NACE_name']=
      c("A. Agriculture, forestry\n and fishing", "B. Mining and\n quarrying", "C. Manufacturing",
        "D. Electricity\n and gas", "E. Water supply and\n waste management", "F. Construction",
        "G. Wholesale and\n retail trade ", "H. Transportation and\n storage",
        "I. Accommodation and\n food service activities", "J. Information and\n communication",
        "K. Financial and\n insurance activities", "L. Real estate\n activities",
        "M. Professional, scientific\n and technical activities",
        "N. Administration and\n support service ", "O. Public administration and\n defence",
        "P. Education", "Q. Health and\n social work", "R. Arts, entertainment\n and recreation",
        "S. Other Service", "T. Activities of households\n as employers",
        "U. Activities of extra-\nterritorial organisations")
    
    overall_gdp_change_in_per=sum(gdp_data_i['dgdp_total'])/sum(gdp_data_i['gdp_base'])*100
    gdp_data_i$dgdp_total_rel <- gdp_data_i$dgdp_total / gdp_data_i$gdp_base
    
    gdp_data_i <- gdp_data_i[complete.cases(gdp_data_i),]
    
    coe_gdp_tot=(max(gdp_data_i["dgdp_total"])-min(gdp_data_i["dgdp_total"]))*1000/(
      max(gdp_data_i['dgdp_total_rel'])-min(gdp_data_i['dgdp_total_rel']))
    
    output_data_i_effect <- output_data_i[c(
      "NACE_name","dq_tech_eff","dq_trade_eff","dq_hh_price","dq_hh_inc",
      "dq_gov_recyc","dq_inv_induced","dq_inv_recyc","dq_inv_exog","dq_supply_constraint","dq_hh_exog_fd")]
    names(output_data_i_effect) <- c(
      "NACE_name", "Energy substitution", "Trade substitution",
      "HH price eff.", "HH income eff.", "Govt. spending",
      "Induced invest.", "Public invest.", "External invest.","Supply shock","HH adaptation spend.")
    output_data_i_effect <- output_data_i_effect %>% 
      gather(Driver, value, "Energy substitution", "Trade substitution",
             "HH price eff.", "HH income eff.", "Govt. spending",
             "Induced invest.", "Public invest.", "External invest.","Supply shock","HH adaptation spend.")
    
    employ_data_i$dempl_hh_exog_fd = employ_data_i$dempl_total - employ_data_i$dempl_trade_eff - 
      employ_data_i$dempl_hh_price - employ_data_i$dempl_hh_inc - employ_data_i$dempl_inv_induced -
      employ_data_i$dempl_inv_exog - employ_data_i$dempl_supply_constraint
    employ_data_i_effect <- employ_data_i[c(
      "NACE_name","dempl_tech_eff","dempl_trade_eff","dempl_hh_price","dempl_hh_inc",
      "dempl_gov_recyc","dempl_inv_induced","dempl_inv_recyc","dempl_inv_exog","dempl_supply_constraint","dempl_hh_exog_fd")]
    names(employ_data_i_effect) <- c(
      "NACE_name", "Energy substitution", "Trade substitution",
      "HH price eff.", "HH income eff.", "Govt. spending",
      "Induced invest.", "Public invest.", "External invest.","Supply shock","HH adaptation spend.")
    employ_data_i_effect <- employ_data_i_effect %>% 
      gather(Driver, value, "Energy substitution", "Trade substitution",
             "HH price eff.", "HH income eff.", "Govt. spending",
             "Induced invest.", "Public invest.", "External invest.","Supply shock","HH adaptation spend.")
    
    gdp_data_i$dgdp_hh_exog_fd = gdp_data_i$dgdp_total - gdp_data_i$dgdp_trade_eff - 
      gdp_data_i$dgdp_hh_price - gdp_data_i$dgdp_hh_inc - gdp_data_i$dgdp_inv_induced -
      gdp_data_i$dgdp_inv_exog - gdp_data_i$dgdp_supply_constraint
    gdp_data_i_effect <- gdp_data_i[c(
      "NACE_name","dgdp_tech_eff","dgdp_trade_eff","dgdp_hh_price","dgdp_hh_inc",
      "dgdp_gov_recyc","dgdp_inv_induced","dgdp_inv_recyc","dgdp_inv_exog","dgdp_supply_constraint","dgdp_hh_exog_fd")]
    names(gdp_data_i_effect) <- c(
      "NACE_name", "Energy substitution", "Trade substitution",
      "HH price eff.", "HH income eff.", "Govt. spending",
      "Induced invest.", "Public invest.", "External invest.","Supply shock","HH adaptation spend.")
    gdp_data_i_effect <- gdp_data_i_effect %>% 
      gather(Driver, value, "Energy substitution", "Trade substitution",
             "HH price eff.", "HH income eff.", "Govt. spending",
             "Induced invest.", "Public invest.", "External invest.","Supply shock","HH adaptation spend.")
    
    
    # exclude govt_spending and public invest for now
    gdp_data_i_effect <- gdp_data_i_effect %>% filter(!(Driver %in% c("Govt. spending","Public invest.","Energy substitution")))
    employ_data_i_effect <- employ_data_i_effect %>% filter(!(Driver %in% c("Govt. spending","Public invest.","Energy substitution")))
    output_data_i_effect <- output_data_i_effect %>% filter(!(Driver %in% c("Govt. spending","Public invest.","Energy substitution")))
    
    # write.csv(output_data_i_effect, paste0("GLORIA_results/MNG/", "Output.csv"))
    # write.csv(gdp_data_i_effect, paste0("GLORIA_results/MNG/", "GDP.csv"))
    # write.csv(employ_data_i_effect, paste0("GLORIA_results/MNG/", "Employment.csv"))
    
    pdf_name = strtrim(results_name, nchar(results_name)-5)
    pdf(file = paste0(pdf_name,"_",i_country,"_effects.pdf"), width=10, height=5)
    par(mar=c(3,2,1.5,1))
    
    p <- ggplot() +
      geom_bar(data=output_data_i_effect, aes(
        fill = Driver, x = NACE_name, y = value/1e3),
        position="stack", stat="identity") +
      scale_fill_manual(values=rep(colors,20)) +
      geom_point(data=output_data_i, aes(
        x = NACE_name, y = dq_total_rel*coe_output_tot/1e6, shape="Relative change"),
        stat="identity") +
      scale_y_continuous(
        # Features of the first axis
        name = "Gross Output (in MM USD)",
        # Add a second axis and specify its features
        sec.axis = sec_axis(~./coe_output_tot*1e6*100, name= "Output Effect (in %)"))+
      labs(title=paste0("Change in sectoral gross output for ", country_name),
           subtitle=paste0(title, ". ISIC Class. at 1-digit level"),
           caption=paste0("Gross output in ", country_name, " changes by ",
                          format(round(overall_output_change_in_per, 2), nsmall = 2), "%"), x="")+
      theme_minimal()+ theme(legend.position="bottom",
                             axis.text.x=element_text(angle=90,hjust=1,vjust=0.5))
    plot(p)
    
    p<-ggplot()+
      geom_bar(data=employ_data_i_effect, aes(
        fill = Driver, x = NACE_name, y = value/1e3),
        position="stack", stat="identity") +
      scale_fill_manual(values=rep(colors,20)) +
      geom_point(data=employ_data_i, aes(
        x = NACE_name, y = dempl_total_rel*coe_employ_tot/1e6, shape="Relative change"), stat="identity")+
      scale_y_continuous(
        # Features of the first axis
        name =  "Employment Effect (in thous.)",
        # Add a second axis and specify its features
        sec.axis = sec_axis(~./coe_employ_tot*100*1e6, name= "Employment Effect (in %)")) +
      labs(title=paste0("Change in sectoral labor demand by skill for ", country_name),
           subtitle=paste0(title, ". ISIC Class. at 1-digit level"),
           caption=paste0("Labor demand in ", country_name, " changes by ",
                          format(round(overall_employ_change_in_per, 2), nsmall = 2), "%"), x="")+
      theme_minimal()+ theme(legend.position="bottom",
                             axis.text.x=element_text(angle=90,hjust=1,vjust=0.5))
    plot(p)
    
    p <- ggplot()+
      geom_bar(data=gdp_data_i_effect, aes(
        fill = Driver, x = NACE_name, y = value/1e3),
        position="stack", stat="identity") +
      scale_fill_manual(values=rep(colors,20)) +
      geom_point(data=gdp_data_i, aes(
        x = NACE_name, y = dgdp_total_rel*coe_gdp_tot/1e6,
        shape="Relative change"), stat="identity") +
      scale_y_continuous(
        # Features of the first axis
        name = "GDP (in MM USD)",
        # Add a second axis and specify its features
        sec.axis = sec_axis(~./coe_gdp_tot*1e6*100, name= "GDP Effect (in %)"))+
      labs(title=paste0("Change in sectoral GDP for ", country_name),
           subtitle=paste0(title, ". ISIC Class. at 1-digit level"),
           caption=paste0("GDP in ", country_name, " changes by ",
                          format(round(overall_gdp_change_in_per, 2), nsmall = 2), "%"), x="")+
      theme_minimal()+ theme(legend.position="bottom",
                             axis.text.x=element_text(angle=90,hjust=1,vjust=0.5))
    plot(p)
    
    dev.off()
    
  }
  
  
}


