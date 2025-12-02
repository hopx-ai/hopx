#!/usr/bin/env python3
"""
Interactive Test Runner
Allows hierarchical selection and execution of tests.

Optional dependency: Install 'readchar' for arrow key navigation support:
    pip install readchar

Without readchar, the script will fall back to number-based selection.
"""

import ast
import os
import subprocess
import sys
import hashlib
from pathlib import Path
from collections import defaultdict

# Try to import readchar for arrow key support
try:
    import readchar  # type: ignore
    READCHAR_AVAILABLE = True
except ImportError:
    READCHAR_AVAILABLE = False
    readchar = None

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
                    # Check for both regular and async test methods
                    if (isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) 
                        and item.name.startswith('test_')):
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

def display_menu(items, title, breadcrumb="", show_back=True, show_run_all=False, settings=None, show_generate_manifest=False):
    """Display a menu and return selected item."""
    clear_screen()
    
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{title:^60}{Colors.ENDC}")
    if breadcrumb:
        print(f"{Colors.CYAN}Location: {breadcrumb}{Colors.ENDC}")
    
    # Display settings status if provided
    if settings:
        verbose_status = f"{Colors.GREEN}● ON{Colors.ENDC}" if settings['verbose'] else f"{Colors.RED}○ OFF{Colors.ENDC}"
        reports_status = f"{Colors.GREEN}● ON{Colors.ENDC}" if settings['generate_reports'] else f"{Colors.RED}○ OFF{Colors.ENDC}"
        print(f"{Colors.YELLOW}Settings: Verbose {verbose_status} | Reports {reports_status} | Press 'v' to toggle verbose, 'r' to toggle reports{Colors.ENDC}")
    
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")
    
    # Build menu_items list (same as items, but we need it for indexing)
    menu_items = list(items)
    selected_index = 0  # Track currently selected item
    
    # Build help text
    help_parts = []
    if READCHAR_AVAILABLE:
        help_parts.append("↑↓ arrows to navigate")
    if show_run_all:
        help_parts.append("'a' for all")
    if show_back:
        help_parts.append("'b' for back")
    if show_generate_manifest:
        help_parts.append("'m' for manifest")
    if settings:
        help_parts.append("'v' for verbose")
        help_parts.append("'r' for reports")
    if items and not READCHAR_AVAILABLE:
        help_parts.append(f"1-{len(items)} for items")
    if READCHAR_AVAILABLE and items:
        help_parts.append("Enter to select")
    
    help_text = " | ".join(help_parts)
    
    def redisplay_menu():
        """Redisplay menu with current selection highlighted."""
        clear_screen()
        print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{title:^60}{Colors.ENDC}")
        if breadcrumb:
            print(f"{Colors.CYAN}Location: {breadcrumb}{Colors.ENDC}")
        
        # Display settings status if provided
        if settings:
            verbose_status = f"{Colors.GREEN}● ON{Colors.ENDC}" if settings['verbose'] else f"{Colors.RED}○ OFF{Colors.ENDC}"
            reports_status = f"{Colors.GREEN}● ON{Colors.ENDC}" if settings['generate_reports'] else f"{Colors.RED}○ OFF{Colors.ENDC}"
            print(f"{Colors.YELLOW}Settings: Verbose {verbose_status} | Reports {reports_status} | Press 'v' to toggle verbose, 'r' to toggle reports{Colors.ENDC}")
        
        print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")
        
        # Display special options first
        if show_run_all:
            print(f"{Colors.GREEN}[a] Run All Tests{Colors.ENDC}")
        
        if show_generate_manifest:
            print(f"{Colors.CYAN}[m] Generate Manifest{Colors.ENDC}")
        
        if show_back:
            print(f"{Colors.YELLOW}[b] ← Back{Colors.ENDC}")
        
        if show_run_all or show_back or show_generate_manifest:
            print()
        
        # Display items with highlighting
        index = 1
        for i, (key, value) in enumerate(items):
            is_selected = (i == selected_index) and READCHAR_AVAILABLE
            prefix = f"{Colors.BOLD}{Colors.GREEN}▶ {Colors.ENDC}" if is_selected else "  "
            
            if isinstance(value, dict):
                if value.get('_type') == 'file':
                    file_name = key
                    classes = value.get('_classes', [])
                    class_count = len(classes)
                    method_count = sum(len(c['methods']) for c in classes)
                    print(f"{prefix}{Colors.BLUE}[{index}] {file_name}{Colors.ENDC} ({class_count} classes, {method_count} methods)")
                elif value.get('_type') == 'category':
                    print(f"{prefix}{Colors.CYAN}[{index}] {key}/ {Colors.ENDC}→")
                else:
                    print(f"{prefix}{Colors.CYAN}[{index}] {key}/ {Colors.ENDC}→")
            else:
                print(f"{prefix}{Colors.BLUE}[{index}] {key}{Colors.ENDC}")
            
            index += 1
        
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
        print(f"{Colors.CYAN}{help_text}{Colors.ENDC}")
    
    # Initial display
    redisplay_menu()
    
    while True:
        try:
            if READCHAR_AVAILABLE:
                # Use readchar for arrow key support
                key = readchar.readkey()
                
                # Handle arrow keys
                if key == readchar.key.UP:
                    if selected_index > 0:
                        selected_index -= 1
                        redisplay_menu()
                    continue
                elif key == readchar.key.DOWN:
                    if selected_index < len(items) - 1:
                        selected_index += 1
                        redisplay_menu()
                    continue
                elif key == readchar.key.ENTER or key == '\r' or key == '\n':
                    # Select current item
                    if items:
                        return menu_items[selected_index]
                    continue
                else:
                    choice = key.lower()
            else:
                # Fallback to input() for systems without readchar
                choice = input(f"\n{Colors.BOLD}Select option ({help_text}): {Colors.ENDC}").strip().lower()
            
            # Handle settings toggles
            if settings:
                if choice == 'v':
                    settings['verbose'] = not settings['verbose']
                    verbose_status = f"{Colors.GREEN}● ON{Colors.ENDC}" if settings['verbose'] else f"{Colors.RED}○ OFF{Colors.ENDC}"
                    if READCHAR_AVAILABLE:
                        redisplay_menu()
                        continue
                    else:
                        print(f"{Colors.CYAN}✓ Verbose: {verbose_status}{Colors.ENDC}")
                        input(f"{Colors.YELLOW}Press Enter to continue...{Colors.ENDC}")
                        return ('__settings_changed__', None)
                elif choice == 'r':
                    settings['generate_reports'] = not settings['generate_reports']
                    reports_status = f"{Colors.GREEN}● ON{Colors.ENDC}" if settings['generate_reports'] else f"{Colors.RED}○ OFF{Colors.ENDC}"
                    if READCHAR_AVAILABLE:
                        redisplay_menu()
                        continue
                    else:
                        print(f"{Colors.CYAN}✓ Reports: {reports_status}{Colors.ENDC}")
                        input(f"{Colors.YELLOW}Press Enter to continue...{Colors.ENDC}")
                        return ('__settings_changed__', None)
            
            # Handle special options
            if choice == 'a' and show_run_all:
                return ('__run_all__', 'Run All Tests')
            if choice == 'm' and show_generate_manifest:
                return ('__generate_manifest__', 'Generate Manifest')
            if choice == 'b' and show_back:
                return ('__back__', 'Back')
            
            # Handle numbered options (fallback when readchar not available)
            if not READCHAR_AVAILABLE:
                try:
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(items):
                        return menu_items[choice_num - 1]
                    else:
                        print(f"{Colors.RED}Invalid option. Please select 1-{len(items)}.{Colors.ENDC}")
                except ValueError:
                    print(f"{Colors.RED}Invalid input. Please enter a number (1-{len(items)}) or letter (a/b/v/r).{Colors.ENDC}")
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Exiting...{Colors.ENDC}")
            sys.exit(0)


def update_manifest(script_dir, python_dir):
    """
    Update the test reports manifest after a test run.
    
    Args:
        script_dir: Path to the tests directory
        python_dir: Path to the python directory (for running the script)
    
    Returns:
        bool: True if manifest was updated successfully, False otherwise
    """
    try:
        manifest_script = script_dir / 'reports' / 'generate_manifest.py'
        if not manifest_script.exists():
            print(f"{Colors.YELLOW}⚠ Manifest script not found at {manifest_script}{Colors.ENDC}")
            return False
        
        print(f"{Colors.CYAN}Updating test reports manifest...{Colors.ENDC}")
        manifest_result = subprocess.run(
            [sys.executable, str(manifest_script)], 
            cwd=python_dir, 
            capture_output=True,
            text=True,
            check=False
        )
        
        if manifest_result.returncode == 0:
            # Show success message from the script if available
            if manifest_result.stdout.strip():
                print(f"{Colors.GREEN}{manifest_result.stdout.strip()}{Colors.ENDC}")
            else:
                print(f"{Colors.GREEN}✓ Manifest updated successfully{Colors.ENDC}")
            return True
        else:
            # Show error if manifest generation failed
            error_msg = manifest_result.stderr.strip() or manifest_result.stdout.strip()
            if error_msg:
                print(f"{Colors.YELLOW}⚠ Manifest update warning: {error_msg}{Colors.ENDC}")
            else:
                print(f"{Colors.YELLOW}⚠ Manifest update completed with warnings{Colors.ENDC}")
            return False
    except Exception as e:
        print(f"{Colors.YELLOW}⚠ Failed to update manifest: {str(e)}{Colors.ENDC}")
        return False

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

def run_tests(test_path, test_name="", settings=None):
    """Run tests and display results."""
    if settings is None:
        settings = {'verbose': True, 'generate_reports': False}
    
    verbose = settings['verbose']
    generate_reports = settings['generate_reports']
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
        
        # Auto-generate manifest.json for index.html after test run
        if generate_reports:
            update_manifest(script_dir, python_dir)
            print()  # Add blank line after manifest update message
        
        input(f"{Colors.YELLOW}Press Enter to continue...{Colors.ENDC}")
        return result.returncode == 0
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Test execution interrupted.{Colors.ENDC}")
        
        # Still update manifest if reports were being generated
        if generate_reports:
            update_manifest(script_dir, python_dir)
            print()
        
        input(f"{Colors.YELLOW}Press Enter to continue...{Colors.ENDC}")
        return False

def navigate_suite(suite_name, suite_data, settings, breadcrumb=""):
    """Navigate through a test suite."""
    # Get directories for manifest updates
    script_dir = Path(__file__).parent.resolve()
    python_dir = script_dir.parent
    
    current_breadcrumb = f"{breadcrumb} > {suite_name}" if breadcrumb else suite_name
    
    while True:
        # Filter out internal metadata keys (starting with _)
        items = [(k, v) for k, v in suite_data.items() if not k.startswith('_')]
        selected_key, selected_value = display_menu(
            items,
            f"Test Suite: {suite_name.upper()}",
            current_breadcrumb,
            show_back=bool(breadcrumb),
            show_run_all=True,
            settings=settings,
            show_generate_manifest=True
        )
        
        if selected_key == '__generate_manifest__':
            update_manifest(script_dir, python_dir)
            input(f"{Colors.YELLOW}Press Enter to continue...{Colors.ENDC}")
            continue
        
        if selected_key == '__settings_changed__':
            continue  # Redisplay menu after settings change
        elif selected_key == '__back__':
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
                run_tests(' '.join(test_paths), f"All {suite_name} tests", settings)
            continue
        
        # Navigate deeper
        if isinstance(selected_value, dict):
            if selected_value.get('_type') == 'file':
                navigate_file(selected_key, selected_value, settings, current_breadcrumb)
            elif selected_value.get('_type') == 'category':
                navigate_category(selected_key, selected_value, settings, current_breadcrumb)
            else:
                navigate_category(selected_key, selected_value, settings, current_breadcrumb)

def navigate_category(category_name, category_data, settings, breadcrumb=""):
    """Navigate through a category."""
    # Get directories for manifest updates
    script_dir = Path(__file__).parent.resolve()
    python_dir = script_dir.parent
    
    current_breadcrumb = f"{breadcrumb} > {category_name}"
    
    while True:
        # Filter out internal metadata keys (starting with _)
        items = [(k, v) for k, v in category_data.items() if not k.startswith('_')]
        selected_key, selected_value = display_menu(
            items,
            f"Category: {category_name}",
            current_breadcrumb,
            show_back=True,
            show_run_all=True,
            settings=settings,
            show_generate_manifest=True
        )
        
        if selected_key == '__generate_manifest__':
            update_manifest(script_dir, python_dir)
            input(f"{Colors.YELLOW}Press Enter to continue...{Colors.ENDC}")
            continue
        
        if selected_key == '__settings_changed__':
            continue  # Redisplay menu after settings change
        elif selected_key == '__back__':
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
                run_tests(' '.join(test_paths), f"All {category_name} tests", settings)
            continue
        
        if isinstance(selected_value, dict):
            if selected_value.get('_type') == 'file':
                navigate_file(selected_key, selected_value, settings, current_breadcrumb)
            else:
                navigate_category(selected_key, selected_value, settings, current_breadcrumb)

def navigate_file(file_name, file_data, settings, breadcrumb=""):
    """Navigate through a test file."""
    # Get directories for manifest updates
    script_dir = Path(__file__).parent.resolve()
    python_dir = script_dir.parent
    
    current_breadcrumb = f"{breadcrumb} > {file_name}"
    file_path = file_data['_path']
    classes = file_data.get('_classes', [])
    
    while True:
        items = []
        for cls in classes:
            items.append((cls['name'], cls))
        
        if not items:
            # No classes, just run the file
            run_tests(file_path, file_name, settings)
            return
        
        selected_key, selected_value = display_menu(
            items,
            f"Test File: {file_name}",
            current_breadcrumb,
            show_back=True,
            show_run_all=True,
            settings=settings,
            show_generate_manifest=True
        )
        
        if selected_key == '__generate_manifest__':
            update_manifest(script_dir, python_dir)
            input(f"{Colors.YELLOW}Press Enter to continue...{Colors.ENDC}")
            continue
        
        if selected_key == '__settings_changed__':
            continue  # Redisplay menu after settings change
        elif selected_key == '__back__':
            return
        elif selected_key == '__run_all__':
            run_tests(file_path, file_name, settings)
            continue
        
        # Navigate to class methods
        navigate_class(selected_key, selected_value, settings, current_breadcrumb, file_path)

def navigate_class(class_name, class_data, settings, breadcrumb="", file_path=""):
    """Navigate through a test class."""
    # Get directories for manifest updates
    script_dir = Path(__file__).parent.resolve()
    python_dir = script_dir.parent
    
    current_breadcrumb = f"{breadcrumb} > {class_name}"
    methods = class_data.get('methods', [])
    
    while True:
        items = [(method, method) for method in methods]
        
        selected_key, selected_value = display_menu(
            items,
            f"Test Class: {class_name}",
            current_breadcrumb,
            show_back=True,
            show_run_all=True,
            settings=settings,
            show_generate_manifest=True
        )
        
        if selected_key == '__generate_manifest__':
            update_manifest(script_dir, python_dir)
            input(f"{Colors.YELLOW}Press Enter to continue...{Colors.ENDC}")
            continue
        
        if selected_key == '__settings_changed__':
            continue  # Redisplay menu after settings change
        elif selected_key == '__back__':
            return
        elif selected_key == '__run_all__':
            # Run entire class
            test_path = f"{file_path}::{class_name}"
            run_tests(test_path, f"{class_name}", settings)
            continue
        
        # Run individual method
        test_path = f"{file_path}::{class_name}::{selected_key}"
        run_tests(test_path, f"{class_name}::{selected_key}", settings)

def main():
    """Main interactive test runner."""
    # Initialize settings with defaults
    settings = {
        'verbose': True,
        'generate_reports': False
    }
    
    print(f"{Colors.CYAN}Building test hierarchy...{Colors.ENDC}")
    hierarchy = build_test_hierarchy()
    print(f"{Colors.GREEN}✓ Test hierarchy built{Colors.ENDC}\n")
    
    # Get directories for manifest updates
    script_dir = Path(__file__).parent.resolve()
    python_dir = script_dir.parent
    
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
            show_run_all=False,
            settings=settings,
            show_generate_manifest=True
        )
        
        if selected_key == '__settings_changed__':
            continue  # Redisplay menu after settings change
        elif selected_key == '__generate_manifest__':
            update_manifest(script_dir, python_dir)
            input(f"{Colors.YELLOW}Press Enter to continue...{Colors.ENDC}")
            continue
        elif selected_key in ['integration', 'e2e']:
            navigate_suite(selected_key, selected_value, settings)
        else:
            break

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Exiting...{Colors.ENDC}")
        sys.exit(0)

