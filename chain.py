import os
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from prompts.system_prompt import SYSTEM_PROMPT
from prompts.schemas import MediGuideResponse

MODELS = {
    "Llama 3.3 70B (recommended)": "llama-3.3-70b-versatile",
    "GPT-OSS 120B": "openai/gpt-oss-120b",
}


def build_chain(model_name: str):
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set. Add it to your environment or .env file before using the app.")
    llm = ChatGroq(groq_api_key=api_key, model_name=model_name, temperature=0.3)
    structured_llm = llm.with_structured_output(MediGuideResponse, include_raw=True)
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder("history"),
            ("human", "{input}"),
        ]
    )
    return prompt | structured_llm
