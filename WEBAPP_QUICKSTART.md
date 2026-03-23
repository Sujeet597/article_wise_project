# ⚡ FastAPI Web App - Quick Start

## 5-Minute Setup

### Step 1: Install Dependencies (1 min)
```bash
pip install -r requirements.txt
```

### Step 2: Start Server (instantly)
```bash
python main.py
```

Expected output:
```
============================================================
🚀 MSA Stock Analysis - FastAPI Web Server
============================================================

📡 Starting server...
🌐 Open: http://localhost:8000
📚 API Docs: http://localhost:8000/docs
============================================================
```

### Step 3: Open in Browser (instantly)
```
http://localhost:8000
```

---

## ✨ What You Get

### 4 Tabs in Web Interface

| Tab | What It Does |
|-----|-------------|
| 📂 **File Browser** | Browse any folder, see files, filter by type |
| 🌳 **Folder Structure** | Visual tree of folder hierarchy |
| ⚙️ **MSA Pipeline** | Configure files, run pipeline, watch progress |
| 📊 **Output Files** | Download results, manage output |

---

## 🚀 First Time Using

### 1. Browse Folders
1. Go to **File Browser** tab
2. Paste a folder path: `/Users/john/Documents`
3. Click **Browse**
4. See all files with sizes and types
5. Filter by .csv, .xlsx, etc.

### 2. View Folder Structure
1. Go to **Folder Structure** tab
2. Paste folder path
3. Click **Load Tree**
4. See visual hierarchy

### 3. Run Data Pipeline
1. Go to **Pipeline** tab
2. Paste 5 file/folder paths
3. Click **Run MSA Pipeline**
4. Watch real-time progress
5. See results in **Output Files** tab

### 4. Download Results
1. Go to **Output Files** tab
2. Click **Download** on any file
3. File saves to downloads

---

## 📊 Example Workflow

```
STEP 1: Browse
┌─────────────────────────────────────┐
│ Enter: /Users/john/MSA_Data         │
│ Click: Browse                       │
│ Result: Shows 250 CSV/Excel files   │
└─────────────────────────────────────┘
         ↓
STEP 2: Configure Pipeline
┌─────────────────────────────────────┐
│ Select 5 input files/folders:       │
│ ✓ MSA_Data.csv                      │
│ ✓ Store_Master.xlsx                 │
│ ✓ BASE_DATA/ folder                 │
│ ✓ LIST_DATA/ folder                 │
│ ✓ MRST_Data.xlsx                    │
└─────────────────────────────────────┘
         ↓
STEP 3: Execute
┌─────────────────────────────────────┐
│ Click: Run MSA Pipeline             │
│ Wait: 2-10 minutes                  │
│ Watch: Progress bar (0% → 100%)     │
│ Result: ✓ Complete                  │
└─────────────────────────────────────┘
         ↓
STEP 4: Download
┌─────────────────────────────────────┐
│ Go to: Output Files tab             │
│ See: 3 files generated              │
│ Download:                           │
│ • MSA_Analysis_Output.csv           │
│ • MSA_Analysis_Output.xlsx          │
│ • SUMMARY.txt                       │
└─────────────────────────────────────┘
```

---

## 🌐 Server Endpoints

| Endpoint | What It Does |
|----------|-------------|
| `GET /` | Web interface (HTML) |
| `GET /docs` | Interactive API docs (Swagger) |
| `GET /redoc` | Alternative API docs (ReDoc) |
| `POST /api/browse` | Browse folder |
| `POST /api/tree` | Get folder tree |
| `POST /api/pipeline/run` | Start pipeline |
| `GET /api/pipeline/status` | Check progress |
| `GET /api/output/files` | List results |
| `GET /api/output/download/{file}` | Download file |

---

## 🎨 Features

✅ **File Browsing**
- Browse any folder
- See file details (size, type, date)
- Filter by file type
- Copy paths to clipboard
- Show total size

✅ **Folder Structure**
- Visual tree display
- Nested folders
- File sizes in tree
- Up to 3 levels deep

✅ **Pipeline Execution**
- Configure 5 inputs
- Real-time progress (0-100%)
- Show current step
- Cancel anytime
- Background processing

✅ **Output Management**
- View generated files
- Download results
- See file sizes
- Clear files safely
- Real-time updates

✅ **Responsive Design**
- Works on desktop
- Works on tablet
- Mobile friendly
- Modern UI
- No external dependencies

---

## ⚙️ Settings

### Change Port
Edit `main.py`:
```python
uvicorn.run(
    ...
    port=8000,  # Change this
    ...
)
```

### Access from Network
Other computers can access at:
```
http://your-computer-ip:8000
```

Example:
```
http://192.168.1.100:8000
```

---

## 🐛 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Port already in use | Change port in main.py |
| Can't find folder | Use absolute path, not relative |
| Pipeline won't start | Verify all 5 files exist |
| Progress stuck | Click Cancel, restart server |
| Can't access from network | Use your computer's IP address |

---

## 📚 Full Documentation

Read `WEBAPP_README.md` for:
- Detailed API documentation
- Deployment options
- Performance notes
- Security recommendations
- FAQ section

---

## ✅ Checklist

```
☐ Python 3.8+ installed
☐ Requirements installed: pip install -r requirements.txt
☐ Server running: python main.py
☐ Browser opened: http://localhost:8000
☐ File browser works (browse a folder)
☐ Ready to process data!
```

---

## 🎉 You're Ready!

### Start using immediately:
```bash
# Terminal window 1: Start server
python main.py

# Terminal window 2: Open browser
open http://localhost:8000  # Mac/Linux
start http://localhost:8000 # Windows
```

### First run should take <5 minutes!

---

## 💡 Tips

1. **Use absolute paths** (don't use ~/)
2. **Keep server running** while using web interface
3. **Watch progress** - don't close browser
4. **Download results** before clearing
5. **Check API docs** at http://localhost:8000/docs

---

## 🚀 Next Steps

1. ✅ Get it running (this page)
2. 📚 Read full docs: WEBAPP_README.md
3. 🔧 Configure your data files
4. ⚙️ Run your first pipeline
5. 📊 Download and analyze results

**Enjoy your data pipeline!** 🎊
