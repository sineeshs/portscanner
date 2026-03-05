import socket
import concurrent.futures
import sys
import subprocess
import platform
import ipaddress

# UI Constants
RED = "\033[91m"
GREEN = "\033[92m"
BLUE = "\033[94m"
RESET = "\033[0m"

def get_os_hint(ip):
    """Detect OS based on ICMP TTL values."""
    param = "-n" if platform.system().lower() == "windows" else "-c"
    command = ["ping", param, "1", ip]
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, timeout=2).decode()
        if "ttl=" in output.lower():
            ttl_value = int(output.lower().split("ttl=")[1].split()[0])
            if ttl_value <= 64: return f"Linux/Unix (TTL: {ttl_value})"
            if ttl_value <= 128: return f"Windows (TTL: {ttl_value})"
            if ttl_value <= 255: return f"Solaris/Cisco (TTL: {ttl_value})"
    except:
        pass
    return "Unknown OS (ICMP blocked or unreachable)"

def get_active_banner(sock, port):
    """Probes the port to extract service version information."""
    try:
        sock.settimeout(1.5)
        # Attempt 1: Passive grab
        banner = sock.recv(1024).decode(errors='ignore').strip()
        
        if not banner:
            # Attempt 2: Active probe
            if port in [80, 8080, 443]:
                sock.send(b"HEAD / HTTP/1.1\r\nHost: localhost\r\n\r\n")
            else:
                sock.send(b"\r\n")
            banner = sock.recv(1024).decode(errors='ignore').strip()

        if banner:
            for line in banner.split('\r\n'):
                if "Server:" in line:
                    return line.strip()
            return banner.replace('\n', ' ').replace('\r', '')[:60]
    except:
        pass
    return "No banner available"

def scan_port(target_ip, port):
    """Attempts to connect to a specific port."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    try:
        result = sock.connect_ex((target_ip, port))
        if result == 0:
            try:
                service = socket.getservbyport(port, 'tcp')
            except:
                service = 'Unknown'
            
            banner = get_active_banner(sock, port)
            return port, service, banner, True
        return port, "", "", False
    except:
        return port, "", "", False
    finally:
        sock.close()

def port_scan(target_host, start_port, end_port):
    """Main scanning logic."""
    try:
        # Validate IP or Resolve Hostname
        try:
            ipaddress.ip_address(target_host)
            target_ip = target_host
        except ValueError:
            target_ip = socket.gethostbyname(target_host)
    except socket.gaierror:
        print(f"{RED}Error: Hostname could not be resolved.{RESET}")
        return

    print(f"\n{BLUE}Target Information:{RESET}")
    print(f"IP Address: {target_ip}")
    print(f"OS Hint:    {get_os_hint(target_ip)}")
    print("-" * 40)

    results = []
    # Using ThreadPoolExecutor for speed
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        futures = {executor.submit(scan_port, target_ip, port): port for port in range(start_port, end_port + 1)}
        total = end_port - start_port + 1
        
        for i, future in enumerate(concurrent.futures.as_completed(futures), 1):
            res = future.result()
            if res[3]: 
                results.append(res)
            sys.stdout.write(f"\rProgress: {i}/{total} ports scanned")
            sys.stdout.flush()

    results.sort(key=lambda x: x[0])
    print(f"\n\n{BLUE}{'Port':<8} {'Service':<15} {'Version/Banner'}{RESET}")
    print("-" * 60)
    for port, service, banner, _ in results:
        print(f"{RED}{port:<8}{RESET} {service:<15} {GREEN}{banner}{RESET}")

if __name__ == '__main__':
    try:
        target = input("Enter target IP or Hostname: ")
        start_p = int(input("Enter start port (e.g. 1): "))
        end_p = int(input("Enter end port (e.g. 1024): "))
        
        if start_p > end_p:
            print(f"{RED}Error: Start port cannot be greater than end port.{RESET}")
        else:
            port_scan(target, start_p, end_p)
    except KeyboardInterrupt:
        print("\nExiting...")
    except ValueError:
        print("Please enter valid numbers for ports.")
