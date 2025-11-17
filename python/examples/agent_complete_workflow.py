"""
Complete Agent Workflow

Automate a complete data science workflow:
- Upload datasets
- Install packages
- Analyze data
- Generate visualizations
- Create reports
- Download results
"""

from hopx_ai import Sandbox

def main():
    print("Complete Agent Workflow")
    print("=" * 60)
    print("Running data science workflow:\n")
    
    # Create sandbox with context manager (auto-cleanup)
    with Sandbox.create(template="code-interpreter") as sandbox:
        print(f"✅ Sandbox created: {sandbox.sandbox_id}")
        info = sandbox.get_info()
        print(f"   Status: {info.status}")
        print(f"   Agent URL: {info.public_host}")
        print(f"   Resources: {info.resources.vcpu if info.resources else '?'} vCPU\n")
        
        # Step 1: Upload dataset
        print("Step 1: Preparing dataset...")
        dataset = """date,temperature,humidity,rainfall
2024-01-01,22.5,65,0
2024-01-02,24.0,70,5
2024-01-03,21.5,68,12
2024-01-04,23.0,72,8
2024-01-05,25.5,60,0
2024-01-06,26.0,55,0
2024-01-07,24.5,58,3"""
        
        sandbox.files.write('/workspace/weather.csv', dataset)
        print("Dataset uploaded to /workspace/weather.csv\n")

        # Step 2: Install required packages
        print("Step 2: Installing packages...")
        result = sandbox.commands.run('pip3 install pandas matplotlib seaborn --quiet', timeout=60)
        if result.success:
            print("Packages installed\n")
        else:
            print(f"Warning: {result.stderr[:100]}\n")

        # Step 3: Data analysis
        print("Step 3: Running data analysis...")
        analysis_code = """
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

# Load data
df = pd.read_csv('/workspace/weather.csv')
print("Dataset loaded successfully!")
print(f"Shape: {df.shape}")
print()
print("First few rows:")
print(df.head())
print()

# Statistics
print("Summary Statistics:")
print(df.describe())
print()

# Analysis
print("Analysis Results:")
print(f"Average temperature: {df['temperature'].mean():.1f}°C")
print(f"Average humidity: {df['humidity'].mean():.1f}%")
print(f"Total rainfall: {df['rainfall'].sum():.1f}mm")
print(f"Days with rain: {(df['rainfall'] > 0).sum()}")
"""
        
        result = sandbox.run_code(analysis_code)
        print(result.stdout)

        # Step 4: Create visualizations
        print("Step 4: Generating visualizations...")
        viz_code = """
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

# Set style
sns.set_style('whitegrid')

# Load data
df = pd.read_csv('/workspace/weather.csv')

# Create figure with subplots
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Weather Data Analysis', fontsize=16, fontweight='bold')

# Temperature over time
axes[0, 0].plot(df.index, df['temperature'], marker='o', linewidth=2, markersize=8)
axes[0, 0].set_title('Temperature Trend')
axes[0, 0].set_xlabel('Day')
axes[0, 0].set_ylabel('Temperature (°C)')
axes[0, 0].grid(True, alpha=0.3)

# Humidity over time
axes[0, 1].plot(df.index, df['humidity'], marker='s', color='green', linewidth=2, markersize=8)
axes[0, 1].set_title('Humidity Trend')
axes[0, 1].set_xlabel('Day')
axes[0, 1].set_ylabel('Humidity (%)')
axes[0, 1].grid(True, alpha=0.3)

# Rainfall bar chart
axes[1, 0].bar(df.index, df['rainfall'], color='blue', alpha=0.7)
axes[1, 0].set_title('Daily Rainfall')
axes[1, 0].set_xlabel('Day')
axes[1, 0].set_ylabel('Rainfall (mm)')
axes[1, 0].grid(True, alpha=0.3)

# Correlation heatmap
correlation = df[['temperature', 'humidity', 'rainfall']].corr()
sns.heatmap(correlation, annot=True, fmt='.2f', cmap='coolwarm', ax=axes[1, 1])
axes[1, 1].set_title('Correlation Matrix')

plt.tight_layout()
plt.savefig('/workspace/weather_analysis.png', dpi=150, bbox_inches='tight')
print("Visualization saved")
"""

        result = sandbox.run_code(viz_code)
        print(result.stdout)
        print(f"   Rich outputs captured: {result.rich_count}\n")

        # Step 5: Generate report
        print("Step 5: Generating report...")
        report_code = """
import pandas as pd

df = pd.read_csv('/workspace/weather.csv')

# Generate report
report = f'''
WEATHER ANALYSIS REPORT
{'=' * 50}

Dataset Information:
- Period: {df['date'].min()} to {df['date'].max()}
- Total days: {len(df)}

Key Findings:
- Average Temperature: {df['temperature'].mean():.1f}°C
- Temperature Range: {df['temperature'].min():.1f}°C - {df['temperature'].max():.1f}°C
- Average Humidity: {df['humidity'].mean():.1f}%
- Total Rainfall: {df['rainfall'].sum():.1f}mm
- Rainy Days: {(df['rainfall'] > 0).sum()} out of {len(df)} days

Correlations:
- Temperature vs Humidity: {df['temperature'].corr(df['humidity']):.3f}
- Temperature vs Rainfall: {df['temperature'].corr(df['rainfall']):.3f}
- Humidity vs Rainfall: {df['humidity'].corr(df['rainfall']):.3f}

Conclusion:
The data shows {'stable' if df['temperature'].std() < 2 else 'variable'} temperature patterns
with {'low' if df['humidity'].mean() < 60 else 'moderate' if df['humidity'].mean() < 70 else 'high'} humidity levels.
'''

# Save report
with open('/workspace/report.txt', 'w') as f:
    f.write(report)

print(report)
"""
        
        result = sandbox.run_code(report_code)
        print(result.stdout)

        # Step 6: List all generated files
        print("Step 6: Listing generated files...")
        files = sandbox.files.list('/workspace')
        print(f"Found {len(files)} files:")
        for f in files:
            if f.is_file:
                print(f"   📄 {f.name} ({f.size_kb:.2f} KB)")
        print()
        
        # Step 7: Download results
        print("Step 7: Downloading results...")
        downloads = [
            ('/workspace/weather_analysis.png', '/tmp/weather_analysis.png'),
            ('/workspace/report.txt', '/tmp/weather_report.txt'),
        ]

        for remote, local in downloads:
            try:
                sandbox.files.download(remote, local)
                print(f"Downloaded: {remote} -> {local}")
            except Exception as e:
                print(f"Failed to download {remote}: {e}")
        print()

        # Step 8: Final verification
        print("Step 8: Verification...")
        result = sandbox.commands.run('ls -lh /workspace')
        print("Final workspace contents:")
        print(result.stdout)

        print("\n" + "=" * 60)
        print("Workflow complete")
        print("=" * 60)
        print("\nGenerated files:")
        print("  - /tmp/weather_analysis.png (visualization)")
        print("  - /tmp/weather_report.txt (analysis report)")
        print("\nView these files on your local system.")

    # Context manager automatically calls sandbox.kill()
    print("\nSandbox cleaned up")


if __name__ == "__main__":
    main()

