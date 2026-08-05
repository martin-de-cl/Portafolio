@echo off
SetLocal EnableDelayedExpasion
title Menu Completo

::
:: Menu completo para trabajo en batches
::
:: @Autor     : Martin Pimentel
:: @Fecha     : 2021_11_08
:: @Licensia  : BSD
::

:: Aqui obtenemos el path de este batch, asi podemos anidar carpetas
:: en los que almacenar los recursos que necesitamos acceder.
::
:: El objetivo de outerPath es el demostrar que podemos usar recursos
:: de directorios afuera de donde reside este batch.

SET rootPath=%~dp0
SET outerPath=%~dp0..\
SET resPath=%rootPath%\res

:: Chequeo de parametros de linea de comandos simple

IF "%~1"=="-q" goto silent
IF "%~1"=="/?" goto ayuda
IF "%~1"=="-?" goto ayuda
IF "%~1"=="-w" (
        SET logpath="%~2"
        )
IF "%~2"=="-w" (
    IF not "%~3"=="" (
        SET logpath="%~3"
        )
    )
IF "%~1"=="" goto inicio

:: Menu de Seleccion 

:inicio
color 0A
cls
echo *********************************************
echo *************   Menu Completo   *************
echo *********************************************
echo.
echo      1)  Opcion 1   
echo      2)  Opcion 2    
echo      3)  Opcion 3
echo      4)  Opcion 4
echo      5)  Opcion 5
echo      6)  Opcion 6
echo      7)  Opcion 7
echo      8)  Opcion 8
echo      9)  Opcion 9
echo     10)  Todas
echo.
echo     xx) Opcion texto
echo.
echo *********************************************
echo               11) Salir  ?)Ayuda
echo *********************************************
echo.

:: Validacion de opciones

set /p var=Seleccione una opcion:
if "%var%"=="1" goto op1
if "%var%"=="2" goto op2
if "%var%"=="3" goto op3
if "%var%"=="4" goto op4
if "%var%"=="5" goto op5
if "%var%"=="6" goto op6
if "%var%"=="7" goto op7
if "%var%"=="8" goto op8
if "%var%"=="9" goto op9
if "%var%"=="10" goto op10
if "%var%"=="11" goto salir
if "%var%"=="?" goto ayuda
if "%var%"=="xx" goto opcionTexto

:: Mensaje de error
echo. - "%var%" no es una opcion valida, por favor intente de nuevo.
pause
goto inicio

:: Bloque de etiquetas de opciones 

:op1
    cls
    echo.
    echo.
    echo. Ejecutando Opcion 1 
    echo    Hora de inicio - %time%
    echo.
	color 0D
        :: Aqui ejecutar el script que deberia estar en .\res
        :: python .\res\script.py
	:: o usando expasion de variables
	:: python %resPath%
        ::
        color 08
    echo.
    echo    Hora de inicio - %time%
    echo.
    pause
    goto inicio

:op2
    cls
    echo.
    echo.
    echo. Ejecutando Opcion 2
    echo    Hora de inicio - %time%
    echo.
    color 0D
        :: Aqui ejecutar el script que deberia estar en .\res
        :: python .\res\script.py
        ::
        color 08
    echo.
    echo    Hora de inicio - %time%
    echo.
    pause
    goto inicio

:op3
    cls
    echo.
    echo.
    echo. Ejecutando Opcion 3 
    echo    Hora de inicio - %time%
    echo.
    color 0D
        :: Aqui ejecutar el script que deberia estar en .\res
        :: python .\res\script.py
        ::
        color 08
    echo.
    echo    Hora de inicio - %time%
    echo.
    pause
    goto inicio

:op4
    cls
    echo.
    echo.
    echo. Ejecutando Opcion 4 
    echo    Hora de inicio - %time%
    echo.
    color 0D
        :: Aqui ejecutar el script que deberia estar en .\res
        :: python .\res\script.py
        ::
        color 08
    echo.
    echo    Hora de inicio - %time%
    echo.
    pause
    goto inicio

:op5
    cls
    echo.
    echo.
    echo. Ejecutando Opcion 5 
    echo    Hora de inicio - %time%
    echo.
    color 0D
        :: Aqui ejecutar el script que deberia estar en .\res
        :: python .\res\script.py
        ::
        color 08
    echo.
    echo    Hora de inicio - %time%
    echo.
    pause
    goto inicio

:op6
    cls
    echo.
    echo.
    echo. Ejecutando Opcion 6 
    echo    Hora de inicio - %time%
    echo.
    color 0D
        :: Aqui ejecutar el script que deberia estar en .\res
        :: python .\res\script.py
        ::
        color 08
    echo.
    echo    Hora de inicio - %time%
    echo.
    pause
    goto inicio

:op7
    cls
    echo.
    echo.
    echo. Ejecutando Opcion 7
    echo    Hora de inicio - %time%
    echo.
    color 0D
        :: Aqui ejecutar el script que deberia estar en .\res
        :: python .\res\script.py
        ::
        color 08
    echo.
    echo    Hora de inicio - %time%
    echo.
    pause
    goto inicio

:op8
    cls
    echo.
    echo.
    echo. Ejecutando Opcion 8
    echo    Hora de inicio - %time%
    echo.
    color 0D
        :: Aqui ejecutar el script que deberia estar en .\res
        :: python .\res\script.py
        ::
        color 08
    echo.
    echo    Hora de inicio - %time%
    echo.
    pause
    goto inicio

:op9
    cls
    echo.
    echo.
    echo. Ejecutando Opcion 9 
    echo    Hora de inicio - %time%
    echo.
    color 0D
        :: Aqui ejecutar el script que deberia estar en .\res
        :: python .\res\script.py
        ::
    color 08
    echo.
    echo    Hora de inicio - %time%
    echo.
    pause
    goto inicio


:opcionTexto
    cls
    echo.
    echo.
    echo. Ejecutando Opcion Texto 
    echo    Hora de inicio - %time%
    echo.
    color 0D
        :: Aqui ejecutar el script que deberia estar en .\res
        :: python .\res\script.py
        ::
        color 08
    echo.
    echo    Hora de inicio - %time%
    echo.
    pause
    goto inicio

:op10
    cls
    echo.
    echo.
    echo. Ejecutando todos los scripts
    echo. 
    echo    Hora de inicio - %time%
    echo.
    color 0D
        :: Para que no sea tedioso dejar todos los paths aca
        :: podemos usar la siguien funcion si los arhivos son
        :: del mismo tipo
        :: for /f %%f in ('dir /b .\res') do python %%f
    color 08
    echo.
    echo    Hora de inicio - %time%
    echo.
    pause
    goto inicio

:silent
    cls
    (
    echo.
    echo.
    echo. Ejecutando todos los scripts
    echo. 
    echo    Hora de inicio - %time%
    echo.
    color 0D
        :: Para que no sea tedioso dejar todos los paths aca
        :: podemos usar la siguien funcion si los arhivos son
        :: del mismo tipo
        :: for /f %%f in ('dir /b .\res') do python %%f
    color 08
    echo.
    echo    Hora de inicio - %time%
    echo.
    ) > logm.txt 2>&1
    pause
    goto salir
:salir
    @cls&exit

:ayuda
@cls
echo.
echo                            Menu Completo
echo.
echo.
echo  +Utilizacion de opciones:
echo.
echo    menucompleto.bat [OPCION1] [OPCION2 PATH]
echo.
echo.
echo  +Opciones
echo.
echo     -q        Modo silencioso. No recibe inputs y escribe output en: 
echo               ./log_captura_de_saldos.txt
echo     -w PATH   Especifica donde se quiere guarda el log
echo     -?, /?    Ayuda y manual de esta intefaz
echo.
echo.
echo.
echo  +Si no hay opciones explicitas, el menu entra en modo manual
echo    el output es escrito en logm.txt, en la misma carpeta.
echo.
echo  +Para configurar la utilizacion programada, debe usarse la opcion -q
echo   de esta manera no se necesita la interaccion de un usuario.
echo.
echo.
echo    Para interrumpir el proceso, utilizar Ctrl+C
echo.
echo.
echo.
pause
:EOF

:: --- EOF ---
