from tkinterdnd2 import TkinterDnD, DND_FILES
import tkinter as tk
from tkinter import messagebox
import json
from metadata_tool import extract_metadata
from api_client import search_by_hash
from tkinterdnd2 import TkinterDnD, DND_FILES

def process_file(file_path):

    raw = extract_metadata(file_path)

    if not raw:
        messagebox.showerror("Error", "No metadata found")
        return

    try:
        fp = json.loads(raw)
    except:
        messagebox.showerror("Error", "Invalid metadata")
        return

    result = search_by_hash(fp["hash"])

    output.delete("1.0", tk.END)

    output.insert(tk.END, "=== Fingerprint ===\n")
    output.insert(tk.END, json.dumps(fp, indent=2))

    output.insert(tk.END, "\n\n=== Server Result ===\n")

    if result and "status" not in result:
        output.insert(tk.END, json.dumps(result, indent=2))
    else:
        output.insert(tk.END, "Not found")


def drop(event):
    file_path = event.data.strip("{}")
    process_file(file_path)


# UI
root = TkinterDnD.Tk() 
root.title("USB Guardian Verify Tool (Drag & Drop)")

label = tk.Label(root, text="Drag & Drop File Here", width=50, height=5, bg="lightgray")
label.pack(pady=10)

output = tk.Text(root, width=80, height=25)
output.pack()

# Enable Drag & Drop
root.tk.call('tk', 'scaling', 1.0)
root.tk.call('package', 'require', 'tkdnd')

label.drop_target_register('DND_Files')
label.dnd_bind('<<Drop>>', drop)

root.mainloop()
