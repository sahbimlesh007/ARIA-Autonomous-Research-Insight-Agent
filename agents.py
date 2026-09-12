from dotenv import load_dotenv

load_dotenv()

# from langchain_mistralai import ChatMistralAI
from langchain_groq import ChatGroq
from langchain.agents import create_agent

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from agentTools import webSearch, urlScrapper

from rich import print

llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0)


def search_agent():
    return create_agent(model=llm, tools=[webSearch])


def reader_agent():
    return create_agent(model=llm, tools=[urlScrapper])


writer_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an expert research writer. Write clear, structured and insightful reports.",
        ),
        (
            "human",
            """Write a detailed research report on the topic below.

Topic: {topic}

Research Gathered:
{research}

Structure the report as:
- Introduction
- Key Findings (minimum 3 well-explained points)
- Conclusion
- Sources (list all URLs found in the research)

Be detailed, factual and professional.""",
        ),
    ]
)


writer_chain = writer_prompt | llm | StrOutputParser()


critic_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a sharp and constructive research critic. Be honest and specific.",
        ),
        (
            "human",
            """Review the research report below and evaluate it strictly.

Report:
{report}

Respond in this exact format:

Score: X/10

Strengths:
- ...
- ...

Areas to Improve:
- ...
- ...

One line verdict:
...""",
        ),
    ]
)


critic_chain = critic_prompt | llm | StrOutputParser()
