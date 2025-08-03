"""
Test script to receive broadcast packets from Euler system.
"""
import os
import sys
from pathlib import Path
import socket
from datetime import datetime

# Add project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.insert(0, project_root)

def main():
    """Listen for market analysis broadcasts."""
    # Create UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Allow reuse of address/port
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    # Set socket timeout to handle regular updates
    sock.settimeout(1.0)
    
    # Bind to address and port
    server_address = ('', 5000)  # Bind to all interfaces
    print(f'\nStarting Euler Market Analysis Monitor on port 5000')
    print('Press Ctrl+C to exit\n')
    sock.bind(server_address)
    
    last_regime = None
    last_update = None
    
    try:
        while True:
            try:
                data, addr = sock.recvfrom(4096)
                message = data.decode()
                current_time = datetime.now()
                
                print(f"\nReceived from {addr}: {message}")  # Debug line
                
                # Parse message
                # Format: EULER|score|regime
                try:
                    parts = message.split('|')
                    if len(parts) == 3 and parts[0] == 'EULER':
                        score = float(parts[1])
                        regime = parts[2]
                        
                        # Check if regime changed or if it's been more than 30 seconds
                        if (regime != last_regime or 
                            last_update is None or 
                            (current_time - last_update).total_seconds() >= 30):
                            
                            if regime != last_regime:
                                print('\n' + '=' * 80)
                                print(f'MARKET REGIME CHANGE DETECTED at {current_time.strftime("%Y-%m-%d %H:%M:%S")}')
                                print('=' * 80)
                            
                            print(f'Current Risk Score: {score:6.2f} | Regime: {regime}')
                            last_update = current_time
                            
                        last_regime = regime
                    else:
                        print(f'Invalid message format: {message}')
                except Exception as e:
                    print(f'Error parsing message: {str(e)}')
                    print(f'Raw message: {message}')
                    
            except socket.timeout:
                # No data received, print a dot to show we're still alive
                print('.', end='', flush=True)
                continue
            except Exception as e:
                print(f'\nError receiving data: {str(e)}')
                continue

    except KeyboardInterrupt:
        print('\n\nShutting down...')
    finally:
        print('Closing socket')
        sock.close()

if __name__ == '__main__':
    main() 