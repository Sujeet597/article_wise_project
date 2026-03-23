"""
Smart Folder Structure Detector
================================

Automatically finds and validates MSA pipeline input files
from a given root folder path.

Supports flexible folder naming and detects:
- BASE DATA folder (with CSVs)
- LIST DATA folder (with CSVs)
- MRST folder (with Excel file)
- MSA/msa folder (with CSV)
- Store/STORE folder (with Excel)
"""

import os
from pathlib import Path
from typing import Dict, Optional, Tuple
import pandas as pd


class FolderStructureDetector:
    """Automatically detect and validate folder structure"""
    
    def __init__(self, root_path: str):
        """Initialize detector with root folder path"""
        self.root_path = Path(root_path)
        self.detected_files = {}
        self.errors = []
        
        if not self.root_path.exists():
            raise ValueError(f"Path does not exist: {root_path}")
        
        if not self.root_path.is_dir():
            raise ValueError(f"Path is not a directory: {root_path}")
    
    def detect_all(self) -> Dict[str, str]:
        """
        Detect all required files in the folder structure.
        
        Returns:
            dict: {
                'msa_csv': path to MSA CSV,
                'store_master': path to Store Master Excel,
                'base_data_folder': path to BASE DATA folder,
                'list_data_folder': path to LIST DATA folder,
                'mrst': path to MRST Excel or folder
            }
        """
        self.detected_files = {}
        self.errors = []
        
        # Detect each component
        self._detect_msa_csv()
        self._detect_store_master()
        self._detect_base_data_folder()
        self._detect_list_data_folder()
        self._detect_mrst()
        
        # Validate that we found required files
        required = ['msa_csv', 'store_master', 'base_data_folder', 'list_data_folder', 'mrst']
        missing = [k for k in required if k not in self.detected_files or not self.detected_files[k]]
        
        if missing:
            self.errors.append(f"Missing required: {', '.join(missing)}")
        
        return self.detected_files
    
    def _detect_msa_csv(self):
        """Find MSA CSV file (usually in msa/ or msa_data/ folder or root)"""
        patterns = [
            'msa/*[Gg]enerated*.csv',
            'msa/*[Cc]olor*.csv',
            'msa/*[Dd]ata*.csv',
            'msa_data/*[Gg]enerated*.csv',
            '*[Gg]enerated*[Cc]olor*.csv',
            '*[Mm]sa*.csv',
        ]
        
        for pattern in patterns:
            files = sorted(self.root_path.glob(pattern))
            if files:
                self.detected_files['msa_csv'] = str(files[0])
                return
        
        # Try direct search in root
        for file in self.root_path.glob('*.csv'):
            if 'generated' in file.name.lower() or 'color' in file.name.lower():
                self.detected_files['msa_csv'] = str(file)
                return
        
        self.errors.append("MSA CSV not found")
    
    def _detect_store_master(self):
        """Find Store Master Excel file"""
        patterns = [
            'store/*[Ss]tore*.xlsx',
            'store/*[Ss]tore*.xls',
            'store_master/*[Ss]tore*.xlsx',
            '*[Ss]tore*[Nn]ame*.xlsx',
            '*[Ss]tore*[Nn]ame*.xls',
        ]
        
        for pattern in patterns:
            files = sorted(self.root_path.glob(pattern))
            if files:
                self.detected_files['store_master'] = str(files[0])
                return
        
        # Try direct search in root
        for file in self.root_path.glob('*.xlsx'):
            if 'store' in file.name.lower():
                self.detected_files['store_master'] = str(file)
                return
        
        for file in self.root_path.glob('*.xls'):
            if 'store' in file.name.lower():
                self.detected_files['store_master'] = str(file)
                return
        
        self.errors.append("Store Master Excel not found")
    
    def _detect_base_data_folder(self):
        """Find BASE DATA folder"""
        patterns = [
            '[Bb]ase*[Dd]ata',
            '[Bb]ase*[Dd]ata*',
            '*[Bb]ase*[Dd]ata*',
        ]
        
        for pattern in patterns:
            matches = sorted(self.root_path.glob(pattern))
            for match in matches:
                if match.is_dir():
                    # Check if it contains CSV files
                    csv_files = list(match.glob('*.csv'))
                    if csv_files:
                        self.detected_files['base_data_folder'] = str(match)
                        return
        
        self.errors.append("BASE DATA folder not found")
    
    def _detect_list_data_folder(self):
        """Find LIST DATA folder"""
        patterns = [
            '[Ll]ist*[Dd]ata',
            '[Ll]ist*[Dd]ata*',
            '*[Ll]ist*[Dd]ata*',
        ]
        
        for pattern in patterns:
            matches = sorted(self.root_path.glob(pattern))
            for match in matches:
                if match.is_dir():
                    # Check if it contains CSV files
                    csv_files = list(match.glob('*.csv'))
                    if csv_files:
                        self.detected_files['list_data_folder'] = str(match)
                        return
        
        self.errors.append("LIST DATA folder not found")
    
    def _detect_mrst(self):
        """Find MRST Excel file or folder"""
        # Try to find MRST folder first
        patterns = [
            '[Mm]rst*',
            '*[Mm]rst*',
        ]
        
        for pattern in patterns:
            matches = sorted(self.root_path.glob(pattern))
            for match in matches:
                if match.is_dir():
                    # Check if folder contains Excel files
                    excel_files = list(match.glob('*.xlsx')) + list(match.glob('*.xls'))
                    if excel_files:
                        self.detected_files['mrst'] = str(match)
                        return
        
        # Try to find MRST Excel file directly
        for file in self.root_path.glob('*[Mm]rst*.xlsx'):
            self.detected_files['mrst'] = str(file)
            return
        
        for file in self.root_path.glob('*[Mm]rst*.xls'):
            self.detected_files['mrst'] = str(file)
            return
        
        self.errors.append("MRST file/folder not found")
    
    def validate(self) -> Tuple[bool, list]:
        """
        Validate detected files exist and are accessible.
        
        Returns:
            (is_valid, error_messages)
        """
        errors = []
        
        for key, path in self.detected_files.items():
            if not path:
                errors.append(f"{key}: Not found")
                continue
            
            path_obj = Path(path)
            
            if not path_obj.exists():
                errors.append(f"{key}: Path does not exist: {path}")
                continue
            
            # Check file readability
            try:
                if path_obj.is_file():
                    # Try to open and read a few bytes
                    with open(path_obj, 'rb') as f:
                        f.read(100)
                elif path_obj.is_dir():
                    # Check if directory is readable
                    list(path_obj.iterdir())
            except Exception as e:
                errors.append(f"{key}: Not readable: {str(e)[:50]}")
        
        return len(errors) == 0, errors
    
    def get_summary(self) -> Dict:
        """Get summary of detected structure"""
        summary = {
            'root_path': str(self.root_path),
            'detected_files': self.detected_files,
            'errors': self.errors,
            'is_valid': len(self.errors) == 0
        }
        
        # Add file sizes
        for key, path in self.detected_files.items():
            if path and Path(path).exists():
                path_obj = Path(path)
                if path_obj.is_file():
                    size_mb = path_obj.stat().st_size / (1024 * 1024)
                    summary[f'{key}_size_mb'] = f"{size_mb:.2f}"
                elif path_obj.is_dir():
                    total_size = sum(f.stat().st_size for f in path_obj.rglob('*') if f.is_file())
                    size_mb = total_size / (1024 * 1024)
                    file_count = len(list(path_obj.glob('*.*')))
                    summary[f'{key}_size_mb'] = f"{size_mb:.2f}"
                    summary[f'{key}_files'] = file_count
        
        return summary


def detect_folder_structure(root_path: str) -> Tuple[bool, Dict, list]:
    """
    Convenience function to detect folder structure.
    
    Args:
        root_path: Path to root folder (e.g., "DW01")
    
    Returns:
        (success, detected_files_dict, error_messages)
    """
    try:
        detector = FolderStructureDetector(root_path)
        files = detector.detect_all()
        is_valid, errors = detector.validate()
        
        return is_valid, files, errors
    except Exception as e:
        return False, {}, [str(e)]


# ==================== USAGE EXAMPLES ====================

if __name__ == "__main__":
    import json
    
    # Example usage
    root_path = "DW01"  # Change to your actual path
    
    print(f"\n🔍 Detecting folder structure: {root_path}")
    print("=" * 60)
    
    success, files, errors = detect_folder_structure(root_path)
    
    if errors:
        print("\n❌ Errors:")
        for error in errors:
            print(f"  • {error}")
    
    if files:
        print("\n✅ Detected Files:")
        for key, path in files.items():
            if path:
                print(f"  {key}:")
                print(f"    → {path}")
    
    if success:
        print("\n✅ All required files found and valid!")
        
        # Show summary
        detector = FolderStructureDetector(root_path)
        detector.detect_all()
        summary = detector.get_summary()
        
        print("\n📊 Summary:")
        print(json.dumps({k: v for k, v in summary.items() if k not in ['root_path', 'detected_files', 'errors']}, indent=2))
    else:
        print("\n⚠️  Some files missing or invalid")
