from DecalUploader import DecalClass, Functions
from PIL import Image
from rblxopencloud import exceptions
import random, io, threading
from time import sleep as sleepy

class DaThreads:
    def run(creator,barrier,buffer) -> None:

        barrier.wait()

        # while True: # keep uploading till one works :)
        try:
            asset = creator.upload(buffer, "decal", 'decal')
            # break
        # except exceptions.RateLimited:
        #     sleepy(1)
        #     #print('rate limit')
        except Exception as e:
            print('erorr ext',e)
            exit()

        if asset:
            img_id = Functions.get_image_id(asset.id)
            print(asset.id, img_id)
            outfile = open('Out.csv','a')
            outfile.write(f'{a},{asset.id},{img_id}\n')
            outfile.close()

if '__main__' in __name__:
    # ROBLOSECURITY = input('Cookie: ')
    ROBLOSECURITY = '_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|_F76F5D89D5D79E00A9AB8F3E754701A5746BF7B26C5FBA672639BAD4EC11CAA2B3EFE531417B865D2FDB8D96FC1D0B7D18C19F5390579FD39E2ED82A212A64651F5BB83E2FA6795B3F59C46B6E5178070102CCA46F2F7BB78971910E5FCB80A034D4E4481B40FAB372E4340088CFFA2E11203881BCDC6C39F4C848A6A80E884F18696C3736E40E685168B826E409853BAE2DAACCB9A1F3F2D2886CC6B09F0A02AC108742DFCB7F847DBD8110A0C21C4DF97AE5D752A2BAF5651DDBD03FF40AB0C942FC7A6AE7667C1628999081D587F751D1631B4383460E4B024FBE7482EE22E7596D398A1DC70A1407FB6B7ACF80B3261B090B65082E95D927CCBA06FBD212BD8D2603BA549566D836F378976CF66463E22AF2192145E2CD3E327CBE17C796ADE83ABD4B5D4517F302C3A448A066EE5AF60ADB68A6C6DA442FC0A1F01A04F2AAD1FE19400DD41CA6BBECF373EFCCFA8B3551D30C76A885ADD5F938760E051DAE9B46C968B016E5E804C96BD930B2D7221B51B512812CF6175E730D37E3811488AFC915E38287971EE509DF3843F4376B2B4CCE39A7F7083612F921DA41E09F1099B5FCB26DF9C6055A0D33F67EFAADA347F3CED7903438571F7DB73D3221267110F7001FE2721A2416C282D1F8C4FBFC3FC0196EE576AC1DC20E569457470CC53569B4468875C3CF7A295258D33BBCF35A3D7C439D23EC12AB616CEF737E73DB0303AE4857C031EFA7E243AB6473B0AF2868E6A9BA2F3480A260A621EB27F3791E1670551EC0CFE029A7E1A9753F750A79AB7ED5339B0DB230D421372455B962F3755C00C0988A95C1F3ED39C68B05A78D8F0BDB7B968AAFAB07348F0B81BE74616B320746A0ED9BC020F1963BC52C4F0EE5EB8795733C7FF5C4F67920B8C0B305C27A9ACB5C30F8DB82C800BD00A76098CFB9DA7DB443801D704E55EEEF543DCA46A4A01CBC9CD5E16E32B74195301AAF07E584CCF1BB1DF6B341CFC94E68A7471D01B975A286B0A49959CFD3D2E550E562AEBC0D9074C266EA0FB73657CB1D0B37AD0901815AEB5472BB5A0CA60635F03B98'

    file = input('Image: ').replace('"', '')
    img = Image.open(file)
    img.thumbnail((420,420))

    clear = input('Clear Out.csv? (Y/N): ')
    if 'y' in clear.lower():
        with open('Out.csv','w') as clr:
            clr.write('FileName,DecalId,ImageId\n') # CSV headers
            # filename will just be the insance for this for obv reasons

    CREATOR = DecalClass(ROBLOSECURITY)
    threads2make = range(60)
    barrier = threading.Barrier(len(threads2make)+1)
    threads = []
    print('creating images/threads')
    for a in threads2make:
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

        thread = threading.Thread(target=DaThreads.run, args=(CREATOR,barrier,buffer,))
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
    except:
        print('erm i think you were banned, kinda awkward')
