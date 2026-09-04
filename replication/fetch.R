options(irw.itemtext_disclaimer = FALSE)
suppressMessages(library(irw))
for (tb in c("spelling2pronounce_edwards2023","kalimahnorms_alzahrani_2025","Forthmann-2024-creative_quality")) {
  cat("fetching", tb, "\n"); flush.console()
  d <- try(irw_fetch(tb), silent=TRUE)
  if (inherits(d,"try-error")) { cat("FAIL", tb, "\n"); next }
  write.csv(d, paste0(tb, ".csv"), row.names=FALSE)
  cat("  ok", nrow(d), "x", ncol(d), "cols:", paste(names(d), collapse=","), "\n"); flush.console()
}
