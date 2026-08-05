#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
        File Handler

  Metodos para revision de archivos para el proyecto de automatizacion

    @BY     : MARTIN PIMENTEL TARBUSKOVIC
    @DATE   : 2026_02_26
    @LICENSE: MIT

"""


from os.path import exists

class FileHandler():

    def __init__(self, path_to_file:str=""):

        self.PATH_TO_FILE = self.main(path_to_file)

    def file_exist(self):
        if exists(self.PATH_TO_FILE):
            return True
        else:
            return False

    def main(self, path_to_file:str):

        if path_to_file != "":
            if self.file_exist():
                if "xls" in self.PATH_TO_FILE:
                    self._convert_xlsx_to_csv(self.PATH_TO_FILE)
                    self.PATH_TO_CSV = self.PATH_TO_FILE.replace("xls", "csv").replace("xlsx", "csv")
