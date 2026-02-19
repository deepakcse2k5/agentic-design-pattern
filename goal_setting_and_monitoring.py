import os
import re
import random
from pathlib import Path
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv, find_dotenv
from typing import List

_ = load_dotenv(find_dotenv())

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise EnvironmentError("Please set OPENAI API KEY env variable")

print("initializing OPENAI LLM gpt-4o")

llm = ChatOpenAI(model= "gpt-4o",
                 temperature=0.3,
                 openai_api_key = OPENAI_API_KEY
)
          



# Utility function
def generate_prompt(use_case:str, goals:List[str],previous_code:str="", feedback:str="") -> str:
    print(f"constructing prompt for code generation")
    base_prompt = f"""
    You are an AI coding agent.Your job is to write python code based on the following use case:
    
    Use Case:{use_case}
    
    Your goals are :
    {chr(10).join(f"-{g.strip()}" for g in goals)}
    """
    if previous_code:
        print(f"Adding previous code to the prompt for refinement")
        base_prompt += f"\nPreviously generated code:\n{previous_code}"
    if feedback:
        print(f"Including feedback for revision.")
        base_prompt += f"\nFeedback on previous version:\n{feedback}\n"
        
    base_prompt += "\nPlease return only the revised Python code.Do not include comments or explanations outside the code. "
    return base_prompt

def get_code_feedback(code:str, goals:List[str]) -> str:
    print(f" Evaluating code against the goals...")
    feedback_prompt = f"""
    You are a Python code reviewer . A Code snippet is shown below.Based on the following goals:
    {chr(10).join(f"-{g.strip()}" for g in goals)}
    
    Please critique this code and identify if the goals are met.
    Mention if improvements are needed for clarity, simplicity, correctness, edge case handling, or test coverage
    
    Code:
    {code}
    """
    return llm.invoke(feedback_prompt)

def goals_met(feedback_text:str, goals:List[str]) -> bool:
    """
    Uses the LLM to evaluate whether the goals have been met based on the feedback text.
    Return True or False (Parsed from LLM output) 

    Args:
        feedback_text (str): _description_
        goals (List[str]): _description_

    Returns:
        bool: _description_
    """
    review_prompt = f"""
    You are an AI reviewer.
    Here are the goals:
    {chr(10).join(f"- {g.strip()}" for g in goals)}
    Here is the feedback on the code:
    \"\"\"
    {feedback_text}
    \"\"\"
    
    Based on the feedback above, have the goals been met?
    
    Respond with only one word: True or False
    """
    
    response = llm.invoke(review_prompt).content.strip().lower()
    return response == "true"


def clean_code_block(code:str) -> str:
    lines = code.strip().splitlines()
    if lines and lines[0].strip().startswith(" ```"):
        lines = lines[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    return "\n".join(lines).strip()

def add_comment_header(code:str, use_case:str) -> str:
    comment = f"# This Python program implements the following use case:\n#{use_case.strip()}\n"
    return comment + "\n" + code

def to_snake_case(text:str) -> str:
    text = re.sub(r"[^a-zA-Z0-9]","",text)
    return re.sub(r"\s+","_", text.strip().lower())

def save_code_to_file(code:str, use_case:str)-> str:
    print(f" Saving final code file...")
    summary_prompt = (
        f"Summarize the following use case into a single lowercase word or phrase,"
        f"no more than 10 characters , suitable for a Python filename:\n\n{use_case}"
    )
    raw_summary = llm.invoke(summary_prompt).content.strip()
    short_name = re.sub(r"[^a-zA-Z0-9]", "", raw_summary.replace(" ","_").lower())[:10]
    random_suffix = str(random.randint(1000,9999))
    filename = f"{short_name}_{random_suffix}.py"
    filepath = Path.cwd()/filename
    
    with open(filepath,"w") as f:
        f.write(code)
    print(f" Code Saved to :{filepath}")
    
    
    
def run_code_agent(use_case:str, goals_input:str, max_iterations:int=5)-> str:
    goals = [g.strip() for g in goals_input.split(",")]
    
    print(f"\n Use Case:{use_case}")
    print("\n Goals:")
    for g in goals:
        print(f"- {g}")
    
    previous_code = ""
    feedback = ""
    for i in range(max_iterations):
        print(f"\n=== Iteration{i+1} of {max_iterations}===")
        prompt = generate_prompt(use_case, goals, previous_code, feedback if isinstance(feedback, str) else feedback.content)
        print(" Generating Code...")
        code_response = llm.invoke(prompt)
        raw_code = code_response.content.strip()
        code = clean_code_block(raw_code)
        print("\n Submitting code for feedback review..")
        feedback = get_code_feedback(code, goals)
        feedback_text = feedback.content.strip()
        print("\n Feedback Received:\n" + "-" *50 + f"\n{feedback_text}\n"+"-"*50)
        
        if goals_met(feedback_text,goals):
            print(f" LLM Conforms goal met .Stopping iteration")
            break
        print(f"goals not fully met . Preparing for next iteration...")
        previous_code = code
        
    final_code = add_comment_header(code, use_case)
    return save_code_to_file(final_code, use_case)


if __name__=="__main__":
    print(f"\n Welcome to AI code generation agent")
    
    # Eaxmple 1
    # use_case_input = "Write code to find BinaryGap of a given positive integer"
    # goals_input = "Code simple to understand , Functionally correct , Handles comprehensive edge cases, Takes positive integer input only, prints the results with few examples"
    # run_code_agent(use_case_input, goals_input)
    
    # Example 2
    # use_case_input = "Write code to count the number of files in current directory and all its nested directories, and print the total count"
    
    # goals_input = ("Code simple to understand , Functionally correct , Handles comprehensive edge cases, Ignore recommendations for test suite use like unittest or pytest")
    # run_code_agent(use_case_input, goals_input)
    
    use_case_input = "Write code which takes a command line input of a word doc or docx file and opens it and counts the number of words , and characters in it and prints all "
    goals_input = "Code simple to understand , Functionally correct , Handles comprehensive edge cases"
    run_code_agent(use_case_input, goals_input)
