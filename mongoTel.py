# Pymongo
from pymongo import MongoClient
import pymongo.errors as mongoErr
from pymongo.database import Collection # Variable
from variables import * 

def iniciarBD():
    """
    Iniciar una base de datos desde cero, borra la base de datos anterior
    """
    try:
        print("Inicializando base de datos desde cero")
        entrada = input("La base de datos anterior será borrada antes de crear una nueva desde cero.\n¿Estás seguro de ello? [y/n]").strip().split()
        cliente = MongoClient(url_bbddConection)
        if entrada == 'y':
            cliente.drop_database(databaseName)
            bbdd = cliente.get_database(databaseName) # Crear/acceder base de datos
            collection = bbdd.get_collection(collectionName) # Crear/acceder coleccion
            guardar(collection, itemEjemplo) # Introducir un 1º elemento de pruebas
            print("Base de datos iniciada desde cero correctamente")
        return 
    except Exception as err:
        print("Algo ha salido mal al inicializar la base de datos desde cero - " + str(err))
        return 

def connect() -> Collection|False:
    """
    Conectarse a la base de datos. Devuelve directamente la colección de la base de datos (Solo hay una coleccion) 
    """
    try:
        cliente = MongoClient(url_bbddConection)
        try:
            print("Conexión con la base de datos: ", end="")
            print(cliente.server_info()['version'])
            bbdd = cliente.get_database(databaseName)
            collection = bbdd.get_collection(collectionName)
            return collection
        except mongoErr.OperationFailure as err:
            print(err)
            return False
    except mongoErr.ConnectionFailure as e:
        print("Error de conexión -> ", e)
    return False
def closeDB():
    try:
        cliente = MongoClient(url_bbddConection)
        cliente.close()
        print("Conexción con la base de datos cerrada")
    except Exception.ConnectionFailure as e:
        print("Error de conexión -> ", e)
    return

def guardar(col: Collection, item: dict) -> bool: 
    """
    Guardar los datos en la base de datos.
    """
    resultado = col.insert_one(item)
    if not resultado:
        print("No se ha podido guardar el elemento")
        return False
    else:
        print("Elemento guardado en la base de datos correctamente")
    return True