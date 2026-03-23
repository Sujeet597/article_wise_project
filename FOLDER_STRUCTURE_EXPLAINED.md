# 📁 FOLDER STRUCTURE EXPLANATION

## Project Layout

```
article_wise_project/
│
├── 📄 desktop_app.py              [MAIN APPLICATION - 23KB]
├── 📄 msa_stock_analysis.py       [DATA PIPELINE - 28KB]
├── 📄 requirements.txt            [DEPENDENCIES - 78B]
├── 📄 README.md                   [FULL DOCUMENTATION - 8.5KB]
├── 📄 QUICKSTART.md               [QUICK START - 2.9KB]
├── 🪟 run_app.bat                 [WINDOWS LAUNCHER - 1.5KB]
├── 🐧 run_app.sh                  [MAC/LINUX LAUNCHER - 1.5KB]
│
└── 📁 output/                     [AUTO-CREATED AFTER RUN]
    ├── MSA_Analysis_Output.csv    (Main results)
    ├── MSA_Analysis_Output.xlsx   (Excel format)
    └── SUMMARY.txt                (Processing summary)

```

---

## 📄 FILE DESCRIPTIONS

### 1. **desktop_app.py** (23KB) - THE MAIN APPLICATION ⭐

**What it does:**
- Creates the desktop GUI window
- Displays the File Browser
- Shows Folder Structure
- Runs MSA Pipeline

**Main Components:**

```python
┌─────────────────────────────────────┐
│   MSADesktopApp (Main Window)       │
├─────────────────────────────────────┤
│                                     │
│  ┌─ TAB 1: File Browser 📂        │
│  │  - Browse folder                │
│  │  - Load all files               │
│  │  - Filter by type               │
│  │  - Show file details            │
│  │                                 │
│  ┌─ TAB 2: Folder Structure 🌳    │
│  │  - Display tree view            │
│  │  - Show folder hierarchy        │
│  │  - Display file sizes           │
│  │                                 │
│  ┌─ TAB 3: MSA Pipeline ⚙️         │
│  │  - Configure input files        │
│  │  - Run pipeline                 │
│  │  - Show progress                │
│  │  - Display results              │
│                                     │
└─────────────────────────────────────┘
```

**Classes in this file:**

```
1. FileListWorker (Thread)
   ├─ Scans folder for files
   ├─ Gets file details (size, date, type)
   ├─ Doesn't freeze UI while loading
   └─ Emits signals when done

2. MSAWorker (Thread)
   ├─ Runs data pipeline
   ├─ Doesn't freeze UI while processing
   └─ Sends progress updates

3. MSADesktopApp (Main Window)
   ├─ Creates all GUI elements
   ├─ Handles button clicks
   ├─ Manages tabs
   └─ Shows file information
```

**Key Features:**
```python
def browse_folder()          # Opens folder picker
def load_files()             # Loads files from folder
def display_files()          # Shows files in table
def apply_filter()           # Filters by file type
def run_pipeline()           # Executes MSA pipeline
def build_folder_tree()      # Creates tree structure
```

**What happens when you run it:**
```
1. Creates a window (1200x800 pixels)
2. Builds 3 tabs
3. Waits for user interaction
4. When you click Browse → opens file dialog
5. Scans folder in background thread
6. Updates table when done
7. Shows progress and results
```

---

### 2. **msa_stock_analysis.py** (28KB) - DATA PROCESSING PIPELINE

**What it does:**
- Loads MSA data from CSV
- Loads Store Master from Excel
- Loads external data sources (BASE, LIST, MRST)
- Merges all data together
- Cleans and consolidates
- Exports results

**14-Step Process:**

```
Step 1:  Load Input Data
         ↓
Step 2:  Filter Data (STK_QTY >= 50)
         ↓
Step 3:  Expand Across Stores
         ↓
Step 4:  Load External Data
         ├─ BASE DATA
         ├─ LIST DATA
         └─ MRST Data
         ↓
Step 5:  Prepare Merge Keys
         ↓
Step 6:  Merge BASE DATA
         ↓
Step 7:  Merge LIST DATA
         ↓
Step 8:  Merge MRST Data
         ↓
Step 9:  Clean After Merge
         ↓
Step 10: Consolidate Columns
         ↓
Step 11: Handle Missing Values
         ↓
Step 12: Remove Duplicate CLR Rows
         ↓
Step 13: Generate Output (CSV/Excel)
         ↓
Step 14: Generate Summary
```

**Main Class:**

```python
class MSAStockAnalysis
├─ __init__()                    # Initialize
├─ step1_load_input_data()       # Load CSV + Excel
├─ step2_filter_data()           # Filter by STK_QTY
├─ step3_expand_across_stores()  # Create store combos
├─ step4_load_external_data()    # Load BASE/LIST/MRST
├─ step5_prepare_merge_keys()    # Standardize keys
├─ step6_merge_base_data()       # Merge BASE DATA
├─ step7_merge_list_data()       # Merge LIST DATA
├─ step8_merge_mrst_data()       # Merge MRST Data
├─ step9_clean_after_merge()     # Remove duplicates
├─ step10_consolidate_columns()  # Merge columns
├─ step11_handle_missing_values()# Fill NaN
├─ step12_remove_duplicate_clr_rows() # Clean CLR
├─ step13_generate_output()      # Save results
├─ step14_generate_summary()     # Create summary
└─ run_pipeline()                # Execute all steps
```

**Input Data:**
```
MSA_Data.csv
├─ Row 1: Headers
├─ Row 2-N: Article data
└─ Columns: STK_QTY, MAJ_CAT, GEN_ART_NUMBER, etc.

Store_Master.xlsx
├─ Row 1: Headers
├─ Row 2-N: Store data
└─ Columns: ST_CD, STORE_NAME, etc.

BASE_DATA/
├─ data_GM.csv
├─ data_KIDS.xlsx
├─ data_LADIES.csv
└─ data_MENS.xlsx

LIST_DATA/
├─ listing_1.csv
├─ listing_2.xlsx
└─ listing_3.csv

MRST_Data.xlsx
├─ Sheet 1: Store + Category mapping
├─ Sheet 2: Category level data
└─ Sheet 3: Article level data
```

**Output Data:**
```
output/
├─ MSA_Analysis_Output.csv     # Main result (merged data)
├─ MSA_Analysis_Output.xlsx    # Same as Excel
├─ MSA_Analysis_Output_Part_1.csv (if >100K rows)
├─ MSA_Analysis_Output_Part_2.csv (if >100K rows)
└─ SUMMARY.txt                 # Statistics & info
```

---

### 3. **requirements.txt** (78B) - DEPENDENCIES

**What it is:**
A list of Python libraries needed to run the app

**What it contains:**
```
pandas==1.5.3              # Data manipulation
openpyxl==3.10.9         # Excel file handling
PyQt5==5.15.9            # Desktop GUI framework
PyQt5-sip==12.13.0       # Required for PyQt5
numpy==1.24.3            # Numerical operations
```

**How to use:**
```bash
pip install -r requirements.txt
```

This installs all 5 libraries automatically.

---

### 4. **README.md** (8.5KB) - FULL DOCUMENTATION

**What it is:**
Complete user manual with:
- Installation instructions
- Detailed usage guide
- Troubleshooting section
- Example workflows
- Tips & best practices
- Feature explanations

**Sections:**
```
├─ Features
├─ Installation
├─ How to Use
├─ Data Processing Pipeline (14 steps)
├─ Troubleshooting
├─ Folder Structure
├─ Example Workflow
├─ Tips & Best Practices
├─ Reporting Issues
├─ Changelog
└─ Support
```

**Read this when:**
- You're setting up for the first time
- You want detailed explanations
- You encounter problems
- You want to understand data flow

---

### 5. **QUICKSTART.md** (2.9KB) - QUICK START GUIDE

**What it is:**
Simplified guide for fast setup

**Contains:**
```
├─ Installation (5 minutes)
├─ Run Application
├─ Using the App (3 tabs)
├─ Common Issues
├─ File Requirements
├─ Example Run
└─ What the App Does
```

**Read this when:**
- You just want to run it quickly
- You need basic overview
- You're in a hurry

---

### 6. **run_app.bat** (1.5KB) - WINDOWS LAUNCHER

**What it does:**
Launches the desktop app on Windows

**How to use:**
```
Double-click: run_app.bat

Or in Command Prompt:
python run_app.bat
```

**What it does inside:**
1. Checks if Python is installed
2. Checks if PyQt5 is installed
3. Installs dependencies if missing
4. Runs desktop_app.py
5. Shows error messages if any

---

### 7. **run_app.sh** (1.5KB) - MAC/LINUX LAUNCHER

**What it does:**
Launches the desktop app on Mac/Linux

**How to use:**
```bash
chmod +x run_app.sh
./run_app.sh

Or:
bash run_app.sh
```

**What it does inside:**
1. Checks if Python 3 is installed
2. Checks if pip3 is installed
3. Checks if PyQt5 is installed
4. Installs dependencies if missing
5. Runs desktop_app.py
6. Shows error messages if any

---

## 🔄 HOW FILES WORK TOGETHER

### Scenario: User Runs App

```
1. User double-clicks run_app.bat (Windows)
   or runs ./run_app.sh (Mac/Linux)
   
2. Launcher script checks:
   ✓ Is Python installed?
   ✓ Are dependencies installed?
   
3. Launcher runs:
   python desktop_app.py
   
4. desktop_app.py imports:
   - PyQt5 libraries (for GUI)
   - msa_stock_analysis (for pipeline)
   - pandas, openpyxl (from requirements.txt)
   
5. MSADesktopApp class is created:
   - Creates window
   - Builds 3 tabs
   - Shows GUI
   
6. User clicks "Browse"
   - FileListWorker thread starts
   - Scans folder in background
   - Doesn't freeze UI
   
7. Files display in table
   - User can filter, refresh, view details
   
8. User configures MSA Pipeline
   - Selects input files
   - Selects output folder
   - Clicks "Run Pipeline"
   
9. MSAWorker thread starts
   - Imports MSAStockAnalysis class
   - Runs all 14 steps
   - Doesn't freeze UI
   
10. Pipeline uses:
    - pandas: Read CSV/Excel files
    - openpyxl: Handle Excel sheets
    - msa_stock_analysis.py: Process data
    
11. Results saved to output/ folder
    - CSV file
    - Excel file
    - Summary text file
    
12. User can see results
    - Check output/ folder
    - Open CSV/Excel
    - Review SUMMARY.txt
```

---

## 📊 DATA FLOW DIAGRAM

```
┌─────────────────┐
│  User Clicks    │
│  "Browse Folder"│
└────────┬────────┘
         │
         ▼
┌──────────────────────────┐
│  FileListWorker Thread   │
│  (desktop_app.py)        │
│  - Scans folder          │
│  - Gets file info        │
│  - Non-blocking UI       │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│  display_files()         │
│  - Updates table         │
│  - Shows file details    │
│  - Color-codes files     │
└──────────────────────────┘


┌─────────────────────────┐
│  User Configures        │
│  MSA Pipeline           │
│  - Selects input files  │
│  - Clicks Run Pipeline  │
└────────┬────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│  MSAWorker Thread                │
│  (desktop_app.py)               │
│  - Runs MSAStockAnalysis class  │
│  - 14 processing steps           │
│  - Non-blocking UI               │
└────────┬─────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  Step 1-14 in MSAStockAnalysis         │
│  (msa_stock_analysis.py)               │
│                                        │
│  1. Load Data          (pandas)        │
│  2-4. Filter & Expand  (pandas)        │
│  5-8. Merge Data       (pandas)        │
│  9-12. Clean Data      (pandas)        │
│  13. Export            (pandas/openpyxl)
│  14. Summary           (txt file)      │
└────────┬───────────────────────────────┘
         │
         ▼
┌──────────────────────┐
│  output/ folder      │
├──────────────────────┤
│ - MSA_Output.csv     │
│ - MSA_Output.xlsx    │
│ - SUMMARY.txt        │
└──────────────────────┘
```

---

## 🎯 WHICH FILE TO USE FOR WHAT

| Task | File | Action |
|------|------|--------|
| Run the app | run_app.bat (Windows) or run_app.sh (Mac/Linux) | Double-click or execute |
| Understand app | desktop_app.py | Read the code comments |
| Understand pipeline | msa_stock_analysis.py | Read the code comments |
| Install libraries | requirements.txt | Run `pip install -r requirements.txt` |
| Quick setup | QUICKSTART.md | Read this first |
| Full documentation | README.md | Read for detailed info |
| Troubleshooting | README.md → Troubleshooting section | Look up your issue |

---

## 💾 FILE SIZES & PURPOSES

| File | Size | Type | Purpose |
|------|------|------|---------|
| desktop_app.py | 23KB | Python Code | GUI Application |
| msa_stock_analysis.py | 28KB | Python Code | Data Processing |
| requirements.txt | 78B | Text | Dependencies |
| README.md | 8.5KB | Markdown | Full Documentation |
| QUICKSTART.md | 2.9KB | Markdown | Quick Start |
| run_app.bat | 1.5KB | Batch Script | Windows Launcher |
| run_app.sh | 1.5KB | Shell Script | Mac/Linux Launcher |
| **TOTAL** | **~65KB** | | Complete Project |

---

## 📥 WHAT YOU NEED TO PROVIDE

When you run the app, you need to provide these files:

```
Your Data Folder/
├─ MSA_Data.csv              (REQUIRED)
├─ Store_Master.xlsx         (REQUIRED)
├─ MRST_Data.xlsx            (REQUIRED)
│
├─ BASE_DATA/                (REQUIRED FOLDER)
│  ├─ data_GM.csv
│  ├─ data_KIDS.xlsx
│  └─ ...
│
└─ LIST_DATA/                (REQUIRED FOLDER)
   ├─ list_1.csv
   ├─ list_2.xlsx
   └─ ...
```

---

## 🎓 UNDERSTANDING THE ARCHITECTURE

```
TIER 1: Launchers
├─ run_app.bat       (Windows entry point)
└─ run_app.sh        (Mac/Linux entry point)

TIER 2: GUI Layer
└─ desktop_app.py    (PyQt5 interface)
    ├─ MSADesktopApp (main window)
    ├─ FileListWorker (folder scanner)
    └─ MSAWorker (pipeline executor)

TIER 3: Business Logic
└─ msa_stock_analysis.py (data processing)
    └─ MSAStockAnalysis (14-step pipeline)

TIER 4: Data Layer
├─ Your CSV files
├─ Your Excel files
└─ output/ folder

TIER 5: Documentation
├─ README.md        (full docs)
├─ QUICKSTART.md    (quick guide)
└─ requirements.txt (dependencies)
```

---

## ✅ CHECKLIST BEFORE RUNNING

```
☐ Python 3.8+ installed
☐ requirements.txt present
☐ desktop_app.py present
☐ msa_stock_analysis.py present
☐ run_app.bat (Windows) or run_app.sh (Mac/Linux)
☐ Your data files ready:
   ☐ MSA_Data.csv
   ☐ Store_Master.xlsx
   ☐ MRST_Data.xlsx
   ☐ BASE_DATA folder
   ☐ LIST_DATA folder
```

---

## 🎉 SUMMARY

- **desktop_app.py** = The application you see and click
- **msa_stock_analysis.py** = The engine that processes data
- **run_app.bat/sh** = The buttons you click to start
- **requirements.txt** = The list of ingredients
- **README.md** = The manual
- **QUICKSTART.md** = The cheat sheet

Everything works together to give you:
1. 📂 A file browser to explore folders
2. 🌳 A tree view to see structure
3. ⚙️ A pipeline to process data
4. 📊 CSV/Excel results

**Now you understand the entire structure!** 🚀
