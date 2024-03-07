"""'''''''''''''''''''''''''''''''''''''''''''''''''''''
cccccccccccccccccccccccccccccccccccccccccccccccccccccccc
:::::::::::::::::::::::::c:::::::::::::::c:::cccc:::::::
ccccccccccccccccccccccccccccccc:,'',,;:ccccccccccccccccc
cccccccccccccccccccccccccccc:;'......';ccccccccccccccccc
cccccccccccccccccccccccccc;'........'',:cccccccccccccccc
ccccccclllccccccccccccccl:. ..........',:ccccccccccccccc
cccccllccccllllcccccccccl:. . ......';;;clcccccllllcclcc
clllllllllcc:;,'''',,,'',,.........':c;;llccclccllllcllc
lllllllc:,'.........................,;.,cccclllcllllllcc
llllll:'.........................''',::lxdlllllooddollll
llll:'.............................'';cdkOxollloodxxdoll
olc;.........  ...... ..............'',coddollccclolclol
o:...........            ...........''';:clllc::cllcclll
l,..........,,.           ...............,cllolccccllloo
l,. ......;lol,.....      ...............,coooollloooool
o:. ......,col,..........  ..............,::;;:clooooooo
ol,. ......;lc...............................;cooooooooo
ddo,. .....',...............................,loodddddddd
oool;...,,................................':looooooooooo
oooool;,,..... .........................;loddddddddddodd
oodool:;;......................  ....,:odddddddxxxxxxxxx
::::::ccl:. ........................cddddddddddddddddddd
llllllloll;......  ................'okkkkkkkkkkkkkkkkkxx
ccccc::::::::;;:,..  .....'',,,,,'.,oOOOOOO0000000000OO0
::::::::::::::::::,'''',;:cclllollllodxxkkkkOOOOOOOO00XN
::::::;;;;;;;;;;;::::ccccoooooooooollloooddoddxxkxxxxdkK
ccccccc::;;;;;;;;:clooooooooodooooooddddddoodddxxdddolco
cccccccccc::::;;:clooooddoooododdooodddddddddddddodolcc:
                            Once
'''''''''''''''''''''''''''''''''''''''''''''''''''''"""

from DecalUploader import DecalClass, Functions
from PIL import Image
from rblxopencloud import exceptions
import random, io
from time import sleep as sleepy

if '__main__' in __name__:
    ROBLOSECURITY = input('Cookie: ')

    img = Image.open(input('Image: ').replace('"', ''))
    img = img.resize((420,420))

    clear = input('Clear Out.csv? (Y/N): ')
    if 'y' in clear.lower():
        with open('Out.csv','w') as clr:
            clr.write('FileName,DecalId,ImageId\n') # CSV headers
            # filename will just be the insance for this for obv reasons

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
                        sleepy(1)
                        print('rate limit')
            img_id = Functions.get_image_id(asset.id)
            print(asset.id, img_id)
            
            with open('Out.csv','a') as out:
                out.write(f'{a},{asset.id},{img_id}\n')
    except KeyboardInterrupt:
        print('Exit detected, deleting api key now')
        pass

    try:
        creator.delete_key()
    except:
        print('erm i think you were banned, kinda awkward')
