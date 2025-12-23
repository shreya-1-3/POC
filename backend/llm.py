from llama_cpp import Llama
import re


llm = Llama.from_pretrained(
    repo_id="Ellbendls/Qwen-3-4b-Text_to_SQL-GGUF",
    filename="Qwen-3-4b-Text_to_SQL-F16.gguf",
    n_ctx=4096,
    n_threads=8,       # set to number of CPU cores
    n_gpu_layers=0     # >0 only if you have GPU
)


def build_prompt(question: str, schema: str) -> str:
    return f"""
You are an expert SQLite data analyst.

TASK:
Convert the user's question into a valid SQLite SQL query.

STRICT RULES:
- Output ONLY SQL
- NO explanations
- NO markdown
- NO comments
- Query MUST start with SELECT
- Use only tables and columns from the schema

Database schema:
{schema}

User question:
{question}

SQL:
""".strip()



def extract_sql(text: str) -> str:
    if not text:
        raise ValueError("Empty LLM output")
    
    text = re.sub(r"</?s>", "", text, flags=re.IGNORECASE).strip()
    
    match = re.search(r"\bSELECT\b", text, re.IGNORECASE)
    if not match:
        raise ValueError("No SELECT keyword found in LLM output")

    sql = text[match.start():].strip()

    if ";" in sql:
        sql = sql.split(";", 1)[0] + ";"

    if not sql.lower().startswith("select"):
        raise ValueError("Extracted SQL does not start with SELECT")

    return sql


def generate_sql(question: str, schema: str) -> str:
    prompt = build_prompt(question, schema)

    output = llm(
        prompt,
        max_tokens=512,
        temperature=0.0,     
        top_p=1.0,
        stop=[";"]           
    )

    raw = output["choices"][0]["text"]
    print("\n===== LLM RAW OUTPUT =====\n", raw)

    return extract_sql(raw)



def summarize_result(question, rows):
    return f"The query returned {len(rows)} rows."
