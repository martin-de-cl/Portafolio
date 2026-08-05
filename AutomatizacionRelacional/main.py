#!/usr/bin/env/python3
# -*- coding: utf-8 -*-

"""
        SW Automation

    Automation project for BHP
    
    Este proyecto es una automatizacion para la integracion de datos en un sitio web interno.
    Alcances:
        + Tiempo de desarrollo a finalizacion de actividad en produccion de 15 dias
        + Limitar el proceso a trabajo por batches
        + Integracion de archivos xls, xlsx o csv
        + Base de datos SQLite para seguimiento del proceso y captura de informacion
        + Reporteria para analisis post integracion
        + Generacion de LOG en tiempo real del proceso

    @BY     : MARTIN PIMENTEL TARBUSKOVIC
    @DATE   : 2026_02_26
    @LICENSE: MIT

"""

import sqlite3
import time
import random
import base64
import pickle

from os import system

from selenium import webdriver as wb
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, WebDriverException, TimeoutException
from selenium.webdriver.support.color import Color

from os.path import abspath, join as pjoin, exists

from json import dumps as json_dumps
from time import sleep
from datetime import datetime as dt

from selenium.webdriver.remote import webelement

from mods.new_print import NewPrint
from mods.file_handler import FileHandler
from mods.dbEngine import DBEngine
from fake_useragent import UserAgent


class NVBrowser(NewPrint):

    def __init__(self, sw_list_object:[]=None):
        super().__init__()
        self.FIREFOX_BINARY = abspath("/Applications/Firefox.app/Contents/MacOS/firefox")
        self.GECKO_DRIVER = abspath("./res/geckodriver")
        self.COOKIES = abspath('./res/cookies.pkl')
        self.profile = '/Users/TESTMACHINE/Library/Application Support/Firefox/Profiles/7f3qz1wu.SuperProfile'
        self.PROFILE_test = abspath('./res/7f3qz1wu.SuperProfile')
        self.PATH_TO_DB = abspath('./res/project_2026.db')
        self.PATH_TO_LOG = abspath('./etc/new_print.log')
        self.PATH_TO_CONSUMIBLES = abspath('./stdin')
        self.WEBSITE = 'https://INTERNALSITE-PROD.DNS.com/sw/builder/'
        self.RUNTIME_TIMESTAMP = self._get_runtime_timestamp()
        self.SESSION_ID = self._get_session_id()
        self.driver = self._get_driver()
        self.DBE = DBEngine(path_to_consumible=self.PATH_TO_CONSUMIBLES, path_to_db=self.PATH_TO_DB,
                            path_to_log=self.PATH_TO_LOG, session_id=self.SESSION_ID)
        self.DBE.create_session_record(time_stamp=self.RUNTIME_TIMESTAMP, session_id=self.SESSION_ID)

    def _get_driver(self, FFOptions=None, headless:bool=False):

        agent = " Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)"
        agent2  = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0"

        gen_fake_agent = UserAgent()
        fake_agent = gen_fake_agent.random

        options = FirefoxOptions()
        options.headless = headless
        options.add_argument("-profile")
        options.add_argument(self.PROFILE_test)
        options.set_preference("general.useragent.override", agent2)

        service = Service(self.GECKO_DRIVER)
        options.binary_location = self.FIREFOX_BINARY

        return wb.Firefox(options=options, service=service)

    def _get_session_id(self)->str:
        return str(dt.now().timestamp())

    def _get_runtime_timestamp(self):
        return dt.now().strftime("%Y_%m_%d_%H_%M_%S")

    def _check_if_sign_in_needed(self)->bool:
        return True

    def _load_cookies(self):

        if exists(self.COOKIES):
            self.print_and_log('!', process='WDB', message='Loading cookies')
            cookies = pickle.load(open(self.COOKIES, "rb"))
            tmp = pickle.load(open(self.COOKIES, 'rb'))
            for cookie in tmp:
                self.driver.add_cookie(cookie)

    def _dump_cookies(self):

        self.print_and_log('!', process='WDB', message='Dumping cookies')

        pickle.dump(self.driver.get_cookies(), open(self.COOKIES, 'wb'))

    def _open_site(self, website:str='https://internalsite-TESTINGS.dns.com/'):
        self.driver.get(website)
        self.driver.maximize_window()

    def _nav_to_login_and_sign_in(self, wait_time:int=120):

        usr, psw = self._get_credentials("user"), self._get_credentials("pass")

        self._wait_for_element("//input[@placeholder='BHP Email']")
        self._slow_typing(self.driver.find_element(By.XPATH, "//input[@placeholder='BHP Email']"), usr)
        self.driver.find_element(By.XPATH, "//input[@placeholder='BHP Email']").send_keys(Keys.RETURN)

        self._wait_for_element("//input[@placeholder='Contraseña']")
        self._slow_typing(self.driver.find_element(By.XPATH, "//input[@placeholder='Contraseña']"), psw)

        self.driver.find_element(By.XPATH, "//input[@placeholder='Contraseña']").send_keys(Keys.RETURN)
        time.sleep(wait_time)

    def _store_user_profile(self, path:str=''):
        try:
            path_ = self.driver.firefox_profile.path
            print(path_)
        except:
            print('firefox profile storage fail')

        tmp_profile = self.driver.capabilities['moz:profile']
        print(tmp_profile)
        profileStoragePath = path
        system('cp -R ' + tmp_profile + '/* ' + profileStoragePath)

    def _nav_to_spence_main_frame(self):

        try:
            self.driver.find_element(By.XPATH, "//*[@id='react-component']/div/header/div/div[2]/button")
            tier1 = self.driver.find_element(By.XPATH, "//button[@type='button']").click()
            tier2 = tier1.find_element(By.XPATH, "//div[text()='BHP']").click()
            tier3 = tier2.find_element(By.XPATH, "//div[text()='Minerals Americas']").click()
            tier4 = tier3.find_element(By.XPATH, "//div[text()='Pampa Norte']").click()
            tier4 = tier4.find_element(By.XPATH, "//div[text()='spence']").click()
        except NoSuchElementException:
            pass

    def _extract_confirm_table(self)->str:
        table_info = {}
        self._wait_for_element('//table[@class="MuiTable-root css-kdkbt4"]')
        table = self.driver.find_element(By.XPATH,'//tbody[@Class="MuiTableBody-root css-1xnox0e"]')
        rows = table.find_elements(By.XPATH, './/tr[contains(@data-testid, "metadata-row")]')
        for item in rows:
            field = item.find_element(By.XPATH,'.//td[contains(@data-testid, "metadata-name")]').text
            value = item.find_element(By.XPATH,'.//td[contains(@data-testid, "metadata-value")]').text
            table_info[field] = value
        self.print_and_log('+', process='WDB', message='Extraccion de la tabla de confirmacion exitosa')
        return json_dumps(table_info)

    def _extract_revision_table(self)->str:
        table_info = {}
        self._wait_for_element('//div[@class="MuiGrid-root MuiGrid-container css-1d3bbye"]')
        table = self.driver.find_element(By.XPATH, '//div[@class="MuiGrid-root MuiGrid-container css-1d3bbye"]')
        rows = table.find_elements(By.XPATH,'.//div[@class="MuiGrid-root MuiGrid-container MuiGrid-item css-1ul47bz"]')
        for item in rows:
            field = item.find_element(By.XPATH,'.//div[@class="MuiGrid-root MuiGrid-item MuiGrid-grid-xs-3 css-4xkoi8"]').text
            value = item.find_element(By.XPATH,'.//div[@class="MuiGrid-root MuiGrid-item MuiGrid-grid-xs-8 css-45ujxc"]').text
            table_info[field] = value
        self.print_and_log('+', process='WDB', message='Extraccion de la tabla de validacion exitosa')
        return json_dumps(table_info)

    def _extract_full_info_table(self, actividad:str=''):
        table_info = {}
        table_selector = '//div[@class="activity-info"]/div[@class="flex-row"]'
        rows = self.driver.find_element(By.XPATH, table_selector).find_elements(By.XPATH, './/div[starts-with(@class, "flex-column")]')
        for row in rows:
            header = row.find_element(By.XPATH, './h4[@class="header"]').text
            content = row.find_elements(By.XPATH, './/p')
            content = self._get_long_string(content)
            table_info[header] = content
            table_info[header] = content
        self.print_and_log('+', process='WDB', message='Extraccion de la tabla de Actividad {} EXITOSA'.format(actividad))
        return json_dumps(table_info)

    def _get_long_string(self, lista):
        new_content = ''
        counter = 0
        for item in lista:
            if counter == 0:
                new_content = '{}{}'.format(new_content, item.text)
                counter += 1
            else:
                new_content = '{},{}'.format(new_content, item.text)
        return new_content

    def _nav_to_activities(self, n_order):
        self.driver.find_element(By.XPATH, "//*[@id='react-component']/div/header/div/div[2]/div/div/a[3]").click()

    def _find_filter(self):
        self.driver.find_element(By.XPATH,"//*[@id='react-component']/div/div[1]/div/div[2]/div/div/div[3]/div/div/div[1]/div/div/div/div[2]/div[2]/div/div/div/button/svg").click()

    def _check_if_element_is_present(self, element_xpath, retries:int=5)->bool:
        counter = 0
        while True:
            try:
                self.driver.find_element(By.XPATH, element_xpath)
                sleep(1)
                return True
            except NoSuchElementException:
                sleep(1)
                counter += 1
                if counter == retries:
                    self.print_and_log(icon='!', process='WDB', message='Element is not Present'.format(element_xpath))
                    return False

    def _wait_for_element(self, element, max_wait_time:int=60):
        wait_time = 0
        while True:
            try:
                self.driver.find_element(By.XPATH, element)
                break
            except NoSuchElementException:
                sleep(1)
                wait_time += 1
                if wait_time == max_wait_time:
                    self.print_and_log("!", process='WDB', message="Element Not Found MAX_WAIT_TIME exceeded: {}".format(element))
                    break

    def _get_credentials(self, key:str):
        credentials = {"user": b'dXN1YXJpbw==',
                       "pass": b'cGFzc3dvcmQ='}
        return base64.b64decode(credentials[key]).decode("utf-8")

    def _slow_typing(self, element, word:str, min_time:float=0.098, max_time:float=0.512):
        for char in word:
            element.send_keys(char)
            sleep(round(random.uniform(min_time, max_time),3))

    def _apply_filter(self, element=None, criteria=None):
        self.driver.find_element(By.XPATH,
                                 '/html/body/div/div/div[1]/div/div[2]/div/div/div[3]/div/div/div[1]/div/div/div/div[2]/div[2]/div/div/div/button').click()
        self.driver.find_element(By.XPATH,
                                 '//div[@data-testid="filter-by"]/div/input[starts-with(@id,":r")]').send_keys(criteria)
        self.driver.find_element(By.XPATH, '//button[text()="Aplicar"]').click()

    def _clean_filter(self):
        self.driver.find_element(By.XPATH,
                                 '/html/body/div/div/div[1]/div/div[2]/div/div/div[3]/div/div/div[1]/div/div/div/div[2]/div[2]/div/div/div/button').click()

        hidden_element = self.driver.find_element(By.XPATH, '//div[@class="MuiBackdrop-root MuiBackdrop-invisible MuiModal-backdrop css-esi9ax"]')
        self.driver.execute_script("arguments[0].style.visibility='hidden'", hidden_element)
        hidden_element2 = self.driver.find_element(By.XPATH, '//div[@class="MuiPopover-root MuiMenu-root MuiModal-root css-1sucic7"]')
        self.driver.execute_script("arguments[0].style.visibility='hidden'", hidden_element2)
        self.driver.find_element(By.XPATH, '//button[text()="Limpiar"]').send_keys(Keys.RETURN)
        self.driver.find_element(By.XPATH, '//button[text()="Limpiar"]').click()

    def _case_one(self, lista_de_actividades=None, limit_batch:int=0):

        url_prefix = '{}activity/'.format(self.WEBSITE)
        test_list = self.DBE.get_list_of_unprocessed_activities()

        if limit_batch != 0:
            test_list = test_list[:limit_batch]
        counter = 1
        max_counter = len(test_list)

        for item in test_list:

            self.print_and_log('!', process='WDB', message='Procesando {} de {}'.format(counter, max_counter))
            self.print_and_log('+', process='WDB', message='Buscando Actividad: {}'.format(item[0]))
            self._wait_for_element('//h4[text()="ID"]')
            self._apply_filter(criteria=item[0])

            if self._check_if_element_is_present('//p[text()="Sin resultados"]') is True:
                self.print_and_log('!', process='WDB', message='Actividad no se encuentra creada: {}'.format(item))
                self._wait_for_element('//h4[text()="ID"]')
                self._clean_filter()
                self.driver.back()
            else:

                table = self.driver.find_element(By.XPATH, '//div[@data-testid="data-table-container"]')
                elements = table.find_elements(By.XPATH, '//div[@data-testid="data-row-data"]/div')
                for item2 in elements:
                    print(item2.text)

                print('SIN RESULTADOS {}'.format('{}{}'.format(url_prefix, item[0])))
                self.driver.get('{}{}'.format(url_prefix, item[0]))

                try:
                    tmp_texto = self.driver.find_element(By.XPATH, '//div[@class="alert alert-warning"]/h4').text
                except NoSuchElementException:
                    tmp_texto = 'TIENE DOCUMENTO'
                if 'actividad no tiene un' in tmp_texto:
                    self.print_and_log('!', process='WDB', message='Actividad no tiene numero de Documentum asociado: {} - {}'.format(item[0], item[1]))

                    self._wait_for_element('//a[@href="/sw/builder/59269/edit/"]')
                    activity_table = self._extract_full_info_table()
                    self.driver.find_element(By.XPATH, '//a[@href="/sw/builder/59269/edit/"]').click()
                    self._wait_for_element('//button[@data-testid="add-configuration-button"]')
                    self.driver.find_element(By.XPATH, '//button[@data-testid="add-configuration-button"]').click()
                    self.driver.find_element(By.XPATH, '//input[starts-with(@id,":r")][@name="documentNumber"]').send_keys(item[1])
                    self.driver.find_element(By.XPATH, '//button[text()="Siguiente"]').click()

                    step_two_selector = self._wait_multiple_elements(['//div[text()="Fallo al configurar el número de documento D2"]', '//h2[@data-testid="d2-confirm-configure"]'])
                    if 'Confirme si desea configurar la actividad' in self.driver.find_element(By.XPATH, step_two_selector).text:
                        table_4_export = self._extract_confirm_table()

                        self.driver.find_element(By.XPATH, '//button[text()="Siguiente"]').click()
                        table2_4_export = self._extract_revision_table()
                        self._wait_for_element('//button[text()="Terminar"]')
                        self.driver.find_element(By.XPATH, '//button[text()="Terminar"]').click()
                        self.DBE.update_sw_status(document_number=item[0], status="PROCESSED",
                                                  confirm_table=table_4_export, validate_table=table2_4_export, activity_table=activity_table)
                        self._wait_for_element('//div[@id="notistack-snackbar"]')
                        goalpoast_text = self.driver.find_element(By.XPATH, '//div[@id="notistack-snackbar"]').text
                        msg1 = "Se ha iniciado la generación del PDF para la actividad. Se le notificará una vez la Instrucción PDF de la plantilla actual se publicará a D2."
                        self.driver.get(self.WEBSITE)

                    elif 'Fallo al configurar' in self.driver.find_element(By.XPATH, step_two_selector).text:

                        selector_css = '//div[@class="MuiPaper-root MuiPaper-elevation MuiPaper-rounded MuiPaper-elevation0 MuiAlert-root MuiAlert-colorError MuiAlert-standardError MuiAlert-standard css-eqijgq"]'
                        parent = self.driver.find_element(By.XPATH, selector_css)
                        mensaje_de_fallo = parent.find_element(By.XPATH, './/div[@class="MuiTypography-root MuiTypography-body1 MuiTypography-gutterBottom MuiAlertTitle-root css-wx2r4c"]').text

                        mensaje_1 = parent.find_element(By.XPATH, './/div[@class="MuiAlert-message css-1xsto0d"]/p').text
                        n_activity = parent.find_element(By.XPATH, './/div[@class="MuiAlert-message css-1xsto0d"]/a').get_attribute('href').rsplit('/',1)[1]

                        self.print_and_log('!', process='WDB', message='Numero de Documentum no puede ser asociado {}'.format(item[1]))
                        self.DBE.update_sw_status(document_number=item[0], status="UNPROCESSED", activity_table=activity_table,
                                                  rejection_reason="SW_ALREADY_ASOCIATED", additional_info_1=str('{}\n\n{}'.format(mensaje_1, n_activity)))
                        self.driver.find_element(By.XPATH, '//button[@data-testid="d2-configuration-dialog-close"]').click()
                        self.driver.get(self.WEBSITE)
                else:
                    self.print_and_log('*', process='WDB', message='Documento cuenta con numero de actividad')
                    self.print_and_log('+', process='WDB', message='Capturando Informacion para actividad: {}'.format(item[0]))
                    activity_table = self._extract_full_info_table()
                    self.DBE.update_sw_status(document_number=item[0], status="PROCESSED", rejection_reason='Document Already Processed Successfully',activity_table=activity_table)
                    self.driver.get(self.WEBSITE)
            counter += 1

    def _wait_multiple_elements(self, elements:list, max_tries=20):
        break_counter = 0
        while True:
            element_counter = 0
            for element in elements:
                try:
                    self.driver.find_element(By.XPATH, element)
                    return elements[element_counter]
                except NoSuchElementException:
                    element_counter += 1
                    if break_counter >= max_tries:
                        break
                    sleep(1)
            break_counter += 1

    def _case_two(self, limit_batch:int=0):

        url_prefix = '{}activity/'.format(self.WEBSITE)

        test_list = self.DBE.get_list_of_unprocessed_activities()

        if limit_batch != 0:
            test_list = test_list[:limit_batch]
        self.print_and_log('+', 'WDB', message=test_list)
        counter = 1
        max_counter = len(test_list)

        for item in test_list:
            self.print_and_log('+', 'WDB', message='Procesado actividad {} de {}'.format(counter, max_counter))
            self.print_and_log('+', process='WDB', message='Buscando Actividad: {}'.format(item[0]))
            self.driver.get('{}{}{}'.format(self.WEBSITE,'activity/',item[0]))
            current_url = self.driver.current_url

            if item[0] not in current_url:
                self.print_and_log('!', process='WDB', message='Actividad no se encuentra creada: {}'.format(item[0]))
            else:
                try:
                    tmp_texto = self.driver.find_element(By.XPATH, '//div[@class="alert alert-warning"]/h4').text
                except NoSuchElementException:
                    tmp_texto = 'TIENE DOCUMENTO'

                try:
                    self._wait_for_element('//div[@class="collapse navbar-collapse"]')
                    activity_location = self.driver.find_element(By.XPATH, '//div[@class="collapse navbar-collapse"]').find_element(By.XPATH, './a').text
                except NoSuchElementException:
                    activity_location = 'Not Found'

                if 'actividad no tiene un' in tmp_texto:
                    self.print_and_log('!', process='WDB', message='Actividad no tiene numero de Documentum asociado: {} - {}'.format(item[0],
                                                                                                               item[1]))
                    self._wait_for_element('//a[@href="/sw/builder/{}/edit/"]'.format(item[0]))
                    activity_table = self._extract_full_info_table()
                    self.driver.find_element(By.XPATH, '//a[@href="/sw/builder/{}/edit/"]'.format(item[0])).click()
                    try:
                        self._wait_for_element('//div[@data-testid="data-row-data"]/div[@class="MuiGrid-root MuiGrid-item MuiGrid-zeroMinWidth MuiGrid-grid-xs-4 css-1iwa9py"]/p', max_wait_time=5)
                        sap_number = self.driver.find_element(By.XPATH,'//div[@data-testid="data-row-data"]/div[@class="MuiGrid-root MuiGrid-item MuiGrid-zeroMinWidth MuiGrid-grid-xs-4 css-1iwa9py"]/p').text
                    except NoSuchElementException:
                        sap_number = ''
                    self._expire_document(message=sap_number)
                    if not self._check_if_element_is_present('//button[@data-testid="add-configuration-button"]'):
                        self.print_and_log('!', process='WDB', message='No es posible configurar un numero de Documentum porque no hay acceso')
                        self.DBE.update_sw_status(document_number=item[0], source_file=activity_location, status="UNPROCESSED", rejection_reason='ACCESS_DENIED',additional_info_1=sap_number, activity_table=activity_table)
                    else:
                        self.driver.find_element(By.XPATH, '//button[@data-testid="add-configuration-button"]').click()
                        self.driver.find_element(By.XPATH,
                                                 '//input[starts-with(@id,":r")][@name="documentNumber"]').send_keys(
                            item[1])
                        self.driver.find_element(By.XPATH, '//button[text()="Siguiente"]').click()
                        step_two_selector = self._wait_multiple_elements(
                            ['//div[text()="Fallo al configurar el número de documento D2"]',
                             '//h2[@data-testid="d2-confirm-configure"]'])
                        if 'Confirme si desea configurar la actividad' in self.driver.find_element(By.XPATH,
                                                                                                   step_two_selector).text:
                            table_4_export = self._extract_confirm_table()
                            self.driver.find_element(By.XPATH, '//button[text()="Siguiente"]').click()
                            table2_4_export = self._extract_revision_table()
                            self._wait_for_element('//button[text()="Terminar"]')
                            sleep(1)
                            self.driver.find_element(By.XPATH, '//button[text()="Terminar"]').click()

                            self.DBE.update_sw_status(document_number=item[0], source_file=activity_location, status="PROCESSED",
                                                      confirm_table=table_4_export, validate_table=table2_4_export,
                                                      activity_table=activity_table, additional_info_1=sap_number)
                            self._wait_for_element('//div[@id="notistack-snackbar"]')
                            try:
                                goalpoast_text = self.driver.find_element(By.XPATH, '//div[@id="notistack-snackbar"]').text
                                goalpoast_color = self._get_element_color('//div[@aria-describedby="notistack-snackbar"]')
                            except NoSuchElementException, StaleElementReferenceException:
                                goalpoast_text = ''
                                goalpoast_color =''
                            if 'ff9800' in goalpoast_color:
                                self.DBE.emergency_update(item[0], goalpoast_text)
                            self._wait_for_element('//p[text()="{}"]'.format(item[1]))
                            sleep(1)
                            self.print_and_log('+', process='WDB', message='Se ha asociado exitosamente el numero de Documentum')
                            msg1 = "Se ha iniciado la generación del PDF para la actividad. Se le notificará una vez la Instrucción PDF de la plantilla actual se publicará a D2."
                            self.driver.get(self.WEBSITE)

                        elif 'Fallo al configurar' in self.driver.find_element(By.XPATH, step_two_selector).text:

                            selector_css = '//div[@class="MuiPaper-root MuiPaper-elevation MuiPaper-rounded MuiPaper-elevation0 MuiAlert-root MuiAlert-colorError MuiAlert-standardError MuiAlert-standard css-eqijgq"]'
                            parent = self.driver.find_element(By.XPATH, selector_css)
                            mensaje_de_fallo = parent.find_element(By.XPATH,
                                                                   './/div[@class="MuiTypography-root MuiTypography-body1 MuiTypography-gutterBottom MuiAlertTitle-root css-wx2r4c"]').text

                            mensaje_1 = parent.find_element(By.XPATH,
                                                            './/div[@class="MuiAlert-message css-1xsto0d"]/p').text
                            try:
                                n_activity = parent.find_element(By.XPATH, './/div[@class="MuiAlert-message css-1xsto0d"]/a').get_attribute('href').rsplit('/', 1)[1]
                            except NoSuchElementException:
                                try:
                                    n_activity = parent.find_element(By.XPATH, '//div[@class="MuiPaper-root MuiPaper-elevation MuiPaper-rounded MuiPaper-elevation0 MuiAlert-root MuiAlert-colorError MuiAlert-standardError MuiAlert-standard css-eqijgq"]').find_element(By.XPATH, './/p[@class="MuiTypography-root MuiTypography-body1 css-1391aac"]').text.replace("'","")
                                except NoSuchElementException:
                                    n_activity = 'Error unknown'
                            self.print_and_log('!', process='WDB', message='Numero de Documentum no puede ser asociado {}'.format(item[1]))
                            self.DBE.update_sw_status(document_number=item[0], source_file=activity_location, status="UNPROCESSED",
                                                      activity_table=activity_table,
                                                      rejection_reason="SW_ALREADY_ASOCIATED",
                                                      additional_info_1=str('{}\n\n{}'.format(mensaje_1.replace("'",""), n_activity)))
                            self.driver.find_element(By.XPATH,
                                                     '//button[@data-testid="d2-configuration-dialog-close"]').click()
                            self.driver.get(self.WEBSITE)
                else:
                    self.print_and_log('*', process='WDB', message='Documento cuenta con numero de actividad')
                    self.print_and_log('+', process='WDB', message='Capturando Informacion para actividad: {}'.format(item[0]))
                    activity_table = self._extract_full_info_table()
                    self.DBE.update_sw_status(document_number=item[0], source_file=activity_location, status="PROCESSED",
                                              rejection_reason='Document Already Processed Successfully',
                                              activity_table=activity_table)
                    self.driver.get(self.WEBSITE)

            counter += 1

        self.driver.quit()

    def _wait_and_click(self, element:str, retry_attempts:int=30, retry_interval:int=0.2):
        attempts_counter = 0
        while attempts_counter < retry_attempts:
            try:
                self.driver.find_element(By.XPATH, element).click()
                break
            except:
                sleep(retry_interval)
                attempts_counter += 1

    def _expire_document(self,message:str=''):

        if self._check_if_element_is_present('//button[@data-testid="expire-document-button"]'):
            self.print_and_log('!', process='WDB', message='Se procede a desvincular el documento SAP {}'.format(message))
            self._wait_and_click(element='//button[@data-testid="expire-document-button"]')
            self._wait_and_click(element='//button[@data-testid="delete-yes"]')

        if self._check_if_element_is_present('//div[@aria-describedby="notistack-snackbar"]'):
            goalpost_color = self._get_element_color('//div[@aria-describedby="notistack-snackbar"]')
            goalpost_msg = self.driver.find_element(By.XPATH, '//div[@id="notistack-snackbar"]').text

            if '43a047' in goalpost_color.lower():
                # Usar lo columna checked o hacer una nueva
                self.print_and_log('*', process='WDB', message='Se ha desvinculado el numero legacy de SAP con exito')
                self.print_and_log('*', process='WDB', message='Mensaje systema: {:.30}'.format(goalpost_msg))

    def _get_element_color(self, element:str):
        return Color.from_string(self.driver.find_element(By.XPATH, element).value_of_css_property('background-color')).hex

    def _clean_up_process(self):

        self._store_user_profile(path='/Users/TESTMACHINE/SWAutomation/res/u7f3qz1wu.SuperProfile')
        self.driver.quit()

    def _check_if_login_is_necessary(self):
        self._wait_for_element("//input[@placeholder='BHP Email']")
        tmp =self._check_if_element_is_present("//input[@placeholder='BHP Password']")
        print(tmp)

        if self._check_if_element_is_present("//input[@placeholder='BHP Password']"):
            print('LOGIN ELEMENT FOUND')
            return True
        elif self._check_if_element_is_present('//svg[@data-testid="PersonRoundedIcon"]'):
            print('LOGIN ELEMENT NOT FOUND')
            return False


    def test_suite(self):
        self._open_site(self.WEBSITE)
        self._nav_to_login_and_sign_in()
        try:
            self._store_user_profile(path=abspath('./res/7f3qz1wu.SuperProfile/'))
            print('User Profile Saved')
        except:
            print('fallo guardar los dato')
        try:
            self._dump_cookies()
            print('Cookies Saved')
        except:
            print('fallo guardar cookies')
        self.driver.quit()

    def _check_if_we_are_in_spence(self):
        try:
            self._wait_for_element('//button[text()="Spence"]')
            company_txt = self.driver.find_element(By.XPATH, '//button[text()="Spence"]')
            return True
        except:
            print('No estamos en spence')
            return False

    def test_suite3(self):
        self.print_and_log('!', process='WDB', message='----- INICIO DE PROCESO DE INTEGRACION DE DOCUMENTOS -----')
        self._open_site(website=self.WEBSITE)
        self._case_two()
        self.print_and_log('!', process='WDB', message='----- FIN DE PROCESO DE INTEGRACION DE DOCUMENTOS -----')

    def test_suite2(self):
        self._open_site(website=self.WEBSITE)
        if self._check_if_we_are_in_spence():
           print('Do Something')
           self._case_one()
        else:
            print('Do Nothing')

    def main(self):
        self._nav_to_login_and_sign_in()
    def test_db(self):
        self.DBE.start_up_routine()

class ExcelHandler(object):
    def __init__(self):
        pass
    def convert(self):
        pass

if __name__ == '__main__':

    web_process = NVBrowser()
    web_process.test_suite3()
