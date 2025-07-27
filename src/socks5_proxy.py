"""
SOCKS5 Proxy Server with Bandwidth Throttling (BPS)
Implements RFC 1928 - SOCKS Protocol Version 5
"""
import socket
import struct
import threading
import time
import logging
from typing import Optional, Tuple, Dict, Any
from datetime import datetime, timedelta
from dataclasses import dataclass


@dataclass
class BandwidthConfig:
    """Bandwidth configuration for throttling"""
    max_bytes_per_second: int = 0  # 0 = unlimited
    burst_size: int = 0  # Allow burst up to this many bytes
    reset_interval: float = 1.0  # Reset bandwidth counter every N seconds


class BandwidthThrottler:
    """Bandwidth throttling manager"""
    
    def __init__(self, config: BandwidthConfig):
        self.config = config
        self.bytes_sent = 0
        self.last_reset = time.time()
        self.lock = threading.Lock()
    
    def can_send(self, bytes_to_send: int) -> bool:
        """Check if we can send the specified number of bytes"""
        if self.config.max_bytes_per_second == 0:
            return True
            
        with self.lock:
            current_time = time.time()
            
            # Reset counter if interval has passed
            if current_time - self.last_reset >= self.config.reset_interval:
                self.bytes_sent = 0
                self.last_reset = current_time
            
            # Check if we can send within limits
            if self.bytes_sent + bytes_to_send <= self.config.max_bytes_per_second:
                return True
            
            # Check burst allowance
            if self.config.burst_size > 0:
                if self.bytes_sent + bytes_to_send <= self.config.max_bytes_per_second + self.config.burst_size:
                    return True
            
            return False
    
    def record_sent(self, bytes_sent: int):
        """Record bytes sent for throttling"""
        with self.lock:
            self.bytes_sent += bytes_sent
    
    def get_delay(self, bytes_to_send: int) -> float:
        """Calculate delay needed to stay within bandwidth limits"""
        if self.config.max_bytes_per_second == 0:
            return 0.0
            
        with self.lock:
            current_time = time.time()
            
            # Reset counter if interval has passed
            if current_time - self.last_reset >= self.config.reset_interval:
                self.bytes_sent = 0
                self.last_reset = current_time
                return 0.0
            
            # Calculate delay based on current usage
            time_remaining = self.config.reset_interval - (current_time - self.last_reset)
            bytes_available = max(0, self.config.max_bytes_per_second - self.bytes_sent)
            
            if bytes_to_send <= bytes_available:
                return 0.0
            
            # Calculate delay needed
            excess_bytes = bytes_to_send - bytes_available
            delay = (excess_bytes / self.config.max_bytes_per_second) * self.config.reset_interval
            
            return min(delay, time_remaining)


class SOCKS5Server:
    """SOCKS5 Proxy Server with bandwidth throttling"""
    
    # SOCKS5 Constants
    SOCKS_VERSION = 0x05
    
    # Authentication methods
    NO_AUTH = 0x00
    GSSAPI = 0x01
    USERNAME_PASSWORD = 0x02
    NO_ACCEPTABLE_METHODS = 0xFF
    
    # Commands
    CONNECT = 0x01
    BIND = 0x02
    UDP_ASSOCIATE = 0x03
    
    # Address types
    IPV4 = 0x01
    DOMAIN_NAME = 0x03
    IPV6 = 0x04
    
    # Reply codes
    SUCCESS = 0x00
    GENERAL_FAILURE = 0x01
    CONNECTION_NOT_ALLOWED = 0x02
    NETWORK_UNREACHABLE = 0x03
    HOST_UNREACHABLE = 0x04
    CONNECTION_REFUSED = 0x05
    TTL_EXPIRED = 0x06
    COMMAND_NOT_SUPPORTED = 0x07
    ADDRESS_TYPE_NOT_SUPPORTED = 0x08
    
    def __init__(self, host='127.0.0.1', port=1080, bandwidth_config: Optional[BandwidthConfig] = None):
        self.host = host
        self.port = port
        self.bandwidth_config = bandwidth_config or BandwidthConfig()
        self.running = False
        self.server_socket: Optional[socket.socket] = None
        self.logger = self._setup_logging()
        self.client_count = 0
        self.total_bytes_transferred = 0
        self.start_time = datetime.now()
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for the proxy server"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - SOCKS5 - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('socks5_proxy.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger('socks5_proxy')
    
    def start(self):
        """Start the SOCKS5 proxy server"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(128)
            
            self.running = True
            self.logger.info(f"SOCKS5 Proxy server started on {self.host}:{self.port}")
            
            if self.bandwidth_config.max_bytes_per_second > 0:
                self.logger.info(f"Bandwidth throttling enabled: {self.bandwidth_config.max_bytes_per_second} bytes/sec")
            else:
                self.logger.info("Bandwidth throttling disabled (unlimited)")
            
            while self.running:
                try:
                    client_socket, addr = self.server_socket.accept()
                    self.client_count += 1
                    self.logger.info(f"New connection from {addr} (Client #{self.client_count})")
                    
                    # Handle client in separate thread
                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client_socket, addr),
                        daemon=True
                    )
                    client_thread.start()
                    
                except socket.error as e:
                    if self.running:
                        self.logger.error(f"Socket error: {e}")
                    
        except Exception as e:
            self.logger.error(f"Failed to start server: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the SOCKS5 proxy server"""
        self.running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        uptime = datetime.now() - self.start_time
        self.logger.info(f"SOCKS5 Proxy server stopped")
        self.logger.info(f"Session stats: {self.client_count} clients, {self.total_bytes_transferred} bytes transferred, uptime: {uptime}")
    
    def _handle_client(self, client_socket: socket.socket, client_addr):
        """Handle a client connection"""
        bandwidth_throttler = BandwidthThrottler(self.bandwidth_config)
        
        try:
            # Step 1: Authentication negotiation
            if not self._handle_auth_negotiation(client_socket):
                return
            
            # Step 2: Handle connection request
            target_socket = self._handle_connection_request(client_socket)
            if not target_socket:
                return
            
            # Step 3: Relay data between client and target
            self._relay_data(client_socket, target_socket, bandwidth_throttler, client_addr)
            
        except Exception as e:
            self.logger.error(f"Error handling client {client_addr}: {e}")
        finally:
            try:
                client_socket.close()
            except:
                pass
    
    def _handle_auth_negotiation(self, client_socket: socket.socket) -> bool:
        """Handle SOCKS5 authentication negotiation"""
        try:
            # Receive authentication methods
            data = client_socket.recv(2)
            if len(data) != 2:
                return False
            
            version, nmethods = data
            if version != self.SOCKS_VERSION:
                return False
            
            # Read authentication methods
            methods = client_socket.recv(nmethods)
            if len(methods) != nmethods:
                return False
            
            # For simplicity, we'll use no authentication
            if self.NO_AUTH in methods:
                # Send selected method
                response = struct.pack('!BB', self.SOCKS_VERSION, self.NO_AUTH)
                client_socket.send(response)
                return True
            else:
                # No acceptable methods
                response = struct.pack('!BB', self.SOCKS_VERSION, self.NO_ACCEPTABLE_METHODS)
                client_socket.send(response)
                return False
                
        except Exception as e:
            self.logger.error(f"Auth negotiation error: {e}")
            return False
    
    def _handle_connection_request(self, client_socket: socket.socket) -> Optional[socket.socket]:
        """Handle SOCKS5 connection request"""
        try:
            # Receive connection request
            data = client_socket.recv(4)
            if len(data) != 4:
                return None
            
            version, cmd, rsv, atyp = data
            if version != self.SOCKS_VERSION:
                return None
            
            if cmd != self.CONNECT:
                # Send unsupported command error
                self._send_error_response(client_socket, self.COMMAND_NOT_SUPPORTED)
                return None
            
            # Parse destination address
            dest_addr, dest_port = self._parse_address(client_socket, atyp)
            if not dest_addr:
                self._send_error_response(client_socket, self.ADDRESS_TYPE_NOT_SUPPORTED)
                return None
            
            # Connect to target
            target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            target_socket.settimeout(10)  # 10 second timeout
            
            try:
                target_socket.connect((dest_addr, dest_port))
                self.logger.info(f"Connected to {dest_addr}:{dest_port}")
                
                # Send success response
                self._send_success_response(client_socket, dest_addr, dest_port)
                return target_socket
                
            except socket.error as e:
                self.logger.warning(f"Failed to connect to {dest_addr}:{dest_port}: {e}")
                self._send_error_response(client_socket, self.CONNECTION_REFUSED)
                target_socket.close()
                return None
                
        except Exception as e:
            self.logger.error(f"Connection request error: {e}")
            return None
    
    def _parse_address(self, client_socket: socket.socket, atyp: int) -> Tuple[Optional[str], Optional[int]]:
        """Parse destination address from SOCKS5 request"""
        try:
            if atyp == self.IPV4:
                # IPv4 address (4 bytes)
                addr_data = client_socket.recv(4)
                if len(addr_data) != 4:
                    return None, None
                addr = socket.inet_ntoa(addr_data)
                
            elif atyp == self.DOMAIN_NAME:
                # Domain name
                domain_len = client_socket.recv(1)[0]
                domain_data = client_socket.recv(domain_len)
                if len(domain_data) != domain_len:
                    return None, None
                addr = domain_data.decode('utf-8')
                
            elif atyp == self.IPV6:
                # IPv6 address (16 bytes)
                addr_data = client_socket.recv(16)
                if len(addr_data) != 16:
                    return None, None
                addr = socket.inet_ntop(socket.AF_INET6, addr_data)
                
            else:
                return None, None
            
            # Read port (2 bytes)
            port_data = client_socket.recv(2)
            if len(port_data) != 2:
                return None, None
            port = struct.unpack('!H', port_data)[0]
            
            return addr, port
            
        except Exception as e:
            self.logger.error(f"Address parsing error: {e}")
            return None, None
    
    def _send_success_response(self, client_socket: socket.socket, bind_addr: str, bind_port: int):
        """Send successful connection response"""
        try:
            # Convert address to bytes
            addr_bytes = socket.inet_aton(bind_addr)
            
            # Build response
            response = struct.pack('!BBBB', self.SOCKS_VERSION, self.SUCCESS, 0x00, self.IPV4)
            response += addr_bytes
            response += struct.pack('!H', bind_port)
            
            client_socket.send(response)
            
        except Exception as e:
            self.logger.error(f"Error sending success response: {e}")
    
    def _send_error_response(self, client_socket: socket.socket, error_code: int):
        """Send error response"""
        try:
            response = struct.pack('!BBBB', self.SOCKS_VERSION, error_code, 0x00, self.IPV4)
            response += b'\x00' * 4  # Zero IP
            response += struct.pack('!H', 0)  # Zero port
            
            client_socket.send(response)
            
        except Exception as e:
            self.logger.error(f"Error sending error response: {e}")
    
    def _relay_data(self, client_socket: socket.socket, target_socket: socket.socket, 
                   bandwidth_throttler: BandwidthThrottler, client_addr):
        """Relay data between client and target with bandwidth throttling"""
        
        def forward_data(source: socket.socket, destination: socket.socket, direction: str):
            """Forward data from source to destination"""
            try:
                while True:
                    data = source.recv(4096)
                    if not data:
                        break
                    
                    # Apply bandwidth throttling
                    if direction == "client->target":
                        delay = bandwidth_throttler.get_delay(len(data))
                        if delay > 0:
                            time.sleep(delay)
                        bandwidth_throttler.record_sent(len(data))
                    
                    destination.send(data)
                    self.total_bytes_transferred += len(data)
                    
            except Exception as e:
                self.logger.debug(f"Data relay error ({direction}): {e}")
            finally:
                try:
                    source.close()
                    destination.close()
                except:
                    pass
        
        # Create threads for bidirectional data relay
        client_to_target = threading.Thread(
            target=forward_data,
            args=(client_socket, target_socket, "client->target"),
            daemon=True
        )
        
        target_to_client = threading.Thread(
            target=forward_data,
            args=(target_socket, client_socket, "target->client"),
            daemon=True
        )
        
        # Start threads
        client_to_target.start()
        target_to_client.start()
        
        # Wait for threads to complete
        client_to_target.join()
        target_to_client.join()
        
        self.logger.info(f"Connection from {client_addr} closed")


def main():
    """Main entry point for SOCKS5 proxy server"""
    import argparse
    
    parser = argparse.ArgumentParser(description='SOCKS5 Proxy Server with Bandwidth Throttling')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=1080, help='Port to bind to (default: 1080)')
    parser.add_argument('--bps', type=int, default=0, 
                       help='Bandwidth limit in bytes per second (0 = unlimited)')
    parser.add_argument('--burst', type=int, default=0,
                       help='Burst size in bytes (default: 0)')
    
    args = parser.parse_args()
    
    # Create bandwidth configuration
    bandwidth_config = BandwidthConfig(
        max_bytes_per_second=args.bps,
        burst_size=args.burst,
        reset_interval=1.0
    )
    
    # Create and start server
    server = SOCKS5Server(
        host=args.host,
        port=args.port,
        bandwidth_config=bandwidth_config
    )
    
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nShutting down SOCKS5 proxy server...")
        server.stop()


if __name__ == "__main__":
    main()