"""
Code Execution with Rich Output

Execute code with automatic rich output capture:
- Run Python code
- Capture matplotlib plots
- Capture pandas DataFrames
- Work with execution results
"""

from hopx_ai import Sandbox
import base64

def main():
    print("Code Execution with Rich Output\n")
    
    # Create sandbox
    print("1. Creating sandbox...")
    sandbox = Sandbox.create(template="code-interpreter")
    print(f"Sandbox created: {sandbox.sandbox_id}\n")

    try:
        # Simple code execution
        print("2. Running simple Python code...")
        result = sandbox.run_code('print("Hello from Python!")')
        print(f"Output: {result.stdout.strip()}")
        print(f"   Execution time: {result.execution_time:.3f}s")
        print(f"   Success: {result.success}\n")
        
        # Code with variables
        print("3. Running code with calculations...")
        code = """
x = 42
y = 58
total = x + y
print(f"The answer is: {total}")
"""
        result = sandbox.run_code(code)
        print(f"Output: {result.stdout.strip()}\n")
        
        # Code with matplotlib plot
        print("4. Generating matplotlib plot...")
        plot_code = """
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np

# Generate data
x = np.linspace(0, 10, 100)
y = np.sin(x)

# Create plot
plt.figure(figsize=(10, 6))
plt.plot(x, y, 'b-', linewidth=2, label='sin(x)')
plt.xlabel('X')
plt.ylabel('Y')
plt.title('Sine Wave')
plt.legend()
plt.grid(True)

# Save plot
plt.savefig('/workspace/sine_wave.png', dpi=100, bbox_inches='tight')
print("Plot saved!")
"""
        result = sandbox.run_code(plot_code)
        print(f"Stdout: {result.stdout.strip()}")
        print(f"   Rich outputs: {result.rich_count}")

        if result.rich_outputs:
            for i, output in enumerate(result.rich_outputs):
                print(f"   Output {i+1}: {output.type}")
                if output.metadata:
                    print(f"      Metadata: {output.metadata}")
        print()

        # Download the plot
        if result.rich_count > 0:
            print("5. Downloading generated plot...")
            sandbox.files.download('/workspace/sine_wave.png', '/tmp/sine_wave.png')
            print("Plot saved to /tmp/sine_wave.png\n")
        
        # Code with pandas DataFrame
        print("6. Creating pandas DataFrame...")
        pandas_code = """
import pandas as pd

# Create DataFrame
data = {
    'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
    'Age': [25, 30, 35, 28, 32],
    'City': ['New York', 'San Francisco', 'Seattle', 'Boston', 'Austin'],
    'Salary': [70000, 80000, 90000, 75000, 85000]
}

df = pd.DataFrame(data)
print(df)
print()
print(f"Average age: {df['Age'].mean():.1f}")
print(f"Average salary: ${df['Salary'].mean():,.0f}")

# Save to CSV
df.to_csv('/workspace/employees.csv', index=False)
print("\\nDataFrame saved to CSV!")
"""
        result = sandbox.run_code(pandas_code)
        print(f"Output:\n{result.stdout}")
        print(f"   Execution time: {result.execution_time:.3f}s\n")
        
        # Code with error handling
        print("7. Running code with intentional error...")
        error_code = """
x = 10
y = 0
result = x / y  # This will cause ZeroDivisionError
"""
        result = sandbox.run_code(error_code)
        print(f"   Success: {result.success}")
        print(f"   Exit code: {result.exit_code}")
        if result.stderr:
            print(f"   Error preview: {result.stderr[:100]}...\n")

        # JavaScript code
        print("8. Running JavaScript code...")
        js_code = """
const numbers = [1, 2, 3, 4, 5];
const sum = numbers.reduce((a, b) => a + b, 0);
console.log(`Sum: ${sum}`);
console.log(`Average: ${sum / numbers.length}`);
"""
        result = sandbox.run_code(js_code, language='javascript')
        print(f"JavaScript output:\n{result.stdout}\n")

        # Bash code
        print("9. Running Bash script...")
        bash_code = """
echo "System Information:"
echo "=================="
echo "Hostname: $(hostname)"
echo "Kernel: $(uname -r)"
echo "CPU cores: $(nproc)"
echo "Memory: $(free -h | grep Mem | awk '{print $2}')"
"""
        result = sandbox.run_code(bash_code, language='bash')
        print(f"Bash output:\n{result.stdout}")

        # Complex data analysis
        print("10. Running data analysis with multiple plots...")
        analysis_code = """
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Read the employees data
df = pd.read_csv('/workspace/employees.csv')

# Create figure with subplots
fig, axes = plt.subplots(2, 2, figsize=(12, 10))
fig.suptitle('Employee Data Analysis', fontsize=16)

# Age distribution
axes[0, 0].hist(df['Age'], bins=5, edgecolor='black')
axes[0, 0].set_title('Age Distribution')
axes[0, 0].set_xlabel('Age')
axes[0, 0].set_ylabel('Count')

# Salary by person
axes[0, 1].bar(df['Name'], df['Salary'])
axes[0, 1].set_title('Salary by Employee')
axes[0, 1].set_xlabel('Name')
axes[0, 1].set_ylabel('Salary ($)')
axes[0, 1].tick_params(axis='x', rotation=45)

# Age vs Salary scatter
axes[1, 0].scatter(df['Age'], df['Salary'], s=100, alpha=0.6)
axes[1, 0].set_title('Age vs Salary')
axes[1, 0].set_xlabel('Age')
axes[1, 0].set_ylabel('Salary ($)')

# City distribution
city_counts = df['City'].value_counts()
axes[1, 1].pie(city_counts.values, labels=city_counts.index, autopct='%1.1f%%')
axes[1, 1].set_title('Employees by City')

plt.tight_layout()
plt.savefig('/workspace/analysis.png', dpi=150, bbox_inches='tight')
print("✅ Analysis complete! Plot saved.")
print(f"   Total employees: {len(df)}")
print(f"   Average salary: ${df['Salary'].mean():,.0f}")
print(f"   Salary range: ${df['Salary'].min():,} - ${df['Salary'].max():,}")
"""
        result = sandbox.run_code(analysis_code)
        print(f"\nAnalysis output:\n{result.stdout}")
        print(f"   Rich outputs: {result.rich_count}\n")

        print("All code execution examples completed")

    finally:
        # Cleanup
        print("\nCleaning up...")
        sandbox.kill()
        print("Sandbox destroyed")


if __name__ == "__main__":
    main()

