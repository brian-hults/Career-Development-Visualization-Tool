# clear environment list
rm(list = ls())

# Install ipums package if not present on the system
if("ipumsr" %in% rownames(installed.packages()) == FALSE) {install.packages("ipumsr")}

# Load required 'ipumsr' library
require("ipumsr")

# NOTE: To load data, you must download both the extract's data and the DDI
# and also set the working directory to the folder with these files (or change the path below).

if (!require("ipumsr")) stop("Reading IPUMS data into R requires the ipumsr package. It can be installed using the following command: install.packages('ipumsr')")

file_name = 'cps_00006.xml'
out_file = 'numeric_occupation_data_1968_present.txt'

# function to take in the input file and output file names/paths, extract the IPUMS data, label columns,
# filter out NAs from the last two columns, and write the processed data to a tab separated txt file.
extract_data <- function(ddi_file, out_file) {
  ddi <- read_ipums_ddi(file_name)
  data <- read_ipums_micro(ddi)
  
  # Label the columns
  colnames(data) <- c('YEAR', 'CPSID', 'CPSIDP', 'OCC2010', 'OCCLY2010')
  
  # Find and filter out the rows of data that have 0 to represent either no job change or non-reported job information
  # NOTE: Had to avoid removing NA and zero values from columns 2 and 3 because all data prior to 1989 has 'NA' in the CPSID columns
  filtered_data <- data[complete.cases(data[,4:5]),]
  filtered_data <- filtered_data[which(filtered_data[,4] != filtered_data[,5]),]
  
  # Write the filtered dataframe to a tab separated txt file
  write.table(filtered_data, 'test_file.txt', sep = '\t', quote = FALSE, row.names = FALSE, col.names = TRUE)
}

# Run the program
extract_data(file_name, out_file)
