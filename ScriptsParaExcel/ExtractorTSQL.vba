''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
'                           Extractor SQL
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
' Para que este extractor funcione se deben activar los complementos necesarios dentro
' de Excel. Basicamente asegurarse de que la libreria de conexiones ADODB este chequeada
' Ademas se debe de tener el driver para la base de datos correcta y que esta se encuentre
' en las variables de entorno correspondiente


Sub Extractor_SQL(opcion_de_extraccion, output_folder)

'-Strings
Dim SQL_string As String
Dim output_file_name As String
Dim usr, psw, db, ctlg, con_string As String
Dim wb As Workbook
Dim ws As Worksheet

usr = ""
psw = ""
db_server = ""
db = "" 'db cluster
ctlg = "" 'actual db
SQL_Driver = ""

SQL_string = ""
output_file_name = "" 'full path

'---== Extraccion ==---
Set obj_conexion = New ADODB.Connection
Set obj_record_set = New ADODB.Recordset

con_string = "Driver={" & SQL_Driver & "}; Server=" & db & ";Database=" & ctlg & ";User Id=" & usr & ";Password=" & psw & ";"
obj_conexion.ConnectionString = con_string
obj_conexion.Open

Set obj_record_set.ActiveConnection = obj_conexion
obj_record_set.Open SQL_string

Set wb = Workbooks.Open(output_file_name)
Set ws = wb.Worksheets(1)

With ws
    If .AutoFilterMode = True Then .AutoFilterMode = False
    .Range("A1").CurrentRegion.Delete
    
    For i = 0 To obj_record_set.Fields.Count - 1
        .Cells(1, i + 1) = obj_record_set.Fields(i).Name
    Next i
    
    .Range("A2").CopyFromRecordset obj_record_set
End With

wb.Close True

obj_record_set.Close
Set obj_recor_set = Nothing
obj_conexion.Close
Set obj_conexion = Nothing

End Sub
