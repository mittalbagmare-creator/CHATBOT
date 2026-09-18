import re
import pandas as pd

# ============================================================
# 1. TXT FILE READ
# ============================================================

FILE_NAME = "Current_Affairs_Jan_June_2026.txt"

with open(FILE_NAME, "r", encoding="utf-8") as f:
    text = f.read()


# ============================================================
# 2. REMOVE PDF HEADER / FOOTER
# ============================================================

def clean_page(page):

    lines = page.splitlines()
    clean = []

    for line in lines:
        line = line.strip()

        if not line:
            clean.append("")
            continue

        # Remove page header
        if re.match(r"^Current Affairs\s*\|", line, re.I):
            continue

        # Remove website/footer
        if "www.bankersadda.com" in line.lower():
            continue

        if "www.sscadda.com" in line.lower():
            continue

        if "www.careerpower.in" in line.lower():
            continue

        if "adda247 app" in line.lower():
            continue

        clean.append(line)

    return "\n".join(clean)


# ============================================================
# 3. FIND MONTH
# ============================================================

def find_month(page):

    match = re.search(
        r"Current Affairs\s*\|\s*(January|February|March|April|May|June)\s*2026",
        page,
        re.I
    )

    if match:
        return match.group(1).capitalize() + " 2026"

    return "Unknown"


# ============================================================
# 4. CATEGORY
# ============================================================

def find_category(page):

    p = page.lower()

    if "banking, economy" in p or "banking" in p or "rbi" in p:
        return "Banking & Economy"

    if "govt schemes" in p or "government scheme" in p:
        return "Government Schemes"

    if "international affairs" in p:
        return "International Affairs"

    if "defence" in p:
        return "Defence"

    if "science & technology" in p:
        return "Science & Technology"

    if "sports" in p:
        return "Sports"

    if "awards" in p:
        return "Awards"

    if "appointments" in p:
        return "Appointments"

    if "mou" in p or "agreements" in p:
        return "MoUs & Agreements"

    if "important days" in p:
        return "Important Days"

    return "Current Affairs"


# ============================================================
# 5. CREATE DATASET
# ============================================================

data = []


# ============================================================
# 6. EXTRACT EXPLICIT MARCH Q&A
# ============================================================

qa_start = text.find("CURRENT AFFAIRS Q&A - MARCH 2026")

if qa_start != -1:

    qa_text = text[qa_start:]

    # Stop before next major section if found
    stop_words = [
        "STATIC TAKEAWAYS",
        "Static Takeaways"
    ]

    for stop in stop_words:
        stop_pos = qa_text.find(stop)

        if stop_pos != -1:
            qa_text = qa_text[:stop_pos]
            break

    # Find every Q number
    questions = list(
        re.finditer(r"\bQ(\d+)\.\s*", qa_text)
    )

    for i, q_match in enumerate(questions):

        q_start = q_match.end()

        if i + 1 < len(questions):
            q_end = questions[i + 1].start()
        else:
            q_end = len(qa_text)

        block = qa_text[q_start:q_end]

        # Find Ans:
        ans_match = re.search(r"\bAns:\s*", block, re.I)

        if not ans_match:
            continue

        question = block[:ans_match.start()]
        answer = block[ans_match.end():]

        # Clean question
        question = " ".join(question.split())

        # Clean answer
        answer = " ".join(answer.split())

        if len(question) < 10 or len(answer) < 10:
            continue

        data.append({
            "question": question,
            "answer": answer,
            "month": "March 2026",
            "category": "Current Affairs"
        })


# ============================================================
# 7. EXTRACT ARTICLE INFORMATION FROM ALL PAGES
# ============================================================

pages = re.split(r"--- PAGE \d+ ---", text)

ignore_headings = {
    "contents",
    "most important current affairs of the month",
    "most important article of march 2026",
    "static takeaways",
    "key summary at glance",
    "why in news?",
    "mission overview and launch details",
    "planned mission profile",
    "key highlights",
    "key highlights at glance",
    "what's next?",
    "what did isro say about the anomaly?"
}


for page in pages:

    if len(page.strip()) < 200:
        continue

    month = find_month(page)

    if month == "Unknown":
        continue

    cleaned = clean_page(page)

    # Split into paragraphs
    blocks = re.split(r"\n\s*\n", cleaned)

    blocks = [
        b.strip()
        for b in blocks
        if b.strip()
    ]

    # Look for meaningful article headings
    for i in range(len(blocks) - 1):

        heading = blocks[i].strip()
        next_block = blocks[i + 1].strip()

        # Heading should be reasonably short
        if len(heading) < 15 or len(heading) > 180:
            continue

        # Ignore obvious body paragraphs
        if len(heading) > 3 and heading[-1] in ".;:":
            continue

        # Ignore page/table noise
        if heading.lower() in ignore_headings:
            continue

        if heading.lower().startswith("q"):
            continue

        if "current affairs |" in heading.lower():
            continue

        if "www." in heading.lower():
            continue

        # Next block should contain actual information
        if len(next_block) < 150:
            continue

        # Avoid duplicate headings
        question = f"What is {heading.replace(chr(10), ' ')}?"

        answer = " ".join(next_block.split())

        if len(answer) > 2000:
            answer = answer[:2000]

        category = find_category(page)

        data.append({
            "question": question,
            "answer": answer,
            "month": month,
            "category": category
        })


# ============================================================
# 8. CREATE DATAFRAME
# ============================================================

df = pd.DataFrame(data)


# ============================================================
# 9. CLEAN DATA
# ============================================================

if not df.empty:

    df["question"] = df["question"].str.replace(
        r"\s+", " ", regex=True
    ).str.strip()

    df["answer"] = df["answer"].str.replace(
        r"\s+", " ", regex=True
    ).str.strip()

    # Remove duplicate questions
    df = df.drop_duplicates(
        subset=["question"],
        keep="first"
    )

    # Remove bad questions
    df = df[
        ~df["question"].str.contains(
            r"Current Affairs\s*\|",
            case=False,
            na=False
        )
    ]

    df = df[
        ~df["question"].str.contains(
            r"www\.",
            case=False,
            na=False
        )
    ]

    df = df[
        (df["question"].str.len() >= 20) &
        (df["answer"].str.len() >= 30)
    ]


# ============================================================
# 10. SAVE CSV
# ============================================================

df.to_csv(
    "dataset.csv",
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 11. RESULT
# ============================================================

print()
print("========================================")
print(" DATASET CREATED SUCCESSFULLY")
print("========================================")
print("Total Rows:", len(df))
print()
print("Columns:")
print(list(df.columns))
print()
print("First 5 rows:")
print(df.head().to_string(index=False))
print("========================================")