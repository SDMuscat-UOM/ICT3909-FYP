import pandas as pd
import subprocess

# Maltese → ASCII map
MALTESE_MAP = str.maketrans({
    "ċ": "c", "Ċ": "C",
    "ġ": "g", "Ġ": "G",
    "ħ": "h", "Ħ": "H",
    "ż": "z", "Ż": "Z"
})

def clean_text(text: str) -> str:
    cleaned = text.translate(MALTESE_MAP)
    return cleaned.encode("ascii", "ignore").decode("ascii")

# Load CSV and select top 75 articles
df = pd.read_csv("articles/society_and_culture.csv", usecols=["url", "body"])
top75 = df.head(75)

prompt_template = """
You are a data‑extraction assistant. From the news article below, identify each unique individual exactly once (if someone is later referred to by surname only, treat it as the same person). Determine their gender using name‑based and contextual clues. Do NOT list names — only count unique people. Return exactly three lines (no extra text or punctuation), using integer counts:

Male: <count>
Female: <count>
Unknown: <count>

Article:
{}
""".strip()

# Open file in append mode so that new output is added to the end of the file
with open("model_thinking.txt", "a", encoding="utf-8") as outfile:
    # Iterate through each article with a counter
    for i, (_, row) in enumerate(top75.iterrows(), start=1):
        print(f"On Article {i}")
        article_url = row["url"]
        article_body = clean_text(row["body"])
        prompt = prompt_template.format(article_body)
        
        proc = subprocess.run(
            ["ollama", "run", "deepseek-r1:32b"],
            input=prompt.encode("utf-8"),
            capture_output=True
        )
        
        # Write URL and output to file
        outfile.write(f"URL: {article_url}\n")
        outfile.write(f"Society75\n")  # CHANGE THIS FOR EACH RUN if needed
        if proc.returncode == 0:
            outfile.write(proc.stdout.decode("utf-8").strip() + "\n")
        else:
            outfile.write(f"Error ({proc.returncode}): {proc.stderr.decode('utf-8').strip()}\n")
        outfile.write("-" * 60 + "\n")
