# 🚀 Uithub Clone PRO - Dynamic Edition

A powerful, modern desktop application for visualizing, exploring, and exporting GitHub repositories and local project structures. Built with Python and Tkinter, featuring a sleek dark mode UI.

![Uithub Clone PRO](https://via.placeholder.com/800x500?text=Uithub+Clone+PRO+Screenshot)

## ✨ Features

*   **📂 Dual Source Support**: Load projects from a **Local Folder** or directly from a **GitHub URL**.
*   **🎨 Modern Dark UI**: Professional VS Code-inspired dark theme with resizable panes.
*   **⚡ Lazy Loading**: Efficiently handles large projects by loading directories on demand.
*   **🔍 Smart Filtering**: Filter files by extension (e.g., `.py, .js, .md`) in real-time.
*   **🚫 Dynamic Excludes**: Easily manage excluded folders (like `node_modules`, `.git`) via the UI.
*   **📊 Token & Char Counter**: Real-time estimation of tokens and character counts for LLM context optimization.
*   **💾 Export Power**:
    *   **Copy to Clipboard**: One-click copy of the entire project tree + file contents.
    *   **Save to File**: Export the bundle to a text file.
*   **🖱️ Context Menu**: Right-click to copy specific file paths or contents instantly.
*   **⚙️ Auto-Save Settings**: Remembers your last path, filters, and excludes automatically.

## 🛠️ Installation

1.  **Clone the repository** (or download the source):
    ```bash
    git clone https://github.com/rahmanef63/uithub-clone.git
    cd uithub-clone
    ```

2.  **Run the Application**:
    *   **Windows**: Double-click `run_app.bat`.
    *   **Manual**:
        ```bash
        # Create venv (optional but recommended)
        python -m venv .venv
        .venv\Scripts\activate  # Windows
        # source .venv/bin/activate # Mac/Linux

        # Run
        python main.py
        ```

## 💡 Usage

1.  **Select Source**:
    *   Click **Browse** to select a local folder.
    *   Or paste a **GitHub URL** (e.g., `https://github.com/user/repo`) and click **Load**.
2.  **Configure**:
    *   Add file extensions to **Filters** (e.g., `.py, .ts`) to only include specific files.
    *   Add/Remove folders in the **Excludes** list.
3.  **Explore**:
    *   Navigate the tree on the right.
    *   Click files to preview their content and see token stats.
4.  **Export**:
    *   Click **Copy to Clipboard** to get the full prompt-ready bundle.
    *   Paste into ChatGPT, Claude, or Gemini!

## 📝 Requirements

*   Python 3.8+
*   `tkinter` (usually included with Python)
*   Internet connection (for GitHub downloads)

## 🤝 Contributing

Contributions are welcome! Feel free to submit a Pull Request.

## 📄 License

MIT License
