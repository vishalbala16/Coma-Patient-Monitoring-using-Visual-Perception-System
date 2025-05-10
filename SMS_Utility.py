# import requests


# def process(msg, mob, mob1):
#     mobile = mob + "," + mob1
#     url = "https://www.fast2sms.com/dev/bulkV2"
#
#     querystring = {"authorization": "c13w4hFMmI2BZbyTp6SGYRtkfPJKjA5QXe7osrDqulLNWzvUni4ZAwveNEjoWKiF6pRXJg25rxmVC8Tb",
#                    "sender_id": "TXTIND", "message": str(msg), "route": "v3", "numbers": str(mobile)}
#
#     headers = {
#         'cache-control': "no-cache"
#     }
#
#     response = requests.request("GET", url, headers=headers, params=querystring)
#
#     print(response.text)

#
# def process(msg, mob, mob1):
#     url = "https://www.fast2sms.com/dev/bulkV2"
#
#     payload = "sender_id=DLT_SENDER_ID&message=YOUR_MESSAGE_ID&variables_values=12345|asdaswdx&route=dlt&numbers=9999999999,8888888888,7777777777"
#     headers = {
#         'authorization': "YOUR_API_KEY",
#         'Content-Type': "application/x-www-form-urlencoded",
#         'Cache-Control': "no-cache",
#         }
#     response = requests.request("POST", url, data=payload, headers=headers)
#
#     print(response.text)


from twilio.rest import Client


def send_sms(to_mob):

    # Goto - https://console.twilio.com -> 'Account Info' - to find the below information

    account_sid = 'AC4e644188842190361aba03df0420768a'
    auth_token = '1018e7676295731605bd7d1f015c5c9c'
    my_twilio_phone_number = '+12185100291'
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        from_=my_twilio_phone_number,
        body='Your patient has shown some movements.',
        to=to_mob
    )

    print(message.sid)
