from rblxopencloud import User, AssetType, Asset, exceptions
import requests, random, string
from time import sleep
import xmltodict

class DecalClass:
    def __init__(self, cookie:str, asset_type:AssetType = AssetType.Decal):
        self.cookie = cookie
        self.creator = None
        self.keyId = None
        self.api_key = None
        self.asset_type = asset_type
        self.__get_api_key__()

    def __get_api_key__(self) -> None:
        """Creates a API key and sets the self vers required"""
        if self.api_key: return self.api_key

        payload = {"cloudAuthUserConfiguredProperties": {"name": ''.join(random.choices(string.digits, k=2)),"description": "","isEnabled": True,"allowedCidrs": ["0.0.0.0/0"],"scopes": [{"scopeType": "asset","targetParts": ["U"],"operations": ["read", "write"]}]}}

        headers = {
            "content-type": "application/json",
            "X-Csrf-Token": requests.post('https://auth.roblox.com/v1/login', cookies={'.ROBLOSECURITY': self.cookie}).headers['x-csrf-token']
        }

        response = requests.post("https://apis.roblox.com/cloud-authentication/v1/apiKey", json=payload, headers=headers, cookies={'.ROBLOSECURITY': self.cookie}).json()

        self.api_key = response['apikeySecret']
        self.keyId = response['cloudAuthInfo']['id']
        self.creator = User(requests.get('https://www.roblox.com/mobileapi/userinfo',cookies={'.ROBLOSECURITY':self.cookie}).json()['UserID'],
                                self.api_key)

    def delete_key(self) -> None:
        """Deletes the API key"""
        headers = {
            "content-type": "application/json",
            "X-Csrf-Token": requests.post('https://auth.roblox.com/v1/login', cookies={'.ROBLOSECURITY': self.cookie}).headers['x-csrf-token']
        }
        
        requests.delete(f'https://apis.roblox.com/cloud-authentication/v1/apiKey/{self.keyId}', headers=headers, cookies={'.ROBLOSECURITY': self.cookie}).json()

    def upload(self, file:bytes, title:str, description:str) -> Asset|None:
        """Attempts to upload decal

        Args:
            file (bytes): file data
            title (str): title of decal
            description (str): description of decal

        Returns:
            Asset: the asset of the decal
        """
        asset = self.creator.upload_asset(file, self.asset_type, title, description)

        sleep(5)

        while True:
            try:
                if status := asset.fetch_operation():
                    return status
            except exceptions.InvalidKey: #TODO: if invalid key try and check for a ban/warn
                return None
            except Exception:
                sleep(0.5)
            sleep(0.2)

class Functions:
    def get_image_id(decal_id:int|str) -> str:
        # sourcery skip: instance-method-first-arg-name
        if not decal_id:
            return "no decal id passed???"
        url = f"https://assetdelivery.roblox.com/v1/asset/?id={decal_id}"
        try:
            response = requests.get(url)
            if response.status_code != 200:
                return "failed to get Imgid"
            xml_data = xmltodict.parse(response.text)
            result_url = xml_data['roblox']['Item']['Properties']['Content']['url']
            return result_url.split("=")[1]
        except Exception as e:
            print(e)
            sleep(random.randint(0.1,1))
            return Functions.get_image_id(decal_id)

if __name__ == '__main__':
    input('you don\' run this file')
