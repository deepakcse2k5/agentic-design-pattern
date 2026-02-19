from tensorlake.documentai import DocumentAI, ParsingOptions, ChunkingStrategy
from tensorlake.documentai import TableOutputMode, StructuredExtractionOptions
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv
load_dotenv()
tensorlake_api_key= os.getenv("TENSORLAKE_API_KEY")

class Section(BaseModel):
    heading: str = Field(description="The section heading")
    summary: str = Field(description="Summary of the section content")


class ResearchPaper(BaseModel):
    title: str = Field(description="The title of the research paper")
    authors: str = Field(description="List of paper authors")
    abstract: str = Field(description="The paper's abstract")
    sections: str = Field(description="Sections with headings and summaries")

doc_ai = DocumentAI(api_key=tensorlake_api_key)
file_id = doc_ai.upload(path="/Users/deepakmishra/git/agentic-design-pattern/1706.03762v7.pdf")


reserach_paper_extraction = StructuredExtractionOptions(
    schema_name="research_paper",
    json_schema=ResearchPaper,
    provide_citations=True)
parsing_options = ParsingOptions(
    chunking_strategy= ChunkingStrategy.SECTION,
    table_output_mode= TableOutputMode.MARKDOWN
    
)

parse_id = doc_ai.parse(
    file= file_id,
    parsing_options = parsing_options,
    structured_extraction_options = reserach_paper_extraction

)

result = doc_ai.wait_for_completion(parse_id)
rag_chunks = [chunk.content for chunk in result.chunks]
extracted_data = result.structured_data


