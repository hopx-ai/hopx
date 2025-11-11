#!/usr/bin/env python3
"""
HOPX.AI Python SDK - Rich Outputs Demo (Matplotlib, Pandas, Plotly)

This example demonstrates Jupyter's automatic rich output capture:
- Matplotlib plots → PNG images (base64)
- Pandas DataFrames → HTML tables
- Plotly charts → Interactive HTML/JSON

Agent automatically captures these outputs via Jupyter kernel!
"""

import os
from hopx_ai import Sandbox

API_KEY = os.environ.get('HOPX_API_KEY', 'your-api-key-here')
if API_KEY == 'your-api-key-here':
    raise ValueError("HOPX_API_KEY environment variable not set")


def matplotlib_plot_demo():
    """Matplotlib PNG capture via Jupyter"""
    print("=" * 60)
    print("1. MATPLOTLIB PNG CAPTURE")
    print("=" * 60)
    
    with Sandbox.create(template='code-interpreter', api_key=API_KEY) as sandbox:
        code = '''
import matplotlib.pyplot as plt
import numpy as np

# Create sine wave plot
x = np.linspace(0, 10, 100)
y = np.sin(x)

plt.figure(figsize=(8, 5))
plt.plot(x, y, 'b-', linewidth=2, label='sin(x)')
plt.title('Sine Wave')
plt.xlabel('X')
plt.ylabel('sin(X)')
plt.grid(True, alpha=0.3)
plt.legend()
plt.savefig('/workspace/sine.png')
plt.show()

print("Plot created")
'''
        
        result = sandbox.run_code(code, language='python', timeout=30)
        
        print(f"✅ Success: {result.success}")
        print(f"⏱️  Execution time: {result.execution_time:.2f}s")
        print(f"📊 Rich outputs: {result.rich_count}")
        
        if result.rich_outputs:
            for i, output in enumerate(result.rich_outputs, 1):
                print(f"   Output {i}: {output.type}")
                if output.type == 'image/png':
                    png_size = len(output.data.get('image/png', ''))
                    print(f"   → PNG size: {png_size / 1024:.1f} KB")
        
        print(f"📝 stdout: {result.stdout.strip()}")
        print()


def pandas_dataframe_demo():
    """Pandas DataFrame HTML table capture"""
    print("=" * 60)
    print("2. PANDAS HTML TABLE CAPTURE")
    print("=" * 60)
    
    with Sandbox.create(template='code-interpreter', api_key=API_KEY) as sandbox:
        code = '''
import pandas as pd
import numpy as np

# Create sample DataFrame
np.random.seed(42)
df = pd.DataFrame({
    "Name": ["Alice", "Bob", "Charlie", "David", "Eve"],
    "Age": [25, 30, 35, 40, 28],
    "City": ["NYC", "LA", "Chicago", "Boston", "Seattle"],
    "Salary": [50000, 60000, 70000, 80000, 55000]
})

print("DataFrame created")
df  # Display triggers HTML rendering
'''
        
        result = sandbox.run_code(code, language='python', timeout=30)
        
        print(f"✅ Success: {result.success}")
        print(f"⏱️  Execution time: {result.execution_time:.2f}s")
        print(f"📊 Rich outputs: {result.rich_count}")
        
        if result.rich_outputs:
            for i, output in enumerate(result.rich_outputs, 1):
                print(f"   Output {i}: {output.type}")
                if output.type == 'text/html':
                    html_size = len(output.data.get('text/html', ''))
                    print(f"   → HTML size: {html_size / 1024:.1f} KB")
                    # Preview first 100 chars
                    html_preview = output.data.get('text/html', '')[:100]
                    print(f"   → Preview: {html_preview}...")
        
        print(f"📝 stdout: {result.stdout.strip()}")
        print()


def plotly_chart_demo():
    """Plotly interactive chart capture"""
    print("=" * 60)
    print("3. PLOTLY INTERACTIVE CHART")
    print("=" * 60)
    
    with Sandbox.create(template='code-interpreter', api_key=API_KEY) as sandbox:
        code = '''
import plotly.graph_objects as go
import numpy as np

# Create quadratic function chart
x = np.linspace(0, 10, 50)
y = x ** 2

fig = go.Figure()
fig.add_trace(go.Scatter(x=x, y=y, mode='markers+lines', name='x^2'))
fig.update_layout(
    title='Quadratic Function',
    xaxis_title='X',
    yaxis_title='Y'
)
fig.show()

print("Chart created")
'''
        
        result = sandbox.run_code(code, language='python', timeout=30)
        
        print(f"✅ Success: {result.success}")
        print(f"⏱️  Execution time: {result.execution_time:.2f}s")
        print(f"📊 Rich outputs: {result.rich_count}")
        
        if result.rich_outputs:
            for i, output in enumerate(result.rich_outputs, 1):
                print(f"   Output {i}: {output.type}")
                if 'html' in output.type:
                    html_size = len(output.data.get(output.type, ''))
                    print(f"   → HTML size: {html_size / 1024:.1f} KB")
                elif 'json' in output.type:
                    json_size = len(str(output.data.get(output.type, '')))
                    print(f"   → JSON size: {json_size / 1024:.1f} KB")
        
        print(f"📝 stdout: {result.stdout.strip()}")
        print()


def multiple_outputs_demo():
    """Multiple outputs in single execution"""
    print("=" * 60)
    print("4. MULTIPLE OUTPUTS IN ONE EXECUTION")
    print("=" * 60)
    
    with Sandbox.create(template='code-interpreter', api_key=API_KEY) as sandbox:
        code = '''
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# 1. DataFrame
df = pd.DataFrame({
    "X": [1, 2, 3, 4, 5],
    "Y": [1, 4, 9, 16, 25]
})
print("DataFrame:")
display(df)

# 2. Plot
plt.figure(figsize=(6, 4))
plt.plot(df["X"], df["Y"], 'ro-')
plt.title('X vs Y')
plt.show()

print("\\nBoth outputs generated!")
'''
        
        result = sandbox.run_code(code, language='python', timeout=30)
        
        print(f"✅ Success: {result.success}")
        print(f"⏱️  Execution time: {result.execution_time:.2f}s")
        print(f"📊 Rich outputs: {result.rich_count}")
        
        if result.rich_outputs:
            print(f"   → Captured {len(result.rich_outputs)} outputs:")
            for i, output in enumerate(result.rich_outputs, 1):
                print(f"      {i}. {output.type}")
        
        print(f"📝 stdout:\n{result.stdout}")
        print()


def main():
    print("\n" + "=" * 60)
    print("PYTHON SDK - RICH OUTPUTS DEMO (JUPYTER)")
    print("=" * 60)
    print()
    
    print("ℹ️  Agent automatically captures rich outputs via Jupyter:")
    print("   • Matplotlib → PNG (base64)")
    print("   • Pandas → HTML tables")
    print("   • Plotly → Interactive HTML/JSON")
    print()
    
    try:
        matplotlib_plot_demo()
        pandas_dataframe_demo()
        plotly_chart_demo()
        multiple_outputs_demo()
        
        print("=" * 60)
        print("✅ ALL RICH OUTPUT DEMOS COMPLETED!")
        print("=" * 60)
        print()
        print("💡 Key Points:")
        print("   • No special flags needed - Jupyter is automatic")
        print("   • Access via result.rich_outputs[]")
        print("   • Each output has .type and .data")
        print("   • Supports PNG, HTML, JSON, and more")
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

