#!/usr/bin/env python3
"""
Health check script for Facebook Messenger Bot
Used by Docker and monitoring systems to verify bot status
"""

import os
import sys
import time
import json
from datetime import datetime, timedelta

def check_log_file():
    """Check if the bot has logged activity recently"""
    # Try different possible log file locations
    possible_log_paths = [
        '/app/logs/messenger_bot.log',  # Docker
        'logs/messenger_bot.log',       # Local/VPS
        './logs/messenger_bot.log',     # Current directory
        'messenger_bot.log'             # Legacy location
    ]
    
    log_file = None
    for path in possible_log_paths:
        if os.path.exists(path):
            log_file = path
            break
    
    if not log_file:
        # If no logs directory exists, create it
        log_dir = '/app/logs' if os.path.exists('/app') else 'logs'
        os.makedirs(log_dir, exist_ok=True)
        return False
        
    try:
        # Check if log file was modified in the last 10 minutes
        file_mtime = os.path.getmtime(log_file)
        current_time = time.time()
        
        # If log file is older than 10 minutes, consider it unhealthy
        if current_time - file_mtime > 600:  # 10 minutes
            return False
            
        # Check for recent error patterns in logs
        with open(log_file, 'r') as f:
            # Read last 50 lines
            lines = f.readlines()[-50:]
            recent_lines = ''.join(lines)
            
            # Look for critical errors
            critical_errors = [
                'CRITICAL',
                'Failed to setup WebDriver',
                'Failed to login to Facebook',
                'Bot failed with error'
            ]
            
            for error in critical_errors:
                if error in recent_lines:
                    return False
                    
        return True
        
    except Exception:
        return False

def check_process_status():
    """Check if the main bot process is running"""
    try:
        # Try different possible status file locations
        possible_status_paths = [
            '/app/logs/bot_status.json',  # Docker
            'logs/bot_status.json',       # Local/VPS
            './logs/bot_status.json'      # Current directory
        ]
        
        status_file = None
        for path in possible_status_paths:
            if os.path.exists(path):
                status_file = path
                break
        
        if not status_file:
            return False
            
        with open(status_file, 'r') as f:
            status = json.load(f)
            
        last_heartbeat = datetime.fromisoformat(status.get('last_heartbeat', ''))
        current_time = datetime.now()
        
        # If last heartbeat is older than 15 minutes, consider unhealthy
        if current_time - last_heartbeat > timedelta(minutes=15):
            return False
            
        return status.get('status') == 'running'
        
    except Exception:
        return False

def main():
    """Main health check function"""
    try:
        log_healthy = check_log_file()
        process_healthy = check_process_status()
        
        # Health check passes if either log shows activity or process status is good
        if log_healthy or process_healthy:
            print("Health check: HEALTHY")
            return 0
        else:
            print("Health check: UNHEALTHY")
            return 1
            
    except Exception as e:
        print(f"Health check: ERROR - {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())