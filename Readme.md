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

bash
Copy
Edit
ngrok http 5050
Update .env file
Copy the HTTPS URL from ngrok (e.g., https://abc123.ngrok.io) and paste it into your .env file:

.env
Copy
Edit
NGROK_URL=https://your-ngrok-url.ngrok.io

update this also:- 
# Get your Google API Key from Google AI Studio: https://aistudio.google.com/app/apikey
GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY_HERE"

# Your ngrok public URL (without https://)
NGROK_URL="xxxxxxxx.ngrok-free.app"

# https://console.twilio.com/?frameUrl=%2Fconsole%3Fx-target-region%3Dus1
TWILIO_ACCOUNT_SID="ACe9cb6*****************"

# Twilio auth token       
TWILIO_AUTH_TOKEN="028510dc946***************"

# https://console.twilio.com/?frameUrl=%2Fconsole%3Fx-target-region%3Dus1                         
TWILIO_PHONE_NUMBER=+180******

# Your Port                         
PORT=5050

Run the App
In another terminal, start the FastAPI server:

bash
Copy
Edit

python main.py
Initiate the Call
Enter your phone number in the terminal when prompted. The assistant will place a call and interact in real-time.


