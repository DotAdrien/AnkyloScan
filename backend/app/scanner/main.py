import subprocess
import socket
import os
import tempfile
from .database_handler import save_scan_result
from app.api.email_sender import send_scan_report

def get_local_network():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return ".".join(local_ip.split('.')[:-1]) + ".0/24"
    except Exception:
        return "192.168.2.0/24"

def execute_nmap_process(scan_type, args, xml_path=None):
    try:
        print(f"Scan {scan_type} started on {args[-1]}", flush=True)
        
        process = subprocess.Popen(["nmap"] + args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        
        output_lines = []
        for line in process.stdout:
            output_lines.append(line)
            if "Stats:" in line or "About" in line:
                print(f"[Scan {scan_type}] Progress: {line.strip()}", flush=True)
                
        process.wait()
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, process.args)
        
        xml_output = None
        if xml_path and os.path.exists(xml_path):
            with open(xml_path, 'r', encoding='utf-8') as f:
                xml_output = f.read()

        raw_output = "".join(output_lines)
        save_scan_result(scan_type, raw_output, xml_output)

        send_scan_report(scan_type, raw_output)
            
        print(f"Scan {scan_type} completed", flush=True)
    except Exception as e:
        print(f"Error scan {scan_type}: {e}", flush=True)
    finally:
        if xml_path and os.path.exists(xml_path):
            try:
                os.remove(xml_path)
            except OSError:
                pass

def run_scan(scan_type):
    target_network = get_local_network()
    
    xml_path = None
    if scan_type == 3:
        fd, xml_path = tempfile.mkstemp(suffix=".xml")
        os.close(fd)
        args = [
                    "-p-",
                    "-T4",
                    "-O",
                    "-sV",
                    "--version-intensity", "9",
                    "--script", "vulners,vuln",
                    "-oX", xml_path,
                    target_network
                ]
    elif scan_type == 2:
        args = ["-p-", "-T4", "-O", target_network]
    else:
        args = ["-O",  "-T4", target_network]
        
    execute_nmap_process(scan_type, args, xml_path)
    
    return True