
from pathlib import Path
import re

ROOT = Path(__file__).parent


def clean_text(text):
    # Remove Markdown links but keep their readable labels
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)

    # Remove Markdown heading and bullet markers
    text = re.sub(r"^#{1,6}\s*", "", text)
    text = re.sub(r"^\s*[-*+]\s*", "", text)

    return text.strip()


def search_knowledge(question):
    # Ignore common words that don't help identify the topic
    stop_words = {
        "what", "are", "the", "is", "a", "an", "for",
        "of", "to", "in", "on", "and", "how", "does"
    }

    keywords = [
        word.lower()
        for word in re.findall(r"\b\w+\b", question)
        if word.lower() not in stop_words
    ]

    results = []

    for file_path in ROOT.rglob("*.md"):
        if any(
            part.startswith(".")
            for part in file_path.relative_to(ROOT).parts
        ):
            continue

        if file_path.name == "index.md":
            continue

        lines = file_path.read_text(
            encoding="utf-8-sig"
        ).splitlines()

        # Skip YAML frontmatter
        if lines and lines[0].strip() == "---":
            try:
                end = next(
                    i for i in range(1, len(lines))
                    if lines[i].strip() == "---"
                )
                lines = lines[end + 1:]
            except StopIteration:
                pass

        # Score the whole document, not just individual lines
        document_text = " ".join(
            clean_text(line) for line in lines
        ).lower()

        score = sum(
            1 for keyword in keywords
            if keyword in document_text
        )

        if score > 0:
            results.append((score, file_path, lines))

    results.sort(key=lambda item: item[0], reverse=True)

    return results[:3]


if __name__ == "__main__":
    question = input("Ask your knowledge bundle a question: ")

    results = search_knowledge(question)

    if results:
        print("\nRelevant knowledge:\n")

        for score, file_path, lines in results:
            print(f"Source: {file_path.relative_to(ROOT)}")

            for line in lines:
                text = clean_text(line)

                if text:
                    print(f"- {text}")

            print()
    else:
        print("No matching knowledge found.")
