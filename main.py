import os
import json
import asyncio
from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse, Response
from fastapi.websockets import WebSocketDisconnect
from twilio.rest import Client
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

# Configuration
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
NGROK_URL = os.getenv('NGROK_URL')
PORT = int(os.getenv('PORT', 5050))

if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER, NGROK_URL, GOOGLE_API_KEY]):
    raise ValueError("One or more environment variables (Twilio credentials, NGROK_URL, GOOGLE_API_KEY) not fully set in .env")

# Construct the WebSocket URL for Twilio Media Stream
# Twilio requires wss:// for secure connections
WS_URL = f"wss://{NGROK_URL.replace('https://', '')}/ws"

twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

WELCOME_GREETING = "Hi! I am a voice assistant Developed by Arun Kumar. Ask me anything!"

SYSTEM_PROMPT = """You are a helpful and friendly voice assistant. This conversation is happening over a phone call, so your responses will be spoken aloud.
Please adhere to the following rules:
1. Provide clear, concise, and direct answers.
2. Spell out all numbers (e.g., say 'one thousand two hundred' instead of 1200).
3. Do not use any special characters like asterisks, bullet points, or emojis.
4. Keep the conversation natural and engaging."""

app = FastAPI()

genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel(
    model_name='gemini-2.5-flash',
    system_instruction=SYSTEM_PROMPT
)

# Dictionary to store chat sessions per call SID
sessions = {}

@app.get("/", response_class=HTMLResponse)
async def index_page():
    return HTMLResponse(content="<h1>Twilio Media Stream Server is running!</h1>", status_code=200)

@app.post("/make-call")
async def make_call(request: Request):
    """Make an outgoing call to the specified phone number."""
    data = await request.json()
    to_phone_number = data.get("to")
    if not to_phone_number:
        return {"error": "Phone number is required"}

    try:
        call = twilio_client.calls.create(
            # url points to your TwiML endpoint that initiates the stream
            url=f"{NGROK_URL}/twiml",
            to=to_phone_number,
            from_=TWILIO_PHONE_NUMBER
        )
        return {"call_sid": call.sid}
    except Exception as e:
        print(f"Error initiating call: {e}")
        return {"error": f"Failed to make call: {e}"}

async def gemini_response(chat_session, user_prompt):
    """
    Sends the user prompt to Gemini and returns the response.
    Uses asyncio.to_thread to run the synchronous send_message call without blocking.
    """
    try:
        response = await asyncio.to_thread(chat_session.send_message, user_prompt)
        return response.text
    except Exception as e:
        print(f"Error getting Gemini response: {e}")
        return "I'm sorry, I'm having trouble understanding you right now."

@app.post("/twiml")
async def twiml_endpoint():
    """Endpoint that returns TwiML for Twilio to connect to the WebSocket"""
    # Twilio ConversationRelay has built-in TTS. We specify a provider and voice.
    # You can change 'ElevenLabs' to 'Amazon' or 'Google' if you prefer their TTS.
    xml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
    <Response>
    <Connect>
    <ConversationRelay url="{WS_URL}" welcomeGreeting="{WELCOME_GREETING}" ttsProvider="ElevenLabs" voice="FGY2WhTYpPnrIDTdsKH5" />
    </Connect>
    </Response>"""
    
    return Response(content=xml_response, media_type="text/xml")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication"""
    await websocket.accept()
    call_sid = None
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "setup":
                call_sid = message["callSid"]
                print(f"Setup for call: {call_sid}")
                # Start a new chat session for this call
                sessions[call_sid] = model.start_chat(history=[])
                
            elif message["type"] == "prompt":
                if not call_sid or call_sid not in sessions:
                    print(f"Error: Received prompt for unknown call_sid {call_sid}")
                    continue

                user_prompt = message["voicePrompt"]
                print(f"Processing prompt: {user_prompt}")
                
                chat_session = sessions[call_sid]
                response_text = await gemini_response(chat_session, user_prompt)
                
                # The chat_session object automatically maintains history.
                
                # Send the complete response back to Twilio.
                # Twilio's ConversationRelay will handle the text-to-speech conversion.
                await websocket.send_text(
                    json.dumps({
                        "type": "text",
                        "token": response_text,
                        "last": True  # Indicate this is the full and final message
                    })
                )
                print(f"Sent response: {response_text}")
                
            elif message["type"] == "interrupt":
                print(f"Handling interruption for call {call_sid}.")
                
            else:
                print(f"Unknown message type received: {message['type']}")
                
    except WebSocketDisconnect:
        print(f"WebSocket connection closed for call {call_sid}")
        if call_sid in sessions:
            sessions.pop(call_sid)
            print(f"Cleared session for call {call_sid}")

if __name__ == "__main__":
    import uvicorn

    print(f"Twilio Media Stream Server starting on port {PORT}...")
    print(f"Ensure your NGROK_URL is set to {NGROK_URL}")
    print(f"Twilio TwiML Endpoint: {NGROK_URL}/twiml")
    print(f"Twilio WebSocket Endpoint: {WS_URL}")


    to_phone_number = input("Please enter the phone number to call (e.g., +1234567890): ")
    if to_phone_number:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        try:
            # This will trigger the /twiml endpoint
            call = client.calls.create(
                url=f"{NGROK_URL}/twiml",
                to=to_phone_number,
                from_=TWILIO_PHONE_NUMBER
            )
            print(f"Call initiated with SID: {call.sid}")
        except Exception as e:
            print(f"Error initiating call: {e}")
    else:
        print("No phone number provided, skipping outgoing call initiation.")

    uvicorn.run(app, host="0.0.0.0", port=PORT)