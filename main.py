from seleniumTel import *
from mongoTel import *

if __name__ == '__main__':
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
            elif entrada == "info":
                id = input("Introducir el id del chat\n-> ")
                item = getInfo(driver, id, chats)
                if type(item) == list: # Se ha extraido infor de una comunidad (grupos agrupados)
                    for i in item:
                        guardar(collection, item)
                else:
                    guardar(collection, item) 
            elif entrada in help:
                print(comandos)
            elif entrada in salir:
                seguir = False
            else:
                print("Entrada inválida: " + entrada + "- Prueba de nuevo")
            print(" --------------------------- ")
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