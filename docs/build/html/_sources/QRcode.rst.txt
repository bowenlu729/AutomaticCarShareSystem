QRcode
============

generateQRcode                                                      
----------------                                                              
* import qrcode 
* content: somethings you want to generate to a QRcode(website address, text)
* img = qrcode.make('content'):make a picture
* img.save('picture_name.png'):Export images         
                                                                   
Decode                                                               
---------   

* Need to pip:
* import requests
* from io import BytesIO
* from pyzbar import pyzbar
* from PIL import Image,ImageEnhance

* Img_adds: QR code address (can be a url or a local addres
* Image.open(img_adds):Load the QR code image locally
* txt_list = pyzbar.decode(img): decode QRcode