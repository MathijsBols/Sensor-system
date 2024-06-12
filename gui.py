import tkinter as tk
from tkinter import ttk
import requests
import threading
from datetime import datetime, timedelta

class GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Kamer Sensor Meldingsysteem")

        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Create a Canvas widget
        canvas = tk.Canvas(self.main_frame)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add a Scrollbar to the Canvas
        scrollbar = ttk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.config(yscrollcommand=scrollbar.set)

        # Create a frame inside the Canvas to contain the cards
        self.cards_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=self.cards_frame, anchor=tk.NW)

        self.cards = {}  # Dictionary to store card widgets

        self.update_interval = 1000  # Update interval in milliseconds (e.g., 1000 = 1 second)
        self.api_down_message_displayed = False
        self.fetch_from_api_thread()

        self.create_clear_button()

        # Configure canvas scrolling
        self.cards_frame.bind("<Configure>", lambda event, canvas=canvas: self.on_frame_configure(canvas))

    def fetch_from_api_thread(self):
        thread = threading.Thread(target=self.fetch_from_api)
        thread.daemon = True  # Daemonize the thread so it terminates when the main program exits
        thread.start()

    def fetch_from_api(self):
        try:
            response = requests.get("http://localhost:5000/get-action")
            data = response.json()
            self.root.after(0, self.update_gui, data)  # Update GUI in the main thread
            if self.api_down_message_displayed:
                self.remove_api_down_message()
                self.api_down_message_displayed = False
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            if not self.api_down_message_displayed:
                self.root.after(0, self.display_api_down_message)  # Display API down message in the main thread
                self.api_down_message_displayed = True

        # Schedule the next update
        self.root.after(self.update_interval, self.fetch_from_api_thread)

    def update_gui(self, data):
        # Clear existing cards
        for widget in self.cards_frame.winfo_children():
            widget.destroy()

        if isinstance(data, list):
            for sensor_data in reversed(data):  # Reversed order
                sensor_id = sensor_data.get('id', '')
                timestamp_str = sensor_data.get('timestamp', '')
                self.create_card(sensor_id, timestamp_str)
        elif isinstance(data, dict):
            sensor_id = data.get('id', '')
            timestamp_str = data.get('timestamp', '')
            self.create_card(sensor_id, timestamp_str)

    def create_card(self, sensor_id, timestamp_str):
        card_frame = ttk.Frame(self.cards_frame, relief=tk.RAISED, borderwidth=2)
        card_frame.pack(fill=tk.X, padx=5, pady=5)

        label_id = ttk.Label(card_frame, text=f"Sensor: {sensor_id}", font=("Helvetica", 12, "bold"))
        label_id.pack(anchor=tk.W, padx=10, pady=5)

        label_timestamp = ttk.Label(card_frame, text=f"Laatste Tijd: {timestamp_str}")
        label_timestamp.pack(anchor=tk.W, padx=10, pady=5)

        self.cards[sensor_id] = {'frame': card_frame, 'label_timestamp': label_timestamp}

        self.flash_card(sensor_id, timestamp_str)

    def flash_card(self, sensor_id, timestamp_str):
        card_frame = self.cards[sensor_id]['frame']
        current_time = datetime.now()
        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
        if current_time - timestamp <= timedelta(seconds=20):
            card_frame_style = ttk.Style()
            card_frame_style.configure(f"{sensor_id}.TFrame", background="red")
            card_frame.config(style=f"{sensor_id}.TFrame")
            self.root.after(100, lambda: self.reset_card_bg(sensor_id))
            self.root.after(100, lambda: self.flash_card(sensor_id, timestamp_str))
        else:
            card_frame_style = ttk.Style()
            card_frame_style.configure(f"{sensor_id}.TFrame", background="white")

    def reset_card_bg(self, sensor_id):
        card_frame = self.cards[sensor_id]['frame']
        card_frame_style = ttk.Style()
        card_frame_style.configure(f"{sensor_id}.TFrame", background="white")

    def display_api_down_message(self):
        self.api_down_label = ttk.Label(self.cards_frame, text="Geen Connectie tot API, neem contant op met een beheerder.", font=("Helvetica", 10, "bold"))
        self.api_down_label.pack(fill=tk.BOTH, expand=True)

    def remove_api_down_message(self):
        self.api_down_label.pack_forget()

    def create_clear_button(self):
        clear_button = ttk.Button(self.main_frame, text="Clear All", command=self.clear_all)
        clear_button.pack(side=tk.BOTTOM, pady=10)

    def clear_all(self):

        API_ENDPOINT = "http://localhost:5000/clear"
        api_data = {'mode': 'clear'}
        rpost = requests.post(url=API_ENDPOINT, data=api_data)
        print(rpost)
 
































        for widget in self.cards_frame.winfo_children():
            widget.destroy()
        self.cards = {}

    def on_frame_configure(self, canvas):
        canvas.configure(scrollregion=canvas.bbox("all"))

def main():
    root = tk.Tk()
    root.geometry("600x400")  # Set initial window size
    gui = GUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
