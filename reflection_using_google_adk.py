from google_adk.agents import SequentialAgent, LlmAgent

generator = LlmAgent(
    name = "DraftWriter",
    decsription="Generated initial draft content on a given subject.",
    instruction = "Write a short, informative paragraph about the user's subject.",
    output_key = "draft_text"
)

reviewer = LlmAgent(
    name = "FactChecker",
    description= "Reviews a given text for factual accuracy and provides a structured critique.",
    instruction = """
    You are a meticulous fact-checker.
    1. Read the text provided in the state key 'draft_text'.
    2. Carefully verify the factual accuracy of all claims.
    3. Your final output must be a dictionary containing two keys:
       -"status":A string, either "ACCURATE" or "INACCURATE".
       -"reasoning": A string providing a clear explanation for your status ,citing specific issues if any are found.
       """,
    output_key = "review_output"
)

review_pipeline = SequentialAgent(
    name = "WriteAndReview_Pipeline",
    sub_agents = [generator, reviewer]
)
