#!/usr/bin/env python3
"""
COBOL Analyzer - MVP Version
Parses COBOL files and extracts basic program structure
"""

import sys
import re
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional
import json


@dataclass
class ProgramInfo:
    """Stores extracted COBOL program information"""
    program_id: Optional[str] = None
    file_path: str = ""
    calls: List[str] = None
    files_used: List[str] = None
    procedures: List[str] = None
    
    def __post_init__(self):
        self.calls = self.calls or []
        self.files_used = self.files_used or []
        self.procedures = self.procedures or []


class COBOLAnalyzer:
    """Simple COBOL parser using regex - no dependencies needed for MVP"""
    
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.content = self._read_file()
        self.info = ProgramInfo(file_path=str(file_path))
    
    def _read_file(self) -> str:
        """Read COBOL file content"""
        try:
            with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            sys.exit(1)
    
    def _extract_program_id(self) -> Optional[str]:
        """Extract PROGRAM-ID from COBOL source"""
        # Pattern: PROGRAM-ID. XXXXX
        pattern = r'PROGRAM-ID\.\s+([A-Za-z0-9\-\_]+)'
        match = re.search(pattern, self.content, re.IGNORECASE)
        return match.group(1) if match else None
    
    def _extract_calls(self) -> List[str]:
        """Extract CALL statements"""
        # Pattern: CALL "PROGRAM-NAME" or CALL 'PROGRAM-NAME'
        pattern = r'CALL\s+["\']([A-Za-z0-9\-]+)["\']'
        matches = re.findall(pattern, self.content, re.IGNORECASE)
        return list(set(matches))  # Remove duplicates
    
    def _extract_files(self) -> List[str]:
        """Extract file names from SELECT statements"""
        # Pattern: SELECT file-name ASSIGN TO...
        pattern = r'SELECT\s+([A-Za-z0-9\-]+)\s+ASSIGN'
        matches = re.findall(pattern, self.content, re.IGNORECASE)
        return list(set(matches))
    
    def _extract_procedures(self) -> List[str]:
        """Extract procedure/paragraph names"""
        # Pattern: procedure-name. at start of line (simplified)
        pattern = r'^[ ]{7,}([A-Za-z0-9\-]+)\.'
        matches = re.findall(pattern, self.content, re.MULTILINE)
        # Filter out common COBOL keywords
        keywords = {'PROGRAM-ID', 'AUTHOR', 'DATE-WRITTEN', 'ENVIRONMENT', 'DATA', 'PROCEDURE', 'WORKING-STORAGE', 'FILE', 'SECTION'}
        procedures = [m for m in matches if m.upper() not in keywords]
        return list(set(procedures))[:20]  # Limit to first 20 unique procedures
    
    def analyze(self) -> ProgramInfo:
        """Run all analysis steps"""
        print(f"🔍 Analyzing: {self.file_path.name}")
        
        self.info.program_id = self._extract_program_id()
        self.info.calls = self._extract_calls()
        self.info.files_used = self._extract_files()
        self.info.procedures = self._extract_procedures()
        
        return self.info
    
    def print_results(self):
        """Print analysis results to console"""
        print("\n" + "="*60)
        print(f"📄 File: {self.info.file_path}")
        print("="*60)
        
        print(f"\n🏷️  Program ID: {self.info.program_id or 'Not found'}")
        
        if self.info.calls:
            print(f"\n📞 Calls ({len(self.info.calls)}):")
            for call in sorted(self.info.calls):
                print(f"   → {call}")
        else:
            print("\n📞 Calls: None found")
        
        if self.info.files_used:
            print(f"\n📁 Files ({len(self.info.files_used)}):")
            for file in sorted(self.info.files_used):
                print(f"   → {file}")
        else:
            print("\n📁 Files: None found")
        
        if self.info.procedures:
            print(f"\n⚙️  Procedures ({len(self.info.procedures)} shown):")
            for proc in sorted(self.info.procedures)[:10]:  # Show first 10
                print(f"   → {proc}")
            if len(self.info.procedures) > 10:
                print(f"   ... and {len(self.info.procedures) - 10} more")
        else:
            print("\n⚙️  Procedures: None found")
        
        print("\n" + "="*60)
    
    def export_json(self, output_path: Optional[str] = None):
        """Export results to JSON"""
        if output_path is None:
            output_path = f"{self.file_path.stem}_analysis.json"
        
        data = {
            "file": str(self.info.file_path),
            "program_id": self.info.program_id,
            "calls": sorted(self.info.calls),
            "files": sorted(self.info.files_used),
            "procedures": sorted(self.info.procedures),
            "statistics": {
                "total_calls": len(self.info.calls),
                "total_files": len(self.info.files_used),
                "total_procedures": len(self.info.procedures)
            }
        }
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Exported to: {output_path}")


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python cobol_analyzer.py <cobol_file.cob> [--json]")
        print("\nExample:")
        print("  python cobol_analyzer.py sample.cob")
        print("  python cobol_analyzer.py sample.cob --json")
        sys.exit(1)
    print(sys.argv)
    file_path = sys.argv[1]
    export_json = "--json" in sys.argv
    print(file_path)
    
    if not Path(file_path).exists():
        print(f"❌ File not found: {file_path}")
        sys.exit(1)
    
    # Run analysis
    analyzer = COBOLAnalyzer(file_path)
    analyzer.analyze()
    analyzer.print_results()
    
    # Export if requested
    if export_json:
        analyzer.export_json()


if __name__ == "__main__":
    main()