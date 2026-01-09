import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog, messagebox

# -------------------------
# Global variables
# -------------------------
df = None
selected_graph = None
current_fig = None

# -------------------------
# Styling
# -------------------------
BG_COLOR = "#1e1e2f"
BTN_COLOR = "#4CAF50"
BTN_TEXT = "white"
FONT_TITLE = ("Segoe UI", 20, "bold")
FONT_TEXT = ("Segoe UI", 12)
FONT_BTN = ("Segoe UI", 12, "bold")

def make_fullscreen(win):
    win.state("zoomed")
    win.configure(bg=BG_COLOR)

def styled_button(parent, text, command):
    return tk.Button(
        parent, text=text, command=command,
        font=FONT_BTN, bg=BTN_COLOR, fg=BTN_TEXT,
        padx=30, pady=15, relief="flat", cursor="hand2"
    )

# -------------------------
# Window 1: Welcome
# -------------------------
def welcome_window():
    win = tk.Tk()
    win.title("Graph Visualizer")
    make_fullscreen(win)

    frame = tk.Frame(win, bg=BG_COLOR)
    frame.pack(expand=True)

    tk.Label(frame, text="📊 Graph Visualizer",
             font=FONT_TITLE, fg="white", bg=BG_COLOR).pack(pady=20)

    tk.Label(frame, text="Visualize CSV data step-by-step",
             font=FONT_TEXT, fg="lightgray", bg=BG_COLOR).pack(pady=10)

    styled_button(frame, "Continue",
                  lambda: [win.destroy(), file_upload_window()]).pack(pady=40)

    win.mainloop()

# -------------------------
# Window 2: Upload CSV
# -------------------------
def file_upload_window():
    global df
    win = tk.Tk()
    win.title("Upload CSV")
    make_fullscreen(win)

    frame = tk.Frame(win, bg=BG_COLOR)
    frame.pack(expand=True)

    tk.Label(frame, text="📁 Upload CSV File",
             font=FONT_TITLE, fg="white", bg=BG_COLOR).pack(pady=30)

    def upload():
        global df
        path = filedialog.askopenfilename(
            filetypes=[("CSV Files", "*.csv")]
        )
        if not path:
            return
        try:
            df = pd.read_csv(path)
            messagebox.showinfo("Success", f"File loaded\nRows: {df.shape[0]}")
            win.destroy()
            graph_choice_window()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    styled_button(frame, "Select CSV File", upload).pack(pady=20)
    win.mainloop()

# -------------------------
# Window 3: Graph Type
# -------------------------
def graph_choice_window():
    global selected_graph
    win = tk.Tk()
    win.title("Graph Type")
    make_fullscreen(win)

    frame = tk.Frame(win, bg=BG_COLOR)
    frame.pack(expand=True)

    selected_graph = tk.StringVar(value="line")

    tk.Label(frame, text="📈 Select Graph Type",
             font=FONT_TITLE, fg="white", bg=BG_COLOR).pack(pady=30)

    for text, val in [("Line Plot", "line"), ("Bar Plot", "bar"), ("Scatter Plot", "scatter")]:
        tk.Radiobutton(frame, text=text, variable=selected_graph, value=val,
                       font=FONT_TEXT, bg=BG_COLOR, fg="white",
                       selectcolor=BG_COLOR).pack(anchor="w", padx=50, pady=5)

    styled_button(frame, "Next",
                  lambda: [win.destroy(), column_selection_window()]).pack(pady=30)

    win.mainloop()

# -------------------------
# Window 4: Column Selection
# -------------------------
def column_selection_window():
    win = tk.Tk()
    win.title("Select Columns")
    make_fullscreen(win)

    frame = tk.Frame(win, bg=BG_COLOR)
    frame.pack(expand=True)

    tk.Label(frame, text="🧮 Select Columns",
             font=FONT_TITLE, fg="white", bg=BG_COLOR).pack(pady=20)

    x_var = tk.StringVar()
    y_var = tk.StringVar()

    tk.Label(frame, text="X-axis", fg="white", bg=BG_COLOR).pack()
    tk.OptionMenu(frame, x_var, *df.columns).pack(pady=10)

    tk.Label(frame, text="Y-axis", fg="white", bg=BG_COLOR).pack()
    tk.OptionMenu(frame, y_var, *df.columns).pack(pady=10)

    def plot_graph():
        if not x_var.get() or not y_var.get():
            messagebox.showerror("Error", "Select both columns")
            return
        win.destroy()
        show_plot(x_var.get(), y_var.get())

    styled_button(frame, "Plot Graph", plot_graph).pack(pady=30)
    win.mainloop()

# -------------------------
# Final: Graph + Save Option
# -------------------------
def show_plot(x_col, y_col):
    global current_fig

    x = df[x_col]
    y = df[y_col]

    current_fig = plt.figure(figsize=(10, 6))

    if selected_graph.get() == "line":
        plt.plot(x, y, marker="o")
    elif selected_graph.get() == "bar":
        plt.bar(x, y)
    elif selected_graph.get() == "scatter":
        plt.scatter(x, y)

    plt.xlabel(x_col)
    plt.ylabel(y_col)
    plt.grid(True)
    plt.tight_layout()

    def save_graph():
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png")]
        )
        if path:
            current_fig.savefig(path)
            messagebox.showinfo("Saved", "Graph saved successfully!")

    save_win = tk.Tk()
    save_win.title("Save Graph")
    save_win.geometry("400x200")
    save_win.configure(bg=BG_COLOR)

    tk.Label(save_win, text="Graph Generated Successfully!",
             font=FONT_TEXT, fg="white", bg=BG_COLOR).pack(pady=20)

    styled_button(save_win, "Save Graph as Image", save_graph).pack(pady=20)

    save_win.mainloop()
    plt.show()

# -------------------------
# Start Application
# -------------------------
welcome_window()
