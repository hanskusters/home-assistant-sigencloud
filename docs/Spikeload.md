# Sigen cloud API

- **Url**  
`https://api-eu.sigencloud.com`

- **Content-type**  
application/json; charset=utf-8

- **Authorization**  
Bearer [access token]


### Responses
Seems all responses are of this format:
```JSON
{
    "code": 0, // not sure
    "msg": "success", // result state
    "data": data // the interesting part
}
```

## Authentication
Get access token from auth api:  
`POST /openapi/auth/login/password`
### Body
```JSON
{
    "username": "login-code", 
    "password": "****"
}
 ```

If response is `OK` the response will be like;
```JSON
{
    "data": {
        "accessToken": "****"
    }
}
```

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