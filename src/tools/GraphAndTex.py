# Native Packages
import matplotlib as mpl

import matplotlib.pyplot as plt

import numpy as np

from os import listdir, chdir, system, makedirs

from csv import reader

from time import process_time



# =============================================================================================================
# =============================================================================================================
# =============================================================================================================

# def exportFigures(directoryname, nameVariable, valuesX, valuesY, labelX, labelY, legendY=None):
#
#     # 1/ various test
#     # Test if nameVariable is a str
#     if type(nameVariable) != str:
#         raise TypeError("The argument nameVariable must be a string")
#
#     # Test if it is a single plot or not
#     lengthList = len(valuesY)
#     if (lengthList < 1):
#         raise ValueError("The 'y' argument should be a list with a set of points")
#
#     os.chdir(directoryname)
#
#     filename = nameVariable + ".pdf"
#
#     # 2/ Prepare the LaTeX properties
#     pgf_with_latex = {  # setup matplotlib to use latex for output
#         "pgf.texsystem": "pdflatex",
#         "text.usetex": True,  # use LaTeX to write all text
#         "font.family": "serif",
#         "font.serif": [],  # blank entries should cause plots
#         "font.sans-serif": [],  # to inherit fonts from the document
#         "font.monospace": [],
#         "axes.labelsize": 10,  # LaTeX default is 10pt font.
#         "font.size": 10,
#         "legend.fontsize": 8,  # Make the legend/label fonts
#         "xtick.labelsize": 8,  # a little smaller
#         "ytick.labelsize": 8,
#         # "figure.size": [],     # default fig size of 0.9 textwidth
#         "text.latex.preamble": [
#             r'\usepackage{amsmath}',
#             r'\usepackage{siunitx}'
#         ]
#     }
#
#     mpl.rcParams.update(pgf_with_latex)
#
#     # 3/ Plot !
#     fig = plt.figure()
#     if legendY!=None:
#         for i in range(lengthList):
#             plt.plot(valuesX, valuesY[i], linewidth=0.5, label=legendY[i])
#         plt.xlabel(labelX)
#         plt.ylabel(labelY)
#         plt.legend()
#     else:
#         for i in range(lengthList):
#             plt.plot(valuesX, valuesY[i], linewidth=0.5)
#         plt.xlabel(labelX)
#         plt.ylabel(labelY)
#
#     # 4/ Export
#     fig.savefig(filename)

def write_results(dir_results, filename, vectX, vectY):  # fichier txt avec valeurs brutes
    # Test if filename is a str
    if type(filename) != str:
        raise TypeError("The argument filename must be a string")

    NX = len(vectX)
    NY = len(vectY)

    for i in range(NY):
        local_values_length = len(vectY[i])
        if(local_values_length != NX):
            raise ValueError("Impossible to export the data with non-equal numbers of entries")

    print(filename)

    results = open(filename, "x")

    raw_results = ""
    for i in range(NX):
        raw_results += str(vectX[i]) + " , "
        for j in range(NY - 1):
            raw_results += str(vectY[j][i]) + " , "
        raw_results += str(vectY[NY - 1][i]) + " \n "

    results.write(raw_results)


def write_LaTeX_source(dir_results, filename, dataFile, xlabel, ylabel, indicesPlot):
    # Test if filename is a str
    if type(filename) != str:
        raise TypeError("The argument filename must be a string")

    results = open(filename, "x")

    text = r"\documentclass{standalone}"
    text += "\n"
    text += r"% Packages"
    text += "\n"
    text += r"\usepackage{tikz}"
    text += "\n"
    text += r"\usepackage{pgfplots}"
    text += "\n"
    text += r"\usepackage{pgfplotstable}"
    text += "\n"
    text += r"\pgfplotsset{compat = 1.16}"
    text += "\n"
    text += r"\usepackage{siunitx}"
    text += "\n"
    text += "\n"
    text += "\n"
    text += "\n"
    text += r"% Main"
    text += "\n"
    text += r"\begin{document}"
    text += "\n"
    text += "\n"
    text += r"\pgfplotstableread[col sep = comma]{"+dataFile+"}{\\data}"
    text += "\n"
    text += r"\begin{tikzpicture}"
    text += "\n"
    text += r"\begin{axis}["
    text += "\n"
    text += r"  %xmin=0.0, xmax=1.0,"
    text += "\n"
    text += r"  %ymin=0.0, ymax=1.0,"
    text += "\n"
    text += r"  xlabel={"+xlabel+"},"
    text += "\n"
    text += r"  ylabel={" + ylabel + "},"
    text += "\n"
    text += r"]"
    text += "\n"
    for i in range(len(indicesPlot)):
        text += r"    \addplot+[mark=none, line width=1.25] table[ x index = "+str(indicesPlot[i][0])+", y index = "+str(indicesPlot[i][1])+"]{\\data};"
        text += "\n"
    text += "\n"
    text += r"\end{axis}"
    text += "\n"
    text += r"\end{tikzpicture}"
    text += "\n"
    text += r"\pgfplotstableclear\dataA"
    text += "\n"
    text += "\n"
    text += r"\end{document}"

    results.write(text)

# =============================================================================================================
#                       Export du pdf directement depuis python
# =============================================================================================================

# # Plotting a simple graph (only one plot)
# #-----------------------------------------------------
#
# listValuesX = Xvalues
# listValuesY = YvaluesSimple
#
# # Ex 1
# nameVariable = "rho"
# xLabel = r"$\aleph \,[\si{\joule\per\kelvin\per\kilogram}]$"
# yLabel = r"$\rho \,[\si{\joule\per\kelvin\per\kilogram}]$"
#
# exportFigures(outputDir, nameVariable, listValuesX, listValuesY, xLabel, yLabel)
#
# os.chdir("../")
#
# # Ex 2
# nameVariable = "beta"
# xLabel = r"$\aleph \,[\si{\joule\per\kelvin\per\kilogram}]$"
# yLabel = r"$\beta \,[\si{\joule\per\kelvin\per\kilogram}]$"
# legend = list()
# legend.append("x+y")
#
# exportFigures(outputDir, nameVariable, listValuesX, listValuesY, xLabel, yLabel, legend)
#
# os.chdir("../")
#
# # Plotting multiple graph (several plots on the same figure)
# #-----------------------------------------------------
#
# listValuesY = YvaluesMultiple
#
# # Ex 1
# nameVariable = "gamma"
# xLabel = r"$\aleph \,[\si{\joule\per\kelvin\per\kilogram}]$"
# yLabel = r"$\gamma \,[\si{\joule\per\kelvin\per\kilogram}]$"
#
# exportFigures(outputDir, nameVariable, listValuesX, listValuesY, xLabel, yLabel)
#
# os.chdir("../")
#
# # Ex 2
# nameVariable = "omega"
# xLabel = r"$\omega \,[\si{\cubic\meter}]$"
# yLabel = r"$\gamma \,[\si{\joule\per\kelvin\per\kilogram}]$"
# legend = list()
# legend.append("a")
# legend.append("$\phi$")
#
# exportFigures(outputDir, nameVariable, listValuesX, listValuesY, xLabel, yLabel, legend)
#
#
# os.chdir("../")

# =============================================================================================================
#                      Export des données brutes et construction d'un fichier LaTeX
# =============================================================================================================


def graph_SFT(directory):

    latexCommand = "pdflatex "
    deleteCommand = "rm "  # todo: disjonction os

    # Data samples
    # -----------------------------------------------------

    # array dans array pour les y pour gérer plusieurs colonnes
    Xvalues = np.linspace(1.0, 10.0, 5)
    # YvaluesSimple = [np.linspace(10.0, 100.0, 5)]
    YvaluesMultiple = [np.linspace(10.0, 100.0, 5), np.linspace(50.0, 200.0, 5)]

    # print(str(Xvalues))
    # print(str(YvaluesSimple))
    # print(str(YvaluesMultiple))

    # for files in results directory

    # natures management
    data_file = open(directory + "NaturesBalances.txt", "r")

    root_name = "nature"

    # reading the results file on nature balances
    data = reader(data_file, delimiter="\t")
    columns = []

    for line in data:
        columns = [[] for i in line]
        break

    for line in data:
        for i in range(len(line) - 1):

            # the value is summed over one day
            j = 0
            value = 0
            while j < 23:
                value += line[i]
                j += 1

            # added the value in the column
            columns[i].append(line[i])
            try:
                columns[i][-1] = float(columns[i][-1])
            except:
                pass

    outputDir = directory + root_name + "/"

    nameFile = outputDir + root_name + ".txt"
    latexFile = outputDir + root_name + ".tex"

    makedirs(outputDir)
    CPU_time = process_time()  # CPU time measurement

    write_results(outputDir, nameFile, columns[0], [columns[2], columns[3], columns[6], columns[7]])

    xlabel = root_name + r", [\si{\hour}]"  # number of hours since the beginning of the year
    ylabel = root_name + r", [\si{kW.h}]"  # quantity of energy in kW.h

    # creating x/y couples
    combinatoire = list()

    combinatoire.append([0, 1])  # LVE consumed
    combinatoire.append([0, 2])  # LVE produced
    combinatoire.append([0, 3])  # Heat consumed
    combinatoire.append([0, 4])  # Heat produced

    write_LaTeX_source(outputDir, latexFile, nameFile, xlabel, ylabel, combinatoire)

    system(latexCommand+latexFile)
    system(deleteCommand+"*aux")
    system(deleteCommand+"*log")

    CPU_time = process_time() - CPU_time  # time taken by the initialization

    print(CPU_time)

