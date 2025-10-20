# COBOL Analyzer

A command-line tool for parsing COBOL source files and extracting program structure, dependencies, and statistics.

## Features

- Extract program IDs, procedures, and dependencies
- Identify CALL statements and file operations
- Generate markdown and JSON reports
- Analyze single files or entire directories
- Detailed error handling and reporting

## Installation
```bash
# No dependencies needed - pure Python 3
git clone <your-repo>
cd cobol-analyzer
```

## Usage
```bash
# Analyze single file
python cobol_analyzer.py program.cob

# Generate markdown report
python cobol_analyzer.py program.cob --markdown

# Analyze entire directory with both reports
python cobol_analyzer.py ./cobol_files --both
```

## Use Cases

- Legacy system documentation
- Modernization planning
- Dependency analysis
- Code review automation

## Limitations

- Currently supports standard COBOL syntax
- Does not parse COPY books inline
- Regex-based parsing (not full AST)

## Future Enhancements

- Dependency graph visualization
- COPY book resolution
- Call tree generation
- Integration with Tree-sitter for better parsing