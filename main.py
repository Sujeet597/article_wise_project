"""
MSA Stock Analysis - FastAPI Web Application Backend
Modern async web server for file browsing and data processing pipeline
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import os
import json
import asyncio
import shutil
from pathlib import Path
from datetime import datetime
import uvicorn

from msa_stock_analysis import MSAStockAnalysis

# ==================== FASTAPI APP SETUP ====================

app = FastAPI(
    title="MSA Stock Analysis",
    description="Web-based file browser and data processing pipeline",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directories
Path("uploads").mkdir(exist_ok=True)
Path("output").mkdir(exist_ok=True)
Path("temp").mkdir(exist_ok=True)

# ==================== MODELS ====================

class FolderBrowseRequest(BaseModel):
    folder_path: str

class FileInfo(BaseModel):
    name: str
    path: str
    rel_path: str
    size: str
    size_bytes: int
    modified: str
    type: str
    is_directory: bool

class FolderStructure(BaseModel):
    name: str
    path: str
    type: str  # "file" or "folder"
    size: Optional[str]
    children: Optional[List['FolderStructure']] = None

class PipelineConfig(BaseModel):
    msa_csv_path: str
    store_master_path: str
    base_data_folder: str
    list_data_folder: str
    mrst_path: str
    output_folder: str = "output"

class PipelineResponse(BaseModel):
    status: str
    message: str
    progress: int = 0
    error: Optional[str] = None

# ==================== GLOBAL STATE ====================

pipeline_status = {
    "running": False,
    "progress": 0,
    "current_step": "",
    "error": None,
    "output_files": [],
    "summary": None
}

# ==================== HELPER FUNCTIONS ====================

def format_size(size_bytes: int) -> str:
    """Format bytes to human readable size"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"

def scan_folder(folder_path: str) -> List[FileInfo]:
    """Scan folder and return file list"""
    files = []
    try:
        for root, dirs, filenames in os.walk(folder_path):
            for filename in filenames:
                filepath = os.path.join(root, filename)
                rel_path = os.path.relpath(filepath, folder_path)
                
                try:
                    file_size = os.path.getsize(filepath)
                    mod_time = datetime.fromtimestamp(
                        os.path.getmtime(filepath)
                    ).strftime('%Y-%m-%d %H:%M')
                    ext = os.path.splitext(filename)[1].lower()
                    
                    files.append(FileInfo(
                        name=filename,
                        path=filepath,
                        rel_path=rel_path,
                        size=format_size(file_size),
                        size_bytes=file_size,
                        modified=mod_time,
                        type=ext if ext else 'unknown',
                        is_directory=False
                    ))
                except Exception as e:
                    print(f"Error processing {filepath}: {e}")
                    continue
    except Exception as e:
        print(f"Error scanning folder: {e}")
    
    return files

def build_tree(folder_path: str, max_depth: int = 3, current_depth: int = 0) -> FolderStructure:
    """Build folder structure tree"""
    try:
        folder_name = os.path.basename(folder_path) or folder_path
        
        if current_depth >= max_depth:
            return FolderStructure(
                name=folder_name,
                path=folder_path,
                type="folder",
                size=None,
                children=[]
            )
        
        children = []
        
        try:
            items = sorted(os.listdir(folder_path))
            for item in items:
                item_path = os.path.join(folder_path, item)
                
                if os.path.isdir(item_path):
                    try:
                        child = build_tree(item_path, max_depth, current_depth + 1)
                        children.append(child)
                    except Exception as e:
                        print(f"Error processing directory {item_path}: {e}")
                else:
                    try:
                        size = os.path.getsize(item_path)
                        child = FolderStructure(
                            name=item,
                            path=item_path,
                            type="file",
                            size=format_size(size),
                            children=None
                        )
                        children.append(child)
                    except Exception as e:
                        print(f"Error processing file {item_path}: {e}")
        except Exception as e:
            print(f"Error reading directory {folder_path}: {e}")
        
        return FolderStructure(
            name=folder_name,
            path=folder_path,
            type="folder",
            size=None,
            children=children[:100]  # Limit to 100 items per folder
        )
    
    except Exception as e:
        return FolderStructure(
            name="Error",
            path=folder_path,
            type="folder",
            size=None,
            children=[]
        )

class CustomPipelineLogger:
    """Capture pipeline output for real-time display"""
    def __init__(self):
        self.messages = []
        self.steps = []
    
    def log(self, message: str):
        self.messages.append(message)
        if "STEP" in message:
            self.steps.append(message)
    
    def get_progress(self) -> int:
        """Calculate progress based on completed steps"""
        return min(int((len(self.steps) / 14) * 100), 99)

# ==================== ROUTES: FILE BROWSING ====================

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "MSA Stock Analysis API",
        "version": "1.0.0"
    }

@app.post("/api/browse")
async def browse_folder(request: FolderBrowseRequest):
    """Browse folder and return files"""
    try:
        if not os.path.exists(request.folder_path):
            raise HTTPException(status_code=400, detail="Folder path does not exist")
        
        if not os.path.isdir(request.folder_path):
            raise HTTPException(status_code=400, detail="Path is not a folder")
        
        files = scan_folder(request.folder_path)
        
        return {
            "status": "success",
            "folder_path": request.folder_path,
            "file_count": len(files),
            "files": files,
            "total_size": format_size(sum(f.size_bytes for f in files))
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/tree")
async def get_tree_structure(request: FolderBrowseRequest):
    """Get folder tree structure"""
    try:
        if not os.path.exists(request.folder_path):
            raise HTTPException(status_code=400, detail="Folder path does not exist")
        
        tree = build_tree(request.folder_path)
        
        return {
            "status": "success",
            "tree": tree
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/files")
async def list_files(folder_path: str = "", file_type: str = "all"):
    """List files with optional filtering"""
    try:
        if not folder_path:
            folder_path = os.path.expanduser("~")
        
        if not os.path.exists(folder_path):
            raise HTTPException(status_code=400, detail="Folder does not exist")
        
        files = scan_folder(folder_path)
        
        # Filter by type
        if file_type != "all":
            files = [f for f in files if f.type == file_type]
        
        return {
            "status": "success",
            "folder": folder_path,
            "file_count": len(files),
            "files": files
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/download")
async def download_file(file_path: str):
    """Download a file"""
    try:
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        return FileResponse(
            path=file_path,
            filename=os.path.basename(file_path)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ROUTES: PIPELINE EXECUTION ====================

@app.get("/api/pipeline/status")
async def get_pipeline_status():
    """Get current pipeline status"""
    return pipeline_status

@app.post("/api/pipeline/run")
async def run_pipeline(config: PipelineConfig, background_tasks: BackgroundTasks):
    """Run MSA pipeline asynchronously"""
    
    if pipeline_status["running"]:
        raise HTTPException(status_code=400, detail="Pipeline already running")
    
    # Validate files exist
    if not os.path.exists(config.msa_csv_path):
        raise HTTPException(status_code=400, detail="MSA CSV file not found")
    if not os.path.exists(config.store_master_path):
        raise HTTPException(status_code=400, detail="Store Master file not found")
    if not os.path.exists(config.base_data_folder):
        raise HTTPException(status_code=400, detail="BASE DATA folder not found")
    if not os.path.exists(config.list_data_folder):
        raise HTTPException(status_code=400, detail="LIST DATA folder not found")
    if not os.path.exists(config.mrst_path):
        raise HTTPException(status_code=400, detail="MRST file not found")
    
    # Run pipeline in background
    background_tasks.add_task(
        execute_pipeline,
        config.msa_csv_path,
        config.store_master_path,
        config.base_data_folder,
        config.list_data_folder,
        config.mrst_path,
        config.output_folder
    )
    
    return {
        "status": "started",
        "message": "Pipeline execution started in background"
    }

async def execute_pipeline(msa_csv_path: str, store_master_path: str,
                           base_data_folder: str, list_data_folder: str,
                           mrst_path: str, output_folder: str):
    """Execute pipeline and update status"""
    try:
        pipeline_status["running"] = True
        pipeline_status["progress"] = 0
        pipeline_status["error"] = None
        pipeline_status["output_files"] = []
        
        # Create pipeline instance
        pipeline = MSAStockAnalysis(
            msa_csv_path=msa_csv_path,
            store_master_path=store_master_path,
            base_data_folder=base_data_folder,
            list_data_folder=list_data_folder,
            mrst_path=mrst_path,
            output_folder=output_folder
        )
        
        # Run pipeline
        success = pipeline.run_pipeline()
        
        if success:
            # Get output files
            output_files = []
            if os.path.exists(output_folder):
                for file in os.listdir(output_folder):
                    file_path = os.path.join(output_folder, file)
                    if os.path.isfile(file_path):
                        output_files.append({
                            "name": file,
                            "path": file_path,
                            "size": format_size(os.path.getsize(file_path))
                        })
            
            pipeline_status["output_files"] = output_files
            pipeline_status["progress"] = 100
            pipeline_status["current_step"] = "Complete"
        else:
            pipeline_status["error"] = "Pipeline execution failed"
    
    except Exception as e:
        pipeline_status["error"] = str(e)
    
    finally:
        pipeline_status["running"] = False

@app.post("/api/pipeline/cancel")
async def cancel_pipeline():
    """Cancel running pipeline"""
    pipeline_status["running"] = False
    return {"status": "cancelled"}

# ==================== ROUTES: FILE UPLOAD ====================

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a file"""
    try:
        upload_path = f"uploads/{file.filename}"
        
        with open(upload_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return {
            "status": "success",
            "filename": file.filename,
            "path": upload_path,
            "size": os.path.getsize(upload_path)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ROUTES: OUTPUT FILES ====================

@app.get("/api/output/files")
async def get_output_files():
    """Get list of output files"""
    try:
        output_files = []
        
        if os.path.exists("output"):
            for file in os.listdir("output"):
                file_path = os.path.join("output", file)
                if os.path.isfile(file_path):
                    output_files.append({
                        "name": file,
                        "path": file_path,
                        "size": format_size(os.path.getsize(file_path)),
                        "modified": datetime.fromtimestamp(
                            os.path.getmtime(file_path)
                        ).strftime('%Y-%m-%d %H:%M')
                    })
        
        return {
            "status": "success",
            "file_count": len(output_files),
            "files": output_files
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/output/download/{filename}")
async def download_output(filename: str):
    """Download output file"""
    try:
        file_path = os.path.join("output", filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        return FileResponse(
            path=file_path,
            filename=filename
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/output/clear")
async def clear_output():
    """Clear all output files"""
    try:
        if os.path.exists("output"):
            for file in os.listdir("output"):
                file_path = os.path.join("output", file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
        
        return {
            "status": "success",
            "message": "Output folder cleared"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== MAIN ====================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 MSA Stock Analysis - FastAPI Web Server")
    print("="*60)
    print("\n📡 Starting server...")
    print("🌐 Open: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("="*60 + "\n")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
