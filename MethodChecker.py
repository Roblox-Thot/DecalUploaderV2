from methods import do_method
from PIL import Image
import json

CONFIG:json = json.load(open('config.json'))
INTENSITY = CONFIG['intensity']
WIDTH:int = CONFIG['width']
LENGTH:int = CONFIG['length']
METHODS:list=[
    "alpha",
    "static",
    "tstatic",
    "shadow",
    "light",
    "test",
    "test2",
    "default"
]

if __name__ == '__main__':
    test_image = Image.open('a.jpg')

    if CONFIG['resize']:
        test_image = test_image.resize((WIDTH, LENGTH)) # Sets size exactly
    else:
        test_image.thumbnail((WIDTH, LENGTH)) # Fits into the size

    for method in METHODS:
        rgba = test_image.convert("RGBA")
        print(f'> Making image with method {method}')
        new_data = do_method(method, rgba, intensity=INTENSITY)
        rgba.putdata(new_data)
        rgba.show(f'Test {method}')
        rgba.close()
        input("enter to continue")