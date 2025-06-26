"""
Modul utama untuk otomatisasi Messenger menggunakan Selenium.

Menangani:
- Inisialisasi Chrome WebDriver
- Auto-login ke Facebook/Messenger
- Membaca pesan masuk
- Mengirim respons otomatis
- Manajemen session
"""

import time
import random
import logging
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import sys

from .auto_login import FacebookAutoLogin
from .sentiment_analysis import SentimentAnalyzer
from .database_manager import DatabaseManager

logger = logging.getLogger(__name__)


class MessengerBot:
    """Class utama untuk bot Messenger otomatis."""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize Messenger Bot.
        
        Args:
            db_manager: Instance DatabaseManager
        """
        self.db_manager = db_manager
        self.driver = None
        self.login_handler = None
        self.sentiment_analyzer = SentimentAnalyzer()
        self.is_running = False
        
        # Load config
        # Add project root to path for importing config
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root))
        
        from config.settings import BOT_CONFIG, CHROME_CONFIG, MESSENGER_CONFIG
        self.bot_config = BOT_CONFIG
        self.chrome_config = CHROME_CONFIG
        self.messenger_config = MESSENGER_CONFIG
        
        # Tracking state
        self.processed_messages = set()
        self.last_activity = time.time()
    
    def initialize_driver(self) -> bool:
        """
        Inisialisasi Chrome WebDriver.
        
        Returns:
            True jika berhasil, False jika gagal
        """
        try:
            logger.info("🔄 Inisialisasi Chrome WebDriver...")
            
            # Setup Chrome options
            chrome_options = Options()
            
            # Add basic options
            for option in self.chrome_config['options']:
                chrome_options.add_argument(option)
            
            # Setup user data directory untuk menyimpan session
            user_data_dir = self.chrome_config['user_data_dir']
            Path(user_data_dir).mkdir(parents=True, exist_ok=True)
            chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
            
            # Setup download directory
            download_dir = self.chrome_config['download_dir']
            Path(download_dir).mkdir(parents=True, exist_ok=True)
            
            prefs = {
                "download.default_directory": str(download_dir),
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True
            }
            chrome_options.add_experimental_option("prefs", prefs)
            
            # Headless mode jika diaktifkan
            if self.bot_config.get('headless', False):
                chrome_options.add_argument('--headless')
                logger.info("🔄 Mode headless diaktifkan")
            
            # Initialize driver
            # Note: Pastikan chromedriver sudah terinstall di PATH
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.maximize_window()
            
            # Setup implicit wait
            self.driver.implicitly_wait(10)
            
            logger.info("✅ Chrome WebDriver berhasil diinisialisasi")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saat inisialisasi driver: {e}")
            return False
    
    def start(self):
        """Memulai bot Messenger."""
        try:
            logger.info("🚀 Memulai bot Messenger...")
            
            # Initialize driver
            if not self.initialize_driver():
                raise Exception("Gagal inisialisasi Chrome WebDriver")
            
            # Initialize login handler
            self.login_handler = FacebookAutoLogin(self.driver)
            
            # Login ke Facebook/Messenger
            if not self.login_handler.login():
                raise Exception("Gagal login ke Facebook/Messenger")
            
            # Log aktivitas
            self.db_manager.log_activity(
                'bot_start', 
                'Bot berhasil dimulai dan login',
                'success'
            )
            
            # Mulai main loop
            self.is_running = True
            self._main_loop()
            
        except KeyboardInterrupt:
            logger.info("❌ Bot dihentikan oleh pengguna")
        except Exception as e:
            logger.error(f"❌ Error saat memulai bot: {e}")
            self.db_manager.log_activity(
                'bot_error',
                f'Error saat memulai bot: {str(e)}',
                'error',
                str(e)
            )
        finally:
            self.cleanup()
    
    def _main_loop(self):
        """Main loop untuk monitoring dan respons pesan."""
        logger.info("🔄 Memulai monitoring pesan...")
        
        while self.is_running:
            try:
                # Check apakah masih login
                if not self.login_handler.is_logged_in():
                    logger.warning("⚠️  Session login expired, mencoba login ulang...")
                    if not self.login_handler.login():
                        logger.error("❌ Gagal login ulang")
                        break
                
                # Scan pesan baru
                new_messages = self._scan_new_messages()
                
                # Process setiap pesan baru
                for message in new_messages:
                    self._process_message(message)
                
                # Update last activity
                self.last_activity = time.time()
                
                # Tunggu sebelum check lagi
                time.sleep(self.bot_config['check_interval'])
                
            except KeyboardInterrupt:
                logger.info("❌ Main loop dihentikan")
                break
            except Exception as e:
                logger.error(f"❌ Error di main loop: {e}")
                self.db_manager.log_activity(
                    'main_loop_error',
                    f'Error di main loop: {str(e)}',
                    'error',
                    str(e)
                )
                time.sleep(10)  # Wait before retry
    
    def _scan_new_messages(self) -> list:
        """
        Scan pesan baru yang belum diproses.
        
        Returns:
            List pesan baru
        """
        try:
            new_messages = []
            
            # Navigasi ke chat list jika belum ada
            self._ensure_chat_list_visible()
            
            # Cari conversation dengan unread messages
            unread_conversations = self._find_unread_conversations()
            
            for conversation in unread_conversations:
                try:
                    # Klik conversation
                    conversation.click()
                    time.sleep(2)
                    
                    # Baca pesan dalam conversation
                    messages = self._read_conversation_messages()
                    
                    for message in messages:
                        message_id = self._generate_message_id(message)
                        if message_id not in self.processed_messages:
                            new_messages.append(message)
                            self.processed_messages.add(message_id)
                    
                except Exception as e:
                    logger.error(f"❌ Error saat scan conversation: {e}")
                    continue
            
            if new_messages:
                logger.info(f"📨 Ditemukan {len(new_messages)} pesan baru")
            
            return new_messages
            
        except Exception as e:
            logger.error(f"❌ Error saat scan pesan: {e}")
            return []
    
    def _ensure_chat_list_visible(self):
        """Memastikan chat list terlihat."""
        try:
            # Check apakah sudah di halaman utama Messenger
            current_url = self.driver.current_url
            if 'messenger.com' not in current_url:
                self.driver.get(self.messenger_config['messenger_url'])
                time.sleep(3)
            
            # Tunggu hingga chat list muncul
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="navigation"]'))
            )
            
        except TimeoutException:
            logger.error("❌ Timeout saat menunggu chat list")
    
    def _find_unread_conversations(self) -> list:
        """
        Cari conversation dengan pesan yang belum dibaca.
        
        Returns:
            List elemen conversation yang belum dibaca
        """
        try:
            # Selectors untuk unread conversations
            unread_selectors = [
                'div[aria-label*="unread"]',
                'div[data-testid="unread-conversation"]',
                'div:has(div[aria-label*="unread"])',
                'div[role="gridcell"]:has(strong)'  # Bold text indicates unread
            ]
            
            unread_conversations = []
            
            for selector in unread_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    unread_conversations.extend(elements)
                except:
                    continue
            
            # Remove duplicates
            unique_conversations = []
            seen_conversations = set()
            
            for conv in unread_conversations:
                try:
                    conv_id = conv.get_attribute('data-testid') or conv.get_attribute('id') or str(hash(conv.text))
                    if conv_id not in seen_conversations:
                        unique_conversations.append(conv)
                        seen_conversations.add(conv_id)
                except:
                    continue
            
            return unique_conversations[:5]  # Limit to 5 conversations
            
        except Exception as e:
            logger.error(f"❌ Error saat cari unread conversations: {e}")
            return []
    
    def _read_conversation_messages(self) -> list:
        """
        Baca pesan dalam conversation yang sedang aktif.
        
        Returns:
            List pesan dalam conversation
        """
        try:
            messages = []
            
            # Tunggu hingga conversation load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="main"]'))
            )
            
            # Cari semua message elements
            message_selectors = [
                'div[data-testid="conversation-message"]',
                'div[role="row"]',
                'div:has(span:contains(":"))'  # Messages usually have timestamp
            ]
            
            message_elements = []
            for selector in message_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    message_elements.extend(elements)
                    if elements:  # Use first selector that works
                        break
                except:
                    continue
            
            # Process message elements
            for element in message_elements[-10:]:  # Only process last 10 messages
                try:
                    message_data = self._extract_message_data(element)
                    if message_data and message_data.get('is_incoming'):
                        messages.append(message_data)
                except Exception as e:
                    logger.debug(f"Error extract message: {e}")
                    continue
            
            return messages
            
        except Exception as e:
            logger.error(f"❌ Error saat baca conversation: {e}")
            return []
    
    def _extract_message_data(self, element) -> dict:
        """
        Extract data dari elemen pesan.
        
        Args:
            element: WebElement pesan
            
        Returns:
            Dictionary berisi data pesan
        """
        try:
            # Extract text
            message_text = element.text.strip()
            if not message_text:
                return None
            
            # Determine if incoming or outgoing
            # Incoming messages biasanya ada di sisi kiri, outgoing di kanan
            is_incoming = True  # Default assume incoming
            
            try:
                # Check position atau class untuk menentukan direction
                element_classes = element.get_attribute('class') or ''
                if 'outgoing' in element_classes.lower() or 'sent' in element_classes.lower():
                    is_incoming = False
            except:
                pass
            
            # Extract user info (nama pengirim)
            user_name = "Unknown User"
            user_id = "unknown"
            
            try:
                # Cari elemen yang mengandung nama pengirim
                name_element = element.find_element(By.CSS_SELECTOR, 'strong, span[title], div[title]')
                user_name = name_element.get_attribute('title') or name_element.text
                user_id = user_name.lower().replace(' ', '_')
            except:
                pass
            
            return {
                'user_id': user_id,
                'user_name': user_name,
                'message_text': message_text,
                'is_incoming': is_incoming,
                'timestamp': time.time(),
                'element': element
            }
            
        except Exception as e:
            logger.debug(f"Error extract message data: {e}")
            return None
    
    def _generate_message_id(self, message: dict) -> str:
        """Generate unique ID untuk pesan."""
        return f"{message['user_id']}_{hash(message['message_text'])}_{int(message['timestamp'])}"
    
    def _process_message(self, message: dict):
        """
        Process pesan masuk dan kirim respons.
        
        Args:
            message: Dictionary data pesan
        """
        try:
            logger.info(f"📨 Processing pesan dari {message['user_name']}: {message['message_text'][:50]}...")
            
            # Analisis sentimen
            sentiment_score, sentiment_label = self.sentiment_analyzer.analyze_sentiment(
                message['message_text']
            )
            
            # Simpan pesan ke database
            message_id = self.db_manager.save_message(
                user_id=message['user_id'],
                user_name=message['user_name'],
                message_text=message['message_text'],
                message_type='incoming',
                sentiment_score=sentiment_score,
                sentiment_label=sentiment_label
            )
            
            # Generate respons
            user_history = self.db_manager.get_user_history(message['user_id'], limit=5)
            response_text = self.sentiment_analyzer.get_advanced_response(
                text=message['message_text'],
                sentiment_score=sentiment_score,
                sentiment_label=sentiment_label,
                user_name=message['user_name']
            )
            
            # Kirim respons
            if self._send_response(response_text):
                # Simpan respons ke database
                self.db_manager.save_message(
                    user_id=message['user_id'],
                    user_name='Bot',
                    message_text=response_text,
                    message_type='outgoing',
                    sentiment_score=None,
                    sentiment_label=None
                )
                
                # Mark message as processed
                self.db_manager.mark_message_processed(message_id)
                
                logger.info(f"✅ Respons terkirim: {response_text}")
            else:
                logger.error("❌ Gagal kirim respons")
            
        except Exception as e:
            logger.error(f"❌ Error saat process pesan: {e}")
            self.db_manager.log_activity(
                'message_processing_error',
                f'Error processing pesan: {str(e)}',
                'error',
                str(e)
            )
    
    def _send_response(self, response_text: str) -> bool:
        """
        Kirim respons ke conversation yang aktif.
        
        Args:
            response_text: Teks respons yang akan dikirim
            
        Returns:
            True jika berhasil kirim, False jika gagal
        """
        try:
            # Add random delay untuk terlihat natural
            delay = random.uniform(*self.bot_config['response_delay'])
            time.sleep(delay)
            
            # Cari input field untuk mengetik pesan
            input_selectors = [
                'div[aria-label="Type a message..."]',
                'div[contenteditable="true"]',
                'textarea[placeholder*="message"]',
                'div[role="textbox"]'
            ]
            
            message_input = None
            for selector in input_selectors:
                try:
                    message_input = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    break
                except TimeoutException:
                    continue
            
            if not message_input:
                logger.error("❌ Tidak dapat menemukan input field")
                return False
            
            # Klik input field dan ketik respons
            message_input.click()
            time.sleep(0.5)
            message_input.send_keys(response_text)
            time.sleep(1)
            
            # Cari tombol send
            send_selectors = [
                'div[aria-label="Press Enter to send"]',
                'button[type="submit"]',
                'div[role="button"]:has(svg)',
                'button:contains("Send")'
            ]
            
            send_button = None
            for selector in send_selectors:
                try:
                    send_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except NoSuchElementException:
                    continue
            
            if send_button:
                send_button.click()
            else:
                # Fallback: tekan Enter
                from selenium.webdriver.common.keys import Keys
                message_input.send_keys(Keys.RETURN)
            
            time.sleep(2)
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saat kirim respons: {e}")
            return False
    
    def cleanup(self):
        """Bersihkan resources saat bot dihentikan."""
        try:
            logger.info("🔄 Membersihkan resources...")
            
            self.is_running = False
            
            if self.driver:
                self.driver.quit()
                logger.info("✅ Chrome WebDriver ditutup")
            
            self.db_manager.log_activity(
                'bot_stop',
                'Bot berhasil dihentikan',
                'success'
            )
            
        except Exception as e:
            logger.error(f"❌ Error saat cleanup: {e}")
    
    def get_status(self) -> dict:
        """Dapatkan status bot."""
        return {
            'is_running': self.is_running,
            'last_activity': self.last_activity,
            'processed_messages_count': len(self.processed_messages),
            'driver_active': self.driver is not None
        }