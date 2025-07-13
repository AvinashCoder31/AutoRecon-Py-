#!/usr/bin/env python3
"""
Subdomain Enumeration Module
Performs subdomain discovery using multiple techniques
"""

import os
import requests
import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from colorama import Fore, Style

class SubdomainEnumerator:
    def __init__(self, target, output_dir):
        self.target = target
        self.output_dir = output_dir
        self.subdomains = set()
        self.lock = threading.Lock()
        
        # Common subdomains wordlist
        self.common_subdomains = [
            'www', 'mail', 'ftp', 'localhost', 'webmail', 'smtp', 'pop', 'ns1', 'webdisk',
            'ns2', 'cpanel', 'whm', 'autodiscover', 'autoconfig', 'admin', 'api', 'blog',
            'dev', 'test', 'staging', 'demo', 'app', 'mobile', 'secure', 'vpn', 'remote',
            'support', 'help', 'portal', 'shop', 'store', 'forum', 'wiki', 'news',
            'cdn', 'static', 'img', 'images', 'upload', 'download', 'assets', 'media',
            'beta', 'alpha', 'stage', 'prod', 'production', 'development', 'server',
            'backup', 'old', 'new', 'archive', 'files', 'docs', 'documentation',
            'status', 'monitor', 'stats', 'analytics', 'tracking', 'ads', 'ad',
            'mx', 'mail1', 'mail2', 'email', 'exchange', 'imap', 'pop3', 'webmail',
            'mysql', 'sql', 'database', 'db', 'phpmyadmin', 'adminer', 'pma',
            'jenkins', 'ci', 'build', 'deploy', 'git', 'svn', 'repo', 'code',
            'internal', 'intranet', 'extranet', 'private', 'public', 'external',
            'sso', 'auth', 'login', 'signin', 'signup', 'register', 'oauth',
            'chat', 'voice', 'video', 'call', 'conference', 'meet', 'zoom',
            'calendar', 'cal', 'schedule', 'booking', 'appointment', 'reserve',
            'crm', 'erp', 'hr', 'payroll', 'finance', 'accounting', 'billing',
            'payment', 'checkout', 'cart', 'order', 'invoice', 'receipt'
        ]
    
    def check_subdomain(self, subdomain):
        """Check if a subdomain exists"""
        full_domain = f"{subdomain}.{self.target}"
        try:
            # Try HTTP first
            response = requests.get(f"http://{full_domain}", timeout=5, allow_redirects=True)
            if response.status_code < 400:
                with self.lock:
                    self.subdomains.add(full_domain)
                return full_domain
        except:
            pass
        
        try:
            # Try HTTPS
            response = requests.get(f"https://{full_domain}", timeout=5, allow_redirects=True, verify=False)
            if response.status_code < 400:
                with self.lock:
                    self.subdomains.add(full_domain)
                return full_domain
        except:
            pass
        
        # Try DNS resolution as fallback
        try:
            import socket
            socket.gethostbyname(full_domain)
            with self.lock:
                self.subdomains.add(full_domain)
            return full_domain
        except:
            pass
        
        return None
    
    def brute_force_subdomains(self, max_threads=20):
        """Brute force common subdomains"""
        print(f"{Fore.BLUE}[INFO] Starting subdomain brute force...{Style.RESET_ALL}")
        
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            future_to_subdomain = {
                executor.submit(self.check_subdomain, subdomain): subdomain 
                for subdomain in self.common_subdomains
            }
            
            for future in as_completed(future_to_subdomain):
                subdomain = future_to_subdomain[future]
                try:
                    result = future.result()
                    if result:
                        print(f"{Fore.GREEN}[+] Found: {result}{Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.RED}[-] Error checking {subdomain}: {str(e)}{Style.RESET_ALL}")
    
    def check_certificate_transparency(self):
        """Check Certificate Transparency logs"""
        print(f"{Fore.BLUE}[INFO] Checking Certificate Transparency logs...{Style.RESET_ALL}")
        
        try:
            # crt.sh API
            url = f"https://crt.sh/?q=%.{self.target}&output=json"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                for entry in data:
                    common_name = entry.get('common_name', '')
                    if common_name and common_name.endswith(self.target):
                        with self.lock:
                            self.subdomains.add(common_name)
                        print(f"{Fore.GREEN}[+] CT Log: {common_name}{Style.RESET_ALL}")
                    
                    # Check Subject Alternative Names
                    name_value = entry.get('name_value', '')
                    if name_value:
                        for name in name_value.split('\n'):
                            name = name.strip()
                            if name and name.endswith(self.target) and '*' not in name:
                                with self.lock:
                                    self.subdomains.add(name)
                                print(f"{Fore.GREEN}[+] CT Log SAN: {name}{Style.RESET_ALL}")
        
        except Exception as e:
            print(f"{Fore.YELLOW}[WARNING] Certificate Transparency check failed: {str(e)}{Style.RESET_ALL}")
    
    def use_subfinder(self):
        """Use subfinder if available"""
        print(f"{Fore.BLUE}[INFO] Attempting to use subfinder...{Style.RESET_ALL}")
        
        try:
            result = subprocess.run(
                ['subfinder', '-d', self.target, '-silent'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        with self.lock:
                            self.subdomains.add(line.strip())
                        print(f"{Fore.GREEN}[+] Subfinder: {line.strip()}{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}[WARNING] Subfinder not available or failed{Style.RESET_ALL}")
        
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print(f"{Fore.YELLOW}[WARNING] Subfinder not available{Style.RESET_ALL}")
    
    def use_sublist3r(self):
        """Use Sublist3r if available"""
        print(f"{Fore.BLUE}[INFO] Attempting to use Sublist3r...{Style.RESET_ALL}")
        
        try:
            result = subprocess.run(
                ['python3', '-c', f"""
import sublist3r
subdomains = sublist3r.main('{self.target}', 40, None, ports=None, silent=True, verbose=False, enable_bruteforce=False, engines=None)
for subdomain in subdomains:
    print(subdomain)
"""],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        with self.lock:
                            self.subdomains.add(line.strip())
                        print(f"{Fore.GREEN}[+] Sublist3r: {line.strip()}{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}[WARNING] Sublist3r not available or failed{Style.RESET_ALL}")
        
        except (subprocess.TimeoutExpired, FileNotFoundError, ImportError):
            print(f"{Fore.YELLOW}[WARNING] Sublist3r not available{Style.RESET_ALL}")
    
    def use_amass(self):
        """Use Amass if available"""
        print(f"{Fore.BLUE}[INFO] Attempting to use Amass...{Style.RESET_ALL}")
        
        try:
            result = subprocess.run(
                ['amass', 'enum', '-d', self.target, '-timeout', '5'],
                capture_output=True,
                text=True,
                timeout=180
            )
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        with self.lock:
                            self.subdomains.add(line.strip())
                        print(f"{Fore.GREEN}[+] Amass: {line.strip()}{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}[WARNING] Amass not available or failed{Style.RESET_ALL}")
        
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print(f"{Fore.YELLOW}[WARNING] Amass not available{Style.RESET_ALL}")
    
    def load_wordlist(self):
        """Load wordlist from config if available"""
        wordlist_path = os.path.join("config", "wordlists.txt")
        additional_subdomains = []
        
        if os.path.exists(wordlist_path):
            try:
                with open(wordlist_path, 'r') as f:
                    additional_subdomains = [line.strip() for line in f if line.strip()]
                print(f"{Fore.BLUE}[INFO] Loaded {len(additional_subdomains)} entries from wordlist{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.YELLOW}[WARNING] Could not load wordlist: {str(e)}{Style.RESET_ALL}")
        
        return additional_subdomains
    
    def save_results(self):
        """Save subdomain enumeration results"""
        output_file = os.path.join(self.output_dir, "subdomains.txt")
        
        try:
            with open(output_file, 'w') as f:
                for subdomain in sorted(self.subdomains):
                    f.write(f"{subdomain}\n")
            
            print(f"{Fore.GREEN}[+] Subdomains saved to: {output_file}{Style.RESET_ALL}")
        
        except Exception as e:
            print(f"{Fore.RED}[ERROR] Could not save results: {str(e)}{Style.RESET_ALL}")
    
    def enumerate(self):
        """Run all subdomain enumeration techniques"""
        print(f"{Fore.CYAN}Starting subdomain enumeration for {self.target}{Style.RESET_ALL}")
        
        # Load additional wordlist
        additional_subdomains = self.load_wordlist()
        if additional_subdomains:
            self.common_subdomains.extend(additional_subdomains)
        
        # Remove duplicates
        self.common_subdomains = list(set(self.common_subdomains))
        
        # Run different enumeration methods
        threads = []
        
        # Certificate Transparency
        ct_thread = threading.Thread(target=self.check_certificate_transparency)
        ct_thread.start()
        threads.append(ct_thread)
        
        # External tools (run in separate threads)
        tools_thread = threading.Thread(target=self._run_external_tools)
        tools_thread.start()
        threads.append(tools_thread)
        
        # Brute force (run in main thread to control output)
        self.brute_force_subdomains()
        
        # Wait for other threads to complete
        for thread in threads:
            thread.join()
        
        # Remove main domain from results if it exists
        self.subdomains.discard(self.target)
        
        # Save results
        self.save_results()
        
        print(f"{Fore.GREEN}[+] Subdomain enumeration complete. Found {len(self.subdomains)} subdomains.{Style.RESET_ALL}")
        
        return sorted(list(self.subdomains))
    
    def _run_external_tools(self):
        """Run external tools in parallel"""
        tool_threads = []
        
        # Subfinder
        subfinder_thread = threading.Thread(target=self.use_subfinder)
        subfinder_thread.start()
        tool_threads.append(subfinder_thread)
        
        # Sublist3r
        sublist3r_thread = threading.Thread(target=self.use_sublist3r)
        sublist3r_thread.start()
        tool_threads.append(sublist3r_thread)
        
        # Amass
        amass_thread = threading.Thread(target=self.use_amass)
        amass_thread.start()
        tool_threads.append(amass_thread)
        
        # Wait for all tool threads
        for thread in tool_threads:
            thread.join()