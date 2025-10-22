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

## 📊 Dependency Graph Visualization

Visualize program dependencies and relationships:
```bash
# Generate dependency graphs
python cobol_analyzer.py ./cobol_files --graph

# Generate all outputs (reports + graphs)
python cobol_analyzer.py ./cobol_files --all
```

### Graph Types

- **Detailed Graph**: Shows programs (squares), files (circles), all relationships
- **Calls Only**: Shows just program-to-program dependencies
- **Simple Graph**: Lightweight visualization

### Features

- Color-coded nodes (programs vs files)
- Node size based on lines of code
- Detects circular dependencies
- Exports to PNG and DOT format

### Example Output

![Dependency Graph](screenshots/dependency_graph.png)

## 🔍 Circular Dependency Detection

The tool automatically detects and reports circular dependencies:
```
⚠️  Found 2 circular dependencies:
   → PROGRAM-A -> PROGRAM-C -> PROGRAM-A
   → PROGRAM-B -> PROGRAM-D -> PROGRAM-B
```

## Future Enhancements

- Dependency graph visualization
- COPY book resolution
- Call tree generation
- Integration with Tree-sitter for better parsing

**`LICENSE`** (MIT License - makes it actually open source):
```
MIT License

Copyright (c) 2024 [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...