##############################
# this script edits the json that pulls on the most recent surveylist and
# established output for python API scripts
###############################


if (!require("pacman")) install.packages("pacman")
pacman::p_load(jsonlite, here, glue, tidyverse, 
               reticulate, beepr, blastula, keyring, 
               Rcpp)

#################################################################
# load json file for Python
json_data <- read_json(here("function", 
                            "qualtricsSurveyConfig.json"))

 json_data$apiToken <- "ngZZK8IxIeJiOs8Y5U6FtbYoeJbkk4CjofJkGGYu" # JAVIER's token. Change to yours if relevant.
 json_data$apiDatacenterID <- "iad1"
 json_data$apiLibraryID <- "GR_8DiwObUzWRKAISy"

# Declare the folder with all the qsf files
json_data$qsfFileLocation <- glue("./input/generated_qsf_files/MEX/") # 

# This is the "surveylist.csv" file matching the .qsf survey file per respondent for upload in Qualtrics
json_data$importSurveyInputCSV <- glue("./input/surveylist/MEX/MEX_surveylist.csv")

# Indicate the new file to store the Qualtrics meta data of the uploaded surveys 
json_data$uploadSurveyScriptOutputCSV <- glue("./output/result-survey-upload_MEX.csv")

# Indicate the new file to store the Qualtrics meta data of the assigned Qualtrics surveys 
json_data$assignSurveyScriptOutputCSV <- glue("./output/result-survey-assignment_MEX.csv")


# save over the json file with current information
json_data %>% 
  as_tibble %>%
  toJSON(pretty=TRUE) %>% 
  str_remove("\\[") %>% # I can't get the [] around the json to leave, [] is an array and we don't want that. 
  str_remove("\\]") %>% # 
  write_file(here("function", "qualtricsSurveyConfig.json"))


##################################################################################
## PYTHON TIME!
## If this is your first time running the script on your computer, you need to
# Download packages only once
#py_install("requests")

# this import your current path to python
py_config() 

# Run the python script that uploads qsfs to qualtrics
source_python(here("function", "subscripts", "1_upload_surveys.py"))
beep(sound = 5) # play sound when done running


# Run the python script that assigns the qualtrics surveys to the right people
source_python(here("function", "subscripts", "2_assign_surveys.py"))
beep(sound = 5) # play sound when done running

# End of script
