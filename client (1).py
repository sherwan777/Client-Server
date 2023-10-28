import socket
import tkinter as tk

class ChatClient:
    # making the window
    def __init__(self):
        self.host = '127.0.0.1'
        self.port = None  # Initialize port to None
        
        # Create the main window and widgets
        self.root = tk.Tk()
        self.root.title('Chat Client')
        
        #taking port input
        self.port_frame = tk.Frame(self.root)
        self.port_label = tk.Label(self.port_frame, text="Enter Port Number:")
        self.port_label.pack(side=tk.LEFT)
        self.port_entry = tk.Entry(self.port_frame, width=10)
        self.port_entry.pack(side=tk.LEFT)
        self.connect_button = tk.Button(self.port_frame, text='Connect', command=self.connect_to_server)
        self.connect_button.pack(side=tk.LEFT, padx=5)
        self.port_frame.pack()

        #box for msg display
        self.message_frame = tk.Frame(self.root)
        self.message_listbox = tk.Listbox(self.message_frame, height=15, width=50)
        self.message_listbox.pack(side=tk.LEFT, fill=tk.BOTH)
        self.message_frame.pack()
        
        self.message_entry = tk.Entry(self.root, width=50)
        self.message_entry.pack(pady=5)
        self.send_button = tk.Button(self.root, text='Send', command=self.send_message)
        self.send_button.pack()
        
        self.root.protocol('WM_DELETE_WINDOW', self.quit)
        self.root.after(100, self.connect_to_server)
        self.root.mainloop()

    # connecting the clients to the server    
    def connect_to_server(self):
        # Get port number from user input
        port_str = self.port_entry.get()
        if port_str:
            self.port = int(port_str)
        
        if not self.port:
            self.message_listbox.insert(tk.END, 'Please enter a valid port number')
            return
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((self.host, self.port))
            self.message_listbox.insert(tk.END, 'Connected to server') # adding client to server list
            self.socket.setblocking(0)
            self.root.after(100, self.receive_messages)
        except:
            self.message_listbox.insert(tk.END, 'Unable to connect to server') # if connection not build

    # recieving the message both from server and other clients    
    def receive_messages(self):
        try:
            message = self.socket.recv(1024).decode()
            if message:
                self.message_listbox.insert(tk.END, message)
        except socket.error as e:
            if e.errno != 10035 and e.errno != 11: # Ignore "Resource temporarily unavailable" and "Resource temporarily unavailable" errors
                self.message_listbox.insert(tk.END, 'Error receiving message: {}'.format(e))#this ignores empty box
        except:
            self.message_listbox.insert(tk.END, 'Error receiving message')
        self.root.after(100, self.receive_messages)

    #sending to server so it can broadcast to everyone    
    def send_message(self):
        message = self.message_entry.get()
        self.message_entry.delete(0, tk.END)
        if not message:
            return
        try:
            self.socket.sendall(message.encode())
            # Add the sent message to the message listbox manually
            self.message_listbox.insert(tk.END, "You: {}".format(message))
        except socket.error as e:
            if e.errno != 10035: # Ignore "Resource temporarily unavailable" error
                self.message_listbox.insert(tk.END, 'Error sending message: {}'.format(e))
        except:
            self.message_listbox.insert(tk.END, 'Error sending message')


    #Destroying when the session end        
    def quit(self):
        try:
            self.socket.close()
        except:
            pass
        self.root.destroy()

if __name__ == '__main__':
    ChatClient()