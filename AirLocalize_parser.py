# Script for getting the number of dots counted from the .loc3 file output from Airlocalize.m
# To run, Im assuming your file structure is made up of a main directory (the experiment) with
# sub-directories containing the conditions of the experiment (time points etc.).
# Then in each subdirectory there should be the images you took and the
# loc3 files for all the channels. To run this, simply type in terminal "python AirLocalize.py -c ", where -c supplies
# the argument for what channel you want to count. Which should be the beginning of the file. For example if I have two
# channels, the file will be something like C1.loc3 and C2.loc3, so to count C2 I would supply the argument C2.

# Written by Max Haase on 2018/01/18 (maxabhaase@gmail.com)
# updated 2018/01/30: added the function intensities() and only write data from sorted .loc files (C3),
# which is a shitty fix for selected only those files.


########################################################################################################################
# Import the various modules needed.
import os
from os import walk
import csv
import argparse
import pandas as pd

########################################################################################################################
# Argument parser. Basically will make sure you supplied the channel argument.
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-c', '--channel', action='store', type=str, required=True, help='Channel of fluorophore')
    parser.add_argument('-s', '--sorted', action='store', type=str, required=True, help='Is your .loc file sorted: y/n)')
    args = parser.parse_args()
#
# # In the cell_dot_counter() function I use this the channel to name the file, so I need to convert it to a string.
d = vars(args)
args_str = d["channel"]
extension = d["sorted"]
if extension in "yY":
    extension = "d.loc3"
else:
    extension = ".loc3"


# hard code for editing
# args_str = "C2"

# Get the absolute path of the current directory.
script_dir = os.path.dirname(os.path.abspath(__file__))
f = []
path = script_dir


########################################################################################################################
# This function will walk through your directories ona at a time and then find the subdirectories containing the .loc3 files.
# It will then call cell_dot_counter and send it the directory with the current .loc3 file and the path to reach it.
# Next it is returned the dot count for the current subdirectory and will add that to a dictionary with its KEY being
# the subdirectory.
# Lastly, once all the subdirectories have been read and counted it will pass off the dictionary to the writer() funct.


def file_tree_parser():
    for (dirpath, dirnames, filenames) in walk(path):
        dirnumber = len(dirnames)
        for x in range(dirnumber):
            path_2 = os.path.join(path, dirnames[x])
            print(dirnames[x])
            cell_dot_count_dic = {"Cell" : "Dot count"}
            intensities_dict = {"Cell" : "Intensities"}
            for (dirpath_2, dirnames_2, filenames_2) in walk(path_2):
                if len(dirnames_2) == 1:
                    continue
                cellnumber = len(dirnames_2)
                for y in range(cellnumber):
                    dot = cell_dot_counter(dirnames_2[y], path_2)
                    if dot is None:
                        continue
                    cell_dot_count_dic[dirnames_2[y]] = dot
                writer_1(cell_dot_count_dic, dirnames[x])


########################################################################################################################
# This function will take the subdirectory with the .loc3 file and will only read the correct file (given by args).
# Then it will remove any rows with negative intensities and return the value of the number of calculated dots (#rows)


def cell_dot_counter(dirnames, path):
    print(dirnames)
    for (dirpath, dirnames, filenames) in walk(os.path.join(path, dirnames)):
        for file in filenames:
            if file.endswith(extension) and file.startswith(args_str):
                file = dirpath + "/" + file
                with open(file, 'r') as f:
                    try:
                        reader = pd.read_csv(f, header=None,  delim_whitespace=True)
                        dot_count = 0
                        df = reader[reader[3] >= 0]
                        intensities(df, file)
                        dot_count = len(df)
                        return dot_count
                    except:
                        dot_count = 0
                        return dot_count


########################################################################################################################
# The intensities() function will take the intensities of each "dot" and output it to a csv file.
# It simply takes the dataframe read in by cell_dot_counter() and saves the forth column of the .loc3 file to a csv
# file.


def intensities(dataframe, name):
    dataframe[3].to_csv("{}_Intensities.csv".format(name), encoding='utf-8', index=False)
    return


########################################################################################################################
# The writer() function just writes the dictionary (supplied from file_tree_parser()) to a .csv file. KEYS and VALUES
# are stored in columns named "Cell" and "Dot count", respectively.


def writer_1(dict, name):
    w = csv.writer(open("{}_{}.csv".format(name, args_str), "w"))
    for key, val in dict.items():
        w.writerow([key, val])


########################################################################################################################
# Call the function to execute the program.

file_tree_parser()