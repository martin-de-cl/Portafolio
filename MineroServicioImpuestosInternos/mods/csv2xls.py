#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import os
import csv
import openpyxl

from locale import *

setlocale(LC_NUMERIC,'')


def csv2xl(file_path):
    wb = openpyxl.Workbook()
    ws = wb.active

    f_path, f_ext = file_path.rsplit('.', maxsplit=1)
    f = open(os.path.abspath(f_path + '.' + f_ext))

    reader = csv.reader(f, delimiter=';')
    row_index = 1
    for row in reader:
        if row_index > 1:
            try:
                row[3] = atof(row[3])
            except:
                if row[3] is None:
                    row[3] = 0
                elif '.' in row[3]:
                    row[3].replace('.','')
        ws.append(row)
        row_index += 1

    f.close()
    wb.save(os.path.abspath(f_path + '.xlsx'))

