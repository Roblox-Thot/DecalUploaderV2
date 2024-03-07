from rblxopencloud import User, AssetType, Asset, exceptions
import requests, random, string, io
from PIL import Image
from time import sleep as sleepy
import xmltodict
import threading # :flushed: is it going to happen? spoiler-prob not in this file

class DecalClass:
    def __init__(self, cookie:str) -> None:
        self.cookie = cookie
        self.creator = None
        self.gotKey = False
        self.apiKey = self.__get_api_key__()
        pass

    def __get_api_key__(self):
        if self.gotKey: return self.apiKey

        payload = {"cloudAuthUserConfiguredProperties": {"name": ''.join(random.choices(string.digits, k=2)),"description": "","isEnabled": True,"allowedCidrs": ["0.0.0.0/0"],"scopes": [{"scopeType": "asset","targetParts": ["U"],"operations": ["read", "write"]}]}}

        headers = {
            "content-type": "application/json",
            "X-Csrf-Token": requests.post('https://auth.roblox.com/v1/login', cookies={'.ROBLOSECURITY': self.cookie}).headers['x-csrf-token']
        }

        response = requests.post("https://apis.roblox.com/cloud-authentication/v1/apiKey", json=payload, headers=headers, cookies={'.ROBLOSECURITY': self.cookie}).json()
        print(response)
        self.apiKey = response['apikeySecret']
        self.creator = User(requests.get('https://www.roblox.com/mobileapi/userinfo',cookies={'.ROBLOSECURITY':self.cookie}).json()['UserID'], self.apiKey)
        self.gotKey = True
        return self.apiKey

    def upload(self, file:bytes, title:str, description:str):
        asset = self.creator.upload_asset(file, AssetType.Decal, title, description)

        if isinstance(asset, Asset):
            return asset
        else:
            while True:
                status = asset.fetch_operation()
                if status:
                    return status
                
    def get_image_id(image_id): #untested gpt moment :)
        if image_id:
            url = f"https://assetdelivery.roblox.com/v1/asset/?id={image_id}"
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    xml_data = xmltodict.parse(response.text)
                    result_url = xml_data['roblox']['Item']['Properties']['Content']['url']['#text']
                    result = result_url.split("=")[1]
                    return result
                else:
                    return "0"
            except Exception as e:
                print(e)
                return "0"
        else:
            return "0"

if '__main__' in __name__:
    ROBLOSECURITY = input('Cookie: ')

    img = Image.open("avatar_1385488.png")
    img = img.resize((500,500))


    creator = DecalClass(ROBLOSECURITY)

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

        print('uploading')
        while True:
            try:
                asset = creator.upload(buffer, "decal", f'{a}')
                break
            except Exception as e:
                if e == exceptions.RateLimited:
                    sleepy(2)
                    print('rate limit')

        sleepy(1)

        print(asset.id)
