from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import requests
import time
import base64
import json
import os
from datetime import datetime


class AntiCaptchaClient:
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.anti-captcha.com"
    
    def create_task(self, image_base64):
        """Crea una tarea de resolución de CAPTCHA"""
        payload = {
            "clientKey": self.api_key,
            "task": {
                "type": "ImageToTextTask",
                "body": image_base64,
                "case": True,
                "minLength": 5,
                "maxLength": 7
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/createTask",
                json=payload,
                timeout=30
            )
            result = response.json()
            
            if result.get("errorId") == 0:
                return result.get("taskId")
            else:
                print(f"[ERROR] Error al crear tarea: {result.get('errorDescription')}")
                return None
        except Exception as e:
            print(f"[ERROR] Error en petición: {e}")
            return None
    
    def get_task_result(self, task_id, max_wait=60):
        """Obtiene el resultado de una tarea"""
        payload = {
            "clientKey": self.api_key,
            "taskId": task_id
        }
        
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                response = requests.post(
                    f"{self.base_url}/getTaskResult",
                    json=payload,
                    timeout=30
                )
                result = response.json()
                
                if result.get("errorId") == 0:
                    if result.get("status") == "ready":
                        return result.get("solution", {}).get("text")
                    elif result.get("status") == "processing":
                        print("[INFO] CAPTCHA en proceso de resolución...")
                        time.sleep(3)
                    else:
                        return None
                else:
                    print(f"[ERROR] Error: {result.get('errorDescription')}")
                    return None
            except Exception as e:
                print(f"[ERROR] Error al obtener resultado: {e}")
                return None
        
        print("[WARNING] Tiempo de espera agotado")
        return None
    
    def solve_captcha(self, image_base64):
        """Resuelve un CAPTCHA de imagen"""
        print("[INFO] Enviando CAPTCHA a Anti-Captcha...")
        task_id = self.create_task(image_base64)
        
        if not task_id:
            return None
        
        print(f"[INFO] Task ID: {task_id}")
        result = self.get_task_result(task_id)
        
        if result:
            print(f"[SUCCESS] CAPTCHA resuelto: {result}")
        
        return result


class RuntScraperAngular:
    
    def __init__(self, anticaptcha_key):
        self.anticaptcha_client = AntiCaptchaClient(anticaptcha_key)
        self.driver = None
        self.wait = None
        self.base_url = "https://www.runt.gov.co/consultaCiudadana/#/consultaVehiculo"
        
    def iniciar_navegador(self):
        """Inicia el navegador Chrome"""
        try:
            print("[INFO] Iniciando navegador Chrome...")
            
            chrome_options = Options()
            chrome_options.add_argument('--start-maximized')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, 20)
            
            print("[SUCCESS] Navegador iniciado correctamente")
            return True
            
        except Exception as e:
            print(f"[ERROR] Error al iniciar navegador: {e}")
            print("[INFO] Asegúrate de tener ChromeDriver instalado")
            return False
    
    def cargar_pagina(self):
        """Carga la página del RUNT"""
        try:
            print(f"[INFO] Cargando página del RUNT...")
            self.driver.get(self.base_url)
            
            # Esperar que cargue Angular
            time.sleep(5)
            
            print(f"[SUCCESS] Página cargada: {self.driver.title}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Error al cargar página: {e}")
            return False
    
    def seleccionar_procedencia_nacional(self):
        """Selecciona NACIONAL en procedencia"""
        try:
            print("[INFO] Seleccionando Procedencia: NACIONAL...")
            
            # Buscar el mat-select de procedencia
            select_procedencia = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//mat-select[@formcontrolname='procedencia']"))
            )
            select_procedencia.click()
            time.sleep(1)
            
            # Seleccionar opción NACIONAL
            opcion_nacional = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//mat-option//span[contains(text(), 'NACIONAL')]"))
            )
            opcion_nacional.click()
            
            print("  [SUCCESS] NACIONAL seleccionado")
            time.sleep(1)
            return True
            
        except Exception as e:
            print(f"  [ERROR] Error al seleccionar procedencia: {e}")
            return False
    
    def seleccionar_placa_propietario(self):
        """Selecciona 'Placa y Propietario' en tipo de consulta"""
        try:
            print("[INFO] Seleccionando Consulta por: Placa y Propietario...")
            
            # Buscar el mat-select de tipo de consulta
            select_consulta = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//mat-select[@formcontrolname='tipoConsulta']"))
            )
            select_consulta.click()
            time.sleep(1)
            
            # Seleccionar opción "Placa y Propietario"
            opcion_placa = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//mat-option//span[contains(text(), 'Placa y Propietario')]"))
            )
            opcion_placa.click()
            
            print("  [SUCCESS] Placa y Propietario seleccionado")
            time.sleep(1)
            return True
            
        except Exception as e:
            print(f"  [ERROR] Error al seleccionar tipo de consulta: {e}")
            return False
    
    def ingresar_placa(self, placa):
        """Ingresa el número de placa"""
        try:
            print(f"[INFO] Ingresando placa: {placa}")
            
            # Buscar el input de placa
            input_placa = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@formcontrolname='placa']"))
            )
            input_placa.clear()
            input_placa.send_keys(placa.upper())
            
            print("  [SUCCESS] Placa ingresada")
            time.sleep(1)
            return True
            
        except Exception as e:
            print(f"  [ERROR] Error al ingresar placa: {e}")
            return False
    
    def seleccionar_cedula_ciudadania(self):
        """Selecciona 'Cédula Ciudadanía' en tipo de documento"""
        try:
            print("[INFO] Seleccionando Tipo de Documento: Cédula Ciudadanía...")
            
            # Buscar el mat-select de tipo de documento
            select_documento = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//mat-select[@formcontrolname='tipoDocumento']"))
            )
            select_documento.click()
            time.sleep(1)
            
            # Seleccionar opción "Cédula Ciudadanía"
            opcion_cc = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//mat-option//span[contains(text(), 'Cédula Ciudadanía')]"))
            )
            opcion_cc.click()
            
            print("  [SUCCESS] Cédula Ciudadanía seleccionada")
            time.sleep(1)
            return True
            
        except Exception as e:
            print(f"  [ERROR] Error al seleccionar tipo de documento: {e}")
            return False
    
    def ingresar_documento(self, numero_documento):
        """Ingresa el número de documento"""
        try:
            print(f"[INFO] Ingresando número de documento: {numero_documento}")
            
            # Buscar el input de documento
            input_documento = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@formcontrolname='documento']"))
            )
            input_documento.clear()
            input_documento.send_keys(numero_documento)
            
            print("  [SUCCESS] Número de documento ingresado")
            time.sleep(1)
            return True
            
        except Exception as e:
            print(f"  [ERROR] Error al ingresar documento: {e}")
            return False
    
    def capturar_captcha(self):
        """Captura la imagen del CAPTCHA"""
        try:
            print("[INFO] Capturando CAPTCHA...")
            
            # Buscar la imagen del CAPTCHA
            captcha_img = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'ng-star-inserted')]//img"))
            )
            
            # Capturar screenshot del CAPTCHA
            captcha_png = captcha_img.screenshot_as_png
            captcha_base64 = base64.b64encode(captcha_png).decode('utf-8')
            
            print("  [SUCCESS] CAPTCHA capturado")
            return captcha_base64
            
        except Exception as e:
            print(f"  [ERROR] Error al capturar CAPTCHA: {e}")
            return None
    
    def ingresar_captcha(self, captcha_text):
        """Ingresa el texto del CAPTCHA resuelto"""
        try:
            print(f"[INFO] Ingresando CAPTCHA: {captcha_text}")
            
            # Buscar el input del CAPTCHA
            input_captcha = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@formcontrolname='captcha']"))
            )
            input_captcha.clear()
            input_captcha.send_keys(captcha_text)
            
            print("  [SUCCESS] CAPTCHA ingresado")
            time.sleep(1)
            return True
            
        except Exception as e:
            print(f"  [ERROR] Error al ingresar CAPTCHA: {e}")
            return False
    
    def enviar_formulario(self):
        """Envía el formulario"""
        try:
            print("[INFO] Enviando formulario...")
            
            # Buscar y hacer clic en el botón de consultar
            boton_consultar = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Consultar') or @type='submit']"))
            )
            boton_consultar.click()
            
            print("  [SUCCESS] Formulario enviado")
            time.sleep(5)
            return True
            
        except Exception as e:
            print(f"  [ERROR] Error al enviar formulario: {e}")
            return False
    
    def verificar_error_captcha(self):
        """Verifica si hay error en el CAPTCHA"""
        try:
            # Buscar mensajes de error
            error_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'captcha') or contains(text(), 'incorrecto')]")
            if error_elements:
                return True
            return False
        except:
            return False
    
    def extraer_resultados(self):
        """Extrae solo los resultados principales del vehículo"""
        try:
            print("[INFO] Extrayendo resultados del vehículo...")
            
            # Esperar a que aparezcan los resultados
            time.sleep(5)
            
            # SOLO CAMPOS PRINCIPALES
            vehicle_data = {
                'placa': None,
                'tipo_servicio': None,
                'clase_vehiculo': None,
                'estado_vehiculo': None,
                'marca': None,
                'gravamenes': None,
                # Solo la fecha de fin de vigencia del SOAT
                'soat_fecha_fin_vigencia': None,
                'fecha_consulta': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Obtener todo el texto visible de la página
            print("  [INFO] Analizando texto de la página...")
            body_text = self.driver.find_element(By.TAG_NAME, "body").text
            
            # Dividir en líneas para procesar
            lineas = body_text.split('\n')
            
            # Función para buscar el valor después de un label
            def buscar_valor(etiqueta, lineas_despues=3):
                for i, linea in enumerate(lineas):
                    if etiqueta.upper() in linea.upper():
                        # Buscar en las siguientes líneas
                        for j in range(1, lineas_despues + 1):
                            if i + j < len(lineas):
                                valor = lineas[i + j].strip()
                                if valor and valor.upper() != etiqueta.upper() and len(valor) > 0:
                                    return valor
                return None
            
            # Extraer SOLO los campos principales
            print("  [INFO] Extrayendo campos principales...")
            
            vehicle_data['placa'] = buscar_valor('PLACA DEL VEHÍCULO')
            vehicle_data['tipo_servicio'] = buscar_valor('TIPO DE SERVICIO')
            vehicle_data['estado_vehiculo'] = buscar_valor('ESTADO DEL VEHÍCULO')
            vehicle_data['clase_vehiculo'] = buscar_valor('CLASE DE VEHÍCULO')
            vehicle_data['marca'] = buscar_valor('MARCA')
            vehicle_data['gravamenes'] = buscar_valor('GRAVAMENES A LA PROPIEDAD')
            
            # Extraer datos completos del SOAT
            print("  [INFO] Buscando panel de Póliza SOAT...")
            try:
                # Buscar el panel de Póliza SOAT de diferentes formas
                time.sleep(2)
                
                # Intentar varios selectores
                panel_encontrado = False
                
                # Intento 1: Por el texto "Póliza SOAT"
                try:
                    panel_soat = self.driver.find_element(
                        By.XPATH, 
                        "//mat-expansion-panel-header[contains(., 'Póliza SOAT')]"
                    )
                    panel_encontrado = True
                    print("  [SUCCESS] Panel encontrado (método 1)")
                except:
                    pass
                
                # Intento 2: Por el icono credit_card
                if not panel_encontrado:
                    try:
                        panel_soat = self.driver.find_element(
                            By.XPATH, 
                            "//mat-icon[text()='credit_card']/ancestor::mat-expansion-panel-header"
                        )
                        panel_encontrado = True
                        print("  [SUCCESS] Panel encontrado (método 2)")
                    except:
                        pass
                
                # Intento 3: Por la clase
                if not panel_encontrado:
                    try:
                        panel_soat = self.driver.find_element(
                            By.XPATH,
                            "//mat-expansion-panel-header[.//mat-panel-title[contains(text(), 'SOAT')]]"
                        )
                        panel_encontrado = True
                        print("  [SUCCESS] Panel encontrado (método 3)")
                    except:
                        pass
                
                if not panel_encontrado:
                    print("  [ERROR] No se pudo encontrar el panel de Póliza SOAT")
                    raise Exception("Panel no encontrado")
                
                # Verificar si el panel está expandido
                aria_expanded = panel_soat.get_attribute('aria-expanded')
                print(f"  [INFO] Estado del panel - aria-expanded: {aria_expanded}")
                
                if aria_expanded == 'false' or aria_expanded is None:
                    print("  [INFO] Haciendo clic en el panel para expandirlo...")
                    
                    # Scroll al elemento para asegurar que esté visible
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", panel_soat)
                    time.sleep(1)
                    
                    # Hacer clic usando JavaScript como alternativa
                    self.driver.execute_script("arguments[0].click();", panel_soat)
                    print("  [INFO] Clic ejecutado, esperando que se expanda...")
                    time.sleep(3)
                else:
                    print("  [INFO] Panel ya está expandido")
                
                # Esperar a que aparezca la tabla
                print("  [INFO] Esperando que cargue la tabla del SOAT...")
                time.sleep(2)
                
                # Extraer datos del SOAT desde el mat-card
                print("  [INFO] Extrayendo fecha de fin de vigencia del SOAT...")
                
                try:
                    # Buscar el mat-card de Póliza SOAT
                    soat_card = self.driver.find_element(
                        By.XPATH,
                        "//mat-card[.//mat-card-title[contains(text(), 'Póliza SOAT')]]"
                    )
                    
                    print("  [SUCCESS] mat-card de SOAT encontrado")
                    
                    # Obtener todo el texto del card
                    card_text = soat_card.text
                    lineas_soat = card_text.split('\n')
                    
                    # Función para extraer valor después de un label
                    def extraer_valor_soat(etiqueta):
                        for linea in lineas_soat:
                            if etiqueta in linea:
                                # Dividir por el label y tomar la parte después
                                partes = linea.split(etiqueta)
                                if len(partes) > 1:
                                    valor = partes[1].strip()
                                    # Limpiar caracteres especiales
                                    valor = valor.replace(':', '').strip()
                                    return valor if valor else None
                        return None
                    
                    # Extraer SOLO la fecha de fin de vigencia
                    fecha_fin = extraer_valor_soat('Fecha fin de vigencia:')
                    
                    # Guardar en vehicle_data
                    vehicle_data['soat_fecha_fin_vigencia'] = fecha_fin
                    
                    if fecha_fin:
                        print(f"  [SUCCESS] ✓ Fecha fin de vigencia SOAT: {fecha_fin}")
                    else:
                        print("  [WARNING] No se encontró la fecha de fin de vigencia")
                    
                except Exception as e:
                    print(f"  [ERROR] No se pudo extraer fecha del SOAT: {e}")
                    import traceback
                    traceback.print_exc()
                    
            except Exception as e:
                print(f"  [ERROR] No se pudo extraer datos del SOAT: {e}")
                import traceback
                traceback.print_exc()
            
            # Contar cuántos campos se llenaron
            campos_llenos = sum(1 for v in vehicle_data.values() if v is not None and v != '' and v != 'None')
            print(f"  [SUCCESS] {campos_llenos} campos extraídos exitosamente")
            
            return vehicle_data
            
        except Exception as e:
            print(f"[ERROR] Error al extraer resultados: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def consultar_vehiculo(self, placa, numero_documento, max_intentos=3):
        """
        Realiza la consulta completa del vehículo
        
        Args:
            placa (str): Número de placa (ej: "OUG59H")
            numero_documento (str): Número de documento (ej: "1043641484")
            max_intentos (int): Número máximo de intentos
        """
        print("\n" + "="*70)
        print("SCRAPER RUNT - Consulta Vehicular Automatizada (Versión Simplificada)")
        print("="*70)
        print(f"Placa: {placa}")
        print(f"Documento: {numero_documento}")
        print(f"Anti-Captcha: Configurado")
        print("="*70 + "\n")
        
        # Iniciar navegador
        if not self.iniciar_navegador():
            return None
        
        try:
            for intento in range(1, max_intentos + 1):
                print(f"\n{'='*70}")
                print(f"INTENTO {intento} de {max_intentos}")
                print(f"{'='*70}\n")
                
                # 1. Cargar página
                if not self.cargar_pagina():
                    continue
                
                # 2. Seleccionar Procedencia: NACIONAL
                if not self.seleccionar_procedencia_nacional():
                    continue
                
                # 3. Seleccionar Consulta por: Placa y Propietario
                if not self.seleccionar_placa_propietario():
                    continue
                
                # 4. Ingresar número de placa
                if not self.ingresar_placa(placa):
                    continue
                
                # 5. Seleccionar Tipo de Documento: Cédula Ciudadanía
                if not self.seleccionar_cedula_ciudadania():
                    continue
                
                # 6. Ingresar número de documento
                if not self.ingresar_documento(numero_documento):
                    continue
                
                # 7. Capturar CAPTCHA
                captcha_base64 = self.capturar_captcha()
                if not captcha_base64:
                    print("[WARNING] Esperando 3 segundos...")
                    time.sleep(3)
                    continue
                
                # 8. Resolver CAPTCHA con Anti-Captcha
                captcha_text = self.anticaptcha_client.solve_captcha(captcha_base64)
                if not captcha_text:
                    print("[WARNING] Esperando 5 segundos...")
                    time.sleep(5)
                    continue
                
                # 9. Ingresar CAPTCHA resuelto
                if not self.ingresar_captcha(captcha_text):
                    continue
                
                # 10. Enviar formulario
                if not self.enviar_formulario():
                    continue
                
                # 11. Verificar si hubo error de CAPTCHA
                if self.verificar_error_captcha():
                    print("[WARNING] CAPTCHA incorrecto, reintentando...")
                    time.sleep(2)
                    continue
                
                # 12. Extraer resultados
                resultados = self.extraer_resultados()
                
                if resultados:
                    # Limpiar datos antes de mostrar
                    resultados_limpios = {k: v for k, v in resultados.items() if v is not None and v != '' and v != 'None'}
                    
                    if len(resultados_limpios) > 1:  # Más de 1 porque fecha_consulta siempre existe
                        print("\n" + "="*70)
                        print("CONSULTA EXITOSA!")
                        print("="*70)
                        
                        # Mostrar resultados
                        self.mostrar_resultados(resultados_limpios)
                        
                        # Guardar en archivo JSON
                        self.guardar_resultado(resultados)
                        
                        # Pausa para ver resultados
                        print("\n[INFO] El navegador permanecerá abierto para que veas los resultados...")
                        print("[INFO] Presiona Enter cuando termines de revisar...")
                        input()
                        
                        return resultados
                    else:
                        print("[WARNING] No se extrajeron datos suficientes, reintentando...")
                        time.sleep(2)
                        continue
                else:
                    print("[WARNING] No se pudieron extraer resultados, reintentando...")
                    time.sleep(2)
                    continue
            
            print("\n[ERROR] No se pudo completar la consulta después de todos los intentos")
            print("\n[INFO] Presiona Enter para cerrar el navegador...")
            input()
            return None
            
        except KeyboardInterrupt:
            print("\n\n[WARNING] Proceso interrumpido por el usuario")
            return None
        finally:
            self.cerrar_navegador()
    
    def mostrar_resultados(self, vehicle_data):
        """Muestra los resultados en consola"""
        print("\nDATOS DEL VEHÍCULO:")
        print("-" * 70)
        for key, value in vehicle_data.items():
            if value and key not in ['html_completo']:
                print(f"  {key.upper():20s}: {value}")
        print("-" * 70)
    
    def guardar_resultado(self, vehicle_data, archivo_json='resultados_runt.json'):
        """Guarda el resultado en archivo JSON"""
        try:
            # Limpiar datos: eliminar campos vacíos o None
            datos_limpios = {k: v for k, v in vehicle_data.items() if v is not None and v != '' and v != 'None'}
            
            # Leer resultados existentes
            resultados_json = []
            try:
                with open(archivo_json, 'r', encoding='utf-8') as f:
                    resultados_json = json.load(f)
            except:
                resultados_json = []
            
            # Verificar si ya existe este registro (por placa)
            placa_actual = datos_limpios.get('placa')
            if placa_actual:
                # Eliminar registros duplicados de la misma placa
                resultados_json = [r for r in resultados_json if r.get('placa') != placa_actual]
            
            # Agregar nuevo resultado
            resultados_json.append(datos_limpios)
            
            # Guardar JSON
            with open(archivo_json, 'w', encoding='utf-8') as f:
                json.dump(resultados_json, f, ensure_ascii=False, indent=2)
            
            print(f"[SUCCESS] JSON guardado en: {archivo_json}")
            
        except Exception as e:
            print(f"[ERROR] Error al guardar: {e}")
    
    def cerrar_navegador(self):
        """Cierra el navegador"""
        if self.driver:
            print("\n[INFO] Cerrando navegador...")
            self.driver.quit()
            print("[SUCCESS] Navegador cerrado")


def main():
    """Función principal"""
    
    # Configuración
    ANTICAPTCHA_KEY = "d057f1ebb8c4334baf6441dffb519a10"
    
    # Datos de consulta
    PLACA = "OUG59H"
    NUMERO_DOCUMENTO = "1043641484"
    
    # Crear scraper
    scraper = RuntScraperAngular(ANTICAPTCHA_KEY)
    
    # Realizar consulta
    resultado = scraper.consultar_vehiculo(
        placa=PLACA,
        numero_documento=NUMERO_DOCUMENTO
    )
    
    if resultado:
        print("\n[SUCCESS] Proceso completado exitosamente!")
    else:
        print("\n[ERROR] No se completó la consulta")


if __name__ == "__main__":
    main()