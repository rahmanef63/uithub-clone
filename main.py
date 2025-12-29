import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from pathlib import Path
import threading
import zipfile
import tempfile
import shutil
import urllib.request
import re
import queue

import json

class UithubCloneApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 Uithub Clone PRO - Dynamic Edition")
        self.root.geometry("1400x900")
        self.root.minsize(1000, 600)
        
        # State
        self.current_root_path = None
        self.temp_dir = None
        self.node_map = {}  # Maps tree item ID to Path object
        self.default_excludes = {".next", "node_modules", ".git", "dist", "build", ".vscode", "__pycache__", "public", ".idea", "coverage", "venv", "env"}
        self.excludes = self.default_excludes.copy()
        self.msg_queue = queue.Queue()
        self.config_file = Path("config.json")
        
        self.load_config()
        
        self.setup_styles()
        self.setup_ui()
        self.start_msg_checker()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def load_config(self):
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.excludes = set(config.get("excludes", self.default_excludes))
                    self.last_path = config.get("last_path", str(Path.cwd()))
                    self.last_filters = config.get("filters", "")
            except Exception:
                self.last_path = str(Path.cwd())
                self.last_filters = ""
        else:
            self.last_path = str(Path.cwd())
            self.last_filters = ""

    def save_config(self):
        config = {
            "excludes": list(self.excludes),
            "last_path": self.path_var.get(),
            "filters": self.ext_var.get()
        }
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f)
        except Exception as e:
            print(f"Failed to save config: {e}")

    def on_closing(self):
        self.save_config()
        self.root.destroy()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Dark Theme Colors
        self.colors = {
            "bg": "#2d2d2d",
            "fg": "#ffffff",
            "accent": "#007acc",
            "accent_hover": "#005a9e",
            "panel_bg": "#252526",
            "input_bg": "#3c3c3c",
            "input_fg": "#cccccc",
            "border": "#454545",
            "success": "#4ec9b0"
        }
        
        # Configure Root
        self.root.configure(bg=self.colors["bg"])
        
        # Configure Styles
        style.configure("TFrame", background=self.colors["bg"])
        style.configure("TLabelframe", background=self.colors["bg"], bordercolor=self.colors["border"])
        style.configure("TLabelframe.Label", background=self.colors["bg"], foreground=self.colors["fg"], font=("Segoe UI", 10, "bold"))
        
        # Buttons
        style.configure("TButton", 
                       font=("Segoe UI", 9), 
                       background=self.colors["input_bg"], 
                       foreground=self.colors["fg"],
                       borderwidth=0,
                       focuscolor=self.colors["accent"])
        style.map("TButton", 
                 background=[("active", self.colors["border"]), ("pressed", self.colors["accent"])],
                 foreground=[("active", "white")])
                 
        # Accent Button
        style.configure("Accent.TButton", 
                       background=self.colors["accent"], 
                       foreground="white", 
                       font=("Segoe UI", 9, "bold"))
        style.map("Accent.TButton", 
                 background=[("active", self.colors["accent_hover"])])
        
        # Inputs
        style.configure("TEntry", 
                       fieldbackground=self.colors["input_bg"],
                       foreground=self.colors["fg"],
                       insertcolor="white",
                       borderwidth=0)
                       
        # Treeview
        style.configure("Treeview", 
                       background=self.colors["panel_bg"],
                       foreground=self.colors["fg"], 
                       fieldbackground=self.colors["panel_bg"],
                       borderwidth=0,
                       font=("Segoe UI", 10))
        style.map("Treeview", 
                 background=[("selected", self.colors["accent"])],
                 foreground=[("selected", "white")])
        style.configure("Treeview.Heading", 
                       background=self.colors["bg"], 
                       foreground=self.colors["fg"], 
                       font=("Segoe UI", 9, "bold"))
                       
        # Scrollbars
        style.configure("Vertical.TScrollbar", 
                       background=self.colors["input_bg"],
                       troughcolor=self.colors["bg"],
                       arrowcolor=self.colors["fg"])

    def setup_ui(self):
        # Header
        header_frame = tk.Frame(self.root, bg=self.colors["panel_bg"], height=60)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        # Logo/Title Area
        title_box = tk.Frame(header_frame, bg=self.colors["panel_bg"])
        title_box.pack(side="left", padx=20, pady=10)
        
        tk.Label(title_box, text="🚀", font=('Segoe UI', 24), bg=self.colors["panel_bg"], fg=self.colors["fg"]).pack(side="left", padx=(0,10))
        
        title_text_frame = tk.Frame(title_box, bg=self.colors["panel_bg"])
        title_text_frame.pack(side="left")
        tk.Label(title_text_frame, text="Uithub Clone", font=('Segoe UI', 14, 'bold'), bg=self.colors["panel_bg"], fg=self.colors["fg"]).pack(anchor="w")
        tk.Label(title_text_frame, text="PRO EDITION", font=('Segoe UI', 8, 'bold'), bg=self.colors["panel_bg"], fg=self.colors["accent"]).pack(anchor="w")

        # Main PanedWindow
        self.main_pane = ttk.PanedWindow(self.root, orient="horizontal")
        self.main_pane.pack(fill="both", expand=True, padx=0, pady=0)
        
        # --- Left Panel: Controls ---
        self.left_frame = ttk.Frame(self.main_pane, padding=15)
        self.main_pane.add(self.left_frame, weight=1)
        
        # Input Section
        ttk.Label(self.left_frame, text="SOURCE", font=("Segoe UI", 8, "bold"), foreground=self.colors["accent"]).pack(anchor="w", pady=(0, 5))
        
        input_frame = ttk.Frame(self.left_frame)
        input_frame.pack(fill="x", pady=(0, 20))
        
        self.path_var = tk.StringVar(value=self.last_path)
        entry = ttk.Entry(input_frame, textvariable=self.path_var)
        entry.pack(fill="x", pady=(0, 5), ipady=3)
        
        btn_grid = ttk.Frame(input_frame)
        btn_grid.pack(fill="x")
        ttk.Button(btn_grid, text="📂 Browse", command=self.browse_path, width=10).pack(side="left", padx=(0, 5), fill="x", expand=True)
        ttk.Button(btn_grid, text="⬇️ Load", command=self.start_loading, style="Accent.TButton", width=10).pack(side="right", fill="x", expand=True)

        # Filters Section
        ttk.Label(self.left_frame, text="FILTERS", font=("Segoe UI", 8, "bold"), foreground=self.colors["accent"]).pack(anchor="w", pady=(0, 5))
        
        filter_frame = ttk.Frame(self.left_frame)
        filter_frame.pack(fill="x", pady=(0, 20))
        
        self.ext_var = tk.StringVar(value=self.last_filters)
        ttk.Entry(filter_frame, textvariable=self.ext_var).pack(fill="x", pady=(0, 5), ipady=3)
        ttk.Label(filter_frame, text="e.g. .py, .js (empty = all)", font=("Segoe UI", 8), foreground="#888888").pack(anchor="w")

        # Excludes Section
        ttk.Label(self.left_frame, text="EXCLUDES", font=("Segoe UI", 8, "bold"), foreground=self.colors["accent"]).pack(anchor="w", pady=(0, 5))
        
        exclude_frame = ttk.Frame(self.left_frame)
        exclude_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        # Add Exclude Input
        add_ex_frame = ttk.Frame(exclude_frame)
        add_ex_frame.pack(fill="x", pady=(0, 5))
        self.new_exclude_var = tk.StringVar()
        ttk.Entry(add_ex_frame, textvariable=self.new_exclude_var).pack(side="left", fill="x", expand=True, ipady=3)
        ttk.Button(add_ex_frame, text="➕", width=3, command=self.add_exclude).pack(side="right", padx=(5, 0))
        
        # Listbox with custom styling
        list_frame = tk.Frame(exclude_frame, bg=self.colors["input_bg"], bd=0)
        list_frame.pack(fill="both", expand=True)
        
        self.exclude_listbox = tk.Listbox(list_frame, 
                                        bg=self.colors["input_bg"], 
                                        fg=self.colors["fg"],
                                        selectbackground=self.colors["accent"],
                                        selectforeground="white",
                                        bd=0,
                                        highlightthickness=0,
                                        activestyle="none",
                                        font=("Segoe UI", 9))
        sb = ttk.Scrollbar(list_frame, orient="vertical", command=self.exclude_listbox.yview)
        self.exclude_listbox.configure(yscrollcommand=sb.set)
        
        self.exclude_listbox.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        sb.pack(side="right", fill="y")
        
        ttk.Button(exclude_frame, text="🗑️ Remove Selected", command=self.remove_exclude).pack(fill="x", pady=5)
        self.refresh_exclude_list()

        # Actions Section
        action_frame = ttk.Frame(self.left_frame)
        action_frame.pack(fill="x", side="bottom", pady=10)
        
        ttk.Button(action_frame, text="📋 Copy to Clipboard", command=self.copy_all, style="Accent.TButton").pack(fill="x", pady=5, ipady=5)
        ttk.Button(action_frame, text="💾 Save to File", command=self.save_all).pack(fill="x", pady=2, ipady=2)

        # Stats Section
        stats_frame = ttk.LabelFrame(self.left_frame, text="STATS", padding=10)
        stats_frame.pack(fill="x", side="bottom", pady=(0, 10))
        
        self.char_count_var = tk.StringVar(value="Chars: 0")
        self.token_count_var = tk.StringVar(value="Tokens: 0")
        
        ttk.Label(stats_frame, textvariable=self.char_count_var, font=("Segoe UI", 9)).pack(anchor="w")
        ttk.Label(stats_frame, textvariable=self.token_count_var, font=("Segoe UI", 9)).pack(anchor="w")

        # --- Right Panel: Tree & Content ---
        self.right_pane = ttk.PanedWindow(self.main_pane, orient="vertical")
        self.main_pane.add(self.right_pane, weight=4)
        
        # Tree View
        tree_container = ttk.Frame(self.right_pane)
        self.right_pane.add(tree_container, weight=1)
        
        # Tree Header
        tree_header = tk.Frame(tree_container, bg=self.colors["panel_bg"], height=30)
        tree_header.pack(fill="x")
        tk.Label(tree_header, text="📂 PROJECT STRUCTURE", font=("Segoe UI", 9, "bold"), bg=self.colors["panel_bg"], fg=self.colors["fg"]).pack(side="left", padx=5, pady=5)
        
        self.tree = ttk.Treeview(tree_container, selectmode="browse", show="tree")
        tree_scroll_y = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        tree_scroll_x = ttk.Scrollbar(tree_container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        tree_scroll_y.pack(side="right", fill="y")
        tree_scroll_x.pack(side="bottom", fill="x")
        
        self.tree.bind("<<TreeviewOpen>>", self.on_tree_open)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        
        # Content View
        content_container = ttk.Frame(self.right_pane)
        self.right_pane.add(content_container, weight=2)
        
        # Content Header
        content_header = tk.Frame(content_container, bg=self.colors["panel_bg"], height=30)
        content_header.pack(fill="x")
        tk.Label(content_header, text="📄 FILE CONTENT", font=("Segoe UI", 9, "bold"), bg=self.colors["panel_bg"], fg=self.colors["fg"]).pack(side="left", padx=5, pady=5)
        
        self.file_stats_var = tk.StringVar(value="")
        tk.Label(content_header, textvariable=self.file_stats_var, font=("Consolas", 9), bg=self.colors["panel_bg"], fg=self.colors["accent"]).pack(side="right", padx=10)

        self.content_text = tk.Text(content_container, wrap="none", font=("Consolas", 10),
                                  bg=self.colors["input_bg"], fg=self.colors["fg"], 
                                  insertbackground="white", borderwidth=0, padx=10, pady=10)
        content_scroll_y = ttk.Scrollbar(content_container, orient="vertical", command=self.content_text.yview)
        content_scroll_x = ttk.Scrollbar(content_container, orient="horizontal", command=self.content_text.xview)
        self.content_text.configure(yscrollcommand=content_scroll_y.set, xscrollcommand=content_scroll_x.set)
        
        self.content_text.pack(side="left", fill="both", expand=True)
        content_scroll_y.pack(side="right", fill="y")
        content_scroll_x.pack(side="bottom", fill="x")
        
        # Context Menu
        self.context_menu = tk.Menu(self.root, tearoff=0, bg=self.colors["panel_bg"], fg=self.colors["fg"], activebackground=self.colors["accent"], activeforeground="white")
        self.context_menu.add_command(label="Copy Path", command=self.copy_selected_path)
        self.context_menu.add_command(label="Copy Content", command=self.copy_selected_content)
        self.tree.bind("<Button-3>", self.show_context_menu)
        
        # Status Bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = tk.Label(self.root, textvariable=self.status_var, bd=0, relief=tk.FLAT, anchor="w", 
                            bg=self.colors["accent"], fg="white", font=("Segoe UI", 9), padx=10, pady=5)
        status_bar.pack(side="bottom", fill="x")

    # --- Logic & Events ---

    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def copy_selected_path(self):
        selection = self.tree.selection()
        if selection:
            path = self.node_map.get(selection[0])
            if path:
                self.root.clipboard_clear()
                self.root.clipboard_append(str(path))
                self.status_var.set(f"Copied path: {path.name}")

    def copy_selected_content(self):
        selection = self.tree.selection()
        if selection:
            path = self.node_map.get(selection[0])
            if path and path.is_file():
                try:
                    content = path.read_text(encoding='utf-8', errors='replace')
                    self.root.clipboard_clear()
                    self.root.clipboard_append(content)
                    self.status_var.set(f"Copied content of {path.name}")
                except Exception as e:
                    messagebox.showerror("Error", f"Could not read file: {e}")
            else:
                messagebox.showwarning("Warning", "Please select a file")

    def start_msg_checker(self):
        try:
            while True:
                msg_type, msg_content = self.msg_queue.get_nowait()
                if msg_type == "error":
                    messagebox.showerror("Error", msg_content)
                elif msg_type == "info":
                    messagebox.showinfo("Info", msg_content)
                elif msg_type == "status":
                    self.status_var.set(msg_content)
                elif msg_type == "tree_root":
                    self.populate_tree_root(msg_content)
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.start_msg_checker)

    def browse_path(self):
        path = filedialog.askdirectory()
        if path:
            self.path_var.set(path)

    def refresh_exclude_list(self):
        self.exclude_listbox.delete(0, tk.END)
        for item in sorted(self.excludes):
            self.exclude_listbox.insert(tk.END, item)

    def add_exclude(self):
        val = self.new_exclude_var.get().strip()
        if val and val not in self.excludes:
            self.excludes.add(val)
            self.refresh_exclude_list()
            self.new_exclude_var.set("")

    def remove_exclude(self):
        selection = self.exclude_listbox.curselection()
        if not selection:
            return
        items = [self.exclude_listbox.get(i) for i in selection]
        for item in items:
            self.excludes.discard(item)
        self.refresh_exclude_list()

    def is_github_url(self, url):
        return bool(re.match(r'https?://github\.com/[\w\-\./]+/?$', url))

    def start_loading(self):
        path_or_url = self.path_var.get().strip()
        if not path_or_url:
            messagebox.showwarning("Input Required", "Please enter a local path or GitHub URL")
            return
        
        # Clear UI
        self.tree.delete(*self.tree.get_children())
        self.content_text.delete(1.0, tk.END)
        self.node_map.clear()
        self.status_var.set("Working...")
        
        threading.Thread(target=self._load_thread, args=(path_or_url,), daemon=True).start()

    def _load_thread(self, path_or_url):
        try:
            if self.is_github_url(path_or_url):
                self.msg_queue.put(("status", "Downloading GitHub repository..."))
                root_path = self.download_github_zip(path_or_url)
            else:
                root_path = Path(path_or_url)
                if not root_path.exists():
                    raise ValueError("Path does not exist")
            
            self.current_root_path = root_path.resolve()
            self.msg_queue.put(("status", f"Loaded: {self.current_root_path.name}"))
            self.msg_queue.put(("tree_root", self.current_root_path))
            
        except Exception as e:
            self.msg_queue.put(("error", str(e)))
            self.msg_queue.put(("status", "Error occurred"))

    def download_github_zip(self, github_url):
        # Cleanup previous temp
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
            except:
                pass
                
        match = re.match(r'https?://github\.com/([^/]+)/([^/]+)/?', github_url)
        if not match:
            raise ValueError("Invalid GitHub URL")
        
        user, repo = match.groups()
        
        # Clean repo name (remove .git)
        if repo.endswith('.git'):
            repo = repo[:-4]
            
        zip_url = f"https://github.com/{user}/{repo}/archive/refs/heads/main.zip"
        
        # Create temp file and close it immediately so we can use it safely
        temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
        temp_zip.close()
        
        try:
            req = urllib.request.Request(zip_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response, open(temp_zip.name, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)
            
            extract_dir = Path(tempfile.mkdtemp())
            with zipfile.ZipFile(temp_zip.name, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            # Find the inner folder (usually repo-main)
            inner_dirs = [d for d in extract_dir.iterdir() if d.is_dir()]
            if inner_dirs:
                return inner_dirs[0]
            return extract_dir
            
        finally:
            if os.path.exists(temp_zip.name):
                try:
                    os.unlink(temp_zip.name)
                except:
                    pass

    def populate_tree_root(self, root_path):
        # Insert root node
        root_node = self.tree.insert("", "end", text=f"📁 {root_path.name}", open=True)
        self.node_map[root_node] = root_path
        
        # Populate first level
        self.populate_node(root_node, root_path)

    def populate_node(self, parent_id, path):
        # Clear dummy nodes if any
        self.tree.delete(*self.tree.get_children(parent_id))
        
        try:
            # Sort: Directories first, then files
            items = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
            
            for item in items:
                if item.name in self.excludes:
                    continue
                
                # Filter extensions for files
                if item.is_file() and not self.check_extension(item.name):
                    continue
                
                if item.is_dir():
                    oid = self.tree.insert(parent_id, "end", text=f"📁 {item.name}", open=False)
                    self.node_map[oid] = item
                    # Add dummy node to make it expandable
                    self.tree.insert(oid, "end", text="dummy")
                else:
                    oid = self.tree.insert(parent_id, "end", text=f"📄 {item.name}")
                    self.node_map[oid] = item
                    
        except PermissionError:
            pass

    def check_extension(self, filename):
        filters = [f.strip() for f in self.ext_var.get().split(",") if f.strip()]
        if not filters:
            return True
        return any(filename.endswith(ext) for ext in filters)

    def on_tree_open(self, event):
        item_id = self.tree.focus()
        path = self.node_map.get(item_id)
        
        if path and path.is_dir():
            # Check if it has a dummy child
            children = self.tree.get_children(item_id)
            if children and self.tree.item(children[0], "text") == "dummy":
                self.populate_node(item_id, path)

    def on_tree_select(self, event):
        selection = self.tree.selection()
        if not selection:
            return
        
        item_id = selection[0]
        path = self.node_map.get(item_id)
        
        if path and path.is_file():
            self.display_file_content(path)

    def estimate_tokens(self, text):
        return len(text) // 4

    def display_file_content(self, path):
        self.content_text.delete(1.0, tk.END)
        try:
            size = path.stat().st_size
            if size > 500 * 1024: # 500KB limit for preview
                self.content_text.insert(1.0, f"⚠️ File is too large to preview ({size/1024:.1f} KB)\nPath: {path}")
                self.file_stats_var.set(f"Size: {size/1024:.1f} KB")
                return

            content = path.read_text(encoding='utf-8', errors='replace')
            self.content_text.insert(1.0, content)
            
            tokens = self.estimate_tokens(content)
            chars = len(content)
            self.file_stats_var.set(f"Chars: {chars} | Tokens: ~{tokens}")
            self.status_var.set(f"Viewing: {path.name}")
        except Exception as e:
            self.content_text.insert(1.0, f"Error reading file: {e}")

    def get_all_files(self):
        """Generator to yield all files based on current filters"""
        if not self.current_root_path:
            return
            
        stack = [self.current_root_path]
        while stack:
            current = stack.pop()
            try:
                # Sort to ensure deterministic order
                for item in sorted(current.iterdir(), key=lambda x: x.name.lower(), reverse=True):
                    if item.name in self.excludes:
                        continue
                    
                    if item.is_dir():
                        stack.append(item)
                    elif item.is_file():
                        if self.check_extension(item.name):
                            yield item
            except PermissionError:
                continue

    def generate_export_text(self):
        if not self.current_root_path:
            return ""
            
        output = []
        
        # 1. Tree Structure
        output.append("=" * 50)
        output.append(f"PROJECT STRUCTURE: {self.current_root_path.name}")
        output.append("=" * 50)
        
        # Helper to print tree
        def print_tree(directory, prefix=""):
            try:
                items = sorted(directory.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
                filtered_items = [
                    i for i in items 
                    if i.name not in self.excludes and 
                    (i.is_dir() or self.check_extension(i.name))
                ]
                
                for i, item in enumerate(filtered_items):
                    is_last = (i == len(filtered_items) - 1)
                    connector = "└── " if is_last else "├── "
                    output.append(f"{prefix}{connector}{item.name}")
                    
                    if item.is_dir():
                        new_prefix = prefix + ("    " if is_last else "│   ")
                        print_tree(item, new_prefix)
            except PermissionError:
                pass

        print_tree(self.current_root_path)
        output.append("\n")
        
        # 2. File Contents
        output.append("=" * 50)
        output.append("FILE CONTENTS")
        output.append("=" * 50)
        output.append("\n")
        
        count = 0
        total_chars = 0
        for file_path in self.get_all_files():
            try:
                rel_path = file_path.relative_to(self.current_root_path)
                output.append(f"📄 FILE: {rel_path}")
                output.append("-" * 50)
                
                if file_path.stat().st_size > 100 * 1024:
                    output.append("(Content skipped - File too large)")
                else:
                    content = file_path.read_text(encoding='utf-8', errors='replace')
                    output.append(content)
                    total_chars += len(content)
                
                output.append("\n" + "-" * 50 + "\n")
                count += 1
            except Exception as e:
                output.append(f"(Error reading file: {e})\n")
        
        return "\n".join(output), count, total_chars

    def copy_all(self):
        if not self.current_root_path:
            messagebox.showwarning("Warning", "No project loaded")
            return
            
        self.status_var.set("Generating export...")
        self.root.update()
        
        text, count, chars = self.generate_export_text()
        tokens = self.estimate_tokens(text)
        
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        
        self.char_count_var.set(f"Chars: {chars}")
        self.token_count_var.set(f"Tokens: ~{tokens}")
        self.status_var.set(f"Copied {count} files to clipboard")
        messagebox.showinfo("Success", f"Copied project tree and {count} files to clipboard.\nTotal Chars: {chars}\nEstimated Tokens: ~{tokens}")

    def save_all(self):
        if not self.current_root_path:
            messagebox.showwarning("Warning", "No project loaded")
            return
            
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if path:
            self.status_var.set("Saving...")
            self.root.update()
            
            text, count, chars = self.generate_export_text()
            tokens = self.estimate_tokens(text)
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(text)
                
                self.char_count_var.set(f"Chars: {chars}")
                self.token_count_var.set(f"Tokens: ~{tokens}")
                self.status_var.set(f"Saved to {Path(path).name}")
                messagebox.showinfo("Success", f"Saved {count} files to {path}\nTotal Chars: {chars}\nEstimated Tokens: ~{tokens}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save: {e}")
            self.root.update()
            
            text, count, chars = self.generate_export_text()
            tokens = self.estimate_tokens(text)
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(text)
                self.status_var.set(f"Saved to {Path(path).name} | ~{tokens} tokens")
                messagebox.showinfo("Success", f"Saved {count} files to {path}\nEstimated Tokens: ~{tokens}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = UithubCloneApp(root)
    root.mainloop()
