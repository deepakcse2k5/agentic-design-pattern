from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableBranch, RunnableLambda
import os
from dotenv import load_dotenv

load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")

try:
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
        google_api_key=google_api_key  # optional if env is set
    )
    print(f"Language model initiated: {llm.model}")
except Exception as e:
    print(f"Error Initializing language model: {e}")
    llm = None  # only set None on failure

if llm is None:
    print("\nSkipping execution time due to LLM initialization failure.")
    raise SystemExit(1)

# Handlers
def booking_handler(request: str) -> str:
    print("\n--- DELEGATING TO BOOKING HANDLER ---")
    return f"Booking handler processed request: '{request}'. Result: Simulated booking action."

def info_handler(request: str) -> str:
    print("\n--- DELEGATING TO INFO HANDLER ---")
    return f"Info handler processed request: '{request}'. Result: Simulated information retrieval"

def unclear_handler(request: str) -> str:
    print("\n--- HANDLING UNCLEAR REQUEST ---")
    return f"Coordinator could not delegate request: '{request}'. Please clarify."

# Router
coordinator_router_prompt = ChatPromptTemplate.from_messages([
    ("system", """Analyze the user's request and determine which specialist handler should process it.
- If the request is related to booking flights or hotels, output 'booker'.
- For all other general information questions, output 'info'.
- If the request is unclear or doesn't fit either category, output 'unclear'.
ONLY output one word: 'booker', 'info', or 'unclear'."""),
    ("user", "{request}")
])
router_chain = coordinator_router_prompt | llm | StrOutputParser()

# Helpers
to_text = RunnableLambda(lambda x: x["request"])
booker_r = RunnableLambda(lambda s: booking_handler(s))
info_r = RunnableLambda(lambda s: info_handler(s))
unclear_r = RunnableLambda(lambda s: unclear_handler(s))

# Branch on computed route
branch = RunnableBranch(
    (lambda x: x["route"].strip() == "booker", to_text | booker_r),
    (lambda x: x["route"].strip() == "info",   to_text | info_r),
    to_text | unclear_r,  # default
)

# Full pipeline
coordinator_agent = (
    RunnableLambda(lambda x: {"request": x} if isinstance(x, str) else x)
    | RunnablePassthrough.assign(route=router_chain)
    | branch
)

# Demo
print(coordinator_agent.invoke({"request": "Book me a flight to London"}))
print(coordinator_agent.invoke({"request": "What is the capital of Italy?"}))
print(coordinator_agent.invoke({"request": "Maybe later"}))
