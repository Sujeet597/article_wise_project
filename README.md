# MSA Stock Analysis - Desktop Application

A professional PyQt5-based desktop application for managing and processing stock analysis files with an integrated MSA (Multi-Store Article) data pipeline.

## 🎯 Features

### 📂 File Browser Tab
- **Folder Browsing**: Select any folder and instantly view all files
- **File Filtering**: Filter by file type (.csv, .xlsx, .xls, .json, .txt)
- **Detailed View**: See file names, types, sizes, and modification dates
- **Quick Access**: Double-click files to view full paths
- **File Count**: Real-time count of files matching your filter

### 🌳 Folder Structure Tab
- **Tree View**: Visual hierarchy of your folder structure
- **File Sizes**: Display file sizes alongside names
- **Expandable Folders**: Navigate through nested directories
- **Quick Overview**: Understand your folder organization at a glance

### ⚙️ MSA Pipeline Tab
- **One-Click Pipeline**: Run complete data processing workflow
- **File Configuration**: Select all required input files
- **Output Management**: Choose output folder location
- **Progress Tracking**: Visual feedback during processing
- **Error Handling**: Clear error messages and debugging info

---

## 🚀 Installation

### Step 1: Clone the Repository
```bash
git clone https://github.com/Sujeet597/article_wise_project.git
cd article_wise_project
```

### Step 2: Install Python (if not already installed)
- Download from [python.org](https://www.python.org/downloads/)
- Make sure Python 3.8+ is installed
- Verify: `python --version`

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

If you encounter issues with PyQt5:
```bash
pip install --upgrade pip
pip install PyQt5 --force-reinstall
```

---

## 🎮 How to Use

### Starting the Application

**Option 1: Run Python Script**
```bash
python desktop_app.py
```

**Option 2: Create a Shortcut (Windows)**
```batch
@echo off
python desktop_app.py
pause
```

**Option 3: Use Run Script (included)**
```bash
./run_app.sh    # On Mac/Linux
./run_app.bat   # On Windows
```

---

## 📖 Detailed Usage Guide

### 1. File Browser Tab 📂

#### Browse Folders
1. Click **🔍 Browse** button
2. Select a folder from your computer
3. All files in that folder will automatically load

#### View File Details
- **File Name**: The name of each file
- **Type**: File extension (.csv, .xlsx, etc.)
- **Size**: File size in human-readable format
- **Modified**: Last modification date and time
- **Path**: Full file path

#### Filter Files
1. Use dropdown menu: **Filter by Type**
2. Select file type (All Files, .csv, .xlsx, etc.)
3. Table updates automatically

#### Refresh Files
- Click **🔄 Refresh** to reload files from the folder
- Useful if files were added/deleted while app is open

### 2. Folder Structure Tab 🌳

#### View Organization
- Visual tree representation of your folder structure
- Expand folders by clicking the arrow (▶)
- See file sizes at a glance
- Understand your directory hierarchy

### 3. MSA Pipeline Tab ⚙️

#### Configure Input Files

**Required Files:**

1. **MSA CSV File**
   - Your main MSA data file
   - Format: CSV with columns like STK_QTY, MAJ_CAT, GEN_ART_NUMBER, etc.
   - Click Browse to select

2. **Store Master File**
   - Excel file with store list
   - Format: .xlsx or .xls
   - Contains store codes and details

3. **BASE DATA Folder**
   - Folder containing BASE category files
   - Auto-detects: GM, KIDS, LADIES, MENS categories
   - Can contain multiple CSV/Excel files

4. **LIST DATA Folder**
   - Folder with listing information
   - Supports multiple files
   - Auto-detects headers

5. **MRST File**
   - Excel file with 3 sheets:
     - Sheet 1: Store + Category mapping
     - Sheet 2: Category-level data
     - Sheet 3: Article-level data

6. **Output Folder**
   - Where results will be saved
   - Default: "output"
   - Creates folder if it doesn't exist

#### Run Pipeline
1. Configure all input files (click Browse buttons)
2. Verify output folder
3. Click **▶️ Run MSA Pipeline**
4. Watch progress bar
5. See status updates
6. Receive success/error message

#### Output Files
After pipeline completes:
- `MSA_Analysis_Output.csv` — Main result file
- `MSA_Analysis_Output.xlsx` — Excel version
- `SUMMARY.txt` — Processing summary
- `MSA_Analysis_Output_Part_1.csv` (if >100K rows) — Split files

---

## 📊 Data Processing Pipeline (14 Steps)

The MSA Pipeline executes these steps automatically:

1. ✅ Load MSA CSV and Store Master
2. ✅ Remove empty columns and rows
3. ✅ Filter by stock quantity (STK_QTY ≥ 50)
4. ✅ Expand data across all stores
5. ✅ Load external data sources
6. ✅ Prepare merge keys (standardize formatting)
7. ✅ Merge BASE DATA
8. ✅ Merge LIST DATA
9. ✅ Merge MRST data (all 3 sheets)
10. ✅ Clean duplicate columns
11. ✅ Consolidate category columns
12. ✅ Handle missing values
13. ✅ Remove duplicate CLR rows
14. ✅ Generate output and summary

---

## 🔧 Troubleshooting

### Issue: "No module named 'PyQt5'"
**Solution:**
```bash
pip install PyQt5 --force-reinstall
```

### Issue: "Permission denied" on Mac/Linux
**Solution:**
```bash
chmod +x desktop_app.py
python desktop_app.py
```

### Issue: Files not showing in folder browser
**Solution:**
- Check folder path is valid
- Ensure you have read permissions
- Click **🔄 Refresh** button
- Check filters aren't hiding files

### Issue: Pipeline fails with "File not found"
**Solution:**
- Verify all file paths exist
- Check file paths don't have special characters
- Ensure files are not opened in other programs
- Check output folder permissions

### Issue: "Insufficient memory"
**Solution:**
- Close other applications
- Process fewer files at once
- Increase system RAM if possible

---

## 📁 Folder Structure

```
article_wise_project/
├── desktop_app.py              # Main PyQt5 application
├── msa_stock_analysis.py       # Data processing pipeline
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── run_app.sh                  # Run script (Mac/Linux)
├── run_app.bat                 # Run script (Windows)
└── output/                     # Results folder (created on first run)
    ├── MSA_Analysis_Output.csv
    ├── MSA_Analysis_Output.xlsx
    └── SUMMARY.txt
```

---

## 🎓 Example Workflow

### Step-by-Step Example

1. **Open Application**
   ```bash
   python desktop_app.py
   ```

2. **Browse Files** (File Browser Tab)
   - Click 🔍 Browse
   - Select your data folder
   - See all files listed

3. **Configure Pipeline** (MSA Pipeline Tab)
   - Browse → Select `MSA_Data.csv`
   - Browse → Select `Store_Master.xlsx`
   - Browse → Select `BASE_DATA` folder
   - Browse → Select `LIST_DATA` folder
   - Browse → Select `MRST_Data.xlsx`
   - Keep Output as "output" or change if needed

4. **Run Pipeline**
   - Click ▶️ Run MSA Pipeline
   - Wait for completion
   - Check success message

5. **Review Results**
   - Check `output/` folder
   - Open `MSA_Analysis_Output.csv` in Excel
   - Review `SUMMARY.txt` for statistics

---

## 💡 Tips & Best Practices

### File Organization
- Keep input files in dedicated folders
- Use consistent naming conventions
- Organize by category (BASE_DATA, LIST_DATA, etc.)

### Data Quality
- Verify CSV files are properly formatted
- Ensure Excel files have correct sheet names
- Check for required columns before running

### Performance
- Close unnecessary applications
- Don't run other heavy processes
- Use SSD for faster file operations

### Backup
- Always backup original files
- Keep versions of important runs
- Store outputs in version-controlled folder

---

## 🐛 Reporting Issues

If you encounter bugs or have suggestions:

1. Check this README for solutions
2. Verify file paths and permissions
3. Check Python and library versions
4. Report on GitHub with:
   - Error message
   - File names (anonymized)
   - Steps to reproduce

---

## 📝 Changelog

### Version 1.0.0
- Initial release
- File browser with filtering
- Folder tree visualization
- MSA pipeline integration
- Error handling and logging

---

## 📄 License

This project is proprietary. See LICENSE file for details.

---

## 👥 Support

For help:
- Email: support@example.com
- GitHub Issues: https://github.com/Sujeet597/article_wise_project/issues
- Documentation: See README.md

---

## 🙏 Acknowledgments

- PyQt5 Documentation: https://doc.qt.io/qtforpython/
- Pandas: https://pandas.pydata.org/
- OpenPyXL: https://openpyxl.readthedocs.io/

---

**Happy analyzing! 📊**
