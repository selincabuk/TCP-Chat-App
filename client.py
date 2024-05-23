import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog, Toplevel, Label, Entry, Button, Listbox, Menu, StringVar

class ChatClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat")
        self.root.geometry("500x600")

        self.nickname_set = False  # Flag to track if the nickname is set
        self.groups = {'Friends': [], 'Family': [], 'Others': []}  # Default groups
        self.selected_group = StringVar(value='Friends')

        self.messages_frame = tk.Frame(self.root)
        self.my_msg = tk.StringVar()
        self.my_msg.set("Type here.")
        self.scrollbar = tk.Scrollbar(self.messages_frame)

        self.msg_list = scrolledtext.ScrolledText(self.messages_frame, wrap=tk.WORD, yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.msg_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.msg_list.pack()
        self.messages_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        self.entry_field = tk.Entry(self.root, textvariable=self.my_msg, width=50)
        self.entry_field.bind("<FocusIn>", self.clear_default_text)
        self.entry_field.bind("<Return>", self.send)
        self.entry_field.pack(pady=5, padx=10, fill=tk.X)

        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(pady=5, padx=10, fill=tk.X)

        self.inner_button_frame = tk.Frame(self.button_frame)
        self.inner_button_frame.pack(pady=5, padx=10)

        self.send_button = tk.Button(self.inner_button_frame, text="Send", command=self.send)
        self.send_button.grid(row=0, column=0, padx=5)

        self.quit_button = tk.Button(self.inner_button_frame, text="Quit", command=self.quit)
        self.quit_button.grid(row=0, column=1, padx=5)

        self.online_button = tk.Button(self.inner_button_frame, text="Online Users", command=self.show_online, state=tk.DISABLED)
        self.online_button.grid(row=0, column=2, padx=5)

        self.history_button = tk.Button(self.inner_button_frame, text="Message History", command=self.show_history, state=tk.DISABLED)
        self.history_button.grid(row=0, column=3, padx=5)

        self.search_button = tk.Button(self.inner_button_frame, text="Search Messages", command=self.search_messages, state=tk.DISABLED)
        self.search_button.grid(row=0, column=4, padx=5)

        self.manage_contacts_button = tk.Button(self.inner_button_frame, text="Manage Contacts", command=self.manage_contacts, state=tk.DISABLED)
        self.manage_contacts_button.grid(row=0, column=5, padx=5)

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(("localhost", 25000))

        threading.Thread(target=self.receive).start()

        self.msg_list.bind("<1>", lambda event: "break")

    def send(self, event=None):
        message = self.my_msg.get()
        self.my_msg.set("")
        self.client_socket.send(message.encode("utf8"))
        if message == "/quit":
            self.client_socket.close()
            self.root.quit()

    def receive(self):
        while True:
            try:
                message = self.client_socket.recv(2048).decode("utf8")
                if message.startswith("Welcome to Chat! Please type your nickname:") or \
                   message.startswith("This nickname has already been taken. Please choose a different one:"):
                    self.nickname_set = False
                else:
                    self.nickname_set = True
                    self.online_button.config(state=tk.NORMAL)
                    self.history_button.config(state=tk.NORMAL)
                    self.search_button.config(state=tk.NORMAL)
                    self.manage_contacts_button.config(state=tk.NORMAL)
                self.msg_list.insert(tk.END, message + "\n")
                self.msg_list.yview(tk.END)
            except OSError:
                break

    def quit(self):
        self.my_msg.set("/quit")
        self.send()

    def show_online(self):
        if self.nickname_set:
            self.my_msg.set("/online")
            self.send()

    def show_history(self):
        if self.nickname_set:
            self.my_msg.set("/history")
            self.send()

    def search_messages(self):
        if self.nickname_set:
            self.open_search_dialog()

    def open_search_dialog(self):
        search_window = Toplevel(self.root)
        search_window.title("Search Messages")

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = 300
        window_height = 100
        window_x = (screen_width - window_width) // 2
        window_y = (screen_height - window_height) // 2
        search_window.geometry(f"{window_width}x{window_height}+{window_x}+{window_y}")

        Label(search_window, text="Enter keyword to search:").pack(pady=10)
        keyword_entry = Entry(search_window)
        keyword_entry.pack(pady=5)
        keyword_entry.focus()

        def perform_search():
            keyword = keyword_entry.get()
            if keyword:
                self.my_msg.set(f"/search {keyword}")
                self.send()
            search_window.destroy()

        Button(search_window, text="Search", command=perform_search).pack(pady=5)

    def manage_contacts(self):
        contacts_window = Toplevel(self.root)
        contacts_window.title("Manage Contacts")

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = 400
        window_height = 300
        window_x = (screen_width - window_width) // 2
        window_y = (screen_height - window_height) // 2
        contacts_window.geometry(f"{window_width}x{window_height}+{window_x}+{window_y}")

        self.contact_listbox = Listbox(contacts_window)
        self.contact_listbox.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)

        self.update_contact_listbox()

        menu = Menu(contacts_window, tearoff=0)
        menu.add_command(label="Add Contact", command=self.add_contact)
        menu.add_command(label="Remove Contact", command=self.remove_contact)
        menu.add_command(label="Move Contact", command=self.move_contact)

        def show_menu(event):
            menu.post(event.x_root, event.y_root)

        self.contact_listbox.bind("<Button-3>", show_menu)

    def update_contact_listbox(self):
        self.contact_listbox.delete(0, tk.END)
        for group in self.groups:
            self.contact_listbox.insert(tk.END, f"--- {group} ---")
            for contact in self.groups[group]:
                self.contact_listbox.insert(tk.END, contact)

    def add_contact(self):
        add_window = Toplevel(self.root)
        add_window.title("Add Contact")

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = 200
        window_height = 300
        window_x = (screen_width - window_width) // 2
        window_y = (screen_height - window_height) // 2
        add_window.geometry(f"{window_width}x{window_height}+{window_x}+{window_y}")

        Label(add_window, text="Contact Name:").pack(pady=5)
        contact_name_entry = Entry(add_window)
        contact_name_entry.pack(pady=5)

        Label(add_window, text="Select Group:").pack(pady=5)
        group_listbox = Listbox(add_window)
        group_listbox.pack(pady=5)
        for group in self.groups:
            group_listbox.insert(tk.END, group)

        def add_to_group():
            contact_name = contact_name_entry.get()
            selected_group = group_listbox.get(group_listbox.curselection())
            if contact_name and selected_group:
                self.groups[selected_group].append(contact_name)
                self.update_contact_listbox()
                add_window.destroy()

        Button(add_window, text="Add", command=add_to_group).pack(pady=5)

    def remove_contact(self):
        selected_contact_index = self.contact_listbox.curselection()
        if selected_contact_index:
            selected_contact = self.contact_listbox.get(selected_contact_index)
            if selected_contact.startswith("---") and selected_contact.endswith("---"):
                return
            for group in self.groups:
                if selected_contact in self.groups[group]:
                    self.groups[group].remove(selected_contact)
                    break
            self.update_contact_listbox()

    def move_contact(self):
        selected_contact_index = self.contact_listbox.curselection()
        if selected_contact_index:
            selected_contact = self.contact_listbox.get(selected_contact_index)
            if selected_contact.startswith("---") and selected_contact.endswith("---"):
                return
            move_window = Toplevel(self.root)
            move_window.title("Move Contact")

            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            window_width = 200
            window_height = 300
            window_x = (screen_width - window_width) // 2
            window_y = (screen_height - window_height) // 2
            move_window.geometry(f"{window_width}x{window_height}+{window_x}+{window_y}")

            Label(move_window, text="Select Group:").pack(pady=5)
            group_listbox = Listbox(move_window)
            group_listbox.pack(pady=5)
            for group in self.groups:
                if not selected_contact.startswith("---") and not selected_contact.endswith("---"):
                    group_listbox.insert(tk.END, group)

        def move_to_group():
            new_group = group_listbox.get(group_listbox.curselection())
            if new_group:
                for group in self.groups:
                    if selected_contact in self.groups[group]:
                        self.groups[group].remove(selected_contact)
                        break
                self.groups[new_group].append(selected_contact)
                self.update_contact_listbox()
                move_window.destroy()

        Button(move_window, text="Move", command=move_to_group).pack(pady=5)

    def clear_default_text(self, event):
        if self.entry_field.get() == self.my_msg.get():
            self.entry_field.delete(0, tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    client = ChatClient(root)

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    root_width = 600
    root_height = 600
    root_x = (screen_width - root_width) // 2
    root_y = (screen_height - root_height) // 2

    root.geometry("{}x{}+{}+{}".format(root_width, root_height, root_x, root_y))

    root.mainloop()


