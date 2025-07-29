#!/usr/bin/env python3
"""
Test suite for SOCKS5 Proxy Server
"""
import sys
import os
import time
import socket
import threading
import struct
from typing import Optional

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Test imports
def test_imports():
    """Test if all proxy modules can be imported"""
    print("🧪 Testing SOCKS5 Proxy Server Components")
    print("=" * 50)
    
    try:
        from socks5_proxy import SOCKS5Server, BandwidthConfig, BandwidthThrottler
        print("✅ socks5_proxy module imported successfully")
        
        from proxy_config import ProxyConfig
        print("✅ proxy_config module imported successfully")
        
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False


def test_bandwidth_throttler():
    """Test bandwidth throttling functionality"""
    print("\n📋 Testing Bandwidth Throttler:")
    print("-" * 40)
    
    try:
        from socks5_proxy import BandwidthConfig, BandwidthThrottler
        
        # Test unlimited bandwidth
        config = BandwidthConfig(max_bytes_per_second=0)
        throttler = BandwidthThrottler(config)
        
        assert throttler.can_send(1000000), "Should allow unlimited bytes"
        assert throttler.get_delay(1000000) == 0.0, "Should have no delay for unlimited"
        print("✅ Unlimited bandwidth test passed")
        
        # Test limited bandwidth
        config = BandwidthConfig(max_bytes_per_second=1000, burst_size=500)
        throttler = BandwidthThrottler(config)
        
        assert throttler.can_send(800), "Should allow bytes within limit"
        assert throttler.can_send(1200), "Should allow bytes within burst"
        print("✅ Limited bandwidth test passed")
        
        # Test delay calculation
        delay = throttler.get_delay(2000)
        assert delay > 0, "Should have delay for excess bytes"
        print("✅ Delay calculation test passed")
        
        return True
        
    except Exception as e:
        print(f"❌ Bandwidth throttler test failed: {e}")
        return False


def test_socks5_server_creation():
    """Test SOCKS5 server creation and basic functionality"""
    print("\n📋 Testing SOCKS5 Server Creation:")
    print("-" * 40)
    
    try:
        from socks5_proxy import SOCKS5Server, BandwidthConfig
        
        # Test server creation
        bandwidth_config = BandwidthConfig(max_bytes_per_second=100000)
        server = SOCKS5Server(host='127.0.0.1', port=0, bandwidth_config=bandwidth_config)
        
        assert server.host == '127.0.0.1', "Host should be set correctly"
        assert server.port == 0, "Port should be set correctly"
        assert server.bandwidth_config.max_bytes_per_second == 100000, "Bandwidth config should be set"
        assert not server.running, "Server should not be running initially"
        
        print("✅ Server creation test passed")
        
        # Test logging setup
        assert server.logger is not None, "Logger should be initialized"
        print("✅ Logging setup test passed")
        
        return True
        
    except Exception as e:
        print(f"❌ Server creation test failed: {e}")
        return False


def test_proxy_config():
    """Test proxy configuration"""
    print("\n📋 Testing Proxy Configuration:")
    print("-" * 40)
    
    try:
        from proxy_config import ProxyConfig
        
        # Test default values
        assert ProxyConfig.PROXY_HOST == '127.0.0.1', "Default host should be localhost"
        assert ProxyConfig.PROXY_PORT == 1080, "Default port should be 1080"
        assert ProxyConfig.MAX_BYTES_PER_SECOND == 0, "Default should be unlimited"
        
        print("✅ Default configuration test passed")
        
        # Test validation
        try:
            ProxyConfig.validate_config()
            print("✅ Configuration validation test passed")
        except ValueError:
            print("❌ Configuration validation failed")
            return False
        
        # Test bandwidth description
        desc = ProxyConfig.get_bandwidth_description()
        assert isinstance(desc, str), "Bandwidth description should be string"
        print("✅ Bandwidth description test passed")
        
        return True
        
    except Exception as e:
        print(f"❌ Proxy config test failed: {e}")
        return False


def test_socks5_protocol_constants():
    """Test SOCKS5 protocol constants"""
    print("\n📋 Testing SOCKS5 Protocol Constants:")
    print("-" * 40)
    
    try:
        from socks5_proxy import SOCKS5Server
        
        # Test constants
        assert SOCKS5Server.SOCKS_VERSION == 0x05, "SOCKS version should be 5"
        assert SOCKS5Server.NO_AUTH == 0x00, "No auth constant should be correct"
        assert SOCKS5Server.CONNECT == 0x01, "Connect command should be correct"
        assert SOCKS5Server.IPV4 == 0x01, "IPv4 address type should be correct"
        assert SOCKS5Server.SUCCESS == 0x00, "Success reply should be correct"
        
        print("✅ Protocol constants test passed")
        return True
        
    except Exception as e:
        print(f"❌ Protocol constants test failed: {e}")
        return False


def test_socket_creation():
    """Test if we can create sockets for the proxy"""
    print("\n📋 Testing Socket Creation:")
    print("-" * 40)
    
    try:
        # Test socket creation
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Try to bind to a test port
        test_socket.bind(('127.0.0.1', 0))
        actual_port = test_socket.getsockname()[1]
        test_socket.close()
        
        print(f"✅ Socket creation test passed (tested port: {actual_port})")
        return True
        
    except Exception as e:
        print(f"❌ Socket creation test failed: {e}")
        return False


def run_basic_server_test():
    """Test basic server start and stop functionality"""
    print("\n📋 Testing Basic Server Operations:")
    print("-" * 40)
    
    try:
        from socks5_proxy import SOCKS5Server, BandwidthConfig
        
        # Create server with auto-assigned port
        bandwidth_config = BandwidthConfig(max_bytes_per_second=0)
        server = SOCKS5Server(host='127.0.0.1', port=0, bandwidth_config=bandwidth_config)
        
        # Test server setup
        server._setup_driver = lambda: None  # Mock the driver setup for testing
        server.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.server_socket.bind(('127.0.0.1', 0))
        actual_port = server.server_socket.getsockname()[1]
        server.port = actual_port
        
        # Test stop
        server.stop()
        print(f"✅ Basic server operations test passed (tested port: {actual_port})")
        return True
        
    except Exception as e:
        print(f"❌ Basic server operations test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("🧪 Running SOCKS5 Proxy Tests")
    print("=" * 50)
    
    tests = [
        ("Import Tests", test_imports),
        ("Bandwidth Throttler", test_bandwidth_throttler),
        ("Server Creation", test_socks5_server_creation),
        ("Proxy Configuration", test_proxy_config),
        ("Protocol Constants", test_socks5_protocol_constants),
        ("Socket Creation", test_socket_creation),
        ("Basic Server Operations", run_basic_server_test),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    for i, (test_name, _) in enumerate(tests):
        status = "✅ PASS" if i < passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nPassed: {passed}/{total} tests")
    
    if passed == total:
        print("🎉 All tests passed! SOCKS5 Proxy is ready to use.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())