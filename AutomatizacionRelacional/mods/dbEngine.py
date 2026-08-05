#!/usr/bin/env python3
# -*- coding:utf-8

'''
      DataBase Engine

  Modulo para interaccion con base de datos SQLite

    @BY      : Martin Pimentel Tarbuskovic
    @DATE    : 2026_02_26
    @LICENSE : MIT
'''


import json
from os.path import abspath, exists
from os import rename, walk
from datetime import datetime as dt

import sqlite3
import csv
from pyexpat.errors import messages

import openpyxl as pyxl

from mods.new_print import NewPrint
from json import loads as json_loads

class DBEngine():
    def __init__(self, path_to_consumible:str='../stdin/', path_to_db:str='../res/project_2026.db', path_to_log:str='../res/log.txt', session_id:str=''):

        self.PATH_TO_CONSUMIBLE = abspath(path_to_consumible)
        self.PATH_TO_DB = abspath(path_to_db)
        self.PATH_TO_LOG = abspath(path_to_log)
        self.TABLE_SW_DATA = 'SW_DATA'
        self.TABLE_RUNTIME_INFO = 'runtime_info'
        self.SESSION_ID = session_id
        self.NP = NewPrint(PATH_TO_FILE=self.PATH_TO_LOG)

    def __create_db(self):

        queries = {'tables':
                       {
                           'OLD_SAP_NUMBER_RELATION':'CREATE TABLE "OLD_SAP_NUMBER_RELATION" ("id"	INTEGER NOT NULL UNIQUE,"ORDER_NUMBER"	TEXT,"SW_NUMBER"	TEXT,"OLD_SAP_NUMBER"	TEXT,PRIMARY KEY("id" AUTOINCREMENT))',
                           'SW_DATA' : 'CREATE TABLE "SW_DATA" ("id"	INTEGER NOT NULL UNIQUE,"ORDER_NUMBER"	TEXT,"SW_CODE"	TEXT,"STATUS"	TEXT,"STATUS_INFO"	TEXT,"ADDITIONAL_INFO_1"	TEXT,"SESSION_ID"	TEXT,"UPDATER_ID"	TEXT,"SOURCE_FILE"	TEXT,"CHECKED"	TEXT,"TIME_CREATED"	TEXT,"TIME_PROCESSED"	TEXT,"TIME_LAST_UPDATE"	TEXT,"CONFIRM_TABLE_DATA"	TEXT,"VALIDATE_TABLE_DATA"	TEXT,"ACTIVITY_TABLE_DATA"	TEXT,PRIMARY KEY("id" AUTOINCREMENT))',
                           'runtime_info': 'CREATE TABLE "runtime_info" ("id"	INTEGER NOT NULL UNIQUE,"TIME_STAMP"	TEXT,"SESSION_ID"	TEXT,"PROCESS_ID"	TEXT,PRIMARY KEY("id" AUTOINCREMENT))'
                       }
        }

        db_path = 'PLACEHOLDER'
        conn = sqlite3.connect(db_path)

        for key in queries['tables']:
            conn.execute('{}'.format(queries['tables'][key]))
        conn.commit()
        conn.close()

        self.NP.print_and_log('*', process='DBE', message='BASE DE DATOS CREADA')


    def __check_for_db(self, db_path:str):
        if exists(abspath(db_path)):
            return True
        else:
            return False

    def _open_db_connection(self):
        return sqlite3.connect(self.PATH_TO_DB)


    def _move_consumibles(self, path_old:str, path_new:str):
        rename(path_old, path_new)
        self.NP.print_and_log('+', process='DBE', message='Archivos trasladados exitosamente')

    def _transform_xlsx(self, file_path:str):
        tmp_list = []

        cell_counter = 0
        row_counter = 0
        wb = pyxl.load_workbook(filename=abspath(file_path), data_only=True)
        sh = wb.active

        self.NP.print_and_log('!', process='DBE', message='Convirtiendo archivo .xlsx a .csv')

        with open(abspath(file_path).replace('.xlsx','.csv'), 'w', newline="") as csv_file:
            writer = csv.writer(csv_file)
            for row in sh:
                for cell in row:
                    if row_counter == 0:
                        if cell_counter == 0:
                            tmp_var = cell.value
                        if cell_counter == 1:
                            tmp_var2 = cell.value
                    else:
                        if cell_counter == 0:
                            tmp_var = int(cell.value)
                        if cell_counter == 1:
                            tmp_var2 = cell.value
                    cell_counter += 1
                row_counter += 1
                tmp_list.append((tmp_var, tmp_var2))
                cell_counter = 0
            writer.writerows(tmp_list)
        self.NP.print_and_log('+', process='DBE', message='Archivo Transformado Exitosamente')
        self.NP.print_and_log('+', process='DBE', message='Moviendo archivo consumido a {}'.format(abspath('{}/{}/{}'.format(file_path.rsplit('/', 1)[0], 'old_consumibles', file_path.rsplit('/', 1)[1]))))

        self._move_consumibles(file_path, abspath('{}/{}/{}'.format(file_path.rsplit('/',1)[0],'old_consumibles', file_path.rsplit('/',1)[1])))

    def load_csv_file_to_db(self, file_path:str, table:str='SW_DATA'):

        tmp     = []
        tmp_keys = ""
        tmp_values = []

        replace_dict = {'NªActividad': 'ORDER_NUMBER',
                        'Activity Id': 'ORDER_NUMBER',
                        'NºD2':'SW_CODE',
                        'D2 Id': 'SW_CODE'}

        with open(file_path, newline="") as csv_file:
            reader = csv.reader(csv_file, delimiter=",", quotechar='|')
            for row in reader:
                tmp.append(row)
        # for item in tmp[0]:
        #     print(item)
        #     print('TMP[0] - {}'.format(tmp[0]))
        #     tmp_keys = '", "'.join(item.rstrip(",").split(","))
        # print(tmp_keys)

        tmp_keys = '{}{}{}'.format(tmp[0][0], '", "', tmp[0][1])
        for key in replace_dict:
            tmp_keys = tmp_keys.replace(key, replace_dict[key])

        for item in tmp[1:]:
            tmp_values.append('{}{}{}'.format(item[0],'", "',item[1]))
            # for subitem in item:
            #     tmp_values.append('", "'.join(subitem.rstrip(";").split(";")))

        self.NP.print_and_log('+', process='DBE', message='Creando Registros en DB')
        conn = self._open_db_connection()
        for values in tmp_values:
            cursor = conn.cursor()
            query =  'insert into {}("{}", "{}", "{}", "{}") values("{}", "{}", "{}", "{}")'.format(table, tmp_keys, "TIME_CREATED", "STATUS", "SESSION_ID", values, self._get_timestam(), "UNPROCESSED", self.SESSION_ID)
            cursor.execute(query)
            conn.commit()
        self.NP.print_and_log('+',process='DBE', message='{} - Registros Creados para archivo: {}'.format(len(tmp_values), file_path.rsplit('/',1)[1]))
        conn.close()
        self._move_consumibles(file_path, abspath('{}/{}/{}'.format(file_path.rsplit('/',1)[0],'old_consumibles', file_path.rsplit('/',1)[1])))

    def _get_timestam(self)->str:
        return dt.now().strftime('%Y%m%d_%H%M%S')

    def _check_for_consumible(self, path:str):

        if exists(path):
            self.NP.print_and_log(icon="+", process='DBE', message="Consumible encontrado en {}".format(path))
            return True
        else:
            self.NP.print_and_log(icon="+", process='DBE', message="Consumible no se encuentra en {}".format(path))
            return False

    def get_list_of_unprocessed_activities(self, batch_limit:int=200):

        self.NP.print_and_log('+', process='DBE', message='Tomando lista de Actividades sin Procesar')
        conn = self._open_db_connection()
        cursor = conn.cursor()

        test_batchlist = "select SW_DATA.ORDER_NUMBER, SW_DATA.SW_CODE from SW_DATA where STATUS is 'UNPROCESSED' and STATUS_INFO is NOT 'SW_ALREADY_ASOCIATED'"
        query = "select SW_DATA.ORDER_NUMBER, SW_DATA.SW_CODE from SW_DATA where STATUS is 'UNPROCESSED'"

        cursor.execute(test_batchlist)
        return cursor.fetchall()

    def create_session_record(self, time_stamp, session_id):
        self.NP.print_and_log('+', process='DBE', message='Creando Session record')
        conn = self._open_db_connection()
        cursor = conn.cursor()

        query = "INSERT INTO runtime_info('TIME_STAMP', 'SESSION_ID') VALUES('{}', '{}')".format(time_stamp, session_id)

        cursor.execute(query)
        conn.commit()
        self.NP.print_and_log('+', process='DBE', message='Session Record creado exitosamente')
        conn.close()

    def flag_for_testings(self, activity_number:str, message:str):

        conn = self._open_db_connection()
        cursor = conn.cursor()
        query = "update SW_DATA set CHECKED='{}' where ORDER_NUMBER='{}'".format(message, activity_number)

        cursor.execute(query)
        conn.close()

    def emergency_update(self, document_number:str, msg:str):
        conn = self._open_db_connection()
        cursor = conn.cursor()

        query = "update SW_DATA SET CHECKED=CASE WHEN CHECKED is NULL THEN '{}' ELSE CHECKED || ', ' || '{}' END where ORDER_NUMBER is '{}'".format(msg,msg,document_number)

        cursor.execute(query)

        conn.commit()
        self.NP.print_and_log('!', process='DBE', message='Advertencia de plantilla en formato incorrecto')
        conn.close()

    def update_sw_status(self, document_number:str, status:str, confirm_table:str='', validate_table:str='',
                         activity_table:str='', rejection_reason:str='', additional_info_1:str='', source_file:str=''):
        timestamp = self._get_timestam()
        conn = self._open_db_connection()
        cursor = conn.cursor()

        self.NP.print_and_log('+', process='DBE', message='Actualizando registro de actividad: {}'.format(document_number))
        if rejection_reason == '':
            query = "update SW_DATA set STATUS='{}', SOURCE_FILE='{}', STATUS_INFO='{}', ADDITIONAL_INFO_1='{}', TIME_PROCESSED='{}', TIME_LAST_UPDATE='{}', ACTIVITY_TABLE_DATA='{}', CONFIRM_TABLE_DATA='{}', VALIDATE_TABLE_DATA='{}', UPDATER_ID=CASE WHEN UPDATER_ID is NULL THEN '{}' ELSE UPDATER_ID || ', ' || '{}' END  where ORDER_NUMBER='{}'".format(status, source_file,'EXITOSO', additional_info_1,timestamp, timestamp, activity_table, confirm_table, validate_table, self.SESSION_ID, self.SESSION_ID, document_number)
        else:
            if additional_info_1 == '':
                query = "update SW_DATA set STATUS='{}', SOURCE_FILE='{}', STATUS_INFO='{}', TIME_PROCESSED='{}', TIME_LAST_UPDATE='{}', ACTIVITY_TABLE_DATA='{}', UPDATER_ID=CASE WHEN UPDATER_ID is NULL THEN '{}' ELSE UPDATER_ID || ', ' || '{}' END where ORDER_NUMBER='{}'".format(status, source_file, rejection_reason, timestamp, timestamp, activity_table,self.SESSION_ID, self.SESSION_ID, document_number)
            else:
                query = "update SW_DATA set STATUS='{}', SOURCE_FILE='{}', STATUS_INFO='{}', ADDITIONAL_INFO_1='{}',TIME_PROCESSED='{}', TIME_LAST_UPDATE='{}', ACTIVITY_TABLE_DATA='{}', UPDATER_ID=CASE WHEN UPDATER_ID is NULL THEN '{}' ELSE UPDATER_ID || ', ' || '{}' END where ORDER_NUMBER='{}'".format(status, source_file, rejection_reason, additional_info_1, timestamp, timestamp, activity_table, self.SESSION_ID, self.SESSION_ID, document_number)

        cursor.execute(query)
        conn.commit()
        self.NP.print_and_log('+', 'DBE','Registro Actualizado Correctamente')
        conn.close()

    def informe_uno(self):

        self.NP.print_and_log('+', process='DBE', message='Tomando lista de Actividades sin Procesar')
        conn = self._open_db_connection()
        conn_2 = self._open_db_connection()
        conn.row_factory = sqlite3.Row
        conn_2.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor_2 = conn_2.cursor()
        query = 'SELECT * from SW_DATA where STATUS = "PROCESSED" ORDER BY TIME_PROCESSED ASC'
        cursor.execute(query)
        cursor_2.execute(query)
        lista = cursor.fetchall()
        keys_1 = cursor_2.fetchone().keys()

        with open('../stdout/informe_procesados.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(keys_1)
            for item in lista:
                writer.writerow(item)

    def informe_dos(self):

        self.NP.print_and_log('+', process='DBE', message='Tomando lista de Actividades sin Procesar')
        conn = self._open_db_connection()
        conn_2 = self._open_db_connection()
        conn.row_factory = sqlite3.Row
        conn_2.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor_2 = conn_2.cursor()

        query = 'SELECT * from SW_DATA where STATUS = "UNPROCESSED" ORDER BY TIME_PROCESSED ASC'

        cursor.execute(query)
        cursor_2.execute(query)
        lista = cursor.fetchall()
        keys_1 = cursor_2.fetchone().keys()

        with open('../stdout/informe_No_Procesados.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(keys_1)
            for item in lista:
                writer.writerow(item)

    def informe_tres(self):

        self.NP.print_and_log('+', process='DBE', message='Tomando lista de Actividades sin Procesar')
        conn = self._open_db_connection()
        conn_2 = self._open_db_connection()
        conn.row_factory = sqlite3.Row
        conn_2.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor_2 = conn_2.cursor()

        query = 'select * from SW_DATA where CHECKED is "La generación del PDF de instrucciones ha sido omitida ya que la Plantilla actual no es válida."'

        cursor.execute(query)
        cursor_2.execute(query)
        lista = cursor.fetchall()
        keys_1 = cursor_2.fetchone().keys()

        with open('../stdout/informe_Plantilla_no_valida.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(keys_1)
            for item in lista:
                writer.writerow(item)

    def informe_cuatro(self):
        self.NP.print_and_log('+', process='DBE', message='Tomando lista de Actividades sin Procesar')
        conn = self._open_db_connection()
        conn_2 = self._open_db_connection()
        conn.row_factory = sqlite3.Row
        conn_2.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor_2 = conn_2.cursor()

        query = 'select * from SW_DATA where ADDITIONAL_INFO_1 like "%draft%"'

        cursor.execute(query)
        cursor_2.execute(query)
        lista = cursor.fetchall()
        keys_1 = cursor_2.fetchone().keys()

        with open('../stdout/informe_Estado_de_draft.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(keys_1)
            for item in lista:
                writer.writerow(item)

    def informe_cinco(self):
        self.NP.print_and_log('+', process='DBE', message='Tomando lista de Actividades sin Procesar')
        conn = self._open_db_connection()
        conn_2 = self._open_db_connection()
        conn.row_factory = sqlite3.Row
        conn_2.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor_2 = conn_2.cursor()
        query = 'select * from SW_DATA where ADDITIONAL_INFO_1 like "%draft%"'
        cursor.execute(query)
        cursor_2.execute(query)
        lista = cursor.fetchall()
        keys_1 = cursor_2.fetchone().keys()

        with open('../stdout/informe_NO_PROCESADOS_2.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(keys_1)
            for item in lista:
                writer.writerow(item)

    def informe_seis(self):
        self.NP.print_and_log('+', process='DBE', message='Tomando lista de Actividades sin Procesar')
        conn = self._open_db_connection()
        conn_2 = self._open_db_connection()
        conn.row_factory = sqlite3.Row
        conn_2.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor_2 = conn_2.cursor()
        query = 'select * from SW_DATA where ADDITIONAL_INFO_1 like "%ya configurado%"'
        cursor.execute(query)
        cursor_2.execute(query)
        lista = cursor.fetchall()
        keys_1 = cursor_2.fetchone().keys()

        with open('../stdout/informe.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(keys_1)
            for item in lista:
                writer.writerow(item)

    def check_if_already_in_db(self, activity:str)->bool:
        con=self._open_db_connection()
        cursor = con.cursor()
        query= 'select * from SW_DATA WHERE ORDER_NUMBER="{}"'.format(activity)
        cursor.execute(query)
        tmp = cursor.fetchall()
        if len(tmp)>0:
            return True
        else:
            return False

    def _json_load(self, string):
        return json.loads(string)

    def retrieve_sap_number(self, activity_n):
        last_val = 0
        conn = self._open_db_connection()
        cursor = conn.cursor()
        query = "SELECT ACTIVITY_TABLE_DATA from SW_DATA WHERE ORDER_NUMBER='{}'".format(activity_n)
        cursor.execute(query)
        ls_dict = self._json_load(cursor.fetchall()[0][0])
        for key in ls_dict.keys():
            print('{}: {}'.format(key, ls_dict[key]))
        ls_tmp = ls_dict['CONFIGURACIÓN'].split(',')
        print(ls_tmp)
        for item in ls_tmp:
            if 'Números de documentos' in item:
                print(ls_tmp[last_val+1])
            else:
                last_val += 1

    def start_up_routine(self):
        files = next(walk(self.PATH_TO_CONSUMIBLE), (None, None, []))[2]
        for file in files:
            if 'xlsx' in file:
                if self._check_for_consumible('{}/{}'.format(self.PATH_TO_CONSUMIBLE, file)):
                    self.NP.print_and_log(icon='+', process='DBE', message='Consumible Encontrado: {:.15}....{}'.format(file.rsplit('.',1)[0],file.rsplit('.',1)[1]))
                    self._transform_xlsx('{}/{}'.format(self.PATH_TO_CONSUMIBLE, file))
                    self.load_csv_file_to_db('{}/{}'.format(self.PATH_TO_CONSUMIBLE, file.replace('.xlsx','.csv')))
                    break
            if 'csv' in file:
                self.load_csv_file_to_db('{}/{}'.format(self.PATH_TO_CONSUMIBLE, file))
                break
            else:
                self.NP.print_and_log(icon='!', process='DBE', message='No hay consumibles')

    def test_suit(self):
        if self._check_for_consumible():
            self.load_csv_file_to_db(file_path=self.PATH_TO_CONSUMIBLE)

    def test_suit_2(self):
        self._transform_xlsx('../stdin/BATCH1.xlsx')


if __name__ == '__main__':
    dbe = DBEngine()

    dbe.informe_uno()

    dbe.informe_dos()

    dbe.informe_tres()

    dbe.informe_cuatro()

    dbe.informe_cinco()

    dbe.informe_seis()
