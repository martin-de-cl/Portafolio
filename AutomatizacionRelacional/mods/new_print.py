#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
        New Print

  Modulo para hacer Print de mensaje al estilo TEE de las utilidades GNU
  puede imprimir mensajes en consola y a la vez redirigir el output a un
  archivo de LOG

    @BY     : MARTIN PIMENTEL TARBUSKOVIC
    @DATE   : 2026_02_26
    @LICENSE: MIT

"""

from datetime import datetime as dt
from os.path import abspath
from os.path import exists

class NewPrint():


    #agregar metodo para escribir a archivo

    def __init__(self, PATH_TO_FILE:str='./etc/new_print.log', LOG_FLAG:bool=True):
        log_path = abspath(PATH_TO_FILE)
        self.LOG_FLAG = LOG_FLAG
        self.LOG_FILE = log_path

    def _check_for_file(self, file):
        if not exists(file):
            pass
        pass

    def print_and_log(self, icon:str, process:str, message:str):
        format_message = "[{}][{}][{}] - {}".format(dt.now().strftime("%Y-%m-%d %H:%M:%S"),icon, process, message)
        if self.LOG_FLAG:
            with open(self.LOG_FILE, 'a') as log_file:
                log_file.write("{}{}".format(format_message, '\r\n'))
        print(format_message)
