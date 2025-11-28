"""
HTTP POST request tool for submitting answers
"""
import aiohttp
import json as json_module
from langchain_core.tools import tool

@tool
async def post_request(url: str, payload: dict) -> str:
    """
    Send a POST request with JSON payload.
    Used for submitting quiz answers to evaluation endpoints.
    
    Args:
        url: The endpoint URL to POST to
        payload: Dictionary containing the JSON payload (will be serialized)
    
    Returns:
        Response as JSON string with status code and body
    
    Example:
        response = await post_request(
            "https://example.com/submit",
            {
                "email": "student@example.com",
                "secret": "secret123",
                "url": "https://example.com/quiz-1",
                "answer": 42
            }
        )
    
    Notes:
        - Automatically sets Content-Type: application/json
        - Returns parsed JSON response with status code
        - Handles errors gracefully
    """
    print(f"📮 Sending POST request to: {url}")
    print(f"📦 Payload keys: {list(payload.keys())}")
    
    try:
        # Ensure payload is serializable
        try:
            payload_json = json_module.dumps(payload)
        except Exception as e:
            error_msg = f"Failed to serialize payload: {str(e)}"
            print(f"❌ {error_msg}")
            return json_module.dumps({
                "error": error_msg,
                "status_code": -1
            })
        
        # Send POST request
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                json=payload,
                headers={
                    "Content-Type": "application/json"
                },
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                status_code = response.status
                
                # Try to parse JSON response
                try:
                    response_data = await response.json()
                except:
                    # If not JSON, get text
                    response_text = await response.text()
                    response_data = {"text": response_text}
                
                result = {
                    "status_code": status_code,
                    "response": response_data
                }
                
                print(f"✅ Response received: {status_code}")
                
                # Log important fields
                if isinstance(response_data, dict):
                    if "correct" in response_data:
                        print(f"{'✅' if response_data['correct'] else '❌'} Answer correct: {response_data['correct']}")
                    if "url" in response_data:
                        print(f"🔗 Next URL: {response_data['url']}")
                    if "reason" in response_data:
                        print(f"💬 Reason: {response_data['reason']}")
                
                return json_module.dumps(result, indent=2)
    
    except asyncio.TimeoutError:
        error_msg = "Request timed out after 30 seconds"
        print(f"❌ {error_msg}")
        return json_module.dumps({
            "error": error_msg,
            "status_code": -1
        })
    
    except Exception as e:
        error_msg = f"❌ Error sending POST request: {str(e)}"
        print(error_msg)
        return json_module.dumps({
            "error": error_msg,
            "status_code": -1
        })