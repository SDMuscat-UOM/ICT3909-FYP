import pandas as pd

# Load only the url and body columns from csv needed
df = pd.read_csv("articles/society_and_culture.csv", usecols=["url", "body"])

# Select the top 20 entries - or as many as needed
top20 = df.head(20)

# Write output to top_20.txt (overwrite mode)
with open("top_20.txt", "w", encoding="utf-8") as outfile:
    for _, row in top20.iterrows():
        outfile.write(f"URL: {row['url']}\n\n")
        outfile.write(f"Body:\n{row['body']}\n\n")
        outfile.write("-" * 80 + "\n")
