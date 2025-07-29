#!/usr/bin/env python3
"""
Command-line wrapper for SOCKS5 Proxy Server
"""
import sys
import os
import argparse
import signal
import threading
import time

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from socks5_proxy import SOCKS5Server, BandwidthConfig
from proxy_config import ProxyConfig


def signal_handler(sig, frame):
    """Handle shutdown signals gracefully"""
    print("\n🛑 Received shutdown signal...")
    sys.exit(0)


def print_banner():
    """Print application banner"""
    print("=" * 60)
    print("🌐 SOCKS5 Proxy Server with Bandwidth Control")
    print("   Created for Local Repository - helena1994/Local")
    print("=" * 60)


def check_environment():
    """Check if environment is properly set up"""
    try:
        ProxyConfig.validate_config()
        print("✅ Configuration validation passed")
        return True
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        return False


def format_bytes(bytes_value: int) -> str:
    """Format bytes to human readable string"""
    if bytes_value == 0:
        return "unlimited"
    
    units = ['B', 'KB', 'MB', 'GB']
    unit_index = 0
    value = float(bytes_value)
    
    while value >= 1024 and unit_index < len(units) - 1:
        value /= 1024
        unit_index += 1
    
    if unit_index == 0:
        return f"{int(value)} {units[unit_index]}"
    else:
        return f"{value:.2f} {units[unit_index]}"


def show_stats(server: SOCKS5Server):
    """Show server statistics in a separate thread"""
    while server.running:
        time.sleep(30)  # Update every 30 seconds
        uptime = time.time() - server.start_time.timestamp()
        uptime_str = f"{int(uptime // 3600)}h {int((uptime % 3600) // 60)}m {int(uptime % 60)}s"
        
        print(f"\n📊 Stats: {server.client_count} clients, "
              f"{format_bytes(server.total_bytes_transferred)} transferred, "
              f"uptime: {uptime_str}")


def main():
    """Main command-line interface"""
    parser = argparse.ArgumentParser(
        description='SOCKS5 Proxy Server with Bandwidth Throttling',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_proxy.py                          # Run with default settings
  python run_proxy.py --host 0.0.0.0 --port 8080  # Custom host/port
  python run_proxy.py --bps 1048576            # Limit to 1 MB/s
  python run_proxy.py --bps 102400 --burst 512000  # 100 KB/s with 500 KB burst
  python run_proxy.py --check-config           # Check configuration only
  
Environment variables (optional):
  PROXY_HOST              Server host (default: 127.0.0.1)
  PROXY_PORT              Server port (default: 1080)
  MAX_BYTES_PER_SECOND    Bandwidth limit in bytes/sec (default: 0 = unlimited)
  BURST_SIZE              Burst allowance in bytes (default: 0)
  MAX_CONNECTIONS         Maximum concurrent connections (default: 100)
  CONNECTION_TIMEOUT      Connection timeout in seconds (default: 10)
  LOG_LEVEL               Logging level (default: INFO)
        """
    )
    
    parser.add_argument(
        '--host',
        default=ProxyConfig.PROXY_HOST,
        help=f'Host to bind to (default: {ProxyConfig.PROXY_HOST})'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=ProxyConfig.PROXY_PORT,
        help=f'Port to bind to (default: {ProxyConfig.PROXY_PORT})'
    )
    
    parser.add_argument(
        '--bps',
        type=int,
        default=ProxyConfig.MAX_BYTES_PER_SECOND,
        help='Bandwidth limit in bytes per second (0 = unlimited)'
    )
    
    parser.add_argument(
        '--burst',
        type=int,
        default=ProxyConfig.BURST_SIZE,
        help='Burst size in bytes (default: 0)'
    )
    
    parser.add_argument(
        '--timeout',
        type=int,
        default=ProxyConfig.CONNECTION_TIMEOUT,
        help='Connection timeout in seconds'
    )
    
    parser.add_argument(
        '--max-connections',
        type=int,
        default=ProxyConfig.MAX_CONNECTIONS,
        help='Maximum concurrent connections'
    )
    
    parser.add_argument(
        '--check-config',
        action='store_true',
        help='Check configuration and exit'
    )
    
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show periodic statistics'
    )
    
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Reduce output verbosity'
    )
    
    args = parser.parse_args()
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    if not args.quiet:
        print_banner()
    
    # Override config with command line arguments
    if args.host != ProxyConfig.PROXY_HOST:
        os.environ['PROXY_HOST'] = args.host
    if args.port != ProxyConfig.PROXY_PORT:
        os.environ['PROXY_PORT'] = str(args.port)
    if args.bps != ProxyConfig.MAX_BYTES_PER_SECOND:
        os.environ['MAX_BYTES_PER_SECOND'] = str(args.bps)
    if args.burst != ProxyConfig.BURST_SIZE:
        os.environ['BURST_SIZE'] = str(args.burst)
    if args.timeout != ProxyConfig.CONNECTION_TIMEOUT:
        os.environ['CONNECTION_TIMEOUT'] = str(args.timeout)
    if args.max_connections != ProxyConfig.MAX_CONNECTIONS:
        os.environ['MAX_CONNECTIONS'] = str(args.max_connections)
    
    # Reload config with new values
    ProxyConfig.PROXY_HOST = args.host
    ProxyConfig.PROXY_PORT = args.port
    ProxyConfig.MAX_BYTES_PER_SECOND = args.bps
    ProxyConfig.BURST_SIZE = args.burst
    ProxyConfig.CONNECTION_TIMEOUT = args.timeout
    ProxyConfig.MAX_CONNECTIONS = args.max_connections
    
    # Check configuration
    if not check_environment():
        return 1
    
    if not args.quiet:
        ProxyConfig.print_config()
        print()
    
    if args.check_config:
        print("✅ Configuration check passed!")
        return 0
    
    # Create bandwidth configuration
    bandwidth_config = BandwidthConfig(
        max_bytes_per_second=args.bps,
        burst_size=args.burst,
        reset_interval=1.0
    )
    
    # Create server
    server = SOCKS5Server(
        host=args.host,
        port=args.port,
        bandwidth_config=bandwidth_config
    )
    
    # Start statistics thread if requested
    stats_thread = None
    if args.stats and not args.quiet:
        stats_thread = threading.Thread(target=show_stats, args=(server,), daemon=True)
        stats_thread.start()
    
    print(f"🚀 Starting SOCKS5 proxy server on {args.host}:{args.port}")
    if args.bps > 0:
        print(f"📊 Bandwidth limit: {format_bytes(args.bps)}/s")
        if args.burst > 0:
            print(f"⚡ Burst allowance: {format_bytes(args.burst)}")
    else:
        print("📊 Bandwidth: unlimited")
    
    if not args.quiet:
        print("💡 Press Ctrl+C to stop the server")
        print("-" * 50)
    
    try:
        server.start()
        return 0
    except KeyboardInterrupt:
        if not args.quiet:
            print("\n⚠️  Server stopped by user")
        return 1
    except Exception as e:
        print(f"\n❌ Server failed with error: {str(e)}")
        return 1
    finally:
        server.stop()


if __name__ == "__main__":
    sys.exit(main())