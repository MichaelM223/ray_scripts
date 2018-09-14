""" Generate Planning Structures

    This script is designed to help you make planning structures.  Prior to starting you should determine:
    All structures to be treated, and their doses
    All structures with priority 1 goals (they are going to be selected for UnderDose)
    All structures where hot-spots are undesirable but underdosing is not desired.  They will be placed in
    the UniformDose ROI.


    Note:
    Using the Standard InputDialog
    We have several calls
    The first will determine the target doses and whether we are uniform or underdosing
         Based on those responses:
         Select and Approve underdose selections
         Select and Approve uniform dose selections
    The second non-optional call prompts the user to use:
        -Target-specific rings
        -Specify desired standoffs in the rings closest to the target
    Raystation script to make structures used for planning.

    Inputs:
        None, though eventually the common uniform and underdose should be dumped into xml files
        and stored in protocols

    Usage:


    This program is free software: you can redistribute it and/or modify it under
    the terms of the GNU General Public License as published by the Free Software
    Foundation, either version 3 of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
    FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along with
    this program. If not, see <http://www.gnu.org/licenses/>.
"""
from pickle import FALSE

# from typing import List, Any

__author__ = 'Adam Bayliss'
__contact__ = 'rabayliss@wisc.edu'
__version__ = '1.0.0'
__license__ = 'GPLv3'
__help__ = 'https://github.com/mwgeurts/ray_scripts/wiki/User-Interface'
__copyright__ = 'Copyright (C) 2018, University of Wisconsin Board of Regents'

import connect
import logging
import UserInterface
import time


def make_boolean_structure(patient, case, examination, **kwargs):
    StructureName = kwargs.get("StructureName")
    ExcludeFromExport = kwargs.get("ExcludeFromExport")
    VisualizeStructure = kwargs.get("VisualizeStructure")
    StructColor = kwargs.get("StructColor")
    SourcesA = kwargs.get("SourcesA")
    MarginTypeA = kwargs.get("MarginTypeA")
    ExpA = kwargs.get("ExpA")
    OperationA = kwargs.get("OperationA")
    SourcesB = kwargs.get("SourcesB")
    MarginTypeB = kwargs.get("MarginTypeB")
    ExpB = kwargs.get("ExpB")
    OperationB = kwargs.get("OperationB")
    MarginTypeR = kwargs.get("MarginTypeR")
    ExpR = kwargs.get("ExpR")
    OperationResult = kwargs.get("OperationResult")
    StructType = kwargs.get("StructType")
    try:
        case.PatientModel.RegionsOfInterest[StructureName]
        logging.warning("Structure " + StructureName + " exists.  This will be overwritten in this examination")
    except:
        case.PatientModel.CreateRoi(Name=StructureName,
                                    Color=StructColor,
                                    Type=StructType,
                                    TissueName=None,
                                    RbeCellTypeName=None,
                                    RoiMaterial=None)

    case.PatientModel.RegionsOfInterest[StructureName].SetAlgebraExpression(
        ExpressionA={'Operation': OperationA, 'SourceRoiNames': SourcesA,
                     'MarginSettings': {'Type': MarginTypeA,
                                        'Superior': ExpA[0],
                                        'Inferior': ExpA[1],
                                        'Anterior': ExpA[2],
                                        'Posterior': ExpA[3],
                                        'Right': ExpA[4],
                                        'Left': ExpA[5]
                                        }},
        ExpressionB={'Operation': OperationB, 'SourceRoiNames': SourcesB,
                     'MarginSettings': {'Type': MarginTypeB,
                                        'Superior': ExpB[0],
                                        'Inferior': ExpB[1],
                                        'Anterior': ExpB[2],
                                        'Posterior': ExpB[3],
                                        'Right': ExpB[4],
                                        'Left': ExpB[5]}},
        ResultOperation=OperationResult,
        ResultMarginSettings={'Type': MarginTypeR,
                              'Superior': ExpR[0],
                              'Inferior': ExpR[1],
                              'Anterior': ExpR[2],
                              'Posterior': ExpR[3],
                              'Right': ExpR[4],
                              'Left': ExpR[5]})
    case.PatientModel.RegionsOfInterest[StructureName].ExcludeFromExport = ExcludeFromExport
    case.PatientModel.RegionsOfInterest[StructureName].UpdateDerivedGeometry(
        Examination=examination, Algorithm="Auto")


def main():
    # The following list allows different elements of the code to be toggled
    # No guarantee can be made that things will work if elements are turned off
    # all dependencies are not really resolved
    generate_ptvs = True
    generate_ptv_evals = True
    generate_otvs = True
    GenerateSkin = True
    generate_inner_air = True
    generate_ring_hd = True
    GenerateRingLD = True
    GenerateNormal_2cm = True

    # Contraction in cm to be used in the definition of the skin contour
    skin_contraction = 0.5

    # InnerAir Parameters
    # Upper Bound on the air volume to be removed from target coverage considerations
    InnerAirHU = -900

    try:
        patient = connect.get_current('Patient')
        case = connect.get_current("Case")
        examination = connect.get_current("Examination")
    except:
        logging.warning("Aww crap, No patient")

    status = UserInterface.ScriptStatus(
        steps=['User Input',
               'Support elements Generation',
               'Target Generation',
               'Ring Generation'],
        docstring=__doc__,
        help=__help__)

    status.next_step(text='Please fill out the following input dialogs')
    # At this point start tracking all ROI's generated by this program
    newly_generated_rois = []
    # Commonly underdoses structures
    # Plan structures matched in this list will be selected for checkbox elements below
    UnderStructureChoices = [
        'Aorta',
        'BrachialPlexus_L',
        'BrachialPlexus_L_PRV05',
        'BrachialPlexus_R',
        'BrachialPlexus_R_PRV05',
        'BrainStem',
        'CaudaEquina',
        'Chiasm',
        'Cochlea_L',
        'Cochlea_R',
        'Duodenum',
        'Esophagus',
        'SmallBowel',
        'Heart',
        'LargeBowel',
        'Lens_R',
        'Lens_L',
        'Rectum',
        'Genitalia',
        'Globe_L',
        'Globe_R',
        'Hippocampus_L',
        'Hippocampus_L_PRV05',
        'Hippocampus_R',
        'Hippocampus_R_PRV05',
        'IliacCrest_L',
        'IliacCrest_R',
        'PulmonaryTrunk',
        'SpinalCord',
        'SpinalCord_PRV02',
        'OpticNerve_L',
        'OpticNerve_R',
        'ProxBronchialTree',
        'Trachea',
    ]

    # Common uniformly dosed areas
    # Plan structures matched in this list will be selected for checkbox elements below
    UniformStructureChoices = [
        'Aorta_PRV05',
        'BrainStem_PRV03',
        'Bladder',
        'CaudaEquina_PRV05',
        'Chiasm_PRV03',
        'Cochlea_L_PRV05',
        'Cochlea_R_PRV05',
        'ConstrMuscle',
        'Esophagus_PRV05',
        'Duodenum_PRV05',
        'Mandible',
        'LargeBowel',
        'Larynx',
        'Lens_L_PRV05',
        'Lens_R_PRV05',
        'Lips',
        'PeritonealCavity',
        'ProxBronchialTree_PRV05',
        'PulmonaryTrunk_PRV05',
        'OpticNerve_L_PRV03',
        'OpticNerve_R_PRV03',
        'Rectum',
        'SmallBowel',
        'SpinalCord_PRV05',
        'Stomach',
        'Trachea',
        'Vulva',
    ]

    # Find all the target names and generate the potential dropdown list for the cases
    # Use the above list for Uniform Structure Choices and Underdose choices, then
    # autoassign to the potential dropdowns
    TargetMatches = []
    UniformMatches = []
    UnderMatches = []
    AllOars = []
    for r in case.PatientModel.RegionsOfInterest:
        if r.Type == 'Ptv':
            TargetMatches.append(r.Name)
        if r.Name in UniformStructureChoices:
            UniformMatches.append(r.Name)
        if r.Name in UnderStructureChoices:
            UnderMatches.append(r.Name)
        if r.OrganData.OrganType == 'OrganAtRisk':
            AllOars.append(r.Name)

    # This dialog will determine whether the user wants underdose or uniform dose structures
    # This dialog also matches desired targets and specifies doses
    initial_dialog = UserInterface.InputDialog(
        inputs={
            'PTV1': 'Select 1st target Source',
            'PTV1Dose': 'Enter 1st target Dose in cGy',
            'PTV2': 'Select 2nd target Source',
            'PTV2Dose': 'Enter 2nd target Dose in cGy',
            'PTV3': 'Select 3rd target Source',
            'PTV3Dose': 'Enter 3rd target Dose in cGy',
            'PTV4': 'Select 4th target Source',
            'PTV4Dose': 'Enter 4th target Dose in cGy',
            'PTV5': 'Select 5th target Source',
            'PTV5Dose': 'Enter 5th target Dose in cGy',
            'UnderDose': 'Priority 1 goals present: Use Underdosing',
            'UniformDose': 'Targets overlap sensitive structures: Use UniformDoses',
        },
        title='Target Selection',
        datatype={'PTV1': 'combo',
                  'PTV2': 'combo',
                  'PTV3': 'combo',
                  'PTV4': 'combo',
                  'PTV5': 'combo',
                  'UniformDose': 'check',
                  'UnderDose': 'check',
                  },
        initial={
            'PTV1Dose': '0',
            'PTV2Dose': '0',
            'PTV3Dose': '0',
            'PTV4Dose': '0',
            'PTV5Dose': '0',
        },
        options={'PTV1': TargetMatches,
                 'PTV2': TargetMatches,
                 'PTV3': TargetMatches,
                 'PTV4': TargetMatches,
                 'PTV5': TargetMatches,
                 'UniformDose': ['yes'],
                 'UnderDose': ['yes']
                 },
        required=['PTV1'])

    # Launch the dialog
    print initial_dialog.show()

    # Parse the output from initial_dialog
    # We are going to take a user input input_source_list and convert them into PTV's used for planning
    # input_source_list consists of the user-specified targets to be massaged into PTV1, PTV2, .... below

    input_source_list = []
    source_doses = []
    if 'PTV1' in initial_dialog.values:
        input_source_list.append(initial_dialog.values['PTV1'])
        source_doses.append(initial_dialog.values['PTV1Dose'])

    if 'PTV2' in initial_dialog.values:
        input_source_list.append(initial_dialog.values['PTV2'])
        source_doses.append(initial_dialog.values['PTV2Dose'])

    if 'PTV3' in initial_dialog.values:
        input_source_list.append(initial_dialog.values['PTV3'])
        source_doses.append(initial_dialog.values['PTV3Dose'])

    if 'PTV4' in initial_dialog.values:
        input_source_list.append(initial_dialog.values['PTV4'])
        source_doses.append(initial_dialog.values['PTV4Dose'])

    if 'PTV5' in initial_dialog.values:
        input_source_list.append(initial_dialog.values['PTV5'])
        source_doses.append(initial_dialog.values['PTV5Dose'])

    # User selected that Uniformdose is required
    if 'yes' in initial_dialog.values['UniformDose']:
        generate_uniformdose = True
    else:
        generate_uniformdose = False

    # User selected that Underdose is required

    if 'yes' in initial_dialog.values['UnderDose']:
        generate_underdose = True
    else:
        generate_underdose = False

    # Rephrase the next statement with logging
    logging.debug('Proceeding with target list: [%s]' % ', '.join(map(str, input_source_list)))
    logging.debug('Proceeding with target doses: [%s]' % ', '.join(map(str, source_doses)))
    logging.debug('User selected {} for UnderDose'.format(generate_underdose))
    logging.debug('User selected {} for UniformDose'.format(generate_uniformdose))

    # Underdose dialog call
    if generate_underdose:
        under_dose_dialog = UserInterface.InputDialog(
            title='UnderDose',
            inputs={
                'input1_underdose': 'Select UnderDose Structures',
                'input2_underdose': 'Select UnderDose OAR',
                'input3_underdose': 'Select UnderDose OAR',
                'input4_under_standoff': 'UnderDose Standoff: x cm gap between targets and UnderDose volume'},
            datatype={
                'input1_underdose': 'check',
                'input2_underdose': 'combo',
                'input3_underdose': 'combo'},
            initial={'input4_under_standoff': '0.4'},
            options={
                'input1_underdose': UnderMatches,
                'input2_underdose': AllOars,
                'input3_underdose': AllOars},
            required=[])
        print under_dose_dialog.show()
        underdose_structures = []
        try:
            underdose_structures.extend(under_dose_dialog.values['input1_underdose'])
        except KeyError:
            pass
        try:
            underdose_structures.extend([under_dose_dialog.values['input2_underdose']])
        except KeyError:
            pass
        try:
            underdose_structures.extend([under_dose_dialog.values['input3_underdose']])
        except KeyError:
            pass
        underdose_standoff = float(under_dose_dialog.values['input4_under_standoff'])
        logging.debug("Underdose list selected: {}".format(underdose_structures))

    # Replace with a logging debug call
    # for structs in uniform_structures: print structs

    # UniformDose dialog call
    if generate_uniformdose:
        uniformdose_dialog = UserInterface.InputDialog(
            title='UniformDose Selection',
            inputs={
                'input1_uniform': 'Select UniformDose Structures',
                'input2_uniform': 'Select UniformDose OAR',
                'input3_uniform': 'Select UniformDose OAR',
                'input4_uniform_standoff': 'UniformDose Standoff: x cm gap between targets and UniformDose volume'},
            datatype={
                'input1_uniform': 'check',
                'input2_uniform': 'combo',
                'input3_uniform': 'combo'},
            initial={'input4_uniform_standoff': '0.4'},
            options={
                'input1_uniform': UniformMatches,
                'input2_uniform': AllOars,
                'input3_uniform': AllOars},
            required=[])
        print uniformdose_dialog.show()
        uniformdose_structures = []
        try:
            uniformdose_structures.extend(uniformdose_dialog.values['input1_uniform'])
        except KeyError:
            pass
        try:
            uniformdose_structures.extend([uniformdose_dialog.values['input2_uniform']])
        except KeyError:
            pass
        try:
            uniformdose_structures.extend([uniformdose_dialog.values['input3_uniform']])
        except KeyError:
            pass
        uniformdose_standoff = float(uniformdose_dialog.values['input4_uniform_standoff'])
        print "Uniform Dose list selected: {}".format(uniformdose_structures)

    # OPTIONS DIALOG
    #  Users will select use of:
    #
    options_dialog = UserInterface.InputDialog(
        title='Options',
        inputs={
            'input1_otv_standoff': 'OTV Standoff: x cm gap between higher dose targets',
            'input2_ring_standoff': 'Ring Standoff: x cm gap between targets and rings',
            'input3_skintarget': 'Preserve skin dose using skin-specific targets',
            'input4_targetrings': 'Make target-specific High Dose (HD) rings',
            'input5_thick_hd_ring': 'Thickness of the High Dose (HD) ring',
            'input6_thick_ld_ring': 'Thickness of the Low Dose (LD) ring',},
        datatype={
            'input3_skintarget': 'check',
            'input4_targetrings': 'check'},
        initial={'input1_otv_standoff': '0.3',
                 'input2_ring_standoff': '0.2',
                 'input5_thick_hd_ring': '2',
                 'input6_thick_ld_ring': '7'},
        options={
            'input3_skintarget': ['Preserve Skin Dose'],
            'input4_targetrings': ['Use target-specific rings']},
        required=[])
    print options_dialog.show()

    # Determine if targets using the skin are in place
    try:
        if 'Preserve Skin Dose' in options_dialog.values['input3_skintarget']:
            generate_target_skin = True
        else:
            generate_target_skin = False
    except KeyError:
        generate_target_skin = False

    # User wants target specific rings or no
    try:
        if 'Use target-specific rings' in options_dialog.values['input4_targetrings']:
            generate_target_rings = True
            generate_ring_hd = False
        else:
            generate_target_rings = False
    except KeyError:
        generate_target_rings = False

    print "User Selected Preserve Skin Dose: {}".format(generate_target_skin)
    print "User Selected target Rings: {}".format(generate_target_rings)

    # DATA PARSING FOR THE OPTIONS MENU
    # Stand - Off Values - Gaps between structures
    # cm gap between higher dose targets (used for OTV volumes)
    otv_standoff = float(options_dialog.values['input1_otv_standoff'])

    # ring_standoff: cm Expansion between targets and rings
    ring_standoff = float(options_dialog.values['input2_ring_standoff'])

    # Ring thicknesses
    thickness_hd_ring = float(options_dialog.values['input5_thick_hd_ring'])
    thickness_ld_ring = float(options_dialog.values['input6_thick_ld_ring'])

    status.next_step(text='Support structures used for removing air, skin, and overlap being generated')

    if generate_ptvs:
        # Build the name list for the targets
        PTVPrefix = "PTV"
        OTVPrefix = "OTV"
        sotvu_prefix = "sOTVu"
        PTVList = []
        PTVEvalList = []
        OTVList = []
        PTVEZList = []
        sotvu_list = []
        high_med_low_targets = False
        numbered_targets = True
        for index, target in enumerate(input_source_list):
            if high_med_low_targets:
                NumMids = len(input_source_list) - 2
                if index == 0:
                    PTVName = PTVPrefix + "_High"
                    PTVEvalName = PTVPrefix + "_Eval_High"
                    PTVEZName = PTVPrefix + "_EZ_High"
                    OTVName = OTVPrefix + "_High"
                    sotvu_name = sotvu_prefix + "_High"
                elif index == len(input_source_list) - 1:
                    PTVName = PTVPrefix + "_Low"
                    PTVEvalName = PTVPrefix + "_Eval_Low"
                    PTVEZName = PTVPrefix + "_EZ_Low"
                    OTVName = OTVPrefix + "_Low"
                    sotvu_name = sotvu_prefix + "_Low"
                else:
                    MidTargetNumber = index - 1
                    PTVName = PTVPrefix + "_Mid" + str(MidTargetNumber)
                    PTVEvalName = PTVPrefix + "_Eval_Mid" + str(MidTargetNumber)
                    PTVEZName = PTVPrefix + "_EZ_Mid" + str(MidTargetNumber)
                    OTVName = OTVPrefix + "_Mid" + str(MidTargetNumber)
                    sotvu_name = sotvu_prefix + "_Mid" + str(MidTargetNumber)
            elif numbered_targets:
                PTVName = PTVPrefix + str(index + 1) + '_' + source_doses[index]
                PTVEvalName = PTVPrefix + str(index + 1) + '_Eval_' + source_doses[index]
                PTVEZName = PTVPrefix + str(index + 1) + '_EZ_' + source_doses[index]
                OTVName = OTVPrefix + str(index + 1) + '_' + source_doses[index]
                sotvu_name = sotvu_prefix + str(index + 1) + '_' + source_doses[index]
            PTVList.append(PTVName)
            PTVEvalList.append(PTVEvalName)
            PTVEZList.append(PTVEZName)
            OTVList.append(OTVName)
            sotvu_list.append(sotvu_name)
        else:
            logging.debug("Generate PTV's off - a nonsupported operation")

    TargetColors = ["Red", "Green", "Blue", "Yellow", "Orange", "Purple"]

    # Redraw the clean external volume if necessary
    try:
        StructureName = "ExternalClean"
        retval_ExternalClean = case.PatientModel.RegionsOfInterest[StructureName]
        logging.warning("Structure " + StructureName + " exists.  Using predefined structure.")
    except:
        retval_ExternalClean = case.PatientModel.CreateRoi(Name="ExternalClean", Color="Green", Type="External",
                                                           TissueName="", RbeCellTypeName=None, RoiMaterial=None)
        retval_ExternalClean.CreateExternalGeometry(Examination=examination, ThresholdLevel=None)
        InExternalClean = case.PatientModel.RegionsOfInterest['ExternalClean']
        retval_ExternalClean.VolumeThreshold(InputRoi=InExternalClean, Examination=examination, MinVolume=1,
                                             MaxVolume=200000)
        retval_ExternalClean.SetAsExternal()
        newly_generated_rois.append('External_Clean')

    if GenerateSkin:
        Skin_defs = {
            "StructureName": "Skin",
            "ExcludeFromExport": True,
            "VisualizeStructure": False,
            "StructColor": " Blue",
            "OperationA": "Union",
            "SourcesA": ["ExternalClean"],
            "MarginTypeA": "Expand",
            "ExpA": [0, 0, 0, 0, 0, 0],
            "OperationB": "Union",
            "SourcesB": ["ExternalClean"],
            "MarginTypeB": "Contract",
            "ExpB": [skin_contraction]*6,
            "OperationResult": "Subtraction",
            "MarginTypeR": "Expand",
            "ExpR": [0, 0, 0, 0, 0, 0],
            "StructType": "Undefined"}
        make_boolean_structure(patient=patient, case=case, examination=examination, **Skin_defs)
        newly_generated_rois.append('Skin')
    # Generate the UnderDose structure and the UnderDose_Exp structure
    if generate_underdose:
        print "Creating UnderDose ROI using Sources: {}".format(underdose_structures)
        # Generate the UnderDose structure
        underdose_defs = {
            "StructureName": "UnderDose",
            "ExcludeFromExport": True,
            "VisualizeStructure": False,
            "StructColor": " Blue",
            "OperationA": "Union",
            "SourcesA": underdose_structures,
            "MarginTypeA": "Expand",
            "ExpA": [0, 0, 0, 0, 0, 0],
            "OperationB": "Union",
            "SourcesB": [],
            "MarginTypeB": "Expand",
            "ExpB": [0, 0, 0, 0, 0, 0],
            "OperationResult": "None",
            "MarginTypeR": "Expand",
            "ExpR": [0, 0, 0, 0, 0, 0],
            "StructType": "Undefined"}
        make_boolean_structure(patient=patient, case=case, examination=examination, **underdose_defs)
        newly_generated_rois.append('UnderDose')
        UnderDoseExp_defs = {
            "StructureName": "UnderDose_Exp",
            "ExcludeFromExport": True,
            "VisualizeStructure": False,
            "StructColor": " 255, 0, 255",
            "OperationA": "Union",
            "SourcesA": underdose_structures,
            "MarginTypeA": "Expand",
            "ExpA": [underdose_standoff]*6,
            "OperationB": "Union",
            "SourcesB": [],
            "MarginTypeB": "Expand",
            "ExpB": [0, 0, 0, 0, 0, 0],
            "OperationResult": "None",
            "MarginTypeR": "Expand",
            "ExpR": [0, 0, 0, 0, 0, 0],
            "StructType": "Undefined"}
        make_boolean_structure(patient=patient, case=case, examination=examination, **UnderDoseExp_defs)
        newly_generated_rois.append('UnderDose_Exp')

    # Generate the UniformDose structure
    if generate_uniformdose:
        print "Creating UniformDose ROI using Sources: {}".format(uniformdose_structures)
        if generate_underdose:
            print "UnderDose structures required, excluding overlap from UniformDose"
            uniformdose_defs = {
                "StructureName": "UniformDose",
                "ExcludeFromExport": True,
                "VisualizeStructure": False,
                "StructColor": " Blue",
                "OperationA": "Union",
                "SourcesA": uniformdose_structures,
                "MarginTypeA": "Expand",
                "ExpA": [0, 0, 0, 0, 0, 0],
                "OperationB": "Union",
                "SourcesB": underdose_structures,
                "MarginTypeB": "Expand",
                "ExpB": [0, 0, 0, 0, 0, 0],
                "OperationResult": "Subtraction",
                "MarginTypeR": "Expand",
                "ExpR": [0, 0, 0, 0, 0, 0],
                "StructType": "Undefined"}
        else:
            uniformdose_defs = {
                "StructureName": "UniformDose",
                "ExcludeFromExport": True,
                "VisualizeStructure": False,
                "StructColor": " Blue",
                "OperationA": "Union",
                "SourcesA": uniformdose_structures,
                "MarginTypeA": "Expand",
                "ExpA": [0, 0, 0, 0, 0, 0],
                "OperationB": "Union",
                "SourcesB": [],
                "MarginTypeB": "Expand",
                "ExpB": [0, 0, 0, 0, 0, 0],
                "OperationResult": "None",
                "MarginTypeR": "Expand",
                "ExpR": [0, 0, 0, 0, 0, 0],
                "StructType": "Undefined"}
        make_boolean_structure(patient=patient, case=case, examination=examination, **uniformdose_defs)
        newly_generated_rois.append('UniformDose')

    status.next_step(text='Targets being generated')
    # Make the primary targets, PTV1... these are limited by external and overlapping targets
    if generate_ptvs:
        # Limit each target to the ExternalClean surface
        ptv_sources = ['ExternalClean']
        # Initially, there are no targets to use in the subtraction
        subtract_targets = []
        for index, target in enumerate(input_source_list):
            print "Creating main target {}: {}".format(index, PTVList[index])
            ptv_sources.append(target)
            if index == 0:
                ptv_definitions = {
                    "StructureName": PTVList[index],
                    "ExcludeFromExport": True,
                    "VisualizeStructure": False,
                    "StructColor": TargetColors[index],
                    "OperationA": "Union",
                    "SourcesA": [target],
                    "MarginTypeA": "Expand",
                    "ExpA": [0, 0, 0, 0, 0, 0],
                    "OperationB": "Union",
                    "SourcesB": [],
                    "MarginTypeB": "Expand",
                    "ExpB": [0, 0, 0, 0, 0, 0],
                    "OperationResult": "None",
                    "MarginTypeR": "Expand",
                    "ExpR": [0, 0, 0, 0, 0, 0],
                    "StructType": "Ptv"}
            else:
                ptv_definitions = {
                    "StructureName": PTVList[index],
                    "ExcludeFromExport": True,
                    "VisualizeStructure": False,
                    "StructColor": TargetColors[index],
                    "OperationA": "Union",
                    "SourcesA": [target],
                    "MarginTypeA": "Expand",
                    "ExpA": [0, 0, 0, 0, 0, 0],
                    "OperationB": "Union",
                    "SourcesB": subtract_targets,
                    "MarginTypeB": "Expand",
                    "ExpB": [0, 0, 0, 0, 0, 0],
                    "OperationResult": "Subtraction",
                    "MarginTypeR": "Expand",
                    "ExpR": [0, 0, 0, 0, 0, 0],
                    "StructType": "Ptv"}
            make_boolean_structure(patient=patient, case=case, examination=examination, **ptv_definitions)
            newly_generated_rois.append(ptv_definitions.get("StructureName"))
            subtract_targets.append(PTVList[index])

    # Make the InnerAir structure
    if generate_inner_air:
        # Automated build of the Air contour
        try:
            retval_AIR = case.PatientModel.RegionsOfInterest["Air"]
        except:
            retval_AIR = case.PatientModel.CreateRoi(Name="Air", Color="Green", Type="Undefined", TissueName=None,
                                                     RbeCellTypeName=None, RoiMaterial=None)
            newly_generated_rois.append('Air')
        retval_AIR.GrayLevelThreshold(Examination=examination, LowThreshold=-1024, HighThreshold=InnerAirHU, PetUnit="",
                                      CbctUnit=None, BoundingBox=None)

        inner_air_defs = {
            "StructureName": "InnerAir",
            "ExcludeFromExport": True,
            "VisualizeStructure": False,
            "StructColor": " SaddleBrown",
            "OperationA": "Intersection",
            "SourcesA": ["ExternalClean", "Air"],
            "MarginTypeA": "Expand",
            "ExpA": [0, 0, 0, 0, 0, 0],
            "OperationB": "Union",
            "SourcesB": PTVList,
            "MarginTypeB": "Expand",
            "ExpB": [1, 1, 1, 1, 1, 1],
            "OperationResult": "Intersection",
            "MarginTypeR": "Expand",
            "ExpR": [0, 0, 0, 0, 0, 0],
            "StructType": "Undefined"}
        make_boolean_structure(patient=patient, case=case, examination=examination, **inner_air_defs)
        InAir = case.PatientModel.RegionsOfInterest['InnerAir']
        InAir.VolumeThreshold(InputRoi=InAir, Examination=examination, MinVolume=0.1, MaxVolume=500)
        newly_generated_rois.append('InnerAir')

    # Make the PTVEZ objects now
    if generate_underdose:
        # Loop over the PTV_EZs
        for index, target in enumerate(PTVList):
            ptv_ez_name = 'PTV' + str(index + 1) + '_EZ'
            print "Creating exclusion zone target {}: {}".format(str(index + 1), ptv_ez_name)
            # Generate the PTV_EZ
            PTVEZ_defs = {
                "StructureName": PTVEZList[index],
                "ExcludeFromExport": True,
                "VisualizeStructure": False,
                "StructColor": TargetColors[index],
                "OperationA": "Union",
                "SourcesA": [target],
                "MarginTypeA": "Expand",
                "ExpA": [0, 0, 0, 0, 0, 0],
                "OperationB": "Union",
                "SourcesB": ["UnderDose"],
                "MarginTypeB": "Expand",
                "ExpB": [0, 0, 0, 0, 0, 0],
                "OperationResult": "Intersection",
                "MarginTypeR": "Expand",
                "ExpR": [0, 0, 0, 0, 0, 0],
                "StructType": "Ptv"}
            make_boolean_structure(
                patient=patient,
                case=case,
                examination=examination,
                **PTVEZ_defs)
            newly_generated_rois.append(PTVEZ_defs.get("StructureName"))

    # make the sOTVu structures now
    if generate_uniformdose:
        # Loop over the sOTVu's
        for index, target in enumerate(PTVList):
            print "Creating uniform zone target {}: {}".format(str(index + 1), sotvu_name)
            # Generate the sOTVu
            sotvu_defs = {
                "StructureName": sotvu_list[index],
                "ExcludeFromExport": True,
                "VisualizeStructure": False,
                "StructColor": TargetColors[index],
                "OperationA": "Union",
                "SourcesA": [target],
                "MarginTypeA": "Expand",
                "ExpA": [0, 0, 0, 0, 0, 0],
                "OperationB": "Union",
                "SourcesB": ["UniformDose"],
                "MarginTypeB": "Expand",
                "ExpB": [uniformdose_standoff]*6,
                "OperationResult": "Intersection",
                "MarginTypeR": "Expand",
                "ExpR": [0, 0, 0, 0, 0, 0],
                "StructType": "Ptv"}
            make_boolean_structure(
                patient=patient,
                case=case,
                examination=examination,
                **sotvu_defs)
            newly_generated_rois.append(sotvu_defs.get("StructureName"))

    # We will subtract the adjoining air, skin, or Priority 1 ROI that overlaps the target
    if generate_ptv_evals:
        EvalSubtract = ['Skin', 'InnerAir', 'UnderDose']
        for index, target in enumerate(PTVList):
            logging.debug("Creating evaluation target {}: {}".format(str(index + 1), PTVEvalList[index]))
            # Set the Sources Structure for Evals
            PTVEval_defs = {
                "StructureName": PTVEvalList[index],
                "ExcludeFromExport": True,
                "VisualizeStructure": False,
                "StructColor": TargetColors[index],
                "OperationA": "Union",
                "SourcesA": [target],
                "MarginTypeA": "Expand",
                "ExpA": [0, 0, 0, 0, 0, 0],
                "OperationB": "Union",
                "SourcesB": EvalSubtract,
                "MarginTypeB": "Expand",
                "ExpB": [0, 0, 0, 0, 0, 0],
                "OperationResult": "Subtraction",
                "MarginTypeR": "Expand",
                "ExpR": [0, 0, 0, 0, 0, 0],
                "StructType": "Ptv"}
            make_boolean_structure(patient=patient, case=case, examination=examination, **PTVEval_defs)
            newly_generated_rois.append(PTVEval_defs.get("StructureName"))
            # Append the current target to the list of targets to subtract in the next iteration
            EvalSubtract.append(target)

    # Generate the OTV's
    # Build a region called z_derived_not_exp_underdose that does not include the underdose expansion
    if generate_otvs:
        otv_intersect = []
        otv_subtract = []
        # If the UnderDose structure has contours, then we must create a ~underdose_exp structure
        if case.PatientModel.StructureSets[examination.Name].RoiGeometries['UnderDose_Exp'].HasContours():
            not_exp_underdose_definitions = {
                "StructureName": "z_derived_not_exp_underdose",
                "ExcludeFromExport": True,
                "VisualizeStructure": False,
                "StructColor": "192, 192, 192",
                "OperationA": "Union",
                "SourcesA": ["ExternalClean"],
                "MarginTypeA": "Expand",
                "ExpA": [0] * 6,
                "OperationB": "Union",
                "SourcesB": ["UnderDose_Exp"],
                "MarginTypeB": "Expand",
                "ExpB": [0] * 6,
                "OperationResult": "Subtraction",
                "MarginTypeR": "Expand",
                "ExpR": [0] * 6,
                "StructType": "Undefined"}
            make_boolean_structure(patient=patient,
                                   case=case,
                                   examination=examination,
                                   **not_exp_underdose_definitions)
            newly_generated_rois.append(not_exp_underdose_definitions.get("StructureName"))
            otv_intersect.append(not_exp_underdose_definitions.get("StructureName"))


        for index, target in enumerate(PTVList):
            OTV_defs = {
                "StructureName": OTVList[index],
                "ExcludeFromExport": True,
                "VisualizeStructure": False,
                "StructColor": TargetColors[index],
                "OperationA": "Intersection",
                "SourcesA": [PTVEvalList[index]] + otv_intersect,
                "MarginTypeA": "Expand",
                "ExpA": [0, 0, 0, 0, 0, 0],
                "OperationB": "Union",
                "SourcesB": otv_subtract,
                "MarginTypeB": "Expand",
                "ExpB": [otv_standoff] * 6,
                "OperationResult": "Subtraction",
                "MarginTypeR": "Expand",
                "ExpR": [0, 0, 0, 0, 0, 0],
                "StructType": "Ptv"}
            make_boolean_structure(patient=patient,
                                   case=case,
                                   examination=examination,
                                   **OTV_defs)
            newly_generated_rois.append(OTV_defs.get("StructureName"))
            otv_subtract.append(PTVList[index])

    # Target creation complete moving on to rings
    status.next_step(text='Rings being generated')

    if generate_target_rings:
        logging.debug('Target specific rings being constructed')
        # First make an ExternalClean-limited expansion volume
        # This will be the outer boundary for any expansion
        z_derived_maxhd_defs = {
            "StructureName": "z_derived_maxhd",
            "ExcludeFromExport": True,
            "VisualizeStructure": False,
            "StructColor": " 255, 0, 255",
            "SourcesA": ["ExternalClean"],
            "MarginTypeA": "Expand",
            "ExpA": [thickness_hd_ring] * 6,
            "OperationA": "Union",
            "SourcesB": PTVList,
            "MarginTypeB": "Expand",
            "ExpB": [ring_standoff+thickness_hd_ring]*6,
            "OperationB": "Union",
            "MarginTypeR": "Expand",
            "ExpR": [0, 0, 0, 0, 0, 0],
            "OperationResult": "Subtraction",
            "StructType": "Undefined"}
        make_boolean_structure(patient=patient,
                               case=case,
                               examination=examination,
                               **z_derived_maxhd_defs)
        newly_generated_rois.append(z_derived_maxhd_defs.get("StructureName"))

        z_derived_targets_plus_standoff_hd_defs = {
            "StructureName": "z_derived_targets_plus_standoff_hd_defs",
            "ExcludeFromExport": True,
            "VisualizeStructure": False,
            "StructColor": " 255, 0, 255",
            "SourcesA": PTVList,
            "MarginTypeA": "Expand",
            "ExpA": [thickness_hd_ring] * 6,
            "OperationA": "Union",
            "SourcesB": [],
            "MarginTypeB": "Expand",
            "ExpB": [0, 0, 0, 0, 0, 0],
            "OperationB": "Union",
            "MarginTypeR": "Expand",
            "ExpR": [0, 0, 0, 0, 0, 0],
            "OperationResult": "None",
            "StructType": "Undefined"}
        make_boolean_structure(patient=patient,
                               case=case,
                               examination=examination,
                               **z_derived_targets_plus_standoff_hd_defs)
        newly_generated_rois.append(z_derived_targets_plus_standoff_hd_defs.get("StructureName"))
        # Now generate a ring for each target
        # Each iteration will add the higher dose targets and rings to the subtract list for subsequent rings
        ring_avoid_subtract = [z_derived_maxhd_defs.get("StructureName"),
                               z_derived_targets_plus_standoff_hd_defs.get("StructureName")]
        for index, target in enumerate(PTVList):
            ring_name = "ring" + str(index+1) + "_" + source_doses[index]
            target_ring_defs = {
                "StructureName": ring_name,
                "ExcludeFromExport": True,
                "VisualizeStructure": False,
                "StructColor": TargetColors[index],
                "OperationA": "Union",
                "SourcesA": [target],
                "MarginTypeA": "Expand",
                "ExpA": [thickness_ld_ring]*6,
                "OperationB": "Union",
                "SourcesB": ring_avoid_subtract,
                "MarginTypeB": "Expand",
                "ExpB": [0, 0, 0, 0, 0, 0],
                "OperationResult": "Subtraction",
                "MarginTypeR": "Expand",
                "ExpR": [0, 0, 0, 0, 0, 0],
                "StructType": "Avoidance"}
            make_boolean_structure(patient=patient, case=case, examination=examination, **target_ring_defs)
            newly_generated_rois.append(target_ring_defs.get("StructureName"))
            # Append the current target to the list of targets to subtract in the next iteration
            ring_avoid_subtract.append(target)

        # RingLD
        if GenerateRingLD:
            # First make an ExternalClean-limited expansion volume
            # Would a sequential expansion be faster?
            z_derived_maxld_defs = {
                "StructureName": "z_derived_maxld",
                "ExcludeFromExport": True,
                "VisualizeStructure": False,
                "StructColor": " 255, 0, 255",
                "SourcesA": PTVList,
                "MarginTypeA": "Expand",
                "ExpA": [thickness_ld_ring] * 6,
                "OperationA": "Union",
                "SourcesB": ["ExternalClean"],
                "MarginTypeB": "Expand",
                "ExpB": [0, 0, 0, 0, 0, 0],
                "OperationB": "Union",
                "MarginTypeR": "Expand",
                "ExpR": [0, 0, 0, 0, 0, 0],
                "OperationResult": "Intersection",
                "StructType": "Undefined"}
            make_boolean_structure(patient=patient, case=case, examination=examination, **z_derived_maxld_defs)
            newly_generated_rois.append(z_derived_maxld_defs.get("StructureName"))

            RingLD_defs = {
                "StructureName": "RingLD",
                "ExcludeFromExport": True,
                "VisualizeStructure": False,
                "StructColor": " 255, 0, 255",
                "SourcesA": ["z_derived_maxld"],
                "MarginTypeA": "Expand",
                "ExpA": [0, 0, 0, 0, 0, 0],
                "OperationA": "Union",
                "SourcesB": PTVList,
                "MarginTypeB": "Expand",
                "ExpB": [ring_standoff] * 6,
                "OperationB": "Union",
                "MarginTypeR": "Expand",
                "ExpR": [0, 0, 0, 0, 0, 0],
                "OperationResult": "Subtraction",
                "StructType": "Undefined"}
            make_boolean_structure(patient=patient, case=case, examination=examination, **RingLD_defs)
            newly_generated_rois.append(RingLD_defs.get("StructureName"))
    else:
        # RingHD
        if generate_ring_hd:
            # First make an ExternalClean-limited expansion volume
            z_derived_maxhd_defs = {
                "StructureName": "z_derived_maxhd",
                "ExcludeFromExport": True,
                "VisualizeStructure": False,
                "StructColor": " 255, 0, 255",
                "SourcesA": PTVList,
                "MarginTypeA": "Expand",
                "ExpA": [thickness_hd_ring]*6,
                "OperationA": "Union",
                "SourcesB": ["ExternalClean"],
                "MarginTypeB": "Expand",
                "ExpB": [0, 0, 0, 0, 0, 0],
                "OperationB": "Union",
                "MarginTypeR": "Expand",
                "ExpR": [0, 0, 0, 0, 0, 0],
                "OperationResult": "Intersection",
                "StructType": "Undefined"}
            make_boolean_structure(patient=patient, case=case, examination=examination, **z_derived_maxhd_defs)
            newly_generated_rois.append(z_derived_maxhd_defs.get("StructureName"))

            RingHD_defs = {
                "StructureName": "Ring_HD",
                "ExcludeFromExport": True,
                "VisualizeStructure": False,
                "StructColor": " 255, 0, 255",
                "SourcesA": ["z_derived_maxhd"],
                "MarginTypeA": "Expand",
                "ExpA": [0, 0, 0, 0, 0, 0],
                "OperationA": "Union",
                "SourcesB": PTVList,
                "MarginTypeB": "Expand",
                "ExpB": [ring_standoff]*6,
                "OperationB": "Union",
                "MarginTypeR": "Expand",
                "ExpR": [0, 0, 0, 0, 0, 0],
                "OperationResult": "Subtraction",
                "StructType": "Undefined"}
            make_boolean_structure(patient=patient, case=case, examination=examination, **RingHD_defs)
            newly_generated_rois.append(RingHD_defs.get("StructureName"))



        # RingLD
        if GenerateRingLD:
            # First make an ExternalClean-limited expansion volume
            # Would a sequential expansion be faster?
            z_derived_maxld_defs = {
                "StructureName": "z_derived_maxld",
                "ExcludeFromExport": True,
                "VisualizeStructure": False,
                "StructColor": " 255, 0, 255",
                "SourcesA": PTVList,
                "MarginTypeA": "Expand",
                "ExpA": [thickness_ld_ring]*6,
                "OperationA": "Union",
                "SourcesB": ["ExternalClean"],
                "MarginTypeB": "Expand",
                "ExpB": [0, 0, 0, 0, 0, 0],
                "OperationB": "Union",
                "MarginTypeR": "Expand",
                "ExpR": [0, 0, 0, 0, 0, 0],
                "OperationResult": "Intersection",
                "StructType": "Undefined"}
            make_boolean_structure(patient=patient, case=case, examination=examination, **z_derived_maxld_defs)
            newly_generated_rois.append(z_derived_maxld_defs.get("StructureName"))

            RingLD_defs = {
                "StructureName": "RingLD",
                "ExcludeFromExport": True,
                "VisualizeStructure": False,
                "StructColor": " 255, 0, 255",
                "SourcesA": ["z_derived_maxld"],
                "MarginTypeA": "Expand",
                "ExpA": [0, 0, 0, 0, 0, 0],
                "OperationA": "Union",
                "SourcesB": PTVList,
                "MarginTypeB": "Expand",
                "ExpB": [ring_standoff]*6,
                "OperationB": "Union",
                "MarginTypeR": "Expand",
                "ExpR": [0, 0, 0, 0, 0, 0],
                "OperationResult": "Subtraction",
                "StructType": "Undefined"}
            make_boolean_structure(patient=patient, case=case, examination=examination, **RingLD_defs)
            newly_generated_rois.append(RingLD_defs.get("StructureName"))

    # Normal_2cm
    if GenerateNormal_2cm:
        Normal_2cm_defs = {
            "StructureName": "Normal_2cm",
            "ExcludeFromExport": True,
            "VisualizeStructure": False,
            "StructColor": " 255, 0, 255",
            "SourcesA": ["ExternalClean"],
            "MarginTypeA": "Expand",
            "ExpA": [0, 0, 0, 0, 0, 0],
            "OperationA": "Union",
            "SourcesB": PTVList,
            "MarginTypeB": "Expand",
            "ExpB": [2, 2, 2, 2, 2, 2],
            "OperationB": "Union",
            "MarginTypeR": "Expand",
            "ExpR": [0, 0, 0, 0, 0, 0],
            "OperationResult": "Subtraction",
            "StructType": "Undefined"}
        make_boolean_structure(patient=patient, case=case, examination=examination, **Normal_2cm_defs)
        newly_generated_rois.append(Normal_2cm_defs.get("StructureName"))

    #if dialogresponse == {}:
    #    status.finish('Script cancelled, inputs were not supplied')
    #    sys.exit('Script cancelled')
    status.finish(text='The script executed successfully')


if __name__ == '__main__':
    main()
