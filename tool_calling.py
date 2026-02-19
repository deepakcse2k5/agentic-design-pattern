import os, getpass
import asyncio
import nest_asyncio
from typing import List
from dotenv import load_dotenv
import logging
from langchain_google_genai import ChatGoogleGenerativeAI

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool as langchain_tool
from langchain.agents import create_tool_calling_agent, AgentExecutor
from sympy.physics.units import temperature
load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")
try:
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature = 0
    )

    print(f"language model initialized:{llm.model}")
except Exception as e:
    print(f"error initializing in llm model:{e}")
    llm = None

#-- defining tool

@langchain_tool
def search_information(query:str) -> str:
    """
    provide factual information of a given topic.Use this tool to find answers
    to phrases like 'capital of france' or 'weather in london?.
    :param query:
    :return:
    """
    print(f"\n--- Tool called: search_information with query: f'{query}' ---")
    # Simulate a search tool with a dictionary of predefined results:
    simulated_results = {
        "weather in London" : "The weather in london is currently cloudy with a tem of 15 degree C",
        "Capital of France" : "The capital of france is paris.",
        "population of earth": "The estimatated population of earth is around 8 billion people.",
        "tallest mountain" : "Mount everest is the tallest mountain above the sea level",
        "default": f"Simulated search result for '{query}': No specific information found, but the topic seems interesting."
    }

    result = simulated_results.get(query.lower(), simulated_results["default"])

    print(f"--- TOOL RESULT:{result}")
    return result

tools = [search_information]

# Create a tool-calling agent

if llm:
    # This prompt requires an `agent_scratchpad` placeholder for the agent's internal steps.
    agent_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}")
    ])

    # create agent, binding the placeholder, tools and prompts together.
    agent = create_tool_calling_agent(llm, tools, agent_prompt)
    # AgentExecutor is the runtime that invokes the agent and executes the chosen tools.
    # The 'tools' argument is not needed here as they are already bound to the agent.
    agent_executor = AgentExecutor(agent=agent, verbose=True, tools=tools)

async def run_agent_with_tools(query:str):
    """
    Invoke the agent executor with a query and prints the final response
    :param query:
    :return:
    """
    print(f"\n--- Running agent with query:'{query}' ---")
    try:
        response = await agent_executor.ainvoke({"input":query})
        print(f"\n--- Final agent response ---")
    except Exception as e:
        print(f"\n An error occured during agent execution: {e}")

async def main():
    """ Runs all agent queries concurrently."""
    tasks = [
        run_agent_with_tools("What is the capital of france?"),
        run_agent_with_tools("weather in london?"),
        run_agent_with_tools("Tell me something about india")
    ]
    await asyncio.gather(*tasks)
nest_asyncio.apply()
asyncio.run(main())



