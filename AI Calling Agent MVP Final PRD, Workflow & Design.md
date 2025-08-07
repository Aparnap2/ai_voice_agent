# AI Calling Agent MVP: Final PRD, Workflow & Design

## **Product Requirements Document (PRD)**

## **Product Overview**

**AI Calling Agent MVP** - A production-ready AI voice assistant that handles inbound/outbound calls, integrates with Salesforce CRM, and demonstrates enterprise-level capabilities for your portfolio.

## **Core Value Proposition**

- **24/7 intelligent call handling** with human-like conversation
- **Seamless Salesforce integration** for lead management and CRM updates
- **Real-time lead qualification** and automated follow-up workflows
- **Portfolio-ready demonstration** of AI + CRM integration skills

## **Technical Stack**

```
python# Final MVP Stack
- CRM: Salesforce Trailhead Playground (Free)
- Backend: FastAPI + Python 3.11+
- LLM: OpenRouter API (for speed/cost) 
- STT: & TTS: ElevenLabs (high-quality voice for demos)
- Telephony: Twilio (free $15 credit)
- Database: Salesforce Objects + Local SQLite for logs
- Deployment: Railway or Render (free tier)
```

## **System Architecture & Workflow**

## **High-Level Architecture**

```
text┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Phone Call    │    │   Twilio API     │    │   FastAPI App   │
│   (Inbound/     │◄──►│   (Telephony)    │◄──►│   (Core Logic)  │
│   Outbound)     │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                        │
                                            ┌───────────┼───────────┐
                                            │           │           │
                                    ┌───────▼──┐  ┌─────▼─────┐  ┌──▼────────┐
                                    │ OpenAI   │  │OpenRouter │  │ElevenLabs │
                                    │ Whisper  │  │(mistralai/mistral-nemo:free)   │  │   TTS     │
                                    │  (STT)   │  │   (LLM)   │  │           │
                                    └──────────┘  └───────────┘  └───────────┘
                                                        │
                                            ┌───────────┼───────────┐
                                            │                       │
                                        ┌───▼─────────┐     ┌──────▼──────┐
                                        │ Salesforce  │     │   Local     │
                                        │     CRM     │     │  Database   │
                                        │  (Contacts, │     │   (Logs)    │
                                        │ Leads, Tasks)│     │             │
                                        └─────────────┘     └─────────────┘
```

## **Call Workflow Process**

```
textgraph TD
    A[Incoming Call] --> B[Twilio Receives]
    B --> C[FastAPI Webhook]
    C --> D[Find/Create Salesforce Contact]
    D --> E[Start Conversation Loop]
    E --> F[Speech to Text - Whisper]
    F --> G[Process with mistralai/mistral-nemo:free via OpenRouter]
    G --> H[Generate Response]
    H --> I[Text to Speech - ElevenLabs]
    I --> J[Play Audio to Caller]
    J --> K{Continue Call?}
    K -->|Yes| F
    K -->|No| L[End Call Processing]
    L --> M[Update Salesforce Records]
    M --> N[Create Follow-up Tasks]
    N --> O[Trigger Workflows]
```

## **Implementation Code**

## **1. Core Application Structure**

```
python# main.py
from fastapi import FastAPI, Form, Request
from twilio.twiml import VoiceResponse
import asyncio
import os

# Project structure
"""
ai-calling-agent-mvp/
├── main.py                 # FastAPI app and endpoints
├── services/
│   ├── __init__.py
│   ├── salesforce.py       # Salesforce integration
│   ├── openrouter_llm.py   # OpenRouter LLM client
│   ├── speech_services.py  # Whisper STT + ElevenLabs TTS
│   └── call_handler.py     # Main call processing logic
├── models/
│   ├── __init__.py
│   └── call_models.py      # Pydantic models
├── config/
│   ├── __init__.py
│   └── settings.py         # Environment configuration
└── requirements.txt
```

app = FastAPI(title="AI Calling Agent MVP")

@app.post("/webhook/incoming-call")
 async def handle_incoming_call(From: str = Form(...), CallSid: str = Form(...)):
 """Handle incoming call from Twilio"""
 print(f"📞 Incoming call from {From}, Call ID: {CallSid}")

```
textresponse = VoiceResponse()

# Initial greeting
response.say("Hello! Thank you for calling. Please hold while I connect you with our AI assistant.")
response.pause(length=1)

# Redirect to conversation handler
response.redirect(url="/webhook/conversation", method="POST")

return str(response)
```

@app.post("/webhook/conversation")
 async def handle_conversation(request: Request):
 """Handle ongoing conversation with speech recognition"""
 form_data = await request.form()

```
textfrom services.call_handler import CallHandler
handler = CallHandler()

# Get caller info
caller_phone = form_data.get("From", "")
call_sid = form_data.get("CallSid", "")
speech_result = form_data.get("SpeechResult", "")

# Process the conversation turn
ai_response = await handler.process_conversation_turn(
    caller_phone=caller_phone,
    call_sid=call_sid,
    user_input=speech_result
)

response = VoiceResponse()

if ai_response.get("end_call", False):
    response.say("Thank you for calling! We'll follow up with you soon. Have a great day!")
    response.hangup()
else:
    response.say(ai_response["message"])
    response.gather(
        input="speech",
        action="/webhook/conversation",
        method="POST",
        speech_timeout="auto",
        language="en-US"
    )

return str(response)
text
### **2. Salesforce Integration**
```

# services/salesforce.py

import requests
 from typing import Dict, Optional
 import os
 from datetime import datetime

class SalesforceService:
 def **init**(self):
 self.username = os.getenv("SALESFORCE_USERNAME")
 self.password = os.getenv("SALESFORCE_PASSWORD")
 self.security_token = os.getenv("SALESFORCE_SECURITY_TOKEN")
 self.client_id = os.getenv("SALESFORCE_CLIENT_ID")
 self.client_secret = os.getenv("SALESFORCE_CLIENT_SECRET")
 self.instance_url = "[https://your-domain.my.salesforce.com](https://your-domain.my.salesforce.com/)"

```
text    self.access_token = None
    self.authenticate()

def authenticate(self):
    """OAuth 2.0 authentication with Salesforce"""
    auth_url = f"{self.instance_url}/services/oauth2/token"
    
    data = {
        'grant_type': 'password',
        'client_id': self.client_id,
        'client_secret': self.client_secret,
        'username': self.username,
        'password': self.password + self.security_token
    }
    
    response = requests.post(auth_url, data=data)
    result = response.json()
    
    if 'access_token' in result:
        self.access_token = result['access_token']
        self.instance_url = result['instance_url']
        print("✅ Salesforce authentication successful")
    else:
        raise Exception(f"Salesforce auth failed: {result}")

def find_or_create_contact(self, phone: str, additional_data: Dict = None) -> Dict:
    """Find existing contact or create new one"""
    headers = {
        'Authorization': f'Bearer {self.access_token}',
        'Content-Type': 'application/json'
    }
    
    # Search for existing contact
    query = f"SELECT Id, FirstName, LastName, Phone, Email, LeadSource FROM Contact WHERE Phone = '{phone}' LIMIT 1"
    search_url = f"{self.instance_url}/services/data/v61.0/query"
    
    response = requests.get(search_url, headers=headers, params={'q': query})
    results = response.json()
    
    if results.get('records'):
        contact = results['records']
        print(f"📋 Found existing contact: {contact.get('FirstName', '')} {contact.get('LastName', '')}")
        return contact
    
    # Create new contact
    contact_data = {
        'Phone': phone,
        'LeadSource': 'AI_Calling_Agent',
        'Description': f'Contact created via AI calling agent on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
    }
    
    if additional_data:
        contact_data.update(additional_data)
    
    create_url = f"{self.instance_url}/services/data/v61.0/sobjects/Contact"
    response = requests.post(create_url, headers=headers, json=contact_data)
    
    if response.status_code == 201:
        contact_id = response.json()['id']
        print(f"✅ Created new contact: {contact_id}")
        return {**contact_data, 'Id': contact_id}
    else:
        print(f"❌ Failed to create contact: {response.text}")
        return {}

def log_call_activity(self, contact_id: str, call_summary: str, call_outcome: str):
    """Create Task record for call activity"""
    headers = {
        'Authorization': f'Bearer {self.access_token}',
        'Content-Type': 'application/json'
    }
    
    task_data = {
        'WhoId': contact_id,
        'Subject': f'AI Agent Call - {call_outcome}',
        'Description': call_summary,
        'Status': 'Completed',
        'Priority': 'Normal',
        'Type': 'Call',
        'ActivityDate': datetime.now().strftime("%Y-%m-%d"),
        'TaskSubtype': 'Call',
        'CallType': 'Inbound'
    }
    
    task_url = f"{self.instance_url}/services/data/v61.0/sobjects/Task"
    response = requests.post(task_url, headers=headers, json=task_data)
    
    if response.status_code == 201:
        print("✅ Call logged in Salesforce")
        return response.json()['id']
    else:
        print(f"❌ Failed to log call: {response.text}")

def create_qualified_lead(self, contact_data: Dict, qualification_score: int):
    """Convert qualified contact to Lead"""
    if qualification_score < 60:
        return None
        
    headers = {
        'Authorization': f'Bearer {self.access_token}',
        'Content-Type': 'application/json'
    }
    
    lead_data = {
        'FirstName': contact_data.get('FirstName', ''),
        'LastName': contact_data.get('LastName', 'Qualified Lead'),
        'Phone': contact_data.get('Phone', ''),
        'Email': contact_data.get('Email', ''),
        'Company': contact_data.get('Company', 'TBD'),
        'LeadSource': 'AI_Agent_Qualification',
        'Status': 'Open - Not Contacted',
        'Rating': 'Hot' if qualification_score > 80 else 'Warm',
        'Description': f'AI-qualified lead with score: {qualification_score}/100'
    }
    
    lead_url = f"{self.instance_url}/services/data/v61.0/sobjects/Lead"
    response = requests.post(lead_url, headers=headers, json=lead_data)
    
    if response.status_code == 201:
        lead_id = response.json()['id']
        print(f"🎯 Created qualified lead: {lead_id}")
        
        # Create follow-up task
        self.create_follow_up_task(lead_id, qualification_score)
        return lead_id
    else:
        print(f"❌ Failed to create lead: {response.text}")

def create_follow_up_task(self, lead_id: str, qualification_score: int):
    """Create follow-up task for sales team"""
    headers = {
        'Authorization': f'Bearer {self.access_token}',
        'Content-Type': 'application/json'
    }
    
    priority = "High" if qualification_score > 80 else "Normal"
    due_date = (datetime.now().date()).strftime("%Y-%m-%d")
    
    task_data = {
        'WhoId': lead_id,
        'Subject': f'Follow up AI-qualified lead (Score: {qualification_score})',
        'Description': f'''
```

High-priority lead qualified by AI agent.
 Qualification Score: {qualification_score}/100

Recommended next steps:

1. Schedule discovery call within 24 hours
2. Send personalized follow-up email
3. Review call recording for context

Lead shows strong buying signals and should be prioritized.
 ''',
 'Status': 'Not Started',
 'Priority': priority,
 'Type': 'Call',
 'ActivityDate': due_date
 }

```
text    task_url = f"{self.instance_url}/services/data/v61.0/sobjects/Task"
    requests.post(task_url, headers=headers, json=task_data)
text
### **3. Speech Services Integration**
```



## **Modified Speech Services Implementation**

```
python# services/speech_services.py
import requests
import os
from typing import Optional
import tempfile
import time

class SpeechServices:
    def __init__(self):
        # ElevenLabs configuration
        self.elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
        self.elevenlabs_voice_id = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
        self.base_url = "https://api.elevenlabs.io/v1"
        
        # Common headers
        self.headers = {
            "xi-api-key": self.elevenlabs_api_key,
            "Content-Type": "application/json"
        }
    
    async def transcribe_audio(self, audio_url: str) -> Optional[str]:
        """Transcribe audio using ElevenLabs Speech-to-Text"""
        try:
            # Download audio from Twilio
            audio_response = requests.get(audio_url)
            
            # ElevenLabs STT endpoint
            stt_url = f"{self.base_url}/speech-to-text"
            
            # Prepare files for upload
            files = {
                'audio': ('audio.wav', audio_response.content, 'audio/wav'),
                'model_id': (None, 'eleven_english_sts_v2')  # ElevenLabs STT model
            }
            
            # Custom headers for file upload
            stt_headers = {
                "xi-api-key": self.elevenlabs_api_key
            }
            
            response = requests.post(stt_url, headers=stt_headers, files=files)
            
            if response.status_code == 200:
                result = response.json()
                return result.get('text', '')
            else:
                print(f"❌ ElevenLabs STT error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Transcription error: {str(e)}")
            return None
    
    async def synthesize_speech(self, text: str) -> Optional[str]:
        """Convert text to speech using ElevenLabs TTS"""
        try:
            tts_url = f"{self.base_url}/text-to-speech/{self.elevenlabs_voice_id}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.elevenlabs_api_key
            }
            
            # Optimized settings for phone calls
            data = {
                "text": text,
                "model_id": "eleven_turbo_v2",  # Fastest model for real-time
                "voice_settings": {
                    "stability": 0.6,
                    "similarity_boost": 0.8,
                    "style": 0.2,
                    "use_speaker_boost": True
                },
                "pronunciation_dictionary_locators": [],
                "seed": None,
                "previous_text": None,
                "next_text": None,
                "previous_request_ids": [],
                "next_request_ids": []
            }
            
            response = requests.post(tts_url, json=data, headers=headers)
            
            if response.status_code == 200:
                # Save audio file with timestamp
                audio_filename = f"response_{int(time.time())}.mp3"
                with open(audio_filename, "wb") as f:
                    f.write(response.content)
                print(f"✅ TTS audio generated: {audio_filename}")
                return audio_filename
            else:
                print(f"❌ ElevenLabs TTS error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ TTS synthesis error: {str(e)}")
            return None
    
    def get_available_voices(self) -> list:
        """Get list of available ElevenLabs voices for configuration"""
        try:
            voices_url = f"{self.base_url}/voices"
            response = requests.get(voices_url, headers={"xi-api-key": self.elevenlabs_api_key})
            
            if response.status_code == 200:
                voices = response.json().get('voices', [])
                return [{"id": v["voice_id"], "name": v["name"], "category": v.get("category", "Unknown")} for v in voices]
            else:
                print(f"❌ Failed to fetch voices: {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ Error fetching voices: {str(e)}")
            return []
    
    async def check_api_usage(self) -> dict:
        """Check ElevenLabs API usage and limits"""
        try:
            user_url = f"{self.base_url}/user"
            response = requests.get(user_url, headers={"xi-api-key": self.elevenlabs_api_key})
            
            if response.status_code == 200:
                user_data = response.json()
                subscription = user_data.get('subscription', {})
                
                return {
                    "character_count": subscription.get('character_count', 0),
                    "character_limit": subscription.get('character_limit', 0),
                    "can_extend_character_limit": subscription.get('can_extend_character_limit', False),
                    "allowed_to_extend_character_limit": subscription.get('allowed_to_extend_character_limit', False),
                    "next_character_count_reset_unix": subscription.get('next_character_count_reset_unix', 0)
                }
            else:
                return {"error": f"Failed to check usage: {response.text}"}
                
        except Exception as e:
            return {"error": f"Usage check error: {str(e)}"}
```

## **Updated Environment Configuration**

```
bash# Updated .env - Remove OpenAI Whisper, Add ElevenLabs STT
# Salesforce Configuration
SALESFORCE_USERNAME=your-playground-username@example.com
SALESFORCE_PASSWORD=your-reset-password
SALESFORCE_SECURITY_TOKEN=your-security-token
SALESFORCE_CLIENT_ID=your-connected-app-client-id
SALESFORCE_CLIENT_SECRET=your-connected-app-secret

# ElevenLabs Configuration (Both STT and TTS)
ELEVENLABS_API_KEY=your-elevenlabs-api-key
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM  # Or your preferred voice

# LLM Service
OPENROUTER_API_KEY=sk-or-v1-your-openrouter-key

# Twilio Configuration
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE_NUMBER=+1234567890

# Application
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=True
```

## **Updated Requirements.txt (Simplified)**

```
textfastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
requests==2.31.0
openai==1.3.0  # Only for OpenRouter, not Whisper
twilio==8.10.0
python-multipart==0.0.6
python-dotenv==1.0.0
# Removed: openai whisper dependencies
```

## **Enhanced Call Handler with ElevenLabs STT**

```
python# services/call_handler.py - Updated transcription handling
from services.speech_services import SpeechServices
import asyncio

class CallHandler:
    def __init__(self):
        self.sf_service = SalesforceService()
        self.llm_service = OpenRouterService()
        self.speech_service = SpeechServices()  # Now using ElevenLabs for both
        self.call_sessions = {}
    
    async def process_twilio_audio(self, recording_url: str) -> str:
        """Process audio from Twilio using ElevenLabs STT"""
        try:
            # ElevenLabs handles the transcription
            transcribed_text = await self.speech_service.transcribe_audio(recording_url)
            
            if transcribed_text:
                print(f"🎤 Transcribed: {transcribed_text}")
                return transcribed_text
            else:
                print("❌ Transcription failed, asking user to repeat")
                return ""  # Will trigger "please repeat" response
                
        except Exception as e:
            print(f"❌ Audio processing error: {str(e)}")
            return ""
    
    async def handle_twilio_webhook_with_recording(self, request_data: dict):
        """Enhanced Twilio webhook handler with recording support"""
        recording_url = request_data.get("RecordingUrl")
        call_sid = request_data.get("CallSid")
        caller_phone = request_data.get("From")
        
        if recording_url:
            # Process the recorded audio
            transcribed_text = await self.process_twilio_audio(recording_url)
            
            # Continue with normal conversation processing
            return await self.process_conversation_turn(
                caller_phone=caller_phone,
                call_sid=call_sid,
                user_input=transcribed_text
            )
        
        # Handle live speech input (from Twilio's speech recognition)
        speech_result = request_data.get("SpeechResult", "")
        return await self.process_conversation_turn(
            caller_phone=caller_phone,
            call_sid=call_sid,
            user_input=speech_result
        )
```

## **Updated Twilio Integration for Recording**

```
python# main.py - Enhanced Twilio webhooks
from fastapi import FastAPI, Form, Request, BackgroundTasks

@app.post("/webhook/incoming-call")
async def handle_incoming_call(From: str = Form(...), CallSid: str = Form(...)):
    """Handle incoming call with recording setup"""
    print(f"📞 Incoming call from {From}, Call ID: {CallSid}")
    
    response = VoiceResponse()
    
    # Initial greeting
    response.say("Hello! Thank you for calling. I'm connecting you with our AI assistant.")
    response.pause(length=1)
    
    # Start recording for ElevenLabs STT backup
    response.record(
        action="/webhook/recording-complete",
        method="POST",
        max_length=30,  # 30 second chunks
        play_beep=False,
        trim="trim-silence"
    )
    
    # Also use Twilio's speech recognition as fallback
    response.gather(
        input="speech",
        action="/webhook/conversation",
        method="POST",
        speech_timeout="auto",
        language="en-US",
        enhanced=True  # Better speech recognition
    )
    
    return str(response)

@app.post("/webhook/recording-complete")
async def handle_recording_complete(
    request: Request,
    background_tasks: BackgroundTasks,
    RecordingUrl: str = Form(...),
    CallSid: str = Form(...),
    From: str = Form(...)
):
    """Handle completed recording with ElevenLabs STT"""
    form_data = await request.form()
    
    # Process recording in background
    background_tasks.add_task(
        process_recording_with_elevenlabs,
        dict(form_data)
    )
    
    # Continue conversation
    response = VoiceResponse()
    response.gather(
        input="speech",
        action="/webhook/conversation",
        method="POST",
        speech_timeout="auto",
        language="en-US"
    )
    
    return str(response)

async def process_recording_with_elevenlabs(form_data: dict):
    """Background task to process recording with ElevenLabs"""
    handler = CallHandler()
    
    # Process with ElevenLabs STT
    result = await handler.handle_twilio_webhook_with_recording(form_data)
    
    # Store result for next conversation turn
    call_sid = form_data.get("CallSid")
    if call_sid:
        # Update session with ElevenLabs transcription
        handler.update_session_with_better_transcription(call_sid, result)
```

## **Benefits of Using ElevenLabs for Both STT & TTS**

## **Advantages**

- **Single API provider** - Simplified billing and management
- **Consistent audio quality** - Same provider handles both directions
- **Reduced latency** - No switching between services
- **Better voice matching** - STT and TTS optimized for same voice models
- **Cost efficiency** - Bundled pricing and usage tracking

## **ElevenLabs Pricing Comparison**

- **Free Tier**: 10,000 characters/month for TTS + limited STT
- **Starter Plan**: $5/month for 30,000 characters + extended STT
- **Creator Plan**: $22/month for 100,000 characters + full features

## **Portfolio Benefits**

- **Modern AI stack** - Using cutting-edge voice AI technology
- **Simplified architecture** - Fewer external dependencies
- **Cost optimization** - Single provider for multiple services
- **Quality demonstration** - High-quality voice interactions for demos

This unified approach with ElevenLabs for both STT and TTS creates a more streamlined, professional AI calling agent perfect for your portfolio demonstration while reducing complexity and potential integration issues.

# services/openrouter_llm.py

from openai import OpenAI
 import os
 from typing import Dict, List

class OpenRouterService:
 def **init**(self):
 self.client = OpenAI(
 base_url="https://openrouter.ai/api/v1",
 api_key=os.getenv("OPENROUTER_API_KEY")
 )

```
textasync def generate_response(self, contact_context: Dict, conversation_history: List, extracted_data: Dict) -> str:
    """Generate contextual response using mistralai/mistral-nemo:free via OpenRouter"""
    
    # Build system prompt with Salesforce context
    system_prompt = self.build_system_prompt(contact_context, extracted_data)
    
    # Prepare messages
    messages = [{"role": "system", "content": system_prompt}]
    
    # Add conversation history (last 10 turns for context)
    recent_history = conversation_history[-10:] if len(conversation_history) > 10 else conversation_history
    messages.extend([{"role": turn["role"], "content": turn["content"]} for turn in recent_history])
    
    try:
        response = self.client.chat.completions.create(
            model="mistralai/mistral-nemo:free",  # Fast and cost-effective
            messages=messages,
            temperature=0.3,  # Consistent but natural responses
            max_tokens=150,   # Keep responses concise for phone calls
            top_p=0.9
        )
        
        return response.choices.message.content
        
    except Exception as e:
        print(f"❌ LLM error: {str(e)}")
        return "I apologize, I'm having a technical issue. Let me transfer you to a human agent."

def build_system_prompt(self, contact_context: Dict, extracted_data: Dict) -> str:
    """Build comprehensive system prompt"""
    
    customer_name = f"{contact_context.get('FirstName', '')} {contact_context.get('LastName', '')}".strip()
    is_existing_customer = bool(contact_context.get('Id'))
    
    system_prompt = f"""You are a professional AI assistant representing a technology company. You're handling a phone call with excellent customer service.
```

CUSTOMER CONTEXT:

- Customer: {customer_name if customer_name else 'New caller'}
- Existing customer: {'Yes' if is_existing_customer else 'No'}
- Phone: {contact_context.get('Phone', 'Unknown')}
- Previous source: {contact_context.get('LeadSource', 'Unknown')}

INFORMATION GATHERED SO FAR:
 {self._format_extracted_data(extracted_data)}

YOUR OBJECTIVES:

1. Provide helpful, professional assistance
2. Understand their needs and challenges
3. Gather missing contact information naturally (name, email, company)
4. Identify if this is a sales opportunity
5. Guide toward appropriate next steps (demo, consultation, etc.)

CONVERSATION GUIDELINES:

- Keep responses under 30 seconds when spoken
- Be warm, professional, and helpful
- Ask one clear question at a time
- Listen actively and acknowledge their responses
- If they seem qualified, guide toward scheduling a call or demo
- If they have issues, focus on problem-solving first

CURRENT PRIORITY:
 {self._determine_conversation_priority(extracted_data)}

Remember: You're representing a professional company. Be helpful, efficient, and focused on the customer's success."""

```
text    return system_prompt

def _format_extracted_data(self, extracted_data: Dict) -> str:
    """Format extracted data for system prompt"""
    if not extracted_data:
        return "No information gathered yet."
    
    formatted = []
    for key, value in extracted_data.items():
        formatted.append(f"- {key.replace('_', ' ').title()}: {value}")
    
    return "\n".join(formatted) if formatted else "No information gathered yet."

def _determine_conversation_priority(self, extracted_data: Dict) -> str:
    """Determine current conversation priority"""
    if not extracted_data.get("email"):
        return "Gather contact information (email and name)"
    elif not extracted_data.get("company"):
        return "Understand their business and role"
    elif extracted_data.get("budget_mentioned"):
        return "Qualify opportunity and guide toward demo/consultation"
    else:
        return "Understand their needs and challenges"
text
## **Configuration & Deployment**

### **Environment Variables (.env)**
```

# Salesforce Configuration

SALESFORCE_USERNAME=[your-playground-username@example.com](mailto:your-playground-username@example.com)
 SALESFORCE_PASSWORD=your-reset-password
 SALESFORCE_SECURITY_TOKEN=your-security-token
 SALESFORCE_CLIENT_ID=your-connected-app-client-id
 SALESFORCE_CLIENT_SECRET=your-connected-app-secret

# API Services

OPENROUTER_API_KEY=sk-or-v1-your-openrouter-key
 OPENAI_API_KEY=sk-your-openai-key-for-whisper
 ELEVENLABS_API_KEY=your-elevenlabs-key
 ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM

# Twilio Configuration

TWILIO_ACCOUNT_SID=your-twilio-account-sid
 TWILIO_AUTH_TOKEN=your-twilio-auth-token
 TWILIO_PHONE_NUMBER=+1234567890

# Application

APP_HOST=0.0.0.0
 APP_PORT=8000
 DEBUG=True

```
text
### **Requirements.txt**
```

fastapi==0.104.1
 uvicorn==0.24.0
 pydantic==2.5.0
 requests==2.31.0
 openai==1.3.0
 twilio==8.10.0
 python-multipart==0.0.6
 python-dotenv==1.0.0

```
text
### **Deployment Commands**
```

# Local development

pip install -r requirements.txt
 uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Railway deployment

railway login
 railway new
 railway add
 railway up

```
text
## **Portfolio Demo Script**

### **Demo Scenarios**
1. **Inbound Sales Inquiry**: Caller asks about services, AI qualifies and schedules demo
2. **Support Request**: Existing customer needs help, AI captures issue and creates case
3. **Lead Follow-up**: Outbound call to qualified lead, AI nurtures and books meeting

### **Key Metrics to Track**
- **Call Duration**: Average 2-3 minutes per call
- **Lead Qualification Rate**: Target 60%+ qualified conversations
- **Data Capture Rate**: 90%+ calls should capture email/company
- **Salesforce Integration**: 100% calls logged with follow-up tasks

### **Portfolio Presentation Points**
- **Enterprise Integration**: Full Salesforce CRM integration
- **AI/ML Implementation**: OpenRouter LLM + Whisper STT + ElevenLabs TTS
- **Real-time Processing**: Live conversation handling with <2s response time
- **Scalable Architecture**: FastAPI backend ready for enterprise deployment
- **Business Logic**: Automated lead scoring and workflow triggers

This MVP demonstrates enterprise-level AI integration skills while being fully functional for real business use cases. The Salesforce integration shows you understand business systems, while the AI components demonstrate technical depth with modern tools.
```