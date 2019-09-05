import glob
import os

from PIL import Image

# print(glob.glob(r'D:\VideoPhotos\sign\*.jpg'))
path = 'G:\dzt\资料\交警\备份\梭梭树\\50.45.11.234'
images = glob.glob(path + r"\*.jpg")
for img in images:
    print(img)
    im = Image.open(img)
    print(im.format, im.size, im.mode)
    # 原取证图 3840 * 2656
    size = 1920, 1328
    name = os.path.join(path, img)
    im.thumbnail(size)
    rgb_im = im.convert('RGB')
    rgb_im.save(name, 'JPEG')
    print(im.format, im.size, im.mode)


