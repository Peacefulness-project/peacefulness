# This subclass of Converter represents "lateral" energy exchanges between aggregators of the same energy carriers.
# Meanwhile, for the moment, it is considered possible to put it on/off instantly.
from src.common.DeviceMainClasses import Converter, into_list
from src.common.World import World
from src.common.Messages import MessagesManager

class DummyConverter(Converter):

    def __init__(self, name, contracts, agent, upstream_aggregator, downstream_aggregator, profiles, parameters=None, filename="lib/Subclasses/Device/DummyConverter/DummyConverter.json"):
        upstream_aggregators_list = into_list(upstream_aggregator)
        downstream_aggregators_list = into_list(downstream_aggregator)

        self._name = name  # the name which serve as root in the catalog entries

        self._filename = filename  # the name of the data file

        self._moment = None  # the current moment in the period
        self._period = None  # the duration of a classic cycle of use for the user of the device
        self._offset = None  # the delay between the beginning of the period and the beginning of the year

        self._user_profile = list()  # user profile of utilisation, describing user's priority
        # the content differs depending on the kind of device

        self._technical_profile = list()  # energy profile for one usage of the device
        # the content differs depending on the kind of device

        # here are data dicts dedicated to different levels of energy needed/proposed each turn
        # 1 key <=> 1 energy nature
        self._natures = dict()  # contains, for each energy nature used by the device, the aggregator and the nature associated

        aggregators = into_list(upstream_aggregators_list + downstream_aggregators_list)  # make it iterable
        for aggregator in aggregators:
            if aggregator.nature in self.natures:
                self._natures[aggregator.nature].append({"aggregator": None, "contract": None})
                self._natures[aggregator.nature][-1]["aggregator"] = aggregator
            else:
                self._natures[aggregator.nature] = [{"aggregator": None, "contract": None}]
                self._natures[aggregator.nature][-1]["aggregator"] = aggregator

        contracts = into_list(contracts)  # make it iterable

        for tup in range(len(self._natures[contracts[0].nature])):
            try:  # "try" allows to test if self._natures[nature of the contract] was created in the aggregator definition step
                self._natures[contracts[0].nature][tup]["contract"] = contracts[tup]  # add the contract
                contracts[tup].initialization(self.name)
            except:
                raise Exception(f"an aggregator is missing for nature {contracts[0].nature}")

        self._agent = agent  # the agent represents the owner of the device

        # parameters is an optional dictionary which stores additional information needed by user-defined classes
        # putting these information there allow them to be saved/loaded via world method
        if parameters:
            self._parameters = parameters
        else:  # if there are no parameters
            self._parameters = {}  # they are put in an empty dictionary

        world = World.ref_world  # get automatically the world defined for this case
        self._catalog = world.catalog  # linking the catalog to the device

        world.register_device(self)  # register this device into world dedicated dictionary

        for nature in self.natures:
            if nature not in self.agent.natures:  # complete the list of natures of the agent
                self.agent._contracts[nature] = None

            # messages exchanged
            self._catalog.add(f"{self.name}.{nature.name}.energy_wanted", [self.__class__.information_message() for _ in range(len(aggregators))])  # the energy asked or proposed by the device and the price associated
            self._catalog.add(f"{self.name}.{nature.name}.energy_accorded", [self.__class__.decision_message() for _ in range(len(aggregators))])  # the energy delivered or accepted by the strategy

            # results
            self._catalog.add(f"{self.name}.{nature.name}.energy_erased", [0 for _ in range(len(aggregators))])
            self._catalog.add(f"{self.name}.{nature.name}.energy_bought", [0 for _ in range(len(aggregators))])
            self._catalog.add(f"{self.name}.{nature.name}.energy_sold", [0 for _ in range(len(aggregators))])
            self._catalog.add(f"{self.name}.{nature.name}.money_earned", [0 for _ in range(len(aggregators))])
            self._catalog.add(f"{self.name}.{nature.name}.money_spent", [0 for _ in range(len(aggregators))])

            try:  # creates an entry for effort in agent if there is not
                self._catalog.add(f"{self.agent.name}.{nature.name}.effort", {"current_round_effort": [0 for _ in range(len(aggregators))], "cumulated_effort": [0 for _ in range(len(aggregators))]})  # effort accounts for the energy not delivered accordingly to the needs expressed by the agent
            except:
                pass
            try:  # creates an entry useful for results
                self._catalog.add(f"{self.agent.name}.{nature.name}.energy_erased", [0 for _ in range(len(aggregators))])
                self._catalog.add(f"{self.agent.name}.{nature.name}.energy_bought", [0 for _ in range(len(aggregators))])
                self._catalog.add(f"{self.agent.name}.{nature.name}.energy_sold", [0 for _ in range(len(aggregators))])
            except:
                pass

        if self._filename != "loaded device":  # if a filename has been defined...
            self._read_data_profiles(profiles)  # ... then the file is converted into consumption profiles
            # else, the device has been loaded and does not need a data file

        self._upstream_aggregators_list = [{"name": upstream_aggregators_list[aggregator].name,
                                            "nature": upstream_aggregators_list[aggregator].nature.name,
                                            "contract": contracts[aggregator]}
                                           for aggregator in range(len(upstream_aggregators_list))]  # list of aggregators involved in the production of energy. The order is not important.
        self._downstream_aggregators_list = [{"name": downstream_aggregators_list[aggregator].name,
                                              "nature": downstream_aggregators_list[aggregator].nature.name,
                                              "contract": contracts[aggregator + len(upstream_aggregators_list)]}
                                             for aggregator in range(len(downstream_aggregators_list))]  # list of aggregators involved in the consumption of energy. The order is important: the first aggregator defines the final quantity of energy

        time_step = self._catalog.get("time_step")
        self._energy_physical_limits = {"minimum_energy": 0, "maximum_energy": parameters["max_power"] * time_step}

        for aggregator in self._downstream_aggregators_list:
            nature_name = aggregator["nature"]
            self._catalog.add(f"{self.name}.{nature_name}.efficiency", None)

    def reinitialize(self):
        """
        Method called by world to reinitialize energy and money balances at the beginning of each round.
        """

        for nature in self.natures:
            # message exchanged
            decision_message = self.__class__.decision_message()
            decision_message["quantity"] = [0 for _ in range(len(self._natures[nature]))]
            decision_message["price"] = [0 for _ in range(len(self._natures[nature]))]
            decision_message["aggregator"] = [agg["aggregator"].name for agg in self._natures[nature]]
            self._catalog.set(f"{self.name}.{nature.name}.energy_accorded", decision_message)
            information_message = self.__class__.information_message()
            information_message["aggregator"] = [agg["aggregator"].name for agg in self._natures[nature]]
            self._catalog.set(f"{self.name}.{nature.name}.energy_wanted", information_message)

            # results
            self._catalog.set(f"{self.name}.{nature.name}.energy_erased", [0 for _ in range(len(self._natures[nature]))])
            self._catalog.set(f"{self.name}.{nature.name}.energy_bought", [0 for _ in range(len(self._natures[nature]))])
            self._catalog.set(f"{self.name}.{nature.name}.energy_sold", [0 for _ in range(len(self._natures[nature]))])
            self._catalog.set(f"{self.name}.{nature.name}.money_earned", [0 for _ in range(len(self._natures[nature]))])
            self._catalog.set(f"{self.name}.{nature.name}.money_spent", [0 for _ in range(len(self._natures[nature]))])

        for element_name, default_value in MessagesManager.added_information.items():  # for all added elements
            self._catalog.set(f"{self.name}.{element_name}", default_value)

    def update(self):  # method updating needs of the devices before the supervision
        energy_wanted = {}  # demand or proposal of energy which will be asked eventually
        for nature in self.natures:
            energy_wanted[nature.name] = []

            for _ in range(len(self ._downstream_aggregators_list) + len(self ._upstream_aggregators_list)):
                energy_wanted[nature.name].extend(list(self._create_message().values()))

        # downstream side
        for aggregator in range(len(self ._downstream_aggregators_list)):
            nature_name = self ._downstream_aggregators_list[aggregator]["nature"]
            energy_wanted[nature_name][aggregator]["energy_minimum"] = - self._energy_physical_limits["minimum_energy"] * self._efficiency[nature_name]  # the physical minimum of energy this converter has to consume
            energy_wanted[nature_name][aggregator]["energy_nominal"] = - self._energy_physical_limits["minimum_energy"] * self._efficiency[nature_name]  # the physical minimum of energy this converter has to consume
            energy_wanted[nature_name][aggregator]["energy_maximum"] = - self._energy_physical_limits["maximum_energy"] * self._efficiency[nature_name]  # the physical maximum of energy this converter can consume
            energy_wanted[nature_name][aggregator]["efficiency"] = self._efficiency[nature_name]
            energy_wanted[nature_name][aggregator]["aggregator"] = self._downstream_aggregators_list[aggregator]['name']

        # upstream side
        for aggregator in range(len(self._upstream_aggregators_list)):
            nature_name = self._upstream_aggregators_list[aggregator]["nature"]
            energy_wanted[nature_name][aggregator + len(self ._downstream_aggregators_list)]["energy_minimum"] = self._energy_physical_limits["minimum_energy"] / self._efficiency[nature_name]  # the physical minimum of energy this converter has to consume
            energy_wanted[nature_name][aggregator + len(self ._downstream_aggregators_list)]["energy_nominal"] = self._energy_physical_limits["minimum_energy"] / self._efficiency[nature_name]  # the physical minimum of energy this converter has to consume
            energy_wanted[nature_name][aggregator + len(self ._downstream_aggregators_list)]["energy_maximum"] = self._energy_physical_limits["maximum_energy"] / self._efficiency[nature_name]  # the physical maximum of energy this converter can consume
            energy_wanted[nature_name][aggregator + len(self ._downstream_aggregators_list)]["efficiency"] = self._efficiency[nature_name]
            energy_wanted[nature_name][aggregator + len(self ._downstream_aggregators_list)]["aggregator"] = self._upstream_aggregators_list[aggregator]['name']

        self.publish_wanted_energy(energy_wanted)  # apply the contract to the energy wanted and then publish it in the catalog

    def publish_wanted_energy(self, energy_wanted):  # apply the contract to the energy wanted and then publish it in the catalog
        """
        Method sending the message containing the devices needs to its contract and then communicating it to its aggregator.
        Parameters
        ----------
        energy_wanted: message containing the information for the aggregator
        """
        for nature in self.natures:  # publication of the consumption in the catalog
            for idx in range(len(energy_wanted[nature.name])):
                energy_wanted[nature.name][idx] = self.natures[nature][idx]["contract"].contract_modification(energy_wanted[nature.name][idx], self.name)  # the contract may modify the offer
            self._catalog.set(f"{self.name}.{nature.name}.energy_wanted", energy_wanted[nature.name])  # publication of the message

    def second_update(self):
        energy_wanted = {}  # demand or proposal of energy which will be asked eventually
        for nature in self.natures:
            energy_wanted[nature.name] = []

            for _ in range(len(self._downstream_aggregators_list) + len(self._upstream_aggregators_list)):
                energy_wanted[nature.name].extend(list(self._create_message().values()))

        # determination of the energy consumed/produced
        energy_wanted_downstream = []
        energy_available_upstream = []
        for aggregator in self._downstream_aggregators_list:
            nature_name = aggregator["nature"]
            aggregator_name = aggregator["name"]
            idx = self._catalog.get(f"{self.name}.{aggregator['nature']}.energy_accorded")["aggregator"].index(aggregator_name)
            energy_wanted_downstream.append(abs(self._catalog.get(f"{self.name}.{aggregator['nature']}.energy_accorded")["quantity"][idx]) / self._efficiency[nature_name])  # the energy asked by the downstream aggregator
        for aggregator in self._upstream_aggregators_list:
            nature_name = aggregator["nature"]
            aggregator_name = aggregator["name"]
            idx = self._catalog.get(f"{self.name}.{aggregator['nature']}.energy_accorded")["aggregator"].index(aggregator_name)
            energy_available_upstream.append(abs(self._catalog.get(f"{self.name}.{aggregator['nature']}.energy_accorded")["quantity"][idx]) / self._efficiency[nature_name])  # the energy accorded by the upstream aggregator

        limit_energy_upstream = min(energy_available_upstream)
        limit_energy_downstream = min(energy_wanted_downstream)
        raw_energy_transformed = min(limit_energy_upstream, limit_energy_downstream)
        # raw_energy_transformed = (limit_energy_upstream + limit_energy_downstream) / 2  # todo try the mean as well

        # downstream side
        for aggregator in range(len(self ._downstream_aggregators_list)):
            nature_name = self ._downstream_aggregators_list[aggregator]["nature"]
            aggregator_name = self._downstream_aggregators_list[aggregator]['name']
            # resetting the demand
            energy_wanted[nature_name][aggregator]["energy_minimum"] = - raw_energy_transformed * self._efficiency[nature_name]  # the physical minimum of energy this converter has to consume
            energy_wanted[nature_name][aggregator]["energy_nominal"] = - raw_energy_transformed * self._efficiency[nature_name]  # the physical minimum of energy this converter has to consume
            energy_wanted[nature_name][aggregator]["energy_maximum"] = - raw_energy_transformed * self._efficiency[nature_name]  # the physical maximum of energy this converter can consume
            energy_wanted[nature_name][aggregator]["aggregator"] = aggregator_name
            idx = self._catalog.get(f"{self.name}.{nature_name}.energy_accorded")["aggregator"].index(aggregator_name)
            energy_wanted[nature_name][aggregator]["price"] = self._catalog.get(f"{self.name}.{nature_name}.energy_accorded")["price"][idx]
            self._catalog.set(f"{self.name}.{nature_name}.energy_wanted", energy_wanted[nature_name])  # publication of the message
            energy_wanted[nature_name][aggregator]["efficiency"] = self._efficiency[nature_name]

            # forcing the energy accorded
            energy_accorded = self._catalog.get(f"{self.name}.{nature_name}.energy_accorded")
            energy_accorded["quantity"][idx] = - raw_energy_transformed * self._efficiency[nature_name]
            self._catalog.set(f"{self.name}.{nature_name}.energy_accorded", energy_accorded)

        # upstream side
        for aggregator in range(len(self._upstream_aggregators_list)):
            nature_name = self._upstream_aggregators_list[aggregator]["nature"]
            aggregator_name = self._upstream_aggregators_list[aggregator]['name']
            # resetting the demand
            energy_wanted[nature_name][aggregator + len(self ._downstream_aggregators_list)]["energy_minimum"] = raw_energy_transformed * self._efficiency[nature_name]  # the physical minimum of energy this converter has to consume
            energy_wanted[nature_name][aggregator + len(self ._downstream_aggregators_list)]["energy_nominal"] = raw_energy_transformed * self._efficiency[nature_name]  # the physical minimum of energy this converter has to consume
            energy_wanted[nature_name][aggregator + len(self ._downstream_aggregators_list)]["energy_maximum"] = raw_energy_transformed * self._efficiency[nature_name]  # the physical maximum of energy this converter can consume
            energy_wanted[nature_name][aggregator + len(self ._downstream_aggregators_list)]["aggregator"] = aggregator_name
            idx = self._catalog.get(f"{self.name}.{nature_name}.energy_accorded")["aggregator"].index(aggregator_name)
            energy_wanted[nature_name][aggregator + len(self ._downstream_aggregators_list)]["price"] = self._catalog.get(f"{self.name}.{nature_name}.energy_accorded")["price"][idx]
            self._catalog.set(f"{self.name}.{nature_name}.energy_wanted", energy_wanted[nature_name])  # publication of the message
            energy_wanted[nature_name][aggregator + len(self ._downstream_aggregators_list)]["efficiency"] = self._efficiency[nature_name]

            # forcing the energy accorded
            energy_accorded = self._catalog.get(f"{self.name}.{nature_name}.energy_accorded")
            energy_accorded["quantity"][idx] = raw_energy_transformed * self._efficiency[nature_name]
            self._catalog.set(f"{self.name}.{nature_name}.energy_accorded", energy_accorded)

    def react(self):
        for nature in self.natures:
            energy_wanted = self.get_energy_wanted(nature)
            energy_accorded = self.get_energy_accorded(nature)
            energy_erased = []
            energy_bought = []
            energy_sold = []
            money_earned = []
            money_spent = []
            proxy_accorded = [dict(zip(energy_accorded.keys(), values)) for values in zip(*energy_accorded.values())]
            for idx in range(len(energy_wanted)):
                for _j in range(len(proxy_accorded)):
                    if energy_wanted[idx]['aggregator'] == proxy_accorded[_j]['aggregator']:
                        [proxy_accorded[_j], erased, bought, sold, earned, spent] = self.natures[nature][_j]["contract"].billing(energy_wanted[idx], proxy_accorded[_j], self.name)  # the contract may adjust things
                        energy_erased.insert(0, erased)
                        energy_bought.insert(0, bought)
                        energy_sold.insert(0, sold)
                        money_earned.insert(0, earned)
                        money_spent.insert(0, spent)
                        break

            self.set_energy_accorded(nature, energy_accorded)

            # update of the data at the level of the device
            self._catalog.set(f"{self.name}.{nature.name}.energy_erased", energy_erased)  # TODO: à faire comptabiliser par les contrats
            self._catalog.set(f"{self.name}.{nature.name}.energy_bought", energy_bought)
            self._catalog.set(f"{self.name}.{nature.name}.energy_sold", energy_sold)
            self._catalog.set(f"{self.name}.{nature.name}.money_earned", money_earned)
            self._catalog.set(f"{self.name}.{nature.name}.money_spent", money_spent)

        if self._moment is not None:
            self._moment = (self._moment + 1) % self._period  # incrementing the hour in the period

        for aggregator in self._downstream_aggregators_list:
            nature_name = aggregator["nature"]
            self._catalog.set(f"{self.name}.{nature_name}.efficiency", self._efficiency[nature_name])

    def make_balances(self):
        energy_sold = dict()
        energy_bought = dict()
        energy_erased = dict()
        money_spent = dict()
        money_earned = dict()

        keys_dict = {nature.name: MessagesManager.added_information for nature in self.natures}  # a summary of all values linked to additionnal elements
        idx = len(self._upstream_aggregators_list)
        for nature in self.natures:
            energy_erased["upstream"] = sum(self._catalog.get(f"{self.name}.{nature.name}.energy_erased")[:idx])
            energy_erased["downstream"] = sum(self._catalog.get(f"{self.name}.{nature.name}.energy_erased")[idx:])
            energy_bought["upstream"] = sum(self._catalog.get(f"{self.name}.{nature.name}.energy_bought")[:idx])
            energy_bought["downstream"] = sum(self._catalog.get(f"{self.name}.{nature.name}.energy_bought")[idx:])
            energy_sold["upstream"] = sum(self._catalog.get(f"{self.name}.{nature.name}.energy_sold")[:idx])
            energy_sold["downstream"] = sum(self._catalog.get(f"{self.name}.{nature.name}.energy_sold")[idx:])
            money_earned["upstream"] = sum(self._catalog.get(f"{self.name}.{nature.name}.money_earned")[:idx])
            money_earned["downstream"] = sum(self._catalog.get(f"{self.name}.{nature.name}.money_earned")[idx:])
            money_spent["upstream"] = sum(self._catalog.get(f"{self.name}.{nature.name}.money_spent")[:idx])
            money_spent["downstream"] = sum(self._catalog.get(f"{self.name}.{nature.name}.money_spent")[idx:])

            for key in keys_dict[nature.name]:
                keys_dict[nature.name][key] = self._catalog.get(f"{self.name}.{nature.name}.energy_accorded")[key]

            # balance for different natures
            energy_sold_nature = self._catalog.get(f"{nature.name}.energy_produced")
            energy_bought_nature = self._catalog.get(f"{nature.name}.energy_consumed")
            energy_erased_nature = self._catalog.get(f"{nature.name}.energy_erased")
            money_spent_nature = self._catalog.get(f"{nature.name}.money_spent")
            money_earned_nature = self._catalog.get(f"{nature.name}.money_earned")

            self._catalog.set(f"{nature.name}.energy_produced", energy_sold_nature + energy_sold["upstream"] + energy_sold["downstream"])  # report the energy delivered by the device
            self._catalog.set(f"{nature.name}.energy_consumed", energy_bought_nature + energy_bought["upstream"] + energy_bought["downstream"])  # report the energy consumed by the device
            self._catalog.set(f"{nature.name}.energy_erased", energy_erased_nature + energy_erased["upstream"] + energy_erased["downstream"])  # report the energy consumed by the device
            self._catalog.set(f"{nature.name}.money_spent", money_spent_nature + money_spent["upstream"] + money_spent["downstream"])  # money spent by the aggregator to buy energy during the round
            self._catalog.set(f"{nature.name}.money_earned", money_earned_nature + money_earned["upstream"] + money_earned["downstream"])  # money earned by the aggregator by selling energy during the round

            for key in keys_dict[nature.name]:
                old_value = self._catalog.get(f"{nature.name}.{key}")
                self._catalog.set(f"{nature.name}.{key}", old_value + keys_dict[nature.name][key])

            # balance at the contract level
            for upstream in self._upstream_aggregators_list:
                contract = upstream["contract"]
                energy_sold_contract = self._catalog.get(f"{contract.name}.energy_sold")
                energy_bought_contract = self._catalog.get(f"{contract.name}.energy_bought")
                energy_erased_contract = self._catalog.get(f"{contract.name}.energy_erased")
                money_spent_contract = self._catalog.get(f"{contract.name}.money_spent")
                money_earned_contract = self._catalog.get(f"{contract.name}.money_earned")

                self._catalog.set(f"{contract.name}.energy_sold", energy_sold_contract + energy_sold["upstream"])  # report the energy delivered by the device
                self._catalog.set(f"{contract.name}.energy_bought", energy_bought_contract + energy_bought["upstream"])  # report the energy consumed by the device
                self._catalog.set(f"{contract.name}.energy_erased", energy_erased_contract + energy_erased["upstream"])  # report the energy consumed by the device
                self._catalog.set(f"{contract.name}.money_spent", money_spent_contract + money_spent["upstream"])  # money spent by the contract to buy energy during the round
                self._catalog.set(f"{contract.name}.money_earned", money_earned_contract + money_earned["upstream"])  # money earned by the contract by selling energy during the round

                for key in keys_dict[nature.name]:
                    old_value = self._catalog.get(f"{contract.name}.{key}")
                    self._catalog.set(f"{contract.name}.{key}", old_value + keys_dict[nature.name][key])

            for downstream in self._downstream_aggregators_list:
                contract = downstream["contract"]
                energy_sold_contract = self._catalog.get(f"{contract.name}.energy_sold")
                energy_bought_contract = self._catalog.get(f"{contract.name}.energy_bought")
                energy_erased_contract = self._catalog.get(f"{contract.name}.energy_erased")
                money_spent_contract = self._catalog.get(f"{contract.name}.money_spent")
                money_earned_contract = self._catalog.get(f"{contract.name}.money_earned")

                self._catalog.set(f"{contract.name}.energy_sold", energy_sold_contract + energy_sold["downstream"])  # report the energy delivered by the device
                self._catalog.set(f"{contract.name}.energy_bought", energy_bought_contract + energy_bought["downstream"])  # report the energy consumed by the device
                self._catalog.set(f"{contract.name}.energy_erased", energy_erased_contract + energy_erased["downstream"])  # report the energy consumed by the device
                self._catalog.set(f"{contract.name}.money_spent", money_spent_contract + money_spent["downstream"])  # money spent by the contract to buy energy during the round
                self._catalog.set(f"{contract.name}.money_earned", money_earned_contract + money_earned["downstream"])  # money earned by the contract by selling energy during the round

                for key in keys_dict[nature.name]:
                    old_value = self._catalog.get(f"{contract.name}.{key}")
                    self._catalog.set(f"{contract.name}.{key}", old_value + keys_dict[nature.name][key])

            # balance at the agent level
            energy_erased_agent = self._catalog.get(f"{self.agent.name}.{nature.name}.energy_erased")
            self._catalog.set(f"{self.agent.name}.{nature.name}.energy_erased", energy_erased_agent + energy_erased["upstream"] + energy_erased["downstream"])  # report the energy consumed by the device

            energy_sold_agent = self._catalog.get(f"{self.agent.name}.{nature.name}.energy_sold")
            energy_bought_agent = self._catalog.get(f"{self.agent.name}.{nature.name}.energy_bought")
            self._catalog.set(f"{self.agent.name}.{nature.name}.energy_sold", energy_sold_agent + energy_sold["upstream"] + energy_sold["downstream"])  # report the energy delivered by the device
            self._catalog.set(f"{self.agent.name}.{nature.name}.energy_bought", energy_bought_agent + energy_bought["upstream"] + energy_bought["downstream"])  # report the energy consumed by the device

            money_spent_agent = self._catalog.get(f"{self.agent.name}.money_spent")
            money_earned_agent = self._catalog.get(f"{self.agent.name}.money_earned")
            self._catalog.set(f"{self.agent.name}.money_spent", money_spent_agent + sum(money_spent.values()))  # money spent by the aggregator to buy energy during the round
            self._catalog.set(f"{self.agent.name}.money_earned", money_earned_agent + sum(money_earned.values()))  # money earned by the aggregator by selling energy during the round

            for key in keys_dict[nature.name]:
                old_value = self._catalog.get(f"{self.agent.name}.{key}")
                self._catalog.set(f"{self.agent.name}.{key}", old_value + keys_dict[nature.name][key])
