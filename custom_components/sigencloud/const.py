DOMAIN = "sigencloud"
BASE_URL = "https://api-eu.sigencloud.com"
AUTH_ENDPOINT = "/openapi/auth/login/password"
CONF_STATION_ID = "station_id"
SPIKE_LOAD_ENDPOINT = "/prediction/aipv/prediction/modify/predictLoad"
AUTOMATION_LOAD_RECORD_ENDPOINT = (
    "/prediction/aipv/prediction/get/automationLoadRecord/{station_id}"
)
AUTOMATION_LOAD_DELETE_ENDPOINT = "/prediction/aipv/prediction/del/automationLoad"
