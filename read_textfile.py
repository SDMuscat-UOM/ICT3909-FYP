import csv
import re

def extract_gender_counts(filename):
    """
    Extracts all "Male: X Female: Y Unknown: Z" counts from the given text file,
    returning a list of strings formatted exactly as in the CSV.
    """
    pattern = re.compile(r'Male:\s*(\d+)\s*Female:\s*(\d+)\s*Unknown:\s*(\d+)')
    with open(filename, 'r', encoding='utf-8') as f:
        text = f.read()
    matches = pattern.findall(text)
    # Re-format each match into the desired single-line string
    return [f"Male: {m} Female: {f} Unknown: {u}" for m, f, u in matches]

def merge_counts_into_csv(counts, 
                          input_csv='annotations2_clean.csv',
                          output_csv='annotations2_clean.csv'):
    """
    Reads the input CSV, replaces the Named Entity Recognition column in the
    first len(counts) rows with the provided counts, and writes out the result.
    """
    rows = []
    with open(input_csv, newline='', encoding='utf-8') as infile:
        reader = csv.reader(infile)
        header = next(reader)
        rows = list(reader)
    
    # Index of the "Named Entity Recognition" column
    ner_col_idx = header.index("Named Entity Recognition")
    
    # Replace the column for the first N rows
    for i, count in enumerate(counts):
        if i < len(rows):
            rows[i][ner_col_idx] = count
        else:
            break
    
    # Write out the final CSV
    with open(output_csv, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(header)
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to '{output_csv}' (NER column updated for first {len(counts)} entries).")

if __name__ == '__main__':
    # Step 1: extract counts from the text file
    counts = extract_gender_counts('ner_gender_results.txt')
    # Step 2: merge into CSV
    merge_counts_into_csv(counts)