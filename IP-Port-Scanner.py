import tkinter as tk
import socket
import threading
import tkinter.ttk as ttk
from tkinter import messagebox

# Classe principale dell'applicazione di scansione IP
class IPScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("IP Port Scanner")

        # Aggiungi un label con il titolo del software
        software_label = tk.Label(root, text="IP Port Scanner", font=("Helvetica", 16))
        software_label.grid(row=0, column=0, columnspan=3, padx=10, pady=10)

        # Variabili per il controllo dello stato della scansione
        self.scan_in_progress = False
        self.scan_thread = None

        # Etichette e casella di input per l'intervallo IP
        self.ip_range_label = tk.Label(root, text="IP Range (e.g., 192.168.1.1-192.168.1.254):")
        self.ip_range_label.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

        self.ip_range_entry = tk.Entry(root)
        self.ip_range_entry.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

        # Pulsanti
        self.scan_button = tk.Button(root, text="Scan IPs", command=self.start_ip_scan)
        self.scan_button.grid(row=3, column=0, padx=10, pady=10)

        self.stop_button = tk.Button(root, text="Stop", command=self.stop_scan, state=tk.DISABLED)
        self.stop_button.grid(row=3, column=1, padx=10, pady=10)

        self.port_scan_button = tk.Button(root, text="Port Scan", command=self.start_port_scan, state=tk.DISABLED)
        self.port_scan_button.grid(row=3, column=2, padx=10, pady=10)

        # Albero per visualizzare i risultati
        self.tree = ttk.Treeview(root, columns=("IP", "Hostname"), show="headings", height=15)
        self.tree.heading("IP", text="IP")
        self.tree.heading("Hostname", text="Hostname")
        self.tree.grid(row=4, column=0, columnspan=3, padx=10, pady=10)

        # Lista degli IP selezionati
        self.selected_ips = []

    # Funzione per avviare la scansione IP
    def start_ip_scan(self):
        if self.scan_in_progress:
            messagebox.showinfo("Info", "Scan already in progress")
            return

        self.scan_in_progress = True
        self.scan_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        # Ottieni l'intervallo IP dall'input
        ip_range = self.ip_range_entry.get()
        start_ip, end_ip = ip_range.split('-')
        
        try:
            start_ip_int = int(start_ip.split('.')[-1])
            end_ip_int = int(end_ip.split('.')[-1])

            # Cancella i risultati precedenti nell'albero
            self.tree.delete(*self.tree.get_children())

            # Funzione per eseguire la scansione di un singolo IP
            def scan_ip(ip):
                try:
                    hostname = socket.gethostbyaddr(ip)
                except socket.herror:
                    hostname = ("N/A",)

                # Inserisci i risultati nell'albero
                self.tree.insert("", "end", values=(ip, hostname[0]))

            # Funzione per eseguire la scansione nell'intervallo specificato
            def scan_range():
                for ip_int in range(start_ip_int, end_ip_int + 1):
                    if not self.scan_in_progress:
                        break
                    current_ip = f"192.168.1.{ip_int}"  # Modifica con la tua rete
                    scan_ip(current_ip)

                # Alla fine della scansione, ripristina i pulsanti
                self.scan_in_progress = False
                self.scan_button.config(state=tk.NORMAL)
                self.stop_button.config(state=tk.DISABLED)
                self.port_scan_button.config(state=tk.NORMAL)

            # Avvia la scansione in un thread separato
            self.scan_thread = threading.Thread(target=scan_range)
            self.scan_thread.start()

        except ValueError:
            messagebox.showerror("Error", "Invalid IP range")

    # Funzione per interrompere la scansione IP
    def stop_scan(self):
        self.scan_in_progress = False
        if self.scan_thread and self.scan_thread.is_alive():
            self.scan_thread.join()

        # Ripristina i pulsanti
        self.scan_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.port_scan_button.config(state=tk.DISABLED)

    # Funzione per avviare la scansione delle porte
    def start_port_scan(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showinfo("Info", "Select IPs to scan ports")
            return

        # Ottieni l'IP selezionato dall'albero
        selected_ip = self.tree.item(selected_item[0], "values")[0]

        # Crea una finestra separata per la scansione delle porte
        port_scan_window = tk.Toplevel(self.root)
        PortScanner(port_scan_window, selected_ip)

# Classe per la scansione delle porte
class PortScanner:
    def __init__(self, root, ip):
        self.root = root
        self.root.title(f"Port Scanner - IP: {ip}")

        self.ip = ip

        # Etichette e casella di input per l'intervallo delle porte
        self.port_range_label = tk.Label(root, text="Port Range (e.g., 1-1024):")
        self.port_range_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        self.port_range_entry = tk.Entry(root)
        self.port_range_entry.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

        # Pulsanti
        self.scan_button = tk.Button(root, text="Scan Ports", command=self.start_port_scan)
        self.scan_button.grid(row=2, column=0, padx=10, pady=10)

        self.stop_button = tk.Button(root, text="Stop", command=self.stop_port_scan, state=tk.DISABLED)
        self.stop_button.grid(row=2, column=1, padx=10, pady=10)

        # Albero per visualizzare i risultati della scansione delle porte
        self.tree = ttk.Treeview(root, columns=("Port", "Status"), show="headings", height=15)
        self.tree.heading("Port", text="Port")
        self.tree.heading("Status", text="Status")
        self.tree.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        # Variabili per il controllo dello stato della scansione delle porte
        self.scan_in_progress = False
        self.scan_thread = None

    # Funzione per avviare la scansione delle porte
    def start_port_scan(self):
        if self.scan_in_progress:
            messagebox.showinfo("Info", "Scan already in progress")
            return

        self.scan_in_progress = True
        self.scan_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        # Ottieni l'intervallo delle porte dall'input
        port_range = self.port_range_entry.get()
        start_port, end_port = map(int, port_range.split('-'))
        
        # Cancella i risultati precedenti nell'albero
        self.tree.delete(*self.tree.get_children())

        # Funzione per eseguire la scansione di una singola porta
        def scan_port(port):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((self.ip, port))
            sock.close()
            if result == 0:
                status = "Open"
            else:
                status = "Closed"
            self.tree.insert("", "end", values=(port, status))
            self.tree.see(self.tree.get_children()[-1])

        # Funzione per eseguire la scansione delle porte nell'intervallo specificato
        def scan_ports_range():
            for port in range(start_port, end_port + 1):
                if not self.scan_in_progress:
                    break
                scan_port(port)

            # Alla fine della scansione, ripristina i pulsanti
            self.scan_in_progress = False
            self.scan_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

        # Avvia la scansione delle porte in un thread separato
        self.scan_thread = threading.Thread(target=scan_ports_range)
        self.scan_thread.start()

    # Funzione per interrompere la scansione delle porte
    def stop_port_scan(self):
        self.scan_in_progress = False
        if self.scan_thread and self.scan_thread.is_alive():
            self.scan_thread.join()

        # Ripristina i pulsanti
        self.scan_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

if __name__ == "__main__":
    app = tk.Tk()
    IPScannerApp(app)
    app.mainloop()
