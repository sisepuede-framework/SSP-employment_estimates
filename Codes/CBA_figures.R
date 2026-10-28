# ==============================================================================
# CBA_figures.R -- the five CBA / employment figures, in ONE place.
#
# Sourced by  Codes/Sisepuede - CBA demand vectors for GLORIA (pipeline).Rmd  (S6b)
# right after that chunk writes its CSV exports, and ALSO runnable on its own:
#
#     Rscript "Codes/CBA_figures.R"
#
# Either way it reads only the three exported CSVs in Data/CBA/ (plus the two
# crosswalks for labels) and writes .png + .pdf into Data/CBA/figures/. So the
# figures can be re-cut without re-running the whole pipeline, and there is only
# one definition of each chart.
#
# S27 (Fernando's chart brief), three changes to every figure:
#   1. X AXIS = PERIODS t_1 .. t_33 (real subscripts, via plotmath), not calendar
#      years. The paper reports "33 periods" and deliberately does NOT stamp
#      calendar years onto the CBA ledger (the period->year mapping lives in a
#      different file and is unstated in the write-up), so the axis says what the
#      model says. Period 1 = the first modelled period in the exports.
#   2. SAVINGS ALWAYS BELOW ZERO. The old charts coloured by the line's LABEL
#      (cost line vs savings line), and the CBA delta can flip sign within a
#      line -- a "cost" line can come out negative and a "savings" line positive
#      in a given period (see the S4 checkpoint: 684 negative investment rows,
#      900 positive displaced rows). That put red bars above zero for AGRC, ENTC
#      and FGTV. Now the split is by the SIGN OF THE MONEY: positive dollars are
#      "Added spending" (blue, above zero), negative dollars are "Avoided
#      spending" (red, below zero). Nothing is dropped or re-signed -- the same
#      dollars, bucketed by direction instead of by label, so the sum is
#      unchanged and red can never sit above the axis.
#   3. PLAIN-LANGUAGE TITLES AND LABELS. SISEPUEDE sector codes (AGRC, ENTC,
#      FGTV, SCOE, ...) and cb line codes (SAVINGS:DISPLACED_OIL_GAS:TRNS_LDV)
#      are replaced by names an outside reader can read. Label sources are named
#      at each map below.
#
# Palette: the dataviz reference palette, unchanged -- blue #2a78d6 / red #e34948
# is its documented diverging pair, and the chrome (ink #0b0b0b, muted #898781,
# grid #e1e0d9, surface #fcfcfb) are its chart-chrome roles. Not re-derived here;
# the node validator is not installed on this machine, and these are the
# pre-validated values.
# ==============================================================================

suppressPackageStartupMessages({
  library(dplyr); library(tidyr); library(ggplot2); library(readr); library(grid)
})

# ---- repo root -----------------------------------------------------------------
# Same contract as the Rmd: no hard-coded absolute path. Reuse REPO if the Rmd
# already set it, else walk up from this script's own folder (Rscript) or the wd.
if (!exists("REPO") || !is.character(REPO) || !dir.exists(file.path(REPO, "Data"))) {
  .find_root <- function(start) {
    is_root <- function(p) dir.exists(file.path(p, "Data")) &&
                           dir.exists(file.path(p, "MINDSET_module-main"))
    cur <- normalizePath(start, winslash = "/", mustWork = FALSE)
    for (i in 1:6) {
      if (is_root(cur)) return(cur)
      parent <- dirname(cur); if (identical(parent, cur)) break; cur <- parent
    }
    NA_character_
  }
  .a <- commandArgs(trailingOnly = FALSE)
  .f <- sub("^--file=", "", .a[grepl("^--file=", .a)])
  .start <- if (length(.f)) dirname(normalizePath(.f[1], winslash = "/", mustWork = FALSE)) else getwd()
  REPO <- .find_root(.start)
  if (is.na(REPO)) REPO <- .find_root(getwd())
  if (is.na(REPO)) stop("CBA_figures.R: could not locate the SSP-employment_estimates repo root.")
}
CBA_DIR <- file.path(REPO, "Data", "CBA")
FIG_DIR <- file.path(CBA_DIR, "figures")
if (!dir.exists(FIG_DIR)) dir.create(FIG_DIR, recursive = TRUE)

# ==============================================================================
# 1. Shared styling
# ==============================================================================
INK   <- "#0b0b0b"; MUTED <- "#898781"; GRID <- "#e1e0d9"; SURF <- "#fcfcfb"
ADD_BLUE <- "#2a78d6"   # money spent   (+)  -- diverging pole 1
AVD_RED  <- "#e34948"   # money avoided (-)  -- diverging pole 2
STREAM_ADD <- "Added spending"
STREAM_AVD <- "Avoided spending"
stream_cols <- setNames(c(ADD_BLUE, AVD_RED), c(STREAM_ADD, STREAM_AVD))

# 20 medium-saturation, well-separated hues for the ISIC stacks. NOT the reference
# categorical theme: that theme caps at 8 slots, and these two charts are
# compositions that must sum to their total, so every industry has to stay on
# screen. Kept as-is from S25 (no black, no near-white -> readable on the surface).
# NOTE / open item for Fernando: 19 stacked hues is past what any palette can keep
# reliably distinguishable. The principled fix is "top N industries + Other", or
# small multiples -- but that hides industries, so it is an editorial call, not
# mine. Flagged, not changed.
sector_pal <- c("#3283FE","#FEAF16","#B00068","#16A085","#90AD1C","#2ED9FF",
                "#C39BD3","#AA0DFE","#F8766D","#325A9B","#C4451C","#1C8356",
                "#B10DA1","#5A5AAD","#E67E22","#1CBE4F","#FA0087","#8E7B4C",
                "#00868B","#D62976")

theme_pub <- theme_minimal(base_size = 12) +
  theme(panel.background  = element_rect(fill = SURF, colour = NA),
        plot.background   = element_rect(fill = SURF, colour = NA),
        legend.background = element_rect(fill = SURF, colour = NA),
        strip.background  = element_blank(),
        panel.grid.minor  = element_blank(),
        panel.grid.major  = element_line(colour = GRID, linewidth = 0.3),
        strip.text    = element_text(face = "bold", colour = INK, size = 10),
        axis.text     = element_text(colour = INK),
        axis.title    = element_text(colour = MUTED),
        plot.title    = element_text(face = "bold", colour = INK, size = 15),
        plot.subtitle = element_text(colour = MUTED, size = 9.5, lineheight = 1.15),
        plot.caption  = element_text(colour = MUTED, size = 8, hjust = 0),
        legend.text   = element_text(size = 8.5, colour = INK),
        legend.key.size = unit(0.9, "lines"),
        legend.title  = element_blank(),
        plot.margin   = margin(12, 16, 10, 12))

# ---- the period axis (brief item 1) -------------------------------------------
# The exports carry `year`; the charts carry the PERIOD INDEX. PERIOD1_YEAR is the
# calendar year the exports assign to period 1 -- used only to convert, never
# printed, so no year claim reaches the figure.
PERIOD1_YEAR <- 2018L
as_period <- function(year) as.integer(year) - PERIOD1_YEAR + 1L

# plotmath labels: "t[7]" renders as t with a subscript 7 -- a real subscript, no
# literal underscore. Vectorised: parse() returns one expression per break.
t_labels <- function(p) parse(text = ifelse(is.na(p), "NA", paste0("t[", p, "]")))
period_scale <- function(periods, step = 2L)
  scale_x_continuous(breaks = seq(min(periods), max(periods), by = step),
                     labels = t_labels, expand = expansion(mult = 0.012))
X_PERIOD <- "Period"

# adaptive $ formatter: $3.5K / $250M / $2.5B off one scale, so free-scaled panels
# spanning thousands to billions all read sensibly (the old fixed "US$ billion"
# axis printed 0.0000035 for direct air capture).
usd <- scales::label_currency(prefix = "$", scale_cut = scales::cut_short_scale(),
                              accuracy = 0.1)

# ==============================================================================
# 2. Plain-language label maps (brief item 3)
# ==============================================================================
# (a) SISEPUEDE subsector code -> plain name. Codes are the model's; the canonical
# long names come from ssp_morocco's driver_variables_taxonomy (subsector column);
# the wording here is those names made readable for an outside audience.
sector_name <- c(
  AGRC = "Crop agriculture",
  CCSQ = "Carbon capture and storage",
  ENTC = "Electricity generation",
  FGTV = "Oil and gas: leaks and flaring",
  INEN = "Industrial energy use",
  IPPU = "Industrial processes",
  LNDU = "Land use and forestry",
  LSMM = "Livestock manure management",
  LVST = "Livestock",
  SCOE = "Buildings and other stationary energy",
  TRNS = "Transport",
  WASO = "Solid waste")

# (b) cb line / transformation code -> plain name. Derived from the CBA line each
# strategy_id owns in Data/Crosswalks/CBA_to_transformation_crosswalk_claude.csv
# (`output_variable_name`, which says what the dollars ARE), cross-checked against
# strategy_semantic_crosswalk.csv's human names. Where the two disagree the CBA
# line wins: that crosswalk's fuzzy matches are wrong for TRNS:SHIFT_FUEL_RAIL
# (0.47 confidence, its name says light-duty road) and mislabel
# IPPU:DEC_PFCS as HFCs, and FGTV:DEC_LEAKS is UNMATCHED_NEW there.
measure_name <- c(
  "AGRC:DEC_CH4_RICE"                 = "Rice: methane management",
  "AGRC:INC_CONSERVATION_AGRICULTURE" = "Conservation agriculture",
  "CCSQ:INC_CAPTURE"                  = "Direct air capture",
  "FGTV:DEC_LEAKS"                    = "Oil and gas: reduce methane leaks",
  "FGTV:INC_FLARE"                    = "Oil and gas: flare instead of vent",
  "INEN:INC_EFFICIENCY_ENERGY"        = "Industry: energy efficiency",
  "INEN:SHIFT_FUEL_HEAT"              = "Industry: electrify process heat",
  "IPPU:DEC_CLINKER"                  = "Cement: reduce clinker content",
  "IPPU:DEC_N2O"                      = "Industry: abate nitrous oxide",
  "IPPU:DEC_OTHER_FCS"                = "Industry: abate other fluorinated gases",
  "IPPU:DEC_PFCS"                     = "Industry: abate perfluorocarbons",
  "LNDU:INC_SILVOPASTURE"             = "Expand silvopasture",
  "LSMM:INC_CAPTURE_BIOGAS"           = "Manure: capture biogas",
  "LSMM:INC_MANAGEMENT_CATTLE_PIGS"   = "Manure management: cattle and pigs",
  "LSMM:INC_MANAGEMENT_OTHER"         = "Manure management: other livestock",
  "LSMM:INC_MANAGEMENT_POULTRY"       = "Manure management: poultry",
  "LVST:DEC_ENTERIC_FERMENTATION"     = "Livestock: reduce enteric methane",
  "SCOE:DEC_DEMAND_HEAT"              = "Buildings: better building shell",
  "SCOE:INC_EFFICIENCY_APPLIANCE"     = "Buildings: efficient appliances",
  "SCOE:SHIFT_FUEL_HEAT"              = "Buildings: heat pumps for heating",
  "TRNS:INC_EFFICIENCY_ELECTRIC"      = "Transport: vehicle energy efficiency",
  "TRNS:SHIFT_FUEL_LIGHT_DUTY"        = "Transport: electrify road vehicles",
  "TRNS:SHIFT_FUEL_MARITIME"          = "Transport: switch maritime fuels",
  "TRNS:SHIFT_FUEL_RAIL"              = "Transport: electrify rail",
  "WASO:INC_CAPTURE_BIOGAS"           = "Landfills: capture biogas",
  # savings lines: cb:<sector>:technical_savings:... / savings_opex / gas_recovery
  "SAVINGS:DISPLACED_GRID_MIX:ENTC_OPEX"        = "Avoided grid electricity operating cost",
  "SAVINGS:DISPLACED_OIL_GAS:FGTV_GAS_RECOVERY" = "Avoided gas purchases: leak recovery",
  "SAVINGS:DISPLACED_OILGAS_COAL:INEN_HI_HEAT"  = "Avoided fuel: high-temperature industrial heat",
  "SAVINGS:DISPLACED_OIL_GAS:INEN_LO_HEAT"      = "Avoided fuel: low-temperature industrial heat",
  "SAVINGS:DISPLACED_OIL_GAS:SCOE_HEAT_PUMPS"   = "Avoided fuel: building heating",
  "SAVINGS:DISPLACED_OIL_GAS:TRNS_HDV"          = "Avoided fuel: heavy-duty vehicles",
  "SAVINGS:DISPLACED_OIL_GAS:TRNS_LDV"          = "Avoided fuel: light-duty vehicles",
  "SAVINGS:DISPLACED_OIL_GAS:TRNS_RAIL"         = "Avoided fuel: rail")

# (c) ISIC section long name -> short legend label (unchanged from S25).
sector_abbr <- c(
  "Agriculture, forestry and fishing" = "Agriculture & fishing",
  "Mining and quarrying" = "Mining",
  "Manufacturing" = "Manufacturing",
  "Electricity, gas, steam and air conditioning supply" = "Electricity & gas",
  "Water supply; sewerage, waste management and remediation activities" = "Water & waste",
  "Construction" = "Construction",
  "Wholesale and retail trade; repair of motor vehicles" = "Trade & repair",
  "Transportation and storage" = "Transport & storage",
  "Accommodation and food service activities" = "Accommodation & food",
  "Information and communication" = "Info & communication",
  "Financial and insurance activities" = "Finance & insurance",
  "Real estate activities" = "Real estate",
  "Professional, scientific and technical activities" = "Professional & technical",
  "Administrative and support services" = "Admin. & support",
  "Public administration and defence; compulsory social security" = "Public administration",
  "Education" = "Education",
  "Human health and social work activities" = "Health & social work",
  "Arts, entertainment and recreation" = "Arts & recreation",
  "Other service activities" = "Other services")

# look-ups that fall back to the raw code and SAY SO, so a new code shows up as an
# obvious "[CODE]" on the figure instead of silently passing as a plain name.
.lookup <- function(x, map) ifelse(x %in% names(map), unname(map[x]), paste0("[", x, "]"))
sector_label  <- function(x) .lookup(x, sector_name)
measure_label <- function(x) .lookup(x, measure_name)
abbr_of       <- function(x) ifelse(x %in% names(sector_abbr), unname(sector_abbr[x]), x)

# SISEPUEDE subsector behind a cb line: cost lines are "SECTOR:...", savings lines
# are "SAVINGS:..:SECTOR_..".
sector_of <- function(code) ifelse(
  grepl("^SAVINGS:", code), sub("_.*$", "", sub("^.*:", "", code)), sub(":.*$", "", code))

# split signed dollars into the two directions (brief item 2). Returns one row per
# (grouping, direction): "Added spending" always > 0, "Avoided spending" always < 0.
split_by_direction <- function(df, value, ...) {
  df %>%
    filter({{ value }} != 0) %>%
    mutate(stream = ifelse({{ value }} > 0, STREAM_ADD, STREAM_AVD)) %>%
    group_by(..., stream) %>%
    summarise(amt = sum({{ value }}), .groups = "drop") %>%
    mutate(stream = factor(stream, levels = c(STREAM_ADD, STREAM_AVD)))
}

save_fig <- function(p, name, width, height) {
  ggsave(file.path(FIG_DIR, paste0(name, ".png")), p,
         width = width, height = height, dpi = 200, bg = SURF)
  ggsave(file.path(FIG_DIR, paste0(name, ".pdf")), p, width = width, height = height, bg = SURF)
  cat(sprintf("[fig] %s.png + .pdf\n", name))
}

# ==============================================================================
# 3. Inputs
# ==============================================================================
.need <- function(p) { if (!file.exists(p)) stop("CBA_figures.R: missing input ", p); p }
cost_by_txn_year <- readr::read_csv(.need(file.path(CBA_DIR, "cost_by_transformation_year.csv")),
                                    show_col_types = FALSE)
inv_by_sector    <- readr::read_csv(.need(file.path(CBA_DIR, "investment_by_sector_year.csv")),
                                    show_col_types = FALSE)
jobs_by_sector   <- readr::read_csv(.need(file.path(CBA_DIR, "jobs_by_sector_year.csv")),
                                    show_col_types = FALSE)

# period-1 assertion: if the exports ever start somewhere else, the t_1 label would
# quietly mean a different period. Fail loudly instead.
for (nm in c("cost_by_txn_year", "inv_by_sector", "jobs_by_sector")) {
  y0 <- min(get(nm)$year)
  if (y0 != PERIOD1_YEAR)
    stop(sprintf("CBA_figures.R: %s starts at %d but PERIOD1_YEAR = %d -> t_1 would mislabel.",
                 nm, y0, PERIOD1_YEAR))
}
N_PERIODS <- length(unique(cost_by_txn_year$year))
cat(sprintf("[fig] %d periods (t_1 .. t_%d).\n", N_PERIODS, N_PERIODS))

# ==============================================================================
# 4. FIGURE 1 -- added vs avoided spending by mitigation sector, per period
# ==============================================================================
# Split by direction BEFORE collapsing to the sector, at the (strategy_id, period,
# bucket) granularity of the exported table -- so the chart and
# cost_by_transformation_year.csv reconcile line for line.
ts_df <- cost_by_txn_year %>%
  mutate(sector = sector_of(strategy_code), period = as_period(year)) %>%
  pivot_longer(c(gross_cost, gross_savings), names_to = "bucket", values_to = "dollars") %>%
  split_by_direction(dollars, sector, period)

# facet order: most money moved first, so the sectors that matter lead. (Panels are
# free-scaled, so the old alphabetical order carried no information at all.)
sector_rank <- ts_df %>% group_by(sector) %>%
  summarise(m = sum(abs(amt)), .groups = "drop") %>% arrange(desc(m))
ts_df <- ts_df %>%
  mutate(panel = factor(sector_label(sector), levels = sector_label(sector_rank$sector)))

p_ts <- ggplot(ts_df, aes(period, amt, fill = stream)) +
  geom_col(width = 0.85) +
  geom_hline(yintercept = 0, colour = MUTED, linewidth = 0.35) +
  # label_wrap_gen so a long sector name (Buildings and other stationary energy)
  # wraps instead of being clipped by the panel width.
  facet_wrap(~ panel, ncol = 4, scales = "free_y",
             labeller = labeller(panel = label_wrap_gen(width = 26))) +
  period_scale(ts_df$period, step = 4L) +
  scale_y_continuous(labels = usd, n.breaks = 7) +
  scale_fill_manual(values = stream_cols, name = NULL, drop = FALSE) +
  labs(title = "Where the portfolio adds spending, and where it avoids it",
       subtitle = paste0("Morocco, by mitigation sector over ", N_PERIODS,
                         " periods. Above zero = spending the portfolio adds; below zero = spending it avoids.\n",
                         "Panels are ordered by total money moved and each has its own vertical scale."),
       x = X_PERIOD, y = "US$ per period") +
  theme_pub + theme(legend.position = "top",
                    legend.justification = "left",
                    axis.text.y = element_text(size = 8))
save_fig(p_ts, "cost_by_sector_time", width = 12, height = 8.5)

# ==============================================================================
# 5. FIGURE 2 -- investment demand by ISIC industry, per period
# ==============================================================================
inv_df <- inv_by_sector %>%
  mutate(industry = abbr_of(sector), period = as_period(year))
inv_pal <- setNames(sector_pal[seq_len(dplyr::n_distinct(inv_df$industry))],
                    sort(unique(inv_df$industry)))
p_inv <- ggplot(inv_df, aes(period, investment / 1e9, fill = industry)) +
  geom_col(width = 0.85, colour = SURF, linewidth = 0.08) +
  geom_hline(yintercept = 0, colour = MUTED, linewidth = 0.35) +
  period_scale(inv_df$period, step = 2L) +
  scale_y_continuous(labels = scales::comma, n.breaks = 8) +
  scale_fill_manual(values = inv_pal, name = NULL) +
  guides(fill = guide_legend(ncol = 1)) +
  labs(title = "Which industries receive the spending",
       subtitle = paste0("Morocco, net investment demand by industry over ", N_PERIODS,
                         " periods. Industries are ISIC sections: where the money lands in the economy,\n",
                         "not the sector being decarbonised."),
       x = X_PERIOD, y = "US$ billion per period") +
  theme_pub + theme(legend.position = "right")
save_fig(p_inv, "investment_by_sector_time", width = 12.5, height = 7)

# ==============================================================================
# 6. FIGURE 3 -- net domestic jobs by ISIC industry, per period
# ==============================================================================
job_df <- jobs_by_sector %>%
  mutate(industry = abbr_of(sector), period = as_period(year))
job_pal <- setNames(sector_pal[seq_len(dplyr::n_distinct(job_df$industry))],
                    sort(unique(job_df$industry)))
p_jobs <- ggplot(job_df, aes(period, jobs, fill = industry)) +
  geom_col(width = 0.85, colour = SURF, linewidth = 0.08) +
  geom_hline(yintercept = 0, colour = MUTED, linewidth = 0.35) +
  period_scale(job_df$period, step = 2L) +
  scale_y_continuous(labels = scales::comma, n.breaks = 8) +
  scale_fill_manual(values = job_pal, name = NULL) +
  guides(fill = guide_legend(ncol = 1)) +
  labs(title = "Which industries gain and lose jobs",
       subtitle = paste0("Morocco, net domestic jobs supported in each of ", N_PERIODS,
                         " periods: jobs from added spending minus jobs displaced by avoided spending.\n",
                         "Bars below zero are net losses. Industries are ISIC sections."),
       x = X_PERIOD, y = "Net domestic jobs") +
  # Larger type than the shared theme (Fernando, S27): this figure carries a 19-entry
  # legend and is the one most often read at slide size, so ticks/titles/keys go up.
  theme_pub +
  theme(legend.position = "right",
        axis.text       = element_text(size = 11.5, colour = INK),
        axis.title      = element_text(size = 12.5, colour = MUTED),
        legend.text     = element_text(size = 10.5, colour = INK),
        legend.key.size = unit(1.05, "lines"))
save_fig(p_jobs, "jobs_by_sector_time", width = 12.5, height = 7)

# ==============================================================================
# 7. FIGURES 4 & 5 -- per-measure totals over the whole horizon
# ==============================================================================
# Cumulative over all periods, one row per transformation. Wide dynamic range
# (tens of billions down to tens of thousands) -> facet by magnitude TIER so the
# small measures stay legible.
txn_totals <- cost_by_txn_year %>%
  group_by(strategy_id, strategy_code) %>%
  summarise(gross_cost = sum(gross_cost), gross_savings = sum(gross_savings),
            net = sum(net), .groups = "drop") %>%
  mutate(measure = measure_label(strategy_code))

tier_of <- function(v) {
  a <- abs(v)
  factor(ifelse(a >= 1e9, "$1B and above", ifelse(a >= 1e8, "$100M to $1B", "Under $100M")),
         levels = c("$1B and above", "$100M to $1B", "Under $100M"))
}
tier_theme <- theme_pub +
  theme(panel.grid.major.y = element_blank(),
        panel.grid.major.x = element_line(colour = GRID, linewidth = 0.3),
        strip.text = element_text(face = "bold", colour = INK, hjust = 0, size = 10),
        legend.position = "top", legend.justification = "left")

# (4) NET: one bar per measure, right of zero = net cost, left = net saving. Legend
# says "net" -- these bars are a single netted number, not the two gross arms of
# figure 5, and the two figures sit side by side in the folder.
NET_ADD <- "Net added spending"; NET_AVD <- "Net avoided spending"
net_cols <- setNames(c(ADD_BLUE, AVD_RED), c(NET_ADD, NET_AVD))
net_df <- txn_totals %>%
  mutate(tier = tier_of(net),
         lab  = reorder(measure, net),
         stream = factor(ifelse(net >= 0, NET_ADD, NET_AVD), levels = c(NET_ADD, NET_AVD)))
p_net <- ggplot(net_df, aes(x = net, y = lab, fill = stream)) +
  geom_col(width = 0.7) +
  geom_vline(xintercept = 0, colour = MUTED, linewidth = 0.4) +
  facet_wrap(~ tier, ncol = 1, scales = "free") +
  scale_fill_manual(values = net_cols, name = NULL, drop = FALSE) +
  # n.breaks: with free scales per tier, the default gave the middle tier only $0 and
  # $500M -- nothing labelled on the savings side. 6 forces a tick on both arms.
  scale_x_continuous(labels = usd, n.breaks = 6,
                     expand = expansion(mult = c(0.06, 0.10))) +
  labs(title = "Net cost of each mitigation measure",
       subtitle = paste0("Morocco, cumulative over all ", N_PERIODS,
                         " periods. Right of zero = the measure adds spending on net; left = it saves on net.\n",
                         "Job-routing measures only. Each magnitude tier has its own horizontal scale."),
       x = NULL, y = NULL) +
  tier_theme
save_fig(p_net, "cost_by_transformation_net", width = 10.5, height = 9)

# (5) GROSS: both directions for the same measure, diverging around zero -- added
# spending to the right, avoided spending to the left. (The old version plotted
# magnitudes side by side and needed a sentence to explain that colour carried the
# sign; a diverging bar says it without the sentence.)
#
# The direction split happens PER PERIOD and is then summed, not the other way
# round. That is what makes this chart say something the net chart does not: 14 of
# the 31 live measures add money in some periods and avoid it in others, and
# splitting after summing would cancel those out -- every measure would collapse to
# a single bar equal to its net, and this figure would just duplicate figure 4.
gross_df <- cost_by_txn_year %>%
  mutate(measure = measure_label(strategy_code)) %>%
  pivot_longer(c(gross_cost, gross_savings), names_to = "bucket", values_to = "dollars") %>%
  split_by_direction(dollars, strategy_code, measure)
# Measures that are exactly $0 in every period (config lines carrying no dollars at
# all) drop out of the split. Put them back as a zero-length bar so both per-measure
# figures list the same measures and "this line spends nothing" stays visible.
gross_df <- txn_totals %>%
  anti_join(gross_df, by = "strategy_code") %>%
  transmute(strategy_code, measure, stream = factor(STREAM_ADD, levels = levels(gross_df$stream)),
            amt = 0) %>%
  bind_rows(gross_df) %>%
  left_join(select(txn_totals, strategy_code, net), by = "strategy_code") %>%
  # tier on the measure's LARGEST gross arm, not on each bar: a measure whose two
  # arms straddle a tier boundary must not be split across two panels.
  group_by(strategy_code) %>% mutate(tier = tier_of(max(abs(amt)))) %>% ungroup() %>%
  mutate(lab = reorder(measure, net))
p_gross <- ggplot(gross_df, aes(x = amt, y = lab, fill = stream)) +
  geom_col(width = 0.7) +
  geom_vline(xintercept = 0, colour = MUTED, linewidth = 0.4) +
  facet_wrap(~ tier, ncol = 1, scales = "free") +
  scale_fill_manual(values = stream_cols, name = NULL, drop = FALSE) +
  scale_x_continuous(labels = usd, n.breaks = 6,
                     expand = expansion(mult = c(0.10, 0.10))) +
  labs(title = "Added and avoided spending, measure by measure",
       subtitle = paste0("Morocco, cumulative over all ", N_PERIODS,
                         " periods. Both directions shown for the same measure: right of zero = money spent,\n",
                         "left = money avoided. Job-routing measures only. Each magnitude tier has its own horizontal scale."),
       x = NULL, y = NULL) +
  tier_theme
save_fig(p_gross, "cost_by_transformation_gross", width = 10.5, height = 9.5)

cat(sprintf("[fig] all five figures written to %s\n", FIG_DIR))
