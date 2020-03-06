# # device subclasses management:
# # as devices are folders and not files, the operation is more subtle
# import os
# import importlib  # this library allows to import modules defined as str
#
# subclasses_list = os.listdir("lib/Subclasses/Device")  # the list of all device subclasses folders
# subclasses_list.remove("__init__.py")  # we remove the file __init__.py
# subclasses_list.remove("__pycache__")  # we remove the file __pycache__
#
# devices_subclasses = {}
#
# for subclass_name in subclasses_list:  # for each folder
#     directory = "lib.Subclasses.Device." + subclass_name + "." + subclass_name
#     devices_subclasses[subclass_name] = importlib.import_module(directory, subclass_name)  # we import the .py file


