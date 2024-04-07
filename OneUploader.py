from DecalUploader.Uploader import DecalClass, Functions
from DecalUploader.Checker import Checker
from PIL import Image
from rblxopencloud import exceptions
from time import sleep, time
import random, io, threading, requests, json

CONFIG:json = json.load(open('config.json'))
OUT:bool = CONFIG['save decals'] # Save decals/imgs to out.csv
WEBHOOK:str = CONFIG['webhook']
TITLE:str = CONFIG['title']
DESCRIPTION:str = CONFIG['description']

# Image configs
METHOD:bool = CONFIG['method']
WIDTH:int = CONFIG['width']
LENGTH:int = CONFIG['length']

class DaThreads:
    def run(thread_num:int, creator:DecalClass, barrier:threading.Barrier, buffer:io.BytesIO) -> None:
        # sourcery skip: instance-method-first-arg-name

        barrier.wait()

        while True: # keep uploading till one works :)
            try:
                asset = creator.upload(buffer, TITLE, DESCRIPTION)
                break
            except exceptions.RateLimited:
                sleep(2)
                print('rate limit')
            except exceptions.PermissionDenied | exceptions.InvalidKey:
                exit()
            except Exception:
                sleep(2)

        if asset is not None:
            img_id = Functions.get_image_id(asset.id)
            # print(f'{asset.id=} {img_id=}')
            if OUT:
                with open('Out.csv','a') as f:
                    f.write(f'#{thread_num},{asset.id},{img_id}\n')
            Checker(asset.id, img_id, WEBHOOK)

if '__main__' in __name__:
    random.seed(time())
    ROBLOSECURITY = input('Cookie: ')

    image_name = input('Image: ').replace('"', '')
    if image_name.lower().startswith('http'):
        img_data = requests.get(image_name)
        if img_data.status_code != 200: print('failed to get img'); exit()
        img = Image.open(io.BytesIO(img_data.content))
    else:
        img = Image.open(image_name)
    # img.thumbnail((WIDTH, LENGTH))
    img = img.resize((WIDTH, LENGTH))

    if OUT:
        clear = input('Clear Out.csv? (Y/N): ')
        if 'y' in clear.lower():
            with open('Out.csv','w') as clr:
                clr.write('FileName,DecalId,ImageId\n') # CSV headers
                # filename will just be the instance for this for obv reasons

    CREATOR = DecalClass(ROBLOSECURITY)
    threads_to_make = range(60)
    barrier = threading.Barrier(len(threads_to_make)+1)
    threads = []
    print('creating images/threads')
    for a in threads_to_make:
        #region making img hashes
        print(f'({a}/{len(threads_to_make)})')
        rgba = img.convert("RGBA")
        data = rgba.getdata()

        newData = []
        intensity=50

        match METHOD.lower():
            case "alpha":
                newData = [
                    (item[0], item[1], item[2], 255-a) for item in data]

            case "static":
                newData = [
                    (
                        item[0] + random.randint(-intensity, intensity),
                        item[1] + random.randint(-intensity, intensity),
                        item[2] + random.randint(-intensity, intensity),
                        item[3],
                    )
                    for item in data
                ]

            case "tstatic":
                newData = [
                    (
                        item[0],
                        item[1],
                        item[2],
                        item[3] - random.randint(0, intensity),
                    )
                    for item in data
                ]

            case "shadow":
                newData = [
                    (
                        item[0] + random.randint(-1,1),
                        item[1] + random.randint(-1,1), # Used fo a tiny bit of static
                        item[2] + random.randint(-1,1),
                        item[3] - (random.randint(250,255)-round((item[0]+item[1]+item[2])/3)),
                    )
                    for item in data
                ]

            case "light":
                newData = [
                    (
                        item[0] + random.randint(-1,1),
                        item[1] + random.randint(-1,1), # Used fo a tiny bit of static
                        item[2] + random.randint(-1,1),
                        item[3] - (random.randint(250,255)-round(255-(item[0]+item[1]+item[2])/3)),
                    )
                    for item in data
                ]

            case _: # Default to random pixel
                for item in data:
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
        print('Failed to delete key, you were prob banned/warned')
