# AutoRecon-Py 🔍

A **beginner-friendly Python-based automated reconnaissance tool** for penetration testing and security assessments. AutoRecon-Py performs comprehensive reconnaissance including subdomain enumeration, port scanning, technology stack detection, and website screenshots.

## 🚀 Features

- **Subdomain Enumeration**: Discovers subdomains using multiple methods
- **Port Scanning**: Fast and efficient port scanning with service detection
- **Technology Stack Detection**: Identifies web technologies, frameworks, and CMS
- **Website Screenshots**: Captures screenshots of discovered websites
- **Multi-threading**: Fast execution with configurable thread count
- **Comprehensive Reporting**: Generates detailed reports in multiple formats
- **Modular Design**: Easy to extend and customize

## 📦 Installation

### Prerequisites

1. **Python 3.7+** installed on your system
2. **Google Chrome** browser installed
3. **ChromeDriver** installed and in PATH
4. **Nmap** installed on your system

### Step 1: Clone the Repository

```bash
git clone https://github.com/AvinashCoder31/AutoRecon-Py.git
cd AutoRecon-Py
```

### Step 2: Install Python Dependencies

```bash
pip3 install -r requirements.txt
```

### Step 3: Install System Dependencies

#### On Ubuntu/Debian:
```bash
sudo apt update
sudo apt install nmap whatweb chromium-browser chromium-chromedriver
```

#### On CentOS/RHEL:
```bash
sudo yum install nmap
```

#### On macOS:
```bash
brew install nmap
```

### Step 4: Install ChromeDriver

#### Manual Installation:
1. Download ChromeDriver from https://chromedriver.chromium.org/
2. Extract and place in `/usr/local/bin/` or add to PATH

## 🛠 Usage

### Basic Usage

```bash
python3 main.py --target example.com
```

### Advanced Usage

```bash
# Custom threads and timeout
python3 main.py --target example.com --threads 20 --timeout 15

# Custom output directory
python3 main.py --target example.com --output /tmp/recon

# Quick scan mode
python3 main.py --target example.com --quick

# Skip specific modules
python3 main.py --target example.com --no-screenshots --no-tech
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `-t, --target` | Target domain (required) | - |
| `-o, --output` | Main output directory | `output` |
| `--threads` | Number of threads | `10` |
| `--timeout` | Connection timeout (seconds) | `10` |
| `--no-subdomains` | Skip subdomain enumeration | `False` |
| `--no-ports` | Skip port scanning | `False` |
| `--no-tech` | Skip technology detection | `False` |
| `--no-screenshots` | Skip screenshot capture | `False` |
| `--quick` | Quick scan mode | `False` |

## 📁 Output Structure

All results are saved in a timestamped directory for each target to keep scans organized.

```
output/
└── <target>_<timestamp>/
    ├── summary_report_<timestamp>.txt
    ├── full_results_<timestamp>.json
    ├── subdomains.txt
    ├── ports_<target>.txt
    ├── tech_stack_<timestamp>.json
    └── screenshots/
        ├── <subdomain>_http.png
        └── <subdomain>_https.png
```

## 🔧 Module Details

### 1. Subdomain Enumeration (`subdomain_enum.py`)
- Uses multiple DNS resolution methods
- Supports wordlist-based enumeration
- Validates discovered subdomains
- Filters out duplicate and invalid results

### 2. Port Scanner (`port_scanner.py`)
- Multi-threaded TCP port scanning
- Service detection and banner grabbing
- Configurable port ranges and timeouts
- Nmap integration for enhanced scanning

### 3. Technology Stack Detection (`tech_stack.py`)
- HTTP header analysis
- HTML content fingerprinting
- Cookie-based detection
- Integration with whatweb tool
- Identifies frameworks, CMS, servers, and libraries

### 4. Website Screenshots (`screenshotter.py`)
- Selenium-based screenshot capture
- Handles both HTTP and HTTPS
- Multi-threaded processing
- Captures page metadata and basic info

## 📊 Sample Output

```
[+] Output directory: output/example.com_20231028_120000


 █████╗ ██╗   ██╗████████╗ ██████╗ ██████╗ ███████╗ ██████╗ ██████╗ ███╗   ██╗
██╔══██╗██║   ██║╚══██╔══╝██╔═══██╗██╔══██╗██╔════╝██╔════╝██╔═══██╗████╗  ██║
███████║██║   ██║   ██║   ██║   ██║██████╔╝█████╗  ██║     ██║   ██║██╔██╗ ██║
██╔══██║██║   ██║   ██║   ██║   ██║██╔══██╗██╔══╝  ██║     ██║   ██║██║╚██╗██║
██║  ██║╚██████╔╝   ██║   ╚██████╔╝██║  ██║███████╗╚██████╗╚██████╔╝██║ ╚████║
╚═╝  ╚═╝ ╚═════╝    ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝

                      AutoRecon-Py v1.1 - Automated Reconnaissance Tool
╔══════════════════════════════════════════════════════════════════════════════╗
║  Target: example.com                                                         ║
║  Threads: 10                                                                 ║
║  Timeout: 10s                                                                ║
║  Output: output/example.com_20231028_120000                                  ║
╚══════════════════════════════════════════════════════════════════════════════╝

============================================================
[1/4] SUBDOMAIN ENUMERATION
============================================================
[+] Subdomain enumeration completed
[+] Found 25 subdomains
[+] Results saved to: output/example.com_20231028_120000/subdomains.txt

============================================================
[2/4] PORT SCANNING
============================================================
[+] Port scanning completed for 11 hosts

============================================================
[3/4] TECHNOLOGY STACK DETECTION
============================================================
[+] Technology stack detection completed
[+] Analyzed 6 targets
[+] Results saved to: output/example.com_20231028_120000/tech_stack_20231028_120000.json

============================================================
[4/4] SCREENSHOT CAPTURE
============================================================
[+] Screenshot capture completed
[+] Successful: 5, Failed: 1
[+] Screenshots saved to: output/example.com_20231028_120000/screenshots

============================================================
GENERATING SUMMARY REPORT
============================================================
[+] Summary report generated: output/example.com_20231028_120000/summary_report_20231028_120000.txt
[+] Full results saved: output/example.com_20231028_120000/full_results_20231028_120000.json
```

## 📋 Generated Reports

AutoRecon-Py generates a structured set of reports inside a dedicated directory for each scan (`output/<target>_<timestamp>/`):

1. **Summary Report** (`summary_report_<timestamp>.txt`): A human-readable summary of all findings.
2. **Full JSON Report** (`full_results_<timestamp>.json`): A machine-readable JSON file containing all collected data.
3. **Subdomain List** (`subdomains.txt`): A simple list of all discovered subdomains.
4. **Port Scan Results** (`ports_<hostname>.txt`): Detailed port scan and banner grabbing results for each host.
5. **Technology Stack** (`tech_stack_<timestamp>.json`): Technology information in JSON format.
6. **Screenshots**: PNG files of websites, stored in the `screenshots/` subdirectory.

## 🚨 Legal Disclaimer

This tool is intended for **educational purposes** and **authorized penetration testing** only. Users are responsible for complying with all applicable laws and regulations. The authors are not responsible for any misuse of this tool.

**Always ensure you have proper authorization before testing any systems that do not belong to you.**

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests, report bugs, or suggest new features.

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🛡 Security Considerations

- Always run on isolated/controlled environments
- Be mindful of rate limiting and respectful scanning
- Some modules require elevated privileges
- Network monitoring may detect scanning activities

## 🔧 Troubleshooting

### Common Issues

1. **ChromeDriver not found**
   - Ensure ChromeDriver is installed and in PATH
   - Check ChromeDriver version compatibility

2. **Permission denied errors**
   - Run with appropriate permissions
   - Check file/directory permissions

3. **Module import errors**
   - Ensure all dependencies are installed
   - Check Python path and module locations

4. **Slow scanning**
   - Reduce thread count
   - Increase timeout values
   - Use `--quick` mode for faster results

### Debug Mode

For debugging issues, you can modify the modules to include more verbose output or use Python's debugging tools.

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the documentation

## 🚀 Future Enhancements

- Web interface for easier usage
- Database integration for result storage
- Additional reconnaissance modules
- Advanced reporting features
- Docker containerization
- API integration

---

**Happy Reconnaissance!** 🔍🛡️
