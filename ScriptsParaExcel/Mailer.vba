Rem Attribute VBA_ModuleType=VBAModule
Option VBASupport 1
'
'      ***  Informacion x Mail ***
'
' Generador de correos a proveedores con informacion de facturas que seran pagadas,
' en una fecha especifica con totales desde una plantilla con detalle de transacciones.
'
' Excel actua como una GUI rudimentaria para generar correos a traves de Outlook.
' Por tanto se debe de agregar una referencia a "Microsoft Outlook xx.x Object Library" al crear el libro, que debe
' soportar Macros(xlsm)
' 
' El libro donde debe ser guardada esta macro contempla una "base de datos" de clientes/proveedores con algunos datos
' parte en A1
'
' +---------------+
' | Titulo        |
' +---------------+---------------+---------------+---------------+
' | ID            | NombreCliente | NombreContact | emails(sep ;) |
' +---------------+---------------+---------------+---------------+
'
' Ejemplo de la planilla que se le debe ingresar con informacion, partiendo en "A1"
'
' +---------------+
' | NombreEmpresa |
' +---------------+
' |               |
' +---------------+---------------+---------------+---------------+---------------+---------------+---------------+
' | ID CLIENTE    | NAME CLIENTE  | ID TRANSAC    | Tipo          | Fecha         | VAL_PENDIENTE | VAL_A_PAGAR   |
' +---------------+---------------+---------------+---------------+---------------+---------------+---------------+
'
'
' Escrito por Martin Pimentel Tarbuskovic, Mayo 2017 - Ultima edicion Abril 2017
' Version 1.1.
'

Sub ejecuta_en_un_boton()

    ' Se asume una estructura con las carpetas que se encuentran abajo, sino fueron creadas manualmente se hara en la ejecucion'

    Dim wm_path As String
    Dim p_stdin As String
    Dim p_etc As String
    Dim p_tmp As String

    wm_path = ThisWorkbook.Path
    p_stdin = wm_path & "\stdin\" : createFolder(p_stdin)
    p_etc = wm_path & "\etc\" : createFolder(p_etc)
    p_tmp = wm_path & "\tmp\" : createFolder(p_tmp)

    Call make_emails(p_stdin, p_tmp, "", "")

End Sub

Sub make_emails(ByRef p_stdin As String, ByRef p_tmp As String, ByVal sheet_name as String, ByVal wb_file_name as String)
    'Libro
    Dim wb_trf As Workbook
    
    'Hojas
    Dim ws_info As Worksheet
    Dim ws_facturas As Worksheet
    
    'Variable
    Dim count_proveedores As Integer
    Dim count_info_para_proveedor As Integer
    
    Dim rut_a_enviar As String
    Dim p_info_tmp As String
    Dim empresa_pagadora As String
    
    Dim sub_total_cxc As Double
    Dim sub_total_cxp As Double
    Dim sub_total_Total As Double
    
    Dim arr_cxc, arr_cxp As Variant
    arr_cxc = Array("cxc", "Cxc", "CxC", "cxC", "cXc", "cXC", "CXc", "CXC")
    arr_cxp = Array("cxp", "Cxp", "CxP", "cxP", "cXp", "cXP", "CXp", "CXP")
    
    
    'Abrir Libros y Asignar
    Set ws_info = ThisWorkbook.Sheets(sheet_name)
    Set wb_trf = Workbooks.Open(p_stdin & wb_file_name)

    'Asignamos la hoja con los detalles explicitamente, en error implicito
    On Error Resume Next
    Set ws_facturas = wb_trf.Sheets("Detalle")
    Set ws_facturas = wb_trf.Sheets(1)
    
    count_proveedores = ws_info.Range("A3").CurrentRegion.Rows.Count          ' talves hay que sumar 1

    For i = 3 To count_proveedores
    
        rut_a_enviar = ws_info.Range("A" & i)
        
        With ws_facturas
            empresa_pagadora = .Range("A1")
            
            If .AutoFilterMode = True Then .AutoFilterMode = False
            
            .Range("A3:G3").AutoFilter Field:=1, Criteria1:=rut_a_enviar, Operator:=xlFilterValues
            
            If .Range("A3:A" & .Range("A3").CurrentRegion.Rows.Count + 2).SpecialCells(xlCellTypeVisible).Count > 1 Then
            
                ' Creamos un objeto que apunta a la instancia de Outlook o crea una

                Dim Outlook As Outlook.Application
                Dim o_correo_a_proveedor As Outlook.MailItem
                
                Set Outlook = CreateObject("Outlook.Application")
                Set o_correo_a_proveedor = Outlook.CreateItem(olMailItem)
                
                p_info_tmp = p_tmp & "img_tmp.png"
                
                'Copiamos la informacion relevante al auxiliar
                
                Dim ws_aux_data
                wb_trf.Worksheets.Add.Name = "aux_data"
                Set ws_aux_data = wb_trf.Sheets("aux_data")
                
                count_info_para_proveedor = .Range("A3").CurrentRegion.Rows.Count + 2
                
                .Range("A3:G" & count_info_para_proveedor).Copy
                ws_aux_data.Range("A1").PasteSpecial Paste:=xlPasteValues
                
                'Sacamos subtotales
                    
                    'subtotal CxC
                    .Range("A3:G3").AutoFilter Field:=4, Criteria1:=arr_cxc, Operator:=xlFilterValues
                    On Error Resume Next
                    If .Range("G3:G" & count_info_para_proveedor).SpecialCells(xlCellTypeVisible) > 1 Then
                        sub_total_cxc = Application.WorksheetFunction.Sum(.Range("G3:G" & count_info_para_proveedor).SpecialCells(xlCellTypeVisible))
                    Else
                        sub_total_cxc = 0
                    End If
                    'subtotal CxP
                    .Range("A3:G3").AutoFilter Field:=4, Criteria1:=arr_cxp, Operator:=xlFilterValues
                    sub_total_cxp = Application.WorksheetFunction.Sum(.Range("G3:G" & count_info_para_proveedor).SpecialCells(xlCellTypeVisible))
                    'Subtotal Total 'revisar aca el signo
                    sub_total_Total = sub_total_cxp - sub_total_cxc
                
                '[Formateamos la informacion auxiliar]
                
                ws_aux_data.Columns("E:F").EntireColumn.Delete shift:=xlShiftToLeft
                ws_aux_data.Columns("A:B").EntireColumn.Delete shift:=xlShiftToLeft
        
                ws_aux_data.Range("A1") = "ID Factura"
                ws_aux_data.Range("B1") = "Tipo"
                
                ws_aux_data.Range("A1:C1").Interior.ColorIndex = 25
                ws_aux_data.Range("A1:C1").Font.ColorIndex = 2
                
                ws_aux_data.Range("C2:C" & count_info_para_proveedor).NumberFormat = "0,0"
                
                ws_aux_data.Range("A1:C" & ws_aux_data.Range("A1").CurrentRegion.Rows.Count).RowHeight = 20
                ws_aux_data.Range("A1:C" & ws_aux_data.Range("A1").CurrentRegion.Rows.Count).EntireColumn.AutoFit
                
                If ws_aux_data.AutoFilterMode = True Then ws_aux_data.AutoFilterMode = False
                If ws_aux_data.Range("A1").CurrentRegion.Rows.Count > 2 Then
                    ws_aux_data.Range("A2:C" & ws_aux_data.Range("A1").CurrentRegion.Rows.Count).Sort _
                        key1:=ws_aux_data.Range("A2:A" & ws_aux_data.Range("A1").CurrentRegion.Rows.Count), _
                        key2:=ws_aux_data.Range("B2:B" & ws_aux_data.Range("A1").CurrentRegion.Rows.Count), _
                        order1:=xlAscending, order2:=xlDescending, Header:=xlNo
                End If
                
                Dim alto As Double
                Dim ancho As Double
                
                alto = ws_aux_data.Range("A1:C" & ws_aux_data.Range("A1").CurrentRegion.Rows.Count).Height
                ancho = ws_aux_data.Range("A1:C" & ws_aux_data.Range("A1").CurrentRegion.Rows.Count).Width
                
                '[Hacemos la imagen]
                
                Dim ws_aux As Worksheet
                Dim o_chart As ChartObject
                wb_trf.Worksheets.Add.Name = "aux_chart"
                Set ws_aux_chart = wb_trf.Sheets("aux_chart")

                'Instrucciones sobre el objetoChartObjects.Add(left, top, width, height)
                Set o_chart = ws_aux_chart.ChartObjects.Add(100, 30, 400, 250)
                o_chart.Name = "picture"
                
                ws_aux_data.Range("A1:C" & ws_aux_data.Range("A1").CurrentRegion.Rows.Count).CopyPicture xlScreen, xlBitmap
                
                o_chart.Width = ancho
                o_chart.Height = alto
                
                ws_aux_chart.ChartObjects("picture").Activate
                ActiveChart.Paste
                
                ActiveChart.Export Filename:=p_info_tmp, FilterName:="png"
                
                Application.DisplayAlerts = False
                ws_aux_chart.Delete
                ws_aux_data.Delete
                Application.DisplayAlerts = True
                
                If sub_total_cxc <> 0 Then
                    With o_correo_a_proveedor
                    
                        .To = ws_info.Range("D" & i)
                        .CC = "" 
                        .Subject = "Pago a" & empresa_pagadora & " - " & ws_info.Range("B" & i)
                        
                        ' Literalmente un correo HTML y por tanto se pueden agregar imagenes y tablas
                        '
                        .HTMLBody = "<html>" & _
                                    "<head>" & _
                                    "<meta http-equiv='content-type' content='text/html; charset=ISO-8859-15'>" & _
                                    "</head>" & _
                                    "<body style=font-size:11pt;font-family:Calibri>" & _
                                    "</body>" & _
                                    "</html>"
                        
                        .Attachments.Add p_info_tmp
                        .Display
                    
                    End With
                Else
                'Correo para las liquidaciones
                    With o_correo_a_proveedor
                        .To = ws_info.Range("D" & i)
                        .CC = ""
                        .Subject = "Pago a " & empresa_pagadora & " - " & ws_info.Range("B" & i)
                        
                        .HTMLBody = "<html>" & _
                                    "<head>" & _
                                    "<meta http-equiv='content-type' content='text/html; charset=ISO-8859-15'>" & _
                                    "</head>" & _
                                    "<body style=font-size:11pt;font-family:Calibri>" & _
                                    "</body>" & _
                                    "</html>"
                        .Attachments.Add p_info_tmp
                        .Display
                    End With
                End If
            End If
        End With
    Next i
    
    Application.DisplayAlerts = False
    wb_trf.Close False
    Application.DisplayAlerts = True

End Sub

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
'
'           Metodo para capturar archivo
'
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

Function get_file_location() As String

    Dim fldr As FileDialog
    Dim sItem As String
    Set fldr = Application.FileDialog(msoFileDialogFilePicker)
    With fldr
        .Title = "Selecciona proforma"
        .AllowMultiSelect = False
        .InitialFileName = Application.DefaultFilePath
        If .Show <> -1 Then GoTo NextCode
        sItem = .SelectedItems(1)

    End With

    NextCode:
        get_file_location = sItem
        Set fldr = Nothing
End Function

Sub Get_the_files()


    Dim path_in As String
    Dim path_out As String
    Dim p_here As String

    Dim file_to_copy As Object
    Set file_to_copy = VBA.CreateObject("Scripting.FileSystemObject")
    p_here = ThisWorkbook.Path
    p_out = p_here & "\stdin\TRF.xlsx"
    path_in = get_file_location()

    If path_in <> vbNullString Then
        Call file_to_copy.CopyFile(path_in, p_out)
        MsgBox ("    Archivo seleccionado" & vbNewLine & "Listo para generar correos")
    Else
        MsgBox ("No se selecciono archivo")
    End If
End Sub

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
'
'               Bloque de funciones
'
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

Sub createFolder(ByVal path as String)
    ' Funcion que revisa si existe una carpeta, si no la crea
    Dim sh as Object
    Set sh = VBA.CreateObject("WScript.Shell")
    If Len(Dir(path)) = 0 Then sh.Run "cmd.exe /s /C MD " & Dir(path), 1, True
End Sub

Function getUniquesCol(ByRef ws As Worksheet, ByVal col As String) As String()

    'Funcion que devulve los elementos unicos en una columna, en un array. Recibe Hoja para medir y la columna para encontrar.

    Dim tmp As String

    If ws.AutoFilterMode = True Then ws.AutoFilterMode = False
    For i = 2 To ws.Range("A1").CurrentRegion.Rows.Count
        If (ws.Range(col & i) <> "") And (InStr(tmp, ws.Range(col & i)) = 0) Then
            tmp = tmp & ws.Range(col & i) & "|"
        End If
    Next i

    If Len(tmp) > 0 Then tmp = Left(tmp, Len(tmp) - 1)

    getUniquesCol = Split(tmp, "|")

End Function


Sub Open_Clean_AVISO()

    ' Abre una proforma limpia para ser llenada y guardada en algun otro lugar.
    ' La razon de que es asi, es por la trasabilidad de los archivos(burocracia coorporativa)

    Dim wb As Workbook: Set wb = Workbooks.Open(ThisWorkbook.Path & "\stdin\AVISO.xlsx")
    Dim ws As Worksheet: Set ws = wb.Sheets(1)
    
    With ws
        .Range("A1") = ""        
        .Range(.Cells(5, 1), .Cells(.Range("A4").CurrentRegion.Rows.Count + 2, 7)).Delete shift:=xlShiftUp
        .Range(.Cells(4, 1), .Cells(4, 7)).Delete
        Application.Goto Sheets("Detalle").Range("A1"), True
    End With
    
    wb.Save

End Sub
