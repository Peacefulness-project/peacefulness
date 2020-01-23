# This sheet describes the supervisor
# It contains only the name of a file serving as a "main" for the supervisor and a description


class Supervisor:

    def __init__(self, name, description):
        self._name = name  # the name of the supervisor  in the catalog
        self.description = description  # a description of the objective/choice/process of the supervisor

        self._catalog = None  # the catalog in which some data are stored

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def _register(self, catalog):  # add a catalog and create relevant entries
        self._catalog = catalog  # linking the local grid with the catalog of world

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def reinitialize(self):
        pass

    def ascendant_phase(self, cluster):  # before communicating with the exterior, the cluster makes its local balances
        # once the cluster has made made local arrangements, it publishes its needs (both in demand and in offer)
        pass

    def distribute_remote_energy(self, cluster):  # after having exchanged with the exterior, the cluster
        pass

    def _emergency_sort(self, cluster):  # a function calculating the emergency associated with devices and returning 2 sorted lists: one for the demands and one for the offers
        sorted_demands = []  # a list where the demands of energy are sorted by emergency
        sorted_offers = []  # a list where the offers of energy are sorted by emergency

        for device_name in cluster.devices:  # if there is missing energy
            Emin = self._catalog.get(f"{device_name}.{cluster.nature.name}.energy_wanted")["energy_minimum"]
            Enom = self._catalog.get(f"{device_name}.{cluster.nature.name}.energy_wanted")["energy_nominal"]
            Emax = self._catalog.get(f"{device_name}.{cluster.nature.name}.energy_wanted")["energy_maximum"]
            price = self._catalog.get(f"{device_name}.{cluster.nature.name}.energy_wanted")["price"]

            if Emax == Emin:  # if the min energy is equal to the maximum, it means that this quantity is necessary
                emergency = 1  # an indicator of how much the quantity is urgent
            else:
                emergency = (Enom - Emin) / (Emax - Emin)  # an indicator of how much the quantity is urgent

            if Emax > 0:  # if the energy is strictly positive, it means that the device or the cluster is asking for energy
                sorted_demands.append([emergency, Emax, price, device_name])
            elif Emax < 0:  # if the energy is strictly negative, it means that the device or the cluster is proposing energy
                sorted_offers.append([emergency, Emax, price, device_name])
            # if the energy = 0, then there is no need to add it to one of the list

            # methode adoptee ici pour transformer couples prix/quantités des clusters en degre d'urgence: urgence = 1 <=> prix >= 2 * prix du grid
            # oui c'est merdique
            # je sais
            # TODO: le faire proprement

        energy_price = self._catalog.get(f"{cluster.nature.name}.grid_buying_price")
        for subcluster in cluster.subclusters:
            quantities = self._catalog.get(f"{subcluster.name}.quantities_asked")

            for couple in quantities:
                emergency = min(1, couple[1]/(2*energy_price))
                if couple[0] > 0:  # if the energy is strictly positive, it means that the device or the cluster is asking for energy
                    sorted_demands.append([emergency, couple[0], couple[1], subcluster.name])
                elif couple[0] < 0:  # if the energy is strictly negative, it means that the device or the cluster is proposing energy
                    emergency = min(1, 1-emergency)  # as it is energy to sell, emergency must be reversed (it becomes more urgent when prices become lower)
                    sorted_offers.append([emergency, couple[0], couple[1], subcluster.name])

        sorted_demands = sorted(sorted_demands, reverse=True)
        sorted_offers = sorted(sorted_offers, reverse=True)

        sorted_demands.append([0, 0, 0, ""])
        sorted_offers.append([0, 0, 0, ""])

        return [sorted_demands, sorted_offers]

    def _price_sort(self, cluster):  # a function calculating the emergency associated with devices and returning 2 sorted lists: one for the demands and one for the offers
        sorted_demands = []  # a list where the demands of energy are sorted by emergency
        sorted_offers = []  # a list where the offers of energy are sorted by emergency

        for device_name in cluster.devices:  # if there is missing energy
            Emin = self._catalog.get(f"{device_name}.{cluster.nature.name}.energy_wanted")["energy_minimum"]
            Enom = self._catalog.get(f"{device_name}.{cluster.nature.name}.energy_wanted")["energy_nominal"]
            Emax = self._catalog.get(f"{device_name}.{cluster.nature.name}.energy_wanted")["energy_maximum"]
            price = self._catalog.get(f"{device_name}.{cluster.nature.name}.energy_wanted")["price"]

            if Emax == Emin:  # if the min energy is equal to the maximum, it means that this quantity is necessary
                emergency = 1  # an indicator of how much the quantity is urgent
            else:
                emergency = (Enom - Emin) / (Emax - Emin)  # an indicator of how much the quantity is urgent

            if Emax > 0:  # if the energy is strictly positive, it means that the device or the cluster is asking for energy
                sorted_demands.append([emergency, Emax, price, device_name])
            elif Emax < 0:  # if the energy is strictly negative, it means that the device or the cluster is proposing energy
                sorted_offers.append([emergency, Emax, price, device_name])
            # if the energy = 0, then there is no need to add it to one of the list

            # methode adoptee ici pour transformer couples prix/quantités des clusters en degre d'urgence: urgence = 1 <=> prix >= 2 * prix du grid
            # oui c'est merdique
            # je sais
            # TODO: le faire proprement

        energy_price = self._catalog.get(f"{cluster.nature.name}.grid_buying_price")
        for subcluster in cluster.subclusters:
            quantities = self._catalog.get(f"{subcluster.name}.quantities_asked")

            for couple in quantities:
                emergency = min(1, couple[1]/(2*energy_price))
                if couple[0] > 0:  # if the energy is strictly positive, it means that the device or the cluster is asking for energy
                    sorted_demands.append([emergency, couple[0], couple[1], subcluster.name])
                elif couple[0] < 0:  # if the energy is strictly negative, it means that the device or the cluster is proposing energy
                    emergency = min(1, 1-emergency)  # as it is energy to sell, emergency must be reversed (it becomes more urgent when prices become lower)
                    sorted_offers.append([emergency, couple[0], couple[1], subcluster.name])

        def get_prices(line):
            return line[2]

        sorted_demands = sorted(sorted_demands, key=get_prices, reverse=True)  # decreasing prices of buying
        sorted_offers = sorted(sorted_offers, key=get_prices, reverse=False)  # increasing prices of selling

        sorted_demands.append([0, 0, 0, ""])
        sorted_offers.append([0, 0, 0, ""])

        return [sorted_demands, sorted_offers]

    def _revenues_sort(self, cluster):  # a function calculating the emergency associated with devices and returning 2 sorted lists: one for the demands and one for the offers
        sorted_demands = []  # a list where the demands of energy are sorted by emergency
        sorted_offers = []  # a list where the offers of energy are sorted by emergency

        for device_name in cluster.devices:  # if there is missing energy
            Emin = self._catalog.get(f"{device_name}.{cluster.nature.name}.energy_wanted")["energy_minimum"]
            Enom = self._catalog.get(f"{device_name}.{cluster.nature.name}.energy_wanted")["energy_nominal"]
            Emax = self._catalog.get(f"{device_name}.{cluster.nature.name}.energy_wanted")["energy_maximum"]
            price = self._catalog.get(f"{device_name}.{cluster.nature.name}.energy_wanted")["price"]

            if Emax == Emin:  # if the min energy is equal to the maximum, it means that this quantity is necessary
                emergency = 1  # an indicator of how much the quantity is urgent
            else:
                emergency = (Enom - Emin) / (Emax - Emin)  # an indicator of how much the quantity is urgent

            if Emax > 0:  # if the energy is strictly positive, it means that the device or the cluster is asking for energy
                sorted_demands.append([emergency, Emax, price, device_name])
            elif Emax < 0:  # if the energy is strictly negative, it means that the device or the cluster is proposing energy
                sorted_offers.append([emergency, Emax, price, device_name])
            # if the energy = 0, then there is no need to add it to one of the list

            # methode adoptee ici pour transformer couples prix/quantités des clusters en degre d'urgence: urgence = 1 <=> prix >= 2 * prix du grid
            # oui c'est merdique
            # je sais
            # TODO: le faire proprement

        energy_price = self._catalog.get(f"{cluster.nature.name}.grid_buying_price")
        for subcluster in cluster.subclusters:
            quantities = self._catalog.get(f"{subcluster.name}.quantities_asked")

            for couple in quantities:
                emergency = min(1, couple[1] / (2 * energy_price))
                if couple[0] > 0:  # if the energy is strictly positive, it means that the device or the cluster is asking for energy
                    sorted_demands.append([emergency, couple[0], couple[1], subcluster.name])
                elif couple[0] < 0:  # if the energy is strictly negative, it means that the device or the cluster is proposing energy
                    emergency = min(1, 1 - emergency)  # as it is energy to sell, emergency must be reversed (it becomes more urgent when prices become lower)
                    sorted_offers.append([emergency, couple[0], couple[1], subcluster.name])

        def get_revenues(line):
            return line[1] * line[2]

        sorted_demands = sorted(sorted_demands, key=get_revenues, reverse=True)  # decreasing prices of buying
        sorted_offers = sorted(sorted_offers, key=get_revenues, reverse=False)  # increasing prices of selling

        sorted_demands.append([0, 0, 0, ""])
        sorted_offers.append([0, 0, 0, ""])

        return [sorted_demands, sorted_offers]

    # ##########################################################################################
    # Utility
    # ##########################################################################################

    @property
    def name(self):  # shortcut for read-only
        return self._name


class SupervisorException(Exception):
    def __init__(self, message):
        super().__init__(message)


