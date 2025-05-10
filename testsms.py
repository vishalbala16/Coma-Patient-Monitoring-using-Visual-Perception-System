import requests
def process(msg,mob,mob1):
    
    mobile=mob+","+mob1
    url = "https://www.fast2sms.com/dev/bulkV2"

    querystring = {"authorization":"--ENTER----AUTH----KEY----HERE--","sender_id":"FastSM","message":str(msg),"route":"v3","numbers":str(mobile)}

    headers = {
        'cache-control': "no-cache"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    print(response.text)

