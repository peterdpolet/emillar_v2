
#!/usr/bin/python3

# Based on https://github.com/SquirrelCZE/ptouch-770
# Trying to add multi-line capabilities.
# Font size calculation/positioning apparently not correct.
# On 12mm tape, the topmost 20px are not printed, the following 84 px are printed
# (as determined by experimentation using calibrate_12mm_tape.pbm made with GIMP)

from PIL import Image, ImageFont, ImageDraw
import argparse
import os

def run():

    parser = argparse.ArgumentParser(description="Utility for printing on ptouch 700")
    parser.add_argument('--text', type=str, help="string to be printed", default="Two\\nlines")
    parser.add_argument('--height', type=int, help="height in pixels of loaded tape", default=84)
    parser.add_argument('--max-height', type=int, help="maximal height in pixels for printer", default=104)
    parser.add_argument('--rim', type=int, help="rim around the text in pixels", default=5)
    parser.add_argument('--font', type=str, help="name of truetype font", default="FreeSansBold.ttf")

    args = parser.parse_args()

    text = args.text.split("\\n")
    #text=['10/2018, drive pixels from 2A PSU', 'https://github.com/wvdv2002/ESP8266-LED-Websockets', 'NUM_LEDS=60, DATA_PIN=13', 'Adafruit_NeoPixel(NUM_LEDS, DATA_PIN, ', 'NEO_GRBW + NEO_KHZ800);']
    print(text)

    lines = len(text)

    fontsize = int(round(args.height/lines,0))

    font = ImageFont.truetype(args.font, fontsize)

    # Determine the longest line
    max_width = 0
    for line in text:
        text_width, text_height = font.getsize(line)
        width = text_width + args.rim * 2
        if(width > max_width):
            max_width = width

    image = Image.new("1", ( max_width, args.max_height ), 0)
    draw = ImageDraw.Draw( image )

    text_x = args.rim
    text_y = -0
    for line in text:
        text_y = text_y + text_height*0.9
        draw.text((text_x,text_y), line, fill=255, font=font)

    image.save("out.pbm")