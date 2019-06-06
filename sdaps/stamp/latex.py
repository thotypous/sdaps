
import sys
import os
import tempfile
import shutil

from sdaps import log
from sdaps import paths
from sdaps import defs

from sdaps.utils import latex
from sdaps.utils.ugettext import ugettext, ungettext
_ = ugettext

def create_stamp_pdf(survey, output_filename, questionnaire_ids):

    if questionnaire_ids is None:
        log.warn(_("There should be no need to stamp a SDAPS Project that uses LaTeX and does not have different questionnaire IDs printed on each sheet.\nI am going to do so anyways."))

    # Temporary directory for TeX files.
    tmpdir = tempfile.mkdtemp(prefix='sdaps-stamp-')

    try:
        latex.write_override(survey, os.path.join(tmpdir, 'sdaps.opt'), questionnaire_ids=questionnaire_ids)

        print _("Running %s now twice to generate the stamped questionnaire.") % defs.latex_engine
        latex.compile('questionnaire.tex', tmpdir, inputs=[os.path.abspath(survey.path())])

        if not os.path.exists(os.path.join(tmpdir, 'questionnaire.pdf')):
            log.error(_("Error running \"%s\" to compile the LaTeX file.") % defs.latex_engine)
            raise AssertionError('PDF file not generated')

        shutil.move(os.path.join(tmpdir, 'questionnaire.pdf'), output_filename)

    except:
        log.error(_("An error occured during creation of the report. Temporary files left in '%s'." % tmpdir))

        raise

    #log.error(_("An error occured during creation of the report. Temporary files left in '%s'." % tmpdir))
    shutil.rmtree(tmpdir)
