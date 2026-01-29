import zipfile
import sys
import re
import difflib
import json
from bs4 import BeautifulSoup

def extract_text_segments(epub_path):
    """
    Extracts text from EPUB, split by lines/paragraphs to facilitate matching.
    Returns a dict: { filename: [line1, line2, ...] }
    """
    segments = {}
    try:
        with zipfile.ZipFile(epub_path, 'r') as z:
            html_files = [f for f in z.namelist() if f.endswith(('.html', '.xhtml'))]
            html_files.sort()
            
            for f in html_files:
                if 'cover' in f.lower() or 'nav' in f.lower() or 'toc' in f.lower() or 'colophon' in f.lower(): 
                    continue
                
                with z.open(f) as html_file:
                    soup = BeautifulSoup(html_file.read(), 'html.parser')
                    # Extract text lines, stripping whitespace
                    text = soup.get_text()
                    lines = [l.strip() for l in text.splitlines() if l.strip()]
                    segments[f] = lines
    except Exception as e:
        print(f"Error reading {epub_path}: {e}")
        return {}
    return segments

def analyze_changes(original_path, cleaned_path, output_json):
    print(f"Analyzing changes between:\nOriginal: {original_path}\nCleaned:  {cleaned_path}")
    
    orig_data = extract_text_segments(original_path)
    clean_data = extract_text_segments(cleaned_path)
    
    analysis_report = {
        "summary": {
            "files_analyzed": 0,
            "total_corrections": 0,
            "additions": 0,
            "deletions": 0,
            "modifications": 0
        },
        "details": []
    }
    
    for filename, orig_lines in orig_data.items():
        if filename in clean_data:
            clean_lines = clean_data[filename]
            analysis_report["summary"]["files_analyzed"] += 1
            
            # Use SequenceMatcher to find diffs
            matcher = difflib.SequenceMatcher(None, orig_lines, clean_lines)
            
            for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                if tag == 'equal':
                    continue
                
                original_segment = "\n".join(orig_lines[i1:i2])
                cleaned_segment = "\n".join(clean_lines[j1:j2])
                
                # Filter out pure noise (like page numbers if possible, though 'strip' helps)
                if not original_segment and not cleaned_segment:
                    continue

                entry = {
                    "file": filename,
                    "type": tag, # replace, delete, insert
                    "original": original_segment,
                    "cleaned": cleaned_segment,
                    "length_diff": len(cleaned_segment) - len(original_segment)
                }
                
                analysis_report["details"].append(entry)
                
                if tag == 'replace':
                    analysis_report["summary"]["modifications"] += 1
                elif tag == 'insert':
                    analysis_report["summary"]["additions"] += 1
                elif tag == 'delete':
                    analysis_report["summary"]["deletions"] += 1

    analysis_report["summary"]["total_corrections"] = len(analysis_report["details"])
    
    print(f"\nAnalysis Complete.")
    print(f"Files Processed: {analysis_report['summary']['files_analyzed']}")
    print(f"Total Corrections Found: {analysis_report['summary']['total_corrections']}")
    
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(analysis_report, f, indent=2, ensure_ascii=False)
    
    print(f"Report saved to: {output_json}")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python analyze_corrections.py <original_epub> <cleaned_epub> <output_json>")
    else:
        analyze_changes(sys.argv[1], sys.argv[2], sys.argv[3])
