'''
file:           main.py
author:         Max Legrand
fileOverview:   Scrape Glucose Data and output contents to text file
                and create thread for webserver
'''
import urllib.request
import urllib.error
import urllib.parse
import json
import os
import time
from keep_alive import keep_alive


def get_data():
    """
    Scrapes Glucose Data and returns results

    Returns:
        (String, String, List): Tuple containing glucose value, trend value, and list of glucose data
    """
    method = "POST"
    handler = urllib.request.HTTPHandler()
    opener = urllib.request.build_opener(handler)
    sessionIdUrl = 'https://share2.dexcom.com/ShareWebServices/Services/General/LoginPublisherAccountByName'
    glucoseUrl = 'https://share2.dexcom.com/ShareWebServices/Services/Publisher/ReadPublisherLatestGlucoseValues?sessionID='  # noqa:E501
    username = os.getenv("username")
    password = os.getenv("password")
    glucoseGetParams = '&minutes=1440&maxCount=11'
    payload = {"password": password, "applicationId": "d89443d2-327c-4a6f-89e5-496bbb0317db", "accountName": username}
    payload = json.dumps(payload).encode('utf8')
    seshRequest = urllib.request.Request(sessionIdUrl, payload)
    seshRequest.add_header("Content-Type", 'application/json')
    seshRequest.add_header("User-Agent", 'Dexcom Share/3.0.2.11 CFNetwork/672.0.2 Darwin/14.0.0')
    seshRequest.add_header("Accept", 'application/json')
    seshRequest.get_method = lambda: method
    sessionID = None
    try:
        connection = opener.open(seshRequest)
    except urllib.error.HTTPError as e:
        connection = e
    if connection.code == 200:
        sessionID = connection.read()
        sessionID = sessionID[1:-1]
        sessionID = sessionID.decode("utf8")
    else:
        print((connection.code))

    getGlucoseUrl = glucoseUrl + sessionID + glucoseGetParams
    glucoseRequest = urllib.request.Request(getGlucoseUrl)
    glucoseRequest.get_method = lambda: method
    glucoseRequest.add_header("Accept", 'application/json')
    glucoseRequest.add_header("Content-Length", '0')
    emptyLoad = {"": ""}
    try:
        connection2 = opener.open(glucoseRequest, json.dumps(emptyLoad).encode("utf8"))
    except urllib.error.HTTPError as e:
        connection2 = e

    glucose = None
    trend = None
    data = []

    if connection2.code == 200:
        glucoseReading = connection2.read()
        glucoseReading = json.loads(glucoseReading)
        glucose = glucoseReading[0]["Value"]
        trend = glucoseReading[0]["Trend"]
        data = []
        for item in glucoseReading:
            data.append(int(item["Value"]))

    else:
        print((connection2.code))

    return (glucose, trend, data)


def replace_trend(trend):
    """
    Replace trend number with arrows

    Args:
        trend (int): trend number

    Returns:
        String: trend represented with arrows
    """
    trendtext = None
    if trend == 0:
        trendtext = ""
    if trend == 1:
        # trendtext = "rising quickly"
        trendtext = "↑↑"
    if trend == 2:
        # trendtext = "rising"
        trendtext = "↑"
    if trend == 3:
        # trendtext = "rising slightly"
        trendtext = "↗"
    if trend == 4:
        # trendtext = "steady"
        trendtext = "→"
    if trend == 5:
        # trendtext = "falling slightly"
        trendtext = "↘"
    if trend == 6:
        # trendtext = "falling"
        trendtext = "↓"
    if trend == 7:
        trendtext = "↓↓"
    if trend == 8:
        # trendtext = "unable to determine a trend"
        trendtext = " "
    if trend == 9:
        # trendtext = "trend unavailable"
        trendtext = " "
    return trendtext


glucose, trend, datalist = get_data()
trend_str = replace_trend(trend)

final_string = f"{glucose}{trend_str}"
# final_string = f"{glucose}"
data = {"bg": final_string}
f = open("output.txt", "w")
json.dump(data, f)
f.close()
with open('datalist.txt', 'w') as f:
    for counter in range(len(datalist)):
        item = datalist[counter]
        if counter != len(datalist)-1:
            f.write(f"{item},")
        else:
            f.write(f"{item}")

keep_alive()

try:
    while 1:
        glucose, trend, datalist = get_data()
        trend_str = replace_trend(trend)
        final_string = f"{glucose}{trend_str}"
        data = {"bg": final_string}
        f = open("output.txt", "w")
        json.dump(data, f)
        f.close()
        with open('datalist.txt', 'w') as f:
            for counter in range(len(datalist)):
                item = datalist[counter]
                if counter != len(datalist)-1:
                    f.write(f"{item},")
                else:
                    f.write(f"{item}")
        time.sleep(30)
except KeyboardInterrupt:
    f.close()
