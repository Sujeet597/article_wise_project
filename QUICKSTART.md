# 🚀 Quick Start Guide

## Installation (5 minutes)

### 1. Clone Repository
```bash
git clone https://github.com/Sujeet597/article_wise_project.git
cd article_wise_project
```

### 2. Install Python (if needed)
- Download from [python.org](https://www.python.org)
- Choose Python 3.8+

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## Run Application

### Windows
**Double-click:** `run_app.bat`

Or in Command Prompt:
```bash
python desktop_app.py
```

### Mac/Linux
**In Terminal:**
```bash
chmod +x run_app.sh
./run_app.sh
```

Or:
```bash
python3 desktop_app.py
```

---

## Using the App (3 tabs)

### 📂 Tab 1: File Browser
1. Click **🔍 Browse** → Select your folder
2. See all files automatically
3. Filter by type if needed
4. Click **🔄 Refresh** to update

### 🌳 Tab 2: Folder Structure
- Visual tree of your folders
- Expand folders to explore
- See file sizes

### ⚙️ Tab 3: MSA Pipeline
1. Select your input files (click Browse buttons)
2. Verify output folder
3. Click **▶️ Run MSA Pipeline**
4. Wait for completion
5. Check results in output folder

---

## Common Issues

| Issue | Solution |
|-------|----------|
| "No module PyQt5" | `pip install PyQt5 --force-reinstall` |
| App won't start | Check Python version `python --version` |
| Files not showing | Ensure folder has read permissions |
| Pipeline fails | Verify file paths exist |

---

## File Requirements

For MSA Pipeline to work, you need:

```
Input Files:
├── MSA_Data.csv           (your main data)
├── Store_Master.xlsx      (store list)
├── BASE_DATA/             (folder with category files)
│   ├── data_GM.xlsx
│   ├── data_KIDS.csv
│   └── ...
├── LIST_DATA/             (folder with listing data)
│   ├── list_1.csv
│   └── ...
└── MRST_Data.xlsx         (3-sheet file)

Output:
└── output/                (auto-created)
    ├── MSA_Analysis_Output.csv
    ├── MSA_Analysis_Output.xlsx
    └── SUMMARY.txt
```

---

## Example Run

```
1. Open desktop_app.py
2. Tab: File Browser → Browse "C:\Data"
   → See 250 files
   → Filter by .csv → See 45 files
   
3. Tab: MSA Pipeline → Select files:
   ✓ MSA_Data.csv
   ✓ Store_Master.xlsx
   ✓ BASE_DATA folder
   ✓ LIST_DATA folder
   ✓ MRST_Data.xlsx
   
4. Click ▶️ Run MSA Pipeline
5. Wait ~2-5 minutes
6. See "✅ Pipeline completed successfully!"
7. Check output/ folder for results
```

---

## Need Help?

1. Check **README.md** for detailed docs
2. Check **Troubleshooting** section
3. Review error messages carefully
4. Check file paths are correct

---

## What the App Does

- 📂 **Browse**: View all files in any folder
- 🌳 **Explore**: See folder structure visually
- ⚙️ **Process**: Run MSA data pipeline
- 📊 **Export**: Generate CSV, Excel, and reports

---

**Ready to go! 🎉**
