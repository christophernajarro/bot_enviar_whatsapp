from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time
import os

# Configuración
image_path = os.path.abspath('imagen.jpg')
message_path = os.path.abspath('mensaje.txt')
numbers_path = os.path.abspath('numeros.xlsx')
chromedriver_path = "C:/chromedriver/chromedriver.exe"

service = Service(chromedriver_path)
driver = webdriver.Chrome(service=service)

# Leer el mensaje desde el archivo de texto
with open(message_path, 'r') as file:
    msg = file.read().strip()

# Abrir WhatsApp Web
link = 'https://web.whatsapp.com'
driver.get(link)

# Esperar a que el usuario inicie sesión
WebDriverWait(driver, 600).until(
    EC.presence_of_element_located((By.XPATH, '//SPAN[@data-icon="new-chat-outline"]'))
)

# Leer los números desde el archivo XLSX
numeros_df = pd.read_excel(numbers_path)
numeros_exitosos = []
numeros_no_exitosos = []

def enviar_mensajes():
    # Presionar el botón de nuevo chat solo una vez
    new_chat_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//SPAN[@data-icon="new-chat-outline"]'))
    )
    driver.execute_script("arguments[0].click();", new_chat_btn)
    
    for index, row in numeros_df.iterrows():
        num = str(row['Numeros'])  # Convertir a cadena
        try:
            # Buscar el cuadro de búsqueda y limpiar su contenido
            search_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//div[@role="textbox"]'))
            )
            search_box.click()  # Asegurarse de que el cuadro de búsqueda está activo
            search_box.send_keys(Keys.CONTROL, 'a')  # Seleccionar todo el contenido
            search_box.send_keys(Keys.BACKSPACE)  # Borrar todo el contenido
            time.sleep(1)  # Asegurar que el campo esté limpio
            search_box.send_keys(num)
            search_box.send_keys(Keys.ENTER)

            # Esperar 2 segundos antes de verificar si el número no existe
            time.sleep(2)

            # Verificar si el número no existe en WhatsApp
            if len(driver.find_elements(By.XPATH, '//DIV[@class="x1f6kntn x1fc57z9 x40yjcy"]')) > 0:
                numeros_no_exitosos.append(num)
                print(f"{num} no encontrado en WhatsApp")
                search_box.click()
                search_box.send_keys(Keys.CONTROL, 'a')  # Seleccionar todo el contenido
                search_box.send_keys(Keys.BACKSPACE)  # Borrar todo el contenido
                time.sleep(1)  # Añadir un pequeño retraso para asegurar que el campo esté limpio
                continue

            # Verificar si el número existe en WhatsApp
            contact_element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '(//DIV[@class="_ak8l"])[1]'))
            )
            contact_element.click()

            # Adjuntar la imagen si existe
            if image_path:
                attach_btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//div[@title="Adjuntar"]'))
                )
                attach_btn.click()
                
                img_input = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//SPAN[@class="xdod15v xzwifym x6ikm8r x10wlt62 xlyipyv xuxw1ft"][text()="Fotos y videos"]'))
                )
                img_input.click()

                file_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//input[@accept="image/*,video/mp4,video/3gpp,video/quicktime"]'))
                )
                file_input.send_keys(image_path)
                
                send_img_btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//SPAN[@data-icon="send"]'))
                )
                send_img_btn.click()

            # Enviar el mensaje de texto
            msg_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[1]/div[2]/div[1]/p'))
            )
            for line in msg.split('\n'):
                msg_box.send_keys(line)
                msg_box.send_keys(Keys.SHIFT, Keys.ENTER)
            msg_box.send_keys(Keys.ENTER)

            numeros_exitosos.append(num)
            print(f"Mensaje enviado a {num}")

            # Borrar el campo de búsqueda después de enviar el mensaje
            search_box.click()
            search_box.send_keys(Keys.CONTROL, 'a')  # Seleccionar todo el contenido
            search_box.send_keys(Keys.BACKSPACE)  # Borrar todo el contenido
            time.sleep(1)  # Añadir un pequeño retraso para asegurar que el campo esté limpio

        except Exception as e:
            numeros_no_exitosos.append(num)
            print(f"Error al enviar mensaje a {num}: {e}")
            search_box.click()
            search_box.send_keys(Keys.CONTROL, 'a')  # Seleccionar todo el contenido
            search_box.send_keys(Keys.BACKSPACE)  # Borrar todo el contenido
            time.sleep(1)  # Añadir un pequeño retraso para asegurar que el campo esté limpio

enviar_mensajes()
driver.quit()

# Imprimir el resumen
print("\nResumen del envío de mensajes:")
print(f"Números exitosos ({len(numeros_exitosos)}): {', '.join(numeros_exitosos)}")
print(f"Números no exitosos ({len(numeros_no_exitosos)}): {', '.join(numeros_no_exitosos)}")
