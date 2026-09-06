print("===== CURRENT AFFAIRS CHATBOT =====")
print("Type 'exit' to quit.\n")

current_affairs = {
    "moon": "India is planning future missions to explore the Moon's south pole.",
    
    "chandrayaan-3": "Chandrayaan-3 successfully landed near the Moon's south pole in 2023.",
    
    "isro": "ISRO is the Indian Space Research Organisation. It is India's space research organization.",
    
    "artificial intelligence": "Artificial Intelligence is the technology that enables machines to perform tasks that normally require human intelligence.",
    
    "education": "Education plays an important role in the development of a country.",
    
    "budget": "The Union Budget of India is presented annually by the Government of India.",
    
    "sports": "Sports are an important part of a healthy lifestyle and national development.",
    
    "climate change": "Climate change is a major global challenge caused mainly by greenhouse gas emissions."
}

while True:
    question = input("You: ").lower().strip()

    if question == "exit":
        print("Bot: Thank you! Goodbye.")
        break

    elif question in current_affairs:
        print("Bot:", current_affairs[question])

    else:
        print("Bot: Sorry, I don't have information about that topic.")