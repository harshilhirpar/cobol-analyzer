#!/usr/bin/env python3
"""
COBOL Analyzer - Production Version
Parses COBOL files and generates analysis reports
"""

import sys
import re
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict
from datetime import datetime
import json


@dataclass
class ProgramInfo:
    """Stores extracted COBOL program information"""
    program_id: Optional[str] = None
    file_path: str = ""
    file_name: str = ""
    calls: List[str] = None
    files_used: List[str] = None
    procedures: List[str] = None
    lines_of_code: int = 0
    
    def __post_init__(self):
        self.calls = self.calls or []
        self.files_used = self.files_used or []
        self.procedures = self.procedures or []


class COBOLAnalyzer:
    """Simple COBOL parser using regex"""
    
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.content = ""
        self.info = ProgramInfo(
            file_path=str(file_path),
            file_name=self.file_path.name
        )
        self.errors = []
    
    def _read_file(self) -> bool:
        """Read COBOL file content with error handling"""
        try:
            with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as f:
                self.content = f.read()
            
            # Count non-empty lines
            self.info.lines_of_code = len([line for line in self.content.split('\n') 
                                          if line.strip() and not line.strip().startswith('*')])
            return True
            
        except FileNotFoundError:
            self.errors.append(f"File not found: {self.file_path}")
            return False
        except PermissionError:
            self.errors.append(f"Permission denied: {self.file_path}")
            return False
        except Exception as e:
            self.errors.append(f"Error reading file: {str(e)}")
            return False
    
    def _extract_program_id(self) -> Optional[str]:
        """Extract PROGRAM-ID from COBOL source"""
        try:
            pattern = r'PROGRAM-ID\.\s+([A-Za-z0-9\-]+)'
            match = re.search(pattern, self.content, re.IGNORECASE)
            return match.group(1).strip() if match else None
        except Exception as e:
            self.errors.append(f"Error extracting PROGRAM-ID: {str(e)}")
            return None
    
    def _extract_calls(self) -> List[str]:
        """Extract CALL statements"""
        try:
            pattern = r'CALL\s+["\']([A-Za-z0-9\-]+)["\']'
            matches = re.findall(pattern, self.content, re.IGNORECASE)
            return sorted(list(set(matches)))
        except Exception as e:
            self.errors.append(f"Error extracting CALLs: {str(e)}")
            return []
    
    def _extract_files(self) -> List[str]:
        """Extract file names from SELECT statements"""
        try:
            pattern = r'SELECT\s+([A-Za-z0-9\-]+)\s+ASSIGN'
            matches = re.findall(pattern, self.content, re.IGNORECASE)
            return sorted(list(set(matches)))
        except Exception as e:
            self.errors.append(f"Error extracting files: {str(e)}")
            return []
    
    def _extract_procedures(self) -> List[str]:
        """Extract procedure/paragraph names"""
        try:
            pattern = r'^[ ]{7,}([A-Za-z0-9\-]+)\.'
            matches = re.findall(pattern, self.content, re.MULTILINE)
            
            # Filter out COBOL keywords
            keywords = {
                'PROGRAM-ID', 'AUTHOR', 'DATE-WRITTEN', 'ENVIRONMENT',
                'DATA', 'PROCEDURE', 'WORKING-STORAGE', 'FILE', 'SECTION',
                'IDENTIFICATION', 'DIVISION', 'CONFIGURATION', 'INPUT-OUTPUT',
                'FILE-CONTROL', 'FD', 'LINKAGE'
            }
            
            procedures = [m for m in matches if m.upper() not in keywords]
            return sorted(list(set(procedures)))
            
        except Exception as e:
            self.errors.append(f"Error extracting procedures: {str(e)}")
            return []
    
    def analyze(self) -> bool:
        """Run all analysis steps"""
        if not self._read_file():
            return False
        
        self.info.program_id = self._extract_program_id()
        self.info.calls = self._extract_calls()
        self.info.files_used = self._extract_files()
        self.info.procedures = self._extract_procedures()
        
        return True
    
    def print_results(self):
        """Print analysis results to console"""
        print("\n" + "="*70)
        print(f"📄 File: {self.info.file_name}")
        print("="*70)
        
        if self.errors:
            print("⚠️  Warnings/Errors:")
            for error in self.errors:
                print(f"   ⚠️  {error}")
            print()
        
        print(f"🏷️  Program ID: {self.info.program_id or 'Not found'}")
        print(f"📊 Lines of Code: {self.info.lines_of_code}")
        
        if self.info.calls:
            print(f"\n📞 External Calls ({len(self.info.calls)}):")
            for call in self.info.calls:
                print(f"   → {call}")
        else:
            print("\n📞 External Calls: None")
        
        if self.info.files_used:
            print(f"\n📁 File Operations ({len(self.info.files_used)}):")
            for file in self.info.files_used:
                print(f"   → {file}")
        else:
            print("\n📁 File Operations: None")
        
        if self.info.procedures:
            print(f"\n⚙️  Procedures/Paragraphs ({len(self.info.procedures)}):")
            shown = self.info.procedures[:15]
            for proc in shown:
                print(f"   → {proc}")
            if len(self.info.procedures) > 15:
                print(f"   ... and {len(self.info.procedures) - 15} more")
        else:
            print("\n⚙️  Procedures: None")
        
        print("\n" + "="*70)


class ReportGenerator:
    """Generates markdown reports from analysis results"""
    
    def __init__(self, analyses: List[COBOLAnalyzer]):
        self.analyses = analyses
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def generate_markdown(self, output_path: str = "analysis_report.md"):
        """Generate comprehensive markdown report"""
        report = []
        
        # Header
        report.append("# COBOL Code Analysis Report\n")
        report.append(f"**Generated:** {self.timestamp}\n")
        report.append(f"**Files Analyzed:** {len(self.analyses)}\n")
        report.append("---\n")
        
        # Summary statistics
        report.append("## 📊 Summary Statistics\n")
        total_loc = sum(a.info.lines_of_code for a in self.analyses)
        total_calls = sum(len(a.info.calls) for a in self.analyses)
        total_files = sum(len(a.info.files_used) for a in self.analyses)
        total_procs = sum(len(a.info.procedures) for a in self.analyses)
        
        report.append(f"- **Total Lines of Code:** {total_loc:,}")
        report.append(f"- **Total External Calls:** {total_calls}")
        report.append(f"- **Total File Operations:** {total_files}")
        report.append(f"- **Total Procedures:** {total_procs}\n")
        report.append("---\n")
        
        # Program dependency graph
        report.append("## 🔗 Program Dependencies\n")
        report.append("| Program | Calls | Files | Procedures |\n")
        report.append("|---------|-------|-------|------------|\n")
        
        for analyzer in self.analyses:
            info = analyzer.info
            prog_id = info.program_id or info.file_name
            report.append(
                f"| {prog_id} | {len(info.calls)} | "
                f"{len(info.files_used)} | {len(info.procedures)} |\n"
            )
        
        report.append("\n---\n")
        
        # Detailed analysis per file
        report.append("## 📋 Detailed Analysis\n")
        
        for analyzer in self.analyses:
            info = analyzer.info
            report.append(f"\n### {info.file_name}\n")
            report.append(f"**Program ID:** `{info.program_id or 'N/A'}`  \n")
            report.append(f"**Lines of Code:** {info.lines_of_code}  \n")
            report.append(f"**File Path:** `{info.file_path}`\n")
            
            if analyzer.errors:
                report.append("\n**⚠️ Warnings:**\n")
                for error in analyzer.errors:
                    report.append(f"- {error}\n")
            
            if info.calls:
                report.append("\n**External Calls:**\n")
                for call in info.calls:
                    report.append(f"- `{call}`\n")
            
            if info.files_used:
                report.append("\n**File Operations:**\n")
                for file in info.files_used:
                    report.append(f"- `{file}`\n")
            
            if info.procedures:
                report.append("\n**Procedures:**\n")
                shown = info.procedures[:10]
                for proc in shown:
                    report.append(f"- `{proc}`\n")
                if len(info.procedures) > 10:
                    report.append(f"- *...and {len(info.procedures) - 10} more*\n")
            
            report.append("\n---\n")
        
        # Write to file
        with open(output_path, 'w') as f:
            f.writelines(report)
        
        return output_path
    
    def generate_json(self, output_path: str = "analysis_report.json"):
        """Generate JSON report"""
        data = {
            "generated": self.timestamp,
            "summary": {
                "files_analyzed": len(self.analyses),
                "total_lines": sum(a.info.lines_of_code for a in self.analyses),
                "total_calls": sum(len(a.info.calls) for a in self.analyses),
                "total_files": sum(len(a.info.files_used) for a in self.analyses),
                "total_procedures": sum(len(a.info.procedures) for a in self.analyses)
            },
            "programs": []
        }
        
        for analyzer in self.analyses:
            prog_data = asdict(analyzer.info)
            prog_data["errors"] = analyzer.errors
            data["programs"].append(prog_data)
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        return output_path


def analyze_file(file_path: str, verbose: bool = True) -> COBOLAnalyzer:
    """Analyze a single COBOL file"""
    analyzer = COBOLAnalyzer(file_path)
    
    if verbose:
        print(f"🔍 Analyzing: {file_path}")
    
    if analyzer.analyze():
        if verbose:
            analyzer.print_results()
    else:
        print(f"❌ Failed to analyze: {file_path}")
        for error in analyzer.errors:
            print(f"   {error}")
    
    return analyzer


def analyze_directory(dir_path: str) -> List[COBOLAnalyzer]:
    """Analyze all COBOL files in a directory"""
    path = Path(dir_path)
    
    if not path.is_dir():
        print(f"❌ Not a directory: {dir_path}")
        return []
    
    # Find COBOL files
    cobol_extensions = ['.cob', '.cbl', '.cobol', '.CBL']
    cobol_files = []
    
    for ext in cobol_extensions:
        cobol_files.extend(path.glob(f"**/*{ext}"))
    
    if not cobol_files:
        print(f"⚠️  No COBOL files found in: {dir_path}")
        return []
    
    print(f"\n📁 Found {len(cobol_files)} COBOL file(s)")
    print("="*70)
    
    analyzers = []
    for file in cobol_files:
        analyzer = analyze_file(str(file), verbose=False)
        analyzers.append(analyzer)
        status = "✅" if not analyzer.errors else "⚠️"
        print(f"{status} {file.name}")
    
    return analyzers


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("COBOL Analyzer - Extract structure from legacy COBOL code\n")
        print("Usage:")
        print("  python cobol_analyzer.py <file.cob>           # Analyze single file")
        print("  python cobol_analyzer.py <directory>          # Analyze directory")
        print("  python cobol_analyzer.py <path> --markdown    # Generate markdown report")
        print("  python cobol_analyzer.py <path> --json        # Generate JSON report")
        print("  python cobol_analyzer.py <path> --both        # Generate both reports")
        print("  python cobol_analyzer.py <path> --graph       # Generate dependency graph")
        print("  python cobol_analyzer.py <path> --all         # Generate all outputs")
        sys.exit(1)
    
    target_path = sys.argv[1]
    generate_markdown = "--markdown" in sys.argv or "--both" in sys.argv or "--all" in sys.argv
    generate_json = "--json" in sys.argv or "--both" in sys.argv or "--all" in sys.argv
    generate_graph = "--graph" in sys.argv or "--all" in sys.argv
    
    # Check if path exists
    if not Path(target_path).exists():
        print(f"❌ Path not found: {target_path}")
        sys.exit(1)
    
    # Analyze
    if Path(target_path).is_file():
        analyzers = [analyze_file(target_path)]
    else:
        analyzers = analyze_directory(target_path)
    
    if not analyzers:
        sys.exit(1)
    
    # Generate reports
    if generate_markdown or generate_json or generate_graph:
        print("\n" + "="*70)
        print("📝 Generating Reports...")
        print("="*70)
        
        reporter = ReportGenerator(analyzers)
        
        if generate_markdown:
            md_file = reporter.generate_markdown()
            print(f"✅ Markdown report: {md_file}")
        
        if generate_json:
            json_file = reporter.generate_json()
            print(f"✅ JSON report: {json_file}")
        
        if generate_graph:
            try:
                from graph_visualizer import DependencyGraphGenerator
                
                grapher = DependencyGraphGenerator(analyzers)
                grapher.build_graph()
                
                # Generate all three graph styles
                grapher.generate_visualization("dependency_graph_detailed.png", "detailed")
                grapher.generate_visualization("dependency_graph_calls.png", "calls_only")
                grapher.generate_visualization("dependency_graph_simple.png", "simple")
                
                # Print statistics
                stats = grapher.get_statistics()
                print(f"\n📊 Graph Statistics:")
                print(f"   Programs: {stats['program_nodes']}")
                print(f"   Files: {stats['file_nodes']}")
                print(f"   Dependencies: {stats['call_edges']}")
                
                # Check for circular dependencies
                cycles = grapher.find_circular_dependencies()
                if cycles:
                    print(f"\n⚠️  Found {len(cycles)} circular dependencies:")
                    for cycle in cycles[:5]:  # Show first 5
                        print(f"   → {' -> '.join(cycle)} -> {cycle[0]}")
                
            # except ImportError:
            #     print("❌ Graph generation requires: pip install networkx matplotlib")
            except Exception as e:
                print(f"❌ Error generating graph: {e}")


if __name__ == "__main__":
    main()