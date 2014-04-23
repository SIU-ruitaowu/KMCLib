""" Module for testing an ising spin model. """

# Copyright (c)  2014  Mikael Leetmaa
#
# This file is part of the KMCLib project distributed under the terms of the
# GNU General Public License version 3, see <http://www.gnu.org/licenses/>.
#

import unittest
import numpy
import time


# Import the interface.
from KMCLib import *

def trueFunction(obj):
    return True

def falseFunction(obj):
    return False

class CustomRateCalculator(KMCRateCalculatorPlugin):
    """ Class for defining the custom rates function for the KMCLib paper. """

    def rate(self, geometry, elements_before, elements_after, rate_constant, process_number, coordinate):
        """ Overloaded base class API function """
        diff = 1.0

        # Get the number of U and D neighbours.
        u_neighbours = len([ e for e in [elements_before[1], elements_before[2], elements_before[3], elements_before[4]] if e == "U"])
        d_neighbours = len([ e for e in [elements_before[1], elements_before[2], elements_before[3], elements_before[4]] if e == "D"])

        # Flipping U->D
        if process_number == 0:
            # D neighbours count as negative, U neighbours as positive.
            diff = u_neighbours - d_neighbours

        # Flipping D->U
        if process_number == 1:
            # U neighbours count as negative, D neighbours as positive.
            diff = d_neighbours - u_neighbours

        J   = 1.0
        kbT = 1.0

        return min(1.0, numpy.exp(-diff*J/kbT))

    def cutoff(self):
        """ Determines the cutoff for this custom model """
        return 1.0


# Implement the test.
class IsingSpinTest(unittest.TestCase):
    """ Class for testing the an Ising spin model. """

    def testWithAndWithoutCustomRates(self):
        """ Test the Ising model with custom rates. """
        # --------------------------------------------------------------------
        # Setup a calculation with custom rates and no caching.

        # FIXME: Find out a less hacky way to do this.
        CustomRateCalculator.cacheRates = falseFunction
        t1 = time.clock()

        # Load the configuration and interactions.
        configuration = KMCConfigurationFromScript("config.py")
        interactions  = KMCInteractionsFromScript("custom_processes.py")

        # Set the rate calculator.
        interactions.setRateCalculator(rate_calculator=CustomRateCalculator)

        # Create the model.
        model = KMCLatticeModel(configuration, interactions)

        # Define the parameters.
        control_parameters = KMCControlParameters(number_of_steps=1000000,
                                                  dump_interval=10000,
                                                  seed=13997)

        # Run the simulation - save trajectory to 'custom_traj.py'
        model.run(control_parameters, trajectory_filename="custom_traj.py")

        t2 = time.clock()

        # --------------------------------------------------------------------
        # Setup a calculation with custom rates and caching.

        # FIXME: Find out a less hacky way to do this.
        CustomRateCalculator.cacheRates = trueFunction

        # Load the configuration and interactions.
        configuration = KMCConfigurationFromScript("config.py")
        interactions  = KMCInteractionsFromScript("custom_processes.py")

        # Set the rate calculator.
        interactions.setRateCalculator(rate_calculator=CustomRateCalculator)

        # Create the model.
        model = KMCLatticeModel(configuration, interactions)

        # Define the parameters.
        control_parameters = KMCControlParameters(number_of_steps=1000000,
                                                  dump_interval=10000,
                                                  seed=13997)

        # Run the simulation - save trajectory to 'custom_traj_cache.py'
        model.run(control_parameters, trajectory_filename="custom_traj_cache.py")

        t3 = time.clock()

        # --------------------------------------------------------------------
        # Setup the same calculation with fixed rates.

        configuration = KMCConfigurationFromScript("config.py")
        interactions  = KMCInteractionsFromScript("fixed_processes.py")

        # Create the model.
        model = KMCLatticeModel(configuration, interactions)

        # Define the parameters.
        control_parameters = KMCControlParameters(number_of_steps=1000000,
                                                  dump_interval=10000,
                                                  seed=13997)

        # Run the simulation - save trajectory to 'fixed_traj.py'
        model.run(control_parameters, trajectory_filename="fixed_traj.py")

        t4 = time.clock()
        # --------------------------------------------------------------------
        # Check that the results are the same.
        global_dict = {}
        local_dict  = {}
        execfile("custom_traj.py", global_dict, local_dict)
        elem_custom = local_dict["types"][-1]

        global_dict = {}
        local_dict  = {}
        execfile("custom_traj_cache.py", global_dict, local_dict)
        elem_cache  = local_dict["types"][-1]

        global_dict = {}
        local_dict  = {}
        execfile("fixed_traj.py", global_dict, local_dict)
        elem_fixed  = local_dict["types"][-1]

        d0 = len([e for e in elem_custom if e == "D"] )
        u0 = len([e for e in elem_custom if e == "U"] )

        d1 = len([e for e in elem_cache if e == "D"] )
        u1 = len([e for e in elem_cache if e == "U"] )

        d2 = len([e for e in elem_fixed if e == "D"] )
        u2 = len([e for e in elem_fixed if e == "U"] )

        # Excact values will depend on the seed. Check against hardcoded
        # values.
        print "Time for custom run (s):", t2-t1
        print "Time for cache run  (s):", t3-t2
        print "Time for fixed run  (s):", t4-t3

        self.assertEqual(d0, 4062)
        self.assertEqual(d1, 4062)
        self.assertEqual(d2, 4320)

        self.assertEqual(u0, 5938)
        self.assertEqual(u1, 5938)
        self.assertEqual(u2, 5680)


        # --------------------------------------------------------------------
        # Now, plot the last configuration from each trajectory and compare
        # with the images 'fixed_rates.png', 'custom_rates.png'


if __name__ == '__main__':
    unittest.main()


