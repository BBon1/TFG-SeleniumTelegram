####### Rellenar #########
phone = "OPCIONAL"
rutaDescargas = "Donde se van a descargar los archivos en caso de implementar dicha función"
url_bbddConection = 'Enlace con las credenciales de la base de datos MongoDB'
##########################
url_login = "https://web.telegram.org/a/"
salir = ["exit", "quit", "salir", "adios", "bye"]
help = ["-help", "-h", "--h"]
comandos = \
    "bbdd                                - Iniciar desde cero una base de datos.\n" \
    "chats                               - Imprime por pantalla los nombres de los chats con sus respectivos ids.\n"\
    "info                                - Sacar todos los datos de un chat dado un id. Y los guarda en la base de datos\n" \
    "-help, -h, --h                      - Menú de ayuda\n"\
    "exit, quit, salir, adios, bye       - Exit\n"
inicio = "############## Herramienta para extraer datos en Telegram ##############\n" \
         "Una herramienta básica desarollada como proyecto de fin de grado\n"\
         "Comandos disponibles: \n"
databaseName = 'telegram'
collectionName = "scraping"
itemEjemplo = {
    # "_id": "Lo general la base de datos | Id del elemento en la bbdd" 
    "id_chat": "123456789",
    "name_chat": "Entrada de Pruebas",
    "type": "Test",
    "avatar": "Por defecto/nombreImg",
    "fullName": "Entrada de Pruebas",
    "status": "Pruebas",
    "extras": ["description: Vacío", "contact: 123"],
    "num_mensajes": 2,
    "mensajes": {
        "1": {
            "sender": "Mensaje propio",
            "date": "",
            "typeContent": "Texto",
            "content": ["Contenido del mensaje"]
        },
        "2": {
            "sender": {
                "id_user": "987654321", 
                "name_user": "Otro usuario",
                "avatar": "Por defecto/nombreImg"
            },
            "date": "",
            "typeContent": "Texto",
            "content": ["Contenido del mensaje"]
        }
    }
}