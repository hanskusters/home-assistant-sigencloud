# Spike load

## Add spike load

`POST /prediction/aipv/prediction/modify/predictLoad`

### Body
```JSON
{
 "stationId": 11111111111111,  // ID of the station
  "loadType": 4, // Car charging
  "startTime": "13:15", // local time
  "startDate": "2026-04-04", // date
  "duration": 180, // duration in minutes
  "power": 10 // kW
}
```
### Response
unknown

## Get spike loads

`GET /prediction/aipv/prediction/get/automationLoadRecord/{stationId}?stationId={stationId}`

### Response
```JSON
{
    "code": 0,
    "msg": "success",
    "data": [
        {
            "stationId": 11111111111111,
            "loadType": 4,
            "eventId": "2041611720920752128", // = string !
            "startDate": "2026-04-08",
            "startTime": "02:00",
            "duration": 180,
            "power": 11.0
        }
    ]
}
```


## Delete spike load
 
`POST /prediction/aipv/prediction/del/automationLoad?stationId={station_id}&eventId={event_id}`

### Response
```JSON
{
    "code":0,
    "msg":"success",
    "data": true
}
```