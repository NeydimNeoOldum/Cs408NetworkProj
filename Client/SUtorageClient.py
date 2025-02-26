import socket
import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

class CloudStorageClient:
    def __init__(self):
        # main window
        self.window = tk.Tk()
        self.window.title("Cloud Storage Client")
        self.window.geometry("600x500")

        # Create the server connection section
        self._create_connection_section()

        
    def _create_connection_section(self):
        # connection frame for server info and connection
        connection_frame = tk.Frame(self.window)
        connection_frame.pack(padx=10, pady=10)

        # server ip input
        tk.Label(connection_frame, text="Server IP:").grid(row=0, column=0)
        self.ip_entry = tk.Entry(connection_frame)
        self.ip_entry.grid(row=0, column=1)
        
        #server port input 
        tk.Label(connection_frame, text="Port:").grid(row=1, column=0)
        self.port_entry = tk.Entry(connection_frame)
        self.port_entry.grid(row=1, column=1)

        # username input
        tk.Label(connection_frame, text="Your Username:").grid(row=2, column=0)
        self.username_entry = tk.Entry(connection_frame)
        self.username_entry.grid(row=2, column=1)

        # connect button
        self.connect_button = tk.Button(connection_frame, text="Connect", command=self.connect_to_server)
        self.connect_button.grid(row=3, column=0, columnspan=2)
        
        # disconnect button
        self.disconnect_button = tk.Button(connection_frame, text="Disconnect", command=self.disconnect_from_server, state=tk.DISABLED)
        self.disconnect_button.grid(row=4, column=0, columnspan=2)

        # file operations frame for upload and listing files
        file_ops_frame = tk.Frame(self.window)
        file_ops_frame.pack(padx=10, pady=10)

        # upload button
        self.upload_button = tk.Button(file_ops_frame, text="Upload File", command=self.upload_file, state=tk.DISABLED)
        self.upload_button.pack(side=tk.LEFT, padx=5)

        # list files button
        self.list_files_button = tk.Button(file_ops_frame, text="List Files", command=self.list_files, state=tk.DISABLED)
        self.list_files_button.pack(side=tk.LEFT, padx=5)

        # download frame
        download_frame = tk.Frame(self.window)
        download_frame.pack(padx=10, pady=10)

        tk.Label(download_frame, text="Owner:").pack(side=tk.LEFT)
        self.owner_entry = tk.Entry(download_frame)
        self.owner_entry.pack(side=tk.LEFT, padx=5)

        tk.Label(download_frame, text="Filename:").pack(side=tk.LEFT)
        self.download_filename_entry = tk.Entry(download_frame)
        self.download_filename_entry.pack(side=tk.LEFT, padx=5)

        self.download_button = tk.Button(download_frame, text="Download", command=self.download_file, state=tk.DISABLED)
        self.download_button.pack(side=tk.LEFT, padx=5)

        # delete file frame
        delete_frame = tk.Frame(self.window)
        delete_frame.pack(padx=10, pady=10)

        tk.Label(delete_frame, text="Delete Filename:").pack(side=tk.LEFT)
        self.delete_filename_entry = tk.Entry(delete_frame)
        self.delete_filename_entry.pack(side=tk.LEFT, padx=5)

        self.delete_button = tk.Button(delete_frame, text="Delete File", command=self.delete_file, state=tk.DISABLED)
        self.delete_button.pack(side=tk.LEFT, padx=5)

        # client log display
        tk.Label(self.window, text="Client Log:").pack()
        self.log_box = scrolledtext.ScrolledText(self.window, height=10, width=70)
        self.log_box.pack()

        # client state variables
        self.client_socket = None
        self.download_directory = None
        self.username = None

    def log(self, message):
        self.log_box.insert(tk.END, message + "\n")
        self.log_box.see(tk.END)

    def connect_to_server(self):
        try:
            # get connection detailes from enrty fields
            server_ip = self.ip_entry.get()
            server_port = int(self.port_entry.get())
            self.username = self.username_entry.get()

            # set up
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((server_ip, server_port))

            # send username to server and wait for server acknowledgment
            self.client_socket.send(self.username.encode('utf-8'))
            response = self.client_socket.recv(1024).decode('utf-8')

            if "ERROR" in response:
                messagebox.showerror("Connection Error", response)
                self.client_socket.close()
                return

            self.log(f"Connected to server {server_ip}:{server_port}")
            
            # enable buttons
            self.upload_button.config(state=tk.NORMAL)
            self.list_files_button.config(state=tk.NORMAL)
            self.download_button.config(state=tk.NORMAL)
            self.delete_button.config(state=tk.NORMAL)
            self.connect_button.config(state=tk.DISABLED)
            self.disconnect_button.config(state=tk.NORMAL)

        except Exception as e:
            messagebox.showerror("Connection Error", str(e))

    def disconnect_from_server(self):
        try:
            if self.client_socket:
                self.client_socket.close()
                self.client_socket = None
                
                # Disable all operation buttons
                self.upload_button.config(state=tk.DISABLED)
                self.list_files_button.config(state=tk.DISABLED)
                self.download_button.config(state=tk.DISABLED)
                self.delete_button.config(state=tk.DISABLED)
                self.disconnect_button.config(state=tk.DISABLED)
                self.connect_button.config(state=tk.NORMAL)
                
                self.log("Disconnected from server")
                
        except Exception as e:
            messagebox.showerror("Disconnect Error", str(e))

    def upload_file(self):
        try:
            filename = filedialog.askopenfilename(title="Select a text file to upload")
            if not filename:
                return

            with open(filename, 'r') as f:
                file_content = f.read()

            short_filename = os.path.basename(filename)
            upload_request = f"UPLOAD:{short_filename}:{file_content}"
            self.client_socket.send(upload_request.encode('utf-8'))
            
            response = self.client_socket.recv(1024).decode('utf-8')
            self.log(f"Upload result: {response}")

        except Exception as e:
            messagebox.showerror("Upload Error", str(e))

    def list_files(self):
        try:
            # requesting file list from server 
            self.client_socket.send("LIST".encode('utf-8'))
            files = self.client_socket.recv(4096).decode('utf-8')

            # display files in a dialog
            messagebox.showinfo("Available Files", files)
            self.log("Retrieved file list")

        except Exception as e:
            messagebox.showerror("List Files Error", str(e))

    def download_file(self):
        try:
            # getting file details
            owner = self.owner_entry.get()
            filename = self.download_filename_entry.get()

            # prompt for download directory
            download_dir = filedialog.askdirectory(title="Select Download Directory")
            if not download_dir:
                return

            download_request = f"DOWNLOAD:{owner}:{filename}"
            self.client_socket.send(download_request.encode('utf-8'))
            
            response = self.client_socket.recv(4096).decode('utf-8')
            
            if response.startswith("DOWNLOAD:"):
                _, recv_filename, content = response.split(":", 2)
                full_path = os.path.join(download_dir, recv_filename)
                
                with open(full_path, 'w') as f:
                    f.write(content)
                
                self.log(f"Downloaded {recv_filename} from {owner}")
                messagebox.showinfo("Download", f"File {recv_filename} downloaded successfully")
            else:
                messagebox.showerror("Download Error", response)

        except Exception as e:
            messagebox.showerror("Download Error", str(e))

    def delete_file(self):
        try:
            #getting the filename to delete
            filename = self.delete_filename_entry.get()
            delete_request = f"DELETE:{filename}"
            # send delete request
            self.client_socket.send(delete_request.encode('utf-8'))
            
            self.log(f"Deleted file: {filename}")
        except Exception as e:
            messagebox.showerror("Delete Error", str(e))

    def run(self):
        # create GUI window
        self.window.mainloop()

if __name__ == "__main__":
    client = CloudStorageClient()
    client.run()
