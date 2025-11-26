#!/usr/bin/env python3
"""
Auto-generate manifest.json for test reports index.
This script scans the reports directory and creates a manifest file
that index.html can read to display all available reports.
"""

import json
import os
from pathlib import Path
from datetime import datetime

def generate_manifest():
    """Generate manifest.json with all available test reports."""
    # Get the directory where this script is located
    script_dir = Path(__file__).parent.resolve()
    reports_dir = script_dir
    
    reports = []
    
    # Scan for report.html files in subdirectories
    for report_dir in sorted(reports_dir.iterdir()):
        if not report_dir.is_dir():
            continue
        
        # Skip hidden directories and the current directory
        if report_dir.name.startswith('.'):
            continue
        
        report_html = report_dir / 'report.html'
        junit_xml = report_dir / 'junit.xml'
        
        if report_html.exists():
            # Get file stats
            stat = report_html.stat()
            size = stat.st_size
            modified = datetime.fromtimestamp(stat.st_mtime).isoformat()
            
            # Create relative path
            rel_path = f"{report_dir.name}/report.html"
            
            reports.append({
                'name': report_dir.name,
                'path': rel_path,
                'directory': report_dir.name,
                'size': size,
                'date': modified,
                'has_junit': junit_xml.exists()
            })
    
    # Sort by date (newest first)
    reports.sort(key=lambda x: x['date'], reverse=True)
    
    # Create manifest
    manifest = {
        'generated': datetime.now().isoformat(),
        'total_reports': len(reports),
        'reports': reports
    }
    
    # Write manifest.json
    manifest_path = reports_dir / 'manifest.json'
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    # Also write manifest.js for direct embedding (works with file:// protocol)
    manifest_js_path = reports_dir / 'manifest.js'
    with open(manifest_js_path, 'w', encoding='utf-8') as f:
        f.write('// Auto-generated manifest data\n')
        f.write('window.TEST_REPORTS_MANIFEST = ')
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write(';\n')
    
    print(f"✓ Generated manifest.json and manifest.js with {len(reports)} reports")
    return manifest

if __name__ == '__main__':
    generate_manifest()

