"""
MSA Stock Analysis – Data Processing Pipeline
Converts plain text logic into executable Python code

Flow: Load → Filter → Expand → Merge → Clean → Output
"""

import pandas as pd
import numpy as np
import os
from pathlib import Path
from typing import Tuple, Dict, List
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
            base_data_folder: Path to BASE DATA folder
            list_data_folder: Path to LIST DATA folder
            mrst_path: Path to MRST Excel file (with multiple sheets)
            output_folder: Where to save outputs
        """
        self.msa_csv_path = msa_csv_path
        self.store_master_path = store_master_path
        self.base_data_folder = base_data_folder
        self.list_data_folder = list_data_folder
        self.mrst_path = mrst_path
        self.output_folder = output_folder
        
        # Create output folder if it doesn't exist
        Path(self.output_folder).mkdir(parents=True, exist_ok=True)
        
        # Data containers
        self.msa_data = None
        self.store_master = None
        self.base_data = None
        self.list_data = None
        self.mrst_data = None
        self.filtered_data = None
        self.expanded_data = None
        self.final_data = None
        
        print("✅ MSA Stock Analysis Pipeline Initialized")
    
    # ================== HELPER: Multi-Encoding File Reader ==================
    
    def _read_csv_with_encoding(self, filepath: str, encodings: List[str] = None):
        """
        Try reading CSV with multiple encodings
        
        Tries encodings in order: utf-8, latin-1, cp1252, iso-8859-15, ascii (with errors='ignore')
        """
        if encodings is None:
            encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252', 'iso-8859-15', 'utf-16']
        
        last_error = None
        
        # Try each encoding
        for encoding in encodings:
            try:
                df = pd.read_csv(filepath, encoding=encoding)
                return df
            except Exception as e:
                last_error = e
                continue
        
        # If all encodings fail, try with errors='ignore' (most permissive)
        try:
            df = pd.read_csv(filepath, encoding='latin-1', on_bad_lines='skip')
            return df
        except Exception as e:
            last_error = e
        
        # Last resort: try utf-8 with errors='ignore'
        try:
            df = pd.read_csv(filepath, encoding='utf-8', on_bad_lines='skip', engine='python')
            return df
        except Exception as e:
            raise Exception(f"Could not read {filepath} with any encoding. Last error: {e}")
    
    # ================== STEP 1: Load Input Data ==================
    
    def step1_load_input_data(self):
        """Load MSA CSV and Store Master Excel, remove empty columns/rows"""
        print("\n📥 STEP 1: Loading Input Data...")
        
        try:
            # Load MSA data (with multi-encoding support)
            self.msa_data = self._read_csv_with_encoding(self.msa_csv_path)
            print(f"   ✓ MSA data loaded: {self.msa_data.shape[0]} rows, {self.msa_data.shape[1]} columns")
            
            # Load Store Master
            self.store_master = pd.read_excel(self.store_master_path)
            print(f"   ✓ Store Master loaded: {self.store_master.shape[0]} stores")
            
            # Remove unnamed columns
            self.msa_data = self.msa_data.loc[:, ~self.msa_data.columns.str.contains('^Unnamed')]
            self.store_master = self.store_master.loc[:, ~self.store_master.columns.str.contains('^Unnamed')]
            
            # Remove fully empty columns
            self.msa_data = self.msa_data.dropna(axis=1, how='all')
            self.store_master = self.store_master.dropna(axis=1, how='all')
            
            # Remove fully empty rows
            self.msa_data = self.msa_data.dropna(axis=0, how='all')
            self.store_master = self.store_master.dropna(axis=0, how='all')
            
            print(f"   ✓ After cleaning: {self.msa_data.shape[0]} rows, {self.msa_data.shape[1]} columns")
            
        except Exception as e:
            print(f"   ❌ Error loading data: {e}")
            return False
        
        return True
    
    # ================== STEP 2: Filter Data ==================
    
    def step2_filter_data(self, stk_qty_threshold: int = 50):
        """Filter rows where STK_QTY >= threshold"""
        print(f"\n🔍 STEP 2: Filtering Data (STK_QTY >= {stk_qty_threshold})...")
        
        if 'STK_QTY' not in self.msa_data.columns:
            print(f"   ⚠️  Column 'STK_QTY' not found. Available columns: {self.msa_data.columns.tolist()}")
            print("   ℹ️  Proceeding without filtering...")
            self.filtered_data = self.msa_data.copy()
            return True
        
        initial_rows = len(self.msa_data)
        self.filtered_data = self.msa_data[self.msa_data['STK_QTY'] >= stk_qty_threshold].copy()
        filtered_rows = len(self.filtered_data)
        
        print(f"   ✓ Filtered: {initial_rows} → {filtered_rows} rows (removed {initial_rows - filtered_rows})")
        
        return True
    
    # ================== STEP 3: Expand Data Across Stores ==================
    
    def step3_expand_across_stores(self):
        """Create a row for each article × store combination"""
        print("\n📈 STEP 3: Expanding Data Across Stores...")
        
        try:
            # Reset index for clean cross-join
            filtered_reset = self.filtered_data.reset_index(drop=True)
            store_reset = self.store_master.reset_index(drop=True)
            
            # Add key column for cross join
            filtered_reset['_key'] = 1
            store_reset['_key'] = 1
            
            # Cross join
            expanded = filtered_reset.merge(store_reset, on='_key', how='outer')
            expanded = expanded.drop('_key', axis=1)
            
            # Prefix store columns
            store_cols = self.store_master.columns.tolist()
            rename_dict = {col: f'STORE_{col}' for col in store_cols}
            expanded = expanded.rename(columns=rename_dict)
            
            self.expanded_data = expanded.reset_index(drop=True)
            
            print(f"   ✓ Expanded: {self.filtered_data.shape[0]} articles × {len(self.store_master)} stores")
            print(f"   ✓ Result: {self.expanded_data.shape[0]} rows")
            
        except Exception as e:
            print(f"   ❌ Error expanding data: {e}")
            return False
        
        return True
    
    # ================== STEP 4: Load External Data Sources ==================
    
    def step4_load_external_data(self):
        """Load BASE DATA, LIST DATA, and MRST data"""
        print("\n📂 STEP 4: Loading External Data Sources...")
        
        # Load BASE DATA
        print("   Loading BASE DATA...")
        base_data_list = []
        if os.path.exists(self.base_data_folder):
            for file in os.listdir(self.base_data_folder):
                if file.endswith(('.csv', '.xlsx')):
                    filepath = os.path.join(self.base_data_folder, file)
                    try:
                        if file.endswith('.csv'):
                            df = self._read_csv_with_encoding(filepath)
                        else:
                            df = pd.read_excel(filepath)
                        
                        # Detect category from filename
                        category = None
                        for cat in ['GM', 'KIDS', 'LADIES', 'MENS']:
                            if cat in file.upper():
                                category = cat
                                break
                        
                        if category:
                            df['CATEGORY'] = category
                        
                        base_data_list.append(df)
                        print(f"      ✓ {file} ({df.shape[0]} rows)")
                    except Exception as e:
                        print(f"      ❌ Error reading {file}: {e}")
            
            if base_data_list:
                self.base_data = pd.concat(base_data_list, ignore_index=True)
                self.base_data = self.base_data.drop_duplicates()
                print(f"   ✓ BASE DATA consolidated: {self.base_data.shape[0]} rows")
        
        # Load LIST DATA
        print("   Loading LIST DATA...")
        list_data_list = []
        if os.path.exists(self.list_data_folder):
            for file in os.listdir(self.list_data_folder):
                if file.endswith(('.csv', '.xlsx')):
                    filepath = os.path.join(self.list_data_folder, file)
                    try:
                        if file.endswith('.csv'):
                            df = self._read_csv_with_encoding(filepath)
                        else:
                            # Try header at row 6, then default
                            try:
                                df = pd.read_excel(filepath, header=5)
                            except:
                                df = pd.read_excel(filepath)
                        
                        list_data_list.append(df)
                        print(f"      ✓ {file} ({df.shape[0]} rows)")
                    except Exception as e:
                        print(f"      ❌ Error reading {file}: {e}")
            
            if list_data_list:
                self.list_data = pd.concat(list_data_list, ignore_index=True)
                self.list_data = self.list_data.drop_duplicates()
                print(f"   ✓ LIST DATA consolidated: {self.list_data.shape[0]} rows")
        
        # Load MRST DATA
        print("   Loading MRST DATA...")
        if os.path.exists(self.mrst_path):
            try:
                self.mrst_data = {
                    'sheet1': pd.read_excel(self.mrst_path, sheet_name=0),
                    'sheet2': pd.read_excel(self.mrst_path, sheet_name=1),
                    'sheet3': pd.read_excel(self.mrst_path, sheet_name=2)
                }
                print(f"   ✓ MRST Sheet 1 (Store + Category): {self.mrst_data['sheet1'].shape[0]} rows")
                print(f"   ✓ MRST Sheet 2 (Category Level): {self.mrst_data['sheet2'].shape[0]} rows")
                print(f"   ✓ MRST Sheet 3 (Article Level): {self.mrst_data['sheet3'].shape[0]} rows")
            except Exception as e:
                print(f"   ❌ Error reading MRST: {e}")
        
        return True
    
    # ================== STEP 5: Prepare Merge Keys ==================
    
    def _prepare_merge_keys(self, df: pd.DataFrame, key_cols: List[str]) -> pd.DataFrame:
        """Convert key columns to string and trim spaces"""
        df_copy = df.copy()
        for col in key_cols:
            if col in df_copy.columns:
                df_copy[col] = df_copy[col].astype(str).str.strip()
        return df_copy
    
    def step5_prepare_merge_keys(self):
        """Standardize key columns for merging"""
        print("\n🔑 STEP 5: Preparing Merge Keys...")
        
        key_cols = ['MAJ_CAT', 'GEN_ART_NUMBER', 'STORE_ST_CD', 'CLR']
        
        self.expanded_data = self._prepare_merge_keys(self.expanded_data, key_cols)
        if self.base_data is not None:
            self.base_data = self._prepare_merge_keys(self.base_data, ['MAJCAT', 'GEN_ART', 'Store_Code', 'CLR'])
        if self.list_data is not None:
            self.list_data = self._prepare_merge_keys(self.list_data, ['MAJCAT', 'GEN_ART', 'ST_CD', 'CLR'])
        if self.mrst_data is not None:
            for sheet_name in self.mrst_data:
                self.mrst_data[sheet_name] = self._prepare_merge_keys(
                    self.mrst_data[sheet_name], 
                    ['MAJ_CAT', 'GEN_ART_NUMBER', 'STORE_ST_CD', 'CLR']
                )
        
        print("   ✓ Keys standardized and trimmed")
        return True
    
    # ================== STEP 6: Merge BASE DATA ==================
    
    def step6_merge_base_data(self):
        """Merge BASE DATA with expanded data"""
        print("\n🔗 STEP 6: Merging BASE DATA...")
        
        if self.base_data is None or self.base_data.empty:
            print("   ℹ️  BASE DATA not available, skipping...")
            self.expanded_data = self.expanded_data.copy()
            return True
        
        try:
            # Identify merge columns
            merge_cols_main = [col for col in ['MAJ_CAT', 'GEN_ART_NUMBER', 'STORE_ST_CD', 'CLR'] 
                             if col in self.expanded_data.columns]
            merge_cols_base = [col.replace('MAJ_CAT', 'MAJCAT').replace('GEN_ART_NUMBER', 'GEN_ART')
                              .replace('STORE_ST_CD', 'Store_Code') 
                              for col in merge_cols_main]
            merge_cols_base = [col for col in merge_cols_base if col in self.base_data.columns]
            
            if not merge_cols_main or not merge_cols_base:
                print("   ⚠️  No matching columns for merge, skipping...")
                return True
            
            # Map column names
            rename_dict = dict(zip(merge_cols_base, merge_cols_main))
            base_renamed = self.base_data.rename(columns=rename_dict)
            
            # Merge
            self.expanded_data = self.expanded_data.merge(
                base_renamed, 
                on=merge_cols_main,
                how='left',
                suffixes=('', '_base')
            )
            
            print(f"   ✓ Merged: {self.expanded_data.shape[0]} rows")
            
        except Exception as e:
            print(f"   ❌ Error merging BASE DATA: {e}")
        
        return True
    
    # ================== STEP 7: Merge LIST DATA ==================
    
    def step7_merge_list_data(self):
        """Merge LIST DATA with expanded data"""
        print("\n🔗 STEP 7: Merging LIST DATA...")
        
        if self.list_data is None or self.list_data.empty:
            print("   ℹ️  LIST DATA not available, skipping...")
            return True
        
        try:
            merge_cols_main = [col for col in ['MAJ_CAT', 'GEN_ART_NUMBER', 'STORE_ST_CD', 'CLR'] 
                             if col in self.expanded_data.columns]
            merge_cols_list = [col.replace('MAJ_CAT', 'MAJCAT').replace('GEN_ART_NUMBER', 'GEN_ART')
                              .replace('STORE_ST_CD', 'ST_CD') 
                              for col in merge_cols_main]
            merge_cols_list = [col for col in merge_cols_list if col in self.list_data.columns]
            
            if not merge_cols_main or not merge_cols_list:
                print("   ⚠️  No matching columns for merge, skipping...")
                return True
            
            rename_dict = dict(zip(merge_cols_list, merge_cols_main))
            list_renamed = self.list_data.rename(columns=rename_dict)
            
            self.expanded_data = self.expanded_data.merge(
                list_renamed,
                on=merge_cols_main,
                how='left',
                suffixes=('', '_list')
            )
            
            print(f"   ✓ Merged: {self.expanded_data.shape[0]} rows")
            
        except Exception as e:
            print(f"   ❌ Error merging LIST DATA: {e}")
        
        return True
    
    # ================== STEP 8: Merge MRST Data ==================
    
    def step8_merge_mrst_data(self):
        """Merge all three MRST sheets"""
        print("\n🔗 STEP 8: Merging MRST DATA...")
        
        if self.mrst_data is None:
            print("   ℹ️  MRST DATA not available, skipping...")
            return True
        
        try:
            # Sheet 1: Store + Category
            if 'sheet1' in self.mrst_data and not self.mrst_data['sheet1'].empty:
                merge_cols = [col for col in ['STORE_ST_CD', 'MAJ_CAT'] 
                            if col in self.expanded_data.columns 
                            and col in self.mrst_data['sheet1'].columns]
                if merge_cols:
                    self.expanded_data = self.expanded_data.merge(
                        self.mrst_data['sheet1'],
                        on=merge_cols,
                        how='left',
                        suffixes=('', '_mrst1')
                    )
                    print(f"   ✓ Sheet 1 (Store+Category): Merged")
            
            # Sheet 2: Category Level
            if 'sheet2' in self.mrst_data and not self.mrst_data['sheet2'].empty:
                if 'MAJ_CAT' in self.expanded_data.columns and 'MAJ_CAT' in self.mrst_data['sheet2'].columns:
                    self.expanded_data = self.expanded_data.merge(
                        self.mrst_data['sheet2'],
                        on='MAJ_CAT',
                        how='left',
                        suffixes=('', '_mrst2')
                    )
                    print(f"   ✓ Sheet 2 (Category): Merged")
            
            # Sheet 3: Article Level
            if 'sheet3' in self.mrst_data and not self.mrst_data['sheet3'].empty:
                merge_cols = [col for col in ['MAJ_CAT', 'GEN_ART_NUMBER', 'CLR'] 
                            if col in self.expanded_data.columns 
                            and col in self.mrst_data['sheet3'].columns]
                if merge_cols:
                    self.expanded_data = self.expanded_data.merge(
                        self.mrst_data['sheet3'],
                        on=merge_cols,
                        how='left',
                        suffixes=('', '_mrst3')
                    )
                    print(f"   ✓ Sheet 3 (Article): Merged")
            
            print(f"   ✓ Final: {self.expanded_data.shape[0]} rows, {self.expanded_data.shape[1]} columns")
            
        except Exception as e:
            print(f"   ❌ Error merging MRST DATA: {e}")
        
        return True
    
    # ================== STEP 9: Clean Data After Merge ==================
    
    def step9_clean_after_merge(self):
        """Remove duplicate columns from merges"""
        print("\n🧹 STEP 9: Cleaning Data After Merge...")
        
        # Remove _x, _y suffixes by keeping first occurrence
        cols_to_drop = [col for col in self.expanded_data.columns if col.endswith('_x')]
        self.expanded_data = self.expanded_data.drop(columns=cols_to_drop, errors='ignore')
        
        # Rename _y columns to base name
        rename_dict = {col: col[:-2] for col in self.expanded_data.columns if col.endswith('_y')}
        self.expanded_data = self.expanded_data.rename(columns=rename_dict)
        
        # Keep only one ST_CD column
        st_cd_cols = [col for col in self.expanded_data.columns if 'ST_CD' in col or 'ST_CODE' in col]
        if len(st_cd_cols) > 1:
            # Keep STORE_ST_CD, drop others
            cols_to_drop = [col for col in st_cd_cols if col != 'STORE_ST_CD']
            self.expanded_data = self.expanded_data.drop(columns=cols_to_drop, errors='ignore')
        
        print(f"   ✓ Cleaned: {self.expanded_data.shape[1]} columns remain")
        return True
    
    # ================== STEP 10: Consolidate Columns ==================
    
    def step10_consolidate_columns(self):
        """Merge multiple category columns into one"""
        print("\n📋 STEP 10: Consolidating Columns...")
        
        # Find columns with category patterns (ST-STK_BASE_GM, etc.)
        category_patterns = ['ST-STK_BASE_', 'ST_STK_BASE_']
        cols_to_consolidate = {}
        
        for col in self.expanded_data.columns:
            for pattern in category_patterns:
                if pattern in col:
                    base_name = pattern.replace('_BASE_', '').replace('_', '-')
                    if base_name not in cols_to_consolidate:
                        cols_to_consolidate[base_name] = []
                    cols_to_consolidate[base_name].append(col)
        
        # Consolidate by taking first non-null value
        for base_name, cols in cols_to_consolidate.items():
            if len(cols) > 1:
                self.expanded_data[base_name] = self.expanded_data[cols].bfill(axis=1).iloc[:, 0]
                self.expanded_data = self.expanded_data.drop(columns=cols, errors='ignore')
        
        print(f"   ✓ Consolidated: {len(cols_to_consolidate)} column groups")
        return True
    
    # ================== STEP 11: Handle Missing Values ==================
    
    def step11_handle_missing_values(self):
        """Fill NaN with 0 for non-identifier columns"""
        print("\n⚠️  STEP 11: Handling Missing Values...")
        
        identifier_cols = [col for col in ['MAJ_CAT', 'GEN_ART_NUMBER', 'STORE_ST_CD', 'CLR', 'DATE'] 
                          if col in self.expanded_data.columns]
        
        # Fill non-identifiers with 0
        non_identifier_cols = [col for col in self.expanded_data.columns if col not in identifier_cols]
        for col in non_identifier_cols:
            if self.expanded_data[col].dtype in ['float64', 'int64']:
                self.expanded_data[col] = self.expanded_data[col].fillna(0)
        
        print(f"   ✓ Filled: {len(identifier_cols)} identifier cols kept, {len(non_identifier_cols)} filled")
        return True
    
    # ================== STEP 12: Remove Duplicate CLR Rows ==================
    
    def step12_remove_duplicate_clr_rows(self):
        """Remove CLR rows with all zeros"""
        print("\n♻️  STEP 12: Removing Duplicate CLR Rows...")
        
        if 'CLR' not in self.expanded_data.columns:
            print("   ℹ️  No CLR column found, skipping...")
            return True
        
        initial_rows = len(self.expanded_data)
        
        # For each CLR group, if all numeric values are 0, keep only one row
        numeric_cols = self.expanded_data.select_dtypes(include=['float64', 'int64']).columns
        
        rows_to_keep = []
        for clr_group, group_df in self.expanded_data.groupby('CLR', dropna=False):
            numeric_sum = group_df[numeric_cols].sum(axis=1)
            zero_rows = numeric_sum == 0
            
            if zero_rows.all() and len(group_df) > 1:
                # Keep only first row of zero group
                rows_to_keep.append(group_df.index[0])
            else:
                # Keep all rows with real data
                rows_to_keep.extend(group_df.index.tolist())
        
        self.expanded_data = self.expanded_data.loc[rows_to_keep].reset_index(drop=True)
        
        print(f"   ✓ Removed duplicates: {initial_rows} → {len(self.expanded_data)} rows")
        return True
    
    # ================== STEP 13: Generate Output ==================
    
    def step13_generate_output(self, row_limit: int = 100000):
        """Save output to CSV/Excel"""
        print("\n💾 STEP 13: Generating Output...")
        
        self.final_data = self.expanded_data.copy()
        total_rows = len(self.final_data)
        
        if total_rows <= row_limit:
            # Single CSV
            csv_path = os.path.join(self.output_folder, 'MSA_Analysis_Output.csv')
            self.final_data.to_csv(csv_path, index=False)
            print(f"   ✓ CSV saved: {csv_path} ({total_rows} rows)")
            
            # Excel
            try:
                excel_path = os.path.join(self.output_folder, 'MSA_Analysis_Output.xlsx')
                self.final_data.to_excel(excel_path, index=False, sheet_name='Data')
                print(f"   ✓ Excel saved: {excel_path}")
            except Exception as e:
                print(f"   ⚠️  Could not save Excel: {e}")
        else:
            # Split into multiple CSVs
            chunk_size = row_limit
            for i, chunk_start in enumerate(range(0, total_rows, chunk_size)):
                chunk_end = min(chunk_start + chunk_size, total_rows)
                chunk = self.final_data.iloc[chunk_start:chunk_end]
                
                csv_path = os.path.join(self.output_folder, f'MSA_Analysis_Output_Part_{i+1}.csv')
                chunk.to_csv(csv_path, index=False)
                print(f"   ✓ Part {i+1} saved: {csv_path} ({len(chunk)} rows)")
        
        return True
    
    # ================== STEP 14: Generate Summary ==================
    
    def step14_generate_summary(self):
        """Create a summary report"""
        print("\n📊 STEP 14: Generating Summary...")
        
        summary = {
            'Total Rows': len(self.final_data),
            'Total Columns': len(self.final_data.columns),
            'Numeric Columns': len(self.final_data.select_dtypes(include=['float64', 'int64']).columns),
            'Text Columns': len(self.final_data.select_dtypes(include=['object']).columns),
            'Memory Usage (MB)': round(self.final_data.memory_usage(deep=True).sum() / 1024**2, 2),
        }
        
        print("\n" + "="*50)
        print("📈 SUMMARY")
        print("="*50)
        for key, value in summary.items():
            print(f"  {key}: {value}")
        
        print("\n📋 First 5 Rows:")
        print(self.final_data.head())
        
        print("\n📋 Column List:")
        for i, col in enumerate(self.final_data.columns, 1):
            dtype = self.final_data[col].dtype
            null_count = self.final_data[col].isna().sum()
            print(f"  {i}. {col} ({dtype}) - {null_count} nulls")
        
        # Save summary to text file
        summary_path = os.path.join(self.output_folder, 'SUMMARY.txt')
        with open(summary_path, 'w') as f:
            f.write("MSA STOCK ANALYSIS SUMMARY\n")
            f.write("="*50 + "\n\n")
            for key, value in summary.items():
                f.write(f"{key}: {value}\n")
            f.write(f"\nColumns: {self.final_data.shape[1]}\n")
            for i, col in enumerate(self.final_data.columns, 1):
                f.write(f"{i}. {col}\n")
        
        print(f"\n   ✓ Summary saved: {summary_path}")
        return True
    
    # ================== MAIN EXECUTION ==================
    
    def run_pipeline(self):
        """Execute all steps in sequence"""
        print("\n" + "="*60)
        print("🚀 MSA STOCK ANALYSIS PIPELINE STARTING")
        print("="*60)
        
        steps = [
            ("Load Input Data", self.step1_load_input_data),
            ("Filter Data", self.step2_filter_data),
            ("Expand Across Stores", self.step3_expand_across_stores),
            ("Load External Data", self.step4_load_external_data),
            ("Prepare Merge Keys", self.step5_prepare_merge_keys),
            ("Merge BASE DATA", self.step6_merge_base_data),
            ("Merge LIST DATA", self.step7_merge_list_data),
            ("Merge MRST Data", self.step8_merge_mrst_data),
            ("Clean After Merge", self.step9_clean_after_merge),
            ("Consolidate Columns", self.step10_consolidate_columns),
            ("Handle Missing Values", self.step11_handle_missing_values),
            ("Remove Duplicate CLR", self.step12_remove_duplicate_clr_rows),
            ("Generate Output", self.step13_generate_output),
            ("Generate Summary", self.step14_generate_summary),
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
        
        print("\n" + "="*60)
        print("✅ PIPELINE COMPLETED SUCCESSFULLY")
        print("="*60)
        return True


# ================== USAGE EXAMPLE ==================

if __name__ == "__main__":
    """
    Example usage:
    
    1. Update file paths below
    2. Run: python msa_stock_analysis.py
    """
    
    pipeline = MSAStockAnalysis(
        msa_csv_path="data/MSA_Data.csv",
        store_master_path="data/Store_Master.xlsx",
        base_data_folder="data/BASE_DATA",
        list_data_folder="data/LIST_DATA",
        mrst_path="data/MRST_Data.xlsx",
        output_folder="output"
    )
    
    success = pipeline.run_pipeline()
    
    if success:
        print("\n🎉 All done! Check the 'output' folder for results.")
    else:
        print("\n⚠️  Pipeline had issues. Check messages above.")
