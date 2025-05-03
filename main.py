import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# Cargar variables desde .env
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BASE_DIR = os.getenv("BASE_DIR", "archivos")

# Diccionario para guardar carpetas seleccionadas por usuario
user_selected_folder = {}

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    folders = [f for f in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, f))]
    keyboard = [[InlineKeyboardButton(f, callback_data=f)] for f in folders]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Selecciona la carpeta de destino para los archivos:", reply_markup=reply_markup)

# Selección de carpeta
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    folder = query.data
    user_id = query.from_user.id
    user_selected_folder[user_id] = folder
    await query.answer()
    await query.edit_message_text(f"Has seleccionado la carpeta: {folder}")

# Recepción de archivos
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    folder = user_selected_folder.get(user_id)

    if not folder:
        await update.message.reply_text("Por favor, selecciona una carpeta primero con /start")
        return

    file = update.message.document or update.message.photo[-1]
    file_name = getattr(file, "file_name", f"{file.file_unique_id}.jpg")
    file_path = os.path.join(BASE_DIR, folder, file_name)

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
