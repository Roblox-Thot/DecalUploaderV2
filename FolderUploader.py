# TODO: make/finish this

from DecalUploader import DecalClass, Functions
from rblxopencloud import exceptions
import random, os, threading
from time import sleep as sleepy

class ThreadShit:
    def start(files: list,barrier):
        barrier.wait()
        print(len(files),__import__('datetime').datetime.now())

class Functions:
    def split_list(input_list, max_length=60):
        """
        Split a list into sublists with a maximum length.
        """
        return [input_list[i:i+max_length] for i in range(0, len(input_list), max_length)]

if __name__ == '__main__':
    files = os.listdir('decals')
    split_files = Functions.split_list(files)
    barrier = threading.Barrier(len(split_files) + 1)

    threads = []
    for l in split_files:
        thread = threading.Thread(target=ThreadShit.start, args=(l,barrier,))
        thread.start()
        threads.append(thread)

    barrier.wait()

