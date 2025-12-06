import json
import os
import unicodedata
import re

# ------------ CONFIG ------------
INPUT_FILE = "recipes.json"  # the file where all recipes exist
OUTPUT_DIR = "recipes"       # folder where individual files will be saved
# --------------------------------


def clean_filename(name: str) -> str:
    """
    Converts a recipe name into a safe filename:
    - lowercase
    - replace spaces with underscores
    - remove accents
    - keep only letters, numbers, and underscores
    """
    # lowercase
    name = name.lower()

    # remove accents
    name = ''.join(
        c for c in unicodedata.normalize('NFD', name)
        if unicodedata.category(c) != 'Mn'
    )

    # replace spaces with underscores
    name = name.replace(" ", "_")

    # keep only letters, digits, and underscores
    name = re.sub(r"[^a-z0-9_]", "", name)

    return name


def main():
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Load the full recipe JSON
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    recipes = data.get("recipes", [])

    for idx, recipe in enumerate(recipes, start=1):
        clean_name = clean_filename(recipe["name"])
        numbered_name = f"{idx}_{clean_name}.json"
        output_path = os.path.join(OUTPUT_DIR, numbered_name)

        # Write each recipe to its own JSON file
        with open(output_path, "w", encoding="utf-8") as out:
            json.dump(recipe, out, indent=2, ensure_ascii=False)

        print(f"Created: {output_path}")

    print("\nDone! All recipes have been split into individual numbered JSON files.")


if __name__ == "__main__":
    main()
