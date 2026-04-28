# ------- Employment plots ----------------------------------------------

# INPUTS FROM PREVIOUS:
#   results
#   scenariofile

# LOADED INPUTS:
#   GLORIAtoNACE
#   Countries_USDAtoGLORIA

# OUTPUTS:
#   Plots per taxed country in pdf


##########################################################################
####    1. Load packages
##########################################################################

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

##########################################################################
####    2. Set inputs
##########################################################################
args = commandArgs(trailingOnly=TRUE)

# if running from RStudio you need to set by hand!
MINDSET_FOLDER = 'C:/Users/wb614213/Model/MINDSET_module'
# activated if first argument is set
MINDSET_FOLDER = if(length(args) > 0) getwd() else MINDSET_FOLDER

# if want to print only select countries, specify them here

#>> UPDATE NAME HERE
SELECT_COUNTRY = 'GEO'
SELECT_COUNTRY = if(length(args)>1) str_split(args[2],",")[[1]] else SELECT_COUNTRY
SELECT_COUNTRY = if(SELECT_COUNTRY[1]=='ALL') c() else SELECT_COUNTRY
F
# if you want to specify which scenarios to print specify here as regex pattern
PATTERN = "Results_GEO*.*xlsx"
# PATTERN = "Results_LAO_Adaptation_NW*.*xlsx"
PATTERN = if(length(args)>2) args[3] else PATTERN

rename_variables_ <- c(
  'tech_eff' = 'Energy substitution',
  'trade_eff' = 'Trade substitution',
  'hh_price' = 'HH price eff.',
  'hh_inc' = 'HH income eff.',
  'gov_recyc' = 'Govt. spending',
  'inv_induced' = 'Induced inv.',
  'inv_recyc' = 'Public inv.',
  'inv_exog' = 'Ext. inv.',
  'supply_constraint' = 'Supply constraint',
  'hh_exog_fd' = 'Exog. HH demand',
  'fcf_exog_fd' = 'Exog. FCF demand',
  'gov_exog_fd' = 'Exog. Govt. demand'
)

isic_names <- c("A. Agriculture, forestry\n and fishing", "B. Mining and\n quarrying", "C. Manufacturing",
        "D. Electricity\n and gas", "E. Water supply and\n waste management", "F. Construction",
        "G. Wholesale and\n retail trade ", "H. Transportation and\n storage",
        "I. Accommodation and\n food service activities", "J. Information and\n communication",
        "K. Financial and\n insurance activities", "L. Real estate\n activities",
        "M. Professional, scientific\n and technical activities",
        "N. Administration and\n support service ", "O. Public administration and\n defence",
        "P. Education", "Q. Health and\n social work", "R. Arts, entertainment\n and recreation",
        "S. Other Service", "T. Activities of households\n as employers",
        "U. Activities of extra-\nterritorial organisations")


##########################################################################
####    3. Run loops
##########################################################################

files <- list.files(path=paste0(MINDSET_FOLDER,"/GLORIA_results"), pattern=PATTERN, full.names=TRUE, recursive=FALSE)
print("################# PROCESSING FILES:")
print(files)
for(f in files){

  results_loc <- f
  title = str_replace(str_c(tail(str_split(results_loc, "_")[[1]], -3), collapse=", "), ".xlsx", "")

  results_output <- read.xlsx(results_loc, sheet = "output")
  results_employment <- read.xlsx(results_loc, sheet = "employment")
  results_gdp <- read.xlsx(results_loc, sheet = "gdp")

  sector_data <- read.xlsx(here(paste0(MINDSET_FOLDER,"/GLORIA_template/modelinputdata/Sectors_USDAtoGLORIA.xlsx")))

  #Load scenario file and take taxed countries to loop
  tax_countries=results_output$Reg_ID
  tax_countries=unique(tax_countries)
  tax_countries=tax_countries[!is.na(tax_countries)]

  #Load MRIO results
  employ_data = results_employment %>% rename(
    "PROD_COMM" = "Sec_ID", "REG_imp" = "Reg_ID")
  output_data = results_output %>% rename(
    "PROD_COMM" = "Sec_ID", "REG_imp" = "Reg_ID")
  gdp_data = results_gdp %>% rename(
    "PROD_COMM" = "Sec_ID", "REG_imp" = "Reg_ID")

  tax_countries = if(length(SELECT_COUNTRY)==0) tax_countries else SELECT_COUNTRY

  for(ctr in tax_countries){
    i_country <- ctr 
    # Output the country being processed for debugging
    print(paste("Processing country:", i_country))
    
    #Load NACE
    GLORIA2NACE = read.xlsx(here(paste0(MINDSET_FOLDER,"/GLORIA_template/modelinputdata/GLORIA_ISIC.xlsx")),
                            sheet = "1-digit")
    GLORIA2NACE1=GLORIA2NACE[,c(1,3,4)]
    GLORIA2NACE1=unique(GLORIA2NACE1)
    names(GLORIA2NACE1) <- c("PROD_COMM", "NACE1", "NACE1_name")
    
    country_name<- read.xlsx(here(paste0(MINDSET_FOLDER,"/GLORIA_template/modelinputdata/Countries_USDAtoGLORIA.xlsx")))%>%
      filter(Country_Code==i_country)
    
    country_name = country_name$GLORIA_Country
    
    #Load output outcome for country i
    output_data_i <- output_data[output_data$REG_imp==i_country,]
    
    #Merge it with GTAP2NACE
    output_data_i <- (merge(output_data_i, GLORIA2NACE1, by = 'PROD_COMM')) 
      
    output_data_i <- output_data_i %>% select(-Sector, -PROD_COMM) %>% group_by(REG_imp, Region, NACE1, NACE1_name, year) %>% summarize_all(sum) %>% ungroup()
    output_data_i <- output_data_i %>% arrange(NACE1)
    
    #Putting names to Sectors
    output_data_i['NACE_name']= isic_names
        
    overall_output_change_in_per=sum(head(output_data_i$dq_total,-2))/sum(head(output_data_i$q_base,-2))*100
    output_data_i$dq_total_rel <- output_data_i$dq_total / output_data_i$q_base
    
    output_data_i <- output_data_i[complete.cases(output_data_i),]
    
    coe_output_tot=(max(output_data_i["dq_total"])-min(output_data_i["dq_total"]))*1000/(
      max(output_data_i['dq_total_rel'])-min(output_data_i['dq_total_rel']))
    
    #Load output outcome for country i
    employ_data_i <- employ_data[employ_data$REG_imp==i_country,]
    
    #Merge it with GTAP2NACE
    employ_data_i <- (merge(employ_data_i, GLORIA2NACE1, by = 'PROD_COMM')) 
    
    #Aggregate according to NACE sectors
    employ_data_i <- employ_data_i %>% select(-Sector, -PROD_COMM) %>% group_by(REG_imp, Region, NACE1, NACE1_name, year) %>% summarize_all(sum) %>% ungroup()
    employ_data_i <- employ_data_i %>% arrange(NACE1)
    
    #Putting names to Sectors
    employ_data_i['NACE_name']= isic_names
    
    overall_employ_change_in_per=sum(head(employ_data_i$dempl_total,-2))/sum(head(employ_data_i$empl_base,-2))*100
    employ_data_i$dempl_total_rel <- employ_data_i$dempl_total / employ_data_i$empl_base
    
    employ_data_i <- employ_data_i[complete.cases(employ_data_i),]
    
    coe_employ_tot=(max(employ_data_i["dempl_total"])-min(employ_data_i["dempl_total"]))*1000/(
      max(employ_data_i['dempl_total_rel'])-min(employ_data_i['dempl_total_rel']))
    
    #Load GDP outcome for country i
    gdp_data_i <- gdp_data[gdp_data$REG_imp==i_country,]
    
    #Merge it with GTAP2NACE
    gdp_data_i <- (merge(gdp_data_i, GLORIA2NACE1, by = 'PROD_COMM'))
    
    #Aggregate according to NACE sectors
    gdp_data_i <- gdp_data_i %>% select(-Sector, -PROD_COMM) %>% group_by(REG_imp, Region, NACE1, NACE1_name, year) %>% summarize_all(sum) %>% ungroup()
    gdp_data_i <- gdp_data_i %>% arrange(NACE1)
    
    #Putting names to Sectors
    gdp_data_i['NACE_name']= isic_names
    
    overall_gdp_change_in_per=sum(head(gdp_data_i$dgdp_total,-2))/sum(head(gdp_data_i$gdp_base,-2))*100
    gdp_data_i$dgdp_total_rel <- gdp_data_i$dgdp_total / gdp_data_i$gdp_base
    
    gdp_data_i <- gdp_data_i[complete.cases(gdp_data_i),]
    
    coe_gdp_tot=(max(gdp_data_i["dgdp_total"])-min(gdp_data_i["dgdp_total"]))*1000/(
      max(gdp_data_i['dgdp_total_rel'])-min(gdp_data_i['dgdp_total_rel']))
    
    match_replace_names <- function(dataframe, rename_dict){
      ren1 <- sapply(names(rename_dict), function(x) ifelse(grepl(paste0("*",x,"*"), names(dataframe)),rename_dict[x],""))
      ren1 <- apply( ren1 , 1 , paste , collapse = "" )
      names(dataframe)[ren1 != ""] <- ren1[ren1 != ""]
      return(dataframe)
    }
    
    output_data_i_effect <- match_replace_names(output_data_i, rename_variables_)
    output_data_i_effect <- output_data_i_effect %>% 
      gather(Driver, value, all_of(rename_variables_[rename_variables_ %in% names(output_data_i_effect)])) %>% 
      mutate(Driver = factor(Driver, levels=rename_variables_))
    
    employ_data_i_effect <- match_replace_names(employ_data_i, rename_variables_)
    employ_data_i_effect <- employ_data_i_effect %>% 
      gather(Driver, value, all_of(rename_variables_[rename_variables_ %in% names(employ_data_i_effect)])) %>% 
      mutate(Driver = factor(Driver, levels=rename_variables_))
    
    gdp_data_i_effect <- match_replace_names(gdp_data_i, rename_variables_)
    gdp_data_i_effect <- gdp_data_i_effect %>% 
      gather(Driver, value, all_of(rename_variables_[rename_variables_ %in% names(gdp_data_i_effect)])) %>% 
      mutate(Driver = factor(Driver, levels=rename_variables_))
    

##########################################################################
####    4. Plot and print to pdf (within loop)
##########################################################################

    pdf_name = paste0(ctr,", ",title)
    dir.create(paste0(MINDSET_FOLDER, "/GLORIA_results/pdf"), showWarnings = FALSE)
    pdf(file = here(paste0(MINDSET_FOLDER, "/GLORIA_results/pdf/", pdf_name, ".pdf")), width = 10, height = 5)
    
    par(mar=c(3,2,1.5,1))
    
    p <- ggplot() +
      geom_bar(data=output_data_i_effect, aes(
        fill = Driver, x = NACE_name, y = value/1e3),
        position="stack", stat="identity") +
      scale_fill_brewer(palette = "Set3") +
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
      scale_fill_brewer(palette = "Set3") +
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
      scale_fill_brewer(palette = "Set3") +
      geom_point(data=gdp_data_i, aes(
        x = NACE_name, y = dgdp_total_rel*coe_gdp_tot/1e6,
        shape="Relative change"), stat="identity") +
      scale_y_continuous(
        # Features of the first axis
        name = "GVA (in MM USD)",
        # Add a second axis and specify its features
        sec.axis = sec_axis(~./coe_gdp_tot*1e6*100, name= "GDP Effect (in %)"))+
      labs(title=paste0("Change in sectoral GVA for ", country_name),
          subtitle=paste0(title, ". ISIC Class. at 1-digit level"),
          caption=paste0("GDP in ", country_name, " changes by ",
                          format(round(overall_gdp_change_in_per, 2), nsmall = 2), "%"), x="")+
      theme_minimal()+ theme(legend.position="bottom",
                            axis.text.x=element_text(angle=90,hjust=1,vjust=0.5))
    plot(p)
    
    dev.off()
  }
}
