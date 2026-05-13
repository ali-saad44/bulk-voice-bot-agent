# 🤖 VoiceBot — AI Outbound Calling System

> A professional outbound calling system built with **Python**, **Flask**, and **Twilio**.  
> Upload phone lists, customize your message, and call contacts automatically with real-time tracking and result export.

---

## ✨ Features

| Feature | Description |
|---|---|
| 📁 **Multi-format Upload** | Excel (.xlsx), CSV, TXT, PDF |
| 🤖 **AI Voice Calls** | Twilio TTS with Amazon Polly voices |
| 📊 **Real-time Dashboard** | Live progress, stats, call status |
| 📥 **Result Export** | Updated Excel with `Call_Status` column |
| ⏱️ **Smart Detection** | 2-second timer marks calls as "answered" |
| 🎨 **Professional UI** | Dark sidebar, clean cards, human-made design |
| 📱 **Responsive** | Works on desktop and mobile |
| 🔒 **Secure** | API keys in `.env`, never in code |

---

## 🗂️ Project Structure

```
voicebot/
│
├── 📄 .env                    # API keys (gitignored)
├── 📄 .env.example            # Template for API keys
├── 📄 .gitignore
├── 📄 README.md
├── 📄 run.py                  # One-click launcher
│
├── 📁 backend/
│   ├── app.py                 # Main Flask application
│   ├── call_manager.py        # Twilio calling logic + status polling
│   ├── config.py              # Environment configuration loader
│   ├── file_parser.py         # Excel/CSV/TXT/PDF parser
│   ├── models.py              # SQLite database models
│   └── requirements.txt       # Python dependencies
│
├── 📁 frontend/
│   ├── index.html             # Main dashboard
│   ├── css/style.css          # Dark theme styles
│   ├── js/app.js              # Frontend logic & API calls
│   └── assets/                # Logo & favicon
│
├── 📁 uploads/                # Uploaded contact files
├── 📁 campaigns/              # Exported result files
└── 📄 database.db             # SQLite database (auto-created)
```

---


### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/voicebot.git
cd voicebot
```

### 2. Create Required Folders

```bash
mkdir uploads campaigns
```

### 3. Install Dependencies

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
pip install -r backend/requirements.txt
```

**Mac / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
```

### 4. Configure API Keys

Create a `.env` file in the **root** folder (not in `backend/`):

```env
TWILIO_ACCOUNT_SID=ACyour_actual_account_sid_here
TWILIO_AUTH_TOKEN=your_actual_auth_token_here
TWILIO_PHONE_NUMBER=+1234567890
SECRET_KEY=make_up_any_random_string_here
```

> Get your credentials from the [Twilio Console](https://console.twilio.com).

### 5. Run the Server

```bash
source venv/bin/activate   # Mac/Linux
# venv\Scripts\activate    # Windows
python backend/app.py
```

Open your browser at **http://localhost:5000**

---

## 📖 Usage Guide

### 1. Upload a Contact List

- Drag & drop or click to browse
- Supported formats: `.xlsx`, `.xls`, `.csv`, `.txt`, `.pdf`
- Auto-detects phone number columns
- Accepted number formats:
  ```
  +14155551234
  +92 300 1234567
  0300-1234567
  123-456-7890
  ```

### 2. Enter Your Message

Type what the bot should say (max 500 characters):

```
Hello, this is an automated reminder from ABC Company.
Your appointment is scheduled for tomorrow at 10 AM.
Please call us back if you need to reschedule. Thank you.
```

### 3. Start the Campaign

- Click **"Start Campaign"**
- Calls go out one by one (2-second delay between calls)
- Watch the live progress bar and stats update in real time

### 4. Track Call Results

| Status | Badge | Meaning |
|---|---|---|
| `answered` | 🟢 Green | Picked up & listened ≥ 2 seconds |
| `no-answer` | 🟡 Yellow | Rang but no one picked up |
| `voicemail` | 🔵 Blue | Short duration, likely voicemail |
| `busy` | 🟠 Orange | Line was busy |
| `failed` | 🔴 Red | Invalid number or error |
| `pending` | ⚪ Gray | Waiting to be called |

### 5. Export Results

Click **"Export Results"** to download an updated Excel file containing:

| Column | Description |
|---|---|
| `Phone_Number` | Original number |
| `Call_Status` | Call outcome |
| `Duration_Seconds` | Call length |
| `Twilio_SID` | Unique call ID |
| `Completed_At` | Timestamp |

---

## 📦 Dependencies

| Package | Version | Purpose |
|---|---|---|
| `flask` | 3.0.3 | Web framework |
| `flask-cors` | 4.0.1 | Cross-origin requests |
| `twilio` | 9.2.0 | Voice calling API |
| `pandas` | 2.2.2 | Data processing |
| `openpyxl` | 3.1.5 | Excel read/write |
| `PyPDF2` | 3.0.1 | PDF text extraction |
| `python-dotenv` | 1.0.1 | Environment variables |
| `requests` | 2.32.3 | HTTP requests |

**Frontend** — no build step required:

| Technology | Purpose |
|---|---|
| HTML5 | Structure |
| CSS3 | Styling (custom dark theme, no frameworks) |
| Vanilla JavaScript | Logic (no frameworks) |
| Google Fonts (Inter) | Typography |

---
