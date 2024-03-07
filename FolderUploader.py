from DecalUploader import DecalClass, Functions
from rblxopencloud import exceptions
import os, threading
from time import sleep as sleepy

class ThreadShit:
    def upload(creator:DecalClass, filename:str, title:str, discription:str, outfile, barrier:threading.Barrier):
        barrier.wait()
        print(filename)
        with open(f'decals/{filename}', "rb") as file:
            while True: # keep uploading till one works :)
                try:
                    asset = creator.upload(file, title, discription)
                    break
                except Exception as e:
                    if e == exceptions.RateLimited:
                        sleepy(1)
                        print('rate limit')

        img_id = Functions.get_image_id(asset.id)
        outfile.write(f'{filename},{asset.id},{img_id}\n')

    def start(files: list, ROBLOSECURITY:str, outfile):
        creator = DecalClass(ROBLOSECURITY)
        barrierh = threading.Barrier(len(files)+1)
        threads = []
        for i in files:
            thread = threading.Thread(target=ThreadShit.upload, args=(creator,i,"RT","Tools",outfile, barrierh,))
            thread.start()
            threads.append(thread)
        
        barrierh.wait()

        for thread in threads:
            thread.join()

class FolderFunctions:
    def split_list(input_list, max_length=60):
        """
        Split a list into sublists with a maximum length.
        """
        return [input_list[i:i+max_length] for i in range(0, len(input_list), max_length)][:6]

if __name__ == '__main__':
    ROBLOSECURITY = input("Cookie: ")
    files = os.listdir('decals')
    split_files = FolderFunctions.split_list(files)
    outfile = open("Outa.csv",'w')
    outfile.write('FileName,DecalId,ImageId\n')

    threads = []
    for l in split_files:
        thread = threading.Thread(target=ThreadShit.start, args=(l,ROBLOSECURITY,outfile,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    outfile.close()

