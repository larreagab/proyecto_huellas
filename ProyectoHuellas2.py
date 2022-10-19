from signal import signal, SIGTERM, SIGHUP, pause
from time import sleep
from threading import Thread
import openpyxl
import pyrebase
from datetime import datetime,timedelta


import ProyectoModulo2 as huella

#import adafruit_fingerprint
#import serial

config = {
      "apiKey": "AIzaSyCVQXSHJZtpTfgjVvJDzOWoyYQ-hwkuaM0",
  "authDomain": "proyectohuellas-d8dc4.firebaseapp.com",
  "databaseURL": "https://proyectohuellas-d8dc4-default-rtdb.firebaseio.com",
  "storageBucket": "proyectohuellas-d8dc4.appspot.com"
}

firebase=pyrebase.initialize_app(config)
db=firebase.database()
storage=firebase.storage()

#uart = serial.Serial("/dev/ttyUSB0", baudrate=57600, timeout=1)

#finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)

lectura=True
opcion=0
# lista de paralelos
lista_paralelos=["101","102", "103", "104", "105", "106","107", "108", "109","110", "111", "112", "T101"]

paralelo_horario={
    "101":"11:00:00",
    "102":"09:00:00",
    "103":"15:00:00",
    "104":"13:00:00",
    "105":"09:00:00",
    "106":"13:00:00",
    "107":"13:00:00",
    "108":"15:00:00",
    "109":"09:00:00",
    "110":"11:00:00",
    "111":"15:00:00",
    "112":"11:00:00",
    "T101":"13:00:00"

    }


usu="sistemb"
contra="sistemb22"

def safe_exit(signum, frame):
    exit(1)

signal(SIGTERM, safe_exit)
signal(SIGHUP, safe_exit)


def fecha():
    now = datetime.now()
    fecha_hora = now.strftime("%d/%m/%Y - %H:%M:%S")
    return fecha_hora

def restar_hora(hora1, hora2):
    formato="%H:%M:%S"
    lista=hora2.split(":")
    hora=int(lista[0])
    minuto=int(lista[1])
    segundo=int(lista[2])
    h1=datetime.strptime(hora1,formato)
    dh=timedelta(hours=hora)
    dm=timedelta(minutes=minuto)
    ds=timedelta(seconds=segundo)
    resultado1=h1-ds
    resultado2=resultado1-dm
    resultado=resultado2-dh
    resultado=resultado.strftime(formato)
    return str(resultado)

def main():
    while lectura:
        ID=db.child("ID").get().val()
        print()
        print("ELIJA UNA OPCION Y PRESIONE ENTER")
        print("1. REGISTRO")
        print("2. MARCAR ASISTENCIA")
        print("3. PRESTAMO MATERIAL")
        print()
        opcion=(input())
        
        if (opcion=="1"):
            print("Ingrese sus nombres y apellidos:")
            nombres=str(input())
            try:
                print("Ingrese su Matricula")
                matricula=int(input( ))
                matricula=str(matricula)
                try:
                    print("Ingrese su Paralelo")
                    paralelo=str(input())
                    #paralelo=str(paralelo)
                    data={"Nombres":nombres,"Matricula":matricula,"Paralelo":paralelo}
                    print("Verifique sus Datos y Espere")
                    print(nombres)
                    print(matricula)
                    print(paralelo)
                    sleep(6)
                    print("Datos correctos S/N")
                    verificacion=str(input()).lower()
                    if(verificacion=="s"):
                        if(huella.enroll_finger(ID)): 
                            db.child("Tabla Registro").child("ID:"+str(ID)).set(data)
                            ID=ID+1
                            db.child("ID").set(ID)
                        else:
                            print("Intentelo de nuevo")
                            sleep(2)
                           
                    else:
                        print("Intentelo de nuevo")
                        sleep(2)
                        
                except ValueError:
                    print("Intentelo de nuevo")
                    sleep(2)
                    
            except ValueError:
                print("Ingrese un valor correcto")
                sleep(2)
            
        elif (opcion=="2"):
            print()
            print("ELIJA UNA OPCION Y APLASTE ENTER")
            print("1. MARCAR ENTRADA")
            print("2. MARCAR SALIDA")
            print()
            opcion=str(input())
            
            if(opcion=="1"):
                if(huella.get_fingerprint()):
                    dedoID=huella.finger.finger_id
                    print("Usuario Detectado #", dedoID)
                    now=datetime.now()
                    fecha_actual=str(now.strftime("%H:%M:%S"))
                    fecha1=str(now.strftime("%d-%m-%Y"))
                    fecha_ing=str(now.strftime("%d/%m/%Y - %H:%M:%S"))
                    textID="ID:"+str(dedoID)
                    nombres=db.child("Tabla Registro").child(textID).child("Nombres").get().val()
                    matricula=db.child("Tabla Registro").child(textID).child("Matricula").get().val()
                    paralelo=db.child("Tabla Registro").child(textID).child("Paralelo").get().val()
                    estado=""

                    
                    hora_entrada=paralelo_horario.get(paralelo,"Invalido")
                    if(hora_entrada=="Invalido"):
                        print("Paralelo Invalido")
                        print("Intentelo de nuevo") 
                        sleep(2)
                    else:
                        f1=restar_hora(fecha_actual,hora_entrada)
                        lista_f1=f1.split(":")
                        tiempo=int(lista_f1[1])
                        tiempo1=int(lista_f1[0])
                        if(tiempo<=10 and tiempo1<1):
                            print("Estado Asistio")
                            estado="Asistio"
                        elif(tiempo>10 and tiempo<15 and tiempo1<1):
                            print("Estado Atrasado")
                            estado="Atrasado"
                        else:
                            estado="No Asistio"
                            print("Estado No Asistio")
                        data={"Nombres":nombres,"Matricula":matricula,"Paralelo":paralelo,"Fecha Ingreso":fecha_ing,"Fecha Salida":"","Estado":estado}
                        db.child("Tabla Asistencia").child(fecha1).child("ID:"+str(dedoID)).update(data)
                        print("Ingreso de Entrada Correcto")
                        sleep(2)  
                        
                else:
                    print("Error")
                    print("Intentelo de nuevo")
                    sleep(2)
            elif(opcion=="2"):
                if(huella.get_fingerprint()):
                    dedoID=huella.finger.finger_id
                    textID="ID:"+str(dedoID)
                    print("Usuario Detectado #", dedoID)
                    now=datetime.now()  
                    fecha1=str(now.strftime("%d-%m-%Y"))
                    ids=db.child("Tabla Asistencia").child(fecha1).shallow().get().val()
                    if(ids!=None):
                        if (textID in ids):
                            print("Usuario Detectado")
                            fecha_sal=fecha()
                            db.child("Tabla Asistencia").child(fecha1).child(textID).child("Fecha Salida").set(fecha_sal)
                            print("INGRESO DE SALIDA EXITOSO")
                            sleep(2)
                        else:
                            print("No se ha marcado el ingreso")
                            sleep(2)
                    else:
                        print("No existe la tabla de asistencia")
                        sleep(2)
            else:
                print("Opcion Invalida")
                sleep(2)
        elif (opcion=="3"):
            print("ELIJA UNA OPCION Y PRESIONE ENTER")
            print("1.PEDIR MATERIAL")
            print("2.DEVOLVER MATERIAL")
            print()
            
            opcion=str(input())
            if(opcion=="1"):
                if(huella.get_fingerprint()):
                    dedoID=huella.finger.finger_id
                    print("Usuario Detectado #", dedoID)
                    material=input("Ingrese nombre del Material: ")
                    now=datetime.now()
                    fecha_pres=str(now.strftime("%d/%m/%Y - %H:%M:%S"))
                    textID="ID:"+str(dedoID)
                    nombres=db.child("Tabla Registro").child(textID).child("Nombres").get().val()
                    matricula=db.child("Tabla Registro").child(textID).child("Matricula").get().val()
                    paralelo=db.child("Tabla Registro").child(textID).child("Paralelo").get().val()
                    estado="NO DEVUELTO"
                    data={"Nombres":nombres,"Matricula":matricula,"Paralelo":paralelo}
                    lista={material:{"Fecha Prestamo":fecha_pres,"Fecha Devolucion":"","Estado":estado}}
                    print("Verifique los Datos")
                    print(nombres)
                    print(material)
                    sleep(5)
                    
                    print("Datos correctos S/N")
                    verificacion=str(input()).lower()
                    if(verificacion=="s"):
                        db.child("Tabla Prestamo").child("ID:"+str(dedoID)).update(data)
                        db.child("Tabla Prestamo").child("ID:"+str(dedoID)).child("Lista Material").update(lista)
                        print("PRESTAMO EXITOSO")
                        print()
                        sleep(2)
                    else:
                        print("Intentelo de nuevo") 
                        sleep(2)
                else:
                    print("Intentelo de nuevo")  
                    sleep(2)

            elif(opcion=="2"):
                if(huella.get_fingerprint()):
                    dedoID=huella.finger.finger_id
                    textID="ID:"+str(dedoID)
                    ids=db.child("Tabla Prestamo").shallow().get().val()
                    if (textID in ids):
                        print("Usuario Detectado #", dedoID)
                        fecha_dev=fecha()
                        listam=db.child("Tabla Prestamo").child(textID).child("Lista Material").shallow().get().val()
                        if(listam!=None):
                            listam=list(listam)
                            n_estadom=[]
                            #contar elementos de la lista con estado no devuelto
                            for m in listam:
                                estado=db.child("Tabla Prestamo").child(textID).child("Lista Material").child(m).child("Estado").get().val()
                                if(estado=="NO DEVUELTO"):
                                    n_estadom.append(m)
                            if(len(n_estadom)>0):    
                                print("ELIJA NUMERO DE MATERIAL A DEVOLVER")
                                maximo=len(n_estadom)
                                for i in range(maximo):
                                    #imprimir lista de materiales
                                    print(i+1,": ",n_estadom[i])

                                    
                                try:
                                    opcion=int(input("ELIJA UN NUMERO: "))
                                    material_list=str(n_estadom[opcion-1])
                                    print("Verifique los Datos")
                                    print("Material a devolver:")
                                    print(material_list)
                                    sleep(5)
                                    print("Datos correctos S/N ")
                                    verificacion=str(input()).lower()
                                    if(verificacion=="s"):
                                            db.child("Tabla Prestamo").child(textID).child("Lista Material").child(material_list).child("Fecha Devolucion").set(fecha_dev)
                                            db.child("Tabla Prestamo").child(textID).child("Lista Material").child(material_list).child("Estado").set("Devuelto")
                                            print("DEVOLUCION EXITOSA")
                                            sleep(2)
                                    else:
                                        print("Intentelo de nuevo")
                                        sleep(2)
                                
                                except ValueError:
                                    print("Ingrese un Valor Correcto")
                                    sleep(2)
                                    
                                except IndexError:
                                    print("Ingrese un Valor Correcto")
                                    sleep(2)
                            else:
                                print("No tiene deudas de material en prestamo") 
                                sleep(2)
                            
            else:
                
                print("Opcion Invalida")    
                sleep(2)
        elif (opcion=="0"):
           
            usuario=str(input("Ingrese Usuario: "))
            if(usuario==usu):
                
                clave=str(input("Ingrese Clave: "))
                if(clave==contra):
                    print()
                    print("BIENVENIDO")
                    print("ESCOJA UNA OPCION:")
                    print("1.BORRAR USUARIO")
                    print("2.GENERAR REPORTES")
                    print()
                    opcion=str(input())
                    if(opcion=="1"):
                        print("Ingrese Matricula del Usuario a borrar")
                        usuario=str(input())
                        ids=db.child("Tabla Registro").shallow().get().val()
                        if(ids!=None):
                            ids=list(ids)
                            capa=len(ids)
                            n_estadom=[]
                            id_usu=0
                            for i in ids:
                                matricula=db.child("Tabla Registro").child(i).child("Matricula").get().val()
                                id_split=str(i)
                                id_split=i.split(":")
                                num=id_split[1]
                                num=int(num)
                                
                                if(usuario==matricula):
                                    materiales=db.child("Tabla Prestamo").child(i).child("Lista Material").shallow().get().val()
                                    if(materiales!=None):
                                        materiales=list(materiales)
                                    
                                        for m in materiales:
                                            estado_m=db.child("Tabla Prestamo").child(i).child("Lista Material").child(m).child("Estado").get().val()
                                            n_estadom.append(estado_m)
                                    id_usu=num
                                else:
                                    print("Por favor Espere")
                        
                            n_materiales=len(n_estadom)       
                            devueltos=n_estadom.count("Devuelto")
                        
                            if(devueltos==n_materiales and id_usu!=0):  
                                if huella.finger.delete_model(id_usu) == huella.adafruit_fingerprint.OK:
                                    texto=str(id_usu)
                                    i="ID:"+texto
                                    db.child("Tabla Registro").child(i).remove()
                                    db.child("Tabla Prestamo").child(i).remove()
                                    db.child("Tabla Reportes").child(i).remove()
                                    fechas=db.child("Tabla Asistencia").shallow().get().val()
                                    if(fechas!=None):    
                                        fechas=list(fechas)
                                        for a in fechas:
                                            db.child("Tabla Asistencia").child(a).child(i).remove() 
                                    print("USUARIO BORRADO!")
                                    
                                    sleep(2) 
                                else:
                                    
                                    print("FALLO EN BORRAR")
                                    sleep(2)
                            if(devueltos<n_materiales and n_materiales!=0):
                                print("EL USUARIO DEBE DEVOLVER MATERIAL")
                                sleep(2)
                            
                            if(id_usu==0):
                                print("USUARIO NO ENCONTRADO")
                                sleep(2)
                    elif(opcion=="2"):
                        ids=db.child("Tabla Registro").shallow().get().val()
                        fechas=db.child("Tabla Asistencia").shallow().get().val()
                        if(ids!=None and fechas!=None):
                            ids=list(ids)
                            lista_fechas=[]
                            print("Por Favor Espere")
                            for i in ids:
                                
                                if(fechas!=None):
                                    fechas=list(fechas)
                                    lista_rep=[]
                                    
                                    for a in fechas:
                                        if a not in lista_fechas:
                                            lista_fechas.append(a)
                                        estado=db.child("Tabla Asistencia").child(a).child(i).child("Estado").get().val()
                                        lista_rep.append(estado)
                                    
                                    asistencias=str(lista_rep.count("Asistio"))
                                    atrasos=str(lista_rep.count("Atrasado"))
                                    faltas=str(lista_rep.count("No Asistio"))
                                    nombres=db.child("Tabla Registro").child(i).child("Nombres").get().val()
                                    db.child("Tabla Reportes").child(i).child("Nombres").set(nombres)
                                    db.child("Tabla Reportes").child(i).child("Asistencias").set(asistencias)
                                    db.child("Tabla Reportes").child(i).child("Atrasos").set(atrasos)
                                    db.child("Tabla Reportes").child(i).child("Faltas").set(faltas)
                                    
                    
                            for a in lista_paralelos:
                                wb=openpyxl.Workbook()
                                hoja=wb.active
                                ids=db.child("Tabla Reportes").shallow().get().val()
                                ids=list(ids)
                                hoja.append(("Asistencias","Atrasos","Faltas","Nombres"))
                                for i in ids:
                                    data=[]
                                    paralelo=db.child("Tabla Registro").child(i).child("Paralelo").get().val()
                                    reporteuwu=db.child("Tabla Reportes").child(i).shallow().get().val()
                                    reporteuwu=list(reporteuwu)
                                
                                    if(paralelo==a):
                                    
                                        for u in reporteuwu:
                                            datito=db.child("Tabla Reportes").child(i).child(u).get().val()
                                            data.append(datito)
                                        hoja.append(data)
                                wb.save("/home/sistembebidos/Desktop/Reportes/Reportes_P"+a+".xlsx")
                                storage.child("Reportes_P"+a+".xlsx").put("/home/sistembebidos/Desktop/Reportes/Reportes_P"+a+".xlsx")
                            print("REPORTE GENERADO")
                            sleep(2)
                        else:
                            print("NO HAY DATOS")
                            sleep(2)
                    else:
                       
                        print("Opcion Invalida")
                        sleep(2)
                else:
                    
                    print("CLAVE INVALIDA")
                    sleep(2)          
            else:
                
                print("USUARIO INVALIDO")
                sleep(2)
                    
        else:
            
            print("Opcion Invalida")
            sleep(2)

try:
#     db.child("ID").set(1)#Solo se ejecuta una vez
    main()
except KeyboardInterrupt:
    pass

finally:
    lectura=False
    sleep(0.5)

 
