import os
import requests
from io import BytesIO
from pyzbar import pyzbar
from PIL import Image,ImageEnhance
 
 
def get_ewm(img_adds):
    """ Img_adds: QR code address (can be a url or a local address """
    if os.path.isfile(img_adds):
        # Load the QR code image locally
        img = Image.open(img_adds)
 
    txt_list = pyzbar.decode(img)
 
    for txt in txt_list:
        barcodeData = txt.data.decode("utf-8")
        print(barcodeData)
 
if __name__ == '__main__':
    # Parse QR code
    get_ewm('QRcode/bilibili.png')