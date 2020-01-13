""" PMH All NZL Sub 0-5ms

Subtracts leaf time based on a uniformly distributed probability between -5 and 0 ms

Leaves less than 60 ms after sampled perturbation are set to minimum LOT of 60 ms

"""

import connect
import random
import logging

logging.info('executing sinogram perterbation')
logging.info('reducing non-zero leaves by uniformly sampled distribution from -5 to 0 ms')

# get current patient, beam set, and beam
patient = connect.get_current('Patient')
beam_set = connect.get_current('BeamSet')
beam = beam_set.Beams[0]

# calculate 5 ms as a function of the projection time
projtime = beam.BeamMU  # BeamMU is equal to projection time in the RayStation structure
offsetfrac = 5/(projtime*1000)  # 5 ms is testing variable
minfrac = 60/(projtime*1000)  # 60 ms is minimum LOT as defined by machine

# count segments as object technically 'unsized'
nseg = 0

# loop through segments
for seg in beam.Segments:

    logging.info('updating segment {:n}'.format(nseg))

    # get current leaf open time array
    lots = seg.LeafOpenFraction

    # loop though array elements
    for ii in range(0,len(lots)):

        # only change non-zero and non-full LOT leaves
        if lots[ii] != 0 and lots[ii] < 1:

            # get old LOT
            oldlot = lots[ii]

            # calculate new LOT value with random offset from -5 to 0 ms
            newlot = oldlot + random.uniform(-offsetfrac,0)

            # add to LOT array, minimium at 60 ms and capping at 1.0
            if newlot >= minfrac:

                lots[ii] = newlot

            else:

                lots[ii] = minfrac

    # set new LOT array
    seg.LeafOpenFraction = lots

    # increment number of segments
    nseg = nseg + 1

# reset last segment to all zeros, this is required by RayStation to calculate
logging.info('setting final segment to zero LOTs per RayStation requirements')
for ii in range(0,len(lots)):

    beam.Segments[nseg-1].LeafOpenFraction[ii] = 0


logging.info('sinogram perterbation complete')
