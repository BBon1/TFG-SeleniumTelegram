# Selenium
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement # Variable
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver.chrome.options import Options as OpChrome
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver import Keys
import selenium.common.exceptions as seleniumErr
# Generales
import time
import re
from datetime import datetime, timedelta
from variables import *

def newDriverChrome() -> webdriver.Chrome:
    options = OpChrome()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-web-security")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-notifications")
    options.add_argument("--ignore-certificate-errors'")
    options.add_argument("--no-sandbox")
    options.add_argument("--log-level=3")
    options.add_argument("--allow-running-insecure-content")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--no-first-run")
    options.add_argument("--no-proxy-server")
    options.add_argument("--disable--blink-features=AutomationControlled")
    prefs = {"download.default_directory" : rutaDescargas, # Directorio de descarga
             "download.prompt_for_download": False} # Aviso de descarga desactivado
    options.add_experimental_option("prefs",prefs)
    try:
        driver = webdriver.Chrome(options=options)
    except:
        print("Instalando drivers de Chrome")
        driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=options)
    return driver

def login(driver: webdriver.Chrome) -> bool: 
    """
    Inicio de sesión semi-automático, el código de seguridad lo pide siempre.
    """
    print("Iniciando sesión en Telegram")
    driver.get(url_login)
    time.sleep(5) # la página tarda un poco en cargar el QR inicial (el cual no usaremos nosotros)
    try: 
        boton = driver.find_element(By.CSS_SELECTOR, "button[class='Button auth-button default primary text']") 
        boton.click()
        time.sleep(2) 
        phoneNumber = driver.find_element(By.CSS_SELECTOR, "input[id='sign-in-phone-number']")
        phoneNumber.send_keys(phone)
        phoneNumber.send_keys(Keys.ENTER)
        code = input("Código de inicio: ")
        securityCode = driver.find_element(By.CSS_SELECTOR, "input[id='sign-in-code']")
        securityCode.send_keys(code) # Al recibirlo ya continua el proceso
        return True
    except seleniumErr.NoSuchElementException as err:
        print("Algo salió mal con el inicio de sesión ->\n"+ err)
        return False
def loginQR(driver: webdriver) -> bool:  
    """
    Inicio de sesión con QR, más rápido. No tocar la terminal de python mientras se carga.
    """
    driver.get(url_login)
    return True
    
def openMenu(driver: webdriver.Chrome, menu: str) -> None: 
    """
    Desplazarse entre las ventanas del menú principal/contactos \n
    Ya hace la comprobación de si ya se está en el menú indicado \n
    principal/contactos
    """ 
    check = bool() ## Comprobación del menú actual
    aux = driver.find_elements(By.CSS_SELECTOR,  "button[title='Open menu']")
    if menu == "principal":
        check = len(aux) > 0 # Hay botón de menú = Se está en el menú principal
    elif menu == "contactos":
        check = len(aux) <= 0 # No hay boton de menú = Se está en otro menú
    else: 
        check = False

    if not check: # Se está en un menú distinto al que se quiere
        seleccion = "button[title='Open menu']" if menu == "contactos" else "button[title='Return to chat list']"
        try: 
            boton = driver.find_element(By.CSS_SELECTOR, seleccion)  
            boton.click()
            if menu == "contactos":
                options = driver.find_elements(By.CSS_SELECTOR, "div[class='MenuItem compact']")
                for o in options: # No necesariamente encuentra las opciones en orden visual del menú
                    if o.get_attribute('innerText') == "Contacts":
                        o.click() 
                        time.sleep(1)
                        return
        except seleniumErr.NoSuchElementException as err:
            print("Error con el menú ->\n" + str(err)) 
        time.sleep(1)    
    return

def scrollUpDown(driver: webdriver.Chrome, elemento: str) -> None:
    """
    Función auxiliar para hacer scroll en la ventana de chats o en los contactos, hacia arriba o abajo \n
    accion: subir/bajar \n
    elemento: chat / contactosP / contactosC / miembros
    """
    altura = driver.execute_script("return document.body.scrollHeight")
    if elemento == "chat":
        seccion = "div[class='messages-container']"
        altura *= 3
        direccion = -altura # hacia arriba
    elif elemento == "contactosP": # Contactos menú principal
        seccion = "div[class^='chat-list custom-scroll']" # 'chat-list custom-scroll no-overscroll'
        direccion = altura
    elif elemento == "contactosC": # Contacto menú contactos
        seccion = "div[class='chat-list custom-scroll']"
        direccion = altura
    elif elemento == "miembros":
        seccion = "div[class='NiALUSnA es6RankF']"
        direccion = altura//2
    try:
        webelement = driver.find_element(By.CSS_SELECTOR, seccion)
        for _ in range(0,5):
            scroll_origin = ScrollOrigin.from_element(webelement, 0, 0)
            ActionChains(driver).scroll_from_origin(scroll_origin, 0, direccion).perform()
            time.sleep(1) # Espera obligatoria para que cargue el contenido si hay 
    except seleniumErr.NoSuchElementException as err:
        print("Algo salió mal al hacer scroll: " + str(err)) 
    return

def selectChat(driver: webdriver.Chrome, id_chat: str, contactos: list[tuple]) -> str|None: 
    """
    Función auxiliar para seleccionar un chat
    Hay que pasarle una lista de los contactos con los webElement incluidos
    """
    for c in contactos: # tuple (id_chat / name / menu / webElement)
        if c[0] == id_chat:
            try:  
                openMenu(driver, c[2]) # ir al menu donde se encuentra el chat
                driver.execute_script("arguments[0].scrollIntoView();", c[3]) # ir hasta el elemento 
                c[3].click() # acceder al chat
                return c[1] # name  
            except seleniumErr.ElementClickInterceptedException as err:
                print("Ha surgido un error al seleccionar el chat: " + str(err))
                return None
    print("Chat no encontrado en la lista proporcionada")
    return None

def getListChats(driver: webdriver.Chrome) -> list[tuple]: 
    """
    Recolecta todos los contactos, grupos y canales de la cuenta
    lista[(id_user/chat, nombre, menu, webElement)]
    """
    print("Listando todos los chats y contactos de la cuenta...")
    chatsPrincipal = auxChats(driver, "principal") 
    openMenu(driver,"contactos")  
    chatsUsuarios = auxChats(driver, "contactos")   
    chats = list(chatsPrincipal.union(chatsUsuarios))  
    print("Número de chats encontrados: " + str(len(chats))) 
    return chats # una lista de tuplas sin duplicados
def auxChats(driver: webdriver.Chrome, menu: str) -> set:
    """
    Función auxiliar para extraer los contactos, grupos, canales, bots, etc de la cuenta de Telegram
    """
    conjunto = set()
    ids = set()
    contador = -1
    elemento = "a[class='ListItem-button']" if menu == "principal" else "div[class='ListItem chat-item-clickable contact-list-item']"
    scroll = "contactosP" if menu == "principal" else "contactosC"
    openMenu(driver, menu) # comprobar si se está en el menú correcto
    while contador != len(conjunto):
        contador = len(conjunto) # actualizar valor 
        try:
            listAux = driver.find_elements(By.CSS_SELECTOR, elemento)
            for c in listAux:
                id = c.find_element(By.CSS_SELECTOR, "div[class^='Avatar']").get_attribute('data-peer-id')
                if id not in ids:
                    name = c.find_element(By.CSS_SELECTOR, "div[class='title QljEeKI5']").get_attribute("innerText")
                    conjunto.add((id, name, menu ,c)) # (id_chat / name / menu / webElement)
                    ids.add(id)
            scrollUpDown(driver, scroll) # sacar más contactos
            time.sleep(1)
        except seleniumErr.NoSuchElementException as err:
            print("Algo ha salido mal extraer la lista de contactos de "+ menu +"\n" + str(err))
            contador = len(conjunto) # cortar el bucle while
    return conjunto

def getInfoChat(driver: webdriver.Chrome, id_chat: str, name: str) -> dict:  
    """
    Extraer información visible de un usuario, grupo, canal, comunidad...
    """
    info = {
        "id": id_chat,
        "name": name,
        "type": "",
        "avatar": "",
        "fullName": "",
        "status": "",
        "extras": []
    }
    print("Extrayendo información del chat...")
    try:
        middle = driver.find_element(By.CSS_SELECTOR, "div[class='MiddleHeader']") 
        middle.find_element(By.CSS_SELECTOR, "h3[role='button']").click() # abrir la pestaña de info
        right = driver.find_element(By.CSS_SELECTOR, "div[id='RightColumn']")
        info["type"] = right.find_element(By.CSS_SELECTOR, "h3[class='title']").get_attribute('innerText') # User info / Bot info / Group info / Topic...
        profile = right.find_element(By.CSS_SELECTOR, "div[class='r8nY6BZB profile-info']")
        avatar = profile.find_elements(By.TAG_NAME, "img")
        if len(avatar): # Avatar personalizado
            info["avatar"] = avatar[0].get_attribute('src')
        elif info["type"] == "Topic":
            aux = profile.find_element(By.CSS_SELECTOR, "i[class^='icon icon-']").get_attribute('class').split()
            info["avatar"] = aux[1]
        else: 
            info["avatar"] = "Avatar por defecto"
        if info["type"] != "Topic":
            info["fullName"] = profile.find_element(By.CSS_SELECTOR, "h3[class^='fullName']").get_attribute('innerText')
            info["status"] = profile.find_element(By.CSS_SELECTOR, "[class$='status']").get_attribute('innerText')
        else:
            info["fullName"] = profile.find_element(By.CSS_SELECTOR, "h3[class='hjk4U031']")
            info["status"] = profile.find_element(By.CSS_SELECTOR, "p[class='GXxwbzqF']")
        chatExtra = profile.find_element(By.CSS_SELECTOR, "div[class^='ChatExtra']") 
        chatExtra = chatExtra.find_elements(By.XPATH, "*")  # getchild elements
        chatExtra.pop() # quitar el elemento "Notifications"
        for c in chatExtra:
            title = c.find_element(By.CSS_SELECTOR, "[class^='title']").get_attribute('innerText') 
            subtitle = c.find_element(By.CSS_SELECTOR, "[class='subtitle']").get_attribute('innerText')  
            info["extras"].append(subtitle+": "+title)
        if info["type"] == "Group Info":
            m = right.find_element(By.CSS_SELECTOR, "div[class='NiALUSnA es6RankF']")
            contador = -1
            info.update({"members": []})
            nombres = set()
            while contador != len(nombres):
                contador = len(nombres) 
                members = m.find_elements(By.CSS_SELECTOR, "div[class^='ListItem chat-item-clickable']")
                for auxM in members:
                    n = auxM.find_element(By.CSS_SELECTOR, "div[class='title QljEeKI5']").get_attribute('innerText') # nombre
                    if n not in nombres:
                        r = auxM.find_elements(By.CSS_SELECTOR, "div[class^='hJUqHi4B jNZTCgu2']") # rol
                        r = r[0].get_attribute('innerText') if len(r) else "Sin rol"
                        s = auxM.find_element(By.CSS_SELECTOR, "span[class='user-status']").get_attribute('innerText') # status
                        nombres.add(n) 
                        info["members"].append(n + " - " + s + " - " + r) # nombre - status - rol
                loadMembers(driver)
    except seleniumErr.NoSuchElementException as err:
        print("Error al extraer información del chat -> " +str(err))
    except seleniumErr.ElementNotInteractableException as e:
        print("Error al interactiar con un elemento web -> " +str(e))
    print("Extracción completada")
    return info
def loadMembers(driver: webdriver.Chrome):
    """
    Forzar a la lista de miembros a ser ampliada y cargar más miembros. Refinar (!)
    """
    try:
        aux = driver.find_element(By.CSS_SELECTOR, "div[class='Transition shared-media-transition']")
        string = aux.get_attribute('style')
        matches = re.findall(r'-?\d*\.?\d+', string)
        res = [float(x) if '.' in x else int(x) for x in matches]
        res[1] += 1500
        string = 'height: '+ str(res[0])+'px; flex-basis: '+ str(res[1])+'px; min-height: '+ str(res[2])+'px;'
        driver.execute_script("arguments[0].setAttribute('style',arguments[1])", aux, string)
        scrollUpDown(driver, "miembros") 
        time.sleep(1)
        scrollUpDown(driver, "miembros") 
    except:
        print("Error al buscar más miembros del grupo") 
    return

def getMessageIndiv(driver: webdriver.Chrome, name: str) -> dict: 
    mensajes = {
        "num_mensajes": -1,
        "mensajes": dict() 
    }
    ids = set() # no repetir mensajes
    contador = -1
    print("Extrayendo mensajes de la conversación...")
    while contador != len(mensajes["mensajes"]):
        contador = len(mensajes["mensajes"])
        try:
            bloquesMensajes = driver.find_elements(By.CSS_SELECTOR, "div[class^='message-date-group']") 
            for bloque in bloquesMensajes[::-1]: #agrupaciones por fecha
                fecha = bloque.find_element(By.CSS_SELECTOR, "span[dir='auto']").get_attribute('innerText') # mes día, año*(no aparece si es el año actual)
                listaMensajes = bloque.find_elements(By.CSS_SELECTOR, "div[id^='message-']")
                for unidad in listaMensajes[::-1]: # procesar los mensajes uno a uno
                    id = unidad.get_attribute('data-message-id')
                    if id not in ids:
                        ActionChains(driver).scroll_to_element(aux).perform()
                        ids.add(id) # actualizar ids
                        resultado = getMessage(id, unidad ,fecha, name)
                        mensajes["mensajes"].update(resultado) # añadir info mensajes al diccionario, con id del mensaje como identificador
            scrollUpDown(driver, "chat") # generar mas mensajes
            time.sleep(2)
        except seleniumErr as err:
            print("Error al extraer mensajes - " + str(err))
            contador = len(mensajes["mensajes"])
    mensajes["num_mensajes"] = len(mensajes["mensajes"])
    print("¡Extracción completada!")
    return mensajes
def getMessageGroup(driver: webdriver.Chrome, community = None) -> dict:
    mensajes = { 
        "comunidad": community,
        "num_mensajes": -1,
        "mensajes": dict() 
    } 
    print("Extrayendo mensajes de la conversación...")
    if community == None:
        mensajes.pop("comunidad")
    ids = set() # no repetir mensajes
    contador = -1
    while contador != len(mensajes["mensajes"]):
        contador = len(mensajes["mensajes"])
        try:
            bloquesMensajes = driver.find_elements(By.CSS_SELECTOR, "div[class^='message-date-group']") 
            for bloqueMensajesFecha in bloquesMensajes[::-1]: # agrupación por fechas
                fecha = bloqueMensajesFecha.find_element(By.CSS_SELECTOR, "span[dir='auto']").get_attribute('innerText') # mes día, año*(no aparece si es el año actual)
                bloqueMensajesUsuario = bloqueMensajesFecha.find_elements(By.CSS_SELECTOR, "div[id^='message-group-']") 
                if len(bloqueMensajesUsuario):
                    for message in bloqueMensajesUsuario[::-1]: #agrupaciones por usuarios / si hay
                        sender = auxSender(message)
                        m = message.find_elements(By.CSS_SELECTOR, "div[id^='message-']")
                        for aux in m[::-1]: # procesar los mensajes uno a uno
                            id = aux.get_attribute('data-message-id')
                            if id not in ids:
                                ActionChains(driver).scroll_to_element(aux).perform()
                                ids.add(id)
                                resultado = getMessage(id, aux, fecha, sender)
                                mensajes["mensajes"].update(resultado)
                else: # mensaje del sistema(mensajes centrales)
                    messages = bloqueMensajesFecha.find_elements(By.CSS_SELECTOR, "div[id^='message-']")
                    for aux in messages: # procesar los mensajes uno a uno
                        id = aux.get_attribute('data-message-id')
                        if id not in ids:
                            ids.add(id)
                            resultado = auxMessageSystem(id, aux, fecha)
                            mensajes["mensajes"].update(resultado)
            scrollUpDown(driver, "chat") # generar mas mensajes
            time.sleep(2)
        except seleniumErr.NoSuchElementException as err:
            print("Error al extraer mensajes - " + str(err))
            contador = len(mensajes["mensajes"])
    mensajes["num_mensajes"] = len(mensajes["mensajes"])
    print("¡Extracción completada!")
    return mensajes
def auxSender(mensaje:WebElement) -> dict:
    sender = {
        "id_user": "Yo", 
        "name_user": "Yo",
        "avatar": "Yo"
    }
    userData = mensaje.find_elements(By.CSS_SELECTOR, "div[class^='Avatar jdvqXfYh']")    
    if len(userData): # Mensaje enviado por otro usuario
        sender["id_user"] = userData[0].get_attribute('data-peer-id')
        try: # avatar personalizado - img
            sender["name_user"] = userData[0].find_element(By.TAG_NAME, "img").get_attribute('alt')
            sender["avatar"] = userData[0].find_element(By.TAG_NAME, "img").get_attribute('src') 
        except: # avatar por defecto
            sender["name_user"] = userData[0].get_attribute('aria-label')
            sender["avatar"] = "Avatar por defecto"
    return sender
def auxMessageSystem(id: int,message: WebElement, date:str) -> dict:
    objeto = {
        id: {
            "sender": "Sistema",
            "date": date,
            "typeContent": "Información",
            "content": []
        }
    } 
    centro = message.find_elements(By.CSS_SELECTOR, "div[class='CrZTrncJ']") # Mensajes centrales del chat
    if len(centro):
        objeto[id]["content"].append(centro[0].get_attribute('innerText'))
    return objeto
def getMessage(id: int,message: WebElement, date:str, sender: str|dict) -> dict:
    """
    Extraer y dar estructura de diccionario a los datos de un mensaje.
    """
    objeto = {
        id: {
            "sender": "",
            "date": "",
            "typeContent": "",
            "content": []
        }
    } 
    # Remitente del mensaje
    if type(sender) is dict:  # Grupos, varios usuarios
        if sender["id_user"] == "Yo":
            objeto[id]["sender"] = "Mensaje propio"
        else:
            objeto[id]["sender"] = sender 
    elif message.find_elements(By.TAG_NAME, "i"): 
        objeto[id]["sender"] = "Mensaje propio"
    else: # Si no es un mensaje propio, es uno ajeno
        objeto[id]["sender"] = sender
    # Fecha
    if date == "Today":
        date = datetime.strftime(datetime.now(), '%Y-%m-%d')
    elif date == "Yesterday":
        date = datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d')    
    hour = message.find_element(By.CSS_SELECTOR, "span[class='message-time']").get_attribute('innerText')
    objeto[id]["date"] = hour + " " + date    
    # Tipo de contenido posible
    text = message.find_elements(By.CSS_SELECTOR, "div[class^='text-content']") # texto
    media = message.find_elements(By.CSS_SELECTOR, "div[class*='media-inner']") # imagen/sticker/video/Gif/Emoji
    album = message.find_elements(By.CSS_SELECTOR, "div[class='Album']") # Conjunto de imágenes
    voice = message. find_elements(By.CSS_SELECTOR, "div[class^='Audio inline']") # mensaje de voz
    fichero = message.find_elements(By.CSS_SELECTOR, "div[class^='File']") # 'File interactive' / fichero(doc)
    encuesta = message.find_elements(By.CSS_SELECTOR, "div[class='NKFOoVuL']") # Encuesta
    contacto = message.find_elements(By.CSS_SELECTOR, "div[class='tpDpg82n']") # Contacto
    enlace = message.find_elements(By.CSS_SELECTOR, "div[class*='WebPage']") # Enlace
    views = message.find_elements(By.CSS_SELECTOR, "span[class='message-views']")  # Canales 
    # Extraer el contenido 
    try:     
        if len(voice):
            objeto[id]["typeContent"] = "Mensaje de voz"
            duracion = "duracion: " + voice[0].find_element(By.CSS_SELECTOR, "p[class^='voice-duration']").get_attribute('innerText')
            objeto[id]["content"].append(duracion) 
        elif len(fichero):
            objeto[id]["typeContent"] = "Fichero"
            titulo = fichero[0].find_element(By.CSS_SELECTOR, "div[class='file-title']").get_attribute('innerText')
            subtitulo = fichero[0].find_element(By.CSS_SELECTOR, "div[class='file-subtitle']").get_attribute('innerText')
            objeto[id]["content"].extend(titulo +" | "+ subtitulo)
        elif len(encuesta):
            objeto[id]["typeContent"] = "Encuesta"
            objeto[id]["content"].append(encuesta[0].get_attribute('innerText'))
        elif len(contacto):
            objeto[id]["typeContent"] = "Contacto"
            objeto[id]["content"].append(contacto[0].get_attribute('innerText'))
        elif len(enlace):
            objeto[id]["typeContent"] = "Enlace"
            texto = message.find_element(By.CSS_SELECTOR, "div[class^='text-content']")
            url = message.find_element(By.CSS_SELECTOR, "a[data-entity-type='MessageEntityUrl']").get_attribute('href')
            textoEnlace = enlace[0].find_element(By.CSS_SELECTOR, "div[class^='WebPage-text']").get_attribute('innerText')
            objeto[id]["content"].extend([texto.text[:-6], url, textoEnlace])
            imgEnlace = enlace[0].find_elements(By.CSS_SELECTOR, "div[class^='media-inner']")
            if len(imgEnlace): # Puede tener img el enlace
                objeto[id]["content"].append(imgEnlace[0].get_attribute('src')) 
        elif len(album):  
            objeto[id]["typeContent"] = "Album"
            imgs = album[0].find_elements(By.TAG_NAME, "img")
            for i in imgs:
                objeto[id]["content"].append(i.get_attribute('src'))
            texto = message.find_elements(By.CSS_SELECTOR, "div[class^='text-content']")
            if len(texto):
                objeto[id]["content"].append(text[0].text[:-6])
        elif len(media):
            if len(media[0].find_elements(By.CSS_SELECTOR, "img[class^='full-media']")) :
                objeto[id]["typeContent"] = "Imagen" 
                objeto[id]["content"].append(media[0].find_element(By.TAG_NAME, "img").get_attribute('src'))
            elif len(media[0].find_elements(By.CSS_SELECTOR, "div[class^='AnimatedSticker']")): #Sticker/Emoji personalizado
                if len(media[0].find_elements(By.TAG_NAME, "img")):
                    objeto[id]["typeContent"] = "Sticker"
                    objeto[id]["content"].append(media[0].find_element(By.TAG_NAME, "img").get_attribute('src'))
                else: # elif media[0].get_attribute('class') == "AnimatedEmoji media-inner xCi2f0YH":
                    objeto[id]["typeContent"] = "Emoji"
                    objeto[id]["content"].append("Emoji personalizado")
            elif len(media[0].find_elements(By.TAG_NAME, "video")): # Video/Gif
                aux = media[0].find_element(By.CSS_SELECTOR, "div[class='message-media-duration']")
                if aux.get_attribute('innerText') == "GIF":
                    objeto[id]["typeContent"] = "Gif"
                else:
                    objeto[id]["typeContent"] = "Video"
                objeto[id]["content"].append(media[0].find_element(By.TAG_NAME, "video").get_attribute('src'))
            texto = message.find_elements(By.CSS_SELECTOR, "div[class^='text-content']")
            if len(texto):
                objeto[id]["content"].insert(0, text[0].text[:-6])
        elif len(text):
            objeto[id]["typeContent"] = "Texto"
            t = text[0].text[:-6]  
            if t == "This message is not supported on the web version of Telegram":
                objeto[id]["typeContent"] = "Mensaje bomba"
                t = "No se puede visualizar el contenido"
            objeto[id]["content"].append(t)    
            if len(text[0].find_elements(By.CSS_SELECTOR, "img[class^='emoji']")):
                emojis = []
                aux = text[0].find_elements(By.CSS_SELECTOR, "img[class^='emoji']")
                for a in aux:
                    emojis.append(a.get_attribute('src'))
                objeto[id]["content"].append(emojis)
        if len(views): # Atributo de los mensajes de canales
            objeto[id].update({"adicional": views[0].get_attribute('title')})  
            objeto[id]["sender"] = "Administrador del canal"   
    except seleniumErr.NoSuchElementException as err:
        print(err)
    except BaseException as berr:
        print(berr)
    return objeto

def getInfo(driver: webdriver.Chrome, id_chat: str, contactos: list[tuple]) -> list|dict|None:
    """
    Recolecta los mensajes y la información de un chat, grupo, canal o comunidad.
    """
    name = selectChat(driver, id_chat, contactos)
    if name != None: # acceder al chat
        print("Chat encontrado -> ")
        if "-" in id_chat: # es un grupo/canal
            prev = driver.find_elements(By.CSS_SELECTOR, "div[class='lrlHKC_D']") 
            if len(prev) > 0: # Es una comunidad con varios chats asociados
                grupos = prev[0].find_elements(By.CSS_SELECTOR, "a[class='ListItem-button']") # Temas del grupo
                principal = prev[0].find_element(By.CSS_SELECTOR, "h3[role='button']") # Grupo principal
                listaMensajes = []
                listaInfo = []
                for g in grupos:
                    id_subChat = g.get_attribute('href').removeprefix("https://web.telegram.org/a/#")
                    name_subChat = g.find_element(By.TAG_NAME, 'h3').get_attribute('innerText')
                    g.click() # Acceder al chat
                    print("Id: "+id_subChat + " / Chat: "+ name_subChat + " / Comunidad: "+ name)
                    listaMensajes.append(getMessageGroup(driver, name))
                    listaInfo.append(getInfoChat(driver, id_subChat, name_subChat))
                principal.click() # Acceder al chat principal
                print("Id: "+id_chat + " / Chat: "+ name)
                listaMensajes.append(getMessageGroup(driver, name))
                listaInfo.append(getInfoChat(driver, id_chat, name))
                for i in range(len(listaMensajes)):
                    listaInfo[i].update(listaMensajes[i])    
                prev[0].find_element(By.CSS_SELECTOR, "button[title='Close']").click()    
                return listaInfo  # Lista de diccionarios
            else: #  un grupo / canal
                print("Id: "+ id_chat + " / Chat: "+ name)
                chat = getInfoChat(driver, id_chat, name)
                if chat["type"] == "Channel Info": # Es un canal
                    mensajes = getMessageIndiv(driver, name)
                else: # Es un grupo
                    mensajes = getMessageGroup(driver)
        else: # un usuario/bot
            print("Id: "+ id_chat + " / Chat: "+ name)
            mensajes = getMessageIndiv(driver, name)
            chat = getInfoChat(driver, id_chat, name)
            if chat["status"] == "bot": # Es un bot
                bot = driver.find_elements(By.CSS_SELECTOR, "div[class='tFPZHCMt empty']") 
                if len(bot):  # Descripción de la funcionalidad del bots (primer mensaje)
                    chat["extras"].append("Descripción del bot: " + bot[0].get_attribute('innerText'))
        chat.update(mensajes) # Juntar los dos diccionarios infoChat + Mensajes en uno
        return chat
    return None # No se ha podido acceder al chat indicado
