from DecalUploader.Uploader import DecalClass, Functions
from DecalUploader.Checker import Checker
from PIL import Image
from rblxopencloud import exceptions
from time import sleep as sleepy
import random, io, threading, requests, json

CONFIG:json = json.load(open('config.json'))
OUT:bool = CONFIG['save decals'] # Save decals/imgs to out.csv
STATIC:bool = CONFIG['static'] # Static method
WEBHOOK:str = CONFIG['webhook']
TITLE:str = CONFIG['title']
DESCRIPTION:str = CONFIG['description']

class DaThreads:
    def run(thread_num:int, creator:DecalClass, barrier:threading.Barrier, buffer:io.BytesIO) -> None:
        # sourcery skip: instance-method-first-arg-name

        barrier.wait()

        while True: # keep uploading till one works :)
            try:
                asset = creator.upload(buffer, TITLE, DESCRIPTION)
                break
            except exceptions.RateLimited:
                sleepy(2)
                print('rate limit')
            except Exception:
                sleepy(2)

        if asset:
            img_id = Functions.get_image_id(asset.id)
            print(asset.id, img_id)
            if OUT:
                with open('Out.csv','a') as f:
                    f.write(f'#{thread_num},{asset.id},{img_id}\n')
            Checker(asset.id, img_id, WEBHOOK)

if '__main__' in __name__:
    ROBLOSECURITY = input('Cookie: ')

    image_name = input('Image: ').replace('"', '')
    if image_name.lower().startswith('http'):
        img_data = requests.get(image_name)
        if img_data.status_code != 200: print('failed to get img'); exit()
        img = Image.open(io.BytesIO(img_data.content))
    else:
        img = Image.open(image_name)
    img.thumbnail((400,400))

    if OUT:
        clear = input('Clear Out.csv? (Y/N): ')
        if 'y' in clear.lower():
            with open('Out.csv','w') as clr:
                clr.write('FileName,DecalId,ImageId\n') # CSV headers
                # filename will just be the instance for this for obv reasons

    CREATOR = DecalClass(ROBLOSECURITY)
    threads2make = range(60)
    barrier = threading.Barrier(len(threads2make)+1)
    threads = []
    print('creating images/threads')
    for a in threads2make:
        #region making img hashes
        rgba = img.convert("RGBA")
        data = rgba.getdata()

        newData = []

        for item in data:
            newData.append(item)

        if not STATIC:
            # Picks random pixel to replace
            ran = random.randint(0, len(newData))
            # Sets the color
            newData[ran]=(
                random.randint(0,item[0]),
                random.randint(0,item[1]),
                random.randint(0,item[2]), item[3])

        else:
            intensity=20
            newData=[
                (item[0]+random.randint(-intensity, intensity),
                item[1]+random.randint(-intensity, intensity),
                item[2]+random.randint(-intensity, intensity),
                item[3])for item in data
            ]

        rgba.putdata(newData)

        buffer = io.BytesIO()
        rgba.save(buffer, format="PNG")
        buffer.seek(0)
        buffer.name = "File.png"
        rgba.close()
        #endregion

        thread = threading.Thread(target=DaThreads.run, args=(a,CREATOR,barrier,buffer,))
        thread.start()
        threads.append(thread)
        
    barrier.wait()
    print('uploading')

    for thread in threads:
        thread.join()
    print('upload finished')
    
    try:
        CREATOR.delete_key()
        print('API key has now ben deleted')
    except Exception:
        print('erm i think you were banned, kinda awkward')
