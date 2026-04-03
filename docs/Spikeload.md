**## add spike load**



**POST** 

https://api-eu.sigencloud.com/prediction/aipv/prediction/modify/predictLoad



**Headers**
Authorization:	bearer \[access token]

content-type:	application/json; charset=utf-8



**Body**

{

&#x20;   "stationId": 11111111111111,  // ID of the station

&#x20;   "loadType": 4, // Car charging

&#x20;   "startTime": "13:15", // local time

&#x20;   "startDate": "2026-04-04", // date

&#x20;   "duration": 180, // duration in minutes

&#x20;   "power": 10 // kW

}

