from DecalUploader.Uploader import DecalClass, Functions
from DecalUploader.Checker import Checker
from rblxopencloud import exceptions
import os, threading, time, re, json

CONFIG = json.load(open('config.json'))
OUT:bool = CONFIG['save decals'] # Save decals/imgs to out.csv
WEBHOOK:str = CONFIG['webhook']
TITLE:str = CONFIG['title']
DESCRIPTION:str = CONFIG['description']

class ThreadShit:
    def upload(creator:DecalClass, filename:str, barrier:threading.Barrier) -> None:
        # sourcery skip: extract-method, instance-method-first-arg-name

        #TODO: use PIL and make images the W&L from config
        with open(f'decals/{filename}', "rb") as file:
            barrier.wait()
            while True: # keep uploading till one works :)
                try:
                    asset = creator.upload(file, TITLE, DESCRIPTION)
                    break
                except exceptions.RateLimited:
                    time.sleep(2)
                    print('rate limit')
                except Exception:
                    #SOMETHING FUCKING SUCKS IG
                    time.sleep(2)
        
        if asset is not None:
            img_id = Functions.get_image_id(asset.id)
            # img_id = 'temp off'
            clean_filename = re.sub(r'[^\x00-\x7F]+','#',filename) # no emojis
            clean_filename = clean_filename.replace(',',' ') # no comma
            # print(f'{filename} {asset.id=} {img_id=}')
            if OUT:
                with open('Out.csv', 'a') as a:
                    a.write(f'{clean_filename},{asset.id},{img_id}\n')
            Checker(asset.id, img_id, WEBHOOK)

    def start(files: list, ROBLOSECURITY:str) -> None:
        # sourcery skip: instance-method-first-arg-name
        creator = DecalClass(ROBLOSECURITY)
        barrier = threading.Barrier(len(files)+1)
        threads = []
        for i in files:
            thread = threading.Thread(target=ThreadShit.upload, args=(creator,i,barrier,))
            thread.start()
            threads.append(thread)
        
        barrier.wait()

        for thread in threads:
            thread.join()

class FolderFunctions:
    def split_list_len(input_list:list, max_length:int=60) -> list:
        # sourcery skip: instance-method-first-arg-name
        """
        Split a list into sublists with a maximum length.
        """
        return [input_list[i:i+max_length] for i in range(0, len(input_list), max_length)][:6]
    
    def split_list_sec(input_list:list, num_sections:int=6) -> list:
        # sourcery skip: instance-method-first-arg-name
        avg_length, remainder = divmod(len(input_list), num_sections)
        sections = []
        start = 0
        for i in range(num_sections):
            length = avg_length + 1 if i < remainder else avg_length
            end = start + length
            sections.append(input_list[start:end])
            start = end
        return sections

if __name__ == '__main__':
    files = os.listdir('decals')[:100] # i've only ever gotten 100 max
    print('Files in decals:',len(files))
    split_files = FolderFunctions.split_list_sec(files)
    print('Thread to be made:',len(split_files))
    print('Files per thread(max ~60):',len(split_files[0]))
    ROBLOSECURITY = input("Cookie: ")
    
    if OUT:
        clear = input('Clear Out.csv? (Y/N): ')
        if 'y' in clear.lower():
            with open('Out.csv','w') as clr:
                clr.write('FileName,DecalId,ImageId\n') # CSV headers

    threads = []
    for l in split_files:
        thread = threading.Thread(target=ThreadShit.start, args=(l,ROBLOSECURITY,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

