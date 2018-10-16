""" Create Clinical Goals and Objectives

    Add clinical goals and objectives in RayStation given user supplied inputs

    Inputs::


"""
__author__ = 'Adam Bayliss'
__contact__ = 'rabayliss@wisc.edu'
__version__ = '1.0.0'
__license__ = 'GPLv3'
__help__ = 'https://github.com/wrssc/ray_scripts/wiki/CreateGoals'
__copyright__ = 'Copyright (C) 2018, University of Wisconsin Board of Regents'

import sys
import os
import logging
import datetime
import xml.etree.ElementTree
import connect
import UserInterface
import WriteTpo
import Goals


def main():
    protocol_folder = r'../protocols'
    institution_folder = r'UW'
    file_name = 'UWLung_StandardFractionation.xml'
    path_file = os.path.join(os.path.dirname(__file__), protocol_folder, institution_folder, file_name)
    path_protocols = os.path.join(os.path.dirname(__file__), protocol_folder, institution_folder)
    # Get current patient, case, exam, and plan
    try:
        patient = connect.get_current('Patient')
        case = connect.get_current('Case')
        exam = connect.get_current('Examination')
        plan = connect.get_current('Plan')
        patient.Save()

    except Exception:
        UserInterface.WarningBox('This script requires a patient and plan to be loaded')
        sys.exit('This script requires a patient and plan to be loaded')

    # TODO: replace all the hardcoded options with a user interface prompt
    # Without adding another attribute to the goals list, here's what we need to do
    targets = ['PTV', 'ITV', 'GTV']
    tpo = UserInterface.TpoDialog()
    tpo.load_protocols(path_protocols)

    ptv_md_dose = 60
    ptv_name = 'PTV_MD'

    # TODO: Uncomment and add goal loop for secondary - unspecified target goals
    # input_dialog = UserInterface.InputDialog(
    #     inputs={
    #         'input0': 'Number of targets',
    #         'input1': 'Select Protocol',
    #     },
    #     title='Initial Input Clinical Goals',
    #     datatype={'input1': 'combo'},
    #     initial={},
    #     options={'input1': list(tpo.protocols.keys())},
    #     required=['input0', 'input1'])
    #
    # # Launch the dialog
    # print input_dialog.show()
    # # Store the number of targets
    # input_targets = int(input_dialog.values['input0'])
    # logging.info("create_goals.py: user input {} targets for protocol: {}".format(
    #     input_targets, input_dialog.values['input1']
    # ))
    # # To load the xml from file directly, without use of the TPO load:
    # # path_file = path_file = os.path.join(os.path.dirname(__file__),
    # #                                     protocol_folder, institution_folder, file_name)
    # # tree = xml.etree.ElementTree.parse(path_file)
    # # tree = tpo.protocols[input_protocol]
    # # root = tree.getroot()
    # root = tpo.protocols[input_dialog.values['input1']]
    # protocol_targets = []
    # for g in root.findall('./goals/roi'):
    #     # Ugh, gotta be a more pythonic way to do this loop
    #     # ? for g, t in ((a,b) for a in root.findall('./goals/roi') for b in targets)
    #     for t in targets:
    #         if t in g.find('name').text and g.find('name').text not in protocol_targets:
    #             protocol_targets.append(g.find('name').text)
    # logging.debug("protocol contains {} targets called: {}".format(
    #     len(protocol_targets), protocol_targets))
    #
    # # Second dialog
    # # Find RS targets
    # plan_targets = []
    # for r in case.PatientModel.RegionsOfInterest:
    #     if r.Type == 'Ptv':
    #         plan_targets.append(r.Name)
    #
    # final_inputs = {}
    # final_options = {}
    # final_datatype = {}
    # final_required = []
    #
    # # Add an input for every target name and dose
    # for i in range(1, input_targets):
    #     index_k_name = str(2 * i - 1)
    #     k_name = index_k_name.zfill(2) + '_plan_target'
    #     # These dict entries are needed for user-specified target entries
    #     final_inputs[k_name] = 'Target' + str(i) + ' name'
    #     final_options[k_name] = plan_targets
    #     final_datatype[k_name] = 'combo'
    #     final_required.append(k_name)
    #     # These dict entries are needed for dose specification
    #     k_dose = str(2 * i)
    #     k_dose = k_dose.zfill(2) + '_dose'
    #     final_inputs[k_dose] = 'Target' + str(i) + ' Dose in cGy'
    #     final_required.append(k_dose)
    # # Grab the number of inputs so far and start new input
    # i = len(final_inputs) + 1
    # for t in protocol_targets:
    #     print t
    #     index_k_name = str(i)
    #     k_name = index_k_name.zfill(2) + '_match'
    #     final_inputs[k_name] = 'Match protocol target:' + str(t) + ' to one of these'
    #     final_options[k_name] = plan_targets
    #     final_datatype[k_name] = 'combo'
    #     final_required.append(k_name)
    #     i += 1
    # # if input_targets > len(protocol_targets):
    # #     # A set of check boxes is needed to tell us what to do with these
    # #     index_k_name = str(i)
    # #     k_name = index_k_name.zfill(2) + '_check'
    # #     final_inputs[k_name] = ('You have selected more targets than are in the protocol.' +
    # #                             'would you like to assign the protocol goals scaled to the target' +
    # #                             ' doses you provided?')
    # #     final_datatype[k_name] = 'check'
    # #     final_options[k_name] = ['yes']
    # # # Loop over user identified targets that have no corresponding match.
    # # for k, v in final_inputs.iteritems():
    # #     logging.debug("create_goals.py: Inputs created as name, value: {} : {}".format(
    # #         k, v))
    #
    # final_dialog = UserInterface.InputDialog(
    #     inputs=final_inputs,
    #     title='Input Clinical Goals',
    #     datatype=final_datatype,
    #     initial={},
    #     options=final_options,
    #     required=final_required)
    # print final_dialog.show()
    #
    # # Process inputs
    # target_names = []
    # target_dose_values = []
    # protocol_match = []
    # for k, v in final_dialog.values.iteritems():
    #     if '_match' in k:
    #         protocol_match.append(v)
    #     if '_dose' in k:
    #         target_dose_values.append(float(v)/100.)
    #     if '_plan_target' in k:
    #         target_names.append(v)
    #     if '_check' in k and 'yes' in v:
    #         add_nonprotocol_target_objectives = True
    #     else:
    #         add_nonprotocol_target_objectives = False

    input_dialog = UserInterface.InputDialog(
        inputs={
            'input1': 'Select Protocol',
        },
        title='Initial Input Clinical Goals',
        datatype={'input1': 'combo'},
        initial={},
        options={'input1': list(tpo.protocols.keys())},
        required=['input1'])

    # Launch the dialog
    print input_dialog.show()
    # Link root to selected protocol ElementTree
    root = tpo.protocols[input_dialog.values['input1']]
    # Find RS targets
    plan_targets = []
    for r in case.PatientModel.RegionsOfInterest:
        if r.Type == 'Ptv':
            plan_targets.append(r.Name)
    # Use the following loop to find the targets in protocol matching the names above
    protocol_targets = []
    unmatched_protocol_targets = []
    # Build second dialog
    final_inputs = {}
    final_initial = {}
    final_options = {}
    final_datatype = {}
    final_required = []
    i = 1
    for g in root.findall('./goals/roi'):
        # Ugh, gotta be a more pythonic way to do this loop
        # ? for g, t in ((a,b) for a in root.findall('./goals/roi') for b in targets)
        g_name = g.find('name').text
        for t in plan_targets:
            # Look for an existing match to the target in the protocol_target list
            if g_name not in protocol_targets:
                if g_name == t:
                    protocol_targets.append(g_name)
                    k = str(i)
                    k_name = k.zfill(2) + 'Aname_' + g_name
                    # These dict entries are needed for user-specified target entries
                    final_inputs[k_name] = 'Match a plan target to ' + g_name
                    final_initial[k_name] = t
                    final_options[k_name] = plan_targets
                    final_datatype[k_name] = 'combo'
                    final_required.append(k_name)
                    # even index, use for dose values
                    kd = str(i)
                    k_dose = kd.zfill(2) + 'Bdose_' + g_name
                    final_inputs[k_dose] = 'Provide dose for protocol target: ' + g_name + ' Dose in cGy'
                    final_required.append(k_dose)
                    i += 1
                # If the goal is a match in the plan list, but is likely a target
                elif g_name != t and any(g in g_name for g in targets):
                    protocol_targets.append(g_name)
                    k = str(i)
                    k_name = k.zfill(2) + 'Aname_' + g_name
                    # odd index use for protocol_target
                    # These dict entries are needed for user-specified target entries
                    final_inputs[k_name] = 'Match a plan target to ' + g_name
                    final_options[k_name] = plan_targets
                    final_datatype[k_name] = 'combo'
                    final_required.append(k_name)
                    # even index, use for dose values
                    kd = str(i)
                    k_dose = kd.zfill(2) + 'Bdose_' + g_name
                    final_inputs[k_dose] = 'Provide dose for protocol target: ' + g_name + ' Dose in cGy'
                    final_required.append(k_dose)
                    i += 1

    final_dialog = UserInterface.InputDialog(
        inputs=final_inputs,
        title='Input Clinical Goals',
        datatype=final_datatype,
        initial=final_initial,
        options=final_options,
        required=final_required)
    print final_dialog.show()

    # Process inputs
    target_names = []
    target_dose_values = []
    # Make a dict with key = name from elementTree : [ Name from ROIs, Dose in Gy]
    protocol_match = {}
    # Need a different loop here: want key = target name, value = dose in Gy
    # 1a, 1b?
    i = 1
    for k, v in final_dialog.values.iteritems():
        i, p = k.split("_", 1)
        if 'name' in i:
            # Key name will be the protocol target name
            protocol_match[p] = v
            print "key: {}, and protocol_match[p] = {}".format(p, protocol_match[p])
        if 'dose' in i:
            # Append _dose to the key name
            pd = p + '_dose'
            protocol_match[pd] = (float(v) / 100.)
            print "key: {}, and protocol_match[p] = {}".format(pd, protocol_match[pd])

    # Add goals, note that the only way secondary goals get added is if the user is willing
    # to add them in with the same goals as the protocol
    for g in root.findall('./goals/roi'):
        # If the key is a name key, change the ElementTree for the name
        if g.find('name').text in protocol_match and "%" in g.find('dose').attrib['units']:
            name_key = g.find('name').text
            dose_key = g.find('name').text + '_dose'
            logging.debug('Reassigned protocol name from {} to {}, for dose {} Gy'.format(
                g.find('name').text, protocol_match[name_key],
                protocol_match[dose_key]))
            g.find('name').text = protocol_match[name_key]
            g.find('dose').attrib = "Gy"
            g.find('dose').text = protocol_match[dose_key]
        # Regardless, add the goal now
        logging.debug('create_goals.py: Adding goal ' + Goals.print_goal(g, 'xml'))
        Goals.add_goal(g, connect.get_current('Plan'))


if __name__ == '__main__':
    main()
