from src.common.DeviceMainClasses import NonControllableDevice


class DummyCO2Device(NonControllableDevice):

    def __init__(self, name, contracts, agent, aggregators, profiles, parameters=None, filename="lib/Subclasses/Device/DummyCO2Device/DummyCO2Device.json"):
        super().__init__(name, contracts, agent, aggregators, filename, profiles, parameters)

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _read_data_profiles(self, profiles):
        data_user = self._read_consumer_data(profiles["user"])  # parsing the data
        data_device = self._read_technical_data(profiles["device"])  # parsing the data

        self._data_user_creation(data_user)  # creation of an empty user profile

        # we randomize a bit in order to represent reality better
        self._randomize_start_variation(data_user)
        self._randomize_consumption(data_device)
        self._randomize_duration(data_user)

        # adaptation of the data to the time step
        # we need to reshape the data in order to make it fitable with the time step chosen for the simulation
        time_step = self._catalog.get("time_step")

        # user profile
        for line in data_user["profile"]:
            current_moment = int(line[0] // time_step)  # the moment when the device will be turned on

            # creation of the user profile, where there are hours associated with the use of the device
            # first time step

            ratio = (self._moment % time_step - line[0] % time_step) / time_step  # the percentage of use at the beginning (e.g for a device starting at 7h45 with an hourly time step, it will be 0.25)
            if ratio <= 0:  # in case beginning - start is negative
                ratio += 1
            self._user_profile.append([current_moment, ratio])  # adding the first time step when it will be turned on

            # intermediate time steps
            duration_residue = line[1] - (ratio * time_step)  # the residue of the duration is the remnant time during which the device is operating
            while duration_residue >= 1:  # as long as there is at least 1 full time step of functioning...
                current_moment += 1
                duration_residue -= 1
                self._user_profile.append([current_moment, 1])  # ...a new entry is created with a ratio of 1 (full use)

            # final time step
            current_moment += 1
            ratio = duration_residue/time_step  # the percentage of use at the end (e.g for a device ending at 7h45 with an hourly time step, it will be 0.75)
            self._user_profile.append([current_moment, ratio])  # adding the final time step before it wil be turned off

        # usage profile
        self._technical_profile = []  # creation of an empty usage_profile with all cases ready

        self._technical_profile = dict()
        for nature in data_device["usage_profile"]:  # data_usage is then added for each nature used by the device
            self._technical_profile[nature] = data_device["usage_profile"][nature]

        self._CO2_production = data_device["CO2_production"]

        self._unused_nature_removal()  # remove unused natures

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def update(self):  # method updating needs of the devices before the supervision
        energy_wanted = self._create_message()  # demand or proposal of energy which will be asked eventually

        for line in self._user_profile:
            if line[0] == self._moment:  # if a consumption has been scheduled and if it has not been fulfilled yet
                for nature in energy_wanted:
                    energy_wanted[nature]["energy_minimum"] = self._technical_profile[nature] * line[1]  # energy needed for all natures used by the device
                    energy_wanted[nature]["energy_nominal"] = self._technical_profile[nature] * line[1]  # energy needed for all natures used by the device
                    energy_wanted[nature]["energy_maximum"] = self._technical_profile[nature] * line[1]  # energy needed for all natures used by the device
                    energy_wanted[nature]["CO2"] = self._CO2_production

        self.publish_wanted_energy(energy_wanted)  # apply the contract to the energy wanted and then publish it in the catalog

    def react(self):
        super().react()





