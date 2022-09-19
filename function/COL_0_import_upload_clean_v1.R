##############################
# Kelsey Gonzalez
# 4/13/2021
# this script edits the json that pulls on the most recent surveylist and
# established output for python API scripts
###############################


if (!require("pacman")) install.packages("pacman")
pacman::p_load(jsonlite, here, glue, tidyverse, reticulate, beepr, blastula, keyring, Rcpp)


# SET COUNTRY CODE FOR CORRECT COUNTRY, AFG or COL 
country_code <- "COL"

#################################################################
# find newest surveylist for respective country code
files <- list.files(here("3_qualtrics_survey_upload", "0_surveylist")) # find list of all survey results
files <- files[str_detect(files, glue("^{country_code}_"))] # select Colombia/Afghanistan results
newest_surveylist <- sort(files, decreasing = TRUE)[1] # pick newest survey results 
newest_surveylist


#################################################################
# load json file for Python
json_data <- read_json(here("3_qualtrics_survey_upload", "qualtricsSurveyConfig.json"))

## Each time we run this, the script updates the json file with current info
## Instructions for the API tokens are found in 'Qualtrics Import and Assign
## Survey scripts Documentation v2.docx' file

# json_data$apiToken <- "arsdMwOH24PxSHAVQmQlzvw0t69aYWZn5trdG17P" # Kelsey's token. Change to yours if relevant. 
 json_data$apiToken <- "ngZZK8IxIeJiOs8Y5U6FtbYoeJbkk4CjofJkGGYu" # JAVIER's token. Change to yours if relevant.
 json_data$apiDatacenterID <- "iad1"
 json_data$apiLibraryID <- "GR_8DiwObUzWRKAISy"

# Declare the folder with all the qsf files
json_data$qsfFileLocation <- glue("./2_governance_survey_generation/3_generated_gov_qsf_files/{country_code}/{Sys.Date()}/") # 

# This is the "surveylist.csv" file matching the .qsf survey file per respondent for upload in Qualtrics
json_data$importSurveyInputCSV <- glue("./3_qualtrics_survey_upload/0_surveylist/{newest_surveylist}")

# Indicate the new file to store the Qualtrics meta data of the uploaded surveys 
json_data$uploadSurveyScriptOutputCSV <- glue("./3_qualtrics_survey_upload/2_upload_results/result-survey-upload_{country_code}_{Sys.Date()}.csv")

# Indicate the new file to store the Qualtrics meta data of the assigned Qualtrics surveys 
json_data$assignSurveyScriptOutputCSV <- glue("./3_qualtrics_survey_upload/3_assign_results/result-survey-assignment_{country_code}_{Sys.Date()}.csv")


# save over the json file with current information
json_data %>% 
  as_tibble %>%
  toJSON(pretty=TRUE) %>% 
  str_remove("\\[") %>% # I can't get the [] around the json to leave, [] is an array and we don't want that. 
  str_remove("\\]") %>% # stupid brackets. It's hacky but I give up. 
  write_file(here("3_qualtrics_survey_upload", "qualtricsSurveyConfig.json"))


##################################################################################
## PYTHON TIME!
## If this is your first time running the script on your computer, you need to
# Download packages only once
# py_install("requests")

# this import your current path to python
py_config() 

# Run the python script that uploads qsfs to qualtrics
source_python(here("3_qualtrics_survey_upload", "1_subscripts", "1_upload_surveys.py"))
beep(sound = 5) # play sound when done running


# Run the python script that assigns the qualtrics surveys to the right people
source_python(here("3_qualtrics_survey_upload", "1_subscripts", "2_assign_surveys.py"))
beep(sound = 5) # play sound when done running

# Run the python script that collaborates the surveys between armedgov managers
source_python(here("3_qualtrics_survey_upload", "1_subscripts", "3_collaborate_surveys.py"))
beep(sound = 5) # play sound when done running



##################################################################################
#### Post Python processing in preparation for Drupal upload 

# read in result-survey-assignment.csv that gets outputted from 2-survey-assignment.py

# find newest response file
assign_files <- list.files(here("3_qualtrics_survey_upload", "3_assign_results")) # find list of all survey results
assign_files <- assign_files[str_detect(assign_files, glue("^result-survey-assignment_{country_code}_"))] # select correct results
assign_file <- sort(assign_files, decreasing = TRUE)[1] # pick newest survey results 
assign_file

# Create csv file for Drupal to create accounts and assing surveys
result <- read_csv(here("3_qualtrics_survey_upload",
                        "3_assign_results",
                        assign_file))

# Gather respondent's info to create accounts
# read in key for name and email for newest upload
key <- read_csv(here("2_governance_survey_generation",
                     "2_master_keys",
                     glue("{country_code}_resp_key.csv")))

###################
# Drupal step 1. Create new accounts
# create delimited survey respondents list to upload in Drupal
result %>% 
  left_join(key, by = c("email", "name" = "name.svy.id")) %>% 
  mutate(name = email) %>% 
  select(name, email, language = lang, timezone) %>% 
  distinct() %>% 
  write_csv(here("4_drupal_upload", # write out survey-respondents-example.csv
                 "1_respondents",
                 glue("survey_respondents_{country_code}_{Sys.Date()}.csv")))


###################
# Drupal step 2. Attaches a survey URL to each user
# Create result-survey-assignment.csv with Drupal survey name (based on location) for display in interface
key %>% 
  select(name.svy.id, drupal_surveyname, email) %>% 
  right_join(result, by = c("email", "name.svy.id" = "name")) %>% 
  filter(!is.na(drupal_surveyname)) %>% 
  mutate(type = "control") %>% 
  select(email, 
         name = drupal_surveyname,
         type, 
         qualtricsContactID, 
         qualtricsSurveyURL) %>% 
  write_csv(here("4_drupal_upload",
                 "2_surveys",
                 glue("result-survey-assignment_{country_code}_{Sys.Date()}.csv")))

beep("complete")







# Email Kristal or Atal the new survey assignments

# If this is your first time running this script, you'll need to create your
# credential keys. University of Arizona emails block blastula from working so
# you need to use a personal account. go to
# https://myaccount.google.com/security on your personal account, click 'App
# Passwords' under the 'Signing in to Google' section, and create a new password
# with 'Select App' -> Other.
# Then Create an app and give it a name.
# Enter your email address under "user" below.
# When running the code, the system will ask you to enter the password that 
# you created in Google.
# You only need to enter the password once. After that, comment the code below.

# create_smtp_creds_key(
#   id = "gmail",
#   user = "javier.osoriozago@gmail.com",
#   provider = "gmail"
# )


# armedgov_MINERVA password: rtnylvmrhmncdzbd
# create_smtp_creds_key(
#   id = "gmail",
#   user = "lwerthm@gmail.com",
#   provider = "gmail"
# )


if (country_code == "COL") {
  email_col <- render_email(here('4_drupal_upload','email_country_managers.Rmd') ,
                            render_options = list(params = list(data = "COL", 
                                                                name = "Kristal")))
  email_col
  smtp_send(
    email_col, # the email that you just rendered
    from = "javier.osoriozago@gmail.com",
    cc = "armedgov@arizona.edu",
    to = "knatera@email.arizona.edu",
    subject = glue::glue("{format(Sys.Date(), '%b %d')}: New Armed Gov Surveys"),
    credentials = creds_key(id = "gmail")
  )
} else {
  email_afg <- render_email(here('4_drupal_upload','email_country_managers.Rmd') ,
                            render_options = list(params = list(data = "AFG", 
                                                                name = "Atal")))
  email_afg
  smtp_send(
    email_afg, # the email that you just rendered
    from = "javier.osoriozago@gmail.com",
    cc = "armedgov@arizona.edu",
    to = "josorio1@arizona.edu", #"aahmadzai@arizona.edu",
    subject = glue::glue("{format(Sys.Date(), '%b %d')}: New Armed Gov Surveys"),
    credentials = creds_key(id = "gmail")
  )
} 


# End of script
