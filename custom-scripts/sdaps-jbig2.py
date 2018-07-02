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

import sys
import os
import subprocess
import shutil
from backports import tempfile
DEVNULL = open(os.devnull, 'w')

# Use the following and local_run=True below to run without installing SDAPS
sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), '..'))

import sdaps
sdaps.init(local_run=True)
#sdaps.init()

from sdaps import model
from sdaps import image
from sdaps import matrix

survey = model.survey.Survey.load(sys.argv[1])
counter = 1


def generate_pdf():

    global counter
    global survey

    questionnaire = survey.questionnaire
    sheet = survey.sheet

    # Use the questionnaire ID, if not there, give up?
    if sheet.questionnaire_id is not None:
        pdf_name = '%s.pdf' % sheet.questionnaire_id
    else:
        pdf_name = '%04i.pdf' % counter
        counter += 1

    with tempfile.TemporaryDirectory() as tmp_dir:
        page_files = []

        for p in xrange(questionnaire.page_count):
            # 1 based page numbers
            p += 1

            # Get the current image
            img = sheet.get_page_image(p)
            if img is None:
                continue

            page_file = os.path.join(tmp_dir, 'page-%04i.tiff' % p)
            page_files.append(page_file)
            surface = img.surface.load_uncached()
            image.write_a1_to_tiff(page_file, surface)

        if page_files != []:
            p = subprocess.Popen(['jbig2', '-s', '-p'] + page_files,
                                 cwd=tmp_dir,
                                 stderr=DEVNULL)
            assert p.wait() == 0

            p = subprocess.Popen(['pdf.py', 'output'],
                                 cwd=tmp_dir,
                                 stdout=subprocess.PIPE)
            with open(pdf_name, 'wb') as f:
                shutil.copyfileobj(p.stdout, f)
            assert p.wait() == 0


survey.iterate_progressbar(generate_pdf)

