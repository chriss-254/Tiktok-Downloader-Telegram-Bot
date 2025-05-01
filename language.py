"""
Language support module for TikTok Downloader Bot.
This module handles translations for all bot messages.
"""

# Dictionary to store all available languages
AVAILABLE_LANGUAGES = {
    "en": "English",
    "es": "Español",
    "fr": "Français",
    "pt": "Português",
    "ru": "Русский",
    "ar": "العربية",
    "zh": "中文",
    "hi": "हिन्दी",
    "sw": "Kiswahili",
    "tr": "Türkçe",
}

# Default language
DEFAULT_LANGUAGE = "en"

# Store all translations in nested dictionaries
# Structure: translations[language_code][message_key]
translations = {
    # English translations (default)
    "en": {
        # Start command messages
        "welcome_message": "Hi 👋 {first_name}, Welcome to Tiktok Downloader!\n\nHow to use :\n\nJust send the video link and I will download without watermark 🤙",
        "admin_set": "👑 You have been set as the admin!",
        
        # TikTok download messages
        "cooldown_message": "⏳ Please wait {seconds} seconds before requesting another video.",
        "invalid_tiktok_url": "❌Invalid TikTok URL. Make sure you're sending a video link.\n✔️Or Try On This Site\n💥tiktokdownloaderhd.com",
        "no_tiktok_url": "No valid TikTok URL found. Please check the link and try again.",
        "downloading_message": "📥 Downloading... Please wait.",
        "download_complete": "✅ Download Complete!\n⚡Powered By :\n💥tiktokdownloaderhd.com",
        "download_error": "❌ Error Downloading The Video. Please Try Again.\n✔️Or Try On This Site\n💥tiktokdownloaderhd.com",
        "video_details_error": "❌ Error Retrieving Video Details. Please Try Again Later.\n✔️Or Try On This Site\n💥tiktokdownloaderhd.com",
        
        # Admin command messages
        "no_permission": "❌ You don't have permission to use this command.",
        "no_users": "No users have used the bot yet.",
        "user_stats": "📊 Total users: {total}\n🌍 Users who used today: {today}\n\n📋 List:\n\n",
        "user_entry": "👤 ID: {user_id}\n   Username: @{username}\n   Name: {first_name}\n   Last Active: {timestamp}\n\n",
        "no_log_file": "No log file found.",
        "user_data_error": "⚠️ Error retrieving user data.",
        
        # Callback messages
        "reels_coming_soon": "Coming Soon 🚀\n\nWe're working on adding Reels Downloader functionality. Stay tuned!",
        
        # Button text
        "source_video_button": "Source Video",
        "check_channel_button": "Check Channel",
        "all_in_1_button": "All In 1 Downloader",
        
        # Help command
        "help_text": """
📚 **Bot Commands & Usage Guide** 📚

🔹 **Basic Commands**:
/start - Start the bot
/help - Show this help message
/language - Change language

🔽 **TikTok Download**:
Simply send any TikTok video link, and I'll download it without watermark!

⏱ Please wait 10 seconds between downloads.

🔹 **For Admins Only**:
/users - View user statistics
/broadcast - Send message to all users

📢 **Broadcasting**:
Use in these ways:
1. `/broadcast Your message here` - Send text message
2. Reply to any message with `/broadcast` - Forward that message
3. Reply to photo/video with `/broadcast` - Send that media

💡 For buttons in broadcast, use:
```
/broadcast Your message
--btn--Button Text|https://example.com
--btn--Second Button|https://example.com
```

Need more help? Contact: @your_support_username
        """,
        
        # Language command
        "language_selection": "🌐 Please select your preferred language:",
        "language_changed": "✅ Language changed to {language_name}!",
    },
    
    # Spanish translations
    "es": {
        # Start command messages
        "welcome_message": "¡Hola 👋 {first_name}, Bienvenido a Tiktok Downloader!\n\nCómo usar:\n\nSolo envía el enlace del video y lo descargaré sin marca de agua 🤙",
        "admin_set": "👑 ¡Has sido establecido como administrador!",
        
        # TikTok download messages
        "cooldown_message": "⏳ Por favor, espera {seconds} segundos antes de solicitar otro video.",
        "invalid_tiktok_url": "❌URL de TikTok no válida. Asegúrate de enviar un enlace de video.\n✔️O prueba en este sitio\n💥tiktokdownloaderhd.com",
        "no_tiktok_url": "No se encontró una URL de TikTok válida. Por favor revisa el enlace y vuelve a intentarlo.",
        "downloading_message": "📥 Descargando... Por favor, espera.",
        "download_complete": "✅ ¡Descarga Completa!\n⚡Desarrollado por:\n💥tiktokdownloaderhd.com",
        "download_error": "❌ Error al descargar el video. Por favor intenta de nuevo.\n✔️O prueba en este sitio\n💥tiktokdownloaderhd.com",
        "video_details_error": "❌ Error al recuperar los detalles del video. Por favor, intenta más tarde.\n✔️O prueba en este sitio\n💥tiktokdownloaderhd.com",
        
        # Admin command messages
        "no_permission": "❌ No tienes permiso para usar este comando.",
        "no_users": "Ningún usuario ha utilizado el bot aún.",
        "user_stats": "📊 Total de usuarios: {total}\n🌍 Usuarios que lo usaron hoy: {today}\n\n📋 Lista:\n\n",
        "user_entry": "👤 ID: {user_id}\n   Usuario: @{username}\n   Nombre: {first_name}\n   Última Actividad: {timestamp}\n\n",
        "no_log_file": "No se encontró el archivo de registro.",
        "user_data_error": "⚠️ Error al recuperar datos de usuarios.",
        
        # Callback messages
        "reels_coming_soon": "¡Próximamente 🚀\n\nEstamos trabajando en añadir la funcionalidad Reels Downloader. ¡Mantente atento!",
        
        # Button text
        "source_video_button": "Video original",
        "check_channel_button": "Ver canal",
        "all_in_1_button": "Descargador Todo en 1",
        
        # Help command
        "help_text": """
📚 **Comandos del Bot y Guía de Uso** 📚

🔹 **Comandos Básicos**:
/start - Iniciar el bot
/help - Mostrar este mensaje de ayuda
/language - Cambiar idioma

🔽 **Descarga de TikTok**:
¡Simplemente envía cualquier enlace de video de TikTok, y lo descargaré sin marca de agua!

⏱ Por favor, espera 10 segundos entre descargas.

🔹 **Solo para Administradores**:
/users - Ver estadísticas de usuarios
/broadcast - Enviar mensaje a todos los usuarios

📢 **Difusión**:
Úsalo de estas maneras:
1. `/broadcast Tu mensaje aquí` - Enviar mensaje de texto
2. Responde a cualquier mensaje con `/broadcast` - Reenviar ese mensaje
3. Responde a foto/video con `/broadcast` - Enviar ese medio

💡 Para botones en difusión, usa:
```
/broadcast Tu mensaje
--btn--Texto del Botón|https://ejemplo.com
--btn--Segundo Botón|https://ejemplo.com
```

¿Necesitas más ayuda? Contacta: @your_support_username
        """,
        
        # Language command
        "language_selection": "🌐 Por favor, selecciona tu idioma preferido:",
        "language_changed": "✅ ¡Idioma cambiado a {language_name}!",
    },
    
    # French translations
    "fr": {
        # Base content, add other keys as needed
        "welcome_message": "Bonjour 👋 {first_name}, Bienvenue sur Tiktok Downloader !\n\nComment utiliser :\n\nEnvoyez simplement le lien de la vidéo et je la téléchargerai sans filigrane 🤙",
        "language_selection": "🌐 Veuillez sélectionner votre langue préférée :",
        "language_changed": "✅ Langue changée en {language_name} !",
        # Other translations would go here...
    },
    
    # And so on for other languages...
    # Portuguese (pt), Russian (ru), Arabic (ar), Chinese (zh), 
    # Hindi (hi), Swahili (sw), Turkish (tr), etc.
}

# Default to English for any missing translations
def get_text(language_code, key, **kwargs):
    """
    Get the text in the specified language.
    If text doesn't exist in that language, fall back to English.
    Supports format parameters like {first_name} as kwargs.
    """
    # Ensure we have a valid language code
    if language_code not in translations:
        language_code = DEFAULT_LANGUAGE
    
    # Get the text from the language, or fall back to English if not found
    text = translations.get(language_code, {}).get(key)
    if text is None:
        text = translations[DEFAULT_LANGUAGE].get(key, f"Missing translation: {key}")
    
    # Format the text with any provided keyword arguments
    try:
        return text.format(**kwargs)
    except KeyError as e:
        # Handle missing format keys gracefully
        print(f"Error formatting text: {e} for key {key} in language {language_code}")
        return text
    except Exception as e:
        print(f"Unexpected error formatting text: {e}")
        return text

# User language preference storage
# Structure: {user_id: language_code}
user_languages = {}

def get_user_language(user_id):
    """Get the user's preferred language code"""
    return user_languages.get(user_id, DEFAULT_LANGUAGE)

def set_user_language(user_id, language_code):
    """Set the user's preferred language"""
    if language_code in AVAILABLE_LANGUAGES:
        user_languages[user_id] = language_code
        # Here you might want to persist this to a database or file
        return True
    return False

# Helper to create language selection keyboard
def get_language_keyboard():
    """Create an inline keyboard with language options"""
    keyboard = []
    row = []
    
    # Create buttons in rows of 2
    for i, (code, name) in enumerate(AVAILABLE_LANGUAGES.items()):
        # Add button with language name and callback data
        row.append({
            "text": name,
            "callback_data": f"lang_{code}"
        })
        
        # Create new row every 2 buttons
        if (i + 1) % 2 == 0 or i == len(AVAILABLE_LANGUAGES) - 1:
            keyboard.append(row)
            row = []
    
    return keyboard

def save_user_languages():
    """Save user language preferences to a file"""
    import json
    try:
        with open("user_languages.json", "w") as f:
            json.dump(user_languages, f)
    except Exception as e:
        print(f"Error saving user languages: {e}")

def load_user_languages():
    """Load user language preferences from a file"""
    import json
    import os
    global user_languages
    
    if os.path.exists("user_languages.json"):
        try:
            with open("user_languages.json", "r") as f:
                user_languages = json.load(f)
        except Exception as e:
            print(f"Error loading user languages: {e}")

# Load saved language preferences when module is imported
load_user_languages()