import os
import socket
import threading
import tkinter as tk
from tkinter import filedialog, scrolledtext


class CloudStorageServer:
    def __init__(self):
        # Main window 
        self.window = tk.Tk()
        self.window.title("Cloud File Storage Server")
        self.window.geometry("600x500")

        # Port input
        tk.Label(self.window, text="Server Port:").pack()
        self.port_entry = tk.Entry(self.window)
        self.port_entry.pack()

        # Storage directory selection
        tk.Button(self.window, text="Select Storage Directory", command=self.select_storage_directory).pack()
        self.storage_path_label = tk.Label(self.window, text="No directory selected")
        self.storage_path_label.pack()

        # Start server button
        tk.Button(self.window, text="Start Server", command=self.start_server).pack()

        # Server log
        tk.Label(self.window, text="Server Log:").pack()
        self.log_box = scrolledtext.ScrolledText(self.window, height=15, width=70)
        self.log_box.pack()

        #Stop server button 
        tk.Button(self.window, text="Stop Server", command=self.stop_server).pack()

        # Server state variables
        self.server_socket = None
        self.storage_directory = None
        self.connected_clients = {}
        self.file_owners = {}

    def select_storage_directory(self):
        self.storage_directory = filedialog.askdirectory()
        if self.storage_directory:
            self.storage_path_label.config(text=f"Selected: {self.storage_directory}")
            self.log(f"Storage directory set to: {self.storage_directory}")

    def log(self, message):
        self.log_box.insert(tk.END, message + "\n")
        self.log_box.see(tk.END)

    def start_server(self):
        try:
            port = int(self.port_entry.get())
            if not self.storage_directory:
                tk.messagebox.showerror("Error", "Please select a storage directory first!")
                return

            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind(('0.0.0.0', port))
            self.server_socket.listen(5)

            self.log(f"Server started on port {port}")
            threading.Thread(target=self.accept_clients, daemon=True).start()
        except Exception as e:
            self.log(f"Failed to start server: {e}")

    def accept_clients(self):
        while True:
            try:
                client_socket, address = self.server_socket.accept()
                threading.Thread(target=self.handle_client, args=(client_socket,), daemon=True).start()
            except Exception as e:
                self.log(f"Error accepting client: {e}")
                break

    def handle_client(self, client_socket):
        try:
            # Client connection
            username = client_socket.recv(1024).decode('utf-8')
            
            if username in self.connected_clients:
                client_socket.send("ERROR: Username already in use".encode('utf-8'))
                client_socket.close()
                return

            self.connected_clients[username] = client_socket
            self.log(f"Client {username} connected")
            client_socket.send("Connected successfully".encode('utf-8'))

            while True:
                # Receive client's request
                request = client_socket.recv(1024).decode('utf-8')
                
                if not request:
                    break

                # What type of request
                if request.startswith("UPLOAD"):
                    self.handle_upload(username, request, client_socket)
                elif request.startswith("LIST"):
                    self.send_file_list(client_socket)
                elif request.startswith("DOWNLOAD"):
                    self.handle_download(username, request, client_socket)
                elif request.startswith("DELETE"):
                    self.handle_delete(username, request)

        except Exception as e:
            self.log(f"Error handling from {username}: {e}")
        finally:
            if username in self.connected_clients:
                del self.connected_clients[username]
            client_socket.close()
            self.log(f"Client {username} disconnected")

    def handle_upload(self, username, request, client_socket):
        req, filename, file_content = request.split(":", 2)

        # Upload file content to the server's local filesystem
        full_path = os.path.join(self.storage_directory, f"{username}_{filename}") # for creating cross-platform 
          
        try:
            #opens a file at the specified location in write mode by using "w"
            with open(full_path, 'w') as f:
                f.write(file_content)
            self.file_owners[full_path] = username
            
            self.log(f"File {filename} uploaded by {username}")
            client_socket.send("Upload successful".encode('utf-8'))
        except Exception as e:
            self.log(f"Upload error: {e}")
            client_socket.send(f"Upload failed: {e}".encode('utf-8'))

    def send_file_list(self, client_socket):
        file_list = [f"{os.path.basename(f)[len(username)+1:]}: {username}" 
                     for f, username in self.file_owners.items()]
        client_socket.send("\n".join(file_list).encode('utf-8'))

    def handle_download(self, requester, request, client_socket):
        req, owner, filename = request.split(":")
        target_file = os.path.join(self.storage_directory, f"{owner}_{filename}")
        
        if target_file in self.file_owners:
            try:
                with open(target_file, 'r') as f:
                    content = f.read()
                
                client_socket.send(f"DOWNLOAD:{filename}:{content}".encode('utf-8'))
                
                if owner in self.connected_clients:
                    uploader_socket = self.connected_clients[owner]
                    uploader_socket.send(f"File {filename} downloaded by {requester}".encode('utf-8'))
            except Exception as e:
                client_socket.send(f"Download failed: {e}".encode('utf-8'))
        else:
            client_socket.send("File not found".encode('utf-8'))

    def handle_delete(self, username, request):
        req, filename = request.split(":")
        target_file = os.path.join(self.storage_directory, f"{username}_{filename}")
        
        if target_file in self.file_owners and self.file_owners[target_file] == username:
            try:
                os.remove(target_file)
                del self.file_owners[target_file]
                self.log(f"File {filename} deleted by {username}")
            except Exception as e:
                self.log(f"Delete error: {e}")
    

    def run(self):
        self.window.mainloop()
    
    def stop_server(self):
        
        if self.server_socket:
            self.server_socket.close()
            self.server_socket = None
            self.log("Server stopped")
                 
        for username, client_socket in list(self.connected_clients.items()):
            try:
                client_socket.send("Server is shutting down.".encode('utf-8'))
                client_socket.close()
            except Exception as e:
                self.log(f"Error disconnecting client {username}: {e}")
        self.connected_clients.clear()
        self.log("All clients disconnected")

        

if __name__ == "__main__":
    server = CloudStorageServer()
    server.run()
