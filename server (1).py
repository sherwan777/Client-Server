import socket
import threading
import tkinter as tk

class ChatServer: 
# making the window
    def __init__(self):
        self.host = '127.0.0.1' # local host to connect 
        self.port = None # port for server used
        self.max_connections = 10 # max 10 clients can connect
        self.clients = [] # clients are appended to this list
        self.server_socket = None # basic socket connection
        self.root = tk.Tk() # tinker for gui
        self.root.title('Chat Server')

        #Port input
        self.port_entry_frame = tk.Frame(self.root)
        self.port_entry_label = tk.Label(self.port_entry_frame, text='Enter port number:')
        self.port_entry_label.pack(side=tk.LEFT)
        self.port_entry = tk.Entry(self.port_entry_frame, width=10)
        self.port_entry.pack(side=tk.LEFT, padx=5)
        self.listen_button = tk.Button(self.port_entry_frame, text='Listen', command=self.start_server)
        self.listen_button.pack(side=tk.LEFT)
        self.port_entry_frame.pack(pady=5)
        
        # initializing box
        self.message_frame = tk.Frame(self.root) 
        self.scrollbar = tk.Scrollbar(self.message_frame) 
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.message_listbox = tk.Listbox(self.message_frame, height=15, width=50, yscrollcommand=self.scrollbar.set)
        self.message_listbox.pack(side=tk.LEFT, fill=tk.BOTH)
        self.scrollbar.config(command=self.message_listbox.yview)
        self.message_frame.pack()

        #message box frame
        self.entry_frame = tk.Frame(self.root)
        self.message_entry = tk.Entry(self.entry_frame, width=50)
        self.message_entry.pack(side=tk.LEFT, padx=10)
        self.send_button = tk.Button(self.entry_frame, text='Send', command=self.send_message)
        self.send_button.pack(side=tk.LEFT,padx=10)
        self.entry_frame.pack(pady=5)
        
        self.root.protocol('WM_DELETE_WINDOW', self.quit)
        self.root.mainloop()

    #Starting the server  
    def start_server(self):
        self.port = int(self.port_entry.get())
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # basic socket connection
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(self.max_connections)
        self.listen_button.config(state=tk.DISABLED)
        threading.Thread(target=self.accept_clients).start()
        
    # accept the clients to the server    
    def accept_clients(self):
        while True:
            client_socket, client_address = self.server_socket.accept()
            self.clients.append(client_socket)
            threading.Thread(target=self.receive_messages, args=(client_socket,)).start()
            self.message_listbox.insert(tk.END, f'{client_address[0]}:{client_address[1]} connected')

    #Receive the meesage from all the clients connected     
    def receive_messages(self, client_socket):
        while True:
            try:
                message = client_socket.recv(1024).decode()
                if message.strip():
                    self.broadcast(message, client_socket)
                else:
                    raise Exception('Empty message received')
            except:
                self.clients.remove(client_socket)
                self.broadcast(f'{client_socket.getpeername()} disconnected', client_socket)
                client_socket.close()
                break

    #Broadcast msg to all the clients and server itself          
    def broadcast(self, message, sender_socket, is_server_message=False):
        if is_server_message:
            formatted_message = f'Server: {message}'
        else:
            formatted_message = f'{sender_socket.getpeername()[0]}:{sender_socket.getpeername()[1]} {message}'
        for client_socket in self.clients:
            if client_socket != sender_socket:
                try:
                    client_socket.sendall(formatted_message.encode())
                except:
                    self.clients.remove(client_socket)
                    client_socket.close()
                    self.broadcast(f'{client_socket.getpeername()} disconnected', None)
        self.message_listbox.insert(tk.END, formatted_message)



    #Stopping the server and disconneting all the clients    
    def stop_server(self):
        self.server_socket.close()
        for client_socket in self.clients:
            client_socket.close()
        self.clients = []
        self.message_listbox.insert(tk.END, 'Server stopped')

    # Send msg to the clients    
    def send_message(self):
        message = self.message_entry.get()
        self.message_entry.delete(0, tk.END)
        self.broadcast(message, None, is_server_message=True)


    #close the server socket    
    def quit(self):
        try:
            self.socket.close()
        except:
            pass
        self.root.destroy()

if __name__ == '__main__':
    ChatServer()