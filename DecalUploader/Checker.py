import requests
from time import sleep as wait

class Checker:
    def __init__(self, decal_id:int, image_id:int, webhook:str=None) -> None:
        if webhook.strip()=='': return None
        self.webhook = webhook
        self.decal_id = decal_id
        self.image_id = image_id
        self.image_url = None
        
        while True:
            try:
                match self.get_asset_state():
                    case 'Completed':
                        print(f'{decal_id} | {image_id} has been accepted')
                        self.send_webhook()
                        break
                    case 'Blocked':
                        print(f'{decal_id} | {image_id} has been denied')
                        break
                    case _ as status:
                        if status != None: print(f'{decal_id} | {image_id} is {status}')
                        pass
            except: # just incase
                pass
            wait(0.2) # eepy

    def get_asset_state(self) -> str:
        """Gets the current image state

        Returns:
            str: image state
        """        
        url = f'https://thumbnails.roblox.com/v1/assets?assetIds={self.image_id}&returnPolicy=PlaceHolder&size=420x420&format=Png&isCircular=false'
        
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            if 'data' in data and len(data['data']) > 0:
                state = data['data'][0].get('state')
                if state == 'Completed': self.image_url = data['data'][0].get('imageUrl')
                return state
        return None

    def send_webhook(self) -> None:
        """Sends webhook msg

        Args:
            img_url (str): decal image
        """        
        embed_data = {
            'title': f'Decal accepted',
            'url': f'https://www.roblox.com/library/{self.decal_id}',
            'image': {'url': self.image_url},
            'fields': [
                {'name': 'Decal ID', 'value': f'||{self.decal_id}||'},
                {'name': 'Image ID', 'value': f'||{self.image_id}||'}
            ],
            'color': '16777215'
        }

        payload = {'embeds': [embed_data]}

        requests.post(self.webhook, json=payload)

if '__main__' in __name__:
    input('ok so like uhhhhh um so i want to tell you uhhhh that uhhh wait a sec uhh ummm like so um i just wanted to tell you that uhhhhhh so um like what um uhhhhhhhhhhhhhhhh uhhhh oh um so i just hmmmm uhhh ummmm like ummmm i\'ve been uhhhhhhhhhhhhhhhhhhhhhh so like it\'s that um uhh oh the thing is that ummmmmm ahhhhhh it\'s because uhhhhhhhhhh fuckin ummmmmm can I like uhhhhhhhh just um wait just one second uhhhhh ok so like i wanted to uhhhhhhh so the thing is that what i wanted to tell you is uhhhhhhhhh i just ummmmm so uhhhhhhhhh like ummmm hmmmmm uhhhh i need to uhhhh what i wanted to tell you is ahhh like uh so um it\'s that ummmm i just had a uhhhhhhhhhhh well it\'s that ummmmmmmm hmmmm ah yeah it\'s that i uhhhhh hmmmm well i mean that uhhhhhhhhhhhhhhhhhhhhhh it\'s just that i wanted to tell you that uhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh you don\' run this file')
