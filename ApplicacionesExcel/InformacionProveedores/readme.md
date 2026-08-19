# Generador de Correos desde excel

### Programa

<img width="1228" height="307" alt="dbcontactos" src="https://github.com/user-attachments/assets/6d7733e0-6cff-467b-b851-947df3a56733" />

### Formato

<img width="988" height="414" alt="TRFpagadora" src="https://github.com/user-attachments/assets/3334d4e2-e074-48bd-bc28-849ac60958be" />

### Funcionamiento

Este programa funciona segun la siguiente logica:

- En la planilla de excel se añaden los datos de contacto de las personas a las que se les debe enviar la informacion
- La informacion contenida en la planilla ubicada en "/stdin/" llamada "TRF.xlsx" es el formato modelo en el que se debe añadir la informacion
- La planilla puede ser seleccionada manualmente usando el boton Elegir TRF
- Al presionar el boton "Generar", Excel buscara una instancia abierta de Outlook y procedera a generar correos para los RUTS que esten contenidos en el archivo TRF y que hagan match con la informacion en la base de datos de contactos


