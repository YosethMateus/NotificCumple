import mysql.connector
from mysql.connector import Error
from email.message import EmailMessage
import smtplib
from datetime import datetime, date
import time
from dotenv import load_dotenv
import os
from string import Template

# CONSTANTES Y CONFIGURACIONES
# Tiempos
HORA_EJECUCION = 9  # 9 a.m.
INTERVALO_ESPERA = 3600  # 1 hora

# Configuración de la base de datos
load_dotenv() # Cargar variables de entorno desde .env
DB_CONFIG = {
    'user': os.getenv("DB_USER"),
    'password': os.getenv("DB_PASSWORD"),
    'host': os.getenv("DB_HOST"),
    'database': os.getenv("DB_NAME")
}

# Configuración del correo (Gmail)
GMAIL_REMITENTE = os.getenv("GMAIL_REMITENTE")
GMAIL_CLAVE = os.getenv("GMAIL_CLAVE")

# cargar vista HTML
def cargar_vista(nombre):
    with open("markdown.html", "r", encoding="utf-8") as file:
        html_template = Template(file.read())
        return html_template.substitute(nombre=nombre)


# Funcion para enviar correo electrónico
def enviar_correo(destinatario, nombre):
    msg = EmailMessage()
    msg['Subject'] = f"🎉 ¡Feliz cumpleaños, {nombre}!"
    msg['From'] = GMAIL_REMITENTE
    msg['To'] = destinatario
    # Texto plano
    msg.set_content(f"""
Hola {nombre},

¡Te deseamos un feliz cumpleaños! 🎂🎈🎁

Disfruta tu día :)

- Sistema automático
""")

    # Contenido HTML
    html = cargar_vista(nombre)
    msg.add_alternative(html, subtype='html')

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls()
            smtp.login(GMAIL_REMITENTE, GMAIL_CLAVE)
            smtp.send_message(msg)
            print(f"📧 Correo enviado a {nombre} ({destinatario})")
    except Exception as e:
        print("❌ Error al enviar el correo:", e)


def verificar_cumpleaños():
  try:
    conexion = mysql.connector.connect(**DB_CONFIG)
  
    if conexion.is_connected():
      cursor = conexion.cursor()

      sql = " SELECT * FROM personas WHERE MONTH(fecha_cumpleaños) = MONTH(CURDATE()) AND DAY(fecha_cumpleaños) = DAY(CURDATE());"
      cursor.execute(sql)
      resultados = cursor.fetchall()
  
      if resultados:
                print("🎉 Cumpleañeros de hoy:")
                for fila in resultados:
                    nombre = f"{fila[0]} {fila[1]}"
                    correo = fila[4]
                    print(f"🎂 {nombre} - {fila[2]} - {correo}")
                    enviar_correo(correo, nombre)
      else:
          print("🤷‍♂️ No hay cumpleaños hoy.")
  
      cursor.close()
      conexion.close()
  
  
  except Error as e:
      print("❌ Error de MySQL:", e)
  except Exception as ex:
      print("❌ Otro error ocurrió:", ex)


def main():
    ultima_ejecucion = None

    while True:
        ahora = datetime.now()

        if ahora.hour == HORA_EJECUCION and (ultima_ejecucion != date.today()):
            print(f"\n📆 Ejecutando cumpleaños - {ahora.strftime('%Y-%m-%d %H:%M:%S')}")
            verificar_cumpleaños()
            ultima_ejecucion = date.today()
        
        time.sleep(INTERVALO_ESPERA)

# Ejecutar el script
if __name__ == "__main__":
    main()