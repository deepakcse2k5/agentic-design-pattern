from langchain_openai import  ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os
from dotenv import load_dotenv



load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")



llm = ChatOpenAI(api_key=openai_api_key, temperature=0)
# prompt 1
prompt_extract = ChatPromptTemplate.from_template(
"Extract the technical specifications from the following text:\n\n{text_input}")

# prompt 2
prompt_transform = ChatPromptTemplate.from_template(
    "Transform the following specifications into an excel with 'cpu' , 'memory', and 'storage' as columns:\n\n{specifications}"
)

# Build the chain using LCEL

extraction_chain = prompt_extract | llm | StrOutputParser()

full_chain = (
    {"specifications": extraction_chain}
    | prompt_transform
    | llm
    | StrOutputParser()
)

# Run the chain
input_text = " The new laptop model features a 3.5 GHz octacore processor , 16 GB of RAM , and a 1 TB NVMe SSD."

# Execute the chain with the input text dictionary

final_result = full_chain.invoke({"text_input" : input_text})

print(f"result: {final_result}")



