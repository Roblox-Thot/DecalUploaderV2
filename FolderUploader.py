from DecalUploader import DecalClass, Functions
from rblxopencloud import exceptions
import os, threading, time,re

class ThreadShit:
    def upload(creator:DecalClass, filename:str, title:str, discription:str, barrier:threading.Barrier):
        with open(f'decals/{filename}', "rb") as file:
            barrier.wait()
            while True: # keep uploading till one works :)
                try:
                    asset = creator.upload(file, title, discription)
                    break
                except exceptions.RateLimited:
                    time.sleep(2)
                    print('rate limit')
                except:
                    #SOMETHING FUCKING SUCKS IG
                    time.sleep(2)

        img_id = Functions.get_image_id(asset.id)
        #img_id = 'temp off'
        clean_filename = re.sub(r'[^\x00-\x7F]+','#',filename) # no emojis
        clean_filename = clean_filename.replace(',',' ') # no comma
        print(filename,asset.id,img_id)
        with open('Out.csv', 'a') as a:
            a.write(f'{filename},{asset.id},{img_id}\n')

    def start(files: list, ROBLOSECURITY:str):
        creator = DecalClass(ROBLOSECURITY)
        barrier = threading.Barrier(len(files)+1)
        threads = []
        for i in files:
            thread = threading.Thread(target=ThreadShit.upload, args=(creator,i,"Decal","Decal Tools", barrier,))
            thread.start()
            threads.append(thread)
        
        barrier.wait()

        for thread in threads:
            thread.join()

class FolderFunctions:
    def split_list_len(input_list, max_length=60):
        """
        Split a list into sublists with a maximum length.
        """
        return [input_list[i:i+max_length] for i in range(0, len(input_list), max_length)][:6]
    
    def split_list_sec(lst, num_sections=6):
        avg_length = len(lst) // num_sections
        remainder = len(lst) % num_sections
        sections = []
        start = 0
        for i in range(num_sections):
            length = avg_length + 1 if i < remainder else avg_length
            end = start + length
            sections.append(lst[start:end])
            start = end
        return sections

if __name__ == '__main__':
    files = os.listdir('decals')[:100]
    print(len(files))
    split_files = FolderFunctions.split_list_sec(files)
    print(len(split_files))
    print(len(split_files[0]))
    ROBLOSECURITY = input("Cookie: ")
    clear = input('Clear Out.csv? (Y/N): ')
    if 'y' in clear.lower():
        with open('Out.csv','w') as clr:
            clr.write('FileName,DecalId,ImageId\n') # CSV headers
            # filename will just be the insance for this for obv reasons


    threads = []
    for l in split_files:
        thread = threading.Thread(target=ThreadShit.start, args=(l,ROBLOSECURITY,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

