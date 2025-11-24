#  Presentado por:
#  Alexandre Vega Paternina
#  Luis Arrieta Aguirre
#  César Contreras Colon

#  RUNT Scraper Automatizado con Python y Selenium

Este proyecto automatiza la consulta de datos vehiculares en el portal oficial del RUNT Colombia, utilizando Selenium, resolución automática de CAPTCHA con Anti-Captcha y técnicas de extracción de datos desde páginas basadas en Angular Material.

Permite ingresar una placa y un número de documento, resolver el CAPTCHA automáticamente y obtener información clave del vehículo, como:

* Placa
* Tipo de servicio
* Clase del vehículo
* Estado del vehículo
* Marca
* Gravámenes
* Fecha fin de vigencia del SOAT
* Fecha de consulta

Los resultados se almacenan automáticamente en un archivo JSON (`resultados_runt.json`) el cual se crea una vez finalizada la ejecución del código.

---

## Estructura del Proyecto

```
.vscode/
│
├── settings.json            # Variables opcionales
---
scraper/
│
├── scraper_runt.py          # Código principal del scraper
├── config.json              # Configuración del proyecto
├── resultados_runt.json     # Archivo donde se guardan las consultas
```
└── requirements.txt         # Dependencias del proyecto

---

## Requisitos

Antes de ejecutar el proyecto debe tener instalado:

* Python 3.10 o superior
* Google Chrome
* ChromeDriver (se instala automáticamente con webdriver_manager)

---

## Instalación de dependencias

Se ejecuta en la consola el siguiente comando:

pip install -r requirements.txt
```

Esto instalará:

* selenium
* requests
* webdriver-manager
* python-dateutil

---

## Configuración

El scraper requiere una API Key de Anti-Captcha para resolver los CAPTCHAs del RUNT automáticamente.

Aquí puede registrarse para obtener su key:
https://anti-captcha.com/

Luego va a scraper_runt.py y reemplaza:

ANTICAPTCHA_KEY = "TU_API_KEY_AQUI"

## Ejecución del Scraper

Para ejecutar el programa basta con correr:

```
py .\scraper\scraper_runt.py


o en su defecto darle a RUN
```

Fases del script:

1. Abre Google Chrome de forma automatizada
2. Ingresa a la página del RUNT
3. Selecciona las opciones del formulario
4. Ingresa placa y documento
5. Captura el CAPTCHA
6. Lo envía a Anti-Captcha
7. Ingresa la solución
8. Extrae los resultados
9. Los guarda en `resultados_runt.json`
10. Muestra los datos en pantalla

---

## ¿Qué hace cada parte del código?

### AntiCaptchaClient

Clase encargada de:

* Enviar la imagen del CAPTCHA a Anti-Captcha
* Solicitar la solución
* Devolver el texto resuelto

---

### 🧰 RuntScraperAngular

Clase principal del scraper. Contiene:

* Inicio del navegador
* Carga de la página
* Selección de opciones del formulario
* Entrada de placa y documento
* Captura y resolución del CAPTCHA
* Extracción de los resultados
* Guardado en JSON

---

### 📄 main()

Función principal que:

* Define la placa y documento
* Crea el scraper
* Llama a la consulta
* Imprime el resultado final

---

## Resultados

Los datos se guardan automáticamente en:

```
resultados_runt.json
```

Ejemplo:

```json
{
  "placa": "OUG59H",
  "tipo_servicio": "PARTICULAR",
  "clase_vehiculo": "AUTOMÓVIL",
  "estado_vehiculo": "ACTIVO",
  "marca": "RENAULT",
  "gravamenes": "SIN GRAVÁMENES",
  "soat_fecha_fin_vigencia": "2025-03-14",
  "fecha_consulta": "2025-10-21 14:55:12"
}
```

---

## 🧪 Características Destacadas

* Compatible con Angular Material (métodos extra robustos de espera)
* Evita fallos típicos del DOM dinámico
* Resuelve CAPTCHA automático
* Guarda datos sin duplicar placas
* Reintenta automáticamente si falla el CAPTCHA
* Navegador visible para revisar resultados

---

## 🛑 Posibles Errores Comunes

| Problema           | Solución                                  |
| ------------------ | ----------------------------------------- |
| No abre Chrome     | Actualizar Chrome o webdriver-manager     |
| CAPTCHA incorrecto | Aumentar créditos Anti-Captcha            |
| Página no carga    | Internet lento, aumentar tiempo de espera |
| JSON no guarda     | Verificar permisos de escritura           |
