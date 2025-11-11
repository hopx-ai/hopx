"""
05. Environment Variables - Python SDK

This example covers ALL environment variable operations:
- Get all environment variables
- Set all environment variables
- Update environment variables
- Delete environment variables
- Get single variable
- Set single variable
"""

from hopx_ai import Sandbox
import os

API_KEY = os.getenv("HOPX_API_KEY", "your-api-key-here")


def get_all_env_vars():
    """Get all environment variables"""
    print("=" * 60)
    print("1. GET ALL ENVIRONMENT VARIABLES")
    print("=" * 60)
    
    with Sandbox.create(template="code-interpreter", api_key=API_KEY) as sandbox:
        # Get all env vars
        env_vars = sandbox.env.get_all()
        
        print(f"✅ Total environment variables: {len(env_vars)}")
        print(f"✅ Sample variables:")
        for key in list(env_vars.keys())[:5]:
            print(f"   {key} = {env_vars[key]}")
    
    print()


def set_all_env_vars():
    """Set all environment variables (replace)"""
    print("=" * 60)
    print("2. SET ALL ENVIRONMENT VARIABLES (REPLACE)")
    print("=" * 60)
    
    with Sandbox.create(template="code-interpreter", api_key=API_KEY) as sandbox:
        # Set new env vars (replaces all)
        new_env = {
            "API_KEY": "sk-test-123",
            "DEBUG": "true",
            "ENVIRONMENT": "production",
            "DATABASE_URL": "postgres://localhost/mydb"
        }
        
        sandbox.env.set_all(new_env)
        print("✅ Environment variables replaced")
        
        # Verify
        env_vars = sandbox.env.get_all()
        print(f"✅ Total variables now: {len(env_vars)}")
        print(f"✅ Our variables:")
        for key in new_env.keys():
            print(f"   {key} = {env_vars.get(key)}")
    
    print()


def update_env_vars():
    """Update environment variables (merge)"""
    print("=" * 60)
    print("3. UPDATE ENVIRONMENT VARIABLES (MERGE)")
    print("=" * 60)
    
    with Sandbox.create(template="code-interpreter", api_key=API_KEY) as sandbox:
        # Set initial vars
        initial = {
            "VAR1": "value1",
            "VAR2": "value2"
        }
        sandbox.env.set_all(initial)
        print("✅ Initial variables set")
        
        # Update (merge) with new vars
        updates = {
            "VAR2": "updated_value2",  # Overwrite
            "VAR3": "value3"            # Add new
        }
        
        sandbox.env.update(updates)
        print("✅ Variables updated (merged)")
        
        # Verify
        env_vars = sandbox.env.get_all()
        print(f"✅ VAR1: {env_vars.get('VAR1')} (unchanged)")
        print(f"✅ VAR2: {env_vars.get('VAR2')} (updated)")
        print(f"✅ VAR3: {env_vars.get('VAR3')} (new)")
    
    print()


def delete_env_vars():
    """Delete environment variables"""
    print("=" * 60)
    print("4. DELETE ENVIRONMENT VARIABLES")
    print("=" * 60)
    
    with Sandbox.create(template="code-interpreter", api_key=API_KEY) as sandbox:
        # Set some vars
        sandbox.env.set_all({
            "TO_DELETE": "will be deleted",
            "TO_KEEP": "will remain"
        })
        
        print("✅ Variables set:")
        print(f"   TO_DELETE = {sandbox.env.get('TO_DELETE')}")
        print(f"   TO_KEEP = {sandbox.env.get('TO_KEEP')}")
        
        # Delete one variable
        sandbox.env.delete(["TO_DELETE"])
        print("✅ Variable deleted: TO_DELETE")
        
        # Verify
        env_vars = sandbox.env.get_all()
        print(f"✅ TO_DELETE exists: {'TO_DELETE' in env_vars}")
        print(f"✅ TO_KEEP exists: {'TO_KEEP' in env_vars}")
        print(f"✅ TO_KEEP value: {env_vars.get('TO_KEEP')}")
    
    print()


def get_single_var():
    """Get single environment variable"""
    print("=" * 60)
    print("5. GET SINGLE VARIABLE")
    print("=" * 60)
    
    with Sandbox.create(template="code-interpreter", api_key=API_KEY) as sandbox:
        # Set a variable
        sandbox.env.set("MY_VAR", "my_value")
        print("✅ Variable set: MY_VAR")
        
        # Get it
        value = sandbox.env.get("MY_VAR")
        print(f"✅ MY_VAR = {value}")
        
        # Try to get non-existent variable
        value = sandbox.env.get("NON_EXISTENT")
        print(f"✅ NON_EXISTENT = {value}")  # None or empty
    
    print()


def set_single_var():
    """Set single environment variable"""
    print("=" * 60)
    print("6. SET SINGLE VARIABLE")
    print("=" * 60)
    
    with Sandbox.create(template="code-interpreter", api_key=API_KEY) as sandbox:
        # Set individual variables
        sandbox.env.set("API_KEY", "sk-123")
        sandbox.env.set("DEBUG", "true")
        sandbox.env.set("PORT", "8000")
        
        print("✅ Individual variables set")
        
        # Verify
        print(f"✅ API_KEY = {sandbox.env.get('API_KEY')}")
        print(f"✅ DEBUG = {sandbox.env.get('DEBUG')}")
        print(f"✅ PORT = {sandbox.env.get('PORT')}")
    
    print()


def use_env_in_code():
    """Use environment variables in code execution"""
    print("=" * 60)
    print("7. USE ENV VARS IN CODE EXECUTION")
    print("=" * 60)
    
    with Sandbox.create(template="code-interpreter", api_key=API_KEY) as sandbox:
        # Set env vars
        sandbox.env.set_all({
            "DATABASE_URL": "postgres://localhost/mydb",
            "API_KEY": "sk-secret-key-123",
            "MAX_RETRIES": "3"
        })
        
        # Use them in code
        result = sandbox.run_code("""
import os

db_url = os.environ.get('DATABASE_URL')
api_key = os.environ.get('API_KEY')
max_retries = int(os.environ.get('MAX_RETRIES', '1'))

print(f"Database: {db_url}")
print(f"API Key: {api_key}")
print(f"Max retries: {max_retries}")
        """)
        
        print(f"✅ Code output:\n{result.stdout}")
    
    print()


def env_vars_best_practices():
    """Best practices for environment variables"""
    print("=" * 60)
    print("8. BEST PRACTICES")
    print("=" * 60)
    
    with Sandbox.create(template="code-interpreter", api_key=API_KEY) as sandbox:
        print("✅ Best Practice #1: Pass secrets via env, not in code")
        
        # ❌ BAD: Hardcoded in code
        # result = sandbox.run_code('api_key = "sk-secret-123"')
        
        # ✅ GOOD: Via environment variable
        result = sandbox.run_code(
            'import os; api_key = os.environ.get("API_KEY")',
            env={"API_KEY": "sk-secret-123"}
        )
        print("   Passed API key via env parameter ✅")
        
        print("\n✅ Best Practice #2: Set common env vars once")
        
        # Set once for entire sandbox
        sandbox.env.set_all({
            "DATABASE_URL": "postgres://...",
            "REDIS_URL": "redis://...",
            "API_KEY": "sk-..."
        })
        
        # Now available in all code executions
        result1 = sandbox.run_code('import os; print(os.getenv("DATABASE_URL"))')
        result2 = sandbox.run_code('import os; print(os.getenv("REDIS_URL"))')
        
        print("   All env vars available across executions ✅")
        
        print("\n✅ Best Practice #3: Override for specific executions")
        
        # Global env
        sandbox.env.set("ENVIRONMENT", "production")
        
        # Override for one execution
        result = sandbox.run_code(
            'import os; print(os.getenv("ENVIRONMENT"))',
            env={"ENVIRONMENT": "development"}  # Override
        )
        
        print(f"   Overridden for single execution: {result.stdout.strip()} ✅")
    
    print()


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("PYTHON SDK - ENVIRONMENT VARIABLES")
    print("=" * 60 + "\n")
    
    get_all_env_vars()
    set_all_env_vars()
    update_env_vars()
    delete_env_vars()
    get_single_var()
    set_single_var()
    use_env_in_code()
    env_vars_best_practices()
    
    print("=" * 60)
    print("✅ ALL ENVIRONMENT VARIABLE OPERATIONS DEMONSTRATED!")
    print("=" * 60)
    print("\nFeatures covered:")
    print("  ✅ Get all env vars")
    print("  ✅ Set all env vars (replace)")
    print("  ✅ Update env vars (merge)")
    print("  ✅ Delete env vars")
    print("  ✅ Get single var")
    print("  ✅ Set single var")
    print("  ✅ Use in code execution")
    print("  ✅ Best practices")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()

