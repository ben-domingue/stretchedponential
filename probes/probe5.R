options(irw.itemtext_disclaimer = FALSE)
suppressMessages({library(irw)})
cands <- c("famous_melodies","wine_luckett2021","spelling2pronounce_edwards2023",
"Ellipse_Corssley_2024","dumas_Organisciak_2022","Forthmann-2024-creative_quality","mpsycho_lakes",
"tears","emoji_scheffler_2024","det_naismith_2023","double_marking_steele_2022","thomeczek2025_les",
"moralvignettes_rakhmankulova_2025","kalimahnorms_alzahrani_2025","socialstereotype_hughes_2025_judgement")
for (tb in cands) {
  cat("\n=====", tb, "\n")
  d <- try(irw_fetch(tb), silent=TRUE)
  if (inherits(d,"try-error")) { cat("  FETCH FAIL\n"); next }
  cat("  cols:", paste(names(d), collapse=", "), "| nrow:", nrow(d), "\n")
  for (cn in intersect(c("id","item","rater"), names(d)))
    cat("  ",cn,"(",length(unique(d[[cn]])),"):", paste(head(unique(as.character(d[[cn]])),8), collapse=" ; "), "\n")
  cat("   resp range:", paste(range(d$resp,na.rm=TRUE),collapse="-"), " uniq:",length(unique(d$resp)),"\n")
  flush.console()
}
