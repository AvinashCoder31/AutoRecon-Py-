#!/usr/bin/env python3
"""
AutoRecon-Py: Automated Reconnaissance Tool
A beginner-friendly Python-based automated reconnaissance tool for penetration testing.
"""

import argparse
import os
import sys
import time
import json
from datetime import datetime
from colorama import Fore, Style, init

# Initialize colorama for cross-platform colored output
init(autoreset=True)

# Import custom modules
try:
    from modules.subdomain_enum import SubdomainEnumerator
    from modules.port_scanner import PortScanner
    from modules.tech_stack import TechStackDetector
    from modules.screenshotter import WebScreenshotter
except ImportError as e:
    print(f"{Fore.RED}[!] Error importing modules: {e}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}[*] Make sure all required modules are in the modules/ directory{Style.RESET_ALL}")
    sys.exit(1)

class AutoRecon:
    def __init__(self, target, output_dir="output", threads=10, timeout=10):
        self.target = target
        self.output_dir = output_dir
        self.threads = threads
        self.timeout = timeout
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create output directories
        self.setup_directories()
        
        # Initialize modules
        self.subdomain_enum = SubdomainEnumerator()
        self.port_scanner = PortScanner(threads=threads, timeout=timeout)
        self.tech_detector = TechStackDetector()
        self.screenshotter = WebScreenshotter(
            output_dir=os.path.join(self.output_dir, "screenshots"),
            timeout=timeout,
            threads=min(3, threads)  # Limit screenshot threads
        )
        
        # Results storage
        self.results = {
            'target': target,
            'timestamp': self.timestamp,
            'subdomains': [],
            'ports': {},
            'tech_stack': {},
            'screenshots': {'successful': 0, 'failed': 0}
        }
    
    def setup_directories(self):
        """
        Setup output directories
        """
        # Main output directory
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        # Screenshots directory
        screenshots_dir = os.path.join(self.output_dir, "screenshots")
        if not os.path.exists(screenshots_dir):
            os.makedirs(screenshots_dir)
        
        print(f"{Fore.GREEN}[+] Output directory: {self.output_dir}{Style.RESET_ALL}")
    
    def print_banner(self):
        """
        Print tool banner
        """
        banner = f"""
{Fore.CYAN}
╔══════════════════════════════════════════════════════════════╗
║                      AutoRecon-Py v1.0                      ║
║              Automated Reconnaissance Tool                   ║
║                                                              ║
║  Target: {self.target:<49} ║
║  Threads: {self.threads:<48} ║
║  Timeout: {self.timeout}s{' ' * 47} ║
╚══════════════════════════════════════════════════════════════╝
{Style.RESET_ALL}
        """
        print(banner)
    
    def run_subdomain_enumeration(self):
        """
        Run subdomain enumeration
        """
        print(f"\n{Fore.MAGENTA}{'='*60}")
        print(f"[1/4] SUBDOMAIN ENUMERATION")
        print(f"{'='*60}{Style.RESET_ALL}")
        
        try:
            subdomains = self.subdomain_enum.enumerate_subdomains(self.target)
            self.results['subdomains'] = subdomains
            
            # Save subdomain results
            subdomain_file = os.path.join(self.output_dir, f"{self.target}_subdomains_{self.timestamp}.txt")
            with open(subdomain_file, 'w') as f:
                f.write(f"Subdomains for {self.target}\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total found: {len(subdomains)}\n")
                f.write("-" * 50 + "\n")
                for subdomain in subdomains:
                    f.write(f"{subdomain}\n")
            
            print(f"{Fore.GREEN}[+] Subdomain enumeration completed")
            print(f"[+] Found {len(subdomains)} subdomains")
            print(f"[+] Results saved to: {subdomain_file}{Style.RESET_ALL}")
            
        except Exception as e:
            print(f"{Fore.RED}[!] Error in port scanning: {e}{Style.RESET_ALL}")
            self.results['ports'] = {}
    
    def run_tech_stack_detection(self):
        """
        Run technology stack detection
        """
        print(f"\n{Fore.MAGENTA}{'='*60}")
        print(f"[3/4] TECHNOLOGY STACK DETECTION")
        print(f"{'='*60}{Style.RESET_ALL}")
        
        try:
            # Detect tech stack for main domain and subdomains
            subdomains_to_check = self.results['subdomains'][:5] if self.results['subdomains'] else None
            
            tech_results = self.tech_detector.detect_tech_stack(self.target, subdomains_to_check)
            self.results['tech_stack'] = tech_results
            
            # Save tech stack results
            tech_file = os.path.join(self.output_dir, f"{self.target}_tech_stack_{self.timestamp}.json")
            self.tech_detector.save_results(tech_results, tech_file)
            
            print(f"{Fore.GREEN}[+] Technology stack detection completed")
            print(f"[+] Analyzed {len(tech_results)} targets")
            print(f"[+] Results saved to: {tech_file}{Style.RESET_ALL}")
            
        except Exception as e:
            print(f"{Fore.RED}[!] Error in tech stack detection: {e}{Style.RESET_ALL}")
            self.results['tech_stack'] = {}
    
    def run_screenshot_capture(self):
        """
        Run screenshot capture
        """
        print(f"\n{Fore.MAGENTA}{'='*60}")
        print(f"[4/4] SCREENSHOT CAPTURE")
        print(f"{'='*60}{Style.RESET_ALL}")
        
        try:
            # Take screenshots of main domain and top subdomains
            subdomains_to_screenshot = self.results['subdomains'][:5] if self.results['subdomains'] else None
            
            successful, failed = self.screenshotter.capture_screenshots(
                domain=self.target,
                subdomains=subdomains_to_screenshot,
                use_threading=True
            )
            
            self.results['screenshots'] = {
                'successful': successful,
                'failed': failed
            }
            
            print(f"{Fore.GREEN}[+] Screenshot capture completed")
            print(f"[+] Successful: {successful}, Failed: {failed}")
            print(f"[+] Screenshots saved to: {os.path.join(self.output_dir, 'screenshots')}{Style.RESET_ALL}")
            
        except Exception as e:
            print(f"{Fore.RED}[!] Error in screenshot capture: {e}{Style.RESET_ALL}")
            self.results['screenshots'] = {'successful': 0, 'failed': 0}
    
    def generate_summary_report(self):
        """
        Generate a comprehensive summary report
        """
        print(f"\n{Fore.MAGENTA}{'='*60}")
        print(f"GENERATING SUMMARY REPORT")
        print(f"{'='*60}{Style.RESET_ALL}")
        
        try:
            report_file = os.path.join(self.output_dir, f"{self.target}_summary_{self.timestamp}.txt")
            
            with open(report_file, 'w') as f:
                # Header
                f.write("=" * 70 + "\n")
                f.write(f"AutoRecon-Py Report for {self.target}\n")
                f.write("=" * 70 + "\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Target: {self.target}\n")
                f.write(f"Threads: {self.threads}\n")
                f.write(f"Timeout: {self.timeout}s\n\n")
                
                # Subdomain Summary
                f.write("SUBDOMAIN ENUMERATION RESULTS\n")
                f.write("-" * 40 + "\n")
                f.write(f"Total subdomains found: {len(self.results['subdomains'])}\n")
                if self.results['subdomains']:
                    f.write("Top 10 subdomains:\n")
                    for i, subdomain in enumerate(self.results['subdomains'][:10], 1):
                        f.write(f"  {i}. {subdomain}\n")
                f.write("\n")
                
                # Port Scan Summary
                f.write("PORT SCANNING RESULTS\n")
                f.write("-" * 40 + "\n")
                total_open_ports = 0
                for host, ports in self.results['ports'].items():
                    if ports:
                        f.write(f"{host}:\n")
                        for port_info in ports:
                            f.write(f"  Port {port_info['port']}/{port_info['protocol']}: {port_info['state']}")
                            if port_info.get('service'):
                                f.write(f" ({port_info['service']})")
                            f.write("\n")
                            total_open_ports += 1
                        f.write("\n")
                f.write(f"Total open ports found: {total_open_ports}\n\n")
                
                # Technology Stack Summary
                f.write("TECHNOLOGY STACK RESULTS\n")
                f.write("-" * 40 + "\n")
                for host, tech_info in self.results['tech_stack'].items():
                    f.write(f"{host}:\n")
                    for category, technologies in tech_info.items():
                        if technologies:
                            f.write(f"  {category.replace('_', ' ').title()}: {', '.join(technologies)}\n")
                    f.write("\n")
                
                # Screenshot Summary
                f.write("SCREENSHOT CAPTURE RESULTS\n")
                f.write("-" * 40 + "\n")
                f.write(f"Successful screenshots: {self.results['screenshots']['successful']}\n")
                f.write(f"Failed screenshots: {self.results['screenshots']['failed']}\n")
                f.write(f"Screenshots location: {os.path.join(self.output_dir, 'screenshots')}\n\n")
                
                # Files Generated
                f.write("FILES GENERATED\n")
                f.write("-" * 40 + "\n")
                f.write(f"1. Subdomains: {self.target}_subdomains_{self.timestamp}.txt\n")
                f.write(f"2. Port scan: {self.target}_ports_{self.timestamp}.json\n")
                f.write(f"3. Tech stack: {self.target}_tech_stack_{self.timestamp}.json\n")
                f.write(f"4. Screenshots: screenshots/ directory\n")
                f.write(f"5. Summary: {self.target}_summary_{self.timestamp}.txt\n")
                f.write(f"6. Full results: {self.target}_full_results_{self.timestamp}.json\n")
            
            # Save full results as JSON
            full_results_file = os.path.join(self.output_dir, f"{self.target}_full_results_{self.timestamp}.json")
            with open(full_results_file, 'w') as f:
                json.dump(self.results, f, indent=2)
            
            print(f"{Fore.GREEN}[+] Summary report generated: {report_file}")
            print(f"[+] Full results saved: {full_results_file}{Style.RESET_ALL}")
            
        except Exception as e:
            print(f"{Fore.RED}[!] Error generating summary report: {e}{Style.RESET_ALL}")
    
    def print_final_summary(self):
        """
        Print final summary to console
        """
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"RECONNAISSANCE COMPLETED")
        print(f"{'='*60}{Style.RESET_ALL}")
        
        print(f"{Fore.GREEN}[+] Target: {self.target}")
        print(f"[+] Subdomains found: {len(self.results['subdomains'])}")
        
        total_open_ports = sum(len(ports) for ports in self.results['ports'].values())
        print(f"[+] Open ports found: {total_open_ports}")
        
        tech_targets = len(self.results['tech_stack'])
        print(f"[+] Technology stacks analyzed: {tech_targets}")
        
        print(f"[+] Screenshots captured: {self.results['screenshots']['successful']}")
        print(f"[+] Screenshots failed: {self.results['screenshots']['failed']}")
        
        print(f"[+] Output directory: {self.output_dir}")
        print(f"[+] Timestamp: {self.timestamp}{Style.RESET_ALL}")
    
    def run_full_recon(self):
        """
        Run complete reconnaissance workflow
        """
        start_time = time.time()
        
        self.print_banner()
        
        # Run all reconnaissance modules
        self.run_subdomain_enumeration()
        self.run_port_scanning()
        self.run_tech_stack_detection()
        self.run_screenshot_capture()
        
        # Generate reports
        self.generate_summary_report()
        
        # Print final summary
        self.print_final_summary()
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n{Fore.CYAN}[*] Total execution time: {duration:.2f} seconds{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[+] Reconnaissance completed successfully!{Style.RESET_ALL}")

def main():
    """
    Main function
    """
    parser = argparse.ArgumentParser(
        description="AutoRecon-Py - Automated Reconnaissance Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 main.py --target example.com
  python3 main.py --target example.com --threads 20 --timeout 15
  python3 main.py --target example.com --output /tmp/recon --no-screenshots
        """
    )
    
    parser.add_argument(
        "-t", "--target",
        required=True,
        help="Target domain to reconnaissance"
    )
    
    parser.add_argument(
        "-o", "--output",
        default="output",
        help="Output directory (default: output)"
    )
    
    parser.add_argument(
        "--threads",
        type=int,
        default=10,
        help="Number of threads for scanning (default: 10)"
    )
    
    parser.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="Connection timeout in seconds (default: 10)"
    )
    
    parser.add_argument(
        "--no-subdomains",
        action="store_true",
        help="Skip subdomain enumeration"
    )
    
    parser.add_argument(
        "--no-ports",
        action="store_true",
        help="Skip port scanning"
    )
    
    parser.add_argument(
        "--no-tech",
        action="store_true",
        help="Skip technology stack detection"
    )
    
    parser.add_argument(
        "--no-screenshots",
        action="store_true",
        help="Skip screenshot capture"
    )
    
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Quick scan mode (reduced coverage, faster execution)"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="AutoRecon-Py v1.0"
    )
    
    args = parser.parse_args()
    
    # Validate target
    if not args.target:
        print(f"{Fore.RED}[!] Please provide a target domain{Style.RESET_ALL}")
        sys.exit(1)
    
    # Clean target (remove protocol if present)
    target = args.target.replace('http://', '').replace('https://', '').strip('/')
    
    # Adjust settings for quick mode
    if args.quick:
        args.threads = 5
        args.timeout = 5
    
    try:
        # Initialize AutoRecon
        recon = AutoRecon(
            target=target,
            output_dir=args.output,
            threads=args.threads,
            timeout=args.timeout
        )
        
        # Print banner
        recon.print_banner()
        
        # Run individual modules based on arguments
        start_time = time.time()
        
        if not args.no_subdomains:
            recon.run_subdomain_enumeration()
        else:
            print(f"{Fore.YELLOW}[*] Skipping subdomain enumeration{Style.RESET_ALL}")
        
        if not args.no_ports:
            recon.run_port_scanning()
        else:
            print(f"{Fore.YELLOW}[*] Skipping port scanning{Style.RESET_ALL}")
        
        if not args.no_tech:
            recon.run_tech_stack_detection()
        else:
            print(f"{Fore.YELLOW}[*] Skipping technology stack detection{Style.RESET_ALL}")
        
        if not args.no_screenshots:
            recon.run_screenshot_capture()
        else:
            print(f"{Fore.YELLOW}[*] Skipping screenshot capture{Style.RESET_ALL}")
        
        # Generate reports
        recon.generate_summary_report()
        
        # Print final summary
        recon.print_final_summary()
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n{Fore.CYAN}[*] Total execution time: {duration:.2f} seconds{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[+] Reconnaissance completed successfully!{Style.RESET_ALL}")
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[*] Reconnaissance interrupted by user{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Fore.RED}[!] Critical error: {e}{Style.RESET_ALL}")
        sys.exit(1)

if __name__ == "__main__":
    main() in subdomain enumeration: {e}{Style.RESET_ALL}")
            self.results['subdomains'] = []
    
    def run_port_scanning(self):
        """
        Run port scanning
        """
        print(f"\n{Fore.MAGENTA}{'='*60}")
        print(f"[2/4] PORT SCANNING")
        print(f"{'='*60}{Style.RESET_ALL}")
        
        try:
            # Scan main domain
            targets = [self.target]
            
            # Add subdomains if any were found
            if self.results['subdomains']:
                # Limit to top 10 subdomains for faster scanning
                targets.extend(self.results['subdomains'][:10])
            
            port_results = self.port_scanner.scan_multiple_hosts(targets)
            self.results['ports'] = port_results
            
            # Save port scan results
            port_file = os.path.join(self.output_dir, f"{self.target}_ports_{self.timestamp}.json")
            with open(port_file, 'w') as f:
                json.dump(port_results, f, indent=2)
            
            print(f"{Fore.GREEN}[+] Port scanning completed")
            print(f"[+] Scanned {len(targets)} hosts")
            print(f"[+] Results saved to: {port_file}{Style.RESET_ALL}")
            
        except Exception as e:
            print(f"{Fore.RED}[!] Error