# This file contains 1 class corresponding to the bottom-up message (information gathering phase) and top-down (decision trnansmission)
import copy


class MessagesManager:
    """
    This class manages the messages exchanged between devices and aggregators through contracts.
    """

    # the minimum information needed everywhere
    information_message = {"type": "", "aggregator": "", "energy_minimum": 0, "energy_nominal": 0, "energy_maximum": 0, "price": 0}
    decision_message = {"aggregator": "", "quantity": 0, "price": 0}
    # the information added to all messages
    added_information = {}

    def __init__(self):
        self._specific_information_message = {}
        self._specific_decision_message = {}

    # ##########################################################################################
    # Initialization
    # ##########################################################################################

    def complete_information_message(self, additional_element: str, default_value):
        """
        When complementary information is added in the messages exchanged between devices and aggregators,
        this method updates the self._message attribute.

        Parameters
        ----------
        additional_element: any parsable type of object
        """
        self._specific_information_message = {**self._specific_information_message, **{additional_element: default_value}}

    def complete_decision_message(self, additional_element: str, default_value):
        """
        When complementary information is added in the messages exchanged between devices and aggregators,
        this method updates the self._message attribute.

        Parameters
        ----------
        additional_element: any parsable type of object
        """
        self._specific_decision_message = {**self._specific_decision_message, **{additional_element: default_value}}

    def set_type(self, device_type: str):
        self._specific_information_message["type"] = device_type

    @classmethod
    def complete_all_messages(cls, additional_element: str, default_value):
        cls.information_message = {**cls.information_message, **{additional_element: default_value}}
        cls.decision_message = {**cls.decision_message, **{additional_element: default_value}}
        cls.added_information[additional_element] = default_value

    # ##########################################################################################
    # Dynamic behavior
    # ##########################################################################################

    def create_information_message(self):
        general_message = copy.deepcopy(self.__class__.information_message)
        specific_message = copy.deepcopy(self._specific_information_message)
        information_message = {**general_message, **specific_message}

        return information_message

    def create_decision_message(self):
        general_message = copy.deepcopy(self.__class__.decision_message)
        specific_message = copy.deepcopy(self._specific_decision_message)
        decision_message = {**general_message, **specific_message}

        return decision_message

    # ##########################################################################################
    # Utilites
    # ##########################################################################################

    @property
    def information_keys(self):
        return self._specific_information_message.keys()

    @property
    def decision_keys(self):
        return self._specific_decision_message.keys()

