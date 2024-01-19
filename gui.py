import tkinter as tk
from tkinter import messagebox
import json
import subprocess
import json
import os

def save_data_to_file(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f)

def load_data_from_file(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    else:
        return None

# Global variable to keep track of the alerts process
alerts_process = None
env_vars_filename = 'user_data/gui_data/env_vars.json'
def save_env_variables(webhook_url_entry, client_id_entry, client_secret_entry, region_entry, desired_items_entry, 
                       desired_pets_entry, desired_ilvl_entry, desired_ilvl_list_entry):
    try:
        
        env_vars = {
            'MEGA_WEBHOOK_URL': webhook_url_entry.get() if webhook_url_entry.get() != '' else None,
            'WOW_CLIENT_ID': client_id_entry.get() if client_id_entry.get() != '' else None,
            'WOW_CLIENT_SECRET': client_secret_entry.get() if client_secret_entry.get() != '' else None,
            'WOW_REGION': region_entry.get() if region_entry.get() not in ["NA", "EU"] else "NA",
            'DESIRED_ITEMS': json.loads(desired_items_entry.get()) if desired_items_entry.get() != '' else None,
            'DESIRED_PETS': json.loads(desired_pets_entry.get()) if desired_pets_entry.get() != '' else None,
            'DESIRED_ILVL': json.loads(desired_ilvl_entry.get()) if desired_ilvl_entry.get() != '' else None,
            'DESIRED_ILVL_LIST': json.loads(desired_ilvl_list_entry.get()) if desired_ilvl_list_entry.get() != '' else None
        }
        save_data_to_file(env_vars_filename, env_vars)
        required_keys = ['MEGA_WEBHOOK_URL', 'WOW_CLIENT_ID', 'WOW_CLIENT_SECRET', 'WOW_REGION']
        item_keys = ['DESIRED_ITEMS', 'DESIRED_PETS', 'DESIRED_ILVL', 'DESIRED_ILVL_LIST']

        # Check for missing required keys
        for key in required_keys:
            if env_vars[key] is None:
                messagebox.showerror("Error", f"{env_vars[key]} must be provided.")
                return None

        # Check to make sure at least one of the item keys is provided
        if not env_vars['DESIRED_ITEMS'] and not env_vars['DESIRED_PETS'] and not env_vars['DESIRED_ILVL'] and not env_vars['DESIRED_ILVL_LIST']:
            messagebox.showerror("Error", "At least one of DESIRED_ITEMS, DESIRED_PETS, DESIRED_ILVL, DESIRED_ILVL_LIST must be provided.")
            return None

        messagebox.showinfo("Success", "Environment variables saved successfully.")
        return env_vars
    except json.JSONDecodeError:
        messagebox.showerror("Error", "Invalid JSON format in input fields.")
        return None

def start_mega_alerts(env_vars):
    global alerts_process
    if env_vars:
        env_vars = {key: str(value) for key, value in env_vars.items() if value is not None}
         # All checks go here
        necessary_keys = ['MEGA_WEBHOOK_URL', 'WOW_CLIENT_ID', 'WOW_CLIENT_SECRET', 'WOW_REGION']
        if all(key in env_vars and env_vars[key] is not None for key in necessary_keys):
            # Start the mega-alerts.py script as a subprocess
            alerts_process = subprocess.Popen(['/usr/local/bin/python3', 'mega-alerts.py'], env=env_vars)
            messagebox.showinfo("MEGA-ALERTS", "MEGA-ALERTS started.")
        else:
            messagebox.showerror("Error", "Incomplete or missing environment variables.")


def stop_mega_alerts():
    global alerts_process
    if alerts_process:
        alerts_process.terminate()
        alerts_process = None
        messagebox.showinfo("MEGA-ALERTS", "MEGA-ALERTS stopped.")

def create_gui():
    root = tk.Tk()
    root.title("MEGA-ALERTS Configuration")

    env_vars = load_data_from_file(env_vars_filename)
    if not env_vars:
        env_vars = {}

    webhook_url_entry = tk.Entry(root)
    webhook_url_entry.insert(0, env_vars.get('MEGA_WEBHOOK_URL', ''))
    webhook_url_entry.grid(row=0, column=1)
    tk.Label(root, text="MEGA_WEBHOOK_URL").grid(row=0, column=0)

    client_id_entry = tk.Entry(root)
    client_id_entry.insert(0, env_vars.get('WOW_CLIENT_ID', ''))
    client_id_entry.grid(row=1, column=1)
    tk.Label(root, text="WOW_CLIENT_ID").grid(row=1, column=0)

    client_secret_entry = tk.Entry(root)
    client_secret_entry.insert(0, env_vars.get('WOW_CLIENT_SECRET', ''))
    client_secret_entry.grid(row=2, column=1)
    tk.Label(root, text="WOW_CLIENT_SECRET").grid(row=2, column=0)

    region_entry = tk.Entry(root)
    region_entry.insert(0, env_vars.get('WOW_REGION', ''))
    region_entry.grid(row=3, column=1)
    tk.Label(root, text="WOW_REGION").grid(row=3, column=0)

    desired_items_entry = tk.Entry(root)
    desired_items_entry.insert(0, json.dumps(env_vars.get('DESIRED_ITEMS', '')))
    desired_items_entry.grid(row=4, column=1)
    tk.Label(root, text="DESIRED_ITEMS (JSON format)").grid(row=4, column=0)

    desired_pets_entry = tk.Entry(root)
    desired_pets_entry.insert(0, json.dumps(env_vars.get('DESIRED_PETS', '')))
    desired_pets_entry.grid(row=5, column=1)
    tk.Label(root, text="DESIRED_PETS (JSON format)").grid(row=5, column=0)

    desired_ilvl_entry = tk.Entry(root)
    desired_ilvl_entry.insert(0, json.dumps(env_vars.get('DESIRED_ILVL', '')))
    desired_ilvl_entry.grid(row=6, column=1)
    tk.Label(root, text="DESIRED_ILVL (JSON format)").grid(row=6, column=0)

    desired_ilvl_list_entry = tk.Entry(root)
    desired_ilvl_list_entry.insert(0, json.dumps(env_vars.get('DESIRED_ILVL_LIST', '')))
    desired_ilvl_list_entry.grid(row=7, column=1)
    tk.Label(root, text="DESIRED_ILVL_LIST (JSON format)").grid(row=7, column=0)

    save_button = tk.Button(root, text="Save", 
                            command=lambda: save_env_variables(webhook_url_entry, client_id_entry, client_secret_entry,
                                                               region_entry, desired_items_entry, desired_pets_entry,
                                                               desired_ilvl_entry, desired_ilvl_list_entry)
                           )
    save_button.grid(row=8, column=0, columnspan=2)

    start_button = tk.Button(root, text="Start MEGA-ALERTS",
                             command=lambda: start_mega_alerts(load_data_from_file(env_vars_filename))
                            )
    start_button.grid(row=9, column=0, columnspan=2)

    stop_button = tk.Button(root, text="Stop MEGA-ALERTS", command=stop_mega_alerts)
    stop_button.grid(row=10, column=0, columnspan=2)

    root.mainloop()


create_gui()
