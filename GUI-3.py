from tkinter import *
import requests
import zipfile
import io
import json
import re
import os


# Setting user Parameters
apiToken = "8NUQ1BwOxdONDWTtUXIaqXIQ0ka582wdEOJ2XkSv"
dataCenter = "co1"

baseUrl = "https://{0}.qualtrics.com/API/v3/surveys".format(dataCenter)
headers = {
    "x-api-token": apiToken,
    }

response = requests.get(baseUrl, headers=headers)
data = response.json()


root = Tk()

root.geometry("500x600")
topFrame = Frame(root)
topFrame.pack()
bottomFrame = Frame(root)
bottomFrame.pack(side = BOTTOM)

def download(id):
    apiToken = "8NUQ1BwOxdONDWTtUXIaqXIQ0ka582wdEOJ2XkSv"
    surveyId = id
    fileFormat = "json"
    dataCenter = 'co1'

    # Setting static parameters
    requestCheckProgress = 0
    progressStatus = "in progress"
    baseUrl = "https://{0}.qualtrics.com/API/v3/responseexports/".format(dataCenter)
    headers = {
        "content-type": "application/json",
        "x-api-token": apiToken,
    }

    # Step 1: Creating Data Export
    downloadRequestUrl = baseUrl
    downloadRequestPayload = '{"format":"' + fileFormat + '","surveyId":"' + surveyId + '"}'
    downloadRequestResponse = requests.request("POST", downloadRequestUrl, data=downloadRequestPayload,
                                               headers=headers)
    progressId = downloadRequestResponse.json()["result"]["id"]
    print(downloadRequestResponse.text)

    # Step 2: Checking on Data Export Progress and waiting until export is ready

    isFile = None

    while requestCheckProgress < 100 and progressStatus is not "complete" and isFile is None:
        requestCheckUrl = baseUrl + progressId
        requestCheckResponse = requests.request("GET", requestCheckUrl, headers=headers)
        isFile = (requestCheckResponse.json()["result"]["file"])
        if isFile is None:
            print("file not ready")
        else:
            print("file created:", requestCheckResponse.json()["result"]["file"])
        requestCheckProgress = requestCheckResponse.json()["result"]["percentComplete"]
        print("Download is " + str(requestCheckProgress) + " complete")

    # Step 3: Downloading file
    requestDownloadUrl = baseUrl + progressId + '/file'
    requestDownload = requests.request("GET", requestDownloadUrl, headers=headers, stream=True)
    regex = r"([a-zA-Z0-9,.\-|;!_?\[\]&\ \(\)]+.json)"
    text = str(requestDownload.content, 'utf-8', errors='replace')
    filename = re.findall(regex, text)

    # Step 4: Unzipping the file
    zipfile.ZipFile(io.BytesIO(requestDownload.content)).extractall("MyQualtricsDownload")
    dir = os.getcwd()

    with open(str(dir) + "/MyQualtricsDownload/" + str(filename[0]), 'r') as json_file:
        json_decoded = json.load(json_file)

        for element in json_decoded['responses']:
            element['surveyID'] = id
            element['surveyName'] = str(filename[0])

        with open(str(dir) + "/MyQualtricsDownload/" + str(filename[0]), 'w') as json_out_file:
            json.dump(json_decoded, json_out_file, indent=4, separators=(',', ': '))
    print('Complete')

number_of_surveys = len(data["result"]["elements"])
list_of_surveys = []
var_bottoms = []
for i in range(number_of_surveys):
    list_of_surveys.append([data["result"]["elements"][i]["name"], data["result"]["elements"][i]["id"]])
    var_bottoms.append("b" + str(i))
    var_bottoms[i] = Button(topFrame, text = list_of_surveys[i][0], width = 30, wraplength = 150, command = lambda i = i: download(list_of_surveys[i][1])).pack()

root.mainloop()

