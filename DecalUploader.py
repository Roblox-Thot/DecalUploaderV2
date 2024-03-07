from rblxopencloud import User, AssetType, Asset, exceptions
import requests, random, string, io
from time import sleep as sleepy
import xmltodict
from json import dumps

try: from PIL import Image; IMAGE_EDIT = True;
except: IMAGE_EDIT = False

class DecalClass:
    def __init__(self, cookie:str) -> None:
        self.cookie = cookie
        self.creator = None
        self.keyId = None
        self.gotKey = False
        self.apiKey = None
        self.__get_api_key__()
        pass

    def __get_api_key__(self):
        """Creates a API key and sets the self vers required"""
        if self.gotKey: return self.apiKey

        payload = {"cloudAuthUserConfiguredProperties": {"name": ''.join(random.choices(string.digits, k=2)),"description": "","isEnabled": True,"allowedCidrs": ["0.0.0.0/0"],"scopes": [{"scopeType": "asset","targetParts": ["U"],"operations": ["read", "write"]}]}}

        headers = {
            "content-type": "application/json",
            "X-Csrf-Token": requests.post('https://auth.roblox.com/v1/login', cookies={'.ROBLOSECURITY': self.cookie}).headers['x-csrf-token']
        }

        response = requests.post("https://apis.roblox.com/cloud-authentication/v1/apiKey", json=payload, headers=headers, cookies={'.ROBLOSECURITY': self.cookie}).json()
        #print(response)
        self.apiKey = response['apikeySecret']
        self.keyId = response['cloudAuthInfo']['id']
        self.creator = User(requests.get('https://www.roblox.com/mobileapi/userinfo',cookies={'.ROBLOSECURITY':self.cookie}).json()['UserID'], self.apiKey)
        self.gotKey = True

    def delete_key(self):
        """Deletes the API key"""
        headers = {
            "content-type": "application/json",
            "X-Csrf-Token": requests.post('https://auth.roblox.com/v1/login', cookies={'.ROBLOSECURITY': self.cookie}).headers['x-csrf-token']
        }
        
        requests.delete(f'https://apis.roblox.com/cloud-authentication/v1/apiKey/{self.keyId}', headers=headers, cookies={'.ROBLOSECURITY': self.cookie}).json()

    def upload(self, file:bytes, title:str, description:str):
        """Attempts to upload decal

        Args:
            file (bytes): file data
            title (str): title of decal
            description (str): discription of decal

        Returns:
            Asset: the asset of the decal
        """
        asset = self.creator.upload_asset(file, AssetType.Decal, title, description)

        if isinstance(asset, Asset):
            return asset
        else:
            for i in range(10):
                status = asset.fetch_operation()
                sleepy(0.5)
                if status:
                    return status
            return self.upload(file,title,description)

class Functions:
    def send_discord_message(webhook,name_value,decal_value,img_value):
        decal_value = int(decal_value)
        img_value = int(img_value)
        library_url = f"https://www.roblox.com/library/{img_value}/"

        embed_data = {
            "title": "Uploaded",
            "url": library_url,
            "fields": [
                {"name": "File Name", "value": f"{name_value}"},
                {"name": "Decal Id", "value": f"{decal_value}"},
                {"name": "Image ID", "value": f"{img_value}"}
            ],
            "color": "16777215"
        }

        payload = {"embeds": [embed_data]}

        status = requests.post(webhook, data=dumps(payload), headers={"Content-Type": "application/json"}).text
        if 'Invalid Webhook Token' in status or 'Unknown Webhook' in status:
            global WEBHOOK
            WEBHOOK = '' # Webhook doesn't exist so don't keep sending stuff

    def get_image_id(decal_id):
        if decal_id:
            url = f"https://assetdelivery.roblox.com/v1/asset/?id={decal_id}"
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    xml_data = xmltodict.parse(response.text)
                    result_url = xml_data['roblox']['Item']['Properties']['Content']['url']
                    result = result_url.split("=")[1]
                    return result
                else:
                    return "failed to get Imgid"
            except Exception as e:
                print(e)
                return "failed to get Imgid"
        else:
            return "no decal id passed???"

if '__main__' in __name__:
    ROBLOSECURITY = input('Cookie: ')

    img = Image.open("avatar_1385488.png")
    img = img.resize((500,500))


    creator = DecalClass(ROBLOSECURITY)
    try:
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

            buffer = io.BytesIO()
            rgba.save(buffer, format="PNG")
            buffer.seek(0)
            buffer.name = "File.png"
            rgba.close()

            print('uploading')
            while True: # keep uploading till one works :)
                try:
                    asset = creator.upload(buffer, "decal", f'{a}')
                    break
                except Exception as e:
                    if e == exceptions.RateLimited:
                        sleepy(2)
                        print('rate limit')

            sleepy(1)

            print(asset.id, Functions.get_image_id(asset.id))
    except KeyboardInterrupt:
        print('Exit detected, deleting api key now')
        pass

    creator.delete_key()
