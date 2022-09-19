#############
#RUNS THE PIPELINE
#############

if (!require("pacman")) install.packages("pacman")
pacman::p_load(here, glue, tictoc)

#####################
#Using COLOMBIA QSF FILE 
#Works without any error message
tic()
source(here("function","COL_0_import_upload_clean_test.R"))
toc()
#####################


#####################
#Uploading/Assigning MEXICO QSF FILE
#Error message: 
#Error in py_run_file_impl(file, local, convert) : 
#  requests.exceptions.JSONDecodeError: Expecting value: line 1 column 1 (char 0)

tic()
source(here("function","MEX_0_import_upload_clean_test.R"))
toc()
###