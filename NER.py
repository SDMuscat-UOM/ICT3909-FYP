import spacy
import pandas as pd
import string
from transformers import pipeline

# Load the CSV file with the articles
df = pd.read_csv("articles/society_and_culture.csv")

# Load spaCy model for sentence segmentation only
nlp = spacy.load("en_core_web_sm")

# Initialise transformer-based NER pipeline using the recommended model
ner_pipeline = pipeline("ner", model="Jean-Baptiste/roberta-large-ner-english", aggregation_strategy="simple")

# Initialise zero-shot classifier for gender classification
gender_classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# Define common titles to remove from names.
titles = {"judge", "mr.", "mrs.", "ms.", "miss", "dr.", "prof.", "il-", "l-", "triq", "perit"}

# Expanded list of Maltese localities (in lowercase, no punctuation)
maltese_places = {
    "valletta", "floriana", "sliema", "st julians", "st. julians", "gzira", "msida",
    "birkirkara", "qormi", "rabat", "mdina", "marsa", "żabbar", "zabbar", "żejtun", "zejtun",
    "żurrieq", "zurrieq", "birżebbuġa", "birzebbuga", "paola", "fgura", "marsaxlokk", "qrendi",
    "san gwann", "san ġwann", "attard", "balzan", "lija", "marsaskala", "mqabba", "siġġiewi", "siggiewi",
    "kalkara", "kirkop", "pembroke", "swieqi", "mġarr", "mosta", "għargħur", "bormla",
    "birgu", "vittoriosa", "senglea", "cospicua", "għajn tuffieħa", "gozo", "għawdex", "xlendi",
    "maltese", "malti", "malta", "għawdix", "chadwick lakes", "għar lapsi"
}

non_person_keywords = {
    "annexe", "ngo", "hotel", "graffiti", "heritage", "biodiversity", "society",
    "group", "club", "foundation", "association"
}

def normalise_gender(gender_string):
    mapping = {
        "male": "male",
        "mostly_male": "male",
        "female": "female",
        "mostly_female": "female",
        "andy": "unknown",
        "unknown": "unknown"
    }
    return mapping.get(gender_string, "unknown")

def refine_name(name_text):
    tokens = name_text.split()
    refined_tokens = [token for token in tokens if token.lower().strip(string.punctuation) not in titles]
    return refined_tokens[0] if refined_tokens else tokens[0]

def remove_titles(name_text):
    tokens = name_text.split()
    refined_tokens = [token for token in tokens if token.lower().strip(string.punctuation) not in titles]
    return " ".join(refined_tokens)

def get_last_name(entity_text):
    tokens = " ".join(entity_text.split()).split()
    for token in reversed(tokens):
        token_clean = token.lower().strip(string.punctuation)
        if token_clean not in titles:
            return token_clean
    return tokens[-1].lower().strip(string.punctuation)

def get_wider_context(entity, doc):
    context_sentences = []
    sents = list(doc.sents)
    for idx, sent in enumerate(sents):
        if sent.start_char <= entity["start"] and sent.end_char >= entity["end"]:
            if idx > 0:
                context_sentences.append(sents[idx - 1].text)
            context_sentences.append(sent.text)
            if idx < len(sents) - 1:
                context_sentences.append(sents[idx + 1].text)
            break
    return " ".join(context_sentences)

def transformer_context_gender(context_text):
    candidate_labels = ["male", "female", "unknown"]
    result = gender_classifier(context_text, candidate_labels)
    return result["labels"][0]

def is_valid_person(ent):
    text = " ".join(ent["word"].split()).strip()
    if text.lower().strip(string.punctuation) in maltese_places:
        return False
    if text.split()[0].lower().strip(string.punctuation) in {"triq", "il-", "l-"}:
        return False
    if any(keyword in text.lower() for keyword in non_person_keywords):
        return False
    return True

# Open a file to write the results
with open("ner_gender_results.txt", "w", encoding="utf-8") as out_file:
    for idx, row in df.head(75).iterrows():
        article_title = row["title"]
        article_url   = row["url"]
        article_body  = row["body"]
        
        doc = nlp(article_body)
        
        out_file.write("=" * 80 + "\n")
        out_file.write(f"Article: {article_title}\n")
        out_file.write(f"Link:    {article_url}\n")
        
        surname_to_gender = {}
        results = []
        gender_summary = {"male": 0, "female": 0, "unknown": 0}
        
        entities = ner_pipeline(article_body)
        person_entities = [ent for ent in entities if ent["entity_group"] == "PER"]
        full_entities = [ent for ent in person_entities if len(ent["word"].split()) > 1]
        single_entities = [ent for ent in person_entities if len(ent["word"].split()) == 1]
        
        for ent in full_entities:
            if not is_valid_person(ent):
                continue
            
            last_name = get_last_name(ent["word"])
            if last_name in surname_to_gender:
                continue
            
            refined_entity = remove_titles(ent["word"])
            context_text = get_wider_context(ent, doc)
            ctx_gender = transformer_context_gender(context_text)
            final_gender = ctx_gender if ctx_gender != "unknown" else "unknown"
            
            surname_to_gender[last_name] = final_gender
            gender_summary[final_gender] += 1
            results.append(f"Name: {refined_entity} - Gender Guess: {final_gender}")
        
        for ent in single_entities:
            if not is_valid_person(ent):
                continue
            
            last_name = " ".join(ent["word"].split()).lower().strip(string.punctuation)
            if last_name in surname_to_gender:
                continue
            
            refined_entity = remove_titles(ent["word"])
            context_text = get_wider_context(ent, doc)
            ctx_gender = transformer_context_gender(context_text)
            final_gender = ctx_gender if ctx_gender != "unknown" else "unknown"
            
            surname_to_gender[last_name] = final_gender
            gender_summary[final_gender] += 1
            results.append(f"Name: {refined_entity} - Gender Guess: {final_gender}")
        
        for res in results:
            out_file.write(res + "\n")
        
        out_file.write("\nSummary:\n")
        out_file.write(f"Male: {gender_summary['male']} Female: {gender_summary['female']} Unknown: {gender_summary['unknown']}\n")
        out_file.write("=" * 80 + "\n\n")

print("NER + Gender classification results written to 'ner_gender_results.txt'.")