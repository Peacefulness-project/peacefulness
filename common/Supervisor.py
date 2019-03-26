# This sheet describes the supervisor
# It contains only the name of a file serving as a "main" for the supervisor and a description


class Supervisor:

    def __init__(self, name, filename):
        self._name = name  # the name of the supervisor  in the catalog
        self._filename = filename  # the name of the file, who must be in usr.supervisors
        self.description = ""  # a description of the objective/choice/process of the supervisor
