from typing import AsyncGenerator

from google.adk.agents import Agent

from retrieval import response

gemini_pro_agent = Agent(
    name= "GeminiProAgent",
    model="gemini-2.5-pro",
    description="A highly capable agent to solve complex queries",
    instruction= "You are an expert assistant for solving complex problems"
)

gemini_flash_agent = Agent(
    name= "GeminiFlashAgent",
    model="gemini-2.5-flash",
    description="A fast and efficient agent for simple queries",
    instruction="You are a quick assistant for solving straightforward questions"
)

# Router Agent

from google.adk.agents import BaseAgent
from google.adk.events import Event
from google.adk.agents.invocation_context import InvocationContext
import asyncio

class QueryRouterAgent(BaseAgent):
    name:str= "QueryRouter"
    description:str = "Routes user queries to the appropriate LLM agent based on complexity"

    async def _run_async_impl(self, context: InvocationContext) -> AsyncGenerator[Event, None]:
        user_query = context.current_message.text
        query_length = len(user_query.split())
        if query_length < 20:
            print(f"Route to gemini flash agent for short query(length:{query_length})")
            response = await gemini_flash_agent.run_async(context.current_message)
            yield Event(author=self.name, content=f"Flash Agent processed:{response}")
        else:
            print(f"Routing to gemini pro agent for complex queries(length:{query_length})")
            response = await  gemini_pro_agent.run_async(context.current_message)
            yield Event(author=self.name, content=f"Pro Agent processed:{response}")

CRITIC_SYSTEM_PROMPT="""
You are the **Critic Agent**, serving as the quality assurance arm of our collaborative research
assistant system.Your primary function is to **meticulously review and challenge** from the Researcher Agent , guaranteeing
**accuracy, completeness, and unbiased presentation**.
Your duties encompass:
* **Assessing research findings** for factual correctness, thoroughness, and potential leanings.
* **Identifying any missing data** or inconsistencies in reasoning.
* **Raising critical questions** that could refine or expand the current understanding. 
* **Offering constructive suggestions** for enhancement or exploring different angles. 
* **Validating that the final output is comprehensive** and balanced.
All criticism must be constructive. Your goal is to fortify the research,
not invalidate it. Structure your feedback clearly, drawing attention to specific points 
for revision. Your overarching aim is to ensure the final research product meets the highest 
possible quality standards.
"""


