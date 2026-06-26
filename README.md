# 🦅 Regula – Compliance Eagle‑Eye Scanner

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)](https://github.com/20140804/Regula)

**Regula** is a fully offline, privacy‑first compliance scanner that detects misleading or illegal phrasing in marketing copy and generates professional PDF risk reports. All processing stays on your local machine – no data ever leaves your hard drive.

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🧠 **Context‑Aware Rules** | Flags “first” more severely in headlines, “zero risk” as fatal – it understands context. |
| 📁 **Batch Scanning** | Scan an entire folder of `.docx` files with one click. |
| 🔥 **Team Heatmap** | Visual overview of which files contain the most violations – ideal for managers. |
| 📄 **PDF Risk Reports** | Export formal compliance reports with violation details and fix suggestions. |
| ⚙️ **Custom Rule Management** | Add, edit or delete rules interactively – adapt to your industry. |
| 🎨 **Native GUI** | Drag‑and‑drop interface built with PySide6. |
| 🚫 **Zero Cloud** | Runs completely offline – no internet required. |

---

## 🚀 Quick Start

### Option 1 – Download the executable (no Python needed)

1. Go to the [Releases](https://github.com/20140804/Regula/releases) page.  
2. Download the latest `Regula.exe`.  
3. Double‑click to run.

### Option 2 – Run from source

```bash
git clone https://github.com/20140804/Regula.git
cd Regula
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

---

## 📝 Custom Rules

You can define your own rules through the Rule Management dialog. Each rule can include:

- **Keyword** – the word or phrase to detect.  
- **Near‑keyword** – an optional second term that must appear within a set distance.  
- **Position** – restrict detection to headlines or body text.  
- **Severity** – choose from `Fatal`, `High`, or `Normal`.

Example rule:

```json
{
  "name": "No Franchise Solicitation",
  "keyword": "franchise",
  "severity": "High",
  "position": "Any",
  "suggestion": "Avoid using 'franchise' in promotional content."
}
```

---

## 🛠️ Technology Stack

- **Python 3.8+** – core language  
- **PySide6** – GUI framework  
- **python‑docx** – Word document parsing  
- **reportlab** – PDF generation  
- **PyInstaller** – executable packaging  

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repository.  
2. Create a feature branch:  
   ```bash
   git checkout -b feature/your-feature
   ```
3. Commit your changes:  
   ```bash
   git commit -m "Add your feature"
   ```
4. Push to the branch:  
   ```bash
   git push origin feature/your-feature
   ```
5. Open a Pull Request.

---

## 📄 License

Distributed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

## 📧 Contact

- Author: [20140804](https://github.com/20140804)  
- Project URL: [https://github.com/20140804/Regula](https://github.com/20140804/Regula)
- Official Email:Regula_Official@outlook.com
Welcome to ask me questions about the software!!!

---

**Regula** – compliance made simple, secure, and offline. 🦅