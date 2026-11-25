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