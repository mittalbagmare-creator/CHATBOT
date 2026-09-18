import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Dataset load karo
df = pd.read_csv("dataset.csv")

# Empty values ko remove karo
df = df.dropna(subset=["question", "answer"])

# Questions ko TF-IDF mein convert karo
vectorizer = TfidfVectorizer(
    lowercase=True,
    stop_words="english"
)

question_vectors = vectorizer.fit_transform(
    df["question"]
)

print("===================================")
print(" CURRENT AFFAIRS NLP CHATBOT")
print("===================================")
print("Ask your question.")
print("Type 'exit' to stop.")
print()

while True:

    user_question = input("You: ")

    if user_question.lower() == "exit":
        print("Bot: Thank you! Goodbye.")
        break

    # User question ko vector mein convert karo
    user_vector = vectorizer.transform([user_question])

    # Similarity calculate karo
    similarity = cosine_similarity(
        user_vector,
        question_vectors
    )

    # Highest similarity wala question
    best_match = similarity.argmax()

    score = similarity[0][best_match]

    # Answer
    if score < 0.15:
        print("Bot: Sorry, I could not find a relevant answer.")

    else:
        answer = df.iloc[best_match]["answer"]
        month = df.iloc[best_match]["month"]
        category = df.iloc[best_match]["category"]

        print()
        print("Bot:", answer)
        print("Month:", month)
        print("Category:", category)
        print()