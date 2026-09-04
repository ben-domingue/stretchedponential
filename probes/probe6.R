options(irw.itemtext_disclaimer = FALSE)
suppressMessages(library(irw))
for (tb in c("previc_bohn2023","mentalrotation_wolf_2024","klatt_2016_speed_estimation","mclaughlin_samuel_2025_auditory_session_2")) {
  cat("\n=====",tb,"\n"); d<-try(irw_fetch(tb),silent=TRUE)
  if(inherits(d,"try-error")){cat("FAIL\n");next}
  cat(" cols:",paste(names(d),collapse=", "),"| nrow:",nrow(d),"\n")
  cat(" n_id:",length(unique(d$id))," n_item:",length(unique(d$item))," resp uniq:",length(unique(d$resp)),"range",paste(range(d$resp,na.rm=TRUE),collapse="-"),"\n")
  cat(" items:",paste(head(unique(as.character(d$item)),8),collapse=" ; "),"\n")
  for(cn in grep("^itemcov_",names(d),value=TRUE)) cat("  ",cn,":",paste(head(unique(as.character(d[[cn]])),10),collapse=","),"\n")
  flush.console()
}
