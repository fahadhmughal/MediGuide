# 🩺 MediGuide — AI Symptom-to-Specialist Navigator

Helps users identify which type of medical specialist to see, and generates
a downloadable PDF of questions to ask at the appointment.

> Not a diagnostic tool. Always consult a licensed physician. In an
> emergency, contact local emergency services immediately.

## Architecture

```
app.py                   Streamlit UI + orchestration
chain.py                 LangChain LCEL chain (prompt | llm | structured output)
prompts/system_prompt.py System persona and behavior rules
prompts/schemas.py       Pydantic schema the LLM output is parsed into
pdf_generator.py         Builds the appointment-questions PDF (fpdf2)
```

The LLM is bound to a Pydantic schema (`MediGuideResponse`) via
`with_structured_output`, so every reply is one of:
`clarifying_question` (exactly one question), `specialist_recommendation`
(with a question list for the PDF), or `emergency`.

## Setup

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add your Groq API key
streamlit run app.py
```

Get a free key at [console.groq.com](https://console.groq.com) (no card
required).

## Deployment

Push to GitHub, deploy on [share.streamlit.io](https://share.streamlit.io),
set `GROQ_API_KEY` under Settings → Secrets.

## Notes

- Model can be switched in the sidebar between Llama 3.3 70B and GPT-OSS 120B
  for comparison — useful for prompt engineering write-ups.
- "Gather Model Info" in the sidebar shows session token usage and last
  response latency.
- PDF download uses `st.download_button` with in-memory bytes, not a file
  link, so it works reliably in deployed environments.
