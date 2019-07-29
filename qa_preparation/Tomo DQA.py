""" Modify Tomo DQA Plan

    Prompts user for Gantry Period for running a TomoDQA

    Version:
    1.0 Load targets as filled. Normalize isodose to prescription, and try to normalize to the
        maximum dose in External or External_Clean

    This program is free software: you can redistribute it and/or modify it under
    the terms of the GNU General Public License as published by the Free Software
    Foundation, either version 3 of the License, or (at your option) any later
    version.
    
    This program is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
    FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
    
    You should have received a copy of the GNU General Public License along with
    this program. If not, see <http://www.gnu.org/licenses/>.
    """

__author__ = 'Adam Bayliss and Patrick Hill'
__contact__ = 'rabayliss@wisc.edu'
__date__ = '29-Jul-2019'
__version__ = '1.0.0'
__status__ = 'Production'
__deprecated__ = False
__reviewer__ = ''
__reviewed__ = ''
__raystation__ = '8b.SP2'
__maintainer__ = 'One maintainer'
__email__ = 'rabayliss@wisc.edu'
__license__ = 'GPLv3'
__copyright__ = 'Copyright (C) 2018, University of Wisconsin Board of Regents'
__help__ = 'https://github.com/mwgeurts/ray_scripts/wiki/User-Interface'
__credits__ = []

import connect
import logging
import UserInterface
import DicomExport

import os
import sys


def main():
    # Get current patient, case, exam, plan, and beamset
    try:
        patient = connect.get_current('Patient')
        case = connect.get_current('Case')
        exam = connect.get_current('Examination')

    except Exception:
        UserInterface.WarningBox('This script requires a patient to be loaded')
        sys.exit('This script requires a patient to be loaded')

    try:
        plan = connect.get_current('Plan')
        beamset = connect.get_current('BeamSet')

    except Exception:
        logging.debug('A plan and/or beamset is not loaded; plan export options will be disabled')
        plan = None
        beamset = None

    # find the correct verification plan
    index_not_found = True
    bs_name = str(beamset.DicomPlanLabel)
    qa_name = str(plan.VerificationPlans[0].ForTreatmentPlan.Name)
    logging.debug('Finding verification plan for {}'.format(beamset.DicomPlanLabel))
    logging.debug('Verification plan[{}] is {}, not a match for {}.'.format(
        0, qa_name, bs_name
    ))
    # Find the correct verification plan for this beamset
    try:
        indx = 0
        bs_name = str(beamset.DicomPlanLabel)
        qa_name = str(plan.VerificationPlans[indx].ForTreatmentPlan.Name)
        while qa_name not in bs_name:
            logging.debug('Verification plan[{}] is {}, not a match for {}.'.format(
                indx, qa_name, bs_name
            ))
            indx += 1

    except Exception:
        index_not_found = True

    if index_not_found:
        logging.warning("verification plan for {} could not be found.".format(beamset.DicomPlanLabel))
        sys.exit("Could not find beamset optimization")
    else:
        # Found our index.  We will use a shorthand for the remainder of the code
        qa_plan = plan.VerificationPlans[indx]
        logging.info('verification plan found, exporting {} for beamset {}'.format(
                plan.VerificationPlan[indx].DicomPlanLabel, beamset.DicomPlanLabel))

    # extract dicom file and gantry period from directory files
    # Initialize options to include DICOM destination and data selection. Add more if a plan is also selected
    inputs = {'a': 'Enter the gantry period',
              'b': 'Check one or more DICOM destinations to export to:'}
    required = ['a', 'b']
    types = {'b': 'check'}
    options = {'b': DicomExport.destinations()}
    initial = {}

    dialog = UserInterface.InputDialog(inputs=inputs,
                                       datatype=types,
                                       options=options,
                                       initial=initial,
                                       required=required,
                                       title='Export Options')
    response = dialog.show()
    if response == {}:
        sys.exit('DICOM export was cancelled')
    # Link root to selected protocol ElementTree
    logging.info("User input the following Gantry Period: {}".format(
        response['a']))

    success = DicomExport.send(case=case,
                               destination=response['b'],
                               qa_plan=qa_plan,
                               exam=False,
                               beamset=False,
                               ct=False,
                               structures=False,
                               plan=False,
                               plan_dose=False,
                               beam_dose=False,
                               ignore_warnings=False,
                               ignore_errors=False,
                               gantry_period=response['a'],
                               filters=['tomo_dqa'],
                               bar=False)

    # Finish up
    if success:
        logging.info('Export script completed successfully in {:.3f} seconds'.format(time.time() - tic))
        status.finish(text='DICOM export was successful. You can now close this dialog.')

    else:
        logging.warning('Export script completed with errors in {:.3f} seconds'.format(time.time() - tic))
        status.finish(text='DICOM export finished but with errors. You can now close this dialog.')


    filepath = 'W:\\rsconvert\\'
    hlist = os.listdir(filepath)
    flist = filter(lambda x: '.dcm' in x, hlist)
    filename = flist[0]
    GPlist = filter(lambda x: '.txt' in x, hlist)
    # GPval = GPlist[0][3:8]+' '


    # format and set tag to change
    t1 = Tag('300d1040')

    # read file
    ds = pydicom.read_file(filepath+filename)

    # add attribute to beam sequence
    ds.BeamSequence[0].add_new(t1, 'UN', GPval)

    # output file
    ds.save_as(filepath+'new_'+filename, write_like_original=True)


if __name__ == '__main__':
    main()


