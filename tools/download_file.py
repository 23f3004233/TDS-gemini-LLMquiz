"""
File downloader tool for various file types
"""
import os
import aiohttp
from langchain_core.tools import tool
from urllib.parse import urlparse

@tool
async def download_file(url: str, filename: str = None) -> str:
    """
    Download a file from a URL and save it locally.
    Handles PDFs, CSVs, images, audio, video, and other file types.
    
    Args:
        url: Direct URL to the file
        filename: Optional custom filename. If not provided, extracts from URL
    
    Returns:
        Path to the downloaded file
    
    Example:
        filepath = await download_file("https://example.com/data.pdf", "quiz_data.pdf")
    """
    print(f"📥 Downloading file from: {url}")
    
    try:
        # Create directory if it doesn't exist
        os.makedirs("LLMFiles", exist_ok=True)
        
        # Determine filename
        if filename is None:
            # Extract from URL
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path)
            
            # If still no filename, generate one
            if not filename or filename == '':
                # Get extension from Content-Type if possible
                filename = "downloaded_file"
        
        # Ensure filename doesn't have directory traversal
        filename = os.path.basename(filename)
        
        # Full path
        filepath = os.path.join("LLMFiles", filename)
        
        # Download file
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=60)) as response:
                if response.status != 200:
                    error_msg = f"Failed to download: HTTP {response.status}"
                    print(f"❌ {error_msg}")
                    return f"Error: {error_msg}"
                
                # Get file size if available
                content_length = response.headers.get('Content-Length')
                if content_length:
                    size_mb = int(content_length) / (1024 * 1024)
                    print(f"📦 File size: {size_mb:.2f} MB")
                
                # Write file
                with open(filepath, 'wb') as f:
                    chunk_size = 8192
                    bytes_downloaded = 0
                    
                    async for chunk in response.content.iter_chunked(chunk_size):
                        f.write(chunk)
                        bytes_downloaded += len(chunk)
                
                downloaded_mb = bytes_downloaded / (1024 * 1024)
                print(f"✅ Downloaded {downloaded_mb:.2f} MB to: {filepath}")
                
                return filepath
    
    except Exception as e:
        error_msg = f"❌ Error downloading file: {str(e)}"
        print(error_msg)
        return f"Error: {error_msg}"