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

## 📊 Free vs Pro

| Feature | Free | Pro |
|---------|------|-----|
| Context‑Aware Rule Engine | ✅ | ✅ |
| Batch Folder Scanning | ✅ | ✅ |
| Team Heatmap | ✅ | ✅ |
| Custom Rule Management | ✅ | ✅ |
| PDF Risk Report | ✅ (Basic) | ✅ (Advanced + Charts) |
| OCR Image Recognition | ❌ | ✅ |
| 50+ Rule Templates | ❌ | ✅ |
| Multilingual Scanning | ❌ | ✅ |
| Command‑Line Mode | ❌ | ✅ |
| Debug Logging | ❌ | ✅ |
| Priority Support | ❌ | ✅ |

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
> **Note**: For OCR functionality (Pro feature), you will need to install Tesseract OCR separately. See the [OCR Setup](#-ocr-setup) section below.

---

## 🔧 OCR Setup (Pro Feature)

If you are using the Pro version with OCR image recognition, you need to install Tesseract OCR:

### Windows

1. Download the installer from: <https://github.com/UB-Mannheim/tesseract/wiki>
2. Run the installer and **check `Chinese (Simplified)`** under "Additional languages".
3. Follow the default installation path: `C:\Program Files\Tesseract-OCR`
4. Add `C:\Program Files\Tesseract-OCR` to your system `PATH` environment variable.
5. Verify installation:

```bash
tesseract --version
```

### macOS

```bash
brew install tesseract
brew install tesseract-lang
```

### Linux (Ubuntu/Debian)

```bash
sudo apt install tesseract-ocr
sudo apt install tesseract-ocr-chi-sim
```

---

## 💻 Command‑Line Mode (Pro Feature)

For CI/CD integration and automated batch scanning:

```bash
python cli_mode.py ./path/to/your/documents/
```

Generate a JSON report:

```bash
python cli_mode.py ./path/to/your/documents/ --output report.json
```

Example output:

```text
🔍 Scanning: ./path/to/your/documents/
✅ document1.docx: 3 violations
✅ document2.docx: 0 violations
✅ document3.docx: 5 violations
📊 Scan complete: 3 files, 8 violations
📄 Report saved: report.json
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

## 📚 Rule Templates (Pro Feature)

Pro users can import pre‑built rule templates for specific industries:

| Industry | Included Rules |
|----------|---------------|
| **E‑Commerce** | 10+ rules including "No Absolute Claims", "No Misleading Comparisons", "No False Promotions" |
| **Finance** | 10+ rules including "No Guaranteed Returns", "No Zero‑Risk Claims", "No Insider Trading" |
| **Medical** | 10+ rules including "No Cure Claims", "No 100% Effective Claims", "No Side‑Effect Denials" |
| **General** | 20+ rules including anti‑discrimination and anti‑illegal content rules |

---

## 🔑 Pro Activation

To activate Pro features, you need a valid license key:

1. Launch the application.
2. Click **"🚀 Upgrade to Pro"** in the top‑right corner.
3. You will see your **machine ID** – send this to the developer.
4. Receive your activation code and paste it into the activation dialog.
5. Click **"Activate"** – Pro features are now unlocked.

> **Note**: The license key is tied to your specific machine and cannot be used on other computers.

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
- Official Email:Regula_Official@outlook.com
- Project URL: [https://github.com/20140804/Regula](https://github.com/20140804/Regula)
  Welcome to ask me the questions!!!

---

**Regula** – compliance made simple, secure, and offline. 🦅