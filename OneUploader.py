from DecalUploader.Uploader import DecalClass, Functions
from DecalUploader.Checker import Checker
from PIL import Image, ImageFilter
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
            except exceptions.PermissionDenied: # Banned
                exit()
            except exceptions.InvalidKey: # Banned/key was deleted somehow
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
        # Get image from URL if given a URL
        img_data = requests.get(image_name)
        if img_data.status_code != 200: print('failed to get img'); exit()
        img = Image.open(io.BytesIO(img_data.content))
    else:
        img = Image.open(image_name)
    
    if CONFIG['resize']:
        img = img.resize((WIDTH, LENGTH)) # Sets size exactly
    else:
        img.thumbnail((WIDTH, LENGTH)) # Fits into the size

    if OUT:
        clear = input('Clear Out.csv? (Y/N): ')
        if 'y' in clear.lower():
            with open('Out.csv','w') as clr:
                clr.write('FileName,DecalId,ImageId\n') # CSV headers
                # filename will just be the instance for this for obv reasons

    CREATOR = DecalClass(ROBLOSECURITY)
    threads_to_make = range(60)
    intensity = CONFIG['intensity']
    barrier = threading.Barrier(len(threads_to_make)+1)
    threads = []
    print('creating images/threads')

    for a in threads_to_make:
        #region making img hashes
        print(f'({a+1}/{len(threads_to_make)})',end='\r')
        rgba = img.convert("RGBA")
        data = rgba.getdata()

        newData = []
        match METHOD.lower():
            case "alpha":
                newData = [
                    (
                        item[0] + random.randint(-intensity,intensity),
                        item[1] + random.randint(-intensity,intensity), # Used fo a tiny bit of static so that you can use this more than once
                        item[2] + random.randint(-intensity,intensity),
                        255-a
                    ) for item in data
                ]

            case "static":
                # newData = [
                #     (
                #         item[0] + random.randint(-intensity, intensity),
                #         item[1] + random.randint(-intensity, intensity),
                #         item[2] + random.randint(-intensity, intensity),
                #         item[3],
                #     )
                #     for item in data
                # ]
                square_size = 2
                width, height = img.size
                static_image = Image.new('RGB', (width, height))
                
                for x in range(0, width, square_size):
                    for y in range(0, height, square_size):
                        static_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                        static_image.paste(static_color, (x, y, min(x + square_size, width), min(y + square_size, height)))

                data = Image.blend(img, static_image, 0.5)
                newData = data.getdata()

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
                        item[0] + random.randint(-intensity,intensity),
                        item[1] + random.randint(-intensity,intensity), # Used fo a tiny bit of static
                        item[2] + random.randint(-intensity,intensity),
                        item[3] - (random.randint(250,255)-round((item[0]+item[1]+item[2])/3)),
                    )
                    for item in data
                ]

            case "light":
                newData = [
                    (
                        item[0] + random.randint(-intensity,intensity),
                        item[1] + random.randint(-intensity,intensity), # Used fo a tiny bit of static
                        item[2] + random.randint(-intensity,intensity),
                        item[3] - (random.randint(250,255)-round(255-(item[0]+item[1]+item[2])/3)),
                    )
                    for item in data
                ]

            case "default": #   Sets a random pixel
                for item in data: newData.append(item)
                ran = random.randint(0, len(newData))
                newData[ran]=(random.randint(0,item[0]),random.randint(0,item[1]),random.randint(0,item[2]), item[3])

            case _: # Default to random pixel
                print('INVALID METHOD SET, DEFAULTING TO RANDOM COLOR (default) METHOD')
                for item in data: newData.append(item)
                ran = random.randint(0, len(newData))
                newData[ran]=(random.randint(0,item[0]),random.randint(0,item[1]),random.randint(0,item[2]), item[3])
        
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
