#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
    Nombre: Minero de Servicio de Impuestos Internos

        1.- Encontrar Cesion de Facturas para los ruts de las empresas en procesos
            de Confirming y Factoring
        2.- Una vez descargada la informacion, genera una lista de busqueda de certificados y los descarga
            en formato PDF.
        3.- Compartir la informacion en forma de una ruta de red, o por envio de correo
        4.- Generacion de log de proceso con opcion de guardar capturas de pantalla.
        5.- Metodos de extraccion de situacion tributaria

        Instrucciones:
        ! Advertencia: Los binarios no seran distribuidos con estos scripts.
        1.- Se necesita un binario de GekoDriver al menos en la version 0.21 y debe ser colocado
            en la ruta "./bin/geko/" y se debe apuntar la ruta al ejecutable en el constructor
            __init__ de la clase  WebDriver -> self.GEKO_PATH
        2.- Se necesia un Binario en formato portable para Firefox al menos de la version 60 y ser
            colocado en la ruta "./bin/ y se debe apuntar la ruta al ejecutable en el constructor
            __init__ de la clase WebDriver -> self.FIREFOX_PATH


    @BY     : Martín Pimentel Tarbuskovic,
    @DATE   : 2018_06_12
    @lICENSE: MIT License
"""

import os
import shutil
import win32com
import win32com.client
import datetime
import pdfkit
import urllib.request

from bs4 import BeautifulSoup
from subprocess import PIPE, run
from base64 import b64decode as decode64
from datetime import datetime as dt
from time import sleep
from mods.goodies import file_dog
from mods.csv2xls import csv2xl
from random import randint
from sys import argv
from sys import exit

from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, NoSuchFrameException, StaleElementReferenceException, UnexpectedAlertPresentException
from selenium.webdriver.common.keys import Keys


class WebMinner(object):

    """
        Clase contenedora de los metodos del Driver y los metodos de nevagacion para el servicio de impuestos internos.

    """

    def __init__(self, dlPath='./stdout/tmp/'):

        # TODO: Rellenar los datos eventualmente

        self.url        = 'https://homer.sii.cl'
        self.ls_emp     = ''  # Posiblemente inecesario
        self.file_names = ''
        self.log_pdf    = []
        self.sit_trib   = []
        self.GEKO_PATH  = './bin/geckodriver64/geckodriver-0.21.0.exe' #Reemplazar por la ruta correspondiente
        self.FIREFOX_PATH = './bin/firefoxportable60/app/firefox64/firefox.exe' #Reemplazar por la ruta correspondiente

        ffep = os.path.abspath(self.GEKO_PATH)
        ffb = FirefoxBinary(os.path.abspath(self.FIREFOX_PATH))
        ffp = webdriver.FirefoxProfile()
        ffp.set_preference("browser.download.folderList", 2)
        ffp.set_preference("browser.download.manager.showWhenStarting", False)
        ffp.set_preference("browser.download.dir", os.path.abspath(os.path.dirname(__file__) + dlPath))
        ffp.set_preference("browser.helperApps.neverAsk.saveToDisk",
                           "application/octet-stream, application/octet-stream;filename=*.txt")

        self.driver = webdriver.Firefox(firefox_binary=ffb,firefox_profile=ffp, executable_path=ffep)
        self.driver.implicitly_wait(10)

    def surf_to_sii(self):

        self.driver.get(self.url)
        self.driver.maximize_window()
        self.scrn_log()

    def login_to_sii(self, ls_usr, Pass):

        self.scrn_log()
        stop_counter     = 0
        ls_usr_data      = (ls_usr, Pass)
        ls_place_holders = ('//input[@id="rutcntr"]', '//input[@id="clave"]')
        btn_ingresar     = '//*[@id="myform"]/button'

        for box, log_cred in zip(ls_place_holders, ls_usr_data):
            try:
                self.driver.find_element_by_xpath(box).send_keys(decode64(log_cred).decode('utf-8'))
            except NoSuchElementException:
                sleep(1)
                stop_counter += 1
                if stop_counter > 5:
                    raise Exception('No se encuentran las casillas de login %s'% self.driver.current_url)
        self.scrn_log()
        self.driver.find_element_by_xpath(btn_ingresar).click()

    def surf_to_Cesiones(self, decision=2):
        # Metodo 1.- Entrar y navegar la pagina. Lenta, pero mas dificil de detectar.
        def metodo_1():

            Menu = self.driver.find_element_by_xpath('//*[@id="main-menu"]/li[2]/ul')
            self.menu_change_to_visible(Menu)

            self.driver.find_element_by_xpath('//*[@id="main-menu"]/li[2]/ul/li[4]/a').click()
            self.driver.find_element_by_xpath('//*[@id="modalCreditoFacturas"]/div/div/div[3]/button').click() #Publicidad
            sleep(2)
            self.driver.find_element_by_xpath('//*[@id="my-wrapper"]/div[2]/div/div/div[2]/p[5]/a').click() # Sistema de Facturacion de mercado
            self.driver.find_element_by_xpath('//*[@id="headingSesion"]/h4/a').click()  # Consulta de documentos tributarios
            self.driver.find_element_by_xpath('//*[@id="collapseSesion"]/div/ul/li/a').click() # Ingrese al menu registro electronico de cesiones de creditos
            self.driver.find_element_by_xpath('//*[@id="bloq_izq"]/div[3]/div[2]/ul/li[2]/a').click()

        # Metodo 2.- Entra directamente a las Cesiones
        def metodo_2():
            self.driver.get('https://palena.sii.cl/rtc/RTC/RTCMenu.html')
            self.driver.find_element_by_xpath('//*[@id="bloq_izq"]/div[3]/div[2]/ul/li[2]/a').click() # navegar a Cesiones Periodo

        if decision==2:
            metodo_2()
            self.scrn_log()
        elif decision==1:
            metodo_1()
            self.scrn_log()
        else:
            raise Exception('Solo hay 2 metodos disponibles para navegar a Cesiones')

    def surf_to_certificados_de_cesiones(self):
        self.driver.get('https://palena.sii.cl/rtc/RTC/RTCMenu.html')
        self.driver.find_element_by_xpath('//*[@id="bloq_izq"]/div[3]/div[2]/ul/li[4]/a').click()
        self.scrn_log()

    def get_facturas_cesiondas(self):

        day_minus = 1
        while True:
            start_date = (datetime.datetime.today() - datetime.timedelta(days=day_minus))
            if dt.weekday(start_date) not in (5,6):
                start_date = start_date.strftime('%d%m%Y')
                finish_date = start_date
                break
            else:
                day_minus += 1


        root_path = '/html/body/form/div/table[2]/tbody/tr/td/table'
        midle_path = '/tbody/tr[2]/td/table/tbody/tr'
        self.scrn_log()
        self.driver.switch_to.default_content()
        self.driver.find_element_by_xpath(root_path + '[1]' + midle_path + '[1]/td/input').click()
        self.driver.find_element_by_xpath(root_path + '[2]' + midle_path + '[1]/td/input').click()
        self.driver.find_element_by_xpath(root_path + '[3]' + midle_path + '[1]/td[2]/input').send_keys(Keys.CONTROL, 'a')
        self.driver.find_element_by_xpath(root_path + '[3]' + midle_path + '[1]/td[2]/input').send_keys(Keys.BACKSPACE)
        self.driver.find_element_by_xpath(root_path + '[3]' + midle_path + '[1]/td[2]/input').send_keys(start_date)
        self.driver.find_element_by_xpath(root_path + '[3]' + midle_path + '[2]/td[2]/input').send_keys(Keys.CONTROL, 'a')
        self.driver.find_element_by_xpath(root_path + '[3]' + midle_path + '[2]/td[2]/input').send_keys(Keys.BACKSPACE)
        self.driver.find_element_by_xpath(root_path + '[3]' + midle_path + '[2]/td[2]/input').send_keys(finish_date)
        self.scrn_log()
        self.driver.find_element_by_xpath('//input[@name="Submit"]').click()

    def get_certificado_facturas_cesionadas(self):

        self.driver.switch_to.default_content()
        vOld = self.driver.window_handles[0]
        self.scrn_log()
        # TODO: Ver bien si este check va aca o en el main
        dataArray = self.make_dataArray_from_facturas_list(
                os.path.abspath('./stdout/tmp/'+file_dog('./stdout/tmp/').get_newest_file()))

        if dataArray is not None:
            for factura in dataArray:

                self.driver.find_element_by_xpath('//input[@name="rut_emisor"]').send_keys(Keys.CONTROL + 'a')
                self.driver.find_element_by_xpath('//input[@name="rut_emisor"]').send_keys(Keys.BACKSPACE)
                self.driver.find_element_by_xpath('//input[@name="rut_emisor"]').send_keys(factura[0].split('-')[0])

                self.driver.find_element_by_xpath('//input[@name="dv_emisor"]').send_keys(Keys.CONTROL + 'a')
                self.driver.find_element_by_xpath('//input[@name="dv_emisor"]').send_keys(Keys.BACKSPACE)
                self.driver.find_element_by_xpath('//input[@name="dv_emisor"]').send_keys(factura[0].split('-')[1])

                self.driver.find_element_by_xpath('//input[@name="folio"]').send_keys(Keys.CONTROL + 'a')
                self.driver.find_element_by_xpath('//input[@name="folio"]').send_keys(Keys.BACKSPACE)
                self.driver.find_element_by_xpath('//input[@name="folio"]').send_keys(factura[2])

                self.driver.find_element_by_xpath('//input[@name="fecha1"]').send_keys(Keys.CONTROL + 'a')
                self.driver.find_element_by_xpath('//input[@name="fecha1"]').send_keys(Keys.BACKSPACE)
                self.driver.find_element_by_xpath('//input[@name="fecha1"]').send_keys(factura[3])

                self.driver.find_element_by_xpath('//input[@name="botonxml"]').send_keys(Keys.RETURN)

                vNew = self.driver.window_handles[1]
                self.make_pdf_from_html(vOld, vNew, factura[3].replace('-','_')+' '+factura[0]+' '+factura[2])
        self.scrn_log()

    def surf_to_situacion_tributaria(self):
        self.driver.switch_to.default_content()
        self.driver.get('https://zeus.sii.cl/cvc/stc/stc.html')

    def resolve_captcha(self):
        self.driver.switch_to.default_content()
        line = self.driver.find_element_by_xpath('//img[@id="imgcapt"]').get_attribute('src').split('Captcha=', maxsplit=1)[1]
        return decode64(line).decode('utf-8')[36:40]

    def get_situacion_tributaria(self, rut, captcha):
        def does_rut_exist():
            try:
                self.driver.switch_to.default_content()
                texto = self.driver.find_element_by_xpath('/html/body/div/center/table/tbody/tr/td/p/font').text
                if 'no existe' in texto:
                    return False
                else:
                    return True
            except NoSuchElementException:
                return True

        def verifica_rut(rut_a_verificar):
            factor = 2
            resultado = 0
            for numero in reversed(rut_a_verificar.split('-')[0].replace(' ','').replace('\n','')):
                resultado += int(numero) * factor
                if factor == 7:
                    factor = 2
                else:
                    factor += 1
            resultado = 11 - (resultado - (int(str(resultado / 11).split('.')[0]) * 11))

            if resultado == 11:
                verificador = str(0)
            elif resultado == 10:
                verificador = 'K'
            else:
                verificador = str(resultado)

            if verificador == rut_a_verificar.split('-')[1].replace(' ','').replace('\n','').upper():
                return True
            else:
                return False

        def largo_rut(rut_a_verificar):
            if len(rut_a_verificar.split('-')[0].replace(' ','').replace('\n','')) <= 8:
                return True
            else:
                return False

        def todos_numeros(rut_a_verificar):
            if str(rut_a_verificar.split('-')[0].replace(' ','').replace('\n','')).isdigit():
                return True
            else:
                return False

        try:
            if verifica_rut(rut) is True and largo_rut(rut) is True and todos_numeros(rut) is True:
                self.driver.switch_to.default_content()
                self.driver.find_element_by_xpath('//input[@id="RUT"]').send_keys(rut.split('-')[0])
                self.driver.find_element_by_xpath('//input[@id="DV"]').send_keys(rut.split('-')[1])
                self.driver.find_element_by_xpath('//*[@id="txt_code"]').send_keys(captcha)
                self.driver.find_element_by_xpath('//input[@name="ACEPTAR"]').click()
                try:
                    self.driver.switch_to.default_content()
                    raz_social = self.driver.find_element_by_xpath('//*[@id="contenedor"]/div[4]').text

                    if 'PRO-PYME' in self.driver.find_element_by_xpath('//*[@id="contenedor"]/span[5]').text:
                        size_emp   = self.driver.find_element_by_xpath('//*[@id="contenedor"]/span[5]').text
                    else:
                        size_emp   = self.driver.find_element_by_xpath('//*[@id="contenedor"]/span[4]').text

                    ini_act    = self.driver.find_element_by_xpath('//*[@id="contenedor"]/span[2]').text
                except NoSuchElementException:
                    if '**' in self.driver.find_element_by_xpath('/html/body/div/div[4]').text:
                        raz_social = 'No presenta razon social'
                    else:
                        raz_social = self.driver.find_element_by_xpath('/html/body/div/div[4]').text
                    size_emp   = self.driver.find_element_by_xpath('/html/body/div/span[4]').text
                    ini_act = self.driver.find_element_by_xpath('/html/body/div/span[2]').text
                self.sit_trib.append((rut, raz_social, ini_act.split('Actividades:')[1], size_emp.split('PRO-PYME:')[1]))
            else:
                self.sit_trib.append((rut, 'RUT INVALIDO', 'RUT INVALIDO', 'RUT INVALIDO'))
        except NoSuchElementException:
            if does_rut_exist() is False:
                self.sit_trib.append(
                    (rut, 'RUT NO EXISTE EN DB-SII', 'RUT NO EXISTE EN DB-SII', 'RUT NO EXISTE EN DB-SII'))
            else:
                raise Exception('El rut %s, presenta problemas al ser buscado'%rut)
        except UnexpectedAlertPresentException:
            raise Exception('El rut %s, levanta un aviso inesperado'%rut)

    def check_for_url_status(self):
        self.driver.get(self.url)
        try:
            self.driver.find_element_by_xpath('//*[text() [contains(.,"impuestos")]]')
            return True
        except:
            return False

    def kill_browser(self):
        self.driver.quit()

    def handle_errors(self):

        def error_999(wDriver):
            while True:
                try:
                    wDriver.switch_to.default_content()
                    if '(-999)' in wDriver.find_element_by_xpath('//body').text or '(-999)' in wDriver.find_element_by_xpath('//body/br').text:
                        print('Error (-999) en tratamiento')
                        wDriver.find_element_by_xpath('//body').send_keys(Keys.ALT, Keys.ARROW_LEFT)
                        return True
                    elif '(-999)' in wDriver.find_element_by_xpath('//*'):
                        wDriver.find_element_by_xpath('//body').send_keys(Keys.ALT, Keys.ARROW_LEFT)
                        print('da way')
                        return True
                    elif self.driver.find_element_by_xpath('//*[text() [contains(.,"(-999)")]]') is not None:
                        wDriver.find_element_by_xpath('//body').send_keys(Keys.ALT, Keys.ARROW_LEFT)
                        print('handled')
                        return True
                    else:
                        print('false')
                        return False
                except NoSuchElementException:
                    return False


        def otro_error(wDriver):
            # Placeholder para cualquier otro tipo de error no relacionado con
            # la busqueda de certificados de cesion de facturas
            pass

        error_list = [error_999, otro_error]

        for error in error_list:
            if error(self.driver) is True:
                break
        else:
            raise Exception('No hay mas handlers. Puede que el error sea nuevo')

    def menu_change_to_visible(self, element):
        script = "arguments[0].style.display='block';"
        self.driver.execute_script(script,element)

    def scrn_log(self, scrnOutput='./log/scrn/'):

        path_to_file = os.path.abspath(os.path.dirname(__file__) + scrnOutput + 'screenshot - 1.png')
        if os.path.exists(path_to_file) is True:
            version = '2'
            path_to_file = scrnOutput + 'screenshot - %s.png'
            while os.path.isfile(path_to_file % version):
                version = int(version) + 1
            path_to_file = path_to_file % version
        self.driver.save_screenshot(path_to_file)

    def make_dataArray_from_facturas_list(self, path_to_invoices_csv):

        line_count=0
        ls_dataArray = []

        with open(path_to_invoices_csv, 'r') as lefile:
            for line in lefile:
                line_count+=1
                if line_count > 2:
                    ls_dataArray.append(
                        (line.split(';')[0],
                         line.split(';')[5],
                         line.split(';')[6],
                         str(line.split(';')[15].split(' ')[0])
                         ))

        if len(ls_dataArray) > 1:
            return ls_dataArray
        else:
            return None

    def make_pdf_from_html(self, old_window, new_window, name):

        ls_images = []

        self.driver.switch_to.window(new_window)
        self.driver.maximize_window()
        self.scrn_log()
        sleep(2)
        source_string = self.driver.page_source

        Bsoup = BeautifulSoup(source_string, 'lxml')

        for img in self.driver.find_elements_by_xpath('//img'):
            urllib.request.urlretrieve(
                img.get_attribute('src'), './stdout/tmp/'+ img.get_attribute('src').rsplit('/', maxsplit=1)[1])
            ls_images.append(str('./' + img.get_attribute('src').rsplit('/', maxsplit=1)[1]))

        for img, new_src in zip(Bsoup.find_all('img'), ls_images):
            img['src'] = new_src

        new_source_string = str(Bsoup)

        with open('./stdout/tmp/tmp_site.html','w') as file:
            file.write(new_source_string)

        pdfkit.from_file('./stdout/tmp/tmp_site.html', './stdout/tmp/'+name+'.pdf')

        self.log_pdf.append('[+]    Archivo descargado: %s.pdf'%name)
        self.driver.close()
        self.driver.switch_to.window(old_window)

    def log_out_sii(self):
        # TODO: buscar placeholder para log out
        self.driver.switch_to.default_content()
        self.driver.switch_to.frame(self.driver.find_element_by_xpath(''))

class loger(object):

    # Objetor contenedor del output del programa.
    # Escribe un objeto de log en forma sincronica, o realizar un logDump
    # al final de la ejecucion.

    def __init__(self, log_path='./log/log.txt'):
        self.now_time = dt.today()
        self.log_ls = []
        self.log_path = os.path.abspath(os.path.dirname(__file__)+ log_path)

    def tee_output(self, mensaje):
        self.log_ls.append(mensaje)
        print(mensaje)

    def tee_sync_output(self, mensaje):
        print(mensaje, file=self.log_path)

    def drop_log_txt(self, ls_log):

        drop_path = self.log_path

        with open(drop_path, 'a') as le_file:
            le_file.write('[%s] - Inicio de Extractor - SII \n'%self.now_time.strftime('%Y/%m/%d - %H:%M:%S'))
            le_file.writelines(ls_log)
            le_file.write('\n[%s] - Fin de Extractor - SII \n\n'%dt.today().strftime('%Y/%m/%d - %H:%M:%S'))

    def drop_output(self, ls_log):
        for line in ls_log:
            print(line)

    @staticmethod
    def no_output_progressbar(metaFinal, presente):
        porcentaje = round((int(presente)/int(metaFinal))*100,0)
        while metaFinal < 100:
            print('Progreso: %s'%porcentaje + '%', end='\r')
        print(print('Progreso: %s'%porcentaje + '%', end='\n'))


class outlook_bot(object):

    def __init__(self, folder_to_dl_attachment=None, recipient_address=None, path_of_attachment=None):

        self.outlook = win32com.client.Dispatch("Outlook.Application")
        self.USER = 'USER' #Usuario de la instancia de outlook abierta para ser manipulada
        self.EMAIL_MAIN_FOLDER = 'Bandeja de entrada' # Puede cambiar segun idioma
        self.OUTLOOK_PATH = 'C:\\Program Files (x86)\\Microsoft Office\\Office14\\OUTLOOK.EXE' # Apuntar al binario local

        if folder_to_dl_attachment is not None:
            self.folder = self.outlook.GetNamespace("MAPI").Folders[self.USER].Folders[self.EMAIL_MAIN_FOLDER].Folders[folder_to_dl_attachment]
        else:
            self.folder = self.outlook.GetNamespace("MAPI").Folders[self.USER].Folders[self.EMAIL_MAIN_FOLDER]

        if recipient_address is not None:
            self.recipient_email = recipient_address
        else:
            self.recipient_email = None

        if path_of_attachment is not None:
            self.attachment = os.path.abspath(path_of_attachment)
        else:
            self.attachment = None

    def new_mesagge(self, cc:str='persona.uno@domain.com; persona.dos@domain.com')->None:

        at_cc = cc


        subject = 'Cesiones de Facturas - Sii - %s'%dt.today().strftime('%d/%m/%Y')
        copy_to = '{}'.format(at_cc)
        body    = 'Estimados,\nSe ha realizado la extraccion, de las facturas en proceso de Cesion en el SII.\n\n' \
                  'Saludos,\nCorreo generado de manera automatica por Minero SII'
        attachment = self.attachment

        # Formamos el correo

        mail = self.outlook.CreateItem(0)
        mail.To = self.recipient_email
        mail.CC = copy_to
        mail.Subject = subject
        mail.Body = body
        mail.Attachments.Add(attachment)
        mail.Send()

    def mensajes_en_carpeta(self):
        return self.folder.Items

    def list_emails(self, numerToDisplay=100, DateStart=None, DateFinish=None):
        if isinstance(DateStart,datetime.datetime) or isinstance(DateFinish,datetime.datetime) is not True:
            pass
        else:
            pass

class fileHandler(object):

    # Esta clase contiene los metodos de revision de archivos y para moverlos
    # la idea es que sean implementables en plataformas Windows y Unix-like

    def __init__(self):
        self.this_path = os.path.dirname(os.path.abspath(__file__))
        self.file_tmp  = os.path.abspath(self.this_path + '/stdout/tmp/')
        self.file_repo = os.path.abspath(self.this_path + '/stdout/repo/')
        self.file_mods = os.path.abspath(self.this_path + '/mods/')

    def move_to_repo(self):
        success = False
        shutil.copy2(os.path.join(self.file_tmp),os.path.join(self.file_repo))
        while success is False:
            if os.path.getsize(self.file_tmp) == os.path.getsize(self.file_repo):
                success = True
            else:
                sleep(2)

    def files_to_move(self, target_folder):

        for file in os.listdir(self.file_tmp):
            if '.pdf' in file or '.txt' in file or '.xlsx' in file:
                shutil.move(os.path.join(self.file_tmp, file), os.path.join(target_folder, file))

    def check_and_make_folders(self, empresa):

        # Todo: Este metodo es par implementarlo en el masive mover

        inner_cmp = decode64(empresa).decode('utf-8')
        today_date = datetime.datetime.today().strftime('%Y_%m_%d')
        today_output_fd = os.path.abspath('./stdout/repo/' + today_date + '/')
        empresa_output_df = os.path.abspath(today_output_fd + '/' + inner_cmp + '/')

        if not os.path.exists(today_output_fd):
            os.mkdir(today_output_fd)
            sleep(1)
            if not os.path.exists(empresa_output_df):
                os.mkdir(empresa_output_df)
                sleep(1)
                return empresa_output_df
        else:
            if not os.path.exists(empresa_output_df):
                os.mkdir(empresa_output_df)
                sleep(1)
                return empresa_output_df
            else:
                return empresa_output_df

    def read_file(self):
        ls_local = []

        with open(os.path.abspath(self.file_mods + '/creds.txt'), 'r') as le_file:
            for line in le_file:
                ls_local.append((line.split(';')[0], (line.split(';')[1]), (line.split(';')[2])))

        return ls_local

    def conver_txt_file(self, filepath):
        for file in os.listdir(filepath):
            if 'txt' in file:
                csv2xl(os.path.abspath(filepath + '/' +file))

    def read_ruts(self):
        ls_local = []
        with open(os.path.abspath(self.file_mods + '/Ruts-extraibles.csv'), 'r') as le_file:
            for line in le_file:
                ls_local.append(line)
        return ls_local

    @staticmethod
    def share_files(origin, destiny):
        tries_counter = 0

        if not os.path.exists(origin):
            raise Exception('No existe el archivo de origen %s' % origin)
        else:
            pass

        if not os.path.exists(destiny):
            raise Exception('No existe la ruta de destino %s' % destiny)
        else:
            pass

        while True:
            try:
                shutil.copy(os.path.abspath(origin), os.path.abspath(destiny))
                break
            except PermissionError:
                sleep(5)
                tries_counter += 1
                if tries_counter > 5:
                    raise Exception('No es posible copiar en estos momentos, revise que las rutas se encuentren disponibles'
                                    '\n - %s\n - %s' % (origin, destiny))


class ArgParser(object):

    def __init__(self):
        self.option_dict = {'--log_output':'2', '--modo_de_captura':'2', '--retry_intentions':'2',
                            '--rut_proveedor':'2', '--rut_de_sociedad_usuario':'2', '--password':'2',
                            '--ayuda':'0'} # Borrar este diccionario
        self.local_args = [arg for arg in argv[1:]]

        if len(self.local_args) == 1 and '--ayuda' in self.local_args:
            self.asking_for_help = True
        elif len(self.local_args) == 1 and '--intereactivo' in self.local_args:
            self.interactive_mode = True
        else:
            for option, parametre in zip(self.local_args[:-1], self.local_args[1:]):
                if '--' in option and parametre is not None:
                    if option == '--log_output' and os.path.exists(os.path.dirname(parametre)) and '--' not in parametre:
                        self.path_to_log = parametre
                    elif option == '--modo_de_captura' and '--' not in parametre:
                        self.runtime_mode = parametre
                    elif option == '--retry_intentions' and '--' not in parametre:
                        self.how_many_tries = int(parametre)
                    elif option == '--captura_un_proveedor' and len(parametre.split(';'))==3:
                        self.rut_proveedor = parametre.split(';')[0]
                        self.rut_sociedad = parametre.split(';')[1]
                        self.pwd_sociedad = parametre.split(';')[2]

    def interactive(self):

        def cls():
            os.system('cls' if os.name == 'nt' else 'clear')

        def bienvenida():
            return input('\n                  :::: Minero Servicio Impuestos Internos ::::\n\n'
                           'Bienvenido a la consola interactiva para el minero de Servicio de Impuestos Internos\n\n'
                           '    Por favor, elige una opcion:\n'
                           '      1.- Ejecutar extraccion completa standard de Cesiones(listas+Certificados)\n'
                           '      2.- Ejecutar extraccion comopleta, para solo una sociedad\n'
                           '      3.- Ejecutar extraccion completa por rango de fechas(solo una sociedad)\n'
                           '      4.- Extraer informacion tributaria de terceros\n\n'
                           'Opcion[1-4]:')

        def opcion1():
            pass

        def opcion2():
            pass

        def opcion3():
            pass

        def opcion4():
            pass

        while True:
            opcion = bienvenida()
            if opcion == 1:
                cls()
                opcion1()
            elif opcion == 2:
                cls()
                opcion2()
            elif opcion == 3:
                cls()
                opcion3()
            elif opcion == 4:
                cls()
                opcion4()
            elif opcion == 'exit':
                exit(0)
            else:
                cls()
                pass


def main(retryIntentions=5):

    fHan = fileHandler()
    Olog = loger()
    wMin = WebMinner()
    fDog = file_dog('./stdout/tmp/')
    ls_nombreRut = fHan.read_file()

    for company in ls_nombreRut:
        error_counter = 0
        Olog.tee_output('[*]    Empresa: %s'%decode64(company[0]).decode('utf-8'))
        wMin.surf_to_Cesiones()
        wMin.login_to_sii(company[1],company[2])
        while True:
            try:
                wMin.get_facturas_cesiondas()
                last_file = fDog.get_newest_file()
                Olog.tee_output('\n[+]    Archivo descargado: %s' % last_file)
                wMin.surf_to_certificados_de_cesiones()
                wMin.get_certificado_facturas_cesionadas()
                break
            except NoSuchElementException:
                error_counter += 1
                wMin.handle_errors()
                sleep(1)
                if error_counter > retryIntentions:
                    raise Exception('Intentos maximos alcanzados: %s'%retryIntentions)

        output_folder = fHan.check_and_make_folders(company[0])
        fHan.files_to_move(output_folder)
        fHan.conver_txt_file(output_folder)

        Olog.log_ls.append('\n[X]    Archivo convertido: %s' % last_file.replace('.txt', '.xlsx'))
        for line in wMin.log_pdf:
            Olog.log_ls.append('\n'+line)
        Olog.drop_log_txt(Olog.log_ls)

    print('Log del proceso guardado en %s'%Olog.log_path)
    wMin.kill_browser()

def main_debug():

    ls_Data = []
    ls_nombreRut = []
    dl_file_name = ''

    Olog = loger()
    wMin = WebMinner()
    fDog = file_dog('./')

    wMin.surf_to_sii()
    wMin.surf_to_Cesiones()
    wMin.login_to_sii()
    while True:
        try:
            wMin.get_facturas_cesiondas()
            break
        except NoSuchElementException:
            wMin.handle_errors()
            sleep(5)

    Olog.tee_output('Menu de Cesiones')
    wMin.kill_browser()
    Olog.drop_output(Olog.log_ls)

def main_obtencion_de_certificados():
    ls_Data = []
    ls_nombreRut = []
    dl_file_name = ''

    Olog = loger()
    wMin = WebMinner()
    fDog = file_dog('./')

    wMin.surf_to_sii()
    wMin.surf_to_certificados_de_cesiones()
    wMin.login_to_sii()

    while True:
        try:
            wMin.get_certificado_facturas_cesionadas()
            break
        except NoSuchElementException:
            wMin.handle_errors()
            sleep(5)

    Olog.tee_output('Menu de Cesiones')
    wMin.kill_browser()
    Olog.drop_output(Olog.log_ls)


def main_captch():
    fHan = fileHandler()
    wMin = WebMinner()
    wMin.surf_to_situacion_tributaria()
    rut_list = fHan.read_ruts()
    contador = 0
    num_file = 1
    for rut in rut_list:
        sleep(randint(0, 2))
        wMin.get_situacion_tributaria(rut, wMin.resolve_captcha())
        wMin.surf_to_situacion_tributaria()
        contador += 1
        if contador >= 100:
            print('%s Dump de 100 provs'%str(num_file))
            with open(os.path.abspath(os.path.dirname(__file__) + '/stdout/ruts - ' +str(num_file) + '.csv'), 'w') as le_file:
                le_file.write('Rut;RazonSocial;InicioActividades;PROPYME\n')
                for line in wMin.sit_trib[-100:]:
                    le_file.write(line[0].replace('\n', '')+';'+line[1]+';'+line[2]+';'+line[3]+'\n')
            num_file += 1
            contador = 0

    with open(os.path.abspath(os.path.dirname(__file__) + '/stdout/Ruts Completos.csv'), 'w') as le_file:
        le_file.write('Rut;RazonSocial;InicioActividades;PROPYME\n')
        for line in wMin.sit_trib:
            le_file.write(line[0].replace('\n', '')+';'+line[1]+';'+line[2]+';'+line[3]+'\n')

    wMin.kill_browser()

def get_help():
    print('\n                               :::: Minero de SII ::::\n\n'
          'Utilidad de mineria de informacion tributaria y contable, para la pagina del Servicio de Impuestos Internos\n\n'
          '  Uso de Opciones:\n'
          '    siibot.py [--opcion (argumentos)]...\n\n'
          '    --log_output          : Una vez activada esta opcion se lee el segundo argumento que debe ser una ruta\n'
          '                            valida y los directorios deben existir. El log se creara con el nombre provisto\n'
          '                            despues del ultimo separador valido, con la extension provista.\n\n'
          '    --modo_de_captura     : Especifica que modo se esta pidiendo ejecutar y corresponde a la sgte. lista:\n'
          '                            1.- Ejecuta automaticamente la revision de si existen facturas cedidas en el\n'
          '                                periodo(dia anterior por default) y de haber, extrae los certificados\n'
          '                                para todas las empresas. Este es el comportamiento default de no\n'
          '                                especificar un comportamiento especifico\n'
          '                            2.- Captura solamente las listas de facturas cedidas.\n'
          '                            3.- En este modo se consulta la informacion tributaria de terceros de forma\n'
          '                                iterativa. Realiza un DUMP de informacion cada 100 proveedores, al finalizar\n'
          '                                compila la lista de archivo para unificarla\n\n'
          '   --retry_intentions     : Especifica la cantidad de intentos fallidos maximos para el robot. En caso de\n'
          '                            que el sitio de Servicio de Impuestos Internos se encuentre con problemas, se\n'
          '                            puede especificar un numero mayor de intentos. Por default es 5.\n\n'
          '   --captura_un_proveedor : En este modo solo captura la informacion de cesiones de un proveedor se debe\n'
          '                            proveer el RUT del proveedor, el RUT de la sociedad y la clave de esta.\n\n'
          '   --Rango_de_Fechas      : Especifica el Rango de Fechas a consultar. Siempre por defecto es el día\n'
          '                            anterior. El formato en que se deben proveer las fechas es el siguiente:\n'
          '                                dd/mm/yyyy-dd/mm/yyyy -> FechaAnterior-FechaPosterior\n'
          '                            Cualquier diferencia con este formato sera rechazada y se usara el día anterior.\n\n'
          '   --ayuda, -h, /?, /h    : Abre este menu de ayuda. Si la opcion esta presente, todas las demas se anulan\n\n'
          '  Utilidad escrita por Matín Francisco Nicolás Pimentel Tarbuskovic\n'
          '  en Santiago de Chile, 2018_06_12. MIT License.')

if __name__ == '__main__':

    ArgParser().interactive()
