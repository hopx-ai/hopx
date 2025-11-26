#!/usr/bin/env python3
"""
Interactive Test Runner
Allows hierarchical selection and execution of tests.
"""

import ast
import os
import subprocess
import sys
import hashlib
from pathlib import Path
from collections import defaultdict

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def clear_screen():
    """Clear the terminal screen."""
    os.system('clear' if os.name != 'nt' else 'cls')

def get_test_classes_and_methods(file_path):
    """Extract test classes and methods from a Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            tree = ast.parse(content, filename=file_path)
        
        classes = []
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and node.name.startswith('Test'):
                methods = []
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name.startswith('test_'):
                        methods.append(item.name)
                if methods:
                    classes.append({'name': node.name, 'methods': sorted(methods)})
        return classes
    except Exception:
        return []

def build_test_hierarchy():
    """Build hierarchical structure of tests."""
    # Get the directory where this script is located (python/tests/)
    script_dir = Path(__file__).parent.resolve()
    base_dir = script_dir
    python_dir = base_dir.parent  # python/ directory
    
    hierarchy = {
        'integration': {},
        'e2e': {}
    }
    
    # Scan integration tests
    for file_path in sorted(base_dir.glob('integration/**/*.py')):
        if file_path.name == '__init__.py' or file_path.name.startswith('generate_') or file_path.name.startswith('debug_'):
            continue
        
        rel_path = file_path.relative_to(base_dir / 'integration')
        parts = rel_path.parts[:-1]  # Directory parts
        filename = rel_path.name
        
        # Build nested structure
        current = hierarchy['integration']
        for part in parts:
            if part not in current:
                current[part] = {'_type': 'category'}
            current = current[part]
        
        # Add file with classes - store path relative to python/ directory
        classes = get_test_classes_and_methods(file_path)
        test_path_rel = file_path.relative_to(python_dir)
        current[filename] = {
            '_type': 'file',
            '_path': str(test_path_rel),
            '_classes': classes
        }
    
    # Scan e2e tests
    for file_path in sorted(base_dir.glob('e2e/**/*.py')):
        if file_path.name == '__init__.py':
            continue
        
        rel_path = file_path.relative_to(base_dir / 'e2e')
        parts = rel_path.parts[:-1]
        filename = rel_path.name
        
        current = hierarchy['e2e']
        for part in parts:
            if part not in current:
                current[part] = {'_type': 'category'}
            current = current[part]
        
        # Add file with classes - store path relative to python/ directory
        classes = get_test_classes_and_methods(file_path)
        test_path_rel = file_path.relative_to(python_dir)
        current[filename] = {
            '_type': 'file',
            '_path': str(test_path_rel),
            '_classes': classes
        }
    
    return hierarchy

def display_menu(items, title, breadcrumb="", show_back=True, show_run_all=False):
    """Display a menu and return selected item."""
    clear_screen()
    
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{title:^60}{Colors.ENDC}")
    if breadcrumb:
        print(f"{Colors.CYAN}Location: {breadcrumb}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")
    
    menu_items = []
    
    # Display special options first (using letters)
    if show_run_all:
        print(f"{Colors.GREEN}[a] Run All Tests{Colors.ENDC}")
        menu_items.append(('__run_all__', 'Run All Tests'))
    
    if show_back:
        print(f"{Colors.YELLOW}[b] ← Back{Colors.ENDC}")
        menu_items.append(('__back__', 'Back'))
    
    if show_run_all or show_back:
        print()
    
    # Display items (numbered starting from 1)
    index = 1
    for key, value in items:
        if isinstance(value, dict):
            if value.get('_type') == 'file':
                file_name = key
                classes = value.get('_classes', [])
                class_count = len(classes)
                method_count = sum(len(c['methods']) for c in classes)
                print(f"{Colors.BLUE}[{index}] {file_name}{Colors.ENDC} ({class_count} classes, {method_count} methods)")
            elif value.get('_type') == 'category':
                print(f"{Colors.CYAN}[{index}] {key}/ {Colors.ENDC}→")
            else:
                print(f"{Colors.CYAN}[{index}] {key}/ {Colors.ENDC}→")
        else:
            print(f"{Colors.BLUE}[{index}] {key}{Colors.ENDC}")
        
        menu_items.append((key, value))
        index += 1
    
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    
    # Build help text
    help_parts = []
    if show_run_all:
        help_parts.append("'a' for all")
    if show_back:
        help_parts.append("'b' for back")
    if items:
        help_parts.append(f"1-{len(items)} for items")
    
    help_text = " | ".join(help_parts)
    
    while True:
        try:
            choice = input(f"\n{Colors.BOLD}Select option ({help_text}): {Colors.ENDC}").strip().lower()
            
            # Handle special options
            if choice == 'a' and show_run_all:
                return ('__run_all__', 'Run All Tests')
            if choice == 'b' and show_back:
                return ('__back__', 'Back')
            
            # Handle numbered options
            choice_num = int(choice)
            if 1 <= choice_num <= len(items):
                return menu_items[len(menu_items) - len(items) + choice_num - 1]
            else:
                print(f"{Colors.RED}Invalid option. Please select 1-{len(items)}.{Colors.ENDC}")
        except ValueError:
            print(f"{Colors.RED}Invalid input. Please enter a number (1-{len(items)}) or letter (a/b).{Colors.ENDC}")
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Exiting...{Colors.ENDC}")
            sys.exit(0)

def get_pytest_command(test_path, test_name="", verbose=True, generate_reports=True):
    """Build pytest command with options."""
    # Get the tests directory (where this script is located)
    script_dir = Path(__file__).parent.resolve()
    base_dir = script_dir
    
    cmd = ['pytest']
    
    if verbose:
        cmd.extend(['-v', '--showlocals'])
    
    if generate_reports:
        # Create report path - use test_name if provided, otherwise derive from test_path
        if test_name:
            # Sanitize test_name for use as directory name
            safe_name = test_name.lower().replace(' ', '_').replace('/', '_').replace('::', '_')
            # Limit length to avoid filesystem issues
            if len(safe_name) > 100:
                safe_name = safe_name[:100]
            report_dir_name = safe_name
        else:
            # For single test path, use the path
            if ' ' in test_path:
                # Multiple paths - use hash
                path_hash = hashlib.md5(test_path.encode()).hexdigest()[:8]
                report_dir_name = f"multiple_tests_{path_hash}"
            else:
                # Single path
                report_dir_name = test_path.replace('tests/', '').replace('.py', '').replace('/', '_').replace('::', '_')
                # Limit length
                if len(report_dir_name) > 100:
                    path_hash = hashlib.md5(report_dir_name.encode()).hexdigest()[:8]
                    report_dir_name = f"{report_dir_name[:92]}_{path_hash}"
        
        report_dir = base_dir / 'reports' / report_dir_name
        report_dir.mkdir(parents=True, exist_ok=True)
        
        html_report = report_dir / 'report.html'
        junit_report = report_dir / 'junit.xml'
        
        cmd.extend([
            '--html', str(html_report),
            '--self-contained-html',
            '--junitxml', str(junit_report)
        ])
    
    # Handle multiple test paths (space-separated)
    if ' ' in test_path:
        cmd.extend(test_path.split())
    else:
        cmd.append(test_path)
    
    return cmd

def run_tests(test_path, test_name="", verbose=True, generate_reports=True):
    """Run tests and display results."""
    # Get the python/ directory (parent of tests/)
    script_dir = Path(__file__).parent.resolve()
    python_dir = script_dir.parent
    
    clear_screen()
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}Running Tests{Colors.ENDC}")
    if test_name:
        print(f"{Colors.CYAN}Test: {test_name}{Colors.ENDC}")
    print(f"{Colors.CYAN}Path: {test_path}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")
    
    cmd = get_pytest_command(test_path, test_name, verbose, generate_reports)
    
    print(f"{Colors.YELLOW}Command: {' '.join(cmd)}{Colors.ENDC}\n")
    
    try:
        result = subprocess.run(cmd, cwd=python_dir)
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
        if result.returncode == 0:
            print(f"{Colors.GREEN}✓ Tests completed successfully!{Colors.ENDC}")
        else:
            print(f"{Colors.RED}✗ Tests failed (exit code: {result.returncode}){Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")
        
        # Auto-generate manifest.json for index.html
        if generate_reports:
            try:
                manifest_script = script_dir / 'reports' / 'generate_manifest.py'
                if manifest_script.exists():
                    subprocess.run([sys.executable, str(manifest_script)], 
                                 cwd=python_dir, 
                                 capture_output=True,
                                 check=False)
            except Exception:
                pass  # Silently fail if manifest generation doesn't work
        
        input(f"{Colors.YELLOW}Press Enter to continue...{Colors.ENDC}")
        return result.returncode == 0
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Test execution interrupted.{Colors.ENDC}")
        input(f"{Colors.YELLOW}Press Enter to continue...{Colors.ENDC}")
        return False

def navigate_suite(suite_name, suite_data, breadcrumb=""):
    """Navigate through a test suite."""
    current_breadcrumb = f"{breadcrumb} > {suite_name}" if breadcrumb else suite_name
    
    while True:
        # Filter out internal metadata keys (starting with _)
        items = [(k, v) for k, v in suite_data.items() if not k.startswith('_')]
        selected_key, selected_value = display_menu(
            items,
            f"Test Suite: {suite_name.upper()}",
            current_breadcrumb,
            show_back=bool(breadcrumb),
            show_run_all=True
        )
        
        if selected_key == '__back__':
            return
        elif selected_key == '__run_all__':
            # Run all tests in suite
            test_paths = []
            def collect_paths(data, prefix=""):
                for key, value in data.items():
                    # Skip internal metadata keys
                    if key.startswith('_'):
                        continue
                    if isinstance(value, dict):
                        if value.get('_type') == 'file':
                            test_paths.append(value['_path'])
                        else:
                            collect_paths(value, f"{prefix}/{key}" if prefix else key)
            
            collect_paths(suite_data)
            if test_paths:
                run_tests(' '.join(test_paths), f"All {suite_name} tests")
            continue
        
        # Navigate deeper
        if isinstance(selected_value, dict):
            if selected_value.get('_type') == 'file':
                navigate_file(selected_key, selected_value, current_breadcrumb)
            elif selected_value.get('_type') == 'category':
                navigate_category(selected_key, selected_value, current_breadcrumb)
            else:
                navigate_category(selected_key, selected_value, current_breadcrumb)

def navigate_category(category_name, category_data, breadcrumb=""):
    """Navigate through a category."""
    current_breadcrumb = f"{breadcrumb} > {category_name}"
    
    while True:
        # Filter out internal metadata keys (starting with _)
        items = [(k, v) for k, v in category_data.items() if not k.startswith('_')]
        selected_key, selected_value = display_menu(
            items,
            f"Category: {category_name}",
            current_breadcrumb,
            show_back=True,
            show_run_all=True
        )
        
        if selected_key == '__back__':
            return
        elif selected_key == '__run_all__':
            # Run all tests in category
            test_paths = []
            def collect_paths(data):
                for key, value in data.items():
                    # Skip internal metadata keys
                    if key.startswith('_'):
                        continue
                    if isinstance(value, dict):
                        if value.get('_type') == 'file':
                            test_paths.append(value['_path'])
                        else:
                            collect_paths(value)
            
            collect_paths(category_data)
            if test_paths:
                run_tests(' '.join(test_paths), f"All {category_name} tests")
            continue
        
        if isinstance(selected_value, dict):
            if selected_value.get('_type') == 'file':
                navigate_file(selected_key, selected_value, current_breadcrumb)
            else:
                navigate_category(selected_key, selected_value, current_breadcrumb)

def navigate_file(file_name, file_data, breadcrumb=""):
    """Navigate through a test file."""
    current_breadcrumb = f"{breadcrumb} > {file_name}"
    file_path = file_data['_path']
    classes = file_data.get('_classes', [])
    
    while True:
        items = []
        for cls in classes:
            items.append((cls['name'], cls))
        
        if not items:
            # No classes, just run the file
            run_tests(file_path, file_name)
            return
        
        selected_key, selected_value = display_menu(
            items,
            f"Test File: {file_name}",
            current_breadcrumb,
            show_back=True,
            show_run_all=True
        )
        
        if selected_key == '__back__':
            return
        elif selected_key == '__run_all__':
            run_tests(file_path, file_name)
            continue
        
        # Navigate to class methods
        navigate_class(selected_key, selected_value, current_breadcrumb, file_path)

def navigate_class(class_name, class_data, breadcrumb="", file_path=""):
    """Navigate through a test class."""
    current_breadcrumb = f"{breadcrumb} > {class_name}"
    methods = class_data.get('methods', [])
    
    while True:
        items = [(method, method) for method in methods]
        
        selected_key, selected_value = display_menu(
            items,
            f"Test Class: {class_name}",
            current_breadcrumb,
            show_back=True,
            show_run_all=True
        )
        
        if selected_key == '__back__':
            return
        elif selected_key == '__run_all__':
            # Run entire class
            test_path = f"{file_path}::{class_name}"
            run_tests(test_path, f"{class_name}")
            continue
        
        # Run individual method
        test_path = f"{file_path}::{class_name}::{selected_key}"
        run_tests(test_path, f"{class_name}::{selected_key}")

def main():
    """Main interactive test runner."""
    print(f"{Colors.CYAN}Building test hierarchy...{Colors.ENDC}")
    hierarchy = build_test_hierarchy()
    print(f"{Colors.GREEN}✓ Test hierarchy built{Colors.ENDC}\n")
    
    while True:
        # Main menu - select test suite
        items = [
            ('integration', hierarchy['integration']),
            ('e2e', hierarchy['e2e'])
        ]
        
        selected_key, selected_value = display_menu(
            items,
            "Select Test Suite",
            "",
            show_back=False,
            show_run_all=False
        )
        
        if selected_key in ['integration', 'e2e']:
            navigate_suite(selected_key, selected_value)
        else:
            break

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Exiting...{Colors.ENDC}")
        sys.exit(0)

