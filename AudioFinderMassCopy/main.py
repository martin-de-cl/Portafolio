#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
                        AudioFileLocator

    Programa para localizar y mover archivos de forma masiva, basado
    en un archivo de texto plano relacional del siguiente formato:

            codigo_0000_aaaa Transcripcion del audio 1
            ...
            codigo_9999_zzzz Transcripcion del audio N

    Una vez localizados todos los codigos para una determinada frase
    se puede realizar una copia masiva de los archivos  repartidos en
    diferents directorios a uno solo centralizado. Efectivamente
    agrupando todos los recursos de un solo tipo para su uso.

            -Directorio Padre
            |- basedatos.txt
            |- Directorio Hijo 1
                               |- Audio 1.mp3
                               |- ...
                               |- Audio N.mp3
            |- ...
            |- Directorio Hijo N
                               |- Audio 1.mp3
                               |- ...
                               |- Audio N.mp3


@BY         : Martin Pimentel Tarbuskovic
@REQUEST-BY : Santi Nam
@Licencia   : MIT 
@Fecha      : 2026_07_30

"""
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, END, font as tkFont
from os.path import abspath, isdir, isfile, join as pjoin
from os import listdir


class GraphicalUserInterface(tk.Tk):

    def __init__(self, h_res:str='802', v_res:str='602', resizeable:bool=False):

        super().__init__()

        self.INTRUCCIONES_TEXTO = '                                       Instrucciones\n' \
                                  ' ----------------------------------------------------------------------------------------------\n' \
                                  '\n' \
                                  '  1.- Elejir el archivo con la base de datos para iniciar cualquier tipo de operacion.\n' \
                                  '\n' \
                                  '  2.- Escribir una palabra, frase o texto, para encontrar coincidencias. Mientras mas\n' \
                                  '      especifico sea el texto, menos coincidencias encontraras.\n' \
                                  '      ADVERTENCIA: Si no se provee un termino de busqueda mostrara todo en la Base de\n' \
                                  '                  Datos.\n' \
                                  '\n' \
                                  '  3.- Una vez satisfecha con los resultados, elejir la carpeta a donde copiar los\n' \
                                  '      archivos de Audio y usar boton "Copiar".\n' \
                                  '      ADVERTENCIA: Se copiaran todos los archivos que aparezcan en esta pantalla, los\n' \
                                  '                   archivos originales de base de datos y audio no se modificaran de\n' \
                                  '                   manera alguna.\n' \
                                  '                   Evita copiar todos los archivos por error!\n' \
                                  '\n' \
                                  '  4.- BONUS: Es posible crear un archivo txt con todas las frases unicas que se\n' \
                                  '             encuentran en la base de datos. Asi facilitando la lectura del archivo\n' \
                                  '             A.- Seleccionar carpeta donde crear el archivo\n' \
                                  '             B.- Usar el boton "Crear", el archivo tendra nombre "Frases_unicas.txt\n'

        self.RESIZEABLE = resizeable
        self.h_res, self.v_res = h_res, v_res

        self.columnconfigure(0, weight=2)

        self.lbl_1 = 'Pick DB'

        self.LABEL_FONT=self._get_font_style(size=10, weight=True)
        self.ENTRYBOX_FONT=self._get_font_style(size=10)

        self.PATH_TO_CODES_DATABASE = tk.StringVar()
        self.PATH_TO_CODES_DATABASE.set('Selecciona tu base de datos')

        self.SEARCH_TEXT_BOX = tk.StringVar()

        self.RESULTS_TEXT_BOX = tk.StringVar()

        self.LAST_SEARCH = ''
        self.SEARCH_RESULTS_DICTIONARY = {}

        self.STDOUT_DIRECTORY_LOCATION = tk.StringVar()
        self.STDOUT_DIRECTORY_LOCATION.set('Selecciona una carpeta a donde mover los audios')

        self.STDOUT_UNIQUES_PHRASES = tk.StringVar()
        self.STDOUT_UNIQUES_PHRASES.set('Selecciona una carpeta donde guardar frases unicas con el nombre "Frases_unicas.txt"')

    def _get_font_style(self,
                        family:str='Consolas', size:int=16,
                        weight:bool=False, slant:bool=False,
                        underline:bool=False, overstrike:bool=False)->tkFont:
        if weight:
            _weight = 'bold'
        else:
            _weight = 'normal'
        if slant:
            _slant = 'italic'
        else:
            _slant = 'roman'

        return tkFont.Font(family=family, size=size, weight=_weight, slant=_slant, underline=underline, overstrike=overstrike)

    def _find_unique_phrases(self):
        db_file = self.PATH_TO_CODES_DATABASE.get()

        tmp_list_dup = []
        tmp_element = ''
        tmp_list_of_uniques = []

        with open(db_file, 'r', encoding='utf-8') as file:
            lines = file.read()
            for line in lines.split('\n'):
                tmp_list_dup.append(line.split(' ', maxsplit=1)[1])

        tmp_list_dup.sort()

        for element in tmp_list_dup:
            if element != tmp_element:
                tmp_list_of_uniques.append(element)
                tmp_element = element

        with open(abspath(self.STDOUT_UNIQUES_PHRASES.get()), 'w') as file:
            for line in tmp_list_of_uniques:
                file.write('{}\n'.format(line))

    def _get_all_child_folders(self):
        aux_dir_list = []
        if isfile(abspath(self.PATH_TO_CODES_DATABASE.get())):
            root_dir=self.PATH_TO_CODES_DATABASE.get().rsplit('/', maxsplit=1)[0]
            dirs = listdir(abspath(root_dir))
            for dir in dirs:
                if isdir(pjoin(abspath(root_dir), dir)):
                    #excluyo el archivo para guardar los audios, si se encuentra en el directorio de la DB
                    if pjoin(abspath(root_dir), dir) != abspath(self.STDOUT_DIRECTORY_LOCATION.get()):
                        aux_dir_list.append(pjoin(abspath(root_dir), dir))

        return aux_dir_list

    def _get_all_files_recursevely(self, extension:str='wav'):
        #TODO: Ajustar la extension del archivo
        aux_files = []
        directories = self._get_all_child_folders()
        for dir in directories:
            for code in self.SEARCH_RESULTS_DICTIONARY:
                if isfile(abspath(pjoin(dir, '{}.{}'.format(code, extension)))):
                    aux_files.append(abspath(pjoin(dir, '{}.{}'.format(code, extension))))
        return aux_files

    def _copy_all_flagged_files(self):
        aux_files = self._get_all_files_recursevely()
        for file in aux_files:
            shutil.copy(file, abspath(pjoin(self.STDOUT_DIRECTORY_LOCATION.get(), file.rsplit('\\',maxsplit=1)[1])))

    def _format_text_for_box(self, dictionary:{})->str:
        separator = '----------------------------   ---------------------------------------------------------------'
        tmp_str='{:30} {}\n{}\n'.format('Nombre del Archivo', 'Texto Buscado',separator)
        for key in dictionary:
            tmp_str = '{}{:30} {}\n'.format(tmp_str, key, dictionary[key])
        return tmp_str

    def _get_db_file(self)->None:
        db_path = filedialog.askopenfilename()
        if len(db_path) != 0:
            self.PATH_TO_CODES_DATABASE.set(db_path)

    def _get_stdout_folder(self)->None:
        path = filedialog.askdirectory()
        if len(path) !=0:
            self.STDOUT_DIRECTORY_LOCATION.set(path)

    def _get_uniques_phrases_location(self)->None:
        path = filedialog.askdirectory()
        if len(path) !=0:
            self.STDOUT_UNIQUES_PHRASES.set('{}/{}'.format(path, 'Frases_unicas.txt'))

    def _search_db_for_text(self)->None:
        text = self.SEARCH_TEXT_BOX.get()
        db_file = self.PATH_TO_CODES_DATABASE.get()

        if self.LAST_SEARCH != '':
            self.SEARCH_RESULTS_DICTIONARY={}
            self.LAST_SEARCH =text

        with open(db_file, 'r', encoding='utf-8') as file:
            lines = file.read()
            for line in lines.split('\n'):
                if text in line.split(' ', maxsplit=1)[1]:
                    self.SEARCH_RESULTS_DICTIONARY[line.split(' ', maxsplit=1)[0]] = line.split(' ', maxsplit=1)[1]

        self.LAST_SEARCH = text
        texto = self._format_text_for_box(self.SEARCH_RESULTS_DICTIONARY)
        self.set_text_to_box(texto)

    def set_text_to_box(self, text)->None:

        locacion = ['!frame', '!frame3', '!text']
        tmp_obj=self
        for item in locacion:
            tmp_obj = tmp_obj.children[str(item)]
        tmp_obj.delete('1.0', END)
        tmp_obj.insert(END, '{}'.format(text, '\r'))

    def __mk_mlinetextbox(self, tabframe, textvar=None, text='', height=20, width=40, wrap='none', bg='white',
                          fg='black', column=0, columnspan=1, row=0, rowspan=1, ipadx=0, ipady=0, sticky=tk.N,
                         custom_font=None)->None:

        mtextbox = tk.Text(tabframe, height=height, width=width, wrap=wrap, bg=bg, fg=fg, font=custom_font)

        ys = ttk.Scrollbar(tabframe, orient='vertical', command=mtextbox.yview)
        xs = ttk.Scrollbar(tabframe, orient='horizontal', command=mtextbox.xview)
        ys.columnconfigure(0, weight=1)
        xs.rowconfigure(0, weight=1)

        mtextbox['yscrollcommand'] = ys.set
        mtextbox['xscrollcommand'] = xs.set
        mtextbox.insert('end', text)

        mtextbox.grid(column=column, columnspan=columnspan, row=row, rowspan=rowspan, ipadx=ipadx, ipady=ipady,
                      sticky=sticky)
        ys.grid(sticky='nsw', column=column + 1, row=row)
        xs.grid(sticky='wes', column=column, row=row + 1)

    def __mk_frm(self, parent_frame, column=0, row=0, padding=4, sticky='nswe', relief='sunken',
                 height=None, width=None, col_weight=1, row_weight=1,
                 propagate=True, resizable_column=True, resizable_row=True) -> tk.Tk.frame:

        frame = ttk.Frame(parent_frame, width=width, height=height, relief=relief, padding=padding)

        if resizable_column is False:
            frame.columnconfigure(column, weight=col_weight)
        if resizable_row is False:
            frame.rowconfigure(row, weight=row_weight)
        if propagate is False:
            frame.grid_propagate(False)

        frame.grid(column=column, row=row, sticky=sticky)
        return frame

    def __mk_lbl(self, parent_frame, text, column=0, row=0)->ttk.Label:
        lbl = ttk.Label(parent_frame, text=text, font=self.LABEL_FONT)
        lbl.grid(column=column, row=row)
        return lbl

    def __mk_etr(self, parent_frame, column=0, row=0, textvar='', sticky='we')->ttk.Entry:
        entry = ttk.Entry(parent_frame, textvariable=textvar, font=self.ENTRYBOX_FONT)
        entry.grid(column=column, row=row, sticky=sticky)

        return entry

    def __mk_btn(self, parent_frame:ttk.Frame, text:str='TextHolder',
                 column:int=0, row:int=0, command=None, state='enabled', image=None)-> ttk.Button:

        image_path = image
        if image_path is None:
            btn = ttk.Button(parent_frame, text=text, state=state,command=command)
        # else:
        #     imagen = ImageTk.PhotoImage(Image.open(image_path).resize((20,20), Image.ANTIALIAS))
        #     btn = ttk.Button(parent_frame, image=imagen, state=state, command=command)
        #     btn.imagen = imagen #Referencia para las imagenes en general de tkinter
        btn.grid(column=column, row=row)
        return btn

    def _create_gui(self)->None:
        main_window = self.__mk_frm(self, column=0, row=0)
        main_window.rowconfigure(0, weight=1)
        main_window.columnconfigure(0, weight=1)

        file_frame = self.__mk_frm(main_window, column=0, row=0)
        file_frame.rowconfigure(0, weight=1)
        file_frame.columnconfigure(1, weight=1)
        label = self.__mk_lbl(file_frame, column=0, row=0, text='Pick DB          ')
        db_location = self.__mk_etr(file_frame, column=1, row=0, textvar=self.PATH_TO_CODES_DATABASE)
        picker_button = self.__mk_btn(file_frame, column=2, row=0, text='Select File', command=self._get_db_file)

        text_search_frame = self.__mk_frm(main_window, row=1, column=0)
        text_search_frame.columnconfigure(0, weight=0)
        text_search_frame.columnconfigure(1, weight=3)
        text_search_frame.columnconfigure(2, weight=0)
        label_2 = self.__mk_lbl(text_search_frame, row=0, column=0, text='Ingresa tu texto ')
        search_box = self.__mk_etr(text_search_frame, row=0, column=1, textvar=self.SEARCH_TEXT_BOX)
        search_button = self.__mk_btn(text_search_frame, row=0, column=2, text='Search', command=self._search_db_for_text)

        search_results_frame = self.__mk_frm(main_window, row=2, column=0)
        box_1 = self.__mk_mlinetextbox(search_results_frame, row=0, column=0, bg='black', fg='magenta', sticky='we',
                                       width=96, height=24, text=self.INTRUCCIONES_TEXTO)

        file_operation_frame = self.__mk_frm(main_window, row=3, column=0)
        file_operation_frame.columnconfigure(0, weight=0)
        file_operation_frame.columnconfigure(1, weight=3)
        file_operation_frame.columnconfigure(2, weight=0)
        std_out_label = self.__mk_lbl(file_operation_frame, row=0, column=0, text='Guardar Audios ')
        std_out_location=self.__mk_etr(file_operation_frame, row=0, column=1, textvar=self.STDOUT_DIRECTORY_LOCATION)
        std_out_picker_button = self.__mk_btn(file_operation_frame, row=0, column=2, text='Select Folder', command=self._get_stdout_folder)
        std_out_picker_button_test = self.__mk_btn(file_operation_frame, row=1, column=2, text='Copiar', command=self._copy_all_flagged_files)

        uniques_creation_frame = self.__mk_frm(main_window, row=4, column=0)
        uniques_creation_frame.columnconfigure(0, weight=0)
        uniques_creation_frame.columnconfigure(1, weight=3)
        uniques_creation_frame.columnconfigure(2, weight=0)
        uniques_creation_label = self.__mk_lbl(uniques_creation_frame, row=0, column=0, text='Guardar Frases ')
        uniques_creation_location = self.__mk_etr(uniques_creation_frame, row=0, column=1, textvar=self.STDOUT_UNIQUES_PHRASES)
        uniques_creation_button = self.__mk_btn(uniques_creation_frame, row=0, column=2, text='Select Folder', command=self._get_uniques_phrases_location)
        uniques_creation_button_test = self.__mk_btn(uniques_creation_frame, row=1, column=2, text='Crear', command=self._find_unique_phrases)

    def main(self)->None:

        self.title('Buscador de Audio')
        self.geometry('{}x{}'.format(self.h_res, self.v_res))
        self.resizable(width=self.RESIZEABLE, height=self.RESIZEABLE)

        self._create_gui()
        self.mainloop()

if __name__ == '__main__':

    gui = GraphicalUserInterface()
    gui.main()
