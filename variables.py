####### Rellenar #########
phone = ""
rutaDescargas = ""
url_bbddConection = ''
##########################
url_login = "https://web.telegram.org/a/"
salir = ["exit", "quit", "salir", "adios", "bye"]
help = ["-help", "-h", "--h"]
comandos = \
    "bbdd                                - Iniciar desde cero una base de datos.\n" \
    "info                                - Sacar todos los datos de un chat dado un id. Y los guarda en la base de datos\n" \
    "-help, -h, --h                      - Menú de ayuda\n"\
    "exit, quit, salir, adios, bye       - Exit\n"
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
        1: {
            "sender": "Mensaje propio",
            "date": "",
            "typeContent": "Texto",
            "content": ["Contenido del mensaje"]
        },
        2: {
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