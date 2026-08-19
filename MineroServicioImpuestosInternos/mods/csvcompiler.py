import os

ruta = './Tamaño de empresa'
ruta_csv = './Ruts Compilados.csv'

for directorio in os.listdir(os.path.abspath(ruta)):
    #print(directorio)
    if os.path.isdir(os.path.abspath(ruta + '/' + directorio)):
        print(directorio)
        with open(os.path.abspath(ruta_csv), 'a') as compilacion:
            for file in os.listdir(os.path.abspath(ruta + '/' + directorio)):
                with open(os.path.abspath(os.path.abspath(ruta + '/' + directorio) + '/' + file), 'r') as csv_incompleto:
                    for line in csv_incompleto:
                        compilacion.write(line)
