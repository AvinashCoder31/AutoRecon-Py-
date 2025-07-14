#!/usr/bin/env python3
"""
Subdomain Enumeration Module
Performs subdomain discovery using multiple techniques
"""

import os
import json
import sys
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
        """Check if a subdomain exists by trying HTTP, HTTPS, and DNS resolution."""
        full_domain = f"{subdomain}.{self.target}"
        protocols = ['https', 'http']
        
        for protocol in protocols:
            try:
                response = requests.get(f"{protocol}://{full_domain}", timeout=5, allow_redirects=True, verify=False)
                if response.status_code < 400:
                    with self.lock:
                        self.subdomains.add(full_domain)
                    return full_domain
            except requests.exceptions.RequestException:
                continue # Try next protocol or fallback to DNS
        
        # Fallback to DNS resolution if web requests fail
        try:
            import socket
            socket.gethostbyname(full_domain)
            with self.lock:
                self.subdomains.add(full_domain)
            return full_domain
        except socket.gaierror:
            return None # Subdomain does not resolve
        
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
        
        except requests.exceptions.RequestException as e:
            print(f"{Fore.YELLOW}[WARNING] Certificate Transparency check failed: {e}{Style.RESET_ALL}")
        except json.JSONDecodeError:
            print(f"{Fore.YELLOW}[WARNING] Failed to decode JSON from crt.sh.{Style.RESET_ALL}")
    
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
                print(f"{Fore.YELLOW}[WARNING] Subfinder failed with exit code {result.returncode}:{Style.RESET_ALL}")
                if result.stderr:
                    print(f"{Fore.YELLOW}{result.stderr.strip()}{Style.RESET_ALL}")
        
        except FileNotFoundError:
            print(f"{Fore.YELLOW}[INFO] Subfinder not found. Skipping.{Style.RESET_ALL}")
        except subprocess.TimeoutExpired:
            print(f"{Fore.YELLOW}[WARNING] Subfinder timed out.{Style.RESET_ALL}")
    
    def use_sublist3r(self):
        """Use Sublist3r if available by importing it as a library."""
        print(f"{Fore.BLUE}[INFO] Attempting to use Sublist3r...{Style.RESET_ALL}")
        try:
            import sublist3r
            # The sublist3r.main function is designed for command-line output,
            # so we capture its results by redirecting stdout.
            # This is still better than a subprocess call.
            found_subdomains = sublist3r.main(self.target, 40, savefile=None, ports=None, silent=True, verbose=False, enable_bruteforce=False, engines=None)
            
            if found_subdomains:
                for subdomain in found_subdomains:
                    with self.lock:
                        self.subdomains.add(subdomain)
                    print(f"{Fore.GREEN}[+] Sublist3r: {subdomain}{Style.RESET_ALL}")

        except ImportError:
            print(f"{Fore.YELLOW}[INFO] Sublist3r not installed. Skipping.{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}[ERROR] An error occurred with Sublist3r: {e}{Style.RESET_ALL}")
    
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
                print(f"{Fore.YELLOW}[WARNING] Amass failed with exit code {result.returncode}:{Style.RESET_ALL}")
                if result.stderr:
                    print(f"{Fore.YELLOW}{result.stderr.strip()}{Style.RESET_ALL}")
        
        except FileNotFoundError:
            print(f"{Fore.YELLOW}[INFO] Amass not found. Skipping.{Style.RESET_ALL}")
        except subprocess.TimeoutExpired:
            print(f"{Fore.YELLOW}[WARNING] Amass timed out.{Style.RESET_ALL}")
    
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
        
        # Remove main domain & wildcards / non-valid hostnames
        self.subdomains.discard(self.target)
        valid_subs = [s for s in self.subdomains
                      if '*' not in s and s.count('.') >= 1]
        self.subdomains = sorted(set(valid_subs))

        # Save results
        self.save_results()
        print(f"{Fore.GREEN}[+] Subdomain enumeration complete. "
              f"Found {len(self.subdomains)} valid subdomains.{Style.RESET_ALL}")
        return list(self.subdomains)
    
    def _run_external_tools(self):
        """Run external tools in parallel"""
        tool_threads = []
        
        # Subfinder
        subfinder_thread = threading.Thread(target=self.use_subfinder)
        subfinder_thread.start()
        tool_threads.append(subfinder_thread)
        
        # Sublist3r – silent stderr, keep stdout
        sublist3r_thread = threading.Thread(
            target=lambda: subprocess.run(
                [
                    sys.executable,
                    "-c",
                    "import sublist3r; [print(s) for s in sublist3r.main('{}',40,None,None,True,False,False,None)]"
                    .format(self.target)
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True
            ).stdout.splitlines()
        )
        sublist3r_thread.start()
        tool_threads.append(sublist3r_thread)
        
        # Amass
        amass_thread = threading.Thread(target=self.use_amass)
        amass_thread.start()
        tool_threads.append(amass_thread)
        
        # Wait for all tool threads
        for thread in tool_threads:
            thread.join()