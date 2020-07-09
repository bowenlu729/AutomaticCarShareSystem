import qrcode 
from qrtools import QR 
 
img = qrcode.make('https://www.bilibili.com/')
img.save('bilibili.png') 

