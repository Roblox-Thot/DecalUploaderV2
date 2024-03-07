from DecalUploader import DecalClass, Functions
from PIL import Image
from rblxopencloud import exceptions
import random, io
from time import sleep as sleepy

if '__main__' in __name__:
    ROBLOSECURITY = input('Cookie: ')

    img = Image.open("avatar_1385488.png")
    img = img.resize((500,500))

    creator = DecalClass(ROBLOSECURITY)
    try:
        for a in range(0,60):
            rgba = img.convert("RGBA")
            datas = rgba.getdata()

            newData = []

            for item in datas:
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

            print('uploading')
            while True: # keep uploading till one works :)
                try:
                    asset = creator.upload(buffer, "decal", f'{a}')
                    break
                except Exception as e:
                    if e == exceptions.RateLimited:
                        sleepy(2)
                        print('rate limit')

            sleepy(1)

            print(asset.id, Functions.get_image_id(asset.id))
    except KeyboardInterrupt:
        print('Exit detected, deleting api key now')
        pass

    creator.delete_key()
