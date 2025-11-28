"""
Dynamic package installer for adding dependencies at runtime
"""
import asyncio
import subprocess
from langchain_core.tools import tool

@tool
async def add_dependencies(packages: list) -> str:
    """
    Install Python packages dynamically using pip.
    Useful when quiz tasks require specific libraries.
    
    Args:
        packages: List of package names to install (e.g., ["pandas", "matplotlib"])
    
    Returns:
        Installation result message
    
    Example:
        result = await add_dependencies(["tabula-py", "pdfplumber"])
    
    Notes:
        - Uses pip install with --quiet flag
        - Installs to current environment
        - Returns success/failure message
    """
    if not packages:
        return "Error: No packages specified"
    
    print(f"📦 Installing packages: {', '.join(packages)}")
    
    try:
        # Build pip command
        cmd = ['pip', 'install', '--quiet'] + packages
        
        # Run installation
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await asyncio.wait_for(
            process.communicate(),
            timeout=120.0  # 2 minute timeout for package installation
        )
        
        if process.returncode == 0:
            print(f"✅ Successfully installed: {', '.join(packages)}")
            return f"Successfully installed: {', '.join(packages)}"
        else:
            stderr_str = stderr.decode('utf-8', errors='replace')
            error_msg = f"Failed to install packages. Error: {stderr_str}"
            print(f"❌ {error_msg}")
            return error_msg
    
    except asyncio.TimeoutError:
        error_msg = "Package installation timed out after 2 minutes"
        print(f"❌ {error_msg}")
        return error_msg
    
    except Exception as e:
        error_msg = f"❌ Error installing packages: {str(e)}"
        print(error_msg)
        return error_msg