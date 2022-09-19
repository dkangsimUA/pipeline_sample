#!/usr/bin/env python

from genericpath import isfile
import os
import csv
import json
import requests

def find_file(file_name, directory_name):
    files_found = []
    for path, subdirs, files in os.walk(directory_name):
        for name in files:
            if(file_name == name):
                file_path = os.path.join(path,name)
                files_found.append(file_path)
    return files_found
find_file('qualtricsSurveyConfig.json', 'function')


strConfigFileLocation = "./function/qualtricsSurveyConfig.json"

with open(strConfigFileLocation) as fileConfig:
	objConfig = json.load(fileConfig)

strAPIToken = objConfig["apiToken"]
strDatacenter = objConfig["apiDatacenterID"]
strTargetLibraryID = objConfig["apiLibraryID"]
strCSVFileLocation = objConfig["importSurveyInputCSV"]
strCSVInputFileLocation = objConfig["uploadSurveyScriptOutputCSV"]
strCSVOutputFileLocation = objConfig["assignSurveyScriptOutputCSV"]

##################################################################################################################
##################################################################################################################

dictHeaders = { "x-api-token": strAPIToken, 'Content-Type': "application/json" }
strAddEmailToMailListURL = "https://"+ strDatacenter + ".qualtrics.com/API/v3/mailinglists/"
strCreateDistURL = "https://"+ strDatacenter + ".qualtrics.com/API/v3/distributions"
listOutputCSV = [["email", "filename", "name", "listName", "listCategory", "distributionDescription", "shareIDs", "qualtricsSurveyID", "qualtricsContactID", "qualtricsEmailListID", "qualtricsDistID", "qualtricsSurveyURL"]]
intIndexRow = 0
intIndexColumn = 0
dictColumnXRef = {}
strColumnName = ""
listOutputRow = []
dictCurrentRow = {}

#
# Create mailing lists for each CSV row (address)
def createMailingList(strListName = "", strlibraryID = "", strListCategory = "", strDatacenter = "", dictHeaders = {}):
	strURL = "https://" + strDatacenter + ".qualtrics.com/API/v3/mailinglists"
	dictReturn = {}

	dictData = {
		"name": strListName,
		"libraryId": strlibraryID,
		"category": strListCategory
	}

	strJSONData = json.dumps(dictData)
	resResponse = requests.post(strURL, data=strJSONData, headers=dictHeaders)
	dictResponse = resResponse.json()

	if (dictResponse["meta"]["httpStatus"] == "200 - OK"):
		dictReturn = {"status" : "200", "qualtricsEmailListID" : dictResponse["result"]["id"]}
#		strReturn = dictResponse["result"]["id"]
	else:
		dictReturn = { "status" : dictResponse["meta"]["httpStatus"], "error" : dictResponse["meta"]["error"]["errorMessage"] }

	return dictReturn

#
# Assign email address to a mailing list
def assignMailingList(strEmail = "", strListID = "", strDatacenter = "", dictHeaders = {}):
	strURL = "https://"+ strDatacenter + ".qualtrics.com/API/v3/mailinglists/" + strListID + "/contacts"
	dictReturn = {}

	dictData = {
		"email":strEmail,
		"unsubscribed": False
	}
	strJSONData = json.dumps(dictData)

	resResponse = requests.post(strURL, data=strJSONData, headers=dictHeaders)
	dictResponse = resResponse.json()

	if (dictResponse["meta"]["httpStatus"] == "200 - OK"):
		dictReturn = { "status" : "200", "qualtricsContactID" : dictResponse["result"]["id"] }
	else:
		dictReturn = { "status" : dictResponse["meta"]["httpStatus"], "error" : dictResponse["meta"]["error"]["errorMessage"] }

	return dictReturn

#
# Activate survey
def activateSurvey(strSurveyID = "", strDatacenter = "", dictHeaders = {}):
	dictReturn = {}
	strURL = "https://"+ strDatacenter + ".qualtrics.com/API/v3/surveys/" + strSurveyID

	dictData = {
		"isActive": True,
	}

	strJSONData = json.dumps(dictData)

	resResponse = requests.put(strURL, data=strJSONData, headers=dictHeaders)
	dictResponse = resResponse.json()

	if (dictResponse["meta"]["httpStatus"] == "200 - OK"):
		dictReturn = { "status" : "200" }
	else:
		dictReturn = { "status" : dictResponse["meta"]["httpStatus"], "notice" : dictResponse["meta"]["notice"] }

	return dictReturn

#
# Create survey distribution
def createDistribution(strSurveyID = "", strDistributionDescription = "", strListID = "", strDatacenter = "", dictHeaders = {}):
	dictReturn = {}
	strURL = "https://"+ strDatacenter + ".qualtrics.com/API/v3/distributions"

	dictData = {
		"surveyId": strSurveyID,
		"linkType": "Individual",
		"description": strDistributionDescription,
		"action": "CreateDistribution",
#		"expirationDate": "2020-10-24 00:00:00",
		"mailingListId": strListID
	}

	strJSONData = json.dumps(dictData)
	resResponse = requests.post(strURL, data=strJSONData, headers=dictHeaders)
	dictResponse = resResponse.json()
	if (dictResponse["meta"]["httpStatus"] == "200 - OK"):
		dictReturn = { "status" : "200", "qualtricsDistID" : dictResponse["result"]["id"] }
	else:
		dictReturn = { "status" : dictResponse["meta"]["httpStatus"], "error" : dictResponse["meta"]["error"]["errorMessage"] }

	return dictReturn

#
# Get link and data from survey
def getSurveyLink(strDistributionID = "", strSurveyID = "", strDatacenter = "", dictHeaders = {}):
	dictReturn = {}
	strURL = "https://"+ strDatacenter + ".qualtrics.com/API/v3/distributions" + "/" + strDistributionID + "/links"
	dictParameters = { "surveyId" : strSurveyID }

	resResponse = requests.get(strURL, params=dictParameters, headers=dictHeaders)
	dictResponse = resResponse.json()

	if (dictResponse["meta"]["httpStatus"] == "200 - OK"):
		dictReturn = { "status" : "200", "qualtricsSurveyURL" : dictResponse["result"]["elements"][0]["link"], "email": dictResponse["result"]["elements"][0]["email"] }
	else:
		dictReturn = { "status" : dictResponse["meta"]["httpStatus"], "error" : dictResponse["meta"]["error"]["errorMessage"] }

	return dictReturn


with open(strCSVInputFileLocation) as fileDataInput:
	csvReaderFileDataInput = csv.reader(fileDataInput, delimiter=',')

	for listRowData in csvReaderFileDataInput:
		if (intIndexRow == 0):
			for strColumnName in listRowData:
				dictColumnXRef[strColumnName] = intIndexColumn
				intIndexColumn = intIndexColumn + 1
		else:
			for strColumnName in listOutputCSV[0]:
				if (strColumnName in dictColumnXRef):
					dictCurrentRow[strColumnName] = listRowData[dictColumnXRef[strColumnName]]
				else:
					dictCurrentRow[strColumnName] = ""
# 			Create mailing lists for each CSV row (address)
			dictResponse = createMailingList(dictCurrentRow["listName"], strTargetLibraryID, dictCurrentRow["listCategory"], strDatacenter, dictHeaders)
			if (dictResponse["status"] == "200"):
				strCurrentEmailListID = dictResponse["qualtricsEmailListID"]
				dictCurrentRow["qualtricsEmailListID"] = dictResponse["qualtricsEmailListID"]
#				Add target email address to the mailing list we just created
				dictResponse = assignMailingList(dictCurrentRow["email"], strCurrentEmailListID, strDatacenter, dictHeaders)
				if (dictResponse["status"] == "200"):
					strCurrentContactID = dictResponse["qualtricsContactID"]
					dictCurrentRow["qualtricsContactID"] = dictResponse["qualtricsContactID"]
#					activate survey (we can't assign a distribution until we do so)
					dictResponse = activateSurvey(dictCurrentRow["qualtricsSurveyID"], strDatacenter, dictHeaders)
					if (dictResponse["status"] == "200"):
#						Associate the target survey with the target email address via the mailing list we just created (create distribution)
						dictResponse = createDistribution(dictCurrentRow["qualtricsSurveyID"], dictCurrentRow["distributionDescription"], strCurrentEmailListID, strDatacenter, dictHeaders)
						if (dictResponse["status"] == "200"):
							strCurrentDistID = dictResponse["qualtricsDistID"]
							dictCurrentRow["qualtricsDistID"] = dictResponse["qualtricsDistID"]
#							Get the link of our target survey for the target email address
							dictResponse = getSurveyLink(strCurrentDistID, dictCurrentRow["qualtricsSurveyID"], strDatacenter, dictHeaders)
							if (dictResponse["status"] == "200"):
								dictCurrentRow["qualtricsSurveyURL"] = dictResponse["qualtricsSurveyURL"]
								strSurveyLink = dictResponse["qualtricsSurveyURL"]
								strReturnedEmail = dictResponse["email"]
								listOutputRow = []

								for strColumnName in listOutputCSV[0]:
									listOutputRow.append(dictCurrentRow[strColumnName])

								dictCurrentRow.clear()
								listOutputCSV.append(listOutputRow)
							else:
								print ("step five failed")
								print (dictResponse)
						else:
							print ("step four failed")
							print (dictResponse)
					else:
						print ("step three failed")
						print (dictResponse)
				else:
					print ("step two failed")
					print (dictResponse)
			else:
				print ("step one failed")
				print (dictResponse)

		intIndexRow = intIndexRow + 1

if (len(listOutputCSV) > 1):
	rscCSVOutputFile = open(strCSVOutputFileLocation, 'w+', newline ='')

	with rscCSVOutputFile:
		csvWriterFileDataOutput = csv.writer(rscCSVOutputFile, delimiter=',')
		csvWriterFileDataOutput.writerows(listOutputCSV)
