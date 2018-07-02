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
qids_filename = sys.argv[2]

with open(qids_filename) as f:
    qids_to_preserve = set(int(line.strip()) for line in f)

for sheet in survey.sheets[:]:
    qid = int(sheet.questionnaire_id)
    if not qid in qids_to_preserve:
        print('Removing %r' % qid)
        survey.sheets.remove(sheet)

survey.save()
