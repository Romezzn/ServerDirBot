import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# Cargar variables desde .env
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BASE_DIR = os.getenv("BASE_DIR", "archivos")
ALLOWED_USERS = set(map(int, os.getenv("ALLOWED_USERS", "").split(",")))

# Diccionario para guardar carpeta seleccionada por usuario
user_selected_folder = {}

# Verificación de usuario autorizado
def is_authorized(user_id: int) -> bool:
    return user_id in ALLOWED_USERS

# Mostrar carpetas/subcarpetas
async def show_folders(update: Update, context: ContextTypes.DEFAULT_TYPE, path=""):
    base_path = os.path.join(BASE_DIR, path)
    folders = [f for f in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, f))]

    keyboard = []

    if path:  # Agregar botón "Seleccionar esta carpeta" si no estamos en la raíz
        keyboard.append([InlineKeyboardButton("📁 Seleccionar esta carpeta", callback_data=f"SELECT::{path}")])

    for f in folders:
        new_path = os.path.join(path, f).replace("\\", "/")
        keyboard.append([InlineKeyboardButton(f, callback_data=f"FOLDER::{new_path}")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Selecciona una carpeta:", reply_markup=reply_markup)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    await show_folders(update, context)

# Manejo de botones
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if not is_authorized(user_id):
        await query.answer("No tienes permisos para usar este bot.", show_alert=True)
        return

    data = query.data
    if data.startswith("FOLDER::"):
        path = data.split("FOLDER::")[1]
        # Mostrar subcarpetas
        await show_folders(query, context, path)
    elif data.startswith("SELECT::"):
        selected_path = data.split("SELECT::")[1]
        user_selected_folder[user_id] = selected_path
        await query.edit_message_text(f"Has seleccionado: /{selected_path}")

# Manejo de documentos/imágenes
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        return

    folder = user_selected_folder.get(user_id)
    if not folder:
        await update.message.reply_text("Primero selecciona una carpeta con /start")
        return

    file = update.message.document or update.message.photo[-1]
    file_name = getattr(file, "file_name", f"{file.file_unique_id}.jpg")
    file_path = os.path.join(BASE_DIR, folder, file_name)

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    new_file = await context.bot.get_file(file.file_id)
    await new_file.download_to_drive(file_path)

    await update.message.reply_text(f"Archivo guardado en /{folder}/{file_name}")

# Main
if __name__ == "__main__":
    import asyncio

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, handle_document))

    print("Bot corriendo...")
    asyncio.run(app.run_polling())
