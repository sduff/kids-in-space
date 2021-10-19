#!/usr/local/bin/python3

import json

from PIL import Image, ImageDraw, ImageFont

import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer

# read JSON file from https://github.com/Bowserinator/Periodic-Table-JSON
with open('PeriodicTableJSON.json') as fp:
    data = json.load(fp)

output = {}

font50 = ImageFont.truetype(font="Goldman-Bold.ttf", size=50)
font25 = ImageFont.truetype(font="Goldman-Regular.ttf", size=75)
font10 = ImageFont.truetype(font="Goldman-Regular.ttf", size=15)

# Will the text fit in a w*h rectangle if written in the given font.
# Return None if the text is too big, otherwise, return a \n separated string of sentences to write
# *Note* this function assumes single spacing between all words
def will_it_fit(w,h,f,text):
    i = Image.new(mode="RGB", size=(w,h))
    d = ImageDraw.Draw(i)

    lines = []
    words = text.split(' ')
    os = ""

    for word in words:
        temp = " ".join([os, word])
        orect = d.multiline_textbbox((0, 0),text=temp,font=f)
        # if orect is too big on the y-axis, return None
        if orect[3] > h:
            return None
        # if orect is too big x-axis, insert a newline before the most recent word
        elif orect[2] > w:
            os = " ".join([os,f"\n{word}"])
        else:
            os = temp
    print(f"fit, {text}")
    return os

for e in data["elements"]:
    o = {}
    o["name"] = e["name"]
    o["symbol"] = e["symbol"]
    o["number"] = e["number"]
#    o["appearance"] = e["appearance"]
#    o["category"] = e["category"]
    o["summary"] = e["summary"]

    # create a list of objects, can use json.dumps later on
    output[o["name"]] = o["name"]

    # CSV output
    #print("""{symbol},{name},{number},"{appearance}","{category}","{summary}" """.format(**o))

    # generate a QR code (185x185 pixels)
    qr = qrcode.QRCode(
            version=3,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=5,
            border=4
        )
    qr.add_data(o["name"].lower())
    qr.make()
    qr_img = qr.make_image(image_factory=StyledPilImage, module_drawer=RoundedModuleDrawer())
    #qr_img = qr.make_image()

    # load card template file
#    img = Image.new("RGB", (300,300), color="white")
#    draw = ImageDraw.Draw(img)
    img = Image.open("template.png")
    draw = ImageDraw.Draw(img)

    # need to draw a rectangle to give a border
#    draw.rounded_rectangle([1,1,298,298],radius=5,outline=(0,0,0))

    # paste the QR code in place
    qr_img = qr_img.resize((300,300),Image.HAMMING)
    img.paste(qr_img, (610,10))

    # draw the symbol and atomic number
    draw.text((277,55), o["name"], "#fff", font=font50, anchor="mm", align="center")
    draw.text((110,210), o["symbol"], "#000", font=font25, anchor="mm", align="center")
    draw.text((310,210), str(o["number"]), "#000", font=font25, anchor="mm", align="center")

    ml = will_it_fit(190, 190, font10, o["summary"])
    if ml:
        draw.text((510,210), ml, "#000", font=font10, anchor="mm", align="center")

    # save the image to a file
    filename = "%s.png"%o["name"].lower()
    img.save(filename)
