from DecalUploader.Uploader import DecalClass, Functions
from DecalUploader.Checker import Checker
from PIL import Image
from rblxopencloud import exceptions
from time import sleep, time
from methods import do_method
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

        # TODO: Add random to config
        # list_thingy = string.ascii_letters+string.digits
        # title,description =random.choice(list_thingy),random.choice(list_thingy)
        barrier.wait()

        while True: # keep uploading till one works :)
            try:
                asset = creator.upload(buffer, TITLE,DESCRIPTION)
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

# sourcery skip: use-itertools-product
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
        # TODO: add to config
        #if random.randint(0,1) == 1: rgba.transpose(Image.FLIP_LEFT_RIGHT)

        #METHOD = random.choice(["alpha","static","tstatic","shadow","light","test","test2"])
        #print(METHOD)
        newData = do_method(METHOD,rgba,a,intensity)
        
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
