# 📊 VISUAL FOLDER STRUCTURE & COMPONENTS

## PROJECT TREE VIEW

```
📦 article_wise_project/
│
├── 🟦 LAUNCHERS (Click to Start)
│   ├── run_app.bat        ← Double-click on Windows
│   └── run_app.sh         ← Run on Mac/Linux
│
├── 🟩 CORE APPLICATION FILES
│   ├── desktop_app.py     ← Main GUI application (23KB)
│   └── msa_stock_analysis.py  ← Data processing engine (28KB)
│
├── 🟧 CONFIGURATION
│   └── requirements.txt    ← Dependencies list (78B)
│
├── 📖 DOCUMENTATION
│   ├── README.md           ← Full user manual (8.5KB)
│   ├── QUICKSTART.md       ← Quick start guide (2.9KB)
│   └── FOLDER_STRUCTURE_EXPLAINED.md  ← This file!
│
└── 📁 OUTPUT FOLDER (Created when you run pipeline)
    ├── MSA_Analysis_Output.csv
    ├── MSA_Analysis_Output.xlsx
    └── SUMMARY.txt
```

---

## 🎯 COMPONENT RELATIONSHIP MAP

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                    DESKTOP APPLICATION                      │
│                   (desktop_app.py - 23KB)                  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                  GUI WINDOW                          │  │
│  │              (1200 x 800 pixels)                     │  │
│  │                                                      │  │
│  │  ┌──────────────────────────────────────────────┐   │  │
│  │  │ TAB 1: File Browser 📂                       │   │  │
│  │  │                                              │   │  │
│  │  │  [Browse] [Refresh]    Filter: [All Files▼] │   │  │
│  │  │                                              │   │  │
│  │  │  ┌─ FILE TABLE ──────────────────────────┐  │   │  │
│  │  │  │ File Name │ Type │ Size │ Modified   │  │   │  │
│  │  │  │ data.csv  │ .csv │2.5MB │ 2024-03-23│  │   │  │
│  │  │  │ store.xls │ .xls │1.2MB │ 2024-03-22│  │   │  │
│  │  │  └────────────────────────────────────────┘  │   │  │
│  │  │                                              │   │  │
│  │  │  Selected: data.csv                          │   │  │
│  │  └──────────────────────────────────────────────┘   │  │
│  │                                                      │  │
│  │  ┌──────────────────────────────────────────────┐   │  │
│  │  │ TAB 2: Folder Structure 🌳                   │   │  │
│  │  │                                              │   │  │
│  │  │  📁 Project_Data                             │   │  │
│  │  │  ├─ 📁 BASE_DATA                             │   │  │
│  │  │  │  ├─ 📄 data_GM.csv                        │   │  │
│  │  │  │  ├─ 📄 data_KIDS.xlsx                     │   │  │
│  │  │  │  └─ 📄 data_LADIES.csv                    │   │  │
│  │  │  ├─ 📁 LIST_DATA                             │   │  │
│  │  │  │  ├─ 📄 list_1.csv                         │   │  │
│  │  │  │  └─ 📄 list_2.xlsx                        │   │  │
│  │  │  ├─ 📄 MSA_Data.csv (2.5MB)                  │   │  │
│  │  │  └─ 📄 Store_Master.xlsx (1.2MB)             │   │  │
│  │  │                                              │   │  │
│  │  └──────────────────────────────────────────────┘   │  │
│  │                                                      │  │
│  │  ┌──────────────────────────────────────────────┐   │  │
│  │  │ TAB 3: MSA Pipeline ⚙️                        │   │  │
│  │  │                                              │   │  │
│  │  │  MSA CSV:        [Select File] [Browse]      │   │  │
│  │  │  Store Master:   [Select File] [Browse]      │   │  │
│  │  │  BASE DATA:      [Select Folder] [Browse]    │   │  │
│  │  │  LIST DATA:      [Select Folder] [Browse]    │   │  │
│  │  │  MRST File:      [Select File] [Browse]      │   │  │
│  │  │  Output Folder:  [output] [Browse]           │   │  │
│  │  │                                              │   │  │
│  │  │  ┌─────────────────────────────────┐         │   │  │
│  │  │  │ ▶️ RUN MSA PIPELINE            │         │   │  │
│  │  │  └─────────────────────────────────┘         │   │  │
│  │  │                                              │   │  │
│  │  │  Progress: [████████░░░░░░░░░░] 45%         │   │  │
│  │  │  Status: Processing data...                  │   │  │
│  │  │                                              │   │  │
│  │  └──────────────────────────────────────────────┘   │  │
│  │                                                      │  │
│  │  ┌────────────────────────────────────────────────┐ │  │
│  │  │ Status: Ready | Files: 45 | Ready to process │ │  │
│  │  └────────────────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 FILE INTERACTION FLOW

```
                        USER START HERE
                             ↓
                    ┌────────────────┐
                    │ run_app.bat    │ (Windows)
                    │ or run_app.sh  │ (Mac/Linux)
                    └────────┬───────┘
                             ↓
                    ┌────────────────────┐
                    │  Checks:           │
                    │ ✓ Python installed │
                    │ ✓ Dependencies OK  │
                    └────────┬───────────┘
                             ↓
                    ┌────────────────┐
                    │ Runs:          │
                    │ python         │
                    │ desktop_app.py │
                    └────────┬───────┘
                             ↓
        ┌────────────────────────────────────────┐
        │    desktop_app.py                      │
        │    Imports:                            │
        │    - PyQt5 (for GUI)                   │
        │    - pandas (for data)                 │
        │    - msa_stock_analysis (pipeline)     │
        └────────────┬──────────────────────────┘
                     ↓
    ┌────────────────────────────────────────────┐
    │  MSADesktopApp CLASS CREATED               │
    ├────────────────────────────────────────────┤
    │                                            │
    │  Creates 3 Tabs:                          │
    │                                            │
    │  TAB 1: File Browser                       │
    │  ├─ FileListWorker (background thread)     │
    │  ├─ Scans folders                         │
    │  ├─ Loads files                           │
    │  └─ Updates table                         │
    │                                            │
    │  TAB 2: Folder Structure                   │
    │  ├─ Builds tree view                      │
    │  ├─ Shows hierarchy                       │
    │  └─ Displays file sizes                   │
    │                                            │
    │  TAB 3: MSA Pipeline                       │
    │  ├─ MSAWorker (background thread)          │
    │  ├─ Runs msa_stock_analysis.py             │
    │  ├─ Shows progress                        │
    │  └─ Displays results                      │
    │                                            │
    └────────────┬──────────────────────────────┘
                 ↓
    When user clicks "Run Pipeline":
                 ↓
    ┌────────────────────────────────┐
    │  msa_stock_analysis.py         │
    │  (28KB Data Processing Engine) │
    ├────────────────────────────────┤
    │                                │
    │  MSAStockAnalysis CLASS:       │
    │                                │
    │  Step 1:  Load Input Data      │
    │  Step 2:  Filter Data          │
    │  Step 3:  Expand Across Stores │
    │  Step 4:  Load External Data   │
    │  Step 5:  Prepare Merge Keys   │
    │  Step 6:  Merge BASE DATA      │
    │  Step 7:  Merge LIST DATA      │
    │  Step 8:  Merge MRST Data      │
    │  Step 9:  Clean After Merge    │
    │  Step 10: Consolidate Columns  │
    │  Step 11: Handle Missing Values│
    │  Step 12: Remove Duplicates    │
    │  Step 13: Generate Output      │
    │  Step 14: Generate Summary     │
    │                                │
    └────────────┬──────────────────┘
                 ↓
    ┌──────────────────────────────┐
    │  Uses Dependencies:          │
    │  - pandas (data processing)  │
    │  - openpyxl (Excel files)    │
    │  - numpy (calculations)      │
    └────────────┬─────────────────┘
                 ↓
    ┌──────────────────────────────┐
    │  Reads Input Files:          │
    │  - MSA_Data.csv              │
    │  - Store_Master.xlsx         │
    │  - BASE_DATA/*.csv/*.xlsx    │
    │  - LIST_DATA/*.csv/*.xlsx    │
    │  - MRST_Data.xlsx            │
    └────────────┬─────────────────┘
                 ↓
    ┌──────────────────────────────┐
    │  Processes & Merges Data     │
    │  (14 steps as shown)         │
    └────────────┬─────────────────┘
                 ↓
    ┌──────────────────────────────┐
    │  Writes Output Files to:     │
    │  output/                     │
    │  ├─ MSA_Output.csv           │
    │  ├─ MSA_Output.xlsx          │
    │  └─ SUMMARY.txt              │
    └──────────────────────────────┘
```

---

## 📦 DEPENDENCIES DIAGRAM

```
article_wise_project/
│
├─ Requires (from requirements.txt):
│
├─ PyQt5 == 5.15.9
│   └─ Creates the desktop GUI window
│       - Buttons, tables, tabs
│       - File dialogs
│       - Progress bars
│       - Message boxes
│
├─ pandas == 1.5.3
│   └─ Data manipulation & analysis
│       - Read CSV files
│       - Read Excel files
│       - Merge DataFrames
│       - Filter rows
│       - Handle missing values
│
├─ openpyxl == 3.10.9
│   └─ Excel file operations
│       - Read .xlsx files
│       - Access multiple sheets
│       - Write Excel files
│
├─ numpy == 1.24.3
│   └─ Numerical operations
│       - Array operations
│       - Mathematical calculations
│       - Used by pandas
│
└─ PyQt5-sip == 12.13.0
    └─ Required by PyQt5
        (Internal dependency)
```

---

## 📄 FILE PURPOSES AT A GLANCE

```
┌─────────────────────────────────────────────────────────┐
│ FILE                  SIZE    TYPE    WHAT IT DOES       │
├─────────────────────────────────────────────────────────┤
│ desktop_app.py        23KB    Python  Main GUI app       │
│ msa_stock_analysis.py 28KB    Python  Data processor    │
│ requirements.txt      78B     Text    Dependencies      │
│ README.md             8.5KB   Text    Full documentation│
│ QUICKSTART.md         2.9KB   Text    Quick guide       │
│ FOLDER_STR...         6KB     Text    This explanation  │
│ run_app.bat           1.5KB   Script  Windows launcher  │
│ run_app.sh            1.5KB   Script  Mac/Linux launcher│
│ output/ (folder)      varies  Folder  Pipeline results  │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 STEP-BY-STEP: WHAT HAPPENS

### Phase 1: Starting the App

```
1. User double-clicks run_app.bat (or runs run_app.sh)
                    ↓
2. Launcher checks if Python is installed
                    ↓
3. Launcher checks if dependencies are installed
                    ↓
4. Launcher runs: python desktop_app.py
                    ↓
5. desktop_app.py imports PyQt5, pandas, msa_stock_analysis
                    ↓
6. Creates MSADesktopApp instance
                    ↓
7. Window appears on screen with 3 tabs
                    ↓
8. User sees:
   ✓ File Browser tab with "Browse" button
   ✓ Folder Structure tab (empty until browsed)
   ✓ MSA Pipeline tab with file selectors
```

### Phase 2: User Browses Folder

```
1. User clicks "Browse" in File Browser tab
                    ↓
2. File dialog opens (showing computer folders)
                    ↓
3. User selects a folder (e.g., C:\Data)
                    ↓
4. FileListWorker thread starts (background)
                    ↓
5. Scans folder for all files:
   - Gets file names
   - Gets file types
   - Gets file sizes
   - Gets modification dates
   - Gets full paths
                    ↓
6. Thread finishes, sends signal to main thread
                    ↓
7. Main thread updates UI:
   - Populates file table
   - Updates file count
   - Builds folder tree
                    ↓
8. User sees all files in table
   - Can filter by type
   - Can select files
   - Can see details
```

### Phase 3: User Runs Pipeline

```
1. User configures pipeline (Tab 3):
   - Selects MSA_Data.csv
   - Selects Store_Master.xlsx
   - Selects BASE_DATA folder
   - Selects LIST_DATA folder
   - Selects MRST_Data.xlsx
   - Verifies output folder
                    ↓
2. User clicks "Run MSA Pipeline"
                    ↓
3. MSAWorker thread starts (background)
                    ↓
4. Creates MSAStockAnalysis instance
                    ↓
5. Runs all 14 steps in sequence:
   - Step 1: Loads CSV and Excel files
   - Step 2: Filters rows by criteria
   - Step 3: Expands data across stores
   - Step 4: Loads additional data sources
   - Step 5-8: Merges multiple datasets
   - Step 9-12: Cleans and consolidates
   - Step 13: Exports results
   - Step 14: Generates summary
                    ↓
6. Progress bar shows % completion
                    ↓
7. When done, shows success message
                    ↓
8. User can check output/ folder:
   ✓ MSA_Analysis_Output.csv
   ✓ MSA_Analysis_Output.xlsx
   ✓ SUMMARY.txt
```

---

## 🔑 KEY FILES EXPLAINED IN ONE SENTENCE

| File | Purpose |
|------|---------|
| `desktop_app.py` | The window you see and click on |
| `msa_stock_analysis.py` | The engine that processes your data |
| `run_app.bat` | The button to start the app (Windows) |
| `run_app.sh` | The button to start the app (Mac/Linux) |
| `requirements.txt` | The list of tools needed |
| `README.md` | The detailed instruction manual |
| `QUICKSTART.md` | The cheat sheet |
| `output/` | Where your results go |

---

## ✅ BEFORE YOU START

```
HAVE YOU GOT:
☐ Python 3.8+ installed
☐ All 7 files in same folder
☐ Your input data files ready
☐ Read QUICKSTART.md
☐ Read README.md

THEN:
☐ Run run_app.bat (Windows) or run_app.sh (Mac/Linux)
☐ Click Browse and select your folder
☐ Configure MSA Pipeline
☐ Click Run Pipeline
☐ Check output/ folder for results

DONE! 🎉
```

---

## 🎓 LEARNING PATH

```
1. READ FIRST
   ↓
   QUICKSTART.md (5 minutes)
   └─ Quick overview
   
2. UNDERSTAND STRUCTURE
   ↓
   FOLDER_STRUCTURE_EXPLAINED.md (10 minutes)
   └─ What each file does
   
3. USE THE APP
   ↓
   Run run_app.bat or run_app.sh
   └─ Follow on-screen prompts
   
4. DETAILED HELP
   ↓
   README.md (full documentation)
   └─ In-depth explanations
   
5. CODE DETAILS
   ↓
   desktop_app.py & msa_stock_analysis.py
   └─ For developers
```

---

This explains the entire folder structure! 🎉
