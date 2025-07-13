#!/usr/bin/env python3

import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from colorama import Fore, Style
from concurrent.futures import ThreadPoolExecutor, as_completed

class WebScreenshotter:
    def __init__(self, output_dir="screenshots", timeout=10, threads=3):
        self.output_dir = output_dir
        self.timeout = timeout
        self.threads = threads
        self.setup_output_directory()
        
    def setup_output_directory(self):
        """
        Create output directory if it doesn't exist
        """
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"{Fore.GREEN}[+] Created output directory: {self.output_dir}{Style.RESET_ALL}")
    
    def setup_driver(self):
        """
        Setup Chrome WebDriver with appropriate options
        """
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run headless Chrome
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--ignore-ssl-errors")
        chrome_options.add_argument("--ignore-certificate-errors-spki-list")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-images")  # Disable images for faster loading
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        # Disable logging
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        try:
            driver = webdriver.Chrome(options=chrome_options)
            driver.set_page_load_timeout(self.timeout)
            return driver
        except Exception as e:
            print(f"{Fore.RED}[!] Error setting up Chrome driver: {e}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}[*] Make sure ChromeDriver is installed and in PATH{Style.RESET_ALL}")
            return None
    
    def is_url_accessible(self, url):
        """
        Check if URL is accessible before taking screenshot
        """
        try:
            response = requests.get(url, timeout=5, verify=False)
            return response.status_code == 200
        except:
            return False
    
    def take_screenshot(self, target, protocols=['https', 'http']):
        """
        Take screenshot of a single target
        """
        driver = self.setup_driver()
        if not driver:
            return None
        
        screenshot_taken = False
        
        for protocol in protocols:
            url = f"{protocol}://{target}"
            
            try:
                print(f"{Fore.YELLOW}[+] Taking screenshot of: {url}{Style.RESET_ALL}")
                
                # Check if URL is accessible first
                if not self.is_url_accessible(url):
                    print(f"{Fore.RED}[!] URL not accessible: {url}{Style.RESET_ALL}")
                    continue
                
                # Navigate to the URL
                driver.get(url)
                
                # Wait for page to load
                WebDriverWait(driver, self.timeout).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # Additional wait for dynamic content
                time.sleep(2)
                
                # Take screenshot
                safe_filename = self._sanitize_filename(target)
                screenshot_path = os.path.join(self.output_dir, f"{safe_filename}_{protocol}.png")
                
                if driver.save_screenshot(screenshot_path):
                    print(f"{Fore.GREEN}[+] Screenshot saved: {screenshot_path}{Style.RESET_ALL}")
                    screenshot_taken = True
                    
                    # Get basic page info
                    page_info = self._get_page_info(driver, url)
                    
                    # Save page info
                    info_file = os.path.join(self.output_dir, f"{safe_filename}_{protocol}_info.txt")
                    self._save_page_info(info_file, page_info)
                    
                    break  # Success, no need to try other protocols
                else:
                    print(f"{Fore.RED}[!] Failed to save screenshot for {url}{Style.RESET_ALL}")
                    
            except TimeoutException:
                print(f"{Fore.RED}[!] Timeout loading {url}{Style.RESET_ALL}")
                continue
            except WebDriverException as e:
                print(f"{Fore.RED}[!] WebDriver error for {url}: {str(e)[:100]}...{Style.RESET_ALL}")
                continue
            except Exception as e:
                print(f"{Fore.RED}[!] Error taking screenshot of {url}: {str(e)[:100]}...{Style.RESET_ALL}")
                continue
        
        driver.quit()
        return screenshot_taken
    
    def _get_page_info(self, driver, url):
        """
        Get basic information about the page
        """
        try:
            page_info = {
                'url': url,
                'title': driver.title,
                'current_url': driver.current_url,
                'page_source_length': len(driver.page_source),
                'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Try to get some basic elements
            try:
                h1_elements = driver.find_elements(By.TAG_NAME, "h1")
                page_info['h1_count'] = len(h1_elements)
                if h1_elements:
                    page_info['first_h1'] = h1_elements[0].text[:100]
            except:
                pass
            
            try:
                links = driver.find_elements(By.TAG_NAME, "a")
                page_info['link_count'] = len(links)
            except:
                pass
            
            try:
                images = driver.find_elements(By.TAG_NAME, "img")
                page_info['image_count'] = len(images)
            except:
                pass
            
            return page_info
            
        except Exception as e:
            return {'url': url, 'error': str(e), 'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")}
    
    def _save_page_info(self, filepath, page_info):
        """
        Save page information to file
        """
        try:
            with open(filepath, 'w') as f:
                f.write("=== Page Information ===\n")
                for key, value in page_info.items():
                    f.write(f"{key}: {value}\n")
        except Exception as e:
            print(f"{Fore.RED}[!] Error saving page info: {e}{Style.RESET_ALL}")
    
    def _sanitize_filename(self, filename):
        """
        Sanitize filename to be safe for filesystem
        """
        # Replace unsafe characters
        unsafe_chars = '<>:"/\\|?*'
        for char in unsafe_chars:
            filename = filename.replace(char, '_')
        
        # Remove dots except for the last one (for extension)
        filename = filename.replace('.', '_')
        
        # Limit length
        if len(filename) > 100:
            filename = filename[:100]
        
        return filename
    
    def take_screenshots_threaded(self, targets, max_workers=None):
        """
        Take screenshots of multiple targets using threading
        """
        if max_workers is None:
            max_workers = min(self.threads, len(targets))
        
        print(f"\n{Fore.CYAN}[*] Starting screenshot capture for {len(targets)} targets{Style.RESET_ALL}")
        print(f"{Fore.CYAN}[*] Using {max_workers} threads{Style.RESET_ALL}")
        
        successful_screenshots = 0
        failed_screenshots = 0
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_target = {executor.submit(self.take_screenshot, target): target for target in targets}
            
            # Process completed tasks
            for future in as_completed(future_to_target):
                target = future_to_target[future]
                try:
                    result = future.result()
                    if result:
                        successful_screenshots += 1
                    else:
                        failed_screenshots += 1
                except Exception as e:
                    print(f"{Fore.RED}[!] Error processing {target}: {e}{Style.RESET_ALL}")
                    failed_screenshots += 1
        
        print(f"\n{Fore.GREEN}[+] Screenshot Summary:{Style.RESET_ALL}")
        print(f"  Successful: {successful_screenshots}")
        print(f"  Failed: {failed_screenshots}")
        print(f"  Total: {len(targets)}")
        
        return successful_screenshots, failed_screenshots
    
    def take_screenshots_sequential(self, targets):
        """
        Take screenshots sequentially (fallback method)
        """
        print(f"\n{Fore.CYAN}[*] Starting sequential screenshot capture for {len(targets)} targets{Style.RESET_ALL}")
        
        successful_screenshots = 0
        failed_screenshots = 0
        
        for i, target in enumerate(targets, 1):
            print(f"\n{Fore.CYAN}[*] Processing {i}/{len(targets)}: {target}{Style.RESET_ALL}")
            
            result = self.take_screenshot(target)
            if result:
                successful_screenshots += 1
            else:
                failed_screenshots += 1
        
        print(f"\n{Fore.GREEN}[+] Screenshot Summary:{Style.RESET_ALL}")
        print(f"  Successful: {successful_screenshots}")
        print(f"  Failed: {failed_screenshots}")
        print(f"  Total: {len(targets)}")
        
        return successful_screenshots, failed_screenshots
    
    def capture_screenshots(self, domain, subdomains=None, use_threading=True):
        """
        Main method to capture screenshots for domain and subdomains
        """
        targets = [domain]
        
        if subdomains:
            targets.extend(subdomains)
        
        # Remove duplicates
        targets = list(set(targets))
        
        if use_threading:
            return self.take_screenshots_threaded(targets)
        else:
            return self.take_screenshots_sequential(targets)

def main():
    """
    Main function for standalone testing
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Web Screenshot Tool")
    parser.add_argument("-t", "--target", required=True, help="Target domain")
    parser.add_argument("-o", "--output", default="screenshots", help="Output directory")
    parser.add_argument("--timeout", type=int, default=10, help="Page load timeout")
    parser.add_argument("--threads", type=int, default=3, help="Number of threads")
    parser.add_argument("--no-threading", action="store_true", help="Disable threading")
    
    args = parser.parse_args()
    
    screenshotter = WebScreenshotter(
        output_dir=args.output,
        timeout=args.timeout,
        threads=args.threads
    )
    
    screenshotter.capture_screenshots(
        domain=args.target,
        use_threading=not args.no_threading
    )

if __name__ == "__main__":
    main()