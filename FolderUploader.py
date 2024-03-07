from DecalUploader import DecalClass, Functions
from rblxopencloud import exceptions, Asset
import os, threading

class ThreadShit:
    def upload(creator:DecalClass, filename:str, title:str, discription:str, barrier:threading.Barrier):
        with open(f'decals/{filename}', "rb") as file:
            barrier.wait()
            while True: # keep uploading till one works :)
                try:
                    asset = creator.upload(file, title, discription)
                    break
                except Exception as e:
                    if e == exceptions.RateLimited:
                        print('rate limit')

        if isinstance(asset, Asset):
            print(asset)
        else:
            while True:
                status = asset.fetch_operation()
                if status:
                    print(status)
                    break

        #img_id = Functions.get_image_id(asset.id)
        img_id = 'temp off'
        print(f'{filename},{asset.id},{img_id}\n')
        with open('Out2.cvs', 'a') as a:
            a.write(f'hello,{asset.id},{img_id}\n')
        # outfile.write(f'hello,{asset.id},{img_id}\n')

    def start(files: list, ROBLOSECURITY:str):
        creator = DecalClass(ROBLOSECURITY)
        barrierh = threading.Barrier(len(files)+1)
        threads = []
        for i in files:
            thread = threading.Thread(target=ThreadShit.upload, args=(creator,i,"RT","Tools", barrierh,))
            thread.start()
            threads.append(thread)
        
        barrierh.wait()

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
    files = os.listdir('decals')[:90]
    print(len(files))
    split_files = FolderFunctions.split_list_sec(files)
    ROBLOSECURITY = input("Cookie: ")

    threads = []
    for l in split_files:
        thread = threading.Thread(target=ThreadShit.start, args=(l,ROBLOSECURITY,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

