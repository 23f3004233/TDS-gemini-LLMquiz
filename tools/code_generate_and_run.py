"""
Python code execution tool with subprocess isolation
"""
import os
import asyncio
import tempfile
from langchain_core.tools import tool

@tool
async def run_code(code: str) -> str:
    """
    Execute arbitrary Python code in an isolated subprocess.
    Returns stdout, stderr, and exit code.
    
    Args:
        code: Python code to execute
    
    Returns:
        JSON string with stdout, stderr, exit_code
    
    Example:
        result = await run_code('''
import pandas as pd
df = pd.read_csv("LLMFiles/data.csv")
print(df["value"].sum())
''')
    
    Notes:
        - Code runs in subprocess with 60s timeout
        - Has access to installed packages
        - Can read/write files in LLMFiles/ and outputs/ directories
        - For visualizations, save to outputs/ directory
    """
    print(f"🐍 Executing Python code ({len(code)} characters)...")
    
    try:
        # Create temporary file for code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        try:
            # Execute code with timeout
            process = await asyncio.create_subprocess_exec(
                'python', temp_file,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=os.getcwd()
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=60.0  # 60 second timeout
                )
                
                stdout_str = stdout.decode('utf-8', errors='replace')
                stderr_str = stderr.decode('utf-8', errors='replace')
                exit_code = process.returncode
                
                # Format result
                result = {
                    "stdout": stdout_str,
                    "stderr": stderr_str,
                    "exit_code": exit_code
                }
                
                if exit_code == 0:
                    print(f"✅ Code executed successfully")
                    if stdout_str:
                        print(f"📤 Output: {stdout_str[:500]}")
                else:
                    print(f"⚠️  Code execution failed with exit code {exit_code}")
                    if stderr_str:
                        print(f"📤 Error: {stderr_str[:500]}")
                
                # Return formatted string
                import json
                return json.dumps(result, indent=2)
            
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                error_msg = "Code execution timed out after 60 seconds"
                print(f"❌ {error_msg}")
                return json.dumps({
                    "stdout": "",
                    "stderr": error_msg,
                    "exit_code": -1
                })
        
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_file)
            except:
                pass
    
    except Exception as e:
        error_msg = f"❌ Error executing code: {str(e)}"
        print(error_msg)
        import json
        return json.dumps({
            "stdout": "",
            "stderr": error_msg,
            "exit_code": -1
        })