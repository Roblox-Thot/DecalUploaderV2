from requests import get
BASED = 'https://www.roblox.com/users/inventory/list-json?assetTypeId=13&cursor=&itemsPerPage=100&pageNumber={}&userId={}'

def get_decals(userId:int, decals:list = None, pageNumber:int = 1, lastLength:int = float('inf')) -> list:
    if decals is None:
        decals = []

    request_url = BASED.format(pageNumber, userId)
    try:
        response = get(request_url)
        response.raise_for_status()
        if result2 := response.json():
            for decal in result2['Data']['Items']:
                if decal['Creator']['Id'] == userId and decal['Item']['AssetId'] not in decals:
                    asset_id = decal['Item']['AssetId']
                    decals.append(asset_id)

            if len(response.text) != lastLength:
                lastLength = len(response.text)
                pageNumber += 1
                get_decals(userId, decals, pageNumber, lastLength)
    except Exception:
        get_decals(userId, decals, pageNumber, lastLength)

    return decals

if '__main__' in __name__:
    print('Note: inv must be public! (13+)\n\n')
    user_decals = get_decals(int(input('UserId: ')))
    print(user_decals)
    input("Press enter to exit.")
