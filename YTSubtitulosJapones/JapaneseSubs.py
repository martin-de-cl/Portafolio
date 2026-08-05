#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""

	Pequeña herramienta para procesar subtitulos bajados de Youtube
	
	Los subtitulos vienen en un formato de strings largos y dado que en
	el japones no hay espacios, tecnicamente, esto reemplaza espacios
	por saltos de linea.

	Los substitulos los provee esta web
	https://youtubechanneltranscripts.com/

	@autor: Martin Pimetel

"""


from sys import argv, exit as terminate_program
from os.path import abspath, exists as path_exist, join as path_join

ENCODING = 'utf-8'

def _cmd_interface()->list:
	end_flag = False
	file_counter = 1
	lista_archivos = []
	print('[+] Interfaz basica:')
	while end_flag is False:
		lista_archivos.append(input('[-] Archivo {}'.format(file_counter)))
		option_aux = input('[-] Desea agregar otro archivo? [y/n]')
		if option_aux in ['n','N','no','NO','nO','No']: end_flag = True
		elif option_aux in ['y','Y','yes','YES','Yes']: file_counter += 1
		else: terminate_program
	return lista_archivos

def get_arguments() -> list:
	lista_a = []
	if len(argv) <= 1:
		print('[*] Warning: No Filename')
		_cmd_interface()
	else:
		for arg in argv[1:]:
			lista_a.append(arg)
	return lista_a

def main(files:str) -> None:
	for file in files:
		root, file_name = file.rsplit('\\', 1)
		if path_exist(abspath(file)):
			with open(abspath(file), 'r', encoding=ENCODING) as fl:
				lines = fl.readline()
			with open(abspath(path_join(root, file_name.replace('.', '-processed.'))), 'w', encoding=ENCODING) as fl_out:
				fl_out.writelines(lines.replace(' ', '\n'))

if __name__ == '__main__':
	files = get_arguments()
	if len(files) > 0:
		print('[+] Procesando {} archivo(s)'.format(len(files)))
		main(files)
	else:
		print('[+] Process: No file(s) provided, please provide at least one file as argument')
