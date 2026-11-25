# AI Predictions

endpoints to get AI info


## Get :

`GET /data-process/sigen/station/ai/all/prediction/v1?stationId={stationId}&dateFlag=1&startDate={yyyyMMdd}&endDate={yyyyMMdd}


```JSON
{
    "code": 0,
    "msg": "success",
    "data": {
    "status": 0,
    "estimatedDate": "",
    "chartData":
    {
        "chartName": "",
        "unit": "kW",
        "chartType": "",
        "dataSeries": [
        {
            "id": "FROM_SOLAR_PREDICT",
            "points": [ // one point every 5 minutes
            {
                "time": "20261126 00:00",
                "value": 0
            }]
        }
    ],
    "preTimePeriodTotal": null,
    "buyTariffPredictionBoundaryTime": "",
    "sellTariffPredictionBoundaryTime": ""
    }
}
}
```

> note these values are all predictions, even when the timestamp is in the past.

### dataSeries

`id` \
FROM_SOLAR_PREDICT
FROM_SIGEN_SOLAR_PREDICT
GRID_PREDICT : grid power positive is import from grid, negative is export to grid
TO_LOAD_PREDICT: consumed power
BATTERY_PREDICT : battery power (kW) negative is charge, positive discharge
TO_EVDC_EVAC_LOAD_PREDICT :  ??? don't know, this has values but I don't have a sigen EV charger
SOC_PREDICT: battery SOC %

`points` \
one item for each 5 minutes
- `time`: yyyyMMdd HH:mm  (local time)
- `value`: depends on series. SOC_PREDICT is %-value, others propably kW