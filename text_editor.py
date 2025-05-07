import tkinter as tk
from tkinter import filedialog, messagebox

def open_file():
    filepath = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    if not filepath:
        return
    text_area.delete("1.0", tk.END)
    with open(filepath, "r", encoding="utf-8") as file:
        text_area.insert(tk.END, file.read())
    root.title(f"Editor - {filepath}")

def save_file():
    filepath = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    if not filepath:
        return
    with open(filepath, "w", encoding="utf-8") as file:
        file.write(text_area.get("1.0", tk.END))
    root.title(f"Editor - {filepath}")

root = tk.Tk()
root.title("Simple Text Editor")
root.geometry("600x400")

text_area = tk.Text(root, wrap="word")
text_area.pack(expand=True, fill="both")

menu_bar = tk.Menu(root)
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Open", command=open_file)
file_menu.add_command(label="Save", command=save_file)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)
menu_bar.add_cascade(label="File", menu=file_menu)

root.config(menu=menu_bar)
root.mainloop()
