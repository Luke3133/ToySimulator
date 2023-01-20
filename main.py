import numpy as np
import os, sys
import time

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    print(tools)
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

import traci
import traci.constants

sumoBinary = "C:\Program Files (x86)\Eclipse" + os.sep + "Sumo" + os.sep + "bin" + os.sep + "sumo-gui.exe"
print("Starting SUMO")
#sumoCmd = [sumoBinary, "-c", "./london/osm.sumocfg", "--start"]
#sumoCmd = [sumoBinary, "-c", "./smalllondon/osm.sumocfg", "--start"]
#sumoCmd = [sumoBinary, "-c", "./simplenet/simple.sumocfg", "--start"]
sumoCmd = [sumoBinary, "-c", "./GMLReader/HindleyNetwork.sumocfg", "--start"]
traci.start(sumoCmd)

traci.gui.setSchema("View #0", "emissions")
print(traci.gui.getSchema())
if traci.isLoaded():
    print("SUMO successfully loaded")

class AirPollutionSensor:
    location_x = 0
    location_y = 0
    sensitivity = 0
    Readings = []


    def __init__(self, location_x, location_y, sensitivity = 1, readings = []):
        self.location_x = location_x
        self.location_y = location_y
        self.sensitivity = sensitivity
        self.Readings = readings

class AIRecommender:

    state = []
    output_parameters = []
    actions = []
    CurrentLanes = []
    CurrentEmissions = {}

    def __init__(self, omega, s):
        # Set up the known parameters
        self.omega = omega
        self.state.append(s)
        print(self.state)
        # Simulate the current state and update the parameters
        self.output_parameters.append(self.simulate_state(self.state[-1]))

        # Begin the design episode
        self.begin()

    def begin(self):
        finished = False
        while not finished:
            # Await an action by the user
            next_action = input("Select next action")

            if str(next_action) == "end":
                finished = True
            elif str(next_action) == "history":
                self.print_history()
            elif str(next_action) == "run":
                self.runstate()
            else:
                self.new_turn(int(next_action), self.state[-1])
        return(10)

    def simulate_state(self,s):
        # Simulate in the digital twin or surrogate model
        outputParameters = 10 * s  # random function needs changing
        return outputParameters

    def calculate_new_state(self, a, currentState):
        # Calculate new state from old state
        NewState = currentState + a  # random function needs changing
        return NewState

    def new_turn(self,a, s):

        self.actions.append(a)
        self.state.append(self.calculate_new_state(a, s))
        self.output_parameters.append(self.simulate_state(self.state[-1]))
        print(self.output_parameters[-1])
        return()

    def print_history(self):
        print(self.state)
        print(self.actions)
        print(self.output_parameters)

    def GetCurrentLanes(self):
        lanes = traci.lane.getIDList()
        for lane in lanes:
            if ":" not in str(lane):
                self.CurrentLanes.append(lane)

    def runstate(self):
        self.GetCurrentLanes()
        j = 0
        while (j < 150):
            #runs one simulation step
            time.sleep(0.25)
            traci.simulationStep()
            # Update lanes to show pollution levels
            reallanes = []

            if self.CurrentEmissions == {}:
                for lane in self.CurrentLanes:
                    self.CurrentEmissions[lane] = traci.lane.getCO2Emission(lane)
                    traci.lane.setParameter(lane, "Emis", self.CurrentEmissions[lane])
            else:
                for lane in self.CurrentLanes:
                    self.CurrentEmissions[lane] += traci.lane.getCO2Emission(lane)
                    traci.lane.setParameter(lane, "Emis", self.CurrentEmissions[lane]/j)

            #     # for every 5th step, calculate the emissions for each lane
            #     emissions = traci.lane.getCO2Emission(lanes)
            #     print(emissions)

            # vehicles = traci.vehicle.getIDList()
            # if (j%10)==0:
            #     print(len(vehicles))
            #     if len(vehicles) > 1:
            #         print(traci.vehicle.getCO2Emission(vehicles[2]))
            j += 1

        traci.close()


sensor1 = AirPollutionSensor(3500,4500)
designer = AIRecommender(10, [])


# State s refers to changes made. These are stored in an array [] which can be appended to each time a change is made.
