import tkinter as tk
from tkinter import filedialog, Text

def load_text_file():
    file_path = filedialog.askopenfilename(
        title="Choose a text file",
        filetypes=[("Text Documents", "*.txt")]
    )
    if file_path:
        with open(file_path, 'r') as file:
            file_content = file.read()
        text_display.delete(1.0, tk.END)
        text_display.insert(tk.END, file_content)

app = tk.Tk()
app.title("Text File Viewer")
app.geometry("600x400")

load_button = tk.Button(app, text="Load File", command=load_text_file, font=("Arial", 14))
load_button.pack(pady=20)

text_display = Text(app, wrap=tk.WORD, font=("Arial", 12))
text_display.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

app.mainloop()
