#!/usr/bin/env python

import os
import csv
import json
import requests

strConfigFileLocation = "./3_qualtrics_survey_upload/qualtricsSurveyConfig.json"

with open(strConfigFileLocation, encoding="utf8", errors="ignore") as fileConfig:
	objConfig = json.load(fileConfig)

strAPIToken = objConfig["apiToken"]
strDatacenter = objConfig["apiDatacenterID"]
strCSVFileLocation = objConfig["assignSurveyScriptOutputCSV"]

#########################################################################################################
#########################################################################################################

intIndexColumn = 0
intIndexRow = 0
dictColumnXRef = {}
listShareRecords = []
dictShareRecord = {}

dictHeaders = { "X-API-TOKEN": strAPIToken, "Content-Type": "application/json" }

with open(strCSVFileLocation, encoding="utf8", errors="ignore") as fileDataInput:
	csvReaderFileDataInput = csv.reader(fileDataInput, delimiter=',')
	for listRowData in csvReaderFileDataInput:
		if (intIndexRow > 0):
			listShareRecords.append({ "qualtricsSurveyID": listRowData[dictColumnXRef["qualtricsSurveyID"]], "shareIDs": listRowData[dictColumnXRef["shareIDs"]] })
		else:
			for strColumnName in listRowData:
				dictColumnXRef[strColumnName] = intIndexColumn
				intIndexColumn = intIndexColumn + 1
		intIndexRow = intIndexRow + 1

for dictShareRecord in listShareRecords:
	strShareSurveyURL = "https://" + strDatacenter + ".qualtrics.com/API/v3/surveys/" + dictShareRecord["qualtricsSurveyID"] + "/permissions/collaborations"
	listToShare = dictShareRecord["shareIDs"].split("|")
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
		resShareResponse = requests.post(strShareSurveyURL, data=strShareData, headers=dictHeaders)
		dictShareResponse = resShareResponse.json()
		print (dictShareResponse)



