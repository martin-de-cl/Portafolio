#!/usr/bin/env python3
#-*- coding: utf-8 -*-

"""
        OutputManager

    Clase para manajar distintos tipos de outputs de consola.

        Signals: ! : Error controlado
                 * :
                 + : Mensajes regulares de sistema
                 - : Sin Uso
                 ? : Nivel de advertencia desconocido

    Proyecto en desarrollo

    @BY         : Martin Pimentel
    @Licencia   : BSD
    @Fecha      : 2026-02-11

"""

import __main__
from os.path import abspath, dirname, join as pjoin
from datetime import datetime as dt


class OutputManager:

    def __init__(self, FLAG_LOG:bool=True, LOG_FILE:str='', verbosity:str=''):

        self.VERBOSITY  = verbosity
        self.LOG_FILE   = self._log_file(LOG_FILE)
        self.LOG_FLAG   = FLAG_LOG
        self.TIME_STAMP = "{}".format(dt.now().strftime('%Y_%m_%d %H:%M:%S'))

    def _log_file(self, log_file:str):
        if log_file is '':
            return dirname(pjoin(abspath(__main__.__file), 'LOG.txt'))
        else:
            return abspath(self.LOG_FILE)

    def _log(self, message:str):
        if self.LOG_FLAG:
            with open(self.LOG_FILE) as log_file:
                log_file.write(message)

    def _print(self, message:str):
        print(message)
        self._log(message)

    def neo_print(self, message:str, icon:str='?'):

        message = '[{}][{}] {}'.format(icon, self.TIME_STAMP, message)
        self._print(message)

    def neo_tprint(self, data:dict, orientation:bool=True, cell_width:int=10, max_table_lenght:int=80):

        # max_table_length: Cualquier cosa menor a 10 entrega la tabla sin limites de caracteres horizontales,
        #                   el valor default es de 80, pero se puede extender para monitor con mas caracteres

        def get_horizontal_decorator(dict_l:dict, width:int)->str:
            tmp_str = ''
            for x in range(len(dict_l.keys())):
                tmp_str = tmp_str + '+-{}'.format(''.ljust(width, '-'))
                if x == len(dict_l.keys()):
                    tmp_str = '{}-+'.format(tmp_str)
            return tmp_str

        def get_decorated_header(dict_l:dict, width:int)->str:
            tmp_str = ''
            keys = dict_l.keys()
            for key in keys:
                tmp_str = ' | '.join([tmp_str, key[:width]])
            tmp_keys = '| {} |'.format(tmp_str)
            return tmp_keys

        def get_decorated_data(dict_l:dict, width:int)->list:
            tmp_str = ''
            tmp_lst = []
            for lists in zip(*dict_l.values()):
                for item in lists:
                    tmp_str = ' | '.join([tmp_str, item[:width]])
                tmp_str = ' | '.join(lists)
                tmp_lst = tmp_lst.append('| {} |'.format(tmp_str))
                tmp_str = ''
            return tmp_lst

        def make_vtable(max_lenght:int):

            line_decorator = get_horizontal_decorator(dict_l=data, width=cell_width)
            header_decorator = get_decorated_header(dict_l=data, width=cell_width)
            data_decorated = get_decorated_data(dict_l=data, width=cell_width)

            if max_table_lenght <= 10:
                tmp_str = ''
                for item in data_decorated:
                    tmp_str = '\n'.join([tmp_str, item[max_lenght]])
                print('{}\n{}\n{}'.format(line_decorator[max_lenght],
                                          header_decorator[max_lenght],
                                          line_decorator[max_lenght],
                                          tmp_str,
                                          line_decorator[max_lenght]))
            else:
                print('{}\n{}\n{}'.format(line_decorator,
                                          header_decorator,
                                          line_decorator,
                                          '\n'.join(data_decorated),
                                          line_decorator))

        def make_htable():
            pass

    def neo_lprint(self):
        pass

    def neo_dprint(self):
        pass
