import os
from typing_extensions import TypedDict
from typing import Annotated

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from langchain_openai import AzureChatOpenAI
from langchain_groq import ChatGroq
from langchain_core.messages import ChatMessage
from langchain_core.tools import tool

from api import token_tools, anime_tools

llm = ChatGroq(
    model="moonshotai/kimi-k2-instruct"
)

'''
llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    azure_deployment=os.getenv("AZURE_GPT_MODEL_NAME"),
    api_version="2024-02-01",
    temperature=0
)
'''
class State(TypedDict):
    messages: Annotated[list, add_messages]
    expert: Annotated[list, add_messages]

builder = StateGraph(State)

token_tool_node = ToolNode(token_tools)
anime_tool_node = ToolNode(anime_tools)

def anime_wrapper(state: State) -> dict:
    results = anime_tool_node.invoke({
        "messages": state["expert"]
    })
    return {
        "expert": results["messages"]
    }

def token_wrapper(state: State) -> dict:
    results = token_tool_node.invoke(state)
    return {
        "messages": results["messages"]
    }

def router(state: State) -> State:

    llm_tool = llm.bind_tools(token_tools)

    instructions = f"""
You are a specialized router agent. Your first priority is to determine if a tool is required.
A tool call should only be used when asked by an expert. Under no other circumstances should you try to use a tool.

When performing a tool call, do not say anything.

If and only if no tool is required, you must decide which expert to route the request to. The available experts are:
- Anime: Used to gather information from MyAnimeList about anime
- Manga: Used to gather information from MyAnimeList about manga
- Forums: Used to gather information from MyAnimeList about forums

Once either the user's message has been answered, or it can't be answered by one of the experts, say the word Summarize

All responses should be single words.

Message history:
{state["messages"]}
"""

    response = llm_tool.invoke(instructions)
    response.role = "Router"

    return {
        "messages": [response]
    }

def anime(state: State) -> State:

    instructions = f"""
    You are an anime expert with access to MyAnimeList. The user's primary question is in the main message history. Your expert message history is a scratchpad for your own tool use.

    Based on both histories, call tools to answer the user's query. If a tool call is denied due to a 401 error, say that an access token refresh is needed.
    Do not rely on your own knowledge. Always use the MAL API tools to gather information.
    You may continue to call tools until you are able to answer.
    If a tool is not called, your response will be sent back to the router with your scratchpad erased, so always call a tool unless you are finished.

    ## Main Message History:
    {state["messages"]}

    ## Expert Message History (Your Scratchpad):
    {state["expert"]}
    """

    llm_tool = llm.bind_tools(anime_tools)
    response = llm_tool.invoke(instructions)
    response.role = "Anime"

    return {
        "expert": [response]
    }

def summarize(state: State) -> State:

    instructions = f"""
    Use the following message history in order to respond to the user's most recent message

    Message history:
    {state["messages"]}
    """ 

    return {
        "messages": [ChatMessage(role="Final Answer", content=llm.invoke(instructions).content)]
    }

def route_experts(state: State) -> str:
    destination = state["messages"][-1]

    if destination.tool_calls:
        return "RefreshToken"
    elif "Anime" in destination.content:
        return "Anime"
    elif "Summarize" in destination.content:
        return "Summarize"
    else:
        return "Router"
    
def route_anime(state: State) -> str:
    if state["expert"][-1].tool_calls:
        return "AnimeTools"
    else:
        return "Update"

def expert_to_messages(state: State) -> dict:
    return {
        "messages": [state["expert"][-1]]
    }

builder.add_node("Router", router)
builder.add_node("Anime", anime)
builder.add_node("Summarize", summarize)

builder.add_node("RefreshToken", token_wrapper)
builder.add_node("AnimeTools", anime_wrapper)

builder.add_node("Update", expert_to_messages)

builder.add_edge(START, "Router")
builder.add_conditional_edges(
    "Router",
    route_experts,
    {
        "Anime": "Anime",
        "Summarize": "Summarize",
        "RefreshToken": "RefreshToken",
        "Router": "Router"
    }
)
builder.add_edge("RefreshToken", "Router")
builder.add_conditional_edges(
    "Anime",
    route_anime,
    {
        "AnimeTools": "AnimeTools",
        "Update": "Update"
    }
)
builder.add_edge("Update", "Router")
builder.add_edge("AnimeTools", "Anime")
builder.add_edge("Summarize", END)

graph = builder.compile()

query = input("Query: ")

for event in graph.stream({
    "messages": [{
        "role": "user",
        "content": query
        }]
}):

    for node, value in event.items():
        last_message = None

        if "messages" in value and value["messages"]:
            last_message = value["messages"][-1]
        elif "expert" in value and value["expert"]:
            last_message = value["expert"][-1]

        if last_message:
            role = getattr(last_message, "role", "Tool").title()
            content = last_message.content if last_message.content is not None else ""
            if node != "Update":
                print(f"{node}: {content}")
