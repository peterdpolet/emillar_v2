#!/usr/bin/env python3
"""
print_service.py
Standalone label print service — runs on the laptop (bare metal), outside Docker.
Django backend calls this via http://localhost:5100/print

Usage:
    python3 print_service.py

Dependencies:
    pip install flask qrcode pillow --break-system-packages
    (ptouch already installed)
"""

import logging
import traceback

import qrcode
from flask import Flask, jsonify, request
from PIL import Image, ImageDraw, ImageFont

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

app = Flask(__name__)

# ── Printer constants ──────────────────────────────────────────────────────────
VENDOR_ID     = 0x04f9
PRODUCT_ID    = 0x2062
TAPE_WIDTH_PX = 128        # 24mm tape on PT-P750W = 128 printable pixels
LABEL_LENGTH  = 400        # px — adjust to taste
MARGIN        = 6          # px each side


def make_label(sku: str, so_number: str, item_url: str) -> Image.Image:
    """
    Build a PIL image for a 24mm label.
    Layout (tape feeds left to right):

        ┌─────────────────────────────────────────┐
        │  [QR code]  SKU: EM-0042                │
        │             SO:  SO-2024-001             │
        └─────────────────────────────────────────┘
    """
    img  = Image.new('RGB', (LABEL_LENGTH, TAPE_WIDTH_PX), 'white')
    draw = ImageDraw.Draw(img)

    # ── QR code ───────────────────────────────────────────────
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=3,
        border=1,
    )
    qr.add_data(item_url)
    qr.make(fit=True)
    qr_img  = qr.make_image(fill_color='black', back_color='white').convert('RGB')
    qr_size = TAPE_WIDTH_PX - (MARGIN * 2)
    qr_img  = qr_img.resize((qr_size, qr_size), Image.NEAREST)
    img.paste(qr_img, (MARGIN, MARGIN))

    # ── Text ──────────────────────────────────────────────────
    text_x = TAPE_WIDTH_PX + MARGIN
    try:
        font_lg = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 18)
        font_sm = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 15)
    except OSError:
        font_lg = ImageFont.load_default()
        font_sm = font_lg

    draw.text((text_x, MARGIN + 8),  f'SKU: {sku}',       font=font_lg, fill='black')
    draw.text((text_x, MARGIN + 36), f'SO:  {so_number}', font=font_sm, fill='black')

    return img


def send_to_printer(img: Image.Image):
    from ptouch.printers   import PTP750W
    from ptouch.connection import ConnectionUSB
    from ptouch.label      import Label
    from ptouch.tape       import Tape24mm

    conn    = ConnectionUSB(vendor_id=VENDOR_ID, product_id=PRODUCT_ID)
    printer = PTP750W(conn)
    label   = Label(image=img, tape=Tape24mm)
    printer.print(label, auto_cut=True)


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})


@app.route('/print', methods=['POST'])
def print_label():
    data = request.get_json(force=True)
    log.info('Print request: %s', data)

    sku       = data.get('sku', '')
    so_number = data.get('so_number', '')
    item_url  = data.get('item_url', '')

    if not all([sku, so_number, item_url]):
        return jsonify({'error': 'sku, so_number and item_url are required'}), 400

    try:
        img = make_label(sku, so_number, item_url)
        send_to_printer(img)
        log.info('Label printed OK — SKU=%s SO=%s', sku, so_number)
        return jsonify({'status': 'printed'})
    except Exception as e:
        log.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5100, debug=False)