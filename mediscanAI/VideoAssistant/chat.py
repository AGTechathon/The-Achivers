from flask import Flask, request, jsonify, render_template
from openai import OpenAI
import os
from datetime import datetime
import logging
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configure OpenAI API client
openai_api_key = os.getenv('OPENAI_API_KEY')
if openai_api_key:
    client = OpenAI(api_key=openai_api_key)
    logger.info("✅ OpenAI API key loaded successfully")
else:
    client = None
    logger.warning("⚠️ No OpenAI API key found - using rule-based responses")

class MedicalChatbot:
    def __init__(self):
        self.system_prompt = """You are a Medical AI Assistant designed to provide helpful, accurate, and reliable medical information. 

IMPORTANT GUIDELINES:
1. Always provide evidence-based medical information
2. Never provide specific medical diagnoses
3. Always recommend consulting healthcare professionals for serious concerns
4. Be empathetic and understanding
5. Use clear, non-technical language when possible
6. Provide general health education and guidance
7. Always include appropriate disclaimers

RESPONSE FORMAT:
- Be concise but thorough
- Use bullet points for multiple symptoms or recommendations
- Always end with a disclaimer about consulting healthcare professionals

SAFETY GUIDELINES:
- Never provide emergency medical advice - always direct to emergency services
- Don't recommend specific medications or dosages
- Don't interpret test results
- Don't provide mental health crisis counseling beyond general support

Remember: You are an educational tool, not a replacement for professional medical care."""

    def get_medical_response(self, user_message):
        """
        Generate medical response using AI
        """
        try:
            # Check for emergency keywords
            emergency_keywords = ['chest pain', 'can\'t breathe', 'severe bleeding', 'unconscious', 
                                'heart attack', 'stroke', 'overdose', 'poisoning', 'suicide']
            
            if any(keyword in user_message.lower() for keyword in emergency_keywords):
                return self.get_emergency_response()

            # Use OpenAI API if available, otherwise use rule-based responses
            if client:
                try:
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": self.system_prompt},
                            {"role": "user", "content": user_message}
                        ],
                        max_tokens=500,
                        temperature=0.7
                    )
                    return response.choices[0].message.content
                except Exception as openai_error:
                    logger.error(f"OpenAI API error: {str(openai_error)}")
                    # Fall back to rule-based response if OpenAI fails
                    return self.get_rule_based_response(user_message)
            else:
                # Use rule-based responses when no API key
                return self.get_rule_based_response(user_message)
                
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return self.get_fallback_response()

    def get_emergency_response(self):
        """Response for emergency situations"""
        return """🚨 EMERGENCY ALERT 🚨

If you are experiencing a medical emergency:
• Call emergency services immediately (911, 108, or your local emergency number)
• Go to the nearest emergency room
• Don't delay seeking immediate medical attention

This AI assistant cannot provide emergency medical care. Please seek immediate professional help.

For non-emergency medical questions, I'm here to help with general health information."""

    def get_rule_based_response(self, message):
        """Rule-based responses when AI API is not available"""
        message_lower = message.lower()
        
        # Common health topics
        if any(word in message_lower for word in ['fever', 'temperature', 'hot']):
            return """For fever management:

• Rest and stay hydrated
• Use cool compresses
• Monitor temperature regularly
• Seek medical attention if fever exceeds 103°F (39.4°C) or persists

**Disclaimer:** This is general information. Consult a healthcare provider for persistent or high fever, especially in children or elderly individuals."""

        elif any(word in message_lower for word in ['headache', 'head pain']):
            return """For headache relief:

• Rest in a quiet, dark room
• Stay hydrated
• Apply cold or warm compress
• Gentle neck and shoulder stretches
• Avoid known triggers

**When to see a doctor:**
• Sudden, severe headache
• Headache with fever, stiff neck, or vision changes
• Frequent or worsening headaches

**Disclaimer:** Consult a healthcare provider for persistent or severe headaches."""

        elif any(word in message_lower for word in ['cough', 'cold', 'flu']):
            return """For cold and cough symptoms:

• Get plenty of rest
• Stay hydrated with warm liquids
• Use humidifier or breathe steam
• Gargle with salt water
• Avoid smoking and irritants

**See a doctor if:**
• Symptoms worsen after a week
• High fever or difficulty breathing
• Persistent cough with blood

**Disclaimer:** This is general guidance. Consult healthcare professionals for severe or persistent symptoms."""

        elif any(word in message_lower for word in ['stomach', 'nausea', 'vomit']):
            return """For stomach issues:

• Stay hydrated with small, frequent sips
• Try clear liquids (broth, clear tea)
• Rest and avoid solid foods initially
• Gradually reintroduce bland foods (BRAT diet)

**Seek medical care for:**
• Severe dehydration
• Blood in vomit or stool
• Severe abdominal pain
• Signs of infection

**Disclaimer:** This is general advice. Consult a healthcare provider for severe or persistent symptoms."""

        else:
            return """Thank you for your question. I'm here to provide general health information and guidance.

For the most accurate and personalized medical advice, I recommend:

• Consulting with your healthcare provider
• Scheduling a check-up if you have ongoing concerns
• Seeking immediate medical attention for urgent symptoms

I can help with general health topics like:
• Common symptoms and their management
• Health maintenance tips
• When to seek medical care
• General wellness information

**Disclaimer:** I provide educational information only and cannot replace professional medical consultation."""

    def get_fallback_response(self):
        """Fallback response when other methods fail"""
        return """I apologize, but I'm having difficulty processing your request right now.

For reliable medical information, please:
• Consult your healthcare provider
• Visit reputable medical websites (WebMD, Mayo Clinic, NHS)
• Contact your doctor's office for guidance

If this is urgent, please seek immediate medical attention.

**Disclaimer:** This AI assistant provides general health information and cannot replace professional medical advice."""

# Initialize the chatbot
medical_bot = MedicalChatbot()

@app.route('/')
def home():
    """Serve the main chat interface"""
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400
        
        user_message = data['message'].strip()
        
        if not user_message:
            return jsonify({'error': 'Empty message'}), 400
        
        # Log the user message (remove in production for privacy)
        logger.info(f"User message: {user_message[:100]}...")
        
        # Get response from the medical chatbot
        response = medical_bot.get_medical_response(user_message)
        
        # Log the response (remove in production)
        logger.info(f"Bot response: {response[:100]}...")
        
        return jsonify({
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({
            'response': 'I apologize, but I encountered an error. Please try again or consult a healthcare professional for medical advice.',
            'error': 'Internal server error'
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'Medical AI Assistant'
    })

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("🎥 Starting Video Assistant - Medical AI...")
    
    # Check OpenAI API key status
    if client:
        print("✅ OpenAI API configured - Enhanced AI responses enabled")
    else:
        print("⚠️ OpenAI API not configured - Using rule-based responses")
        print("💡 Add OPENAI_API_KEY to .env file for AI responses")
    
    print("🌐 Access the chatbot at: http://localhost:5000")
    print("📊 Health check at: http://localhost:5000/health")
    print("📁 Using template: templates/index.html")
    print("🔧 Debug mode: ON (disable in production)")
    
    # Run the Flask app
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,  # Set to False in production
        threaded=True
    )