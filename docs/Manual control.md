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

## Set manual control

`PUT /device/energy-profile/instant/manunal`

### Body
```JSON
{
  "stationId": 11111111111111,  // ID of the station
  "enable":true, // false to disable control
  "mode":"2", // 2 = hold
  "duration":"30", // minutes
  "powerLimitation":"" // kW
}
```

To disable manual control, send only:

```JSON
{
  "stationId": 11111111111111,
  "enable": false
}
```


**Modes:**
 - 0 = charge
 - 1 = discharge
 - 2 = hold
 - 3 = self-consumption


### Response
```JSON
{"code":0,"msg":"success","data":true}
```


## Get manual control
`GET /device/energy-profile/instant/manunal/{stationId}`

```JSON
{
    "code": 0,
    "msg": "success",
    "data": {
        "enable": false, // true when enabled
        "mode": "2", // the mode when enabled
        "endTime": "1790590201" // when the manual mode will end
    }
}
```