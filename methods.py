
from PIL import Image
import random

def setupRand(intensity):
    def randy():
        return random.randint(-intensity,intensity)
    return randy

#TODO: think about moving each method into a function to clean up
def do_method(METHOD:str,intensity:int,rgba):  # sourcery skip: extract-duplicate-method, low-code-quality, use-itertools-product
    newData = []
    rand = setupRand(intensity)
    match METHOD.lower():
        case "alpha":
            newData = [
                (
                    item[0] + rand(),
                    item[1] + rand(), # Used fo a tiny bit of static so that you can use this more than once
                    item[2] + rand(),
                    255-a
                ) for item in data
            ]

        case "static": # WIP new method
            # newData = [
            #     (
            #         item[0] + random.randint(-intensity, intensity),
            #         item[1] + random.randint(-intensity, intensity),
            #         item[2] + random.randint(-intensity, intensity),
            #         item[3],
            #     )
            #     for item in data
            # ]
            square_size = 3
            width, height = rgba.size
            static_image = Image.new('RGBA', (width, height))
            
            for x in range(0, width, square_size):
                for y in range(0, height, square_size):
                    static_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                    static_image.paste(static_color, (x, y, min(x + square_size, width), min(y + square_size, height)))

            data = Image.blend(rgba, static_image, 255/intensity)
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
                    item[0] + rand(),
                    item[1] + rand(), # Used fo a tiny bit of static
                    item[2] + rand(),
                    item[3] - (random.randint(250,255)-round((item[0]+item[1]+item[2])/3)),
                )
                for item in data
            ]

        case "light":
            newData = [
                (
                    item[0] + rand(),
                    item[1] + rand(), # Used fo a tiny bit of static
                    item[2] + rand(),
                    item[3] - (random.randint(250,255)-round(255-(item[0]+item[1]+item[2])/3)),
                )
                for item in data
            ]

        case "test": # WIP filter method
            image = rgba
            width, height = image.size
            for y in range(height):
                for x in range(width):
                    r, g, b, a = image.getpixel((x, y))
                    r+=rand();g+=rand();b+=rand()
                    if y % 2 == 0: b = 0
                    if y % 3 == 0 or x % 3 == 0: a = 0
                    if x % 2 != 0:
                        image.putpixel((x, y), (0,g,b,a))
                    else:
                        image.putpixel((x, y), (r,0,b,a))
            newData = image.getdata()

        case "test2": # WIP filter method
            image = rgba
            width, height = image.size
            count = 0
            for y in range(height):
                for x in range(width):
                    r, g, b, a = image.getpixel((x, y))
                    r+=rand();g+=rand();b+=rand()
                    count+=1
                    if count == 1:
                        g,b = 0,0
                    elif count == 2:
                        r,b = 0,0
                    elif count == 3:
                        r,g = 0,0
                    else:
                        r,g,b=0,0,0
                        count=0
                        
                    if y % 4 == 0 or x % 4 == 0: a = round((r+g+b)/3)
                    image.putpixel((x, y), (r,g,b,a))
            newData = image.getdata()

        case "default": #   Sets a random pixel
            for item in data: newData.append(item)
            ran = random.randint(0, len(newData))
            newData[ran]=(random.randint(0,item[0]),random.randint(0,item[1]),random.randint(0,item[2]), item[3])

        case _: # Default to random pixel
            print('INVALID METHOD SET, DEFAULTING TO RANDOM COLOR (default) METHOD')
            for item in data: newData.append(item)
            ran = random.randint(0, len(newData))
            newData[ran]=(random.randint(0,item[0]),random.randint(0,item[1]),random.randint(0,item[2]), item[3])
    return newData