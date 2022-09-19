#!/usr/bin/env python

import os
import csv
import json
import requests

# print(os.getcwd())
# # os.path.realpath('./3_qualtrics_survey_upload/')
# path = os.path.abspath(os.path.dirname(__file__))
# print(os.getcwd())

# strConfigFileLocation = "./3_qualtrics_survey_upload/qualtricsSurveyConfig.json"
strConfigFileLocation = './3_qualtrics_survey_upload/qualtricsSurveyConfig.json'
with open(strConfigFileLocation, encoding="utf8", errors="ignore") as fileConfig:
	objConfig = json.load(fileConfig)

strAPIToken = objConfig["apiToken"]
strDatacenter = objConfig["apiDatacenterID"]
strCSVFileLocation = objConfig["importSurveyInputCSV"]
strCSVOutputFileLocation = objConfig["uploadSurveyScriptOutputCSV"]
strSurveyFileLocation = objConfig["qsfFileLocation"]

#########################################################################################################
#########################################################################################################

intIndexColumn = 0
intIndexRow = 0
listFilesToPush = []
dictFilesToPush = {}
dictFileMetaData = {}
dictFilesRecorded = {}
strFileToPushIndex = ""
listDataOutput = [["email", "filename", "name", "listName", "listCategory", "distributionDescription", "shareIDs", "qualtricsSurveyID"]]
dictColumnXRef = {}

strBaseURL = "https://" + strDatacenter + ".qualtrics.com/API/v3/surveys"
dictHeaders = { "x-api-token": strAPIToken }
dictShareHeaders = { "X-API-TOKEN": strAPIToken, "Content-Type": "application/json" }

with open(strCSVFileLocation, encoding="utf8", errors="ignore") as fileDataInput:
	csvReaderFileDataInput = csv.reader(fileDataInput, delimiter=',')
	for listRowData in csvReaderFileDataInput:
		if (intIndexRow > 0):
			if (listRowData[dictColumnXRef["filename"]] in dictFilesToPush):
				dictFilesToPush[listRowData[dictColumnXRef["filename"]]]["emails"].append(listRowData[dictColumnXRef["email"]])
			else:
				dictFilesToPush[listRowData[dictColumnXRef["filename"]]] = { "emails": [listRowData[dictColumnXRef["email"]]], "filename" : listRowData[dictColumnXRef["filename"]], "name": listRowData[dictColumnXRef["name"]], "listName": listRowData[dictColumnXRef["listName"]], "listCategory": listRowData[dictColumnXRef["listCategory"]], "distributionDescription": listRowData[dictColumnXRef["distributionDescription"]], "shareIDs": listRowData[dictColumnXRef["shareIDs"]], "qualtricsSurveyID": "" }
		else:
			for strColumnName in listRowData:
				dictColumnXRef[strColumnName] = intIndexColumn
				intIndexColumn = intIndexColumn + 1

		intIndexRow = intIndexRow + 1

listFilesToPush = dictFilesToPush.keys()

for strFileToPushIndex in listFilesToPush:
	dictFiles = {
		'file': (
			dictFilesToPush[strFileToPushIndex]["filename"],
			open((strSurveyFileLocation + dictFilesToPush[strFileToPushIndex]["filename"]), 'rb'),
			'application/vnd.qualtrics.survey.qsf'
		)
	}

	dictData = {
		"name": dictFilesToPush[strFileToPushIndex]["name"]
	}

	resResponse = requests.post(strBaseURL, files=dictFiles, data=dictData, headers=dictHeaders)
	dictResponse = resResponse.json()
	if (dictResponse["meta"]["httpStatus"] == "200 - OK"):
		dictFilesToPush[strFileToPushIndex]["QualtricsID"] = dictResponse["result"]["id"]
		for strEmail in dictFilesToPush[strFileToPushIndex]["emails"]:
			listDataOutput.append([strEmail, dictFilesToPush[strFileToPushIndex]["filename"], dictFilesToPush[strFileToPushIndex]["name"], dictFilesToPush[strFileToPushIndex]["listName"], dictFilesToPush[strFileToPushIndex]["listCategory"], dictFilesToPush[strFileToPushIndex]["distributionDescription"], listRowData[dictColumnXRef["shareIDs"]], dictResponse["result"]["id"]])
		print("Successfully sent " + dictFilesToPush[strFileToPushIndex]["name"] + " (" + dictFilesToPush[strFileToPushIndex]["filename"] + ") to Qualtrics (surveyID: " + dictResponse["result"]["id"] + ")")

		strShareSurveyURL = "https://" + strDatacenter + ".qualtrics.com/API/v3/surveys/" + dictResponse["result"]["id"] + "/permissions/collaborations"
		listToShare = dictFilesToPush[strFileToPushIndex]["shareIDs"].split("|")

		for strShareID in listToShare:
			dictShareData = {
				"recipientId": strShareID,
				"permissions": {
					"surveyDefinitionManipulation": {
						"copySurveyQuestions": True,
						"editSurveyFlow": True,
						"useBlocks": True,
						"useSkipLogic": True,
						"useConjoint": True,
						"useTriggers": True,
						"useQuotas": True,
						"setSurveyOptions": True,
						"editQuestions": True,
						"deleteSurveyQuestions": True,
						"useTableOfContents": True,
						"useAdvancedQuotas": True
					},
					"surveyManagement": {
						"editSurveys": True,
						"activateSurveys": True,
						"deactivateSurveys": True,
						"copySurveys": True,
						"distributeSurveys": True,
						"deleteSurveys": True,
						"translateSurveys": True
					},
					"response": {
						"editSurveyResponses": True,
						"createResponseSets": True,
						"viewResponseId": True,
						"useCrossTabs": True,
						"useScreenouts": True
					},
					"result": {
						"downloadSurveyResults": True,
						"viewSurveyResults": True,
						"filterSurveyResults": True,
						"viewPersonalData": True
					}
				}
			}

			strShareData = json.dumps(dictShareData)
			resShareResponse = requests.post(strShareSurveyURL, data=strShareData, headers=dictShareHeaders)
			dictShareResponse = resShareResponse.json()
	else:
		print(">>>Failed to send " + dictFilesToPush[strFileToPushIndex]["name"] + " (" + dictFilesToPush[strFileToPushIndex]["filename"] + ") to Qualtrics")

if (len(listDataOutput) > 1):
	rscCSVOutputFile = open(strCSVOutputFileLocation, 'w+', newline ='')

	with rscCSVOutputFile:
		csvWriterFileDataOutput = csv.writer(rscCSVOutputFile, delimiter=',')
		csvWriterFileDataOutput.writerows(listDataOutput)
