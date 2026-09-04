options(irw.itemtext_disclaimer = FALSE); suppressMessages(library(irw))
for (tb in c("rating_speed_2025","famous_melodies","fractals_rating","emoji_scheffler_2024","tears")) {
  cat("\n=====", tb, "\n"); d <- try(irw_fetch(tb), silent=TRUE)
  if (inherits(d,"try-error")) { cat(" FAIL\n"); next }
  cat(" cols:", paste(names(d), collapse=", "), "| nrow:", nrow(d), "\n")
  for (cn in setdiff(names(d), c("resp","rt"))) {
    u <- unique(as.character(d[[cn]]))
    cat("  ", cn, "(", length(u), "):", paste(head(u,10), collapse=" ; "), "\n")
  }
  cat("  resp:", paste(head(sort(unique(d$resp)),12), collapse=","), " ... n_uniq", length(unique(d$resp)), "\n")
  write.csv(d, paste0(tb,".csv"), row.names=FALSE)
}
