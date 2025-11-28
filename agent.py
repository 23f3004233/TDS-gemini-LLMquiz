"""
LangGraph-based autonomous agent for solving quiz tasks
Uses Google Gemini 2.5 Flash with tool orchestration
"""
import os
import time
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

# Import all tools
from tools.web_scraper import get_rendered_html
from tools.download_file import download_file
from tools.code_generate_and_run import run_code
from tools.send_request import post_request
from tools.add_dependencies import add_dependencies

# Agent state definition
class AgentState(TypedDict):
    """State for the agent graph"""
    messages: Annotated[Sequence[BaseMessage], add_messages]
    email: str
    secret: str
    current_url: str
    start_time: float
    quiz_count: int
    max_time: float

# System prompt for the agent
SYSTEM_PROMPT = """You are an autonomous agent designed to solve data-related quiz tasks.

Your capabilities:
1. **Web Scraping**: Use get_rendered_html(url) to fetch JavaScript-rendered HTML pages
2. **File Download**: Use download_file(url, filename) to download PDFs, CSVs, images, etc.
3. **Code Execution**: Use run_code(code) to execute Python code for data processing/analysis
4. **HTTP POST**: Use post_request(url, payload) to submit answers
5. **Package Installation**: Use add_dependencies(packages) to install Python packages

CRITICAL INSTRUCTIONS:

1. **Start by scraping the quiz page**: Always begin by calling get_rendered_html with the current quiz URL to see the instructions.

2. **Parse instructions carefully**: The quiz page HTML will contain base64-encoded content in a <script> tag. Look for patterns like:
   - document.querySelector("#result").innerHTML = atob(`...`)
   - The decoded content contains the actual question and instructions

3. **Follow the workflow**:
   Step 1: Scrape quiz page → Extract instructions
   Step 2: Download any required files
   Step 3: Write and execute Python code to solve the task
   Step 4: Submit answer to the specified endpoint (extract from quiz page, don't hardcode)

4. **Time management**: You have 3 minutes from the initial request. Check elapsed time before operations.

5. **Handle data files**:
   - PDF: Use PyPDF2, pdfplumber, or tabula-py for tables
   - CSV: Use pandas
   - Images: Use PIL, cv2, or send to LLM vision
   - Audio: Use speech_recognition, whisper
   - Video: Use opencv-python, moviepy
   - JSON: Use json module
   - Excel: Use openpyxl, xlrd
   - Text files: Use standard file operations

6. **Answer format**: The answer field can be:
   - A number (int or float)
   - A string
   - A boolean
   - A base64-encoded file (for images/charts)
   - A JSON object with multiple fields

7. **Submission format**: Always use this exact structure:
   {{
     "email": "<email>",
     "secret": "<secret>",
     "url": "<current_quiz_url>",
     "answer": <your_answer>
   }}

8. **Response handling**:
   - If correct=true and new url provided → Continue to next quiz
   - If correct=false → Analyze error, retry if time permits
   - If no url in response → Quiz chain complete

9. **Error recovery**:
   - If code fails, debug and retry
   - If answer wrong, re-analyze the question
   - If time running out, submit best guess

10. **Important patterns**:
    - Base64 decode instructions: atob() in JS, base64.b64decode() in Python
    - Always extract submit URL from quiz page
    - Download files before processing them
    - Install packages as needed (pandas, numpy, matplotlib, etc.)

Remember: Be systematic, check your work, and manage time wisely. Each quiz may chain to the next, so solve efficiently."""

# Initialize LLM with rate limiting
class RateLimitedLLM:
    """Wrapper for Gemini with rate limiting (9 requests per minute)"""
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0.1,
            max_output_tokens=8192,
        )
        self.last_call_time = 0
        self.min_interval = 60.0 / 9  # 9 requests per minute = ~6.67 seconds per request
    
    def invoke(self, messages):
        """Invoke LLM with rate limiting"""
        # Calculate time since last call
        current_time = time.time()
        time_since_last = current_time - self.last_call_time
        
        # Wait if necessary
        if time_since_last < self.min_interval:
            wait_time = self.min_interval - time_since_last
            print(f"⏳ Rate limit: waiting {wait_time:.2f} seconds...")
            time.sleep(wait_time)
        
        # Make the call
        self.last_call_time = time.time()
        return self.llm.invoke(messages)
    
    def bind_tools(self, tools):
        """Bind tools to LLM"""
        self.llm = self.llm.bind_tools(tools)
        return self

# Create rate-limited LLM instance
llm = RateLimitedLLM()

# Define tools
tools = [
    get_rendered_html,
    download_file,
    run_code,
    post_request,
    add_dependencies
]

# Bind tools to LLM
llm_with_tools = llm.bind_tools(tools)

def should_continue(state: AgentState) -> str:
    """Decide whether to continue or end"""
    messages = state["messages"]
    last_message = messages[-1]
    
    # Check if LLM wants to use tools
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    
    # Check for completion signal in content
    if hasattr(last_message, "content"):
        content = last_message.content.lower()
        if "quiz complete" in content or "no new url" in content or "finished" in content:
            return "end"
    
    # Default: continue
    return "end"

def call_model(state: AgentState) -> AgentState:
    """Call the LLM model"""
    messages = state["messages"]
    
    # Add system message if not present
    if not any(isinstance(m, SystemMessage) for m in messages):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + list(messages)
    
    # Add context about current state
    elapsed_time = time.time() - state["start_time"]
    time_remaining = state["max_time"] - elapsed_time
    
    context_msg = f"""
Current context:
- Email: {state['email']}
- Secret: {state['secret']}
- Current URL: {state['current_url']}
- Quiz number: {state['quiz_count']}
- Time elapsed: {elapsed_time:.1f}s
- Time remaining: {time_remaining:.1f}s

Start by scraping the current URL to see the quiz question."""
    
    messages = list(messages) + [HumanMessage(content=context_msg)]
    
    print(f"\n🤖 Calling LLM (quiz #{state['quiz_count']}, {time_remaining:.1f}s remaining)...")
    
    response = llm_with_tools.invoke(messages)
    
    # Update state
    new_state = {
        "messages": [response],
    }
    
    return new_state

# Build the graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("agent", call_model)
workflow.add_node("tools", ToolNode(tools))

# Set entry point
workflow.set_entry_point("agent")

# Add conditional edges
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools",
        "end": END
    }
)

# Add edge from tools back to agent
workflow.add_edge("tools", "agent")

# Compile the graph
graph = workflow.compile()

async def run_agent(email: str, secret: str, initial_url: str) -> dict:
    """
    Run the autonomous agent to solve quiz chain
    
    Args:
        email: Student email
        secret: Student secret
        initial_url: Starting quiz URL
    
    Returns:
        Final result dictionary
    """
    print(f"\n{'='*60}")
    print(f"🚀 Agent starting")
    print(f"📧 Email: {email}")
    print(f"🔗 Initial URL: {initial_url}")
    print(f"{'='*60}\n")
    
    # Initialize state
    initial_state = {
        "messages": [
            HumanMessage(content=f"Solve the quiz at this URL: {initial_url}")
        ],
        "email": email,
        "secret": secret,
        "current_url": initial_url,
        "start_time": time.time(),
        "quiz_count": 1,
        "max_time": 180.0  # 3 minutes
    }
    
    try:
        # Run the graph with recursion limit
        final_state = await graph.ainvoke(
            initial_state,
            config={"recursion_limit": 200}
        )
        
        elapsed = time.time() - initial_state["start_time"]
        print(f"\n{'='*60}")
        print(f"✅ Agent completed")
        print(f"⏱️  Total time: {elapsed:.2f}s")
        print(f"📝 Quizzes solved: {final_state.get('quiz_count', 1)}")
        print(f"{'='*60}\n")
        
        return {
            "success": True,
            "elapsed_time": elapsed,
            "quiz_count": final_state.get("quiz_count", 1)
        }
    
    except Exception as e:
        elapsed = time.time() - initial_state["start_time"]
        print(f"\n{'='*60}")
        print(f"❌ Agent failed")
        print(f"⏱️  Time elapsed: {elapsed:.2f}s")
        print(f"Error: {e}")
        print(f"{'='*60}\n")
        
        import traceback
        traceback.print_exc()
        
        return {
            "success": False,
            "error": str(e),
            "elapsed_time": elapsed
        }