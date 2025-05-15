import csv
import os
from collections import defaultdict

# Existing category→keywords mapping
categories = {
    "Politics": ["Politics", "Robert Abela", "European Parliament", "Government", "PL", "PN", "Bernard Grech", "Elections 2024", "Rule of Law", "Parliament", "European Union", "Democracy", "Diplomacy", "Elections"],
    "Crime & Justice": ["Court", "Police", "Crime", "Domestic Violence", "Murder", "Drugs", "Prison", "Cybercrime", "Harassment", "Human Trafficking", "Prostitution", "Justice"],
    "Health & Medicine": ["Health", "Mental Health", "Pharmaceuticals", "Reproductive Health", "Fertility", "Covid-19", "Hospitals Deal", "Euthanasia"],
    "Business & Finance": ["Banking", "Business", "Commerce", "Finance", "Financial Markets", "Economy", "Retail", "Taxation", "MFSA", "Central Bank", "Corporate Governance", "Pensions", "Fintech"],
    "Technology & Science": ["Artificial Intelligence", "Space", "Science", "Technology", "Cybercrime", "Data Privacy"],
    "Environment & Climate": ["Environment", "Climate Change", "Conservation", "Alternative Energy", "Waste", "Pollution", "Natural Disaster"],
    "International News": ["Palestine", "Russia", "Ukraine", "European Union", "United Nations", "Middle East", "USA", "UK", "China", "Lebanon", "Saudi Arabia", "France", "Germany", "Italy", "Australia", "Canada", "Turkey", "Thailand", "Sweden", "Scotland", "Brazil", "Slovakia", "Ethiopia", "Morocco", "Norway", "Romania", "Spain", "Colombia", "Hungary", "India", "Malta Abroad"],
    "Society & Culture": ["Social and Personal", "Community", "Religion", "Charity", "Racism", "Gender", "LGBTIQ", "Poverty", "Migration", "Parenting", "Disability", "Civil Society", "Identità"],
    "Education & Research": ["Education", "Research", "University", "MCAST", "Data and Surveys", "Statistics"],
    "Entertainment & Media": ["Media", "Music", "Film", "Eurovision", "Theatre", "Entertainment", "Art", "Photography", "Cartoons", "Social Media", "TV", "Literature/Books"],
    "Sports": ["Sports", "Football", "Olympics", "Athletics", "Waterpolo", "Shooting (Sport)", "Swimming", "Horse Racing", "Boxing", "Esports", "Cycling"],
    "Infrastructure & Transport": ["Construction", "Roads", "Transport", "Aviation", "Maritime", "Infrastructure", "Traffic", "Electric Vehicles", "Planning Authority"],
    "Economy & Trade": ["Employment", "Unions", "Trade", "Tourism", "Hotels/Hostels/Airbnb", "Catering", "Food and Drink"],
}

def assign_category(tags_str):
    tags = [t.strip().lower() for t in tags_str.split(',') if t.strip()]
    for category, keywords in categories.items():
        for kw in keywords:
            if kw.lower() in tags:
                return category
    return "No Tags"

def filename_for(category):
    return category.lower().replace(" ", "_").replace("&", "and") + ".csv"

def reassign_no_tags():
    rows_to_move = defaultdict(list)
    remaining = []

    with open("no_tags.csv", newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        headers = reader.fieldnames
        for row in reader:
            category = assign_category(row.get("tags", ""))
            if category != "No Tags":
                rows_to_move[category].append(row)
            else:
                remaining.append(row)

    # Append moved rows to each category file
    for category, rows in rows_to_move.items():
        out_file = filename_for(category)
        file_exists = os.path.isfile(out_file)
        with open(out_file, "a", newline="", encoding="utf-8") as fout:
            writer = csv.DictWriter(fout, fieldnames=headers)
            if not file_exists:
                writer.writeheader()
            writer.writerows(rows)
        print(f"Moved {len(rows)} rows → {out_file}")

    # Overwrite no_tags.csv with remaining rows
    with open("no_tags.csv", "w", newline="", encoding="utf-8") as nofile:
        writer = csv.DictWriter(nofile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(remaining)
    print(f"{len(remaining)} rows remain in no_tags.csv")

if __name__ == "__main__":
    reassign_no_tags()
