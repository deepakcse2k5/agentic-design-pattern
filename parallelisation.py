import os
import asyncio
from typing import Optional

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable, RunnableParallel, RunnablePassthrough

import os
from dotenv import load_dotenv
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

try:
    llm:Optional[ChatOpenAI] = ChatOpenAI(api_key=openai_api_key, model="gpt-4o-mini", temperature=0.7)
except Exception as e:
    print(f"Error Initializing language model: {e}")
    llm = None

# --- Define Independent Chains ---
# These three chains represent distinct tasks that can be executed in parallel.

summarise_chain:Runnable = (
    ChatPromptTemplate.from_messages([
        ("system","Summarize the following topic concisely."),
        ("user","{topic}")
    ])
    | llm
    | StrOutputParser()
)

question_chain:Runnable = (
    ChatPromptTemplate.from_messages([
        ("system", "Generate three interesting questions about the following topic:"),
        ("user","{topic}")
    ])
    | llm
    | StrOutputParser()
)

terms_chain:Runnable = (
    ChatPromptTemplate.from_messages([
        ("message", "Identify 5-10 key terms from the following topic, seperated by commas:"),
        ("user", "{topic}")
    ])
    | llm
    | StrOutputParser()
)

# --- Build the parallel + synthesis chain ---

# --- Define Independent Chains ---
# These three chains represent distinct tasks that can be executed in parallel.

map_chain = RunnableParallel(
    {
        "summary" : summarise_chain,
        "questions" : question_chain,
        "key_terms" : terms_chain,
        "topic" : RunnablePassthrough(),
    }
)

# 2. Define the final synthesis prompt which will combine the parallel results.
synthesis_prompt = ChatPromptTemplate.from_messages([
    ("system",""" Based on the following information:
    Summary : {summary}
    Related Questions : {questions}
    Key Terms : {key_terms}
    Synthesize a comprehensive answer."""),
    ("user","Original topic:{topic}")
])

# 3. Construct the full chain by piping the parallel results directly
#    into the synthesis prompt, followed by the LLM and output parser.

full_parallel_chain = map_chain | synthesis_prompt | llm | StrOutputParser()

# Run the chain

async def run_parallel_example(topic:str) -> None:
    pass
