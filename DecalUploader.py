from rblxopencloud import User, AssetType, Asset
import requests, random, string, io
from PIL import Image


class DecalClass:
    def __init__(self, cookie:str, file:bytes, title:str, description:str) -> None:
        self.cookie = cookie
        self.file = file
        self.title = title
        self.description = description
        self.API_key = None
        self.creator = None
        pass

    def getApiKey(self):
        if self.API_key: return self.API_key

        payload = {"cloudAuthUserConfiguredProperties": {"name": ''.join(random.choices(string.digits, k=2)),"description": "","isEnabled": True,"allowedCidrs": ["0.0.0.0/0"],"scopes": [{"scopeType": "asset","targetParts": ["U"],"operations": ["read", "write"]}]}}

        headers = {
            "content-type": "application/json",
            "X-Csrf-Token": requests.post('https://auth.roblox.com/v1/login', cookies={'.ROBLOSECURITY': self.cookie}).headers['x-csrf-token']
        }

        response = requests.post("https://apis.roblox.com/cloud-authentication/v1/apiKey", json=payload, headers=headers, cookies={'.ROBLOSECURITY': self.cookie}).json()
        print(response)
        self.API_key = response['apikeySecret']
        self.creator = User(requests.get('https://www.roblox.com/mobileapi/userinfo',cookies={'.ROBLOSECURITY':self.cookie}).json()['UserID'], self.API_key)
        return self.API_key

    def upload(self):
        asset = self.creator.upload_asset(self.file, AssetType.Decal, self.title, self.description)

        if isinstance(asset, Asset):
            return asset
        else:
            while True:
                status = asset.fetch_operation()
                if status:
                    return status

if '__main__' in __name__:
    ROBLOSECURITY = input('Cookie: ')

    img = Image.open("811084396810731520.png")
    img = img.resize((500,500))



    for a in range(0,60):
        rgba = img.convert("RGBA")
        datas = rgba.getdata()

        newData = []

        for item in datas:
            newData.append(item)

        # Picks random pixel to replace
        ran = random.randint(0, len(newData))
        # Sets the color
        newData[ran]=(
            random.randint(0,item[0]),
            random.randint(0,item[1]),
            random.randint(0,item[2]), item[3])
        rgba.putdata(newData)

        # Create an in-memory bytes buffer
        buffer = io.BytesIO()
        
        # Save the image to the buffer in JPEG format
        rgba.save(buffer, format="PNG")

        # Seek to the beginning of the buffer
        buffer.seek(0)
        buffer.name = "File.png"
        rgba.close()

        creator = DecalClass(ROBLOSECURITY,buffer,"decal","decal")
        creator.getApiKey()
        asset = creator.upload()

        if isinstance(asset, Asset):
            status = asset
        else:
            while True:
                status = asset.fetch_operation()
                #print(status)
                if status:
                    break

        print(status.id)
