import os
import base64
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# Cargar variables desde .env
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BASE_DIR = os.getenv("BASE_DIR", "archivos")
AUTHORIZED_USERS = os.getenv("AUTHORIZED_USERS", "").split(",")  # IDs separados por coma

# Diccionario para guardar carpetas seleccionadas por usuario
user_selected_folder = {}

# Funciones para codificar/decodificar rutas
def encode_path(path: str) -> str:
    return base64.urlsafe_b64encode(path.encode()).decode()

def decode_path(encoded: str) -> str:
    return base64.urlsafe_b64decode(encoded.encode()).decode()

# Mostrar las carpetas como botones
async def show_folders(query, context, path=BASE_DIR):
    folders = [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]
    keyboard = []

    # Botón para seleccionar esta carpeta
    encoded = encode_path(path)
    keyboard.append([InlineKeyboardButton("📁 Seleccionar esta carpeta", callback_data=f"SELECT::{encoded}")])

    # Subcarpetas
    for f in folders:
        subpath = os.path.join(path, f)
        encoded_subpath = encode_path(subpath)
        keyboard.append([InlineKeyboardButton(f, callback_data=f"FOLDER::{encoded_subpath}")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Selecciona una subcarpeta o esta carpeta:", reply_markup=reply_markup)

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in AUTHORIZED_USERS:
        return  # Usuario no autorizado

    folders = [f for f in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, f))]
    keyboard = [[InlineKeyboardButton(f, callback_data=f"FOLDER::{encode_path(os.path.join(BASE_DIR, f))}")] for f in folders]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Selecciona la carpeta de destino para los archivos:", reply_markup=reply_markup)

# Botón pulsado
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = str(query.from_user.id)
    if user_id not in AUTHORIZED_USERS:
        await query.answer("No estás autorizado para usar este bot.")
        return

    await query.answer()
    data = query.data

    if data.startswith("FOLDER::"):
        encoded = data.split("FOLDER::")[1]
        path = decode_path(encoded)
        await show_folders(query, context, path)

    elif data.startswith("SELECT::"):
        encoded = data.split("SELECT::")[1]
        selected_path = decode_path(encoded)
        user_selected_folder[int(user_id)] = selected_path
        await query.edit_message_text(f"Has seleccionado: /{selected_path}")

# Recepción de archivos
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if str(user_id) not in AUTHORIZED_USERS:
        return  # Usuario no autorizado

    folder = user_selected_folder.get(user_id)
    if not folder:
        await update.message.reply_text("Por favor, selecciona una carpeta primero con /start")
        return

    file = update.message.document or update.message.photo[-1]
    file_name = getattr(file, "file_name", f"{file.file_unique_id}.jpg")
    file_path = os.path.join(folder, file_name)

    new_file = await context.bot.get_file(file.file_id)
    await new_file.download_to_drive(file_path)

    await update.message.reply_text(f"Archivo guardado en:\n📁 /{folder}/{file_name}")

# Main
if __name__ == "__main__":
    import asyncio

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, handle_document))

    print("Bot corriendo...")
    asyncio.run(app.run_polling())
