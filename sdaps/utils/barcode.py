# -*- coding: utf-8 -*-
# SDAPS - Scripts for data acquisition with paper based surveys
# Copyright(C) 2012, Benjamin Berg <benjamin@sipsolutions.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

u"""
This module contains helpers to read barcodes from cairo A1 surfaces.
"""

from sdaps.utils.ugettext import ugettext, ungettext
_ = ugettext

import cairo
import zbar
from zxinglight import read_codes, BarcodeType
from PIL import Image
from sdaps import image
from sdaps import defs

import logging
logging.getLogger('zxinglight').setLevel(logging.CRITICAL)


def read_barcode(surface, matrix, x, y, width, height, btype="CODE128"):
    u"""Tries to read the barcode at the given position"""
    result = scan(surface, matrix, x, y, width, height, btype)

    if result == None:
      # Try kfill approach
      result = scan(surface, matrix, x, y, width, height, btype, True)

    return result

def scan(surface, matrix, x, y, width, height, btype="CODE128", kfill=False):
    x0, y0 = matrix.transform_point(x, y)
    x1, y1 = matrix.transform_point(x + width, y + height)

    # Bounding box ...
    x = min(x0, x1)
    y = min(y0, y1)
    width = max(x0, x1) - x
    height = max(y0, y1) - y

    x, y, width, height = int(x), int(y), int(width), int(height)
    # Round the width to multiple of 4 pixel, so that the stride will
    # be good ... hopefully
    width = width - width % 4 + 4

    # a1 surface for kfill algorithm
    a1_surface = cairo.ImageSurface(cairo.FORMAT_A1, width, height)

    cr = cairo.Context(a1_surface)
    cr.set_operator(cairo.OPERATOR_SOURCE)
    cr.set_source_surface(surface, -x, -y)
    cr.paint()

    if kfill:
        pxpermm = (matrix[0] + matrix[3]) / 2
        barwidth = pxpermm * defs.code128_barwidth
        barwidth = int(round(barwidth))

        if barwidth <= 3:
            return

        if barwidth > 6:
            barwidth = 6

        image.kfill_modified(a1_surface, barwidth)

    # zbar does not understand A1, but it can handle 8bit greyscale ...
    # We create an inverted A8 mask for zbar, which is the same as a greyscale
    # image.
    a8_surface = cairo.ImageSurface(cairo.FORMAT_A8, width, height)

    cr = cairo.Context(a8_surface)
    cr.set_source_rgba(1, 1, 1, 1)
    cr.set_operator(cairo.OPERATOR_SOURCE)
    cr.paint()
    cr.set_source_rgba(0, 0, 0, 0)
    cr.mask_surface(a1_surface, 0, 0)

    del cr
    a8_surface.flush()

    # Try zxing

    if btype == "CODE128":
        barcode_type = BarcodeType.CODE_128
    elif btype == "QRCODE":
        barcode_type = BarcodeType.QR_CODE
    else:
        barcode_type = None
    img = Image.frombuffer("L", (width, height), bytes(a8_surface.get_data()), "raw" ,"L", 0, 1)
    for nw in range(width, 256, -64):
        codes = read_codes(img.resize((nw, nw*height//width), Image.BICUBIC),
            barcode_type=barcode_type, try_harder=True, search_multi=False)
        if len(codes) > 0:
            return codes[0]

    # Try zbar

    # Now we have pixel data that can be passed to zbar
    img = zbar.Image()
    img.format = "Y800"
    img.data = str(a8_surface.get_data())
    img.height = height
    # Use the stride, it should be the same as width, but if it is not, then
    # it is saner to add a couple of junk pixels instead of getting weird
    # offsets and missing data.
    img.width = a8_surface.get_stride()

    scanner = zbar.ImageScanner()
    scanner.scan(img)

    result = None
    result_quality = -1
    for symbol in scanner.results:
        # Ignore barcodes of the wrong type
        if str(symbol.type) != btype:
            continue

        # return the symbol with the highest quality
        if symbol.quality > result_quality:
            result = symbol.data
            result_quality = symbol.quality


    # The following can be used to look at the images
    #rgb_surface = cairo.ImageSurface(cairo.FORMAT_RGB24, width, height)
    #cr = cairo.Context(rgb_surface)
    #cr.set_source_rgba(1, 1, 1, 1)
    #cr.set_operator(cairo.OPERATOR_SOURCE)
    #cr.paint()
    #cr.set_source_rgba(0, 0, 0, 0)
    #cr.mask_surface(a1_surface, 0, 0)
    #rgb_surface.write_to_png("/tmp/barcode-%03i.png" % barcode)
    #barcode += 1

    return result



