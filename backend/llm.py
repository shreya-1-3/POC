from llama_cpp import Llama
import re

# -------------------------------
# Load LLM ONCE at startup
# -------------------------------
llm = Llama.from_pretrained(
    repo_id="Ellbendls/Qwen-3-4b-Text_to_SQL-GGUF",
    filename="Qwen-3-4b-Text_to_SQL-F16.gguf",
    n_ctx=4096,
    n_threads=8,       # set to number of CPU cores
    n_gpu_layers=0     # >0 only if you have GPU
)

# -------------------------------
# Prompt builder
# -------------------------------
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


# -------------------------------
# SQL extractor (robust)
# -------------------------------
def extract_sql(text: str) -> str:
    if not text:
        raise ValueError("Empty LLM output")

    # Remove special tokens if any
    text = re.sub(r"</?s>", "", text, flags=re.IGNORECASE).strip()

    # Find first SELECT anywhere in output
    match = re.search(r"\bSELECT\b", text, re.IGNORECASE)
    if not match:
        raise ValueError("No SELECT keyword found in LLM output")

    # Extract everything from SELECT onward
    sql = text[match.start():].strip()

    # Keep only first SQL statement (safety)
    if ";" in sql:
        sql = sql.split(";", 1)[0] + ";"

    # Final safety check
    if not sql.lower().startswith("select"):
        raise ValueError("Extracted SQL does not start with SELECT")

    return sql


# -------------------------------
# SQL generation
# -------------------------------
def generate_sql(question: str, schema: str) -> str:
    prompt = build_prompt(question, schema)

    output = llm(
        prompt,
        max_tokens=512,
        temperature=0.0,     # CRITICAL for SQL accuracy
        top_p=1.0,
        stop=[";"]           # stop generation after SQL
    )

    raw = output["choices"][0]["text"]
    print("\n===== LLM RAW OUTPUT =====\n", raw)

    return extract_sql(raw)


# -------------------------------
# Result summarization (optional)
# -------------------------------
def summarize_result(question, rows):
    return f"The query returned {len(rows)} rows."
