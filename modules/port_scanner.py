#!/usr/bin/env python3
"""
Port Scanner Module
Performs port scanning using nmap and custom socket scanning
"""

import os
import socket
import subprocess
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from colorama import Fore, Style

class PortScanner:
    def __init__(self, output_dir, threads=10, timeout=10):
        self.output_dir = output_dir
        self.threads = threads
        self.timeout = timeout
        self.lock = threading.Lock()
        
        # Common ports to scan
        self.common_ports = [
            21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 993, 995,
            1723, 3306, 3389, 5432, 5900, 6000, 6001, 6002, 6003, 6004, 6005,
            6006, 6007, 6008, 6009, 8000, 8080, 8443, 8888, 9000, 9001, 9002,
            9003, 9004, 9005, 9006, 9007, 9008, 9009, 9010, 9011, 9012, 9013,
            9014, 9015, 9016, 9017, 9018, 9019, 9020, 9021, 9022, 9023, 9024,
            9025, 9026, 9027, 9028, 9029, 9030, 9031, 9032, 9033, 9034, 9035,
            9036, 9037, 9038, 9039, 9040, 9041, 9042, 9043, 9044, 9045, 9046,
            9047, 9048, 9049, 9050, 9051, 9052, 9053, 9054, 9055, 9056, 9057,
            9058, 9059, 9060, 9061, 9062, 9063, 9064, 9065, 9066, 9067, 9068,
            9069, 9070, 9071, 9072, 9073, 9074, 9075, 9076, 9077, 9078, 9079,
            9080, 9081, 9082, 9083, 9084, 9085, 9086, 9087, 9088, 9089, 9090,
            9091, 9092, 9093, 9094, 9095, 9096, 9097, 9098, 9099, 9100
        ]
        
        # Top 1000 ports for comprehensive scanning
        self.top_ports = [
            1, 3, 4, 6, 7, 9, 13, 17, 19, 20, 21, 22, 23, 24, 25, 26, 30, 32, 33,
            37, 42, 43, 49, 53, 70, 79, 80, 81, 82, 83, 84, 85, 88, 89, 90, 99,
            100, 106, 109, 110, 111, 113, 119, 125, 135, 139, 143, 144, 146, 161,
            163, 179, 199, 211, 212, 222, 254, 255, 256, 259, 264, 280, 301, 306,
            311, 340, 366, 389, 406, 407, 416, 417, 425, 427, 443, 444, 445, 458,
            464, 465, 481, 497, 500, 512, 513, 514, 515, 524, 541, 543, 544, 545,
            548, 554, 555, 563, 587, 593, 616, 617, 625, 631, 636, 646, 648, 666,
            667, 668, 683, 687, 691, 700, 705, 720, 749, 993, 995, 1025, 1026,
            1027, 1028, 1029, 1110, 1433, 1720, 1723, 1755, 1900, 2000, 2001,
            2049, 2121, 2717, 3000, 3128, 3306, 3389, 3986, 4899, 5000, 5009,
            5051, 5060, 5101, 5190, 5357, 5432, 5631, 5666, 5800, 5900, 6000,
            6001, 6646, 7070, 8000, 8008, 8009, 8080, 8081, 8443, 8888, 9100,
            9999, 10000, 32768, 49152, 49153, 49154, 49155, 49156, 49157
        ]
        
        # Service identification map
        self.service_map = {
            21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS", 80: "HTTP",
            110: "POP3", 111: "RPC", 135: "RPC", 139: "NetBIOS", 143: "IMAP",
            443: "HTTPS", 993: "IMAPS", 995: "POP3S", 1433: "MSSQL", 1521: "Oracle",
            3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL", 5900: "VNC", 6000: "X11",
            8000: "HTTP-Alt", 8080: "HTTP-Proxy", 8443: "HTTPS-Alt", 8888: "HTTP-Alt"
        }
    
    def scan_port(self, target, port):
        """Scan a single port"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((target, port))
            sock.close()
            
            if result == 0:
                service = self.service_map.get(port, "Unknown")
                return f"Port {port}/tcp open ({service})"
            
        except socket.gaierror:
            return None
        except Exception as e:
            return None
        
        return None
    
    def socket_scan(self, target, ports=None):
        """Perform socket-based port scanning"""
        if ports is None:
            ports = self.common_ports
        
        print(f"{Fore.BLUE}[INFO] Socket scanning {target} ({len(ports)} ports)...{Style.RESET_ALL}")
        
        open_ports = []
        
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            future_to_port = {
                executor.submit(self.scan_port, target, port): port
                for port in ports
            }
            
            for future in as_completed(future_to_port):
                port = future_to_port[future]
                try:
                    result = future.result()
                    if result:
                        open_ports.append(result)
                        print(f"{Fore.GREEN}[+] {result}{Style.RESET_ALL}")
                except Exception as e:
                    pass
        
        return open_ports
    
    def nmap_scan(self, target, scan_type="basic"):
        """Perform nmap scanning if available"""
        print(f"{Fore.BLUE}[INFO] Nmap scanning {target}...{Style.RESET_ALL}")
        
        # Different nmap scan types
        scan_commands = {
            "basic": ["nmap", "-sS", "-O", "-sV", "--top-ports", "1000"],
            "fast": ["nmap", "-T4", "-F"],
            "comprehensive": ["nmap", "-sS", "-sU", "-O", "-sV", "-sC", "--top-ports", "1000"],
            "stealth": ["nmap", "-sS", "-T2", "--top-ports", "100"]
        }
        
        cmd = scan_commands.get(scan_type, scan_commands["basic"])
        cmd.append(target)
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            if result.returncode == 0:
                output_lines = result.stdout.split('\n')
                open_ports = []
                
                for line in output_lines:
                    if "/tcp" in line and "open" in line:
                        open_ports.append(line.strip())
                        print(f"{Fore.GREEN}[+] Nmap: {line.strip()}{Style.RESET_ALL}")
                    elif "/udp" in line and "open" in line:
                        open_ports.append(line.strip())
                        print(f"{Fore.GREEN}[+] Nmap: {line.strip()}{Style.RESET_ALL}")
                
                # Save full nmap output
                nmap_output_file = os.path.join(self.output_dir, f"nmap_{target}.txt")
                with open(nmap_output_file, 'w') as f:
                    f.write(result.stdout)
                
                return open_ports
            else:
                print(f"{Fore.YELLOW}[WARNING] Nmap scan failed for {target} with exit code {result.returncode}{Style.RESET_ALL}")
                if result.stderr:
                    print(f"{Fore.YELLOW}{result.stderr.strip()}{Style.RESET_ALL}")
                return []
                
        except FileNotFoundError:
            print(f"{Fore.YELLOW}[INFO] Nmap not found. Skipping Nmap scan.{Style.RESET_ALL}")
            return []
        except subprocess.TimeoutExpired:
            print(f"{Fore.YELLOW}[WARNING] Nmap scan timed out for {target}{Style.RESET_ALL}")
            return []
        except Exception as e:
            print(f"{Fore.RED}[ERROR] An unexpected error occurred with Nmap: {e}{Style.RESET_ALL}")
            return []
    
    def masscan_scan(self, target):
        """Perform masscan if available (very fast port scanner)"""
        print(f"{Fore.BLUE}[INFO] Masscan scanning {target}...{Style.RESET_ALL}")
        
        try:
            result = subprocess.run(
                ["masscan", "-p1-65535", target, "--rate=100", "--wait=0"],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                open_ports = []
                for line in result.stdout.split('\n'):
                    if "open" in line and "tcp" in line:
                        open_ports.append(line.strip())
                        print(f"{Fore.GREEN}[+] Masscan: {line.strip()}{Style.RESET_ALL}")
                
                return open_ports
            else:
                print(f"{Fore.YELLOW}[WARNING] Masscan failed for {target} with exit code {result.returncode}{Style.RESET_ALL}")
                if result.stderr:
                    print(f"{Fore.YELLOW}{result.stderr.strip()}{Style.RESET_ALL}")
                return []
                
        except FileNotFoundError:
            print(f"{Fore.YELLOW}[INFO] Masscan not found. Skipping.{Style.RESET_ALL}")
            return []
        except subprocess.TimeoutExpired:
            print(f"{Fore.YELLOW}[WARNING] Masscan scan timed out for {target}{Style.RESET_ALL}")
            return []
        except Exception as e:
            print(f"{Fore.RED}[ERROR] An unexpected error occurred with Masscan: {e}{Style.RESET_ALL}")
            return []
    
    def unicornscan_scan(self, target):
        """Perform unicornscan if available"""
        print(f"{Fore.BLUE}[INFO] Unicornscan scanning {target}...{Style.RESET_ALL}")
        
        try:
            result = subprocess.run(
                ["unicornscan", "-mT", "-I", target],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                open_ports = []
                for line in result.stdout.split('\n'):
                    if "open" in line:
                        open_ports.append(line.strip())
                        print(f"{Fore.GREEN}[+] Unicornscan: {line.strip()}{Style.RESET_ALL}")
                
                return open_ports
            else:
                print(f"{Fore.YELLOW}[WARNING] Unicornscan failed for {target} with exit code {result.returncode}{Style.RESET_ALL}")
                if result.stderr:
                    print(f"{Fore.YELLOW}{result.stderr.strip()}{Style.RESET_ALL}")
                return []
                
        except FileNotFoundError:
            print(f"{Fore.YELLOW}[INFO] Unicornscan not found. Skipping.{Style.RESET_ALL}")
            return []
        except subprocess.TimeoutExpired:
            print(f"{Fore.YELLOW}[WARNING] Unicornscan timed out for {target}{Style.RESET_ALL}")
            return []
        except Exception as e:
            print(f"{Fore.RED}[ERROR] An unexpected error occurred with Unicornscan: {e}{Style.RESET_ALL}")
            return []
    
    def banner_grab(self, target, port):
        """Grab banner from open port"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((target, port))
            
            # Send HTTP request for web ports
            if port in [80, 8000, 8080, 8888]:
                sock.send(b"GET / HTTP/1.1\r\nHost: " + target.encode() + b"\r\n\r\n")
            elif port == 443:
                # For HTTPS, we'd need SSL context
                pass
            elif port == 22:
                # SSH banner is sent automatically
                pass
            elif port == 21:
                # FTP banner is sent automatically
                pass
            else:
                sock.send(b"\r\n")
            
            banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
            sock.close()
            
            if banner:
                return banner[:200]  # Limit banner length
            
        except socket.timeout:
            return "Banner grab timed out"
        except Exception:
            return None
        
        return None
    
    def scan_target(self, target):
        """Perform comprehensive port scanning on a target"""
        print(f"{Fore.CYAN}Starting port scan for {target}{Style.RESET_ALL}")
        
        all_results = []
        
        # Try different scanning methods
        methods = [
            ("nmap", self.nmap_scan),
            ("masscan", self.masscan_scan),
            ("socket", lambda t: self.socket_scan(t, self.common_ports))
        ]
        
        for method_name, method_func in methods:
            try:
                results = method_func(target)
                if results:
                    all_results.extend(results)
                    break  # If we get results, don't try other methods
            except Exception as e:
                print(f"{Fore.RED}[ERROR] {method_name} scan failed: {str(e)}{Style.RESET_ALL}")
                continue
        
        # Remove duplicates while preserving order
        unique_results = []
        seen = set()
        for result in all_results:
            if result not in seen:
                unique_results.append(result)
                seen.add(result)
        
        # Banner grabbing for open ports
        print(f"{Fore.BLUE}[INFO] Performing banner grabbing...{Style.RESET_ALL}")
        enhanced_results = []
        
        for result in unique_results:
            try:
                # Extract port number from result
                port_str = result.split('/')[0]
                if port_str.isdigit():
                    port = int(port_str)
                    banner = self.banner_grab(target, port)
                    if banner:
                        enhanced_result = f"{result} - Banner: {banner}"
                        enhanced_results.append(enhanced_result)
                        print(f"{Fore.GREEN}[+] Banner: {target}:{port} - {banner[:50]}...{Style.RESET_ALL}")
                    else:
                        enhanced_results.append(result)
                else:
                    enhanced_results.append(result)
            except (ValueError, IndexError):
                # Handle cases where port parsing might fail
                enhanced_results.append(result)
        
        # Save results
        self.save_scan_results(target, enhanced_results)
        
        print(f"{Fore.GREEN}[+] Port scan complete for {target}. Found {len(enhanced_results)} open ports.{Style.RESET_ALL}")
        
        return enhanced_results
    
    def save_scan_results(self, target, results):
        """Save port scan results to file"""
        output_file = os.path.join(self.output_dir, f"ports_{target}.txt")
        
        try:
            with open(output_file, 'w') as f:
                f.write(f"Port Scan Results for {target}\n")
                f.write("=" * 50 + "\n\n")
                
                for result in results:
                    f.write(f"{result}\n")
                
                f.write(f"\nTotal open ports: {len(results)}\n")
                f.write(f"Scan completed: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            print(f"{Fore.GREEN}[+] Port scan results saved to: {output_file}{Style.RESET_ALL}")
        
        except Exception as e:
            print(f"{Fore.RED}[ERROR] Could not save port scan results: {str(e)}{Style.RESET_ALL}")
    
    def get_service_info(self, port):
        """Get service information for a port"""
        return self.service_map.get(port, "Unknown")
    
    def is_port_open(self, target, port, timeout=3):
        """Check if a specific port is open"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((target, port))
            sock.close()
            return result == 0
        except:
            return False