# Sigen cloud API

endpoints to set battery power limit (for sigen AI mode)

## Set limits

`PUT /device/energy-profile/battery/limit`

### Body

```JSON
{
  "stationId": 11111111111111,  // ID of the station
  "batteryMaxChargingPower": "4294967.295", // this value means : 'depends on system'
  "batteryMaxDischargingPower": "16.000" // sets to 16 kW
}
```

### Response
```JSON
{"code":0,"msg":"success","data":true}
```

## Get limits:

`GET /device/energy-profile/battery/limit/{stationId}`

```JSON
{
    "code": 0,
    "msg": "success",
    "data": {
        "batteryMaxChargingPower": "4294967.295", // means : 'depends on system'
        "batteryMaxDischargingPower": "16.000" // power limit in kW  (16kW)
    }
}
```