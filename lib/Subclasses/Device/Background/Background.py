# This device represents all the devices that are not explicitly described otherwise because one or several of the following reasons:
# - they are rare;
# - they don't consume a lot of energy nor they have an important power demand;
# - patterns of use or of consumption are difficult to model;
# - they are non-controllable, i.e the supervisor has no possibility to interact with them.

from src.common.DeviceMainClasses import NonControllableDevice


class Background(NonControllableDevice):

    def __init__(self, name, contracts, agent, aggregators, profiles, parameters=None, filename="lib/Subclasses/Device/Background/Background.json"):
        super().__init__(name, contracts, agent, aggregators, filename, profiles, parameters)

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _read_data_profiles(self, profiles):
        data_user = self._read_consumer_data(profiles["user"])  # parsing the data
        data_device = self._read_technical_data(profiles["device"])  # parsing the data

        # we randomize a bit in order to represent reality better
        consumption_variation = self._catalog.get("gaussian")(1, data_device["consumption_variation"])  # modification of the consumption
        for nature in data_device["usage_profile"]:
            for i in range(len(data_device["usage_profile"][nature]["weekday"])):
                data_device["usage_profile"][nature]["weekday"][i] *= consumption_variation
            for i in range(len(data_device["usage_profile"][nature]["weekend"])):
                data_device["usage_profile"][nature]["weekend"][i] *= consumption_variation

        self._data_user_creation(data_user)  # creation of an empty user profile

        self._randomize_start_variation(data_user)

        # adaptation of the data to the time step
        # we need to reshape the data in order to make it fitable with the time step chosen for the simulation
        time_step = self._catalog.get("time_step")
        for nature in data_device["usage_profile"]:
            if time_step < 1:
                # weekday
                temp_list = list()
                for value in data_device["usage_profile"][nature]["weekday"]:
                    element = [value * time_step] * int(1 / time_step)
                    temp_list += element
                data_device["usage_profile"][nature]["weekday"] = temp_list

                # weekend
                temp_list = list()
                for value in data_device["usage_profile"][nature]["weekend"]:
                    element = [value * time_step] * int(1 / time_step)
                    temp_list += element
                data_device["usage_profile"][nature]["weekend"] = temp_list

            elif time_step > 1:
                # weekday
                temp_list = list()
                i = 0
                while i <= len(data_device["usage_profile"][nature]["weekday"]) - int(time_step):
                    value = 0
                    for j in range(int(time_step)):
                        value += data_device["usage_profile"][nature]["weekday"][i+j]
                    temp_list.append(value)
                    i += j + 1
                data_device["usage_profile"][nature]["weekday"] = temp_list

                # weekend
                temp_list = list()
                i = 0
                while i <= len(data_device["usage_profile"][nature]["weekend"]) - int(time_step):
                    value = 0
                    for j in range(int(time_step)):
                        value += data_device["usage_profile"][nature]["weekend"][i+j]
                    temp_list.append(value)
                    i += j + 1
                data_device["usage_profile"][nature]["weekend"] = temp_list

        # usage profile
        self._technical_profile = []  # creation of an empty usage_profile with all cases ready

        self._technical_profile = dict()
        for nature in data_device["usage_profile"]:  # data_usage is then added for each nature used by the device
            self._technical_profile[nature] = list()
            self._technical_profile[nature] = 5 * data_device["usage_profile"][nature]["weekday"] + \
                                              2 * data_device["usage_profile"][nature]["weekend"]

        self._unused_nature_removal()  # remove unused natures

    def _randomize_start_variation(self, data):
        start_time_variation = self._catalog.get("gaussian")(0, data["start_time_variation"])  # creation of a displacement in the user_profile
        self._moment = int((self._moment + start_time_variation) // self._catalog.get("time_step") % self._period)

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def update(self):
        message = {element: self._messages["ascendant"][element] for element in self._messages["ascendant"]}
        energy_wanted = {nature.name: message for nature in self.natures}  # consumption which will be asked eventually

        for nature in energy_wanted:
            # print(self._moment)
            # print(len(self._technical_profile[nature]))
            energy_wanted[nature]["energy_minimum"] = self._technical_profile[nature][self._moment]  # energy needed for all natures used by the device
            energy_wanted[nature]["energy_nominal"] = self._technical_profile[nature][self._moment]  # energy needed for all natures used by the device
            energy_wanted[nature]["energy_maximum"] = self._technical_profile[nature][self._moment]  # energy needed for all natures used by the device

        self.publish_wanted_energy(energy_wanted)  # apply the contract to the energy wanted and then publish it in the catalog




