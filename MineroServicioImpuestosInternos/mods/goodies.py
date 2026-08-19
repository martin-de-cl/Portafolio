#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Modulo de libreria metodos utiles
    1.- Selenium Support:
        Clase de metodos para apoyar el servicio de webdriver. Estos metodos no existen en la libreria actual
        por lo que para evitar la escritura repetitiva, se han creado decoradores para minimizar el verbosing
        en el codigo.
    2.- Navegation Tricks:
        Clase con metodos de navegacion para servicios webdrivers. Esta clase provee metodos escritos en JS
        y por tanto son evaluados de forma segura, para evitar inyecciones de algun tipo.
    3.- String Utils:
        Ofrece metodos de operaciones de strings de manera reducida
    4.- FileDog:
        Contiene metodos relacionados a archivos y directorios. De esta manera es posible vigilar archivos,
        de manera asincronica, revisar la existencia de estos, obtencion de nombres y metadata, y metodos
        para mover archivos de forma segura
    5.- Custom Argument Parser:
        Meotod para parsear argumentos de linea de comando, en caso de que estos se especifiquen. Intenta
        seguir los estandares de POSIX en cuanto al uso de variables, pero aplicado en sistemas operativos
        Microsoft Windows, donde las opciones estandar son antecedidas por un "\", que son reemplazadas
        por el "-" para las opciones cortas y "--" para opciones largas
    6.- Windows Application Calls:
        Metodo que llama a las API's de Windows. Es posible crear y manejar objetos, con las llamadas
        programaticas a las aplicaciones. Ademas se puede abrir, chequear y cerrar procesos.
    7.- Privacy Methods:
        Metodos de ofuscacion de strings, crea una capa blanda de seguridad.
    8.- Outlook Bot:
        Metodo dedicado al manejo programatico de MS Outlook, testeado hasta la version 2012. Puede leer y
        redactar correos de forma autonoma.
    
    @BY      : Martín Pimentel Tarbuskovic
    @DATE    : 2018
    @LICENSE : MIT License

"""

import time
import win32com.client
import os
import ast
import shutil
from subprocess import run,PIPE
from sys import argv

class seleniumSupport:

    def __init__(self):
        pass

    def assert_window_handle(self, base_window, new_window):
        pass


class nav_tricks():

    # Clase de trucos de navegacion que no se encuentran en la libreria oficial
    # o no son capaces de lograr lo que se requiere

    document_props = {'height':'',
                      'width':'',
                      'site':''}

    element_props = {}


    def __init__(self, web_driver, web_element):
        # Chequeamos que los parametros sean objetos

        if web_driver is object and web_element is object:
            self.driver = web_driver
            self.driver = web_element
        else:
            raise Exception('No es un objeto %s' % web_driver)

    def return_element_pos(self, driver, element):
        # Devuelve la posicion relativa de un elemento relativo al documento
        # en forma de String, sin decimales

        js_in = 'return arguments[0].getBoundingClientRect().top + document.documentElement.scrollTop;'
        return driver.execute_script(js_in, element).split('.')[0]


    def scroll_to_element_pos(self, driver, element, displacement=0):
        # Hace scroll hasta la posicion calculada de un elemento
        # en caso de que los metodos de la libreria fallen

        js_in = 'return arguments[0].getBoundingClientRect().top + document.documentElement.scrollTop;'
        elem_pos = str(int(driver.execute_script(js_in, element))+int(displacement)).split('.')[0]
        driver.execute_script('window.scrollTo(0, '+ elem_pos +');')


    def scroll_to_start_of_doc(self, driver):
        driver.execute_script('window.scrollTo(0, 0);')


    def scroll_to_end_of_doc(self, driver):
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')


    def set_element_to_visible(self, driver, element):
        js = 'arguments[0].style.visibility = "visible";'
        driver.execute_script(js, element)


class stringUtils:

    def __init__(self, word=None):
        if word is None:
            raise Exception('No word was given')
        else:
            self.word_list = word
            if word is list or word is tuple:
                self.islist = True
            else:
                self.islist = False

    def swap_tilde_chars(self, palabras):

        # Metodo de fuerza bruta para cambiar Caracteres que no se encuentre en el formato necesario
        # para se integrados en el sistema requerido
        #

        glosa = str(palabras)
        char_map = ['Á', 'á', 'É', 'é', 'Ó', 'ó', 'Í', 'í', 'Ú', 'ú', 'ü','Ü']
        char_dict = {'Á':'A', 'á':'a', 'É':'E', 'é':'e', 'Ó':'O', 'ó':'o', 'Í':'I', 'í':'i', 'Ú':'U', 'ú':'u',
                     'ü':'u','Ü':'U'}

        for char in char_map:
            if char in glosa:
                glosa.replace(char, char_dict[char])
        return glosa

    def swap_list_of_word(self, ls_words):
        ls_tmp = []
        for palabra in ls_words:
            ls_tmp.append(self.swap_tilde_chars(palabra))
        return ls_tmp

    def swap_one_word(self, one_word):
        return self.swap_tilde_chars(one_word)

    @staticmethod
    def concat_plain_txt(ls_of_what_to_concat):
        line = ''
        for element in ls_of_what_to_concat:
            line += '%s' % element
        return line

    @staticmethod
    def printInLine(stringToOutput, animacion=None, formatToOutput=None):
        if animacion is not None and formatToOutput is not None:
            return  print(stringToOutput, end='\r')
        else:
            return print(formatToOutput%(stringToOutput, animacion), end='\r')

    @staticmethod
    def miniTee(whatToPrint, fileToOutput):
        print(whatToPrint, file=os.path.abspath(fileToOutput))


class file_dog(object):

    files_dict = {}
    ls_files_on_watch = []

    def __init__(self, folder_for_watching, id_empresa=None, id_cuenta=None):

        self.carpeta = os.path.abspath(folder_for_watching)

        if id_empresa is not None:
            self.cmp_code = str(id_empresa)
        else:
            self.cmp_code = 'tmp'

        # TODO: Ver bien como parsear esto
        if id_cuenta is not None:
            self.cuenta = str(id_cuenta)
        else:
            self.cuenta = 'YYY-XXXXX'


    def get_newest_file(self, tmp_flag='part'):

        # Vigilar la carpeta para asegurar que no exista un .part en la lista de archivo
        # Encuentra el ultimo archivo creado o modificado

        while True:
            if tmp_flag in max([f for f in os.listdir(self.carpeta)],
                             key=lambda xa: os.path.getctime(os.path.join(self.carpeta, xa))):
                time.sleep(1)
            else:
                time.sleep(1)
                return max([f for f in os.listdir(self.carpeta)],
                             key=lambda xa: os.path.getctime(os.path.join(self.carpeta, xa)))


    def rel_new_name_to_old_name(self, file_final_name):

        if self.cmp_code is not None:
            if not self.cmp_code in self.files_dict:
                self.files_dict[self.cmp_code] = [self.get_newest_file()]
                print('Key creada [%s] - Value añadido [%s]' % (self.cmp_code,self.get_newest_file()))
            else:
                self.files_dict[self.cmp_code].append(self.get_newest_file())
                print('Value añadido: %s : %s' % (self.cmp_code, self.get_newest_file()))
        else:
            print('Funcion no disponible - Falta codigo de empresa')


    def get_renames(self):


        def check_type(value, expected_type=None):
            value_type = str(type(value)).split(' ')[1].replace("'", '').replace('>', '')

            if expected_type is not None:
                if value_type == expected_type:
                    return True
                elif value_type != expected_type:
                    return False
                else:
                    raise Exception('Unexpected error checking %s against %s' % (value_type, expected_type))
            else:
                return value_type

        for old_name, new_name in self.files_dict.items():
            os.rename(os.path.abspath(self.carpeta + '/' + old_name), os.path.abspath(self.carpeta + '/' + new_name))

        for key, value in self.files_dict.items():

            value_type = str(type(value)).split(' ')[1].replace("'", '').replace('>', '')

            if value_type == 'int' or value_type == 'str':
                pass
            elif value_type == 'tuple':
                for val in value:
                    print(val)
            else:
                raise Exception('Unmmaped type for this app, ValueTyp:= %s' % value_type)


    def masive_mov(self, files_path):

        if os.listdir(os.path.abspath(files_path)):
            pass
        else:
            raise FileExistsError('La ruta al directorio no existe %s'% files_path)


    @staticmethod
    def share_files(origin, destiny):

        tries_counter = 0

        if not os.path.exists(origin):
            raise Exception('No existe el archivo de origen %s'%origin)
        else:
            pass

        if not os.path.exists(destiny):
            raise Exception('No existe la ruta de destino %s'%destiny)
        else:
            pass

        while True:
            try:
                shutil.copy(os.path.abspath(origin), os.path.abspath(destiny))
            except:
                time.sleep(5)
                tries_counter += 1
                if tries_counter > 5:
                    raise Exception('No es posible copiar en estos momentos, revise que las rutas se encuentren disponibles'
                                    '\n - %s\n - %s'%(origin,destiny))


class CustomArgParser:

    """
        Parseador de linea de comando propio. Tomas las opciones mas comunes, con identificadores de acuerdo a POSIX,
        Por lo que para ambientes Windows puede causar ambiguedad el uso de guiones, en vez del uso de fowardSlash.
        La razon es que se utiliza el standar de "/" como separador de rutas.
    """

    std_dict = {'-q': False, '--quiet': False, '-w': False, '--write_to': False, '-v': True, '--verbose': True}

    def __init__(self, ls_args, user_options_dict=None):

        self.options_dict = ls_args
        if len(self.options_dict) == 1:
            # Sin argumentos
            pass
        elif len(self.options_dict) == 2:
            # Multiples argumentos
            pass
        else:
            # Solo un argumento
            pass

        if user_options_dict is not None:
            self.custom_dict = user_options_dict
        else:
            self.custom_dict = self.std_dict

    def set_options_dict(self):
        for item1, item2 in zip(self.options_dict, self.options_dict[1:]):
            if item1.find('-') == 0 or item1.find('--') == 0:
                if item2 != self.options_dict[-1]:
                    if item2.find('-') != 0 or item2.find('--') != 0:
                        self.options_dict[item1] = item2
                    else:
                        self.options_dict[item1] = True
                else:
                    if item2.find('-') == 0 or item2.find('--') == 0:
                        self.options_dict[item1] = True
            else:
                raise Exception('El argumento "%s" no es un argumento valido'%item1)

    def get_options(self):
        return self.options_dict


class winAppCalls:

    def __init__(self):
        pass

    def openApp(self):
        pass

    def closeApp(self):
        pass

    def get_proc_info(self):
        pass

    @staticmethod
    def get_PID(appName):
        cmd = 'tasklist | findstr /I "%s"' % appName
        line = run(cmd, bufsize=0, stdout=PIPE, stderr=PIPE, universal_newlines=0, shell=True).stdout.decode('utf-8')
        return int(line.split(' ', maxsplit=1)[1].lstrip().split(' ', maxsplit=1)[0].rstrip())

    @staticmethod
    def get_appName(appName):
        cmd = 'tasklist | findstr /I "%s"' % appName
        line = run(cmd, bufsize=0, stdout=PIPE, stderr=PIPE, universal_newlines=0, shell=True).stdout.decode('utf-8')
        return str(line.split(' ', maxsplit=1)[0])

    @staticmethod
    def kill_app_by_name(taskName):
        cmd = 'killtask /IM "%s"' % taskName
        run(cmd)

    @staticmethod
    def kill_app_by_PID(taskPID):
        cmd = 'taskkill /PID %s' % taskPID
        run(cmd)


class privacyMethods:

    def __init__(self):
        pass

    @staticmethod
    def get_credentials_for_login(Banco, Empresa, credenciales):

        with open(credenciales, 'r') as le_file:
            data = le_file.read().replace('\n', '')

        credenciales = ast.literal_eval(data)
        try:
            return credenciales[Banco][Empresa]
        except KeyError:
            print('No existe tal combinacion de BANCO-EMPRESA')


class outlook_bot(object):

    def __init__(self, folder_to_dl_attachment=None, recipient_address=None, path_of_attachment=None, main_folder:str='Correo Usuario', secondary_folder:str='Bandeja de entrada'):

        self.outlook = win32com.client.Dispatch("Outlook.Application")

        if folder_to_dl_attachment is not None:
            self.folder = self.outlook.GetNamespace("MAPI").Folders[main_folder].Folders[secondary_folder].Folders[folder_to_dl_attachment]
        else:
            self.folder = self.outlook.GetNamespace("MAPI").Folders[main_folder].Folders[secondary_folder]

        if recipient_address is not None:
            self.recipient_email = recipient_address
        else:
            self.recipient_email = None

        if path_of_attachment is not None:
            self.attachment = os.path.abspath(path_of_attachment)
        else:
            self.attachment = None


    def new_mesagge(self):

        # Datos para el correo

        subject = 'Cesiones de Facturas - Sii'
        copy_to = 'persona.uno@domain.com; persona.dos@domain.com'
        body    = 'Estimados,\nSe ha hecho extraccion y envio, del aviso de cesion de facturas en el SII.\n\n' \
                  'Saludos,\nCorreo generado de manera automatica por MineroSII'
        attachment = self.attachment

        # Formamos el correo

        mail = self.outlook.CreateItem(0)
        mail.To = self.recipient_email
        mail.CC = copy_to
        mail.Subject = subject
        mail.Body = body
        mail.Attachments.Add(attachment)
        mail.Send()


    def list_files_to_dl(self, item):
        print([att for att in item.attachments])

    def mensajes_en_carpeta(self):
        return self.folder.Items

    @staticmethod
    def file_check_local(path):
        if os.path.exists(os.path.abspath(path)):
            return True
        else:
            return False
