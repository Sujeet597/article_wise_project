"""
MSA Stock Analysis – Enhanced Data Processing Pipeline
======================================================

Implements advanced consolidation logic:
- Multi-encoding CSV support (UTF-8, Latin-1, CP1252, ISO-8859-1, UTF-16)
- Intelligent VLOOKUP merging with category support
- LIST data header detection (row 1 or row 6)
- 3-sheet MRST Excel handling with column name flexibility
- Column consolidation (ST-STK_BASE_GM + ST-STK_BASE_KIDS -> ST-STK)
- Duplicate CLR removal (keeps only first if all data is zero)
- Identifier column protection (not filled with 0)
- Advanced cleanup (_x, _y suffix removal)

Flow: Load → Filter → Expand → Merge → Consolidate → Clean → Output
"""

import pandas as pd
import numpy as np
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import warnings

warnings.filterwarnings('ignore')


class MSAStockAnalysis:
    def __init__(self, msa_csv_path: str, store_master_path: str, 
                 base_data_folder: str, list_data_folder: str, mrst_path: str,
                 output_folder: str = "output"):
        """
        Initialize MSA Stock Analysis pipeline
        
        Args:
            msa_csv_path: Path to MSA CSV file
            store_master_path: Path to Store Master Excel file
            base_data_folder: Path to BASE DATA folder (CSV/Excel files)
            list_data_folder: Path to LIST DATA folder (CSV/Excel files)
            mrst_path: Path to MRST folder or Excel file (3 sheets)
            output_folder: Where to save outputs
        """
        self.msa_csv_path = msa_csv_path
        self.store_master_path = store_master_path
        self.base_data_folder = base_data_folder
        self.list_data_folder = list_data_folder
        self.mrst_path = mrst_path
        self.output_folder = output_folder
        
        Path(self.output_folder).mkdir(parents=True, exist_ok=True)
        
        # Data containers
        self.msa_data = None
        self.store_master = None
        self.base_data = {}
        self.list_data = {}
        self.mrst_data = {}
        self.filtered_data = None
        self.expanded_data = None
        self.final_data = None
        
        print("✅ MSA Stock Analysis Pipeline Initialized (Enhanced)")
    
    # ================== HELPER: Multi-Encoding CSV Reader ==================
    
    def _read_csv_with_encoding(self, filepath: str, skiprows: int = 0, 
                               encodings: List[str] = None) -> pd.DataFrame:
        """Try reading CSV with multiple encodings and skiprows"""
        if encodings is None:
            encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1252', 'iso-8859-1', 'windows-1252']
        
        # Try with skiprows first (for LIST data with header at row 6)
        if skiprows > 0:
            for encoding in encodings:
                try:
                    return pd.read_csv(filepath, encoding=encoding, skiprows=skiprows, low_memory=False)
                except:
                    continue
        
        # Try without skiprows
        for encoding in encodings:
            try:
                return pd.read_csv(filepath, encoding=encoding, low_memory=False)
            except:
                continue
        
        # Last resort: Latin-1 with error handling
        try:
            return pd.read_csv(filepath, encoding='latin-1', on_bad_lines='skip', low_memory=False)
        except Exception as e:
            raise Exception(f"Could not read {filepath} with any encoding. Last error: {e}")
    
    # ================== STEP 1: Load Input Data ==================
    
    def step1_load_input_data(self):
        """Load MSA CSV and Store Master Excel, remove empty columns/rows"""
        print("\n📥 STEP 1: Loading Input Data...")
        
        try:
            # Load MSA data with encoding support
            self.msa_data = self._read_csv_with_encoding(self.msa_csv_path)
            
            # Remove Unnamed columns (empty from CSV)
            unnamed_cols = [c for c in self.msa_data.columns if 'Unnamed' in c]
            if unnamed_cols:
                self.msa_data = self.msa_data.drop(columns=unnamed_cols)
            
            # Remove completely empty columns
            empty_cols = [c for c in self.msa_data.columns if self.msa_data[c].isna().all()]
            if empty_cols:
                self.msa_data = self.msa_data.drop(columns=empty_cols)
            
            # Remove fully empty rows
            self.msa_data = self.msa_data.dropna(axis=0, how='all')
            
            print(f"   ✓ MSA data loaded: {len(self.msa_data):,} rows, {len(self.msa_data.columns)} columns")
            
            # Load Store Master
            self.store_master = pd.read_excel(self.store_master_path)
            self.store_master = self.store_master.dropna(how='all')
            
            # Remove Unnamed columns
            unnamed_cols = [c for c in self.store_master.columns if 'Unnamed' in c]
            if unnamed_cols:
                self.store_master = self.store_master.drop(columns=unnamed_cols)
            
            print(f"   ✓ Store Master loaded: {len(self.store_master):,} stores")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Error loading data: {e}")
            return False
    
    # ================== STEP 2: Filter Data ==================
    
    def step2_filter_data(self, stk_qty_threshold: int = 50):
        """Filter rows where STK_QTY >= threshold"""
        print(f"\n🔍 STEP 2: Filtering Data (STK_QTY >= {stk_qty_threshold})...")
        
        if 'STK_QTY' not in self.msa_data.columns:
            print(f"   ⚠️  Column 'STK_QTY' not found. Proceeding without filtering...")
            self.filtered_data = self.msa_data.copy()
            return True
        
        initial_rows = len(self.msa_data)
        self.filtered_data = self.msa_data[self.msa_data['STK_QTY'] >= stk_qty_threshold].copy()
        
        print(f"   ✓ Filtered: {initial_rows:,} → {len(self.filtered_data):,} rows")
        
        return True
    
    # ================== STEP 3: Expand Across Stores ==================
    
    def step3_expand_across_stores(self):
        """Expand filtered data by creating one row per store"""
        print(f"\n📈 STEP 3: Expanding Data Across Stores...")
        
        try:
            num_stores = len(self.store_master)
            num_articles = len(self.filtered_data)
            total_rows = num_articles * num_stores
            
            print(f"   Expanding: {num_articles:,} articles × {num_stores} stores = {total_rows:,} rows")
            
            expanded_list = []
            
            # Repeat filtered dataframe for each store
            for store_idx, (_, store_row) in enumerate(self.store_master.iterrows()):
                temp_df = self.filtered_data.copy()
                
                # Add store columns with STORE_ prefix
                for col in self.store_master.columns:
                    temp_df[f'STORE_{col}'] = store_row[col]
                
                expanded_list.append(temp_df)
            
            # Concatenate all at once (faster)
            self.expanded_data = pd.concat(expanded_list, ignore_index=True)
            
            print(f"   ✓ Expanded successfully: {len(self.expanded_data):,} rows")
            return True
            
        except Exception as e:
            print(f"   ❌ Error expanding data: {e}")
            return False
    
    # ================== STEP 4: Load External Data ==================
    
    def step4_load_external_data(self):
        """Load BASE DATA, LIST DATA, and MRST data"""
        print("\n📂 STEP 4: Loading External Data Sources...")
        
        self._load_base_data()
        self._load_list_data()
        self._load_mrst_data()
        
        return True
    
    def _remove_duplicate_columns(self, df, sample_size=100):
        """Remove truly duplicate columns (same values)"""
        cols_to_drop = []
        seen_hashes = {}
        
        for col in df.columns:
            # Create hash of column values (sample-based for efficiency)
            try:
                col_sample = df[col].astype(str).head(sample_size).tolist()
                col_hash = tuple(col_sample)
                
                if col_hash in seen_hashes:
                    cols_to_drop.append(col)
                else:
                    seen_hashes[col_hash] = col
            except:
                pass
        
        return cols_to_drop
    
    def _get_category_from_filename(self, filename: str) -> Optional[str]:
        """Extract category from filename (GM, KIDS, LADIES, MENS)"""
        filename_upper = filename.upper()
        for cat in ['GM', 'KIDS', 'LADIES', 'MENS']:
            if cat in filename_upper:
                return cat
        return None
    
    def _load_base_data(self):
        """Load BASE DATA files with multi-encoding support"""
        print("   Loading BASE DATA...")
        
        if not os.path.exists(self.base_data_folder):
            print(f"      ⚠️  Folder not found: {self.base_data_folder}")
            return
        
        encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1252', 'iso-8859-1', 'windows-1252']
        all_files = os.listdir(self.base_data_folder)
        csv_files = [f for f in all_files if f.endswith('.csv')]
        excel_files = [f for f in all_files if f.endswith(('.xlsx', '.xls', '.xlsb'))]
        
        print(f"      Found {len(csv_files)} CSV + {len(excel_files)} Excel files")
        
        for file in sorted(csv_files + excel_files):
            file_path = os.path.join(self.base_data_folder, file)
            category = self._get_category_from_filename(file)
            
            print(f"      {file}...", end=" ", flush=True)
            
            try:
                if file.endswith('.csv'):
                    df = self._read_csv_with_encoding(file_path)
                else:
                    df = pd.read_excel(file_path, sheet_name=0)
                
                df = df.dropna(how='all')
                print(f"✓ ({len(df):,} rows)")
                
                if category:
                    self.base_data[category] = df
            except Exception as e:
                print(f"✗ {str(e)[:40]}")
        
        print(f"   ✓ Loaded {len(self.base_data)} BASE DATA files")
    
    def _load_list_data(self):
        """Load LIST DATA files with multi-encoding and header detection"""
        print("   Loading LIST DATA...")
        
        if not os.path.exists(self.list_data_folder):
            print(f"      ⚠️  Folder not found: {self.list_data_folder}")
            return
        
        encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1252', 'iso-8859-1', 'windows-1252']
        all_files = os.listdir(self.list_data_folder)
        csv_files = [f for f in all_files if f.endswith('.csv')]
        excel_files = [f for f in all_files if f.endswith(('.xlsx', '.xls', '.xlsb'))]
        
        print(f"      Found {len(csv_files)} CSV + {len(excel_files)} Excel files")
        
        for file in sorted(csv_files + excel_files):
            file_path = os.path.join(self.list_data_folder, file)
            category = self._get_category_from_filename(file)
            
            print(f"      {file}...", end=" ", flush=True)
            
            try:
                df = None
                encoding_used = None
                
                if file.endswith('.csv'):
                    # Try with header at row 6 (skiprows=5) first
                    for encoding in encodings:
                        try:
                            df = pd.read_csv(file_path, encoding=encoding, skiprows=5, low_memory=False)
                            encoding_used = f"{encoding} (row 6)"
                            break
                        except:
                            continue
                    
                    # If that fails, try default header
                    if df is None:
                        df = self._read_csv_with_encoding(file_path, skiprows=0)
                        encoding_used = "utf-8 (row 1)"
                else:
                    # Try Excel with skiprows=5 first
                    try:
                        df = pd.read_excel(file_path, sheet_name=0, skiprows=5)
                        encoding_used = "Excel (row 6)"
                    except:
                        df = pd.read_excel(file_path, sheet_name=0)
                        encoding_used = "Excel (row 1)"
                
                df = df.dropna(how='all')
                print(f"✓ ({len(df):,} rows, {encoding_used})")
                
                if category:
                    self.list_data[category] = df
            except Exception as e:
                print(f"✗ {str(e)[:40]}")
        
        print(f"   ✓ Loaded {len(self.list_data)} LIST DATA files")
    
    def _load_mrst_data(self):
        """Load MRST Excel file with 3 sheets"""
        print("   Loading MRST DATA...")
        
        mrst_path = self.mrst_path
        
        # Find Excel file
        if os.path.isdir(mrst_path):
            excel_files = [f for f in os.listdir(mrst_path) if f.endswith(('.xlsx', '.xls', '.xlsb'))]
            if not excel_files:
                print(f"      ⚠️  No Excel files in {mrst_path}")
                return
            mrst_path = os.path.join(mrst_path, excel_files[0])
        
        if not os.path.exists(mrst_path):
            print(f"      ⚠️  MRST file not found: {mrst_path}")
            return
        
        print(f"      Excel file: {os.path.basename(mrst_path)}")
        
        # Sheet configs: (sheet_name, key_name, description)
        sheet_configs = [
            ('03-ST-MAJ-CAT', 'st_maj_cat', 'Sheet 1: Store + Major Category'),
            ('04-CO-MAJ-CAT', 'co_maj_cat', 'Sheet 2: Commodity Category'),
            ('05-CO-ART', 'co_art', 'Sheet 3: Article Data'),
        ]
        
        for sheet_idx, (sheet_name, key_name, description) in enumerate(sheet_configs):
            try:
                print(f"      {description}...", end=" ", flush=True)
                
                # Try by name first, then by index
                try:
                    df = pd.read_excel(mrst_path, sheet_name=sheet_name)
                except:
                    df = pd.read_excel(mrst_path, sheet_name=sheet_idx)
                
                df = df.dropna(how='all')
                print(f"✓ ({len(df):,} rows)")
                self.mrst_data[key_name] = df
            except Exception as e:
                print(f"✗ {str(e)[:40]}")
        
        print(f"   ✓ Loaded {len(self.mrst_data)} MRST sheets")
    
    # ================== STEP 5: Merge Data ==================
    
    def step5_merge_data(self):
        """Merge BASE DATA, LIST DATA, and MRST data using VLOOKUP logic - OPTIMIZED"""
        print(f"\n🔗 STEP 5: Merging Data (Memory Optimized)...")
        
        # Work directly on expanded_data (no deep copy initially)
        result_df = self.expanded_data
        print(f"   Starting with: {len(result_df):,} rows, {len(result_df.columns)} columns")
        
        # Standardize key columns to string
        result_df['MAJ_CAT'] = result_df['MAJ_CAT'].astype(str).str.strip()
        result_df['GEN_ART_NUMBER'] = result_df['GEN_ART_NUMBER'].astype(str).str.strip()
        result_df['STORE_ST_CD'] = result_df['STORE_ST_CD'].astype(str).str.strip()
        
        # Find CLR column
        clr_col = None
        for col in result_df.columns:
            if col.upper() == 'CLR' or col.upper() == 'COLOR':
                clr_col = col
                result_df[clr_col] = result_df[clr_col].astype(str).str.strip()
                break
        
        merge_count = 0
        categories = ['GM', 'KIDS', 'LADIES', 'MENS']
        
        for category in categories:
            has_base = category in self.base_data
            has_list = category in self.list_data
            
            if not (has_base or has_list):
                continue
            
            print(f"\n   Processing {category}...")
            
            # Merge BASE DATA
            if has_base:
                try:
                    base_df = self.base_data[category].copy()
                    
                    if all(c in base_df.columns for c in ['MAJCAT', 'GEN_ART', 'Store_Code']):
                        print(f"      BASE DATA {category}: {len(base_df):,} rows", end="")
                        
                        # Standardize keys
                        base_df['MAJCAT'] = base_df['MAJCAT'].astype(str).str.strip()
                        base_df['GEN_ART'] = base_df['GEN_ART'].astype(str).str.strip()
                        base_df['Store_Code'] = base_df['Store_Code'].astype(str).str.strip()
                        
                        # Prepare merge columns
                        merge_cols = ['MAJCAT', 'GEN_ART', 'Store_Code']
                        
                        # Check for CLR in base_df
                        base_clr_col = None
                        for col in base_df.columns:
                            if col.upper() == 'CLR' or col.upper() == 'COLOR':
                                base_clr_col = col
                                base_df[col] = base_df[col].astype(str).str.strip()
                                break
                        
                        if clr_col and base_clr_col:
                            merge_cols.append(base_clr_col)
                        
                        # Select and rename ST-STK column
                        keep_cols = merge_cols.copy()
                        if 'ST-STK' in base_df.columns:
                            keep_cols.append('ST-STK')
                        
                        base_df_filtered = base_df[keep_cols].drop_duplicates(subset=merge_cols).copy()
                        
                        # Rename ST-STK to include category
                        if 'ST-STK' in base_df_filtered.columns:
                            base_df_filtered.rename(columns={'ST-STK': f'ST-STK_BASE_{category}'}, inplace=True)
                        
                        # Merge
                        merge_left_on = ['MAJ_CAT', 'GEN_ART_NUMBER', 'STORE_ST_CD']
                        merge_right_on = ['MAJCAT', 'GEN_ART', 'Store_Code']
                        
                        if clr_col and base_clr_col:
                            merge_left_on.append(clr_col)
                            merge_right_on.append(base_clr_col)
                        
                        result_df = result_df.merge(
                            base_df_filtered,
                            left_on=merge_left_on,
                            right_on=merge_right_on,
                            how='left'
                        )
                        
                        # Drop duplicate key columns
                        cols_to_drop = [c for c in merge_right_on if c in result_df.columns]
                        if cols_to_drop:
                            result_df = result_df.drop(columns=cols_to_drop)
                        
                        print(f" ✓ {len(result_df):,} rows")
                        merge_count += 1
                except Exception as e:
                    print(f" ✗ {str(e)[:40]}")
            
            # Merge LIST DATA
            if has_list:
                try:
                    list_df = self.list_data[category].copy()
                    
                    if all(c in list_df.columns for c in ['MAJCAT', 'GEN_ART', 'ST_CD']):
                        print(f"      LIST DATA {category}: {len(list_df):,} rows", end="")
                        
                        # Standardize keys
                        list_df['MAJCAT'] = list_df['MAJCAT'].astype(str).str.strip()
                        list_df['GEN_ART'] = list_df['GEN_ART'].astype(str).str.strip()
                        list_df['ST_CD'] = list_df['ST_CD'].astype(str).str.strip()
                        
                        # Prepare merge columns
                        merge_cols = ['MAJCAT', 'GEN_ART', 'ST_CD']
                        
                        # Check for CLR in list_df
                        list_clr_col = None
                        for col in list_df.columns:
                            if col.upper() == 'CLR' or col.upper() == 'COLOR':
                                list_clr_col = col
                                list_df[col] = list_df[col].astype(str).str.strip()
                                break
                        
                        if clr_col and list_clr_col:
                            merge_cols.append(list_clr_col)
                        
                        # Select LIST columns
                        keep_cols = merge_cols.copy()
                        list_cols = [c for c in list_df.columns if any(x in c for x in ['TAG', 'MBQ', 'LISTING'])]
                        keep_cols.extend(list_cols)
                        
                        list_df_filtered = list_df[keep_cols].drop_duplicates(subset=merge_cols).copy()
                        
                        # Rename to include category
                        rename_dict = {c: f"{c}_LIST_{category}" for c in list_cols}
                        list_df_filtered.rename(columns=rename_dict, inplace=True)
                        
                        # Merge
                        merge_left_on = ['MAJ_CAT', 'GEN_ART_NUMBER', 'STORE_ST_CD']
                        merge_right_on = ['MAJCAT', 'GEN_ART', 'ST_CD']
                        
                        if clr_col and list_clr_col:
                            merge_left_on.append(clr_col)
                            merge_right_on.append(list_clr_col)
                        
                        result_df = result_df.merge(
                            list_df_filtered,
                            left_on=merge_left_on,
                            right_on=merge_right_on,
                            how='left'
                        )
                        
                        # Drop duplicate key columns
                        cols_to_drop = [c for c in merge_right_on if c in result_df.columns]
                        if cols_to_drop:
                            result_df = result_df.drop(columns=cols_to_drop)
                        
                        print(f" ✓ {len(result_df):,} rows")
                        merge_count += 1
                except Exception as e:
                    print(f" ✗ {str(e)[:40]}")
        
        # Merge MRST sheets if available
        if self.mrst_data:
            print(f"\n   Processing MRST sheets...")
            
            # Sheet 1: ST_CD + MAJ_CAT
            if 'st_maj_cat' in self.mrst_data:
                try:
                    mrst1 = self.mrst_data['st_maj_cat'].copy()
                    
                    # Find ST_CD column (handle \n in names)
                    st_cd_col = next((c for c in mrst1.columns if 'ST' in c.upper() and 'CD' in c.upper()), None)
                    
                    if st_cd_col:
                        print(f"      MRST Sheet 1 (ST+MAJ_CAT): {len(mrst1):,} rows", end=" ")
                        
                        # Standardize key
                        mrst1[st_cd_col] = mrst1[st_cd_col].astype(str).str.strip()
                        
                        # Create composite key for merging
                        result_df['_ST_MAJ_CAT'] = result_df['STORE_ST_CD'] + result_df['MAJ_CAT']
                        mrst1['_ST_MAJ_CAT'] = mrst1[st_cd_col] + mrst1['MAJ_CAT'] if 'MAJ_CAT' in mrst1.columns else mrst1[st_cd_col]
                        
                        # Merge on composite key
                        result_df = result_df.merge(
                            mrst1.drop(columns=[st_cd_col]),
                            left_on=['_ST_MAJ_CAT'],
                            right_on=['_ST_MAJ_CAT'],
                            how='left'
                        )
                        
                        result_df = result_df.drop(columns=['_ST_MAJ_CAT'])
                        
                        print(f"✓ {len(result_df):,} rows")
                        merge_count += 1
                except Exception as e:
                    print(f"✗ {str(e)[:40]}")
            
            # Sheet 2: MAJ_CAT only
            if 'co_maj_cat' in self.mrst_data:
                try:
                    mrst2 = self.mrst_data['co_maj_cat'].copy()
                    
                    maj_cat_col = next((c for c in mrst2.columns if 'MAJ' in c.upper() and 'CAT' in c.upper()), None)
                    
                    if maj_cat_col:
                        print(f"      MRST Sheet 2 (MAJ_CAT): {len(mrst2):,} rows", end=" ")
                        
                        mrst2[maj_cat_col] = mrst2[maj_cat_col].astype(str).str.strip()
                        
                        mrst2_filtered = mrst2[[maj_cat_col]].drop_duplicates()
                        
                        result_df = result_df.merge(
                            mrst2.drop(columns=[maj_cat_col]),
                            left_on='MAJ_CAT',
                            right_on=maj_cat_col,
                            how='left'
                        )
                        
                        print(f"✓ {len(result_df):,} rows")
                        merge_count += 1
                except Exception as e:
                    print(f"✗ {str(e)[:40]}")
            
            # Sheet 3: MAJ_CAT + GEN_ART + CLR
            if 'co_art' in self.mrst_data:
                try:
                    mrst3 = self.mrst_data['co_art'].copy()
                    
                    maj_cat_col = next((c for c in mrst3.columns if 'MAJ' in c.upper() and 'CAT' in c.upper()), None)
                    gen_art_col = next((c for c in mrst3.columns if 'GEN' in c.upper() and 'ART' in c.upper()), None)
                    
                    if maj_cat_col and gen_art_col:
                        print(f"      MRST Sheet 3 (MAJ_CAT+GEN_ART+CLR): {len(mrst3):,} rows", end=" ")
                        
                        # Standardize keys
                        mrst3[maj_cat_col] = mrst3[maj_cat_col].astype(str).str.strip()
                        mrst3[gen_art_col] = mrst3[gen_art_col].astype(str).str.strip()
                        
                        # Prepare merge
                        merge_cols = [maj_cat_col, gen_art_col]
                        mrst3_clr_col = next((c for c in mrst3.columns if c.upper() == 'CLR'), None)
                        
                        if mrst3_clr_col:
                            mrst3[mrst3_clr_col] = mrst3[mrst3_clr_col].astype(str).str.strip()
                            merge_cols.append(mrst3_clr_col)
                        
                        mrst3_filtered = mrst3[merge_cols].drop_duplicates()
                        
                        # Merge
                        if mrst3_clr_col:
                            result_df = result_df.merge(
                                mrst3.drop(columns=merge_cols),
                                left_on=['MAJ_CAT', 'GEN_ART_NUMBER', clr_col],
                                right_on=[maj_cat_col, gen_art_col, mrst3_clr_col],
                                how='left'
                            )
                        else:
                            result_df = result_df.merge(
                                mrst3.drop(columns=merge_cols),
                                left_on=['MAJ_CAT', 'GEN_ART_NUMBER'],
                                right_on=[maj_cat_col, gen_art_col],
                                how='left'
                            )
                        
                        print(f"✓ {len(result_df):,} rows")
                        merge_count += 1
                except Exception as e:
                    print(f"✗ {str(e)[:40]}")
        
        # Cleanup: Remove _x, _y suffixes
        cols_to_rename = {}
        for col in result_df.columns:
            if col.endswith('_x') or col.endswith('_y'):
                new_name = col[:-2]
                if new_name not in result_df.columns:
                    cols_to_rename[col] = new_name
        
        if cols_to_rename:
            result_df.rename(columns=cols_to_rename, inplace=True)
        
        # AGGRESSIVE: Remove duplicate key columns from merges
        print(f"   Removing duplicate key columns...", end=" ")
        merge_key_cols = ['MAJCAT', 'GEN_ART', 'Store_Code', 'MAJCAT_1', 'GEN_ART_1', 'ST_CD', 'COMB_1']
        cols_to_drop = [c for c in merge_key_cols if c in result_df.columns]
        
        if cols_to_drop:
            result_df.drop(columns=cols_to_drop, inplace=True)
            print(f"Dropped {len(cols_to_drop)}")
        else:
            print(f"None found")
        
        self.expanded_data = result_df
        print(f"\n   ✓ Merged {merge_count} data sources")
        print(f"   ✓ Final: {len(result_df):,} rows × {len(result_df.columns)} columns")
        
        return True
    
    # ================== STEP 6: Consolidate & Clean ==================
    
    def step6_consolidate_data(self):
        """Consolidate category-specific columns and clean duplicates - MEMORY OPTIMIZED"""
        print(f"\n🧹 STEP 6: Consolidating & Cleaning Data (Memory Optimized)...")
        
        print(f"   Current shape: {self.expanded_data.shape[0]:,} rows × {self.expanded_data.shape[1]:,} columns")
        
        # CRITICAL: Remove duplicate/redundant columns FIRST
        # This reduces memory footprint before any consolidation
        print(f"   Removing redundant columns...")
        
        cols_to_drop = []
        
        # Drop columns that are entirely NaN
        for col in self.expanded_data.columns:
            if self.expanded_data[col].isna().all():
                cols_to_drop.append(col)
        
        if cols_to_drop:
            self.expanded_data.drop(columns=cols_to_drop, inplace=True)
            print(f"   ✓ Removed {len(cols_to_drop)} all-NaN columns")
        
        # Work directly on expanded_data (no copy!)
        result_df = self.expanded_data
        
        # Consolidate category-specific columns
        consolidate_cols = [
            ('ST-STK_BASE', 'ST-STK'),
            ('TAG ART-STATUS (L/X)_LIST', 'TAG ART-STATUS (L/X)'),
            ('ST MBQ + HOLD-MBQ (L-ART)_LIST', 'ST MBQ + HOLD-MBQ (L-ART)'),
            ('LISTING CAP_LIST', 'LISTING CAP')
        ]
        
        for col_base, consolidated_name in consolidate_cols:
            matching_cols = [c for c in result_df.columns if col_base in c]
            
            if len(matching_cols) > 1:
                print(f"   Consolidating {consolidated_name}...", end=" ")
                try:
                    # Combine category columns using fillna - NO copy
                    consolidated = result_df[matching_cols[0]].fillna(0)
                    for col in matching_cols[1:]:
                        consolidated = consolidated.fillna(result_df[col])
                    
                    result_df[consolidated_name] = consolidated
                    result_df.drop(columns=matching_cols, inplace=True)
                    print(f"✓")
                except Exception as e:
                    print(f"✗ ({str(e)[:30]})")
            elif len(matching_cols) == 1:
                result_df.rename(columns={matching_cols[0]: consolidated_name}, inplace=True)
        
        # Remove duplicate ST_CD columns (in-place)
        st_cd_cols = [c for c in result_df.columns if c == 'ST_CD']
        if len(st_cd_cols) > 1:
            result_df.drop(columns=st_cd_cols[1:], inplace=True)
            print(f"   ✓ Kept 1 ST_CD, removed {len(st_cd_cols)-1} duplicates")
        
        # Fill missing values (in-place, selective)
        print(f"   Filling missing values...")
        identifier_cols = ['MAJ_CAT', 'GEN_ART_NUMBER', 'ST_CD', 'STORE_ST_CD', 'STORE_ST_NM', 'CLR', 'DATE']
        existing_id_cols = [c for c in identifier_cols if c in result_df.columns]
        
        # ONLY fill numeric columns (avoid string operations)
        numeric_cols = result_df.select_dtypes(include=['float64', 'int64']).columns
        for col in numeric_cols:
            if col not in existing_id_cols:
                result_df[col].fillna(0, inplace=True)
        
        print(f"   ✓ Filled {len(numeric_cols)} numeric columns")
        
        # Remove duplicate CLR rows with all zero data (OPTIMIZED)
        print(f"   Checking for zero-data CLR rows...", end=" ")
        if 'CLR' in result_df.columns:
            numeric_cols_list = result_df.select_dtypes(include=['number']).columns.tolist()
            data_cols = [c for c in numeric_cols_list if c not in existing_id_cols]
            
            if data_cols and len(data_cols) > 0:
                # Use sum to find zero-sum rows
                try:
                    row_sums = result_df[data_cols].sum(axis=1)
                    
                    rows_to_keep = []
                    for clr in result_df['CLR'].unique():
                        clr_mask = result_df['CLR'] == clr
                        clr_indices = result_df[clr_mask].index
                        clr_sums = row_sums[clr_indices]
                        
                        has_data = clr_sums > 0
                        if has_data.any():
                            rows_to_keep.extend(clr_indices[has_data].tolist())
                        else:
                            rows_to_keep.append(clr_indices[0])
                    
                    result_df = result_df.loc[rows_to_keep].reset_index(drop=True)
                    print(f"✓ ({len(rows_to_keep):,} rows kept)")
                except Exception as e:
                    print(f"⚠ (error: {str(e)[:20]})")
            else:
                print(f"⚠ (no data columns)")
        else:
            print(f"⚠ (CLR column not found)")
        
        self.final_data = result_df
        print(f"   ✓ Final shape: {self.final_data.shape[0]:,} rows × {self.final_data.shape[1]:,} columns")
        
        return True
    
    # ================== STEP 7: Generate Output ==================
    
    def step7_generate_output(self, row_limit: int = 1000000):
        """Save output to CSV/Excel"""
        print(f"\n💾 STEP 7: Generating Output...")
        
        if self.final_data is None or self.final_data.empty:
            print("   ❌ No data to output")
            return False
        
        total_rows = len(self.final_data)
        
        try:
            if total_rows <= row_limit:
                # Single CSV
                csv_path = os.path.join(self.output_folder, 'MSA_Output.csv')
                self.final_data.to_csv(csv_path, index=False)
                print(f"   ✓ CSV saved: MSA_Output.csv ({total_rows:,} rows)")
                
                # Try Excel
                try:
                    excel_path = os.path.join(self.output_folder, 'MSA_Output.xlsx')
                    self.final_data.to_excel(excel_path, index=False, sheet_name='Data')
                    print(f"   ✓ Excel saved: MSA_Output.xlsx")
                except:
                    print(f"   ⚠️  Excel save skipped (file too large)")
            else:
                # Split into multiple CSVs
                chunk_size = row_limit
                for i in range(0, total_rows, chunk_size):
                    chunk = self.final_data.iloc[i:i+chunk_size]
                    part_num = (i // chunk_size) + 1
                    csv_path = os.path.join(self.output_folder, f'MSA_Output_Part_{part_num}.csv')
                    chunk.to_csv(csv_path, index=False)
                    print(f"   ✓ Part {part_num}: {len(chunk):,} rows saved")
            
            return True
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    # ================== STEP 8: Generate Summary ==================
    
    def step8_generate_summary(self):
        """Create summary report"""
        print(f"\n📊 STEP 8: Generating Summary...")
        
        numeric_cols = self.final_data.select_dtypes(include=['number']).columns.tolist()
        text_cols = self.final_data.select_dtypes(include=['object']).columns.tolist()
        
        summary_path = os.path.join(self.output_folder, 'SUMMARY.txt')
        
        try:
            with open(summary_path, 'w') as f:
                f.write("="*70 + "\n")
                f.write("MSA STOCK ANALYSIS - SUMMARY\n")
                f.write("="*70 + "\n\n")
                
                f.write("DATA OVERVIEW\n")
                f.write("-"*70 + "\n")
                f.write(f"Total Rows: {len(self.final_data):,}\n")
                f.write(f"Total Columns: {len(self.final_data.columns)}\n")
                f.write(f"Numeric Columns: {len(numeric_cols)}\n")
                f.write(f"Text Columns: {len(text_cols)}\n\n")
                
                f.write("COLUMN LIST\n")
                f.write("-"*70 + "\n")
                for i, col in enumerate(self.final_data.columns, 1):
                    dtype = self.final_data[col].dtype
                    nulls = self.final_data[col].isna().sum()
                    f.write(f"{i}. {col} ({dtype}) - {nulls} nulls\n")
            
            print(f"   ✓ Summary saved: SUMMARY.txt")
            return True
        except Exception as e:
            print(f"   ⚠️  Summary error: {e}")
            return False
    
    # ================== MAIN PIPELINE ==================
    
    def run_pipeline(self):
        """Execute all steps in sequence"""
        print("\n" + "="*70)
        print("🚀 MSA STOCK ANALYSIS PIPELINE (ENHANCED)")
        print("="*70)
        
        steps = [
            ("Load Input Data", self.step1_load_input_data),
            ("Filter Data", self.step2_filter_data),
            ("Expand Across Stores", self.step3_expand_across_stores),
            ("Load External Data", self.step4_load_external_data),
            ("Merge Data", self.step5_merge_data),
            ("Consolidate & Clean", self.step6_consolidate_data),
            ("Generate Output", self.step7_generate_output),
            ("Generate Summary", self.step8_generate_summary),
        ]
        
        for step_name, step_func in steps:
            try:
                if not step_func():
                    print(f"\n❌ Pipeline stopped at: {step_name}")
                    return False
            except Exception as e:
                print(f"\n❌ Error in {step_name}: {e}")
                import traceback
                traceback.print_exc()
                return False
        
        print("\n" + "="*70)
        print("✅ PIPELINE COMPLETED SUCCESSFULLY!")
        print("="*70 + "\n")
        return True


# ==================== USAGE ====================

if __name__ == "__main__":
    pipeline = MSAStockAnalysis(
        msa_csv_path="MSA_STORENAME/Generated_Colors_2026-03-16.csv",
        store_master_path="MSA_STORENAME/STORE NAME-dw01.xlsx",
        base_data_folder="DW01/BASE DATA",
        list_data_folder="DW01/LIST DATA",
        mrst_path="DW01/MRST",
        output_folder="output"
    )
    
    success = pipeline.run_pipeline()
    
    if success:
        print("🎉 All done! Check the 'output' folder for results.")
    else:
        print("⚠️  Pipeline had issues. Check messages above.")
