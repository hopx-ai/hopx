"""
09. Advanced Use Cases - Python SDK

Real-world examples for production use:
- Data analysis pipeline
- API testing framework
- Report generation
- ML model training
- Multi-step workflows
- Error recovery patterns
- Performance optimization
"""

from hopx_ai import Sandbox
import os
import json

API_KEY = os.getenv("HOPX_API_KEY", "your-api-key-here")

def ensure_workspace(sandbox):
    """Create /workspace directory if it doesn't exist"""
    try:
        sandbox.run_code("import os; os.makedirs('/workspace', exist_ok=True)")
    except Exception:
        pass



def data_analysis_pipeline():
    """Complete data analysis workflow"""
    print("=" * 60)
    print("1. DATA ANALYSIS PIPELINE")
    print("=" * 60)
    
    with Sandbox.create(template="code-interpreter", api_key=API_KEY) as sandbox:
        ensure_workspace(sandbox)
        # Step 1: Upload data
        print("✅ Step 1: Upload data")
        sandbox.files.write("/workspace/data.csv", """
name,age,score
Alice,25,95
Bob,30,87
Charlie,35,92
Diana,28,98
Eve,32,89
        """.strip())
        
        # Step 2: Process data
        print("✅ Step 2: Process data")
        result = sandbox.run_code("""
import pandas as pd
import matplotlib.pyplot as plt

# Load data
df = pd.read_csv('/workspace/data.csv')

# Analysis
print("Dataset shape:", df.shape)
print("\\nSummary statistics:")
print(df.describe())

# Calculate metrics
avg_age = df['age'].mean()
avg_score = df['score'].mean()

print(f"\\nAverage age: {avg_age:.1f}")
print(f"Average score: {avg_score:.1f}")

# Generate plot
plt.figure(figsize=(10, 6))
plt.scatter(df['age'], df['score'])
plt.xlabel('Age')
plt.ylabel('Score')
plt.title('Age vs Score')
plt.savefig('/workspace/analysis.png')

# Save results
results = {
    'total_records': len(df),
    'avg_age': avg_age,
    'avg_score': avg_score
}

import json
with open('/workspace/results.json', 'w') as f:
    json.dump(results, f, indent=2)
        """)
        
        print(f"Analysis output:\n{result.stdout}")
        
        # Step 3: Download results
        print("\n✅ Step 3: Download results")
        results = sandbox.files.read("/workspace/results.json")
        print(f"Results: {results}")
        
        print("✅ Pipeline complete!")
    
    print()


def api_testing_framework():
    """Automated API testing"""
    print("=" * 60)
    print("2. API TESTING FRAMEWORK")
    print("=" * 60)
    
    with Sandbox.create(template="code-interpreter", api_key=API_KEY) as sandbox:
        ensure_workspace(sandbox)
        # Create test suite
        sandbox.files.write("/workspace/test_api.py", """
import requests
import json

def test_get_endpoint():
    \"\"\"Test GET endpoint\"\"\"
    response = requests.get('https://jsonplaceholder.typicode.com/posts/1')
    assert response.status_code == 200
    assert 'userId' in response.json()
    print("✅ GET test passed")

def test_post_endpoint():
    \"\"\"Test POST endpoint\"\"\"
    data = {'title': 'Test', 'body': 'Test body', 'userId': 1}
    response = requests.post(
        'https://jsonplaceholder.typicode.com/posts',
        json=data
    )
    assert response.status_code == 201
    print("✅ POST test passed")

def test_error_handling():
    \"\"\"Test error handling\"\"\"
    response = requests.get('https://jsonplaceholder.typicode.com/posts/999999')
    assert response.status_code == 404
    print("✅ Error handling test passed")

if __name__ == '__main__':
    test_get_endpoint()
    test_post_endpoint()
    test_error_handling()
    print("\\n🎉 All tests passed!")
        """)
        
        # Run tests
        result = sandbox.run_code("exec(open('/workspace/test_api.py').read())")
        print(f"Test results:\n{result.stdout}")
        
        print("✅ API testing complete!")
    
    print()


def report_generation():
    """Generate PDF report"""
    print("=" * 60)
    print("3. REPORT GENERATION")
    print("=" * 60)
    
    with Sandbox.create(template="code-interpreter", api_key=API_KEY) as sandbox:
        ensure_workspace(sandbox)
        # Install required packages
        sandbox.commands.run("pip install reportlab")
        
        # Generate report
        result = sandbox.run_code("""
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime

# Create PDF
c = canvas.Canvas('/workspace/report.pdf', pagesize=letter)
width, height = letter

# Title
c.setFont("Helvetica-Bold", 24)
c.drawString(100, height - 100, "Monthly Report")

# Date
c.setFont("Helvetica", 12)
c.drawString(100, height - 130, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

# Content
c.setFont("Helvetica", 14)
y = height - 180
c.drawString(100, y, "Summary:")
y -= 30
c.drawString(120, y, "• Total Users: 1,234")
y -= 25
c.drawString(120, y, "• Revenue: $45,678")
y -= 25
c.drawString(120, y, "• Growth: +23%")

c.save()

print("✅ PDF report generated!")
        """)
        
        print(result.stdout)
        
        # Verify file exists (optional - reportlab might not be available)
        if sandbox.files.exists("/workspace/report.pdf"):
            print("✅ Report file created")
        else:
            print("⚠️  Report file not created (reportlab not available)")
        
        print("✅ Report generation complete!")
    
    print()


def ml_model_training():
    """Train ML model"""
    print("=" * 60)
    print("4. ML MODEL TRAINING")
    print("=" * 60)
    
    with Sandbox.create(
        template="code-interpreter",
        api_key=API_KEY
        # Note: vcpu/memory come from template
    ) as sandbox:
        ensure_workspace(sandbox)
        result = sandbox.run_code("""
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import pickle

# Load data
iris = load_iris()
X_train, X_test, y_train, y_test = train_test_split(
    iris.data, iris.target, test_size=0.2, random_state=42
)

print(f"Training samples: {len(X_train)}")
print(f"Test samples: {len(X_test)}")

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"\\nModel accuracy: {accuracy:.2%}")

# Save model
with open('/workspace/model.pkl', 'wb') as f:
    pickle.dump(model, f)

print("✅ Model saved to /workspace/model.pkl")
        """, timeout=120)
        
        print(result.stdout)
        
        print("✅ ML training complete!")
    
    print()


def multi_step_workflow():
    """Complex multi-step workflow with dependencies"""
    print("=" * 60)
    print("5. MULTI-STEP WORKFLOW")
    print("=" * 60)
    
    with Sandbox.create(template="code-interpreter", api_key=API_KEY) as sandbox:
        ensure_workspace(sandbox)
        # Step 1: Fetch data
        print("Step 1: Fetch data...")
        sandbox.run_code("""
import requests
data = requests.get('https://jsonplaceholder.typicode.com/posts').json()
print(f"Fetched {len(data)} posts")

import json
with open('/workspace/posts.json', 'w') as f:
    json.dump(data, f)
        """)
        
        # Step 2: Process data
        print("Step 2: Process data...")
        sandbox.run_code("""
import json
with open('/workspace/posts.json') as f:
    posts = json.load(f)

# Extract titles
titles = [p['title'] for p in posts]

# Word frequency
from collections import Counter
all_words = ' '.join(titles).lower().split()
word_freq = Counter(all_words).most_common(10)

print("Top 10 words:")
for word, count in word_freq:
    print(f"  {word}: {count}")

# Save analysis
with open('/workspace/analysis.json', 'w') as f:
    json.dump({'word_freq': dict(word_freq)}, f)
        """)
        
        # Step 3: Generate visualization
        print("Step 3: Generate visualization...")
        sandbox.run_code("""
import json
import matplotlib.pyplot as plt

with open('/workspace/analysis.json') as f:
    data = json.load(f)

words = list(data['word_freq'].keys())
counts = list(data['word_freq'].values())

plt.figure(figsize=(12, 6))
plt.bar(words, counts)
plt.xlabel('Words')
plt.ylabel('Frequency')
plt.title('Top 10 Most Common Words')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('/workspace/word_freq.png')

print("✅ Visualization saved!")
        """)
        
        # Step 4: Create summary
        print("Step 4: Create summary...")
        result = sandbox.run_code("""
import json

with open('/workspace/posts.json') as f:
    posts = json.load(f)

with open('/workspace/analysis.json') as f:
    analysis = json.load(f)

summary = {
    'total_posts': len(posts),
    'unique_users': len(set(p['userId'] for p in posts)),
    'avg_title_length': sum(len(p['title']) for p in posts) / len(posts),
    'top_words': analysis['word_freq']
}

print("=" * 50)
print("WORKFLOW SUMMARY")
print("=" * 50)
print(f"Total posts: {summary['total_posts']}")
print(f"Unique users: {summary['unique_users']}")
print(f"Avg title length: {summary['avg_title_length']:.1f}")
print("\\nTop words:", list(summary['top_words'].keys())[:5])
        """)
        
        print(result.stdout)
        
        print("\n✅ Multi-step workflow complete!")
    
    print()


def error_recovery_pattern():
    """Robust error handling and recovery"""
    print("=" * 60)
    print("6. ERROR RECOVERY PATTERN")
    print("=" * 60)
    
    sandbox = None
    try:
        # Create sandbox with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                sandbox = Sandbox.create(
                    template="code-interpreter",
                    api_key=API_KEY
                )
                ensure_workspace(sandbox)
                print(f"✅ Sandbox created (attempt {attempt + 1})")
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"⚠️  Attempt {attempt + 1} failed, retrying...")
                else:
                    raise
        
        # Execute code with error handling
        try:
            result = sandbox.run_code("""
try:
    # This will fail
    1 / 0
except ZeroDivisionError:
    print("✅ Caught division by zero, continuing...")
    result = None

# Continue with valid operations
print("✅ Workflow continues after error")
            """)
            
            print(result.stdout)
            
        except Exception as e:
            print(f"⚠️  Code execution failed: {e}")
            print("   Attempting recovery...")
            
            # Fallback logic
            result = sandbox.run_code('print("Fallback execution")')
            print(f"✅ Recovered: {result.stdout}")
        
        print("✅ Error recovery complete!")
        
    finally:
        if sandbox:
            sandbox.kill()
            print("✅ Sandbox cleaned up")
    
    print()


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("PYTHON SDK - ADVANCED USE CASES")
    print("=" * 60 + "\n")
    
    data_analysis_pipeline()
    api_testing_framework()
    report_generation()
    ml_model_training()
    multi_step_workflow()
    error_recovery_pattern()
    
    print("=" * 60)
    print("✅ ALL ADVANCED USE CASES DEMONSTRATED!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()

