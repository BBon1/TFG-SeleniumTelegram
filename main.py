from seleniumTel import *
from mongoTel import *
from variables import *

if __name__ == '__main__':
    print(inicio)
    print(comandos)
    collection = connect() # acceder a la base de datos
    driver = newDriverChrome() # abrir navegador
    if loginQR(driver):
        chats = getListChats(driver) # Lista de chats completa
        seguir = True
        while seguir:
            entrada = input("¿Qué quieres hacer?\n-> ")
            if entrada == "bbdd":
                iniciarBD()
            elif entrada == "chats": # visualizar chats
                contador = 0
                print("Lista de chats:")
                for c in chats:
                    if contador == 3:
                        print()
                        contador = 0
                    print("[ "+c[1] +": "+ c[0], end=" ]\t")
                    contador += 1
            elif entrada == "info":
                id = input("Introducir el id del chat\n-> ")
                item = getInfo(driver, id, chats)
                if type(item) == list: # Se ha extraido infor de un grupo con temas (grupos anidados)
                    for i in item:
                        guardar(collection, i)
                elif type(item) == dict:
                    guardar(collection, item) 
            elif entrada in help:
                print(comandos)
            elif entrada in salir:
                seguir = False
            else:
                print("Entrada inválida: " + entrada + "- Prueba de nuevo")
            print("\n --------------------------- ")
    else:
        print("Fallo al iniciar sesión en Telegram")
    closeDB()
    try:
        print("Cerrando navegador")
        driver.close()
        time.sleep(3)
    except seleniumErr.InvalidSessionIdException as err:
        print("Problemas al cerrar el driver -> " + str(err))
    exit(0)