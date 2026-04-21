cat("=== R ANALYTICS SCRIPT STARTED ===\n")

library(RSQLite)
library(dplyr)

cat("Libraries loaded\n")

args <- commandArgs(trailingOnly = TRUE)
device_id <- args[1]

cat("Device ID:", device_id, "\n")

# SQLite DB path
db_path <- "app/analytics/db/analytics.db"

con <- dbConnect(SQLite(), db_path)
cat("SQLite connected\n")

# Read latest window data exported by Python
windows <- read.csv("app/analytics/latest_windows.csv")

if (nrow(windows) < 3) {
  cat("Not enough data, exiting\n")
  quit(save = "no")
}

# Analytics
temp_diff <- diff(windows$temp_avg)
trend <- ifelse(mean(temp_diff) > 0.2, "increasing",
         ifelse(mean(temp_diff) < -0.2, "decreasing", "stable"))

stability <- 1 / (1 + sd(windows$temp_avg))
spike <- max(windows$temp_max - windows$temp_min)
anomaly <- (spike > 3) || (stability < 0.4)

cat("Analytics computed\n")

result <- data.frame(
  device_id = device_id,
  window_timestamp = windows$timestamp[1],
  temp_trend = trend,
  temp_stability_score = stability,
  spike_severity = spike,
  anomaly_flag = as.integer(anomaly)
)

dbWriteTable(con, "analytics_results", result, append = TRUE)
dbDisconnect(con)

cat("=== R ANALYTICS COMPLETED ===\n")
