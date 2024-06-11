import json

import requests

headers = {
    "Authorization": f"Bearer twge3ua3jy5dbmhzjw2c, User 1394bee7b3f920428e0ea577766c948f",
    "Accept": "application/vnd.api.v2+json"
}

data = {
    "login": "dmitriy.tsvetkov.20@gmail.com",
    "password": "nZhqhQg9"
}

client_1 = {

    "phone": "79000000000",
    "fullname": "ДИМА",
    "email": "d@yclients.com",
    "code": "38829",
    "comment": "тестовая запись!",
    "type": "mobile",
    "notify_by_sms": 6,
    "notify_by_email": 24,
    "api_id": "777",
    "custom_fields": {
        "my_client_custom_field": 789,
        "some_another_client_field": [
            "first client value",
            "next client value"
        ]
    },
    "appointments": [
        {
            "id": 1,
            "services": [
                331
            ],
            "staff_id": 6544,
            "datetime": 1443517200,
            "custom_fields": {
                "my_custom_field": 123,
                "some_another_field": [
                    "first value",
                    "next value"
                ]
            }
        },
        {
            "id": 2,
            "services": [
                99055
            ],
            "staff_id": 6544,
            "datetime": 1443614400,
            "custom_fields": {
                "my_custom_field": 456,
                "some_another_field": [
                    "next value",
                    "last value"
                ]
            }
        }
    ]
}

r = requests.post("https://api.yclients.com/api/v1/book_record/1048533", headers=headers, json=client_1)

print(r.json())