""" Whole Brain AutoBlock

    Creates the structures required for the auto-whole brain block.
    
    This python script will generate a PTV_WB_xxxx that attempts to capture the whole brain
    contour to the C1 interface.  In the first iteration, this will simply generate the 
    structures that will be used to populate the UW Template.  In future iterations we 
    will be updating this script to load beam templates and create the actual plan.   

    How To Use: After insertion of S-frame this script is run to generate the blocking 
                structures for a whole brain plan


    Validation Notes: 
    
    Version Notes: 1.0.0 Original
    1.0.1 Hot Fix to apparent error in version 7
  
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

__author__ = 'Adam Bayliss'
__contact__ = 'rabayliss@wisc.edu'
__date__ = '01-Feb-2018'
__version__ = '1.0.1'
__status__ = 'Production'
__deprecated__ = False
__reviewer__ = ''
__reviewed__ = ''
__raystation__ = '7.0.0'
__maintainer__ = 'One maintainer'
__email__ = 'rabayliss@wisc.edu'
__license__ = 'GPLv3'
__copyright__ = 'Copyright (C) 2018, University of Wisconsin Board of Regents'
__help__ = 'https://github.com/mwgeurts/ray_scripts/wiki/User-Interface'
__credits__ = []

import connect
import logging
import UserInterface
import random
import sys


def check_structure_exists(case, structure_name, roi_list, option):
    if any(roi.OfRoi.Name == structure_name for roi in roi_list):
        if option == 'Delete':
            case.PatientModel.RegionsOfInterest[structure_name].DeleteRoi()
            logging.warning(structure_name + 'found - deleting and creating')
        elif option == 'Check':
            connect.await_user_input(
                'Contour {} Exists - Verify its accuracy and continue script'.format(structure_name))
        return True
    else:
        logging.debug('Structure {} not found, and will be created'.format(structure_name))
        return False


def main():
    try:
        patient = connect.get_current('Patient')
        case = connect.get_current("Case")
        examination = connect.get_current("Examination")
    except:
        logging.warning("Aww crap, No patient")

    machine_names = ['TrueBeamSTx', 'TrueBeam']
    # Capture the current list of ROI's to avoid saving over them in the future
    rois = case.PatientModel.StructureSets[examination.Name].RoiGeometries

    # Capture the current list of POI's to avoid a crash
    pois = case.PatientModel.PointsOfInterest

    status = UserInterface.ScriptStatus(
        steps=['SimFiducials point declaration',
               'Making the target',
               'Verify PTV_WB_xxxx coverage',
               'User Inputs Plan Information',
               'Regions at Risk Generation/Validation',
               'Target (BTV) Generation',
               'Plan Generation'],
        docstring=__doc__,
        help=__help__)

    # Look for the sim point, if not create a point
    sim_point_found = any(poi.Name == 'SimFiducials' for poi in pois)
    if sim_point_found:
        logging.warning("POI SimFiducials Exists")
        status.next_step(text="SimFiducials Point found, ensure that it is placed properly")
        connect.await_user_input('Ensure Correct placement of the SimFiducials Point and continue script.')
    else:
        case.PatientModel.CreatePoi(Examination=examination,
                                    Point={'x': 0,
                                           'y': 0,
                                           'z': 0},
                                    Volume=0,
                                    Name="SimFiducials",
                                    Color="Green",
                                    Type="LocalizationPoint")
        status.next_step(text="SimFiducials POI created, ensure that it is placed properly")
        connect.await_user_input('Ensure Correct placement of the SimFiducials Point and continue script.')

    status.next_step(text="The PTV_WB_xxxx target is being generated")
    if not check_structure_exists(case=case, structure_name='PTV_WB_xxxx', roi_list=rois, option='Check'):
        case.PatientModel.MBSAutoInitializer(
            MbsRois=[{'CaseType': "HeadNeck",
                      'ModelName': "Brain",
                      'RoiName': "PTV_WB_xxxx",
                      'RoiColor': "255, 255, 0"}],
            CreateNewRois=True,
            Examination=examination,
            UseAtlasBasedInitialization=True)

        case.PatientModel.AdaptMbsMeshes(Examination=examination,
                                         RoiNames=["PTV_WB_xxxx"],
                                         CustomStatistics=None,
                                         CustomSettings=None)

        case.PatientModel.RegionsOfInterest['PTV_WB_xxxx'].AdaptMbsMesh(
            Examination=examination,
            CustomStatistics=None,
            CustomSettings=[{'ShapeWeight': 0.5,
                             'TargetWeight': 1,
                             'MaxIterations': 100,
                             'OnlyRigidAdaptation': False,
                             'ConvergenceCheck': False}])
        status.next_step(text="The target was auto-generated based on the brain," +
                              " and the computer is not very smart. Check the PTV_WB_xxxx carefully")
    else:
        status.next_step(text="Existing target was used. Check the PTV_WB_xxxx carefully")

    case.PatientModel.RegionsOfInterest['PTV_WB_xxxx'].Type = "Ptv"

    case.PatientModel.RegionsOfInterest['PTV_WB_xxxx'].OrganData.OrganType = "Target"

    connect.await_user_input('Ensure the PTV_WB_xxxx encompasses the brain and C1 and continue playing the script')

    status.next_step(text="Complete plan information - check the TPO for doses " +
                          "and ARIA for the treatment machine")
    # This dialog grabs the relevant parameters to generate the whole brain plan
    make_plan = True
    if make_plan:
        input_dialog = UserInterface.InputDialog(
            inputs={
                'input0_make_plan': 'Create the RayStation Plan',
                'input1_plan_name': 'Enter the Plan Name, typically Brai_3DC_R0A0',
                'input2_number_fractions': 'Enter the number of fractions',
                'input3_dose': 'Enter total dose in cGy',
                'input4_choose_machine': 'Choose Treatment Machine'
            },
            title='Whole Brain Plan Input',
            datatype={'input0_make_plan': 'check',
                      'input4_choose_machine': 'combo'
                      },
            initial={
                'input0_make_plan': ['Make Plan'],
                'input1_plan_name': 'Brai_3DC_R0A0',
            },
            options={'input0_make_plan': ['Make Plan'],
                     'input4_choose_machine': machine_names,
                     },
            required=['input2_number_fractions',
                      'input3_dose',
                      'input4_choose_machine'])

        # Launch the dialog
        print input_dialog.show()

        # Parse the outputs
        # User selected that they want a plan-stub made
        if 'Make Plan' in input_dialog.values['input0_make_plan']:
            make_plan = True
        else:
            make_plan = False
        plan_name = input_dialog.values['input1_plan_name']
        number_of_fractions = float(input_dialog.values['input2_number_fractions'])
        total_dose = float(input_dialog.values['input3_dose'])
        plan_machine = input_dialog.values['input4_choose_machine']

    status.next_step(text="Regions at risk will be created including Globes, Lenses, and Brain.")
    brain_exists = check_structure_exists(case=case,
                                          structure_name='Brain',
                                          roi_list=rois,
                                          option='Check')
    if not brain_exists:
        case.PatientModel.MBSAutoInitializer(
            MbsRois=[{'CaseType': "HeadNeck",
                      'ModelName': "Brain",
                      'RoiName': "Brain",
                      'RoiColor': "255, 255, 0"}],
            CreateNewRois=True,
            Examination=examination,
            UseAtlasBasedInitialization=True)
    if any(roi.OfRoi.Name == 'Globe_L' for roi in rois):
        connect.await_user_input('Globe_L Contour Exists - Verify its accuracy and continue script')
    else:
        case.PatientModel.MBSAutoInitializer(
            MbsRois=[{'CaseType': "HeadNeck",
                      'ModelName': "Eye (Left)",
                      'RoiName': "Globe_L",
                      'RoiColor': "255, 128, 0"}],
            CreateNewRois=True,
            Examination=examination,
            UseAtlasBasedInitialization=True)
    if any(roi.OfRoi.Name == 'Globe_R' for roi in rois):
        connect.await_user_input('Globe_R Contour Exists - Verify its accuracy and continue script')
    else:
        case.PatientModel.MBSAutoInitializer(
            MbsRois=[{'CaseType': "HeadNeck",
                      'ModelName': "Eye (Right)",
                      'RoiName': "Globe_R",
                      'RoiColor': "255, 128, 0"}],
            CreateNewRois=True,
            Examination=examination,
            UseAtlasBasedInitialization=True)

    if not check_structure_exists(case=case, structure_name='Lens_L', roi_list=rois, option='Check'):
        case.PatientModel.CreateRoi(Name='Lens_L',
                                    Color="Purple",
                                    Type="Organ",
                                    TissueName=None,
                                    RbeCellTypeName=None,
                                    RoiMaterial=None)
        connect.await_user_input('Draw the LEFT Lens then continue playing the script')

    if not check_structure_exists(case=case, structure_name='Lens_R', roi_list=rois, option='Check'):
        case.PatientModel.CreateRoi(Name="Lens_R",
                                    Color="Purple",
                                    Type="Organ",
                                    TissueName=None,
                                    RbeCellTypeName=None,
                                    RoiMaterial=None)
        connect.await_user_input('Draw the RIGHT Lens then continue playing the script')

    if not check_structure_exists(case=case, structure_name='External', roi_list=rois, option='Check'):
        case.PatientModel.CreateRoi(Name="External",
                                    Color="Blue",
                                    Type="External",
                                    TissueName="",
                                    RbeCellTypeName=None,
                                    RoiMaterial=None)
        case.PatientModel.RegionsOfInterest['External'].CreateExternalGeometry(
            Examination=examination,
            ThresholdLevel=-250)

    if not check_structure_exists(case=case, roi_list=rois, option='Delete', structure_name='Lens_L_PRV05'):
        logging.debug('Lens_L_PRV05 not found, generating from expansion')

    case.PatientModel.CreateRoi(
        Name="Lens_L_PRV05",
        Color="255, 128, 0",
        Type="Avoidance",
        TissueName=None,
        RbeCellTypeName=None,
        RoiMaterial=None)
    case.PatientModel.RegionsOfInterest['Lens_L_PRV05'].ExcludeFromExport = True
    case.PatientModel.RegionsOfInterest['Lens_L_PRV05'].SetMarginExpression(
        SourceRoiName="Lens_L",
        MarginSettings={'Type': "Expand",
                        'Superior': 0.5,
                        'Inferior': 0.5,
                        'Anterior': 0.5,
                        'Posterior': 0.5,
                        'Right': 0.5,
                        'Left': 0.5})
    case.PatientModel.RegionsOfInterest['Lens_L_PRV05'].UpdateDerivedGeometry(
        Examination=examination, Algorithm="Auto")

    # The Lens_R prv will always be "remade"
    if not check_structure_exists(case=case, roi_list=rois, option='Delete', structure_name='Lens_R_PRV05'):
        logging.debug('Lens_R_PRV05 not found, generating from expansion')

    case.PatientModel.CreateRoi(
        Name="Lens_R_PRV05",
        Color="255, 128, 0",
        Type="Avoidance",
        TissueName=None,
        RbeCellTypeName=None,
        RoiMaterial=None)
    case.PatientModel.RegionsOfInterest['Lens_R_PRV05'].ExcludeFromExport = True
    case.PatientModel.RegionsOfInterest['Lens_R_PRV05'].SetMarginExpression(
        SourceRoiName="Lens_R",
        MarginSettings={'Type': "Expand",
                        'Superior': 0.5,
                        'Inferior': 0.5,
                        'Anterior': 0.5,
                        'Posterior': 0.5,
                        'Right': 0.5,
                        'Left': 0.5})
    case.PatientModel.RegionsOfInterest['Lens_R_PRV05'].UpdateDerivedGeometry(
        Examination=examination,
        Algorithm="Auto")

    if not check_structure_exists(case=case, roi_list=rois, option='Delete', structure_name='Avoid'):
        logging.debug('Avoid not found, generating from expansion')

    case.PatientModel.CreateRoi(Name="Avoid",
                                Color="255, 128, 128",
                                Type="Avoidance",
                                TissueName=None,
                                RbeCellTypeName=None,
                                RoiMaterial=None)
    case.PatientModel.RegionsOfInterest['Avoid'].ExcludeFromExport = True
    case.PatientModel.RegionsOfInterest['Avoid'].SetAlgebraExpression(
        ExpressionA={'Operation': "Union",
                     'SourceRoiNames': ["Lens_L_PRV05",
                                        "Lens_R_PRV05"],
                     'MarginSettings': {
                         'Type': "Expand",
                         'Superior': 0,
                         'Inferior': 0,
                         'Anterior': 0,
                         'Posterior': 0,
                         'Right': 0,
                         'Left': 0}},
        ExpressionB={'Operation': "Union",
                     'SourceRoiNames': [],
                     'MarginSettings': {
                         'Type': "Expand",
                         'Superior': 0,
                         'Inferior': 0,
                         'Anterior': 0,
                         'Posterior': 0,
                         'Right': 0,
                         'Left': 0}},
        ResultOperation="None",
        ResultMarginSettings={'Type': "Expand",
                              'Superior': 0,
                              'Inferior': 0,
                              'Anterior': 0,
                              'Posterior': 0,
                              'Right': 0,
                              'Left': 0})
    case.PatientModel.RegionsOfInterest['Avoid'].UpdateDerivedGeometry(
        Examination=examination,
        Algorithm="Auto")

    if not check_structure_exists(case=case, roi_list=rois, option='Delete', structure_name='BTV_Brain'):
        logging.debug('BTV_Brain not found, generating from expansion')

    case.PatientModel.CreateRoi(Name="BTV_Brain", Color="128, 0, 64", Type="Ptv", TissueName=None,
                                RbeCellTypeName=None, RoiMaterial=None)
    case.PatientModel.RegionsOfInterest['BTV_Brain'].ExcludeFromExport = True

    case.PatientModel.RegionsOfInterest['BTV_Brain'].SetMarginExpression(
        SourceRoiName="PTV_WB_xxxx",
        MarginSettings={'Type': "Expand",
                        'Superior': 1,
                        'Inferior': 0.5,
                        'Anterior': 0.8,
                        'Posterior': 2,
                        'Right': 1,
                        'Left': 1})
    case.PatientModel.RegionsOfInterest['BTV_Brain'].UpdateDerivedGeometry(
        Examination=examination,
        Algorithm="Auto")

    # Avoid_Face - creates a block that will avoid treating the face
    # This contour extends down 10 cm from the brain itself.  Once this is subtracted
    # from the brain - this will leave only the face
    if not check_structure_exists(case=case, roi_list=rois, option='Delete', structure_name='Avoid_Face'):
        logging.debug('Avoid_Face not found, generating from expansion')

    case.PatientModel.CreateRoi(Name="Avoid_Face",
                                Color="255, 128, 128",
                                Type="Organ",
                                TissueName=None,
                                RbeCellTypeName=None,
                                RoiMaterial=None)
    case.PatientModel.RegionsOfInterest['Avoid_Face'].ExcludeFromExport = True
    case.PatientModel.RegionsOfInterest['Avoid_Face'].SetMarginExpression(
        SourceRoiName="PTV_WB_xxxx",
        MarginSettings={'Type': "Expand",
                        'Superior': 0,
                        'Inferior': 10,
                        'Anterior': 0,
                        'Posterior': 0,
                        'Right': 0,
                        'Left': 0})
    case.PatientModel.RegionsOfInterest['Avoid_Face'].UpdateDerivedGeometry(
        Examination=examination,
        Algorithm="Auto")

    # BTV_Flash_20: a 2 cm expansion for flash except in the directions the MD's wish to have no flash
    # Per MD's flashed dimensions are superior, anterior, and posterior
    if not check_structure_exists(case=case, roi_list=rois, option='Delete', structure_name='BTV_Flash_20'):
        logging.debug('BTV_Flash_20 not found, generating from expansion')

    case.PatientModel.CreateRoi(Name="BTV_Flash_20",
                                Color="128, 0, 64",
                                Type="Ptv",
                                TissueName=None,
                                RbeCellTypeName=None,
                                RoiMaterial=None)

    case.PatientModel.RegionsOfInterest['BTV_Flash_20'].ExcludeFromExport = True
    case.PatientModel.RegionsOfInterest['BTV_Flash_20'].SetAlgebraExpression(
        ExpressionA={'Operation': "Union",
                     'SourceRoiNames': ["PTV_WB_xxxx"],
                     'MarginSettings': {'Type': "Expand",
                                        'Superior': 2,
                                        'Inferior': 0,
                                        'Anterior': 2,
                                        'Posterior': 2,
                                        'Right': 0,
                                        'Left': 0}},
        ExpressionB={'Operation': "Union",
                     'SourceRoiNames': ["Avoid_Face"],
                     'MarginSettings': {'Type': "Expand",
                                        'Superior': 0,
                                        'Inferior': 0,
                                        'Anterior': 0,
                                        'Posterior': 0,
                                        'Right': 0,
                                        'Left': 0}},
        ResultOperation="Subtraction",
        ResultMarginSettings={'Type': "Expand",
                              'Superior': 0,
                              'Inferior': 0,
                              'Anterior': 0,
                              'Posterior': 0,
                              'Right': 0,
                              'Left': 0})

    case.PatientModel.RegionsOfInterest['BTV_Flash_20'].UpdateDerivedGeometry(
        Examination=examination,
        Algorithm="Auto")

    # BTV: the block target volume.  It consists of the BTV_Brain, BTV_Flash_20 with no additional structures
    # We are going to make the BTV as a fixture if we are making a plan so that we can autoset the dose grid
    if not check_structure_exists(case=case, roi_list=rois, option='Delete', structure_name='BTV'):
        logging.debug('BTV not found, generating from expansion')

    if make_plan:
        btv_temporary_type = "Fixation"
    else:
        btv_temporary_type = "Ptv"

    case.PatientModel.CreateRoi(Name="BTV",
                                Color="Yellow",
                                Type=btv_temporary_type,
                                TissueName=None,
                                RbeCellTypeName=None,
                                RoiMaterial=None)
    case.PatientModel.RegionsOfInterest['BTV'].ExcludeFromExport = True
    case.PatientModel.RegionsOfInterest['BTV'].SetAlgebraExpression(
        ExpressionA={'Operation': "Union",
                     'SourceRoiNames': ["BTV_Brain",
                                        "BTV_Flash_20"],
                     'MarginSettings': {'Type': "Expand",
                                        'Superior': 0,
                                        'Inferior': 0,
                                        'Anterior': 0,
                                        'Posterior': 0,
                                        'Right': 0,
                                        'Left': 0}},
        ExpressionB={'Operation': "Intersection",
                     'SourceRoiNames': [],
                     'MarginSettings': {'Type': "Expand",
                                        'Superior': 0,
                                        'Inferior': 0,
                                        'Anterior': 0,
                                        'Posterior': 0,
                                        'Right': 0,
                                        'Left': 0}},
        ResultOperation="None",
        ResultMarginSettings={'Type': "Expand",
                              'Superior': 0,
                              'Inferior': 0,
                              'Anterior': 0,
                              'Posterior': 0,
                              'Right': 0,
                              'Left': 0})

    case.PatientModel.RegionsOfInterest['BTV'].UpdateDerivedGeometry(
        Examination=examination,
        Algorithm="Auto")

    if make_plan:
        patient.Save()

        try:
            case.AddNewPlan(
                PlanName=plan_name,
                PlannedBy="",
                Comment="",
                ExaminationName=examination.Name,
                AllowDuplicateNames=False)

        except Exception:
            plan_name = plan_name + str(random.randint(1, 999))
            case.AddNewPlan(
                PlanName=plan_name,
                PlannedBy="",
                Comment="",
                ExaminationName=examination.Name,
                AllowDuplicateNames=False)
        patient.Save()

        plan = case.TreatmentPlans[plan_name]
        plan.SetCurrent()

        plan.AddNewBeamSet(
            Name=plan_name,
            ExaminationName=examination.Name,
            MachineName=plan_machine,
            Modality="Photons",
            TreatmentTechnique="Conformal",
            PatientPosition="HeadFirstSupine",
            NumberOfFractions=number_of_fractions,
            CreateSetupBeams=True,
            UseLocalizationPointAsSetupIsocenter=False,
            Comment="",
            RbeModelReference=None,
            EnableDynamicTrackingForVero=False,
            NewDoseSpecificationPointNames=[],
            NewDoseSpecificationPoints=[],
            RespiratoryMotionCompensationTechnique="Disabled",
            RespiratorySignalSource="Disabled")

        beamset = plan.BeamSets[plan_name]
        patient.Save()
        beamset.SetCurrent()

        beamset.AddDosePrescriptionToRoi(RoiName='PTV_WB_xxxx',
                                         DoseVolume=0,
                                         PrescriptionType='MedianDose',
                                         DoseValue=total_dose,
                                         RelativePrescriptionLevel=1,
                                         AutoScaleDose=True)
        plan.SetDefaultDoseGrid(VoxelSize={'x': 0.2,
                                           'y': 0.2,
                                           'z': 0.2})
        # Set the BTV type above to allow dose grid to cover
        case.PatientModel.RegionsOfInterest['BTV'].Type = 'Ptv'
        try:
            isocenter_position = case.PatientModel.StructureSets[examination.Name]. \
                RoiGeometries['PTV_WB_xxxx'].GetCenterOfRoi()
        except Exception:
            logging.debug('Aborting, could not locate center of PTV_WB_xxxx')
            sys.exit
        ptv_wb_xxxx_center = {'x': isocenter_position.x,
                              'y': isocenter_position.y,
                              'z': isocenter_position.z}
        isocenter_parameters = beamset.CreateDefaultIsocenterData(Position=ptv_wb_xxxx_center)
        isocenter_parameters['Name'] = "iso_" + plan_name
        isocenter_parameters['NameOfIsocenterToRef'] = "iso_" + plan_name
        logging.debug('Isocenter chosen based on center of PTV_WB_xxxx.'+
        'Parameters are: x={}, y={}:, z={}, assigned to isocenter name{}'.format(
            ptv_wb_xxxx_center['x'],
            ptv_wb_xxxx_center['y'],
            ptv_wb_xxxx_center['z'],
            isocenter_parameters['Name']))

        beamset.CreatePhotonBeam(Energy=6,
                                 IsocenterData=isocenter_parameters,
                                 Name='1_Brai_g270c355',
                                 Description='1 3DC: MLC Static Field',
                                 GantryAngle=270.0,
                                 CouchAngle=355,
                                 CollimatorAngle=0)

        beamset.CreatePhotonBeam(Energy=6,
                                 IsocenterData=isocenter_parameters,
                                 Name='2_Brai_g090c005',
                                 Description='2 3DC: MLC Static Field',
                                 GantryAngle=90,
                                 CouchAngle=5,
                                 CollimatorAngle=0)
        for beam in beamset.Beams:
            beam.SetTreatOrProtectRoi(RoiName='BTV')
            beam.SetTreatOrProtectRoi(RoiName='Avoid')

        beamset.TreatAndProtect()
#        beamset.TreatAndProtect(ShowProgress)

        total_dose_string = str(int(total_dose))
        case.PatientModel.RegionsOfInterest['PTV_WB_xxxx'].Name = 'PTV_WB' + total_dose_string.zfill(4)


if __name__ == '__main__':
    main()
