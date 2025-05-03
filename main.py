import os
import uuid
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Cargar variables de entorno
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BASE_DIR = os.getenv("BASE_DIR", "archivos")
AUTHORIZED_USERS = os.getenv("AUTHORIZED_USERS", "").split(",")

SUBFOLDERS_PER_PAGE = 25

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in AUTHORIZED_USERS:
        await update.message.reply_text("⛔ No estás autorizado para usar este bot.")
        return
    context.user_data["current_path"] = BASE_DIR
    await show_directory(update, context, BASE_DIR, 0)

# Mostrar una carpeta con paginación
async def show_directory(update_or_query, context, folder_path, page=0):
    if isinstance(update_or_query, Update):
        user_id = str(update_or_query.effective_user.id)
    else:
        user_id = str(update_or_query.from_user.id)

    # Guardar el path con un ID
    folder_id = str(uuid.uuid4())[:8]
    context.user_data[folder_id] = folder_path
    context.user_data["current_path"] = folder_path

    subfolders = [f for f in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, f))]
    subfolders.sort()  # Opcional: orden alfabético

    start_index = page * SUBFOLDERS_PER_PAGE
    end_index = start_index + SUBFOLDERS_PER_PAGE
    subfolders_to_show = subfolders[start_index:end_index]

    keyboard = []

    for folder in subfolders_to_show:
        sub_path = os.path.join(folder_path, folder)
        sub_id = str(uuid.uuid4())[:8]
        context.user_data[sub_id] = sub_path
        keyboard.append([InlineKeyboardButton(folder, callback_data=f"BROWSE::{sub_id}")])

    # Paginación
    navigation_buttons = []
    if page > 0:
        navigation_buttons.append(InlineKeyboardButton("◀️ Anterior", callback_data=f"PAGE::{folder_id}::{page-1}"))
    if end_index < len(subfolders):
        navigation_buttons.append(InlineKeyboardButton("Siguiente ▶️", callback_data=f"PAGE::{folder_id}::{page+1}"))

    if navigation_buttons:
        keyboard.append(navigation_buttons)

    # Botón volver a raíz
    if folder_path != BASE_DIR:
        keyboard.append([InlineKeyboardButton("🔙 Volver a la carpeta principal", callback_data=f"BROWSE::ROOT")])

    # Botón seleccionar carpeta
    keyboard.append([InlineKeyboardButton("📂 Seleccionar esta carpeta", callback_data=f"SELECT::{folder_id}")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    text = f"📁 Carpeta: `{os.path.basename(folder_path)}` (Página {page+1})"

    if isinstance(update_or_query, Update):
        await update_or_query.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        await update_or_query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")

# Botones: navegar, paginar, seleccionar
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = str(query.from_user.id)
    if user_id not in AUTHORIZED_USERS:
        await query.answer("⛔ No autorizado.", show_alert=True)
        return

    data = query.data
    if "::" not in data:
        await query.edit_message_text("❌ Acción inválida.")
        return

    action, *params = data.split("::")

    if action == "PAGE":
        folder_id = params[0]
        page = int(params[1])
        folder_path = context.user_data.get(folder_id)
        if not folder_path or not os.path.isdir(folder_path):
            await query.edit_message_text("❌ Carpeta no encontrada.")
            return
        await show_directory(query, context, folder_path, page)

    elif action == "BROWSE":
        if params[0] == "ROOT":
            await show_directory(query, context, BASE_DIR, 0)
        else:
            folder_id = params[0]
            folder_path = context.user_data.get(folder_id)
            if not folder_path or not os.path.isdir(folder_path):
                await query.edit_message_text("❌ Carpeta no encontrada.")
                return
            await show_directory(query, context, folder_path, 0)

    elif action == "SELECT":
        folder_id = params[0]
        folder_path = context.user_data.get(folder_id)
        if not folder_path or not os.path.isdir(folder_path):
            await query.edit_message_text("❌ Carpeta no encontrada.")
            return
        context.user_data["selected_folder"] = folder_path
        await query.edit_message_text(f"✅ Carpeta seleccionada:\n`{folder_path}`", parse_mode="Markdown")

# Subir archivo a carpeta seleccionada
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in AUTHORIZED_USERS:
        await update.message.reply_text("⛔ No estás autorizado.")
        return

    folder = context.user_data.get("selected_folder")
    if not folder:
        await update.message.reply_text("❗ Usa /start para seleccionar una carpeta primero.")
        return

    file = update.message.document or update.message.photo[-1]
    file_name = getattr(file, "file_name", f"{file.file_unique_id}.jpg")
    file_path = os.path.join(folder, file_name)

    os.makedirs(folder, exist_ok=True)
    new_file = await context.bot.get_file(file.file_id)
    await new_file.download_to_drive(file_path)

    await update.message.reply_text(f"✅ Archivo guardado:\n`{file_path}`", parse_mode="Markdown")

# Main
if __name__ == "__main__":
    import asyncio
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, handle_file))

    print("🤖 Bot funcionando correctamente.")
    asyncio.run(app.run_polling())
