# Native Packages
import datetime

import numpy as np

from os import listdir, chdir, system, makedirs, path

from csv import reader

from time import process_time

# Specific imports
from src.tools.FilesExtensions import __pdf_extension__, __csv_extension__, __tex_extension__, __matplotlib_extension__

from src.tools.Utilities import adapt_path

# ##############################################################################################

class graph_options():
    def __init__(self, formats, graph_type, graph_style):
        self.formats = formats
        self.graph_type = graph_type
        self.graph_style = graph_style

__default_graph_options__ = graph_options("None", "single_series", "lines")

# ##############################################################################################
# Basic export functions

def write_and_print(message, file):  # write in the chosen file and print the message
    file.write(message + "\n")
    print(message)

# ##############################################################################################
# Export functions for numerical data

def methode_graphique(options, filename, x, y, labels):        # todo: changer le nom
    if "csv" in options.formats:
        exporter_en_csv(options, filename, x, y, labels)
    if "LaTeX" in options.formats:
        exporter_en_latex(options, filename, x, y, labels)
    if "matplotlib" in options.formats:
        exporter_en_matplotlib(options, filename, x, y, labels)


def exporter_en_csv(options, filename, x, y, labels):
    absolute_filename = path.abspath(filename)

    # Configure the exported data
    text = ""
    data = []
    for key in x:
        text += key
        data.append(x[key]["values"])
    for key in y:
        text += "; " + key
        data.append(y[key]["values"])
    text += "\n"

    for key in x:
        number_rows = len(x[key]["values"])
    number_columns = 1 + len(y)

    for i in range(0, number_rows):
        text += str(data[0][i])
        for j in range(1, number_columns):
            text += "; " + str(data[j][i])
        text += "\n"

    # Export
    file = open(filename + __csv_extension__, "x")
    file.write(text)
    file.close()


def exporter_en_latex(options, filename, x, y, labels):
    absolute_filename = path.abspath(filename)

    # Configure the future exported file
    text = "% LaTeX script" + "\n"
    text += "%=================================" + "\n"
    text += "\n"
    text += "\n"

    if options.graph_style == "lines":
        tikz_plot_options = "mark=none, line width=1.25"
    elif options.graph_style == "points":
        tikz_plot_options = "only marks, mark size=1.25"

    is_date = False
    xticklabel_angle = 0
    for key in x:
        if isinstance(x[key]["values"][0], datetime.datetime):
            is_date = True
            xticklabel_angle = 90

    is_multiple = (options.graph_type == "multiple_series")

    # Build the script
    text += r"\documentclass{standalone}" + "\n"
    text += "%" + "\n"
    text += "%" + "\n"
    text += "%" + "\n"
    text += r"% Packages" + "\n"
    text += r"\usepackage{amsmath}" + "\n"
    text += r"\usepackage{tikz}" + "\n"
    text += r"\usepackage{pgfplots}" + "\n"
    text += r"\usepackage{pgfplotstable}" + "\n"
    text += r"\usepackage{siunitx}" + "\n"
    text += "\n"
    text += r"\usepgfplotslibrary{dateplot}" + "\n"
    text += r"\pgfplotsset{compat = 1.16}" + "\n"
    text += "%" + "\n"
    text += "%" + "\n"
    text += r"% Main" + "\n"
    text += "%" + "\n"
    text += r"\begin{document}"
    text += "\n"
    text += "\n"
    text += r"\pgfplotstableread[col sep=semicolon]{" + absolute_filename + __csv_extension__ + "}{\\data}" + "\n"
    text += "\n"
    text += r"\begin{tikzpicture}" + "\n"
    text += r"\begin{axis}[" + "\n"
    text += "\t" + r"%xmin = 0.0, xmax = 1.0," + "\n"
    text += "\t" + r"%ymin = 0.0, ymax = 1.0," + "\n"
    text += "\t" + r"xlabel = {" + labels["xlabel"] + "}," + "\n"
    text += "\t" + r"ylabel = {" + labels["ylabel"] + "}," + "\n"
    text += "\t" + r"xlabel style = {font=\small, xshift=0.0cm, yshift=0.0cm}," + "\n"
    text += "\t" + r"ylabel style = {font=\small, xshift=0.0cm, yshift=0.0cm}," + "\n"
    text += "\t" + r"xticklabel style = {rotate=" + str(xticklabel_angle) + r", anchor=near xticklabel, font=\tiny, xshift=0.0cm, yshift=0.0cm}," + "\n"
    text += "\t" + r"yticklabel style = {rotate=0, anchor=near yticklabel, font=\tiny, xshift=0.0cm, yshift=0.0cm}," + "\n"
    if is_date:
        text += "\t" + "%" + "\n"
        text += "\t" + r"date coordinates in = x," + "\n"
        text += "\t" + r"xticklabel = {\year-\month-\day \, \hour:\minute}," + "\n"
    if is_multiple:
        text += "\t" + "%" + "\n"
        text += "\t" + r"legend pos = north west," + "\n"
        text += "\t" + r"legend style = {draw=none, fill=none, font=\tiny}," + "\n"
        text += "\t" + r"legend cell align = left," + "\n"
        text += "\t" + r"legend columns={2}," + "\n"
        text += "\t" + r"legend image post style={scale=2}," + "\n"
    text += "\t" + r"]" + "\n"
    for key in y:
        if y[key]["label"] == 1:
            text += "\t" + r"\addplot+[" + tikz_plot_options + "] "
            for keyy in x:
                text += "table[ x = " + keyy + ", y = " + key + "]{\\data};"
            text += "\n"
    if is_multiple:
        text += "\t" + r"\legend{ "
        buffer = []
        for key in y:
            if y[key]["label"] == 1:
                buffer.append(y[key]["legend"])
        text += ', '.join(buffer)
        text += "}" + "\n"
    text += r"\end{axis}" + "\n"
    if 'y2label' in labels:                                     # todo: check correspondance Y2 et y2label...
        text += r"\begin{axis}[" + "\n"
        text += "\t" + r"hide x axis," + "\n"
        text += "\t" + r"axis y line* = right," + "\n"
        text += "\t" + r"%xmin = 0.0, xmax = 1.0," + "\n"
        text += "\t" + r"%ymin = 0.0, ymax = 1.0," + "\n"
        text += "\t" + r"ylabel = {" + labels["y2label"] + "}," + "\n"
        text += "\t" + r"ylabel style = {font=\small, xshift=0.0cm, yshift=0.0cm}," + "\n"
        text += "\t" + r"ylabel near ticks," + "\n"
        text += "\t" + r"yticklabel style = {rotate=0, anchor=near yticklabel, font=\tiny, xshift=0.0cm, yshift=0.0cm}," + "\n"
        if is_date:
            text += "\t" + "%" + "\n"
            text += "\t" + r"date coordinates in = x," + "\n"
            text += "\t" + r"xticklabel = {\year-\month-\day \, \hour:\minute}," + "\n"
        if is_multiple:
            text += "\t" + "%" + "\n"
            text += "\t" + r"legend pos = north east," + "\n"
            text += "\t" + r"legend style = {draw=none, fill=none, font=\tiny}," + "\n"
            text += "\t" + r"legend cell align = left," + "\n"
            text += "\t" + r"legend columns={2}," + "\n"
            text += "\t" + r"legend image post style={scale=2}," + "\n"
        text += "\t" + r"]" + "\n"
        for key in y:
            if y[key]["label"] == 2:
                text += "\t" + r"\addplot+[" + tikz_plot_options + ", densely dashed] "
                for keyy in x:
                    text += "table[ x = " + keyy + ", y = " + key + "]{\\data};"
                text += "\n"
        if is_multiple:
            text += "\t" + r"\legend{ "
            buffer = []
            for key in y:
                if y[key]["label"] == 2:
                    buffer.append(y[key]["legend"])
            text += ', '.join(buffer)
            text += "}" + "\n"
        text += r"\end{axis}" + "\n"
    text += r"\end{tikzpicture}"
    text += "\n"
    text += "\n"
    text += r"\pgfplotstableclear\data" + "\n"
    text += "\n"
    text += "\n"
    text += r"\end{document}" + "\n"

    # Export
    file = open(filename+__tex_extension__, "x")
    file.write(text)
    file.close()


def exporter_en_matplotlib(options, filename, x, y, labels):
    absolute_filename = path.abspath(filename)

    # Configure the future exported file
    mpl_built_filename = absolute_filename + __pdf_extension__

    text = "# Python script" + "\n"
    text += "#=================================" + "\n"
    text += "\n"
    text += "\n"

    if options.graph_style == "points":
        mpl_plot_options = ", 's'"
    else:
        mpl_plot_options = ""

    is_multiple = (options.graph_type == "multiple_series")

    # Build the script
    text += "# Packages" + "\n"
    text += r"import matplotlib as mpl" + "\n"
    text += r"import matplotlib.pyplot as plt" + "\n"
    text += r"import pandas as pd" + "\n"
    text += "\n"
    text += "\n"
    text += "\n"
    text += "#" + "\n"
    text += "# Main" + "\n"
    text += "#" + "\n"
    text += "\n"
    text += "# Reading the data and preparing the graph options" + "\n"
    text += "columns_list = ["
    buffer = []
    buffer2 = []
    for key in x:
        tmp = f'"{key}"'
        buffer.append(tmp)
    for key in y:
        tmp = f'"{key}"'
        buffer.append(tmp)
        tmp = str(y[key]["legend"])
        tmp2 = f'"{tmp}"'
        buffer2.append(tmp2)
    text += ', '.join(buffer)
    text += "]" + "\n"
    text += r'df = pd.read_csv("' + absolute_filename + __csv_extension__ + '", sep="; ", usecols = columns_list, engine="python")' + "\n"
    text += "data = []" + "\n"
    text += "for j in range(0, len(columns_list)):" + "\n"
    text += "\t" + "buffer = []" + "\n"
    text += "\t" + "for i in range(0, len(df)):" + "\n"
    text += "\t" +"\t" + "buffer.append(df.iloc[i][j])" + "\n"
    text += "\t" + "data.append(buffer)" + "\n"
    text += "\n"
    text += "y_legends = ["
    text += ', '.join(buffer2)
    text += "]" + "\n"
    text += "\n"
    text += "# Preparing the LaTeX configuration" + "\n"
    text += r"pgf_with_latex = {  # setup matplotlib to use latex for output" + "\n"
    text += "\t" + r'"pgf.texsystem": "pdflatex",' + "\n"
    text += "\t" + r'"text.usetex": True,  # use LaTeX to write all text' + "\n"
    text += "\t" + r'"font.family": "serif",' + "\n"
    text += "\t" + r'"font.serif": [],  # blank entries should cause plots' + "\n"
    text += "\t" + r'"font.sans-serif": [],  # to inherit fonts from the document' + "\n"
    text += "\t" + r'"font.monospace": [],' + "\n"
    text += "\t" + r'"axes.labelsize": 10,  # LaTeX default is 10pt font.' + "\n"
    text += "\t" + r'"font.size": 10,' + "\n"
    text += "\t" + r'"legend.fontsize": 8,  # Make the legend/label fonts' + "\n"
    text += "\t" + r'"xtick.labelsize": 8,  # a little smaller' + "\n"
    text += "\t" + r'"ytick.labelsize": 8,' + "\n"
    text += "\t" + r'# "figure.size": [],     # default fig size of 0.9 textwidth' + "\n"
    text += "\t" + r'"text.latex.preamble": [' + "\n"
    text += "\t" + "\t" + r'r"\usepackage{amsmath}",' + "\n"
    text += "\t" + "\t" + r'r"\usepackage{siunitx}"' + "\n"
    text += "\t" + r"]" + "\n"
    text += r"}" + "\n"
    text += r"mpl.rcParams.update(pgf_with_latex)" + "\n"
    text += "\n"
    text += r"# Plot !" + "\n"
    text += r"fig = plt.figure()" + "\n"
    text += "\n"
    i = 1
    for key in y:
        for keyy in x:
            if y[key]["label"] == 1:
                text += r"plt.plot(data[0], data[" + str(i) + "]" + mpl_plot_options + ", linewidth=1.5, label=y_legends[" + str(i-1) +"])" + "\n"
                i += 1
    text += "\n"
    if is_multiple:
        text += r"plt.legend(frameon=False, loc='upper left', markerscale=2, fontsize='x-small')" + "\n"
        text += "\n"
    text += r"plt.xlabel(" + '"' + labels["xlabel"] + '"' + ")" + "\n"
    text += r"plt.ylabel(" + '"' + labels["ylabel"] + '"' + ")" + "\n"
    text += r"plt.tick_params(axis='x', rotation=0)" + "\n"
    text += r"plt.tick_params(axis='y', rotation=0)" + "\n"
    text += "\n"
    if 'y2label' in labels:
        text += "\n"
        text += r"plt.twinx()" + "\n"
        text += "\n"
        for key in y:
            for keyy in x:
                if y[key]["label"] == 2:
                    text += r"plt.plot(data[0], data[" + str(
                        i) + "]" + mpl_plot_options + ", linewidth=1.5, linestyle='dashed', label=y_legends[" + str(i - 1) + "])" + "\n"
        text += "\n"
        if is_multiple:
            text += r"plt.legend(frameon=False, loc='upper right', markerscale=2, fontsize='x-small')" + "\n"
            text += "\n"
        text += r"plt.ylabel(" + '"' + labels["y2label"] + '"' + ")" + "\n"
        text += r"plt.tick_params(axis='y', rotation=0)" + "\n"
        text += "\n"
    text += r"# Export" + "\n"
    text += r"filename = " + f'"{str(mpl_built_filename)}"' + "\n"
    text += r"fig.savefig(filename)" + "\n"

    # Export
    file = open(filename + __matplotlib_extension__, "x")
    file.write(text)
    file.close()


# ##############################################################################################
# Others

# Exception
class ExportException(Exception):
    def __init__(self, message):
        super().__init__(message)








































# =============================================================================================================
# =============================================================================================================
# =============================================================================================================



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



def graph_SFT(directory):

    latexCommand = "pdflatex "
    deleteCommand = "rm "

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

