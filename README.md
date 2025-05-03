
# 🤖 Bot de Telegram para Organizar Archivos en Carpetas del Servidor

Este bot te permite enviar archivos por Telegram y guardarlos automáticamente en una carpeta seleccionada del servidor. Escanea las subcarpetas de una carpeta base y permite elegir una como destino de los archivos.

---

## ✅ Características

- Detecta subcarpetas dentro de una carpeta base del servidor.
- Permite seleccionar la carpeta de destino mediante botones de Telegram.
- Guarda los archivos recibidos en la carpeta seleccionada.
- Soporta documentos e imágenes.
- Configuración segura usando `.env`.

---

## ⚙️ Requisitos

- Python 3.8+
- Cuenta de bot en Telegram (usa [@BotFather](https://t.me/BotFather) para crearla)
- Sistema operativo compatible (Linux, Windows, macOS)

---

## 🚀 Instalación paso a paso

### 1. Clona el repositorio

```bash
git clone https://github.com/Romezzn/ServerDirBot.git
cd bot-archivos-telegram
```

### 2. Crea un entorno virtual (recomendado)

```bash
python3 -m venv venv
source venv/bin/activate      # En Linux/macOS
venv\Scripts\activate       # En Windows
```

### 3. Instala las dependencias

```bash
pip install -r requirements.txt
```

### 4. Crea el archivo `.env` con tus variables de entorno

```env
TELEGRAM_BOT_TOKEN=123456789:ABCDEF-TOKEN-DEL-BOT
BASE_DIR=archivos
ALLOWED_USERS=123456789,987654321
```

> `BASE_DIR` es la carpeta dentro del proyecto donde estarán las subcarpetas destino (por defecto se usará `archivos/`).

### 5. Crea la carpeta base con subcarpetas

```bash
mkdir -p archivos/fotos archivos/docs archivos/otros
```

---

## 📦 Estructura del Proyecto

```
bot-archivos-telegram/
├── archivos/
│   ├── fotos/
│   ├── docs/
│   └── otros/
├── .env
├── bot.py
├── requirements.txt
└── README.md
```

---

## ▶️ Ejecutar el bot

```bash
python bot.py
```

El bot iniciará y responderá al comando `/start` mostrando las carpetas disponibles.

---

## 🧪 Ejemplo de uso

1. Escribe `/start` al bot.
2. Selecciona la carpeta destino desde los botones.
3. Envía archivos (documentos o imágenes).
4. El bot los guardará automáticamente en la carpeta elegida.

---

## 🛠 Dependencias (requirements.txt)

```txt
python-telegram-bot~=20.0
python-dotenv
```

---

