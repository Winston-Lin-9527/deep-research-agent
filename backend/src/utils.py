from datetime import datetime
import os
from dotenv import load_dotenv
from typing import Annotated, List
from langchain_core.messages import HumanMessage
from typing_extensions import Literal

from tavily import TavilyClient 
from langchain.chat_models import init_chat_model
from langchain_core.tools import InjectedToolArg, tool

from src.prompts import summarize_webpage_prompt
from src.research_states import SummarySchema

# ===== UTILITY FUNCTIONS =====

def get_today_str() -> str:
    """Get current date in a human-readable format."""
    return datetime.now().strftime("%a %b %-d, %Y")

def get_current_directory() -> str:
    """Return the absolute path of the current working directory."""
    return os.getcwd()

# ===== Configs =====
load_dotenv()
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
summarization_model = init_chat_model("gemini-2.5-flash-lite", model_provider="google_genai")

def tavily_multiple_search(
    queries: list[str],
    topic: Literal['general', 'news', 'finance'],
    days: int = 365,
    include_raw_content: bool = False,
    max_results: int = 10
) -> list[str]:
    
    """ Internal function """
    docs = []
    for query in queries:
        result = tavily_client.search(
            query,
            topic=topic,
            days=days,
            include_raw_content=include_raw_content, 
            max_results=max_results
        )
        docs.append(result)
    return docs

def summarize_webpage_content(webpage_content: str) -> str:
    """ Internal function """
    
    structured_output_model = summarization_model.with_structured_output(SummarySchema)
    prompt = HumanMessage(
        summarize_webpage_prompt.format(
            webpage_content=webpage_content,
            date=get_today_str()
        )
    )
    response = structured_output_model.invoke([prompt])
    
    # Handle case where response is None or doesn't have expected attributes
    if response is None:
        return f"<summary>\nError: Could not generate summary\n</summary>\n<key_excerpts>\nError: Could not extract excerpts\n</key_excerpts>"
    
    # Safely access attributes with fallbacks
    summary = getattr(response, 'summary', 'Error: Could not generate summary')
    key_excerpts = getattr(response, 'key_excerpts', 'Error: Could not extract excerpts')
    
    formatted_summary = (
        f"<summary>\n{summary}\n</summary>\n"
        f"<key_excerpts>\n{key_excerpts}\n</key_excerpts>"
    )
    
    return formatted_summary

def deduplicate_sources(search_results: List[dict]) -> dict:
    """ deduplicate search results by sources """
    unique_results = {}
    
    for search_result in search_results:
        for result_website in search_result['results']:
            url = result_website['url']
            if url not in unique_results.keys():
                unique_results[url] = result_website
    
    return unique_results

def process_search_results(unique_results: dict) -> dict:
    """Process search results by summarizing content where available.
    
    Args:
        unique_results: Dictionary of unique search results
        
    Returns:
        Dictionary of processed results with summaries
    """
    summarized_results = {}
    
    for url, result in unique_results.items():
        # Use existing content if no raw content for summarization
        if not result.get("raw_content"):
            content = result['content']
        else:
            # Summarize raw content for better processing
            content = summarize_webpage_content(result['raw_content'])
        
        summarized_results[url] = {
            'title': result['title'],
            'content': content
        }
    
    return summarized_results

def format_search_output(summarized_results: dict) -> str:
    """Format search results for display."""
    
    if not summarized_results:
        return "No search results found, please try with another query"
    
    formatted_output = "Search results:\n"
    
    for url, result in summarized_results.items():
        formatted_output += f"<source>\n{url}\n</source>\n"
        formatted_output += f"<title>\n{result['title']}\n</title>\n"
        formatted_output += f"<content>\n{result['content']}\n</content>\n"
        formatted_output += "-"*100 + "\n"
    
    return formatted_output


# ================== TOOLS
@tool(parse_docstring=True)
def tavily_search_tool(
    query: str,
    max_results: Annotated[int, InjectedToolArg]=3,
    topic: Literal['general', 'finance', 'news']='general',
    days: int=365,
) -> str:
    """Fetch results from Tavily search API with content summarization.

    Args:
        query: A single search query to execute
        max_results: Maximum number of results to return
        topic: Topic to filter results by ('general', 'news', 'finance')

    Returns:
        Formatted string of search results with summaries
    """ 
    # tavily or whatever underlying context provider, can be RAG as well?
    results = tavily_multiple_search([query], topic, days, include_raw_content=True)
    
    unique_results = deduplicate_sources(results)
    
    summarized_results = process_search_results(unique_results)
    
    formatted_results = format_search_output(summarized_results)
    
    return formatted_results

@tool(parse_docstring=True)
def think_tool(reflection: str) -> str:
    """Tool for strategic reflection on research progress and decision-making.

    Use this tool after each search to analyze results and plan next steps systematically.
    This creates a deliberate pause in the research workflow for quality decision-making.

    When to use:
    - After receiving search results: What key information did I find?
    - Before deciding next steps: Do I have enough to answer comprehensively?
    - When assessing research gaps: What specific information am I still missing?
    - Before concluding research: Can I provide a complete answer now?

    Reflection should address:
    1. Analysis of current findings - What concrete information have I gathered?
    2. Gap assessment - What crucial information is still missing?
    3. Quality evaluation - Do I have sufficient evidence/examples for a good answer?
    4. Strategic decision - Should I continue searching or provide my answer?

    Args:
        reflection: Your detailed reflection on research progress, findings, gaps, and next steps

    Returns:
        Confirmation that reflection was recorded for decision-making
    """
    return f"Reflection recorded: {reflection}"