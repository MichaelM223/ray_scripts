""" Create RayStation Water Tank Plans
    
    This script creates a series of water tank reference profiles for each machine/energy
    combination defined below. Each plan is created within the current patient case,
    where the plan name is the machine and energy for photons or machine followed by
    "Electrons" for electrons. Within each photon plan, three courses are created for
    each SSD: Jaw, MLC, and EDW. Within the electorn plan, a beamset is created for each
    energy. Only open electron fields are supported at this time. The beams are created
    with the naming format "[energy]_[SSD]_ [description]" so that they can be parsed
    using the WaterTankAnalysis (https://github.com/mwgeurts/water_tank) tool.

    Note, this script will create each EDW plan but cannot set the wedge angles. Each
    wedge must be manually set during execution of the script. A GUI prompt is displayed
    after each EDW plan is created, after which the script can be resumed. Each EDW must
    only be set once per energy; the wedged fields are copied for each field size and
    SSD.

    Finally, dose is computed and then exported after each beamset is created. The DICOM
    export path is set in the configuration settings below. The calc and export flags can 
    also be set to False to only create the beams but not calculate or export them, 
    respectively.

    This program is free software: you can redistribute it and/or modify it under the
    terms of the GNU General Public License as published by the Free Software Foundation,
    either version 3 of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful, but WITHOUT ANY
    WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
    PARTICULAR PURPOSE. See the GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along with this
    program. If not, see <http://www.gnu.org/licenses/>.
    """

__author__ = 'Mark Geurts'
__contact__ = 'mark.w.geurts@gmail.com'
__date__ = '2017-11-13'
__version__ = '1.0.0'
__status__ = 'Development'
__deprecated__ = False
__reviewer__ = 'N/A'
__reviewed__ = 'YYYY-MM-DD'
__raystation__ = '6.1.1.2'
__maintainer__ = 'Mark Geurts'
__email__ =  'mark.w.geurts@gmail.com'
__license__ = 'GPLv3'
__copyright__ = 'Copyright (C) 2017, University of Wisconsin Board of Regents'

# Specify import statements
from connect import *

# Define calcs and export flags (set to True to calculate dose and export)
calc = True
export = True

# Define list of machines
photon_machines = ['TrueBeam', 'TrueBeam_FFF', 'TrueBeamSTx', 'TrueBeamSTx_FFF']
electron_machines = ['TrueBeam_E']

# Define list of energies for each machine
photons = [6, 10, 15]
electrons = [6, 9, 12, 15]

# Define jaw open field sizes
jaws = [2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25, 30, 35, 40]

# Define SSDs
ssds = [80, 90, 100, 110, 120]

# Define EDWs
edws = ['EDW10IN', 'EDW10OUT', 'EDW15IN', 'EDW15OUT', 'EDW20IN', 'EDW20OUT', 'EDW25IN', \
        'EDW25OUT', 'EDW30IN', 'EDW30OUT', 'EDW45IN', 'EDW45OUT', 'EDW60IN', 'EDW60OUT']

# Define EDW jaw open field sizes
edwjaws = [5, 10, 15, 20]

# Define MLC square field sizes
mlcs = [2, 3, 4, 5, 6, 7, 8, 9, 10]

# Define electron applicators
applicators = [6, 10, 15, 20, 25]

# Define number of MU within each field
mu = 100

# Define the export location
path = '\\\\uwhfs\\shares\\home2\\mwg120\\Water Tank Reference\\RayStation\\'

# Get current patient, case
patient = get_current('Patient')
case = get_current('Case')

# Loop through each machine
for m in photon_machines:

    # Loop through each photon energy
    for e in photons:

        # Create new photon plan
        print 'Creating plan for {} {} MV'.format(m, e)
        plan = case.AddNewPlan(PlanName='{} {} MV'.format(m, e), PlannedBy='', \
            Comment='', ExaminationName=case.Examinations[0].Name, \
            AllowDuplicateNames=False)
        plan.UpdateDoseGrid(Corner={'x': -28, 'y': -0.1, 'z': -28}, \
            VoxelSize={'x': 0.1, 'y': 0.1, 'z': 0.1}, \
            NumberOfVoxels={'x': 560, 'y': 401, 'z': 560})

        # Loop through each SSD
        for s in ssds:

            # Add JAW beamset
            print 'Creating Jaw beamset at {} cm SSD'.format(s)
            beamset = plan.AddNewBeamSet(Name='Jaw {} cm SSD'.format(s), \
                ExaminationName=case.Examinations[0].Name, \
                MachineName=m, Modality='Photons', TreatmentTechnique='Conformal', \
                PatientPosition='HeadFirstSupine', NumberOfFractions=1, \
                CreateSetupBeams=False, UseLocalizationPointAsSetupIsocenter=False, \
                Comment='', RbeModelReference=None, EnableDynamicTrackingForVero=False)

            # Loop through each jaw open field size
            for j in jaws:

                # Add beam for this energy, SSD, and field size
                print 'Creating beam {} MV_{} cm_{} x {}'.format(e, s, j, j)
                beam = beamset.CreatePhotonBeam(Energy=e, IsocenterData={ \
                    'Position': {'x': 0, 'y': 100-s, 'z': 0}, 'NameOfIsocenterToRef': '', \
                    'Name': '{} MV_{} cm_{} x {}'.format(e, s, j, j), 'Color': \
                    '98,184,234'}, Name='{} MV_{} cm_{} x {}'.format(e, s, j, j), \
                    Description='', GantryAngle=0, CouchAngle=0, CollimatorAngle=0)
                beam.SetBolus(BolusName='')
                beam.CreateRectangularField(Width=j, Height=j, CenterCoordinate={'x': \
                    0, 'y': 0}, MoveMLC=False, MoveAllMLCLeaves=False, MoveJaw=True, \
                    JawMargins={'x': 0, 'y': 0}, DeleteWedge=False, \
                    PreventExtraLeafPairFromOpening=False)
                beamset.Beams['{} MV_{} cm_{} x {}'.format(e, s, j, j)].BeamMU=mu

            # Calculate dose on beamset
            if calc:
                print 'Calculating dose'
                beamset.ComputeDose(ComputeBeamDoses=True, DoseAlgorithm='CCDose')
                patient.Save()
            
            # Export beamset to the specified path
            if export:
                print 'Exporting RT plan and beam dose'
                try:
                    case.ScriptableDicomExport(ExportFolderPath=path, \
                        BeamSets=[beamset.BeamSetIdentifier()], \
                        BeamDosesForBeamSets=[beamset.BeamSetIdentifier()], DicomFilter='', \
                        IgnorePreConditionWarnings=True)
                
                except SystemError as error:
                    print str(error)

        # Add EDW reference beamset
        print 'Creating reference EDW beamset'
        refset = plan.AddNewBeamSet(Name='EDW reference', \
            ExaminationName=case.Examinations[0].Name, \
            MachineName=m, Modality='Photons', TreatmentTechnique='Conformal', \
            PatientPosition='HeadFirstSupine', NumberOfFractions=1, \
            CreateSetupBeams=False, UseLocalizationPointAsSetupIsocenter=False, \
            Comment='', RbeModelReference=None, EnableDynamicTrackingForVero=False)

        # Loop through EDWs
        for w in edws:
            print 'Creating reference beam {}'.format(w)
            beam = refset.CreatePhotonBeam(Energy=e, IsocenterData={ \
                'Position': {'x': 0, 'y': 0, 'z': 0}, 'NameOfIsocenterToRef': \
                '', 'Name': w, 'Color': '98,184,234'}, Name=w, Description='', \
                GantryAngle=0, CouchAngle=0, CollimatorAngle=0)
            beam.SetBolus(BolusName='')

        # Display prompt reminding user to set EDW angles
        patient.Save()
        plan.SetCurrent()
        refset.SetCurrent()
        await_user_input('Manually set EDWs for {}. Then continue the script.'.format(m));
        patient.Save()

        # Loop through each SSD
        for s in ssds:

            # Add EDW beamset
            print 'Creating EDW beamset at {} cm SSD'.format(s)
            beamset = plan.AddNewBeamSet(Name='EDW {} cm SSD'.format(s), \
                ExaminationName=case.Examinations[0].Name, \
                MachineName=m, Modality='Photons', TreatmentTechnique='Conformal', \
                PatientPosition='HeadFirstSupine', NumberOfFractions=1, \
                CreateSetupBeams=False, UseLocalizationPointAsSetupIsocenter=False, \
                Comment='', RbeModelReference=None, EnableDynamicTrackingForVero=False)

            # Loop through EDWs
            for w in edws:

                # Loop through each EDW jaw open field size
                for j in edwjaws:

                    # Add beam for this energy, SSD, wedge, and field size
                    print 'Copying beam {} MV_{} cm_{} {} x {}'.format(e, s, w, j, j)
                    beamset.CopyBeamFromBeamSet(BeamToCopy = refset.Beams[w])
                    beam = beamset.Beams[w]

                    # Set name, isocenter position, and field size
                    beam.Name = '{} MV_{} cm_{} {} x {}'.format(e, s, w, j, j)
                    beam.Isocenter.EditIsocenter(Name = '{} MV_{} cm_{} {} x {}'.format(e, s, w, j, j), \
                        Position = {'x': 0, 'y': 100-s, 'z': 0})
                    beam.CreateRectangularField(Width=j, Height=j, \
                        CenterCoordinate={'x': 0, 'y': 0}, MoveMLC=False, \
                        MoveAllMLCLeaves=False, MoveJaw=True, \
                        JawMargins={'x': 0, 'y': 0}, DeleteWedge=False, \
                        PreventExtraLeafPairFromOpening=False)
                    beamset.Beams['{} MV_{} cm_{} {} x {}'.format(e, s, w, j, j)].BeamMU=mu

            # Calculate dose on beamset
            if calc:
                print 'Calculating dose'
                beamset.ComputeDose(ComputeBeamDoses=True, DoseAlgorithm='CCDose')
                patient.Save()
            
            # Export beamset to the specified path
            if export:
                print 'Exporting RT plan and beam dose'
                try:
                    case.ScriptableDicomExport(ExportFolderPath=path, \
                        BeamSets=[beamset.BeamSetIdentifier()], \
                        BeamDosesForBeamSets=[beamset.BeamSetIdentifier()], DicomFilter='', \
                        IgnorePreConditionWarnings=True)

                except SystemError as error:
                    print str(error)

        # Delete reference EDW beam set
        refset.DeleteBeamSet()

        # Loop through each SSD
        for s in ssds:

            # Add MLC beamset
            print 'Creating MLC beamset at {} cm SSD'.format(s)
            beamset = plan.AddNewBeamSet(Name='MLC {} cm SSD'.format(s),
                ExaminationName=case.Examinations[0].Name, \
                MachineName=m, Modality='Photons', TreatmentTechnique='Conformal', \
                PatientPosition='HeadFirstSupine', NumberOfFractions=1, \
                CreateSetupBeams=False, UseLocalizationPointAsSetupIsocenter=False, \
                Comment='', RbeModelReference=None, EnableDynamicTrackingForVero=False)

            # Loop through each MLC square field size
            for l in mlcs:

                # Add beam for this energy, SSD, and field size
                print 'Creating beam {} MV_{} cm_MLC {} x {}'.format(e, s, l, l)
                beam = beamset.CreatePhotonBeam(Energy=e, IsocenterData={ \
                    'Position': {'x': 0, 'y': 100-s, 'z': 0}, 'NameOfIsocenterToRef': '', \
                    'Name': '{} MV_{} cm_MLC {} x {}'.format(e, s, l, l), 'Color': \
                    '98,184,234'}, Name='{} MV_{} cm_MLC {} x {}'.format(e, s, l, l), \
                    Description='', GantryAngle=0, CouchAngle=0, CollimatorAngle=0)
                beam.SetBolus(BolusName='')
                beam.CreateRectangularField(Width=l, Height=l, CenterCoordinate={'x': \
                    0, 'y': 0}, MoveMLC=True, MoveAllMLCLeaves=False, MoveJaw=False, \
                    JawMargins={'x': 0, 'y': 0}, DeleteWedge=False, \
                    PreventExtraLeafPairFromOpening=False)
                beamset.Beams['{} MV_{} cm_MLC {} x {}'.format(e, s, l, l)].BeamMU=mu

            # Add MPPG 5.a field shapes
            print 'Creating MPPG 5.a fields';

            # Create 5.4 Small MLC
            beam = beamset.CreatePhotonBeam(Energy=e, IsocenterData={ \
                'Position': {'x': 0, 'y': 100-s, 'z': 0}, 'NameOfIsocenterToRef': '', \
                'Name': '{} MV_{} cm_MPPG 5.4 Small MLC'.format(e, s), 'Color': \
                '98,184,234'}, Name='{} MV_{} cm_MPPG 5.4 Small MLC'.format(e, s), \
                Description='', GantryAngle=0, CouchAngle=0, CollimatorAngle=0)
            beam.SetBolus(BolusName='')
            beam.CreateRectangularField(Width=4.8, Height=7, CenterCoordinate={'x': \
                -0.2, 'y': 0.5}, MoveMLC=True, MoveAllMLCLeaves=False, MoveJaw=True, \
                JawMargins={'x': 0, 'y': 0}, DeleteWedge=False, \
                PreventExtraLeafPairFromOpening=False)
            beamset.Beams['{} MV_{} cm_MPPG 5.4 Small MLC'.format(e, s)].BeamMU=mu

            # Set leaf positions for 5.4 Small MLC
            leaves = beam.Segments[0].LeafPositions;
            
            if 'STx' in m:
                a = [-2.10, -2.1, -2.2, -2.2, -2.6, -2.6, -2.6, -2.6, -2.6, \
                     -2.6, -2.6, -2.6, -2.6, -2.6, -2.6, -2.6, -2.6, -2.6, \
                     -2.6, -2.6, -2.6, -2.6, -2.2, -2.2, -1.8, -1.8, -1.4, -1.4]
                b = [-1.1, -1.1, 0, 0, 0.4, 0.4, 0.9, 0.9, 1.4, 1.4, 1.7, 1.7, \
                     1.8, 1.8, 2.2, 2.2, 2.2, 2.2, 2.2, 2.2, 2.0, 2.0, 1.9, 1.9, \
                     1.7, 1.7, 1.5, 1.5]

                for i in range(len(a)):
                    leaves[0][18+i] = a[i]
                    leaves[1][18+i] = b[i]
                
            else:
                a = [-1.69, -2.05, -2.25, -2.6, -2.6, -2.6, -2.6, -2.6, \
                     -2.6, -2.6, -2.6, -2.2, -1.8, -1.4]
                b = [0.15, 0.54, 1.2, 1.52, 1.82, 1.93, 2.05, 2.2, 2.2, 2.2, \
                     2, 1.9, 1.7, 1.16]
                     
                for i in range(len(a)):
                    leaves[0][24+i] = a[i]
                    leaves[1][24+i] = b[i]
            
            beam.Segments[0].LeafPositions = leaves

            # Create 5.5 Small MLC
            beam = beamset.CreatePhotonBeam(Energy=e, IsocenterData={ \
                'Position': {'x': 0, 'y': 100-s, 'z': 0}, 'NameOfIsocenterToRef': '', \
                'Name': '{} MV_{} cm_MPPG 5.5 Large MLC'.format(e, s), 'Color': \
                '98,184,234'}, Name='{} MV_{} cm_MPPG 5.4 Large MLC'.format(e, s), \
                Description='', GantryAngle=0, CouchAngle=0, CollimatorAngle=0)
            beam.SetBolus(BolusName='')
            beam.CreateRectangularField(Width=14.8, Height=20, CenterCoordinate={'x': \
                0, 'y': 0}, MoveMLC=True, MoveAllMLCLeaves=False, MoveJaw=True, \
                JawMargins={'x': 0, 'y': 0}, DeleteWedge=False, \
                PreventExtraLeafPairFromOpening=False)
            beamset.Beams['{} MV_{} cm_MPPG 5.4 Large MLC'.format(e, s)].BeamMU=mu

            # Set leaf positions for 5.5 Large MLC
            leaves = beam.Segments[0].LeafPositions;
            if 'STx' in m:
                b = [-0.5, 0.3, 1, 1.8, 2.7, 5.4, 5.8, 6.6, 7.4, 7.4, 7.4, 7.1, 6, 6, \
                     4.8, 4.8, 3.2, 3.2, 0.8, 0.8, -0.5, -0.5, -1.3, -1.3, -2, -2, -2.7, \
                     -2.7, -2.9, -2.9, -2.4, -2.4, -2.1, -2.1, -1.6, -1.6, -0.8, -0.8, \
                     0.1, 0.1, 1, 1, 2, 2, 3.1, 4.3, 4.5, 4.8, 5.8, 6.6, 7.4, 7.4, 6.4, \
                     5.7, 4.3, 3.6]
                for i in range(len(b)):
                    leaves[1][2+i] = b[i]

            else:
                b = [-0.5, 0.3, 1, 1.8, 2.7, 5.4, 5.8, 6.6, 7.4, 7.4, 7.4, 7.1, 6, 4.8, 3.2, \
                     0.8, -0.5, -1.3, -2, -2.7, -2.9, -2.4, -2.1, -1.6, -0.8, 0.1, 1, 2, 3.1, \
                     4.3, 4.5, 4.8, 5.8, 6.6, 7.4, 7.4, 6.4, 5.7, 4.3, 3.6]
                for i in range(len(b)):
                    leaves[1][10+i] = b[i]

            beam.Segments[0].LeafPositions = leaves

            # Create 5.6 Off Axis
            beam = beamset.CreatePhotonBeam(Energy=e, IsocenterData={ \
                'Position': {'x': 0, 'y': 100-s, 'z': 0}, 'NameOfIsocenterToRef': '', \
                'Name': '{} MV_{} cm_MPPG 5.6 Off Axis'.format(e, s), 'Color': \
                '98,184,234'}, Name='{} MV_{} cm_MPPG 5.6 Off Axis'.format(e, s), \
                Description='', GantryAngle=0, CouchAngle=0, CollimatorAngle=0)
            beam.SetBolus(BolusName='')
            beam.CreateRectangularField(Width=10, Height=15, CenterCoordinate={'x': \
                -5, 'y': 0}, MoveMLC=True, MoveAllMLCLeaves=False, MoveJaw=True, \
                JawMargins={'x': 0, 'y': 0}, DeleteWedge=False, \
                PreventExtraLeafPairFromOpening=False)
            beamset.Beams['{} MV_{} cm_MPPG 5.6 Off Axis'.format(e, s)].BeamMU=mu

            # Set leaf positions for 5.6 Off Axis
            leaves = beam.Segments[0].LeafPositions;
            if 'STx' in m:
                for i in range(7,52):
                    leaves[1][i] = -4.5

            else:
                for i in range(15,44):
                    leaves[1][i] = -4.5
            
            beam.Segments[0].LeafPositions = leaves

            # Create 5.7 Asymmetric
            beam = beamset.CreatePhotonBeam(Energy=e, IsocenterData={ \
                'Position': {'x': 0, 'y': 100-s, 'z': 0}, 'NameOfIsocenterToRef': '', \
                'Name': '{} MV_{} cm_MPPG 5.7 Asymmetric'.format(e, s), 'Color': \
                '98,184,234'}, Name='{} MV_{} cm_MPPG 5.7 Asymmetric'.format(e, s), \
                Description='', GantryAngle=0, CouchAngle=0, CollimatorAngle=0)
            beam.SetBolus(BolusName='')
            beam.CreateRectangularField(Width=12, Height=11.5, CenterCoordinate={'x': \
                -2, 'y': 1.75}, MoveMLC=False, MoveAllMLCLeaves=False, MoveJaw=True, \
                JawMargins={'x': 0, 'y': 0}, DeleteWedge=False, \
                PreventExtraLeafPairFromOpening=False)
            beamset.Beams['{} MV_{} cm_MPPG 5.7 Asymmetric'.format(e, s)].BeamMU=mu

            # Create 5.8 Oblique
            beam = beamset.CreatePhotonBeam(Energy=e, IsocenterData={ \
                'Position': {'x': 0, 'y': 100-s, 'z': 0}, 'NameOfIsocenterToRef': '', \
                'Name': '{} MV_{} cm_MPPG 5.8 Oblique'.format(e, s), 'Color': \
                '98,184,234'}, Name='{} MV_{} cm_MPPG 5.8 Oblique'.format(e, s), \
                Description='', GantryAngle=20, CouchAngle=0, CollimatorAngle=0)
            beam.SetBolus(BolusName='')
            beam.CreateRectangularField(Width=20, Height=10, CenterCoordinate={'x': \
                0, 'y': 0}, MoveMLC=True, MoveAllMLCLeaves=False, MoveJaw=True, \
                JawMargins={'x': 0, 'y': 0}, DeleteWedge=False, \
                PreventExtraLeafPairFromOpening=False)
            beamset.Beams['{} MV_{} cm_MPPG 5.8 Oblique'.format(e, s)].BeamMU=mu

            # Calculate dose on beamset
            if calc:
                print 'Calculating Dose'
                beamset.ComputeDose(ComputeBeamDoses=True, DoseAlgorithm='CCDose')
                patient.Save()
            
            # Export beamset to the specified path
            if export:
                print 'Exporting RT plan and beam dose'
                try:
                    case.ScriptableDicomExport(ExportFolderPath=path, \
                        BeamSets=[beamset.BeamSetIdentifier()], \
                        BeamDosesForBeamSets=[beamset.BeamSetIdentifier()], DicomFilter='', \
                        IgnorePreConditionWarnings=True)
                
                except SystemError as error:
                    print str(error)

# Loop through each machine
for m in electron_machines:

    # Add electron plan
    print 'Creating plan for {} Electrons'.format(m)

    # Create new electron plan
    plan = case.AddNewPlan(PlanName='{} Electrons'.format(m), PlannedBy='', \
        Comment='', ExaminationName=case.Examinations[0].Name, \
        AllowDuplicateNames=False)
    plan.UpdateDoseGrid(Corner={'x': -20, 'y': -0.1, 'z': -20}, \
        VoxelSize={'x': 0.2, 'y': 0.1, 'z': 0.2}, NumberOfVoxels={'x': 200, \
        'y': 201, 'z': 200})

    # Loop through each electron energy
    for e in electrons:

        # Add electron energy beamset
        print 'Creating {} MeV beamset'.format(e)
        beamset = plan.AddNewBeamSet(Name='{} MeV'.format(e), \
            ExaminationName=case.Examinations[0].Name, \
            MachineName='{}'.format(m), Modality='Electrons', \
            TreatmentTechnique='ApplicatorAndCutout', PatientPosition='HeadFirstSupine', \
            NumberOfFractions=1, CreateSetupBeams=False, \
            UseLocalizationPointAsSetupIsocenter=False, Comment='', \
            RbeModelReference=None, EnableDynamicTrackingForVero=False)

        # Loop through each SSD
        for s in ssds:

            # Only include SSDs >= 98 cm
            if s >= 98:

                # Loop through each applicator
                for a in applicators:

                    # Add beam for this energy, SSD, and applicator
                    print 'Creating beam {} MeV_{} cm_{} x {}'.format(e, s, a, a)
                    beam = beamset.CreateElectronBeam(ApplicatorName='Varian {}x{}'.format(a, a), \
                        Energy=e, InsertName='', IsAddCutoutChecked=False, \
                        IsocenterData={'Position': {'x': 0, 'y': 100-s, 'z': 0}, \
                        'NameOfIsocenterToRef': '', 'Name': \
                        '{} MeV_{} cm_{} x {}'.format(e, s, a, a), \
                        'Color': '98,184,234'}, Name='{} MeV_{} cm_{} x {}'.\
                        format(e, s, a, a), Description='', GantryAngle=0, \
                        CouchAngle=0, CollimatorAngle=0)
                    beam.SetBolus(BolusName='')
                    beamset.Beams['{} MeV_{} cm_{} x {}'.format(e, s, a, a)].BeamMU=mu

        # Prompt user to set Monte Carlo histories
        plan.SetCurrent()
        beamset.SetCurrent()
        await_user_input('Update the number of Monte Carlo histories (5e6 recommended)');

        # Calculate dose on beamset
        if calc:
            print 'Calculating Dose'
            beamset.ComputeDose(ComputeBeamDoses=True, DoseAlgorithm='ElectronMonteCarlo')
            patient.Save()
            
        # Export beamset to the specified path
        if export:
            print 'Exporting RT plan and beam dose'
            try:
                case.ScriptableDicomExport(ExportFolderPath=path, \
                    BeamSets=[beamset.BeamSetIdentifier()], \
                    BeamDosesForBeamSets=[beamset.BeamSetIdentifier()], DicomFilter='', \
                    IgnorePreConditionWarnings=True)
            
            except SystemError as error:
                print str(error)
                             
# Save patient
patient.Save()

print 'Done!'
