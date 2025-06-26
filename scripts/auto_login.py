"""
Modul auto-login untuk Facebook/Messenger menggunakan Selenium.

Menangani proses login otomatis dengan berbagai skenario:
- Login normal
- 2FA (Two-Factor Authentication)
- Captcha handling
- Session management
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


class FacebookAutoLogin:
    """Class untuk menangani auto-login Facebook/Messenger."""
    
    def __init__(self, driver: webdriver.Chrome = None):
        """
        Initialize auto-login handler.
        
        Args:
            driver: Instance Chrome WebDriver
        """
        self.driver = driver
        self.wait = WebDriverWait(driver, 10) if driver else None
        
        # Load credentials dan config
        try:
            # Add project root to path for importing config
            project_root = Path(__file__).parent.parent
            sys.path.insert(0, str(project_root))
            
            from config.credentials import FACEBOOK_CREDENTIALS, MESSENGER_CONFIG, SECURITY_CONFIG
            self.credentials = FACEBOOK_CREDENTIALS
            self.config = MESSENGER_CONFIG
            self.security = SECURITY_CONFIG
        except ImportError:
            logger.error("❌ File credentials.py tidak ditemukan!")
            raise
    
    def login(self) -> bool:
        """
        Proses login ke Facebook.
        
        Returns:
            True jika login berhasil, False jika gagal
        """
        try:
            logger.info("🔐 Memulai proses login...")
            
            # Navigasi ke halaman login
            self.driver.get(self.config['login_url'])
            time.sleep(2)
            
            # Handle cookies popup jika ada
            if self.security.get('auto_accept_cookies', True):
                self._handle_cookies_popup()
            
            # Input email
            email_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.config['selectors']['email_input']))
            )
            email_input.clear()
            email_input.send_keys(self.credentials['email'])
            logger.info("✅ Email berhasil diinput")
            
            # Input password
            password_input = self.driver.find_element(By.CSS_SELECTOR, self.config['selectors']['password_input'])
            password_input.clear()
            password_input.send_keys(self.credentials['password'])
            logger.info("✅ Password berhasil diinput")
            
            # Klik tombol login
            login_button = self.driver.find_element(By.CSS_SELECTOR, self.config['selectors']['login_button'])
            login_button.click()
            logger.info("🔄 Menunggu proses login...")
            
            # Tunggu hingga login selesai
            time.sleep(5)
            
            # Check apakah perlu handle 2FA
            if self._is_2fa_required():
                if self.security.get('enable_2fa_handling', False):
                    success = self._handle_2fa()
                    if not success:
                        return False
                else:
                    logger.warning("⚠️  2FA diperlukan tapi tidak diaktifkan di config")
                    return False
            
            # Check apakah perlu handle security check
            if self._is_security_check_required():
                success = self._handle_security_check()
                if not success:
                    return False
            
            # Verifikasi login berhasil
            if self._verify_login_success():
                logger.info("✅ Login berhasil!")
                
                # Navigate ke Messenger
                return self._navigate_to_messenger()
            else:
                logger.error("❌ Login gagal!")
                return False
                
        except TimeoutException:
            logger.error("❌ Timeout saat login")
            return False
        except Exception as e:
            logger.error(f"❌ Error saat login: {e}")
            return False
    
    def _handle_cookies_popup(self):
        """Handle popup persetujuan cookies."""
        try:
            # Coba cari tombol accept cookies
            accept_selectors = [
                'button[data-cookiebanner="accept_button"]',
                'button[title="Accept All"]',
                'button:contains("Accept")',
                'div[role="button"]:contains("Accept")'
            ]
            
            for selector in accept_selectors:
                try:
                    accept_btn = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    accept_btn.click()
                    logger.info("✅ Cookies popup diterima")
                    time.sleep(1)
                    return
                except:
                    continue
                    
        except Exception as e:
            logger.debug(f"Tidak ada cookies popup atau error: {e}")
    
    def _is_2fa_required(self) -> bool:
        """Check apakah 2FA diperlukan."""
        try:
            # Cek elemen-elemen yang menandakan 2FA
            two_fa_indicators = [
                'input[name="approvals_code"]',
                'div:contains("two-factor")',
                'div:contains("authentication")',
                'input[placeholder*="code"]'
            ]
            
            for indicator in two_fa_indicators:
                try:
                    self.driver.find_element(By.CSS_SELECTOR, indicator)
                    logger.info("🔐 2FA diperlukan")
                    return True
                except NoSuchElementException:
                    continue
            
            return False
            
        except Exception:
            return False
    
    def _handle_2fa(self) -> bool:
        """
        Handle Two-Factor Authentication.
        
        Returns:
            True jika berhasil, False jika gagal
        """
        try:
            logger.info("🔐 Menangani 2FA...")
            
            # Tunggu user input manual untuk kode 2FA
            print("\n" + "="*50)
            print("🔐 TWO-FACTOR AUTHENTICATION DIPERLUKAN")
            print("="*50)
            print("Silakan cek aplikasi authenticator atau SMS Anda")
            print("Masukkan kode 2FA yang diterima:")
            
            code = input("Kode 2FA: ").strip()
            
            if not code:
                logger.error("❌ Kode 2FA tidak diinput")
                return False
            
            # Input kode 2FA
            code_input = self.driver.find_element(By.CSS_SELECTOR, 'input[name="approvals_code"]')
            code_input.clear()
            code_input.send_keys(code)
            
            # Submit kode
            submit_btn = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            submit_btn.click()
            
            # Tunggu verifikasi
            time.sleep(5)
            
            # Check jika ada opsi "Trust this device"
            try:
                trust_device_btn = self.driver.find_element(By.CSS_SELECTOR, 'button:contains("Don\'t save")')
                if self.security.get('trusted_device', True):
                    # Klik "Save" untuk trust device
                    save_btn = self.driver.find_element(By.CSS_SELECTOR, 'button:contains("Save")')
                    save_btn.click()
                else:
                    trust_device_btn.click()
                
                time.sleep(3)
            except NoSuchElementException:
                pass
            
            logger.info("✅ 2FA berhasil diverifikasi")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saat handle 2FA: {e}")
            return False
    
    def _is_security_check_required(self) -> bool:
        """Check apakah ada security check yang diperlukan."""
        try:
            security_indicators = [
                'div:contains("security check")',
                'div:contains("verify")',
                'div:contains("suspicious")',
                'input[name="captcha"]'
            ]
            
            for indicator in security_indicators:
                try:
                    self.driver.find_element(By.CSS_SELECTOR, indicator)
                    return True
                except NoSuchElementException:
                    continue
            
            return False
            
        except Exception:
            return False
    
    def _handle_security_check(self) -> bool:
        """Handle security check manual."""
        try:
            logger.warning("⚠️  Security check diperlukan")
            print("\n" + "="*50)
            print("🛡️  SECURITY CHECK DIPERLUKAN")
            print("="*50)
            print("Facebook memerlukan verifikasi keamanan.")
            print("Silakan selesaikan verifikasi secara manual di browser.")
            print("Tekan Enter setelah selesai...")
            
            input("Tekan Enter untuk melanjutkan: ")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saat handle security check: {e}")
            return False
    
    def _verify_login_success(self) -> bool:
        """Verifikasi apakah login berhasil."""
        try:
            # Check indikator login berhasil
            success_indicators = [
                'div[role="navigation"]',  # Navigation menu
                'div[aria-label="Account"]',  # Account menu
                'a[href*="/profile"]',  # Profile link
                'div:contains("News Feed")'  # News Feed
            ]
            
            for indicator in success_indicators:
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, indicator))
                    )
                    return True
                except TimeoutException:
                    continue
            
            # Check URL juga
            current_url = self.driver.current_url
            if 'facebook.com' in current_url and 'login' not in current_url:
                return True
            
            return False
            
        except Exception:
            return False
    
    def _navigate_to_messenger(self) -> bool:
        """Navigate ke halaman Messenger."""
        try:
            logger.info("🔄 Navigasi ke Messenger...")
            
            # Navigate ke Messenger
            self.driver.get(self.config['messenger_url'])
            
            # Tunggu halaman Messenger load
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="navigation"]'))
            )
            
            logger.info("✅ Berhasil masuk ke Messenger")
            return True
            
        except TimeoutException:
            logger.error("❌ Timeout saat navigasi ke Messenger")
            return False
        except Exception as e:
            logger.error(f"❌ Error saat navigasi ke Messenger: {e}")
            return False
    
    def is_logged_in(self) -> bool:
        """Check apakah masih dalam status login."""
        try:
            # Check apakah masih di halaman yang memerlukan login
            current_url = self.driver.current_url
            
            if 'login' in current_url or 'checkpoint' in current_url:
                return False
            
            # Check elemen yang menandakan user sudah login
            try:
                self.driver.find_element(By.CSS_SELECTOR, 'div[role="navigation"]')
                return True
            except NoSuchElementException:
                return False
                
        except Exception:
            return False
    
    def logout(self):
        """Logout dari Facebook."""
        try:
            logger.info("🔄 Melakukan logout...")
            
            # Klik menu account
            account_menu = self.driver.find_element(By.CSS_SELECTOR, 'div[aria-label="Account"]')
            account_menu.click()
            time.sleep(2)
            
            # Klik logout
            logout_btn = self.driver.find_element(By.CSS_SELECTOR, 'a[href*="logout"]')
            logout_btn.click()
            
            # Tunggu hingga logout selesai
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="email"]'))
            )
            
            logger.info("✅ Logout berhasil")
            
        except Exception as e:
            logger.error(f"❌ Error saat logout: {e}")