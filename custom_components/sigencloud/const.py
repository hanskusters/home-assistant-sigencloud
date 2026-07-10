DOMAIN = "sigencloud"
BASE_URL = "https://api-eu.sigencloud.com"
# The SigenCloud WAF returns 403 for any User-Agent containing "aiohttp"
# (which is what Home Assistant's default client session sends), so we must
# override it with a UA that does not contain that token.
USER_AGENT = "home-assistant-sigencloud/1.0"
AUTH_ENDPOINT = "/openapi/auth/login/password"
CONF_STATION_ID = "station_id"
SPIKE_LOAD_ENDPOINT = "/prediction/aipv/prediction/modify/predictLoad"
AUTOMATION_LOAD_RECORD_ENDPOINT = (
    "/prediction/aipv/prediction/get/automationLoadRecord/{station_id}"
)
AUTOMATION_LOAD_DELETE_ENDPOINT = "/prediction/aipv/prediction/del/automationLoad"
