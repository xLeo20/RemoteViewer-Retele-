import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import shared.protocol as protocol 
import socket
import threading
import time
import io
import tkinter as tk
from tkinter import simpledialog, messagebox
import mss
from PIL import Image, ImageTk

HOST = '127.0.0.1' 
PORT = 5000

class RemoteViewerClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Remote Viewer")
        self.root.geometry("800x600")

        self.sock = None
        self.my_username = None
        self.users = []
        self.is_connected = False
        
        # Folosim un set pentru a evita duplicatele la spectatori
        self.viewers_of_my_screen = set() 
        
        self.setup_ui()
        self.connect_to_server()

    def setup_ui(self):
        """Construieste interfata grafica."""
        left_frame = tk.Frame(self.root, width=200, bg="lightgray")
        left_frame.pack(side=tk.LEFT, fill=tk.Y)

        tk.Label(left_frame, text="Utilizatori Online:", bg="lightgray").pack(pady=5)
        self.user_listbox = tk.Listbox(left_frame)
        self.user_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.watch_btn = tk.Button(left_frame, text="Vezi Ecran", command=self.request_stream)
        self.watch_btn.pack(pady=5)

        self.image_label = tk.Label(self.root, text="Selecteaza un utilizator pentru a vedea ecranul.")
        self.image_label.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def connect_to_server(self):
        """Gestioneaza logarea si conexiunea TCP."""
        self.my_username = simpledialog.askstring("Autentificare", "Introdu un nume unic:", parent=self.root)
        if not self.my_username:
            self.root.destroy()
            return

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((HOST, PORT))
            
            protocol.send_msg(self.sock, {"type": "connect", "username": self.my_username})
            
            meta, _ = protocol.recv_msg(self.sock)
            if meta["status"] == "accept":
                self.is_connected = True
                self.users = [u for u in meta["users"] if u != self.my_username]
                self.update_user_list()
                self.root.title(f"Remote Viewer - Conectat ca: {self.my_username}")
                
                # Thread-uri separate pentru a nu bloca interfata grafica
                threading.Thread(target=self.network_listener, daemon=True).start()
                threading.Thread(target=self.screen_sender, daemon=True).start()
            else:
                messagebox.showerror("Eroare", meta.get("reason", "Conectare refuzata."))
                self.root.destroy()
        except Exception as e:
            messagebox.showerror("Eroare Conexiune", f"Nu m-am putut conecta la server: {e}")
            self.root.destroy()

    def update_user_list(self):
        """Actualizeaza lista vizuala de utilizatori."""
        self.user_listbox.delete(0, tk.END)
        for u in self.users:
            self.user_listbox.insert(tk.END, u)

    def request_stream(self):
        """Cere serverului acces la ecranul altui utilizator."""
        selection = self.user_listbox.curselection()
        if not selection:
            return
        
        target_user = self.user_listbox.get(selection[0])
        protocol.send_msg(self.sock, {"type": "request_stream", "target": target_user, "from": self.my_username})
        self.image_label.config(text=f"Astept stream de la {target_user}...")

    def network_listener(self):
        """Proceseaza pachetele primite de la server in fundal."""
        try:
            while self.is_connected:
                meta, binary = protocol.recv_msg(self.sock)
                if not meta:
                    break

                msg_type = meta.get("type")

                if msg_type == "user_joined":
                    new_user = meta["username"]
                    if new_user != self.my_username and new_user not in self.users:
                        self.users.append(new_user)
                        self.update_user_list()

                elif msg_type == "user_left":
                    left_user = meta["username"]
                    if left_user in self.users:
                        self.users.remove(left_user)
                        self.update_user_list()

                elif msg_type == "request_stream":
                    viewer = meta["from"]
                    self.viewers_of_my_screen.add(viewer)

                elif msg_type == "frame":
                    self.display_image(binary)

        except Exception as e:
            print(f"Deconectat de la server: {e}")
        finally:
            self.is_connected = False

    def display_image(self, img_bytes):
        """Afiseaza imaginea primita in UI."""
        try:
            image = Image.open(io.BytesIO(img_bytes))
            
            label_width = self.image_label.winfo_width()
            label_height = self.image_label.winfo_height()
            if label_width > 10 and label_height > 10: 
                image.thumbnail((label_width, label_height))
            
            photo = ImageTk.PhotoImage(image)
            
            def update_label():
                self.image_label.config(image=photo, text="")
                self.image_label.image = photo 
            
            self.root.after(0, update_label)
        except Exception as e:
            print(f"Eroare la afisarea imaginii: {e}")

    def screen_sender(self):
        """Trimite capturi de ecran daca exista spectatori."""
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            
            while self.is_connected:
                if not self.viewers_of_my_screen:
                    time.sleep(0.5)
                    continue
                
                try:
                    sct_img = sct.grab(monitor)
                    img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                    
                    # Optimizare rezolutie si calitate pentru retea
                    img.thumbnail((1280, 720))
                    img_byte_arr = io.BytesIO()
                    img.save(img_byte_arr, format='JPEG', quality=60)
                    img_bytes = img_byte_arr.getvalue()

                    for viewer in list(self.viewers_of_my_screen):
                        meta = {"type": "frame", "target": viewer, "from": self.my_username}
                        protocol.send_msg(self.sock, meta, img_bytes)
                        
                except Exception as e:
                    print(f"Eroare la captura de ecran: {e}")
                
                time.sleep(0.2) 

if __name__ == "__main__":
    root = tk.Tk()
    app = RemoteViewerClient(root)
    root.mainloop()