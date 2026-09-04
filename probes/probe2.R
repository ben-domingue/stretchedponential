options(irw.itemtext_disclaimer = FALSE)
suppressMessages({library(irw); library(dplyr)})
cands <- c("concretewords","klatt_2016_speed_estimation","allen_2025_delaydiscount",
"fractals_rating","artistic_preferences","zhang_2024_attractiveness",
"american_multiracial_face","amatus_cipora_2024_arithmetic","himmelstein-number_series-2025",
"roar_lexical","spalex_aguasvivas_2020","simsalRbim_Human_LargeValence_2017",
"rating_speed_2025","Forthmann-2024-cleverness_ratings","realpic_souza2021",
"number_pattern_game","himmelstein-berlin_numeracy-2025","face_memory_test")
it <- readRDS("itemtext_tables.rds")
for (tb in cands) {
  cat("\n=====", tb, " itemtext_available:", tb %in% it, "\n")
  d <- try(irw_fetch(tb), silent=TRUE)
  if (inherits(d,"try-error")) { cat("  FETCH FAIL\n"); next }
  cat("  cols:", paste(names(d), collapse=", "), "\n")
  cat("  nrow:", nrow(d), " n_items:", length(unique(d$item)), " n_id:", length(unique(d$id)), "\n")
  cat("  resp table:", paste(capture.output(print(head(sort(table(d$resp), decreasing=TRUE),12))), collapse=" | "), "\n")
  cat("  items:", paste(head(unique(as.character(d$item)),12), collapse=" ; "), "\n")
  if (tb %in% it) {
    tx <- try(irw_itemtext(tb), silent=TRUE)
    if (!inherits(tx,"try-error")) { cat("  TEXT cols:",paste(names(tx),collapse=","),"\n"); print(utils::head(as.data.frame(tx),6)) }
  }
}
