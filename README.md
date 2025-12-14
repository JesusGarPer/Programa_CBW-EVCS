# Programa_CBW-EVCS
Programa destinado a la representación visual del trabajo #1 de Criptografía.
# 🔐 CBW-EVCS: Criptografía Visual a Color

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://programacbw-evcs-umsrjfsekma3qcjjqbyalc.streamlit.app/)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![Status](https://img.shields.io/badge/Status-Completado-success)

> **Implementación del esquema de Criptografía Visual Extendida basada en Color (CBW-EVCS) para la protección de imágenes sin computación en el descifrado.**

---

## 🚀 Pruébalo Online

¡No necesitas instalar nada! Accede a la aplicación desplegada en la nube y prueba los algoritmos en tiempo real:

👉 **[Hacer clic aquí para abrir la Web App](https://programacbw-evcs-umsrjfsekma3qcjjqbyalc.streamlit.app/)**

---

## 🖌️ ¿Qué es este proyecto?

Este proyecto es una implementación técnica en **Python** del esquema CBW-EVCS. Permite ocultar una imagen secreta (texto) dividiéndola en varias transparencias a color llamadas "sombras".

* **Sin ordenadores:** El secreto se revela simplemente superponiendo las imágenes (apilamiento físico).
* **Sin sospechas:** Las sombras no son ruido aleatorio; muestran imágenes de cubierta (textos visibles) para no levantar sospechas.
* **Eficiente:** Utiliza el color para reducir el tamaño de las imágenes comparado con métodos tradicionales en blanco y negro.

## 🛠️ Algoritmos Implementados

La herramienta incluye 6 construcciones diferentes según las necesidades de seguridad:

| Construcción | Descripción | Tipo |
| :--- | :--- | :--- |
| **1. Estricta RGB** | Esquema básico con paleta reducida. | (2, 2) |
| **2. RGBCMY** | Mejora el contraste usando colores complementarios. | (2, 2) |
| **3. Alto Contraste** | Usa pares Cian/Rojo para máxima visibilidad. | (2, 2) |
| **4. Segura (2, n)** | Extensión para múltiples participantes. | (2, n) |
| **5. Perfect Black** | Garantiza un negro puro en la reconstrucción. | (2, n) |
| **6. Universal (k, n)** | **El más avanzado.** Permite definir un umbral $k$ de $n$. | (k, n) |

---

## 📸 Capturas de Pantalla

![Vista de la Web](screenshots/image.png)

---

## 💻 Instalación Local

Si prefieres ejecutar el proyecto en tu propio ordenador:

1.  **Clona el repositorio:**
    ```bash
    git clone https://github.com/JesusGarPer/Programa_CBW-EVCS.git
    cd Programa_CBW-EVCS
    ```

2.  **Instala las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Ejecuta la aplicación:**
    ```bash
    streamlit run app_web.py
    ```

## 📂 Estructura del Proyecto

* `app_web.py`: Interfaz gráfica (Frontend con Streamlit).
* `Construcciones/`: Lógica matemática y algoritmos de cifrado.
* `ImagenesCreadas/`: Directorio temporal donde se generan las sombras.

---
