import tkinter as tk
import json

from threading import Thread
from tkinter import filedialog

from .server.config import HostServer, CustomStore
from .server.ping import isReachable

from .user.auth import run_bulk_authorization
from .user.requests import run_bulk_users_requests

from .utils import center_window


class AppWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("OSFC Test Perfomance")
        self.root.geometry("518x400")
        self.root.resizable(False, False)

        center_window(self.root)
        
        # Header Label
        self.label = tk.Label(root, text=f"Connected to {HostServer.domain}:{HostServer.port}", pady=10)
        self.label.grid(row=0, column=0, columnspan=4)

        # Users Frame
        self.users_frame = tk.Frame(root, padx=10, borderwidth=2, relief="groove")
        self.users_frame.grid(row=1, column=0, columnspan=4, pady=(10, 0), sticky="w")

        # Auth File Path Entry and Button
        self.auth_file_path = tk.StringVar()
        self.auth_file_path_entry = tk.Entry(self.users_frame, width=40, textvariable=self.auth_file_path)
        self.auth_file_path_entry.grid(row=1, column=1, padx=5, pady=(20, 10), sticky="w")
        self.auth_file_button = tk.Button(self.users_frame, text="Choose Users Login File", 
                                          command=self.choose_user_login_file)
        self.auth_file_button.grid(row=1, column=0, pady=(20, 10), sticky="w")
        
        # Authorization Users Button and Warning Label
        self.authorization_users_button = tk.Button(self.users_frame, text="Authorize Users", 
                                                    state=tk.DISABLED, command=self.authorization_users)
        self.authorization_users_button.grid(row=1, column=3, pady=(20, 10), sticky="w")
        self.warning_auth_label = tk.Label(self.users_frame, text="", fg="red")
        self.warning_auth_label.grid(row=2, column=0, columnspan=3, sticky="w")

        # Requests Per User File Entry and Button
        self.requests_per_user_file_path = tk.StringVar()
        self.requests_per_user_file_path_entry = tk.Entry(self.users_frame, width=40, 
                                                          textvariable=self.requests_per_user_file_path)
        self.requests_per_user_file_path_entry.grid(row=3, padx=5, column=1, pady=(10, 20), sticky="w")
        self.requests_per_user_file_button = tk.Button(self.users_frame, text="Choose Users Requests File", 
                                                       command=self.choose_requests_user_file)
        self.requests_per_user_file_button.grid(row=3, column=0, pady=(10, 20), sticky="w")
        
        # Send Requests Button and Warning Label
        self.send_requests_button = tk.Button(self.users_frame, text="Send Requests", state=tk.DISABLED, 
                                              command=self.send_requests)
        self.send_requests_button.grid(row=3, column=3, pady=(10, 20), sticky="w")
        self.warning_requests_label = tk.Label(self.users_frame, text="", fg="red")
        self.warning_requests_label.grid(row=4, column=0, columnspan=3, sticky="w")

        # Toolbar Frame
        self.toolbar_frame = tk.Frame(root, padx=0, pady=10)
        self.toolbar_frame.grid(row=2, column=0, columnspan=4, sticky="w")

        # Auth Status Circle
        self.auth_status_circle = tk.Canvas(self.toolbar_frame, width=30, height=30, highlightthickness=5)
        self.auth_status_circle.grid(row=0, column=0, pady=5, sticky="w")
        self.auth_status_circle_label = tk.Label(self.toolbar_frame, text="")
        self.auth_status_circle_label.grid(row=0, column=1, padx=5, pady=10, sticky="w")

        # Requests Status Circle
        self.requests_status_circle = tk.Canvas(self.toolbar_frame, width=30, height=30, highlightthickness=5)
        self.requests_status_circle.grid(row=1, column=0, pady=5, sticky="w")
        self.requests_status_circle_label = tk.Label(self.toolbar_frame, text="")
        self.requests_status_circle_label.grid(row=1, column=1, padx=5, pady=10, sticky="w")

        # Draw Circles
        self.draw_circle(obj_circle=self.auth_status_circle,
                         obj_label=self.auth_status_circle_label, text="Auth Status")
        self.draw_circle(obj_circle=self.requests_status_circle,
                         obj_label=self.requests_status_circle_label, text="Requests Status")

        # Footer Frame
        self.footer_frame = tk.Frame(root, padx=0, pady=10)
        self.footer_frame.grid(row=3, column=0, columnspan=4, sticky="n")

        # Additional Window Buttons
        self.reset_window_button = tk.Button(self.footer_frame, text="Reset Window", 
                                             command=self.reset_window)
        self.reset_window_button.grid(row=0, column=0, pady=(10, 10), padx=5)
        self.change_host_button = tk.Button(self.footer_frame, text="Change Host", 
                                            command=self.change_host)
        self.change_host_button.grid(row=0, column=1, pady=(10, 10), padx=5)

    def change_host(self):
        self.root.destroy()
        CustomStore.users_credentials = {}
        CustomStore.users_works_time = {}

        host_ping_window_root = tk.Tk()
        host_ping_window = HostPingWindow(host_ping_window_root)
        host_ping_window_root.mainloop()

    def reset_window(self):
        self.auth_file_path.set("")
        self.requests_per_user_file_path.set("")
        self.warning_auth_label.config(text="")
        self.warning_requests_label.config(text="")
        self.auth_status_circle_label.config(text="")
        self.requests_status_circle_label.config(text="")
        self.requests_status_circle_label.config(text="")
        self.draw_circle(obj_circle=self.auth_status_circle,
                         obj_label=self.auth_status_circle_label, text="Auth Status")
        self.draw_circle(obj_circle=self.requests_status_circle,
                         obj_label=self.requests_status_circle_label, text="Requests Status")
        self.change_allows_to_button(False, self.authorization_users_button)
        self.change_allows_to_button(False, self.send_requests_button)
        CustomStore.users_credentials = {}
        CustomStore.users_works_time = {}

    def draw_circle(self, obj_circle, obj_label, color="white", outline="black", text=""):
        obj_circle.delete("all")
        x, y, r = 20, 20, 8
        obj_circle.create_oval(x - r, y - r, x + r, y + r, fill=color, outline=outline)
        obj_label.config(text=text)

    def handle_auth_results(self, users_data):
        users_credentials = {}
        for status, data in users_data:
            if status != 200:
                self.warning_auth_label.config(text=json.dumps(data))
                self.draw_circle(color="red", text="Auth Failed",
                                 obj_circle=self.auth_status_circle,
                                 obj_label=self.auth_status_circle_label)
                self.change_allows_to_button(False, self.authorization_users_button)
                self.change_allows_to_button(False, self.send_requests_button)
                CustomStore.users_credentials = {}
                return
            users_credentials[data["permissions"]["email"]] = data
        self.warning_auth_label.config(text="")
        self.draw_circle(color="green", text="Auth Success",
                         obj_circle=self.auth_status_circle,
                         obj_label=self.auth_status_circle_label)
        CustomStore.users_credentials = users_credentials

    def handle_requests_results(self, users_data):
        for status, data in users_data:
            if status != 200:
                self.warning_requests_label.config(text=json.dumps(data))
                self.draw_circle(color="red", text="Requests Failed",
                                 obj_circle=self.requests_status_circle,
                                 obj_label=self.requests_status_circle_label)
                self.change_allows_to_button(False, self.authorization_users_button)
                self.change_allows_to_button(False, self.send_requests_button)
                CustomStore.users_works_time = {}
                return
        self.warning_requests_label.config(text="")
        self.draw_circle(color="green", text="Requests Success",
                         obj_circle=self.requests_status_circle,
                         obj_label=self.requests_status_circle_label)

    def authorization_users(self):
        thread = Thread(target=run_bulk_authorization, args=(self.auth_file_path.get(), self.handle_auth_results,))
        thread.start()
        self.root.after(100, self.check_background_auth_status, thread)

    def send_requests(self):
        thread = Thread(target=run_bulk_users_requests, args=(self.requests_per_user_file_path.get(), self.handle_requests_results,))
        thread.start()
        self.root.after(100, self.check_background_requests_status, thread)

    def check_background_auth_status(self, thread):
        if thread.is_alive():
            self.root.after(100, self.check_background_auth_status, thread)
        else:
            self.change_allows_to_button(False, self.authorization_users_button)
            self.change_allows_to_button(True, self.send_requests_button)

    def check_background_requests_status(self, thread):
        if thread.is_alive():
            self.root.after(100, self.check_background_requests_status, thread)
        else:
            self.change_allows_to_button(False, self.authorization_users_button)
            self.change_allows_to_button(True, self.send_requests_button)

    def choose_user_login_file(self):
        file_path = filedialog.askopenfilename()
        if file_path.strip() != "":
            self.auth_file_path.set(file_path)
            self.change_allows_to_button(True, self.authorization_users_button)
            self.change_allows_to_button(False, self.send_requests_button)

    def choose_requests_user_file(self):
        file_path = filedialog.askopenfilename()
        if file_path.strip() != "":
            self.requests_per_user_file_path.set(file_path)
            self.change_allows_to_button(True, self.send_requests_button)
            self.change_allows_to_button(False, self.authorization_users_button)

    def change_allows_to_button(self, is_allowed, button):
        if is_allowed:
            button['state'] = tk.NORMAL
        else:
            button['state'] = tk.DISABLED


class HostPingWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Host Ping")
        self.root.geometry("420x100")
        self.root.resizable(False, False)

        center_window(self.root)

        self.domain_value = tk.StringVar()
        self.domain_entry = tk.Entry(root, textvariable=self.domain_value, width=40)
        self.domain_entry.grid(row=0, column=0, padx=10, pady=10)

        self.port_value = tk.StringVar()
        self.port_entry = tk.Entry(root, textvariable=self.port_value, width=10)
        self.port_entry.grid(row=0, column=1, padx=10, pady=10)

        self.warning_label = tk.Label(root, text="", fg="red")
        self.warning_label.grid(row=1, column=0, padx=0, pady=5)

        self.submit_button = tk.Button(root, text="Submit", state=tk.DISABLED, command=self.submit_action)
        self.submit_button.grid(row=0, column=3, padx=10, pady=10)

        self.domain_value.trace_add("write", self.check_input)
        self.port_value.trace_add("write", self.check_input)

    def check_input(self, *args):
        if self.domain_value.get() and self.port_value.get():
            self.submit_button['state'] = tk.NORMAL
            self.warning_label.config(text="")
        else:
            self.submit_button['state'] = tk.DISABLED
            self.warning_label.config(text="Warning: Domain or Port fields cannot be empty")

    def submit_action(self):
        ip_or_name = self.domain_value.get()
        port = int(self.port_value.get())

        if isReachable(ip_or_name, port):
            HostServer.domain = ip_or_name
            HostServer.port = port
            CustomStore.users_credentials = {}
            CustomStore.users_works_time = {}

            self.root.destroy()
            app_window_root = tk.Tk()
            app_window = AppWindow(app_window_root)
            app_window_root.mainloop()

        else:
            self.warning_label.config(text="Invalid host")
