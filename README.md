# 🤖 VoiceBot — AI Outbound Calling System

A professional outbound calling system built with Python, Flask, and Twilio. Upload phone lists, customize your message, and call contacts automatically with real-time tracking and result export.

---

## 📸 Preview

![Dashboard Preview](https://via.placeholder.com/800x450/0f172a/6366f1?text=VoiceBot+Dashboard)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📁 **Multi-format Upload** | Excel (.xlsx), CSV, TXT, PDF |
| 🤖 **AI Voice Calls** | Twilio TTS with Amazon Polly voices |
| 📊 **Real-time Dashboard** | Live progress, stats, call status |
| 📥 **Result Export** | Updated Excel with `Call_Status` column |
| ⏱️ **Smart Detection** | 2-second timer marks calls as "answered" |
| 🎨 **Professional UI** | Dark sidebar, clean cards, human-made design |
| 📱 **Responsive** | Works on desktop and mobile |
| 🔒 **Secure** | API keys in `.env`, never in code |

---

## 🗂️ Complete File Structure
voicebot/
│
├── 📄 .env                           # API keys (gitignored)
├── 📄 .env.example                   # Template for API keys
├── 📄 .gitignore                     # Git ignore rules
├── 📄 README.md                      # This file
├── 📄 run.py                         # One-click launcher
│
├── 📁 backend/                       # Flask server
│   ├── 📄 app.py                     # Main Flask application
│   ├── 📄 call_manager.py            # Twilio calling logic + status polling
│   ├── 📄 config.py                  # Environment configuration loader
│   ├── 📄 file_parser.py             # Excel/CSV/TXT/PDF parser
│   ├── 📄 models.py                  # SQLite database models
│   └── 📄 requirements.txt           # Python dependencies
│
├── 📁 frontend/                      # Web dashboard
│   ├── 📄 index.html                 # Main dashboard HTML
│   │
│   ├── 📁 css/
│   │   └── 📄 style.css              # Custom styles (dark theme)
│   │
│   ├── 📁 js/
│   │   └── 📄 app.js                 # Frontend logic & API calls
│   │
│   └── 📁 assets/
│       ├── 📄 logo.svg               # VoiceBot logo
│       └── 📄 favicon.ico            # Browser favicon
│
├── 📁 uploads/                       # Uploaded contact files
├── 📁 campaigns/                     # Exported result files
└── 📄 database.db                    # SQLite database (auto-created)
plain
Copy

---

## 🚀 Quick Start

### Prerequisites

- Python **3.8+**
- Twilio account ([Sign up free](https://www.twilio.com/try-twilio))
- Twilio phone number with **Voice** capability

---

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/voicebot.git
cd voicebot
Step 2: Create Folders
bash
Copy
mkdir uploads
mkdir campaigns
Step 3: Install Dependencies
Windows:
bash
Copy
python -m venv venv
venv\Scripts\activate
pip install -r backend/requirements.txt
Mac/Linux:
bash
Copy
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
Step 4: Configure API Keys
Create a .env file in the root folder (not in backend):
env
Copy
TWILIO_ACCOUNT_SID=ACyour_actual_account_sid_here
TWILIO_AUTH_TOKEN=your_actual_auth_token_here
TWILIO_PHONE_NUMBER=+1234567890
SECRET_KEY=make_up_any_random_string_here
Get your credentials from Twilio Console
Step 5: Run the Server
Option A — One-click launcher:
bash
Copy
python run.py
Option B — Manual:
bash
Copy
venv\Scripts\activate        # Windows
# OR
source venv/bin/activate     # Mac/Linux

python backend/app.py
Open browser: http://localhost:5000
📦 Dependencies
Python Packages (backend/requirements.txt)
Table
Package	Version	Purpose
flask	3.0.3	Web framework
flask-cors	4.0.1	Cross-origin requests
twilio	9.2.0	Voice calling API
pandas	2.2.2	Data processing
openpyxl	3.1.5	Excel read/write
PyPDF2	3.0.1	PDF text extraction
python-dotenv	1.0.1	Environment variables
requests	2.32.3	HTTP requests
Frontend (No build step)
Table
Technology	Purpose
HTML5	Structure
CSS3	Styling (custom, no frameworks)
Vanilla JavaScript	Logic (no frameworks)
Google Fonts (Inter)	Typography
📖 Usage Guide
1. Upload Contact List
Drag & drop or click to browse
Supports: .xlsx, .xls, .csv, .txt, .pdf
Auto-detects phone number columns
Supported number formats:
plain
Copy
+14155551234
+92 300 1234567
0300-1234567
123-456-7890
2. Enter Your Message
Type what the bot should say
Max 500 characters
Live character counter
Example message:
plain
Copy
Hello, this is an automated reminder from ABC Company. 
Your appointment is scheduled for tomorrow at 10 AM. 
Please call us back if you need to reschedule. Thank you.
3. Start Campaign
Click "Start Campaign"
Calls go out one by one (2-second delay between calls)
Watch live progress bar and stats
4. Track Results
Table
Status	Badge Color	Meaning
answered	🟢 Green	Picked up & listened ≥ 2 seconds
no-answer	🟡 Yellow	Rang, no one picked up
voicemail	🔵 Blue	Short duration, likely voicemail
busy	🟠 Orange	Line was busy
failed	🔴 Red	Invalid number or error
pending	⚪ Gray	Waiting to be called
5. Export Results
Click "Export Results"
Downloads updated Excel file with:
Phone_Number — original number
Call_Status — outcome
Duration_Seconds — call length
Twilio_SID — call ID
Completed_At — timestamp
⚠️ Trial Account Limitations
Table
Limitation	Solution
Can only call verified numbers	Verify numbers in Twilio Console or upgrade to paid
"You have a trial account" voice message	Upgrade to paid to remove
Max 5 verified numbers	Upgrade to paid for unlimited
10-minute call limit	Upgrade to paid for unlimited
How to Upgrade (Free)
Go to Twilio Console
Click "Upgrade" at the top
Enter payment method
Add $10–$20 starting balance
All restrictions removed + 75 free voice minutes
🔧 Configuration
Environment Variables (.env)
Table
Variable	Required	Description
TWILIO_ACCOUNT_SID	✅ Yes	Your Twilio Account SID
TWILIO_AUTH_TOKEN	✅ Yes	Your Twilio Auth Token
TWILIO_PHONE_NUMBER	✅ Yes	Your Twilio phone number
SECRET_KEY	✅ Yes	Random string for Flask sessions
OPENAI_API_KEY	❌ No	For AI voice (optional, advanced)
Config Settings (backend/config.py)
Table
Setting	Default	Description
CALL_DELAY_SECONDS	2	Delay between calls
MAX_MESSAGE_LENGTH	500	Max characters in message
🛠️ Tech Stack
plain
Copy
Backend:     Python 3.8+ | Flask | SQLite | Twilio API
Frontend:    HTML5 | CSS3 | Vanilla JavaScript
Voice:       Twilio Programmable Voice | Amazon Polly TTS
Data:        Pandas | OpenPyXL | PyPDF2
🐛 Troubleshooting
Table
Problem	Solution
CONFIG ERROR: Missing required config	Check .env file exists in root, not backend/
0 numbers detected	Check file format. One number per line for TXT
Can only call verified numbers	Verify number in Twilio Console or upgrade account
Message cut off	Check message has no special XML characters
Server not starting	Run pip install -r backend/requirements.txt again
📄 License
MIT License — free for personal and commercial use.
🤝 Contributing
Fork the repository
Create a feature branch (git checkout -b feature/amazing)
Commit changes (git commit -m 'Add amazing feature')
Push to branch (git push origin feature/amazing)
Open a Pull Request
👤 Author
Your Name — LinkedIn | GitHub
Built with ❤️ for AI automation enthusiasts.