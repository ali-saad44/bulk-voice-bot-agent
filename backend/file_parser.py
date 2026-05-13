# backend/file_parser.py
import pandas as pd
import re
from pathlib import Path

def extract_numbers_from_file(filepath: str, phone_column: str = "phone") -> list:
    """
    Reads phone numbers from Excel, CSV, TXT, or PDF files.
    Returns cleaned numbers in E.164 format.
    """
    ext = Path(filepath).suffix.lower()
    numbers = []
    
    if ext in ['.xlsx', '.xls']:
        df = pd.read_excel(filepath)
        numbers = _extract_from_dataframe(df, phone_column)
    
    elif ext == '.csv':
        df = pd.read_csv(filepath)
        numbers = _extract_from_dataframe(df, phone_column)
    
    elif ext == '.txt':
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            numbers = _extract_from_text(content)
    
    elif ext == '.pdf':
        try:
            import PyPDF2
            with open(filepath, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() or ""
                numbers = _extract_from_text(text)
        except Exception as e:
            raise ValueError(f"Error reading PDF: {str(e)}")
    
    else:
        raise ValueError(f"Unsupported file type: {ext}")
    
    # Clean and validate numbers
    cleaned = _clean_numbers(numbers)
    print(f"DEBUG: Found {len(cleaned)} numbers: {cleaned}")  # Debug line
    return cleaned

def _extract_from_text(content):
    """Extract phone numbers from raw text - FIXED VERSION."""
    numbers = []
    
    # Split content by lines first
    lines = content.replace('\r\n', '\n').replace('\r', '\n').split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Pattern 1: Standard formats with + (e.g., +14155551234, +92 300 1234567)
        # Match + followed by digits, spaces, dashes, parentheses
        matches = re.findall(r'\+[\d\s\-\(\)]{7,}', line)
        numbers.extend(matches)
        
        # Pattern 2: Numbers without + but with dashes/spaces (e.g., 0300-1234567, 123-456-7890)
        matches2 = re.findall(r'\b\d[\d\s\-]{8,}\d\b', line)
        numbers.extend(matches2)
        
        # Pattern 3: Plain 10-15 digit numbers (e.g., 03001234567, 14155551234)
        matches3 = re.findall(r'\b\d{10,15}\b', line)
        numbers.extend(matches3)
    
    return numbers

def _extract_from_dataframe(df, phone_column):
    """Extract phone numbers from pandas DataFrame."""
    numbers = []
    
    # Try exact column name first
    if phone_column in df.columns:
        numbers = df[phone_column].dropna().astype(str).tolist()
    else:
        # Try common column names
        common_names = ['phone', 'mobile', 'cell', 'number', 'contact', 'tel', 'phone_number', 'cellphone']
        for col in df.columns:
            col_lower = str(col).lower().strip()
            if any(name in col_lower for name in common_names):
                numbers = df[col].dropna().astype(str).tolist()
                break
        
        # If still no match, auto-detect column with phone-like data
        if not numbers:
            for col in df.columns:
                sample_values = df[col].dropna().head(10).astype(str).tolist()
                phone_count = 0
                for sample in sample_values:
                    cleaned = re.sub(r'[^\d+]', '', str(sample))
                    if len(cleaned) >= 10:
                        phone_count += 1
                if phone_count >= 3:
                    numbers = df[col].dropna().astype(str).tolist()
                    break
    
    return numbers

def _clean_numbers(numbers):
    """Clean numbers to E.164 format."""
    cleaned = []
    seen = set()
    
    for num in numbers:
        if pd.isna(num):
            continue
            
        num = str(num).strip()
        if not num or num.lower() in ['nan', 'none', 'null', '']:
            continue
        
        # Remove all non-digit characters except +
        digits = re.sub(r'[^\d+]', '', num)
        
        # Skip if too short
        if len(digits) < 10:
            continue
        
        # Handle Pakistan numbers (starting with 03, length 11)
        if digits.startswith('03') and len(digits) == 11:
            formatted = f"+92{digits[1:]}"  # 03001234567 -> +923001234567
        
        # Handle numbers with + already
        elif digits.startswith('+'):
            formatted = digits
        
        # Handle US 10-digit numbers
        elif len(digits) == 10:
            formatted = f"+1{digits}"
        
        # Handle numbers with country code but no + (e.g., 923001234567)
        elif len(digits) > 10:
            formatted = f"+{digits.lstrip('+')}"
        
        else:
            continue
        
        # Validate length (E.164 max 15 digits including +)
        if len(formatted) <= 16 and formatted not in seen:
            seen.add(formatted)
            cleaned.append(formatted)
    
    return cleaned

def create_result_file(original_filepath: str, campaign_id: int, calls_data: list, campaigns_folder: str) -> str:
    """
    Creates an updated Excel/CSV file with Call_Status column.
    Returns the path to the new file.
    """
    import os
    from datetime import datetime
    
    original_name = Path(original_filepath).stem
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    result_filename = f"{original_name}_results_{timestamp}.xlsx"
    result_path = os.path.join(campaigns_folder, result_filename)
    
    # Create DataFrame with results
    data = []
    for call in calls_data:
        data.append({
            'Phone_Number': call['phone_number'],
            'Call_Status': call['status'],
            'Duration_Seconds': call['duration'],
            'Twilio_SID': call['twilio_sid'],
            'Error_Message': call['error_message'] or '',
            'Completed_At': call['completed_at'] or ''
        })
    
    df = pd.DataFrame(data)
    
    # Add summary sheet
    with pd.ExcelWriter(result_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Call Results', index=False)
        
        # Summary sheet
        stats = df['Call_Status'].value_counts().to_dict()
        summary_data = {
            'Status': list(stats.keys()),
            'Count': list(stats.values())
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
    
    return result_path