"""
Template untuk kredensial login Messenger.

PENTING: Jangan commit file ini dengan kredensial asli!
Salin file ini menjadi credentials.py dan isi dengan data login Anda.
"""

# Kredensial login Facebook/Messenger
FACEBOOK_CREDENTIALS = {
    'email': 'your_email@example.com',
    'password': 'your_password_here'
}

# URL dan selectors untuk Messenger
MESSENGER_CONFIG = {
    'login_url': 'https://www.facebook.com/login',
    'messenger_url': 'https://www.messenger.com',
    'selectors': {
        'email_input': 'input[name="email"]',
        'password_input': 'input[name="pass"]',
        'login_button': 'button[name="login"]',
        'message_input': 'div[aria-label="Type a message..."]',
        'send_button': 'div[aria-label="Press Enter to send"]',
        'conversation_list': 'div[role="navigation"]',
        'message_thread': 'div[role="main"]',
        'unread_messages': 'div[aria-label*="unread"]'
    }
}

# Pengaturan keamanan tambahan
SECURITY_CONFIG = {
    'enable_2fa_handling': False,  # Set True jika akun menggunakan 2FA
    'trusted_device': True,  # Tandai sebagai perangkat terpercaya
    'auto_accept_cookies': True
}