# from src.full_agent import deep_research_agent
# import asyncio

# from langchain_core.messages import HumanMessage

# async def main():
#     thread = {"configurable": {"thread_id": "1", "recursion_limit": 50}}
    
#     result = await deep_research_agent.ainvoke(
#         {"messages": [HumanMessage(content="Compare Gemini to OpenAI Deep Research agents.")]}, 
#         config=thread
#     )
#     print(result['messages'])

# if __name__ == "__main__":
#     asyncio.run(main())