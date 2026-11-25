# Statistics

endpoints to get energy statistics


## Get :

`GET /data-process/sigen/station/statistics/v1/energy?stationId={stationId}&dateFlag=1&startDate={yyyyMMdd}&endDate={yyyyMMdd}


```JSON
{
    "code": 0,
    "msg": "success",
    "data": {
    "status": 0,
    "estimatedDate": "",
    "chartData":
    {
        "chartName": "Energy",
        "unit": "kW",
        "chartType": "LINE",
        "dataSeries": [
        {
            "id": "BATTERY",
            "points": [ // one point every 5 minutes
            {
                "time": "20261126 00:00",
                "value": 1
            }]
        }]
    },
    "sankeyData": {
            "nodes": [
                {
                "id": "FROM_SOLAR",
                "value": 1
                },
                {
                "id": "FROM_BATTERY",
                "value": 17.89
                },
                {
                "id": "TO_BATTERY",
                "value": 10.07
                },
                {
                "id": "FROM_GRID",
                "value": 46.97
                },
                {
                "id": "TO_LOAD",
                "value": 45.58
                },
                {
                "id": "TO_GRID",
                "value": 10.21
                }
            ],
            "links": [
                {
                "sourceId": "FROM_SOLAR",
                "targetId": "TO_BATTERY",
                "value": 0.65
                },
                {
                "sourceId": "FROM_SOLAR",
                "targetId": "TO_LOAD",
                "value": 0.31
                },
                {
                "sourceId": "FROM_SOLAR",
                "targetId": "TO_GRID",
                "value": 0.04
                },
                {
                "sourceId": "FROM_BATTERY",
                "targetId": "TO_LOAD",
                "value": 7.72
                },
                {
                "sourceId": "FROM_BATTERY",
                "targetId": "TO_GRID",
                "value": 10.17
                },
                {
                "sourceId": "FROM_GRID",
                "targetId": "TO_BATTERY",
                "value": 9.42
                },
                {
                "sourceId": "FROM_GRID",
                "targetId": "TO_LOAD",
                "value": 37.55
                }
            ]
        }
    }
}
```

### dataSeries

`id` \
FROM_SOLAR : solor power (kW)
GRID : grid power positive is import from grid, negative is export to grid (kW)
TO_LOAD: consumed power (kW)
BATTERY: battery power (kW) negative is charge, positive discharge

`points` \
one item for each 5 minutes
- `time`: yyyyMMdd HH:mm  (local time)
- `value`: depends on series. SOC_PREDICT is %-value, others kW