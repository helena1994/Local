"""
Configuration settings for SOCKS5 Proxy Server
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class ProxyConfig:
    """Configuration class for the SOCKS5 proxy server"""
    
    # Server settings
    PROXY_HOST = os.getenv('PROXY_HOST', '127.0.0.1')
    PROXY_PORT = int(os.getenv('PROXY_PORT', '1080'))
    
    # Bandwidth settings
    MAX_BYTES_PER_SECOND = int(os.getenv('MAX_BYTES_PER_SECOND', '0'))  # 0 = unlimited
    BURST_SIZE = int(os.getenv('BURST_SIZE', '0'))  # Burst allowance in bytes
    RESET_INTERVAL = float(os.getenv('RESET_INTERVAL', '1.0'))  # Reset counter interval
    
    # Connection settings
    MAX_CONNECTIONS = int(os.getenv('MAX_CONNECTIONS', '100'))
    CONNECTION_TIMEOUT = int(os.getenv('CONNECTION_TIMEOUT', '10'))
    
    # Logging settings
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'socks5_proxy.log')
    
    # Authentication settings (for future expansion)
    ENABLE_AUTH = os.getenv('ENABLE_AUTH', 'False').lower() == 'true'
    AUTH_USERNAME = os.getenv('AUTH_USERNAME', '')
    AUTH_PASSWORD = os.getenv('AUTH_PASSWORD', '')
    
    @classmethod
    def validate_config(cls):
        """Validate proxy configuration"""
        errors = []
        
        # Validate port range
        if not (1 <= cls.PROXY_PORT <= 65535):
            errors.append(f"Invalid port: {cls.PROXY_PORT}. Must be between 1 and 65535")
        
        # Validate bandwidth settings
        if cls.MAX_BYTES_PER_SECOND < 0:
            errors.append(f"Invalid bandwidth limit: {cls.MAX_BYTES_PER_SECOND}. Must be >= 0")
        
        if cls.BURST_SIZE < 0:
            errors.append(f"Invalid burst size: {cls.BURST_SIZE}. Must be >= 0")
        
        if cls.RESET_INTERVAL <= 0:
            errors.append(f"Invalid reset interval: {cls.RESET_INTERVAL}. Must be > 0")
        
        # Validate connection settings
        if cls.MAX_CONNECTIONS <= 0:
            errors.append(f"Invalid max connections: {cls.MAX_CONNECTIONS}. Must be > 0")
        
        if cls.CONNECTION_TIMEOUT <= 0:
            errors.append(f"Invalid connection timeout: {cls.CONNECTION_TIMEOUT}. Must be > 0")
        
        if errors:
            raise ValueError("Configuration errors:\n" + "\n".join(f"- {error}" for error in errors))
        
        return True
    
    @classmethod
    def get_bandwidth_description(cls) -> str:
        """Get human-readable bandwidth description"""
        if cls.MAX_BYTES_PER_SECOND == 0:
            return "Unlimited bandwidth"
        
        # Convert to human-readable units
        if cls.MAX_BYTES_PER_SECOND >= 1024 * 1024:
            bps_mb = cls.MAX_BYTES_PER_SECOND / (1024 * 1024)
            unit = "MB/s"
            value = f"{bps_mb:.2f}"
        elif cls.MAX_BYTES_PER_SECOND >= 1024:
            bps_kb = cls.MAX_BYTES_PER_SECOND / 1024
            unit = "KB/s"
            value = f"{bps_kb:.2f}"
        else:
            unit = "B/s"
            value = str(cls.MAX_BYTES_PER_SECOND)
        
        result = f"{value} {unit}"
        
        if cls.BURST_SIZE > 0:
            if cls.BURST_SIZE >= 1024 * 1024:
                burst_mb = cls.BURST_SIZE / (1024 * 1024)
                burst_desc = f"{burst_mb:.2f} MB"
            elif cls.BURST_SIZE >= 1024:
                burst_kb = cls.BURST_SIZE / 1024
                burst_desc = f"{burst_kb:.2f} KB"
            else:
                burst_desc = f"{cls.BURST_SIZE} B"
            
            result += f" (burst: {burst_desc})"
        
        return result
    
    @classmethod
    def print_config(cls):
        """Print current configuration"""
        print("🔧 SOCKS5 Proxy Configuration:")
        print(f"   Server: {cls.PROXY_HOST}:{cls.PROXY_PORT}")
        print(f"   Bandwidth: {cls.get_bandwidth_description()}")
        print(f"   Max connections: {cls.MAX_CONNECTIONS}")
        print(f"   Connection timeout: {cls.CONNECTION_TIMEOUT}s")
        print(f"   Authentication: {'Enabled' if cls.ENABLE_AUTH else 'Disabled'}")
        print(f"   Log level: {cls.LOG_LEVEL}")
        print(f"   Log file: {cls.LOG_FILE}")