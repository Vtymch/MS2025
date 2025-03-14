import tkinter as tk
from tkinter import messagebox
import json

# Function to update the server list
class ServerMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Server Monitor")
        self.root.geometry("500x300")  # Window size
        self.root.config(bg="#2E3B4E")  # Background color (dark blue shade)
        
        self.server_list = tk.Listbox(root, bg="#3C4D6A", fg="white", font=("Helvetica", 12), selectmode=tk.SINGLE)
        self.server_list.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # Adding buttons and label
        self.status_label = tk.Label(root, text="Server Status", fg="white", bg="#2E3B4E", font=("Helvetica", 16))
        self.status_label.pack(pady=10)
        
        self.update_button = tk.Button(root, text="Update Status", command=self.update_servers, bg="#4E6A88", fg="white", font=("Helvetica", 12))
        self.update_button.pack(pady=10)

        self.update_servers()

    def update_servers(self):
        self.server_list.delete(0, tk.END)
        
        # Load data from the server (e.g., from a file)
        try:
            with open("servers.json", "r") as f:
                servers = json.load(f)
        except FileNotFoundError:
            servers = []
        
        # Add servers to Listbox
        for server in servers:
            self.server_list.insert(tk.END, f"{server['host']} - {server['method']}")

        # Call the function again after 5 seconds
        self.root.after(5000, self.update_servers)

def start_gui():
    root = tk.Tk()
    app = ServerMonitorApp(root)
    root.mainloop()

if __name__ == "__main__":
    start_gui()
