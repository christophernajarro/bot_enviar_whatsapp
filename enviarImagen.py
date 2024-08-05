from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import os

# Configuración
login_time = 30                 # Tiempo para el login (en segundos)
new_msg_time = 10               # Tiempo para un nuevo mensaje (en segundos)
send_msg_time = 10              # Tiempo para enviar un mensaje (en segundos)
action_time = 2                 # Tiempo para acciones de clic en botones
image_path = os.path.abspath('imagen.jpg')       # Ruta a la imagen
numbers_path = os.path.abspath('numeros.xlsx')   # Ruta al archivo de números

# Configuración del servicio usando webdriver_manager
service = Service(ChromeDriverManager().install())

# Crear el driver
driver = webdriver.Chrome(service=service)

# Abrir WhatsApp Web
link = 'https://web.whatsapp.com'
driver.get(link)
time.sleep(login_time)  # Tiempo para escanear el código QR

# Leer los números desde el archivo XLSX
numeros_df = pd.read_excel(numbers_path)

# Listas para registrar los números exitosos y no exitosos
numeros_exitosos = []
numeros_no_exitosos = []

# Función para enviar mensajes
def enviar_mensajes():
    for index, row in numeros_df.iterrows():
        num = row['Numeros']  # Asegúrate de que la columna se llama 'Numeros'
        link = f'https://web.whatsapp.com/send/?phone={num}'
        driver.get(link)
        time.sleep(new_msg_time)

        try:
            # Verificar si el número tiene cuenta de WhatsApp
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//div[@role="textbox"][@spellcheck="true"][@contenteditable="true"]'))
            )

            # Adjuntar la imagen
            if image_path:
                attach_btn = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.XPATH, '//div[@title="Adjuntar"]'))
                )
                attach_btn.click()
                time.sleep(action_time)
                
                img_input = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, '//input[@accept="image/*,video/mp4,video/3gpp,video/quicktime"]'))
                )
                img_input.send_keys(image_path)
                time.sleep(action_time)
                
                # Esperar a que el botón de enviar imagen esté disponible
                send_img_btn = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.XPATH, '//span[@data-icon="send"]'))
                )
                send_img_btn.click()
                time.sleep(send_msg_time)

            numeros_exitosos.append(num)
            print(f"Imagen enviada a {num}")

        except Exception as e:
            numeros_no_exitosos.append(num)
            print(f"Error al enviar imagen a {num}: {e}")

# Ejecutar la función
enviar_mensajes()

# Cerrar el navegador
driver.quit()

# Imprimir el resumen
print("\nResumen del envío de imágenes:")
print(f"Números exitosos ({len(numeros_exitosos)}): {', '.join(map(str, numeros_exitosos))}")
print(f"Números no exitosos ({len(numeros_no_exitosos)}): {', '.join(map(str, numeros_no_exitosos))}")
