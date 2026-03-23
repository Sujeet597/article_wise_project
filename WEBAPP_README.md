# 🚀 MSA Stock Analysis - FastAPI Web Application

Modern, fast web application for file browsing and data processing pipeline.

## ✨ Features

### 📂 File Browser
- Browse any folder on your system
- View detailed file information (name, type, size, modification date)
- Filter files by type (CSV, Excel, JSON, Text, etc.)
- Real-time file count and total size statistics
- Copy file paths to clipboard

### 🌳 Folder Structure Visualization
- Visual tree representation of folder hierarchy
- Shows file sizes in tree view
- Expandable folder navigation
- Understand folder organization at a glance

### ⚙️ MSA Pipeline Execution
- Configure all input files through web interface
- Real-time progress tracking
- Cancel pipeline execution anytime
- View pipeline status and current step
- Background processing (non-blocking UI)

### 📊 Output Management
- View all generated output files
- Download results directly from browser
- File size and modification date
- Clear output files with confirmation
- Real-time file list updates

---

## 🔧 Installation

### Step 1: Install Python (if not already installed)
```bash
python --version  # Requires Python 3.8+
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

This installs:
- **FastAPI** - Modern async web framework
- **Uvicorn** - ASGI web server
- **pandas** - Data processing
- **openpyxl** - Excel file handling
- **aiofiles** - Async file operations

### Step 3: Verify Installation
```bash
pip list | grep -E "fastapi|uvicorn|pandas"
```

---

## 🚀 Running the Application

### Start the Web Server
```bash
python main.py
```

You should see:
```
============================================================
🚀 MSA Stock Analysis - FastAPI Web Server
============================================================

📡 Starting server...
🌐 Open: http://localhost:8000
📚 API Docs: http://localhost:8000/docs
============================================================
```

### Access the Application
1. **Web Interface**: http://localhost:8000
2. **API Documentation**: http://localhost:8000/docs (Interactive Swagger UI)
3. **ReDoc**: http://localhost:8000/redoc (Alternative API docs)

---

## 💻 Web Interface Guide

### 📂 Tab 1: File Browser

**How to use:**
1. Enter a folder path (e.g., `/Users/username/Documents` or `C:\Data`)
2. Click **Browse** to scan the folder
3. Files will be listed in the table
4. Use **Filter by Type** to show only specific file types
5. Click **Copy Path** to copy full file path to clipboard

**Features:**
- Shows file name, type, size, and modification date
- Real-time file count and total size
- Supports all file types
- Fast scanning with progress feedback

### 🌳 Tab 2: Folder Structure

**How to use:**
1. Enter a folder path
2. Click **Load Tree**
3. Tree structure will display hierarchically
4. Expands up to 3 levels deep by default

**Features:**
- Visual folder hierarchy
- Shows file sizes
- Nested display for easy navigation
- Limited to 100 items per folder (performance)

### ⚙️ Tab 3: MSA Pipeline

**How to use:**
1. **Configure all 5 input sources:**
   - MSA CSV File (main data file)
   - Store Master File (store list)
   - BASE DATA Folder (category files)
   - LIST DATA Folder (listing files)
   - MRST File (3-sheet Excel file)

2. **Optional:** Modify output folder (default: "output")

3. **Click** ▶️ Run MSA Pipeline

4. **Monitor** progress:
   - Progress bar shows completion %
   - Current step is displayed
   - Status badge shows "Running"
   - Can cancel anytime with ⏹️ button

**13-Step Process:**
- Load input data
- Filter data
- Expand across stores
- Load external sources
- Prepare merge keys
- Merge BASE DATA
- Merge LIST DATA
- Merge MRST data
- Clean after merge
- Consolidate columns
- Handle missing values
- Remove duplicates
- Generate output

### 📊 Tab 4: Output Files

**How to use:**
1. After pipeline completes, click **Output Files** tab
2. Click **Refresh** to update file list
3. View all generated output files
4. Click **Download** to save files to your computer

**Files Generated:**
- `MSA_Analysis_Output.csv` - Main results
- `MSA_Analysis_Output.xlsx` - Excel format
- `SUMMARY.txt` - Processing summary
- `MSA_Analysis_Output_Part_1.csv` (if >100K rows)

---

## 🔌 API Endpoints

### Health Check
```
GET /api/health
```
Returns server status.

### File Browsing
```
POST /api/browse
{
    "folder_path": "/path/to/folder"
}
```
Returns: List of files with details

### Folder Tree
```
POST /api/tree
{
    "folder_path": "/path/to/folder"
}
```
Returns: Hierarchical folder structure

### Pipeline Execution
```
POST /api/pipeline/run
{
    "msa_csv_path": "path/to/file.csv",
    "store_master_path": "path/to/file.xlsx",
    "base_data_folder": "path/to/folder",
    "list_data_folder": "path/to/folder",
    "mrst_path": "path/to/file.xlsx",
    "output_folder": "output"
}
```
Returns: Pipeline started message

### Pipeline Status
```
GET /api/pipeline/status
```
Returns:
- running (bool)
- progress (0-100)
- current_step (string)
- error (if any)

### Output Files
```
GET /api/output/files
```
Returns: List of generated output files

### Download File
```
GET /api/output/download/{filename}
```
Downloads the file

---

## 📁 Project Structure

```
article_wise_project/
├── main.py                     # FastAPI backend server
├── index.html                  # Web interface
├── msa_stock_analysis.py       # Data processing engine
├── requirements.txt            # Python dependencies
├── uploads/                    # Uploaded files
├── output/                     # Generated results
└── temp/                       # Temporary files
```

---

## 🎯 Common Tasks

### Task 1: Process Files from Specific Folder

1. Go to **File Browser** tab
2. Enter folder path: `/Users/username/MSA_Data`
3. Click **Browse**
4. See all files with sizes
5. Go to **Pipeline** tab
6. Select the files you need
7. Click **Run MSA Pipeline**

### Task 2: Monitor Large Pipeline Run

1. Start pipeline in **Pipeline** tab
2. Watch real-time progress bar
3. Check current step being processed
4. View overall completion percentage
5. Results saved automatically to `output/` folder

### Task 3: Download Results

1. Go to **Output Files** tab
2. See all generated files
3. Click **Download** next to each file
4. Files save to your downloads folder

### Task 4: Clear Old Results

1. Go to **Output Files** tab
2. Click **Clear All** button
3. Confirm deletion in popup
4. All output files deleted
5. Folder ready for new results

---

## ⚙️ Configuration

### Server Settings
Edit `main.py` to change:
- Port (default: 8000)
- Host (default: 0.0.0.0)
- Reload behavior
- Log level

```python
# In main.py:
uvicorn.run(
    "main:app",
    host="0.0.0.0",      # Change here
    port=8000,            # Change here
    reload=True,          # Set False for production
    log_level="info"      # Change log level
)
```

### Performance Settings
```python
# In main.py:
# Limit folder tree depth
build_tree(folder_path, max_depth=3)

# Limit items per folder
children=children[:100]
```

---

## 🐛 Troubleshooting

### Issue: "Connection refused" when opening http://localhost:8000

**Solution:**
1. Make sure server is running: `python main.py`
2. Check console for errors
3. Verify port 8000 is not in use
4. Try different port: Edit main.py and change port

### Issue: Folder path not found

**Solution:**
1. Use absolute paths (not relative)
2. Use forward slashes (/) even on Windows
3. Don't use spaces without quotes
4. Examples:
   - Good: `/Users/john/Documents` or `C:/Users/john/Data`
   - Bad: `~/Documents` or `C:\Users\john\Data`

### Issue: Pipeline fails to start

**Solution:**
1. Verify all files exist before running
2. Check file permissions (readable)
3. Ensure paths are absolute
4. Check console output for specific errors
5. Try with smaller dataset first

### Issue: Progress bar stuck

**Solution:**
1. Click **Cancel** button
2. Check server console for errors
3. Restart server: Kill process and rerun `python main.py`
4. Check available disk space

---

## 📊 Performance Characteristics

| Operation | Time | Notes |
|-----------|------|-------|
| Browse folder (1K files) | <1s | Fast listing |
| Build tree (deep folders) | 1-2s | Recursive traversal |
| Small pipeline run (10K rows) | 10-30s | Quick processing |
| Large pipeline run (1M+ rows) | 2-10 min | Depends on data |
| Download file | <1s | Network speed dependent |

---

## 🔐 Security Notes

### Development Only
This configuration is suitable for **local development only**.

For **production deployment**, consider:
1. Add authentication (API key, OAuth2)
2. Restrict file paths (whitelist)
3. Set proper CORS origins
4. Use HTTPS
5. Add rate limiting
6. Run behind reverse proxy (Nginx)
7. Set DEBUG=False

### File Access
- Current: All files on system accessible
- Recommended for production: Whitelist allowed folders

---

## 📝 Log Files

Logs are printed to console. To save to file:
```bash
python main.py > msa_server.log 2>&1
```

View logs:
```bash
tail -f msa_server.log
```

---

## 🚀 Deployment Options

### Option 1: Local Machine (Development)
```bash
python main.py
```
Access: http://localhost:8000

### Option 2: Network Access
```bash
python main.py  # Replace 0.0.0.0 with your IP
```
Access: http://your-ip:8000

### Option 3: Production (Gunicorn)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 main:app
```

### Option 4: Docker
Create `Dockerfile`:
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

Build and run:
```bash
docker build -t msa-web .
docker run -p 8000:8000 msa-web
```

---

## 📚 API Documentation

### Interactive Swagger UI
- URL: http://localhost:8000/docs
- Try all endpoints
- See request/response examples
- Auto-generated from code

### ReDoc Alternative
- URL: http://localhost:8000/redoc
- Beautiful API documentation
- Read-only view

---

## 🔄 Workflow Example

```
1. Start server
   → python main.py

2. Open browser
   → http://localhost:8000

3. Browse folders
   → File Browser tab
   → Enter path: /Users/john/MSA_Data
   → Click Browse
   → See 250 files

4. Configure pipeline
   → Pipeline tab
   → Select all 5 input files
   → Set output folder

5. Execute
   → Click Run Pipeline
   → Watch progress (takes 2-10 min)
   → See completion message

6. Download results
   → Output Files tab
   → Download CSV, Excel, Summary
   → Analysis complete!
```

---

## ❓ FAQ

**Q: Can I run on a different port?**
A: Yes, edit main.py and change port 8000 to desired port.

**Q: Can I access from other computers?**
A: Yes, use your computer's IP address instead of localhost.

**Q: Can I process multiple pipelines at once?**
A: No, current implementation runs one at a time. Queue support can be added.

**Q: Are files stored permanently?**
A: No, output files are in "output/" folder. Clear them with "Clear All" button.

**Q: Can I use relative paths?**
A: Use absolute paths for reliability. Relative paths may not work correctly.

---

## 📞 Support

For issues or questions:
1. Check this README
2. Check Troubleshooting section
3. Review console output
4. Check API docs: http://localhost:8000/docs

---

## 🎉 Summary

You now have a modern web application for:
- 📂 Browsing any folder
- 🌳 Visualizing directory structure
- ⚙️ Running MSA data pipeline
- 📊 Managing output files
- 💻 Accessing from browser

**Start:** `python main.py`  
**Access:** http://localhost:8000  
**Done!** 🚀
