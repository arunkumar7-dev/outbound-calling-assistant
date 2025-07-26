# 📞 Outbound Calling Assistant

An AI-powered outbound calling assistant built using **Twilio**, **Google Gemini**, **FastAPI**, and **WebSockets**. It handles real-time voice streaming, converts speech to text, generates intelligent AI responses, and speaks them back to the caller—all during an active outbound call.

---

## 🚀 Features

- 🔊 Real-time voice interaction over phone calls
- 🧠 AI-generated replies using Gemini
- 📝 Speech-to-Text & 🗣️ Text-to-Speech using Twilio ConversationRelay 
- 🔐 Environment variable handling using `.env`

---

## 
---

## 🧪 Use Cases

- 🤖 Automated outbound customer support calls & more

---


🛠️ How to Run
Start ngrok
Open a terminal and run:

  bash :- 

ngrok http 5050
Update .env file (pls check dummy .env file for refrence)

Copy the HTTPS URL from ngrok (e.g., https://abc123.ngrok.io) and paste it into your .env file:

Terminal :-

  - python main.py
    
    "Enter your phone number in the terminal when prompted. The assistant will place a call and interact in real-time."


