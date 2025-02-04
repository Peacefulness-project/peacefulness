from json import load
from src.common.World import World
from src.common.Agent import Agent


def agent_generation(name, quantity, filename, aggregators, price_manager_daemon, data_daemons={}, verbose=True):  # this method creates several agents, each with a predefinite set of devices
    world = World.ref_world

    if verbose:
        print(f"generation of the {quantity} agents from the {filename} template.")

    # loading the data in the file
    with open(filename, "r") as file:
        data = load(file)

    # creation of contracts
    contract_dict = {}
    for contract_type in data["contracts"]:  # for each contract
        contract_name = f"{name}_{data['template name']}_{contract_type}"
        nature = world._catalog.natures[data["contracts"][contract_type]["nature_name"]]
        identifier = price_manager_daemon[nature.name]
        contract_class = world._subclasses_dictionary["Contract"][data["contracts"][contract_type]["contract_subclass"]]

        if len(data["contracts"][contract_type]) == 2:  # if there are no parameters
            contract = contract_class(contract_name, nature, identifier)
        else:  # if there are parameters
            parameters = data["contracts"][contract_type]["parameters"]
            contract = contract_class(contract_name, nature, identifier, parameters)

        contract_dict[contract_type] = contract

    # process of data daemon dictionary
    data_daemons = {key: data_daemons[key].name for key in data_daemons}  # transform the daemons objects into strings

    for i in range(quantity):

        # creation of an agent
        agent_name = f"{name}_{data['template name']}_{str(i)}"
        agent = Agent(agent_name)  # creation of the agent, which name is "Profile X"_"number"

        # creation of devices
        for device_data in data["composition"]:
            for profile in data["composition"][device_data]:
                if profile["quantity"][0] > profile["quantity"][1]:
                    raise Exception(f"The minimum number of devices {profile['name']} allowed must be inferior to the maximum number allowed in the profile {data['template name']}.")
                number_of_devices = world._catalog.get("int")(profile["quantity"][0], profile["quantity"][1])  # the number of devices is chosen randomly inside the limits defined in the agent profile
                for j in range(number_of_devices):
                    device_name = f"{agent_name}_{profile['name']}_{j}"  # name of the device, "Profile X"_5_Light_0
                    device_class = world._subclasses_dictionary["Device"][device_data]

                    # management of contracts
                    contracts = []
                    for contract_type in contract_dict:
                        if profile["contract"] == contract_type:
                            contracts.append(contract_dict[contract_type])

                    # management of devices needing data
                    if "parameters" in profile:
                        parameters = profile["parameters"]
                        parameters.update(data_daemons)
                    else:
                        parameters = data_daemons

                    if "profile_filename" in profile:  # management of non default files for devices profiles
                        device_class(device_name, contracts, agent, aggregators, profile["data_profiles"], parameters, profile["profile_filename"])  # creation of the device
                    else:
                        device_class(device_name, contracts, agent, aggregators, profile["data_profiles"], parameters)  # creation of the device

    if verbose:
        print("Done\n")
