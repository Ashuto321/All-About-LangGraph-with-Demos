from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
from dotenv import load_dotenv
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph.message import add_messages
from typing import TypedDict, Annotated, Literal
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
import sys

load_dotenv()

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

# search tool
# search_tool = DuckDuckGoSearchRun(
#     name="Internet_search",
#     description=(
#         "should search updated info from the internet"
#         "use this tool when user ask about current events"
#         "news, current information, information require"
#         "use internet for search"
#     )
# )


#instead of this tool we will add the mcp client-------------------
client = MultiServerMCPClient(
    {
        #for calculator mcp tool server
        "arith": {
            "transport": "stdio",
            "command": sys.executable,
            "args": [r"C:\Users\Ashutosh Pandey\Desktop\Machine Learning\LangGraph-In-Depth\arith_server.py"],
        },
        # for search mcp tool srever
        "server": {
            "transport": "stdio",
            "command": sys.executable,
            "args": [r"C:\Users\Ashutosh Pandey\Desktop\Machine Learning\LangGraph-In-Depth\search_server.py"]
        }
    }
)
# now wwe will go to the build graph function

# now lets create a state for chatbot
class chatstate(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    
    
# we will build a function for building graph
async def build_graph():
    # now we will fetch the tools present in the mcp-server
    tools = await client.get_tools()
    
    print(tools)
    
    # with this tool we will bind the llm
    llm_with_tool = llm.bind_tools(tools)
    
    # lets create out node
    async def chat_node(state: chatstate):
        """LLM node that may answer or request a tool call"""
        messages = state['messages']
        response = await llm_with_tool.ainvoke(messages)  # await and async invoke written as(ainvoke)
        return {'messages': [response]}
    
    # our tool node
    tool_node = ToolNode(tools) # toolnode dont need async since its implementation is async internally.
    
    
    # now lets create our graph
    graph = StateGraph(chatstate)
    
    graph.add_node("chat_node", chat_node)
    graph.add_node("tools", tool_node)
    
    graph.add_edge(START, "chat_node")
    graph.add_conditional_edges("chat_node", tools_condition)
    
    graph.add_edge("tools", "chat_node")
    
    chatbot = graph.compile()
    
    return chatbot


async def main():
    # we will get chatbot from build_graph_function
    chatbot = await build_graph()
    
    # the response also with ainvoke
    response = await chatbot.ainvoke({'messages': [HumanMessage(content="Search the internet and tell me what happened in India on 13 August 2026.")]})
    print(response['messages'][-1].content)
    
if __name__ == "__main__":
    asyncio.run(main()) # this yu cannot use since this is ipynb file if its a .py file it must have workd
# so use
# await main()