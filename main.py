#!/usr/bin/env python3
"""
AutoRecon-Py - Automated Reconnaissance Tool
A beginner-friendly Python-based automated reconnaissance tool for penetration testing.
"""

import argparse
import os
import sys
import time
from datetime import datetime
from colorama import init, Fore, Style
from modules.subdomain_enum import SubdomainEnumerator
from modules.port_scanner import PortScanner
from modules.tech_stack import TechStackDetector
from modules.screenshotter import WebScreenshotter

# Initialize colorama for cross-platform colored output
init()

class AutoRecon:
    def __init__(self, target, threads=5, output_dir="output"):
        self.target = target
        self.threads = threads
        self.output_dir = output_dir
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.target_output_dir = os.path.join(output_dir, f"{target}_{self.timestamp}")
        
        # Create output directories
        os.makedirs(self.target_output_dir, exist_ok=True)
        os.makedirs("screenshots", exist_ok=True)
        
        # Initialize modules
        self.subdomain_enum = SubdomainEnumerator(self.target, self.target_output_dir)
        self.port_scanner = PortScanner(self.target_output_dir, threads)
        self.tech_detector = TechStackDetector(self.target_output_dir)
        self.screenshotter = WebScreenshotter("screenshots")
        
        self.results = {
            'target': target,
            'timestamp': self.timestamp,
            'subdomains': [],
            'ports': {},
            'tech_stack': {},
            'screenshots': []
        }
    
    def print_banner(self):
        banner = f"""
{Fore.CYAN}
 █████╗ ██╗   ██╗████████╗ ██████╗ ██████╗ ███████╗ ██████╗ ██████╗ ███╗   ██╗
██╔══██╗██║   ██║╚══██╔══╝██╔═══██╗██╔══██╗██╔════╝██╔════╝██╔═══██╗████╗  ██║
███████║██║   ██║   ██║   ██║   ██║██████╔╝█████╗  ██║     ██║   ██║██╔██╗ ██║
██╔══██║██║   ██║   ██║   ██║   ██║██╔══██╗██╔══╝  ██║     ██║   ██║██║╚██╗██║
██║  ██║╚██████╔╝   ██║   ╚██████╔╝██║  ██║███████╗╚██████╗╚██████╔╝██║ ╚████║
╚═╝  ╚═╝ ╚═════╝    ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝
                                                                    
{Style.RESET_ALL}{Fore.YELLOW}AutoRecon-Py v1.0 - Automated Reconnaissance Tool{Style.RESET_ALL}
{Fore.GREEN}Target: {self.target}{Style.RESET_ALL}
{Fore.GREEN}Threads: {self.threads}{Style.RESET_ALL}
{Fore.GREEN}Output Directory: {self.target_output_dir}{Style.RESET_ALL}
{Fore.CYAN}{'='*70}{Style.RESET_ALL}
"""
        print(banner)
    
    def print_status(self, message, status="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        colors = {
            "INFO": Fore.BLUE,
            "SUCCESS": Fore.GREEN,
            "WARNING": Fore.YELLOW,
            "ERROR": Fore.RED
        }
        color = colors.get(status, Fore.WHITE)
        print(f"{color}[{timestamp}] [{status}] {message}{Style.RESET_ALL}")
    
    def run_subdomain_enumeration(self):
        self.print_status("Starting subdomain enumeration...", "INFO")
        try:
            subdomains = self.subdomain_enum.enumerate()
            self.results['subdomains'] = subdomains
            self.print_status(f"Found {len(subdomains)} subdomains", "SUCCESS")
            return subdomains
        except Exception as e:
            self.print_status(f"Subdomain enumeration failed: {str(e)}", "ERROR")
            return []
    
    def run_port_scanning(self, targets):
        self.print_status("Starting port scanning...", "INFO")
        try:
            all_results = {}
            for target in targets:
                self.print_status(f"Scanning ports for {target}...", "INFO")
                ports = self.port_scanner.scan_target(target)
                all_results[target] = ports
                self.print_status(f"Found {len(ports)} open ports on {target}", "SUCCESS")
            
            self.results['ports'] = all_results
            return all_results
        except Exception as e:
            self.print_status(f"Port scanning failed: {str(e)}", "ERROR")
            return {}
    
    def run_tech_detection(self, targets):
        self.print_status("Starting technology stack detection...", "INFO")
        try:
            all_results = {}
            for target in targets:
                self.print_status(f"Detecting tech stack for {target}...", "INFO")
                tech_info = self.tech_detector.detect_technologies(target)
                all_results[target] = tech_info
                if tech_info:
                    self.print_status(f"Detected technologies on {target}", "SUCCESS")
            
            self.results['tech_stack'] = all_results
            return all_results
        except Exception as e:
            self.print_status(f"Technology detection failed: {str(e)}", "ERROR")
            return {}
    
    def run_screenshot_capture(self, targets):
        self.print_status("Starting screenshot capture...", "INFO")
        try:
            screenshots = []
            for target in targets:
                self.print_status(f"Capturing screenshot for {target}...", "INFO")
                screenshot_path = self.screenshotter.capture_screenshot(target)
                if screenshot_path:
                    screenshots.append(screenshot_path)
                    self.print_status(f"Screenshot saved: {screenshot_path}", "SUCCESS")
            
            self.results['screenshots'] = screenshots
            return screenshots
        except Exception as e:
            self.print_status(f"Screenshot capture failed: {str(e)}", "ERROR")
            return []
    
    def generate_report(self):
        self.print_status("Generating reconnaissance report...", "INFO")
        report_path = os.path.join(self.target_output_dir, "recon_report.txt")
        
        with open(report_path, 'w') as f:
            f.write("="*70 + "\n")
            f.write(f"AutoRecon-Py Report for {self.target}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*70 + "\n\n")
            
            # Subdomains
            f.write(f"SUBDOMAINS FOUND ({len(self.results['subdomains'])}):\n")
            f.write("-" * 30 + "\n")
            for subdomain in self.results['subdomains']:
                f.write(f"  • {subdomain}\n")
            f.write("\n")
            
            # Port Scan Results
            f.write("PORT SCAN RESULTS:\n")
            f.write("-" * 30 + "\n")
            for target, ports in self.results['ports'].items():
                f.write(f"\n{target}:\n")
                for port_info in ports:
                    f.write(f"  • {port_info}\n")
            f.write("\n")
            
            # Technology Stack
            f.write("TECHNOLOGY STACK:\n")
            f.write("-" * 30 + "\n")
            for target, tech_info in self.results['tech_stack'].items():
                f.write(f"\n{target}:\n")
                for key, value in tech_info.items():
                    f.write(f"  • {key}: {value}\n")
            f.write("\n")
            
            # Screenshots
            f.write("SCREENSHOTS:\n")
            f.write("-" * 30 + "\n")
            for screenshot in self.results['screenshots']:
                f.write(f"  • {screenshot}\n")
        
        self.print_status(f"Report saved to: {report_path}", "SUCCESS")
        return report_path
    
    def run_full_recon(self):
        self.print_banner()
        
        # Step 1: Subdomain Enumeration
        subdomains = self.run_subdomain_enumeration()
        
        # Prepare target list (main domain + subdomains)
        targets = [self.target] + subdomains
        
        # Step 2: Port Scanning
        port_results = self.run_port_scanning(targets)
        
        # Step 3: Technology Detection
        tech_results = self.run_tech_detection(targets)
        
        # Step 4: Screenshot Capture
        screenshot_results = self.run_screenshot_capture(targets)
        
        # Step 5: Generate Report
        report_path = self.generate_report()
        
        # Final summary
        print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}RECONNAISSANCE COMPLETE!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Results saved to: {self.target_output_dir}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Report: {report_path}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")

def main():
    parser = argparse.ArgumentParser(
        description="AutoRecon-Py - Automated Reconnaissance Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 main.py --target example.com
  python3 main.py --target example.com --threads 10
  python3 main.py --target example.com --threads 5 --output results
        """
    )
    
    parser.add_argument(
        '--target', '-t',
        required=True,
        help='Target domain to reconnaissance (e.g., example.com)'
    )
    
    parser.add_argument(
        '--threads',
        type=int,
        default=5,
        help='Number of threads for scanning (default: 5)'
    )
    
    parser.add_argument(
        '--output', '-o',
        default='output',
        help='Output directory for results (default: output)'
    )
    
    args = parser.parse_args()
    
    # Validate target
    if not args.target:
        print(f"{Fore.RED}Error: Please provide a target domain{Style.RESET_ALL}")
        sys.exit(1)
    
    # Remove protocol if present
    target = args.target.replace('http://', '').replace('https://', '').strip('/')
    
    try:
        # Initialize and run AutoRecon
        recon = AutoRecon(target, args.threads, args.output)
        recon.run_full_recon()
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Reconnaissance interrupted by user{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)

if __name__ == "__main__":
    main()