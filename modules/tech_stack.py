#!/usr/bin/env python3

import requests
import re
import subprocess
import json
from colorama import Fore, Style


class TechStackDetector:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.timeout = 10
        
    def detect_tech_stack(self, domain, subdomains=None):
        """
        Detect technology stack for domain and its subdomains
        """
        print(f"\n{Fore.CYAN}[*] Starting Technology Stack Detection for {domain}{Style.RESET_ALL}")
        
        results = {}
        targets = [domain]
        
        if subdomains:
            targets.extend(subdomains)
        
        for target in targets:
            print(f"{Fore.YELLOW}[+] Analyzing: {target}{Style.RESET_ALL}")
            tech_info = self._analyze_target(target)
            if tech_info:
                results[target] = tech_info
                self._print_tech_results(target, tech_info)
        
        return results
    
    def _analyze_target(self, target):
        """
        Analyze a single target for technology stack
        """
        tech_info = {
            'web_server': [],
            'frameworks': [],
            'cms': [],
            'programming_languages': [],
            'databases': [],
            'cdn': [],
            'analytics': [],
            'security': [],
            'other': []
        }
        
        # Try both HTTP and HTTPS
        for protocol in ['https', 'http']:
            url = f"{protocol}://{target}"
            try:
                response = self.session.get(url, timeout=self.timeout, verify=False)
                if response.status_code == 200:
                    tech_info = self._analyze_headers(response.headers, tech_info)
                    tech_info = self._analyze_content(response.text, tech_info)
                    tech_info = self._analyze_cookies(response.cookies, tech_info)
                    break
            except requests.exceptions.RequestException:
                continue
        
        # Try whatweb if available
        whatweb_results = self._run_whatweb(target)
        if whatweb_results:
            tech_info = self._merge_whatweb_results(tech_info, whatweb_results)
        
        return tech_info
    
    def _analyze_headers(self, headers, tech_info):
        """
        Analyze HTTP headers for technology indicators
        """
        header_signatures = {
            'web_server': {
                'Server': [
                    (r'nginx', 'Nginx'),
                    (r'apache', 'Apache'),
                    (r'IIS', 'Microsoft IIS'),
                    (r'cloudflare', 'Cloudflare'),
                    (r'gunicorn', 'Gunicorn'),
                    (r'uwsgi', 'uWSGI')
                ]
            },
            'frameworks': {
                'X-Powered-By': [
                    (r'PHP', 'PHP'),
                    (r'ASP.NET', 'ASP.NET'),
                    (r'Express', 'Express.js'),
                    (r'Django', 'Django'),
                    (r'Rails', 'Ruby on Rails')
                ],
                'X-Framework': [
                    (r'.*', 'Custom Framework')
                ]
            },
            'cms': {
                'X-Generator': [
                    (r'WordPress', 'WordPress'),
                    (r'Drupal', 'Drupal'),
                    (r'Joomla', 'Joomla')
                ]
            },
            'cdn': {
                'Server': [
                    (r'cloudflare', 'Cloudflare'),
                    (r'AmazonS3', 'Amazon S3')
                ],
                'X-CDN': [
                    (r'.*', 'CDN Detected')
                ]
            },
            'security': {
                'X-XSS-Protection': [
                    (r'.*', 'XSS Protection')
                ],
                'X-Content-Type-Options': [
                    (r'.*', 'Content Type Options')
                ],
                'Strict-Transport-Security': [
                    (r'.*', 'HSTS')
                ]
            }
        }
        
        for category, header_patterns in header_signatures.items():
            for header_name, patterns in header_patterns.items():
                if header_name in headers:
                    header_value = headers[header_name]
                    for pattern, tech_name in patterns:
                        if re.search(pattern, header_value, re.IGNORECASE):
                            if tech_name not in tech_info[category]:
                                tech_info[category].append(tech_name)
        
        return tech_info
    
    def _analyze_content(self, content, tech_info):
        """
        Analyze HTML content for technology indicators
        """
        content_signatures = {
            'frameworks': [
                (r'<meta name="generator" content="WordPress.*?"', 'WordPress'),
                (r'<meta name="generator" content="Drupal.*?"', 'Drupal'),
                (r'wp-content/', 'WordPress'),
                (r'wp-includes/', 'WordPress'),
                (r'/sites/default/files/', 'Drupal'),
                (r'Joomla', 'Joomla'),
                (r'django', 'Django'),
                (r'flask', 'Flask'),
                (r'laravel', 'Laravel'),
                (r'symfony', 'Symfony')
            ],
            'programming_languages': [
                (r'\.php', 'PHP'),
                (r'\.asp', 'ASP'),
                (r'\.aspx', 'ASP.NET'),
                (r'\.jsp', 'JSP'),
                (r'\.py', 'Python'),
                (r'\.rb', 'Ruby')
            ],
            'analytics': [
                (r'google-analytics', 'Google Analytics'),
                (r'gtag', 'Google Tag Manager'),
                (r'mixpanel', 'Mixpanel'),
                (r'hotjar', 'Hotjar')
            ],
            'other': [
                (r'jquery', 'jQuery'),
                (r'bootstrap', 'Bootstrap'),
                (r'react', 'React'),
                (r'angular', 'Angular'),
                (r'vue', 'Vue.js')
            ]
        }
        
        for category, patterns in content_signatures.items():
            for pattern, tech_name in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    if tech_name not in tech_info[category]:
                        tech_info[category].append(tech_name)
        
        return tech_info
    
    def _analyze_cookies(self, cookies, tech_info):
        """
        Analyze cookies for technology indicators
        """
        cookie_signatures = {
            'frameworks': [
                ('PHPSESSID', 'PHP'),
                ('ASP.NET_SessionId', 'ASP.NET'),
                ('JSESSIONID', 'Java'),
                ('django_session', 'Django'),
                ('flask_session', 'Flask')
            ],
            'cms': [
                ('wordpress_', 'WordPress'),
                ('wp-', 'WordPress'),
                ('SESS', 'Drupal')
            ]
        }
        
        cookie_names = [cookie.name for cookie in cookies]
        
        for category, patterns in cookie_signatures.items():
            for pattern, tech_name in patterns:
                for cookie_name in cookie_names:
                    if pattern.lower() in cookie_name.lower():
                        if tech_name not in tech_info[category]:
                            tech_info[category].append(tech_name)
        
        return tech_info
    
    def _run_whatweb(self, target):
        """
        Run whatweb command if available
        """
        try:
            cmd = ['whatweb', '--color=never', '--no-errors', f'http://{target}']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return result.stdout
            else:
                # Try HTTPS if HTTP fails
                cmd = ['whatweb', '--color=never', '--no-errors', f'https://{target}']
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    return result.stdout
        except (FileNotFoundError, subprocess.TimeoutExpired):
            # This is expected if whatweb is not installed or times out
            pass
        except Exception as e:
            print(f"{Fore.RED}[!] An unexpected error occurred with whatweb: {e}{Style.RESET_ALL}")
        
        return None
    
    def _merge_whatweb_results(self, tech_info, whatweb_output):
        """
        Parse whatweb output and merge with existing results
        """
        whatweb_signatures = {
            'web_server': ['Apache', 'Nginx', 'IIS', 'Lighttpd'],
            'frameworks': ['PHP', 'ASP.NET', 'Django', 'Rails', 'Express'],
            'cms': ['WordPress', 'Drupal', 'Joomla', 'Magento'],
            'programming_languages': ['PHP', 'Python', 'Ruby', 'Java', 'ASP'],
            'other': ['jQuery', 'Bootstrap', 'AngularJS', 'React']
        }
        
        for category, signatures in whatweb_signatures.items():
            for sig in signatures:
                if sig in whatweb_output:
                    if sig not in tech_info[category]:
                        tech_info[category].append(sig)
        
        return tech_info
    
    def _print_tech_results(self, target, tech_info):
        """
        Print technology stack results for a target
        """
        print(f"\n{Fore.GREEN}[+] Technology Stack for {target}:{Style.RESET_ALL}")
        
        for category, technologies in tech_info.items():
            if technologies:
                category_name = category.replace('_', ' ').title()
                print(f"  {Fore.BLUE}{category_name}:{Style.RESET_ALL} {', '.join(technologies)}")
    
    def save_results(self, results, output_file):
        """
        Save technology stack results to file
        """
        try:
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"{Fore.GREEN}[+] Technology stack results saved to {output_file}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}[!] Error saving results: {e}{Style.RESET_ALL}")

def main():
    """
    Main function for standalone testing
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Technology Stack Detection Tool")
    parser.add_argument("-t", "--target", required=True, help="Target domain")
    parser.add_argument("-o", "--output", default="tech_stack_results.json", help="Output file")
    
    args = parser.parse_args()
    
    detector = TechStackDetector()
    results = detector.detect_tech_stack(args.target)
    detector.save_results(results, args.output)

if __name__ == "__main__":
    main()