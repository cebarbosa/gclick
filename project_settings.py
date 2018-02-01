# -*- coding: utf-8 -*-
"""

Created on 26/05/2017

@Author: Carlos Eduardo Barbosa

General settings files for the project

"""
import os
import getpass

user = getpass.getuser()

def get_directories():
    if user == "kadu":
        home = "/home/kadu/Dropbox/gclick"
        data_dir = os.path.join(home, "data")
        tables_dir = os.path.join(home, "tables")
    if user == "natalia":
        home = "/home/kadu/Dropbox/gclick"
        data_dir = os.path.join(home, "data")
        tables_dir = os.path.join(home, "tables")
    return locals()

if __name__ == "__main__":
    pass