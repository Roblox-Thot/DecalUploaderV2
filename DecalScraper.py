from requests import session,exceptions
sussion=session()
BASED = 'https://www.roblox.com/users/inventory/list-json?assetTypeId=13&cursor=&itemsPerPage=100&pageNumber={}&userId={}'

def get_decals(userId, decals=None, pageNumber=1, lastLength=float('inf')):
    if decals is None:
        decals = []

    request_url = BASED.format(pageNumber, userId)
    try:
        response = sussion.get(request_url)
        response.raise_for_status()
        result2 = response.json()

        if result2:
            for gamepass in result2['Data']['Items']:
                if gamepass['Creator']['Id'] == userId and gamepass['Item']['AssetId'] not in decals:
                    id = gamepass['Item']['AssetId']
                    decals.append(id)

            if len(response.text) != lastLength:
                lastLength = len(response.text)
                pageNumber += 1
                get_decals(userId, decals, pageNumber, lastLength)
    except:
        get_decals(userId, decals, pageNumber, lastLength)

    return decals

print("Note: inv must be public! (13+)\n\n")
userGamepasses = get_decals(int(input("UserId: ")))
print(userGamepasses)
