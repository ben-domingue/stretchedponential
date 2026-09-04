options(irw.itemtext_disclaimer = FALSE)
suppressMessages({library(irw); library(dplyr)})
cands <- c("fractals_rating","artistic_preferences","zhang_2024_attractiveness",
"american_multiracial_face","amatus_cipora_2024_arithmetic","himmelstein-number_series-2025",
"roar_lexical","spalex_aguasvivas_2020","simsalRbim_Human_LargeValence_2017",
"rating_speed_2025","Forthmann-2024-cleverness_ratings","realpic_souza2021",
"number_pattern_game","himmelstein-berlin_numeracy-2025")
it <- readRDS("itemtext_tables.rds")
for (tb in cands) {
  cat("\n=====", tb, " itemtext:", tb %in% it, "\n")
  d <- try(irw_fetch(tb), silent=TRUE)
  if (inherits(d,"try-error")) { cat("  FETCH FAIL\n"); next }
  cat("  cols:", paste(names(d), collapse=", "), "| nrow:", nrow(d), "n_items:", length(unique(d$item)), "n_id:", length(unique(d$id)), "\n")
  cat("  resp:", paste(names(sort(table(d$resp),decreasing=TRUE))[1:min(12,length(unique(d$resp)))], collapse=","), "\n")
  cat("  items:", paste(head(unique(as.character(d$item)),10), collapse=" ; "), "\n")
  cat("  ids:", paste(head(unique(as.character(d$id)),5), collapse=" ; "), "\n")
}
# concretewords id inspection
d <- irw_fetch("concretewords"); cat("\n### concretewords ids:\n"); print(head(unique(as.character(d$id)),30))
