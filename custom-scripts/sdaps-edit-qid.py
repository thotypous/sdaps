#!/usr/bin/env python2
# -*- coding: utf8 -*-
# SDAPS - Scripts for data acquisition with paper based surveys
# Copyright (C) 2008, Christoph Simon <post@christoph-simon.eu>
# Copyright (C) 2015, Benjamin Berg <benjamin@sipsolutions.net>
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

from collections import defaultdict
import sys
import os

# Use the following and local_run=True below to run without installing SDAPS
sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), '..'))

import sdaps
sdaps.init(local_run=True)
#sdaps.init()

from sdaps import model
from sdaps import image
from sdaps import matrix


survey = model.survey.Survey.load(sys.argv[1])


page_data = {}
dirty_qids = set()

for i in xrange(2, len(sys.argv), 3):
    tiff_page, qid, page_number = sys.argv[i:i+3]
    #tiff_page starts counting at 1
    #page_number starts counting at 1

    tiff_page = int(tiff_page)
    page_number = int(page_number)

    page_data[tiff_page] = (qid, page_number)
    dirty_qids.add(qid)


image_count = survey.questionnaire.page_count
# We have two images per page in simplex mode!
if not survey.defs.duplex:
    image_count = image_count * 2
images = defaultdict(lambda : [])

for sheet in survey.sheets[:]:
    for image in sheet.images[:]:
        #print(image.questionnaire_id, image.page_number)
        if image.questionnaire_id is None and image.tiff_page != -1:
            print("unrecog page => %d" % (image.tiff_page + 1))

        qid, page_number = page_data.get(image.tiff_page + 1, (None, None))

        if qid is not None:
            print("%d => (%r, %r)" % (image.tiff_page + 1, qid, page_number))
            image.questionnaire_id = qid
            image.page_number = page_number
            sheet.images.remove(image)
            images[image.questionnaire_id].append(image)

    if sheet.questionnaire_id is None or sheet.questionnaire_id in dirty_qids:
        survey.sheets.remove(sheet)
        for image in sheet.images:
            images[image.questionnaire_id].append(image)


for qid, img_list in images.iteritems():
    if qid is not None:
        sheet = model.sheet.Sheet()
        sheet.questionnaire_id = qid
        survey.add_sheet(sheet)

        while len(img_list) > 0:
            sheet.add_image(img_list.pop(0))
            assert len(sheet.images) < image_count

if len(page_data) != 0:
    survey.save()
