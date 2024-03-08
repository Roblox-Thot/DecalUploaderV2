from rblxopencloud import User, AssetType
import requests, random, string
from time import sleep as sleepy
import xmltodict
from json import dumps

class DecalClass:
    def __init__(self, cookie:str) -> None:
        self.cookie = cookie
        self.creator = None
        self.keyId = None
        self.apiKey = None
        self.__get_api_key__()
        pass

    def __get_api_key__(self):
        """Creates a API key and sets the self vers required"""
        if self.apiKey: return self.apiKey

        payload = {"cloudAuthUserConfiguredProperties": {"name": ''.join(random.choices(string.digits, k=2)),"description": "","isEnabled": True,"allowedCidrs": ["0.0.0.0/0"],"scopes": [{"scopeType": "asset","targetParts": ["U"],"operations": ["read", "write"]}]}}

        headers = {
            "content-type": "application/json",
            "X-Csrf-Token": requests.post('https://auth.roblox.com/v1/login', cookies={'.ROBLOSECURITY': self.cookie}).headers['x-csrf-token']
        }

        response = requests.post("https://apis.roblox.com/cloud-authentication/v1/apiKey", json=payload, headers=headers, cookies={'.ROBLOSECURITY': self.cookie}).json()
        #print(response)
        self.apiKey = response['apikeySecret']
        self.keyId = response['cloudAuthInfo']['id']
        self.creator = User(requests.get('https://www.roblox.com/mobileapi/userinfo',cookies={'.ROBLOSECURITY':self.cookie}).json()['UserID'],
                                self.apiKey)

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

        sleepy(5)

        while True:
            try:
                status = asset.fetch_operation()
                if status:
                    return status
            except:
                sleepy(0.5)
                pass
            sleepy(0.2)

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

if __name__ == '__main__':
    input('ok so like uhhhhh um so i want to tell you uhhhh that uhhh wait a sec uhh ummm like so um i just wanted to tell you that uhhhhhh so um like what um uhhhhhhhhhhhhhhhh uhhhh oh um so i just hmmmm uhhh ummmm like ummmm i\'ve been uhhhhhhhhhhhhhhhhhhhhhh so like it\'s that um uhh oh the thing is that ummmmmm ahhhhhh it\'s because uhhhhhhhhhh fuckin ummmmmm can I like uhhhhhhhh just um wait just one second uhhhhh ok so like i wanted to uhhhhhhh so the thing is that what i wanted to tell you is uhhhhhhhhh i just ummmmm so uhhhhhhhhh like ummmm hmmmmm uhhhh i need to uhhhh what i wanted to tell you is ahhh like uh so um it\'s that ummmm i just had a uhhhhhhhhhhh well it\'s that ummmmmmmm hmmmm ah yeah it\'s that i uhhhhh hmmmm well i mean that uhhhhhhhhhhhhhhhhhhhhhh it\'s just that i wanted to tell you that uhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh you don\' run this file')
