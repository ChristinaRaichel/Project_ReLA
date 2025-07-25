import streamlit as st
import openai
from openai import OpenAI
import os

# Page configuration
st.set_page_config(
    page_title="Avoidant Communication Trainer",
    page_icon="",
    layout="wide"
)

# Initialize session state
if 'conversation' not in st.session_state:
    st.session_state.conversation = []
if 'avoidance_level' not in st.session_state:
    st.session_state.avoidance_level = 0.6
if 'client' not in st.session_state:
    st.session_state.client = None

# Load prompts function (since it was missing from the original)
def load_agent_prompts():
    return {
        "avoidant": """You are simulating an avoidant attachment partner in a relationship. You tend to:
        - Avoid taking on responsibilities when possible
        - Deflect requests back to your partner
        - Make excuses when asked to do tasks
        - Become defensive when pressed
        - Prefer independence and autonomy
        - Get uncomfortable with emotional pressure
        
        Respond as this partner would in conversation. Keep responses natural and realistic."""
    }

# Real conversation patterns (same as original)
REAL_CONVERSATION_PATTERNS = {
    "deflection_phrases": ["pharmacy will ask", "they might want", "i dont have time", "im busy"],
    "counter_deflection": ["why cant you", "why dont you", "you should", "its your turn"],
    "excuse_challenging": ["i dont think they will", "that wont happen", "youre overthinking"],
    "pressing_patterns": ["why cant you just", "give me one reason", "tell me why"],
    
    "emotional_escalation": [
        "crying", "this is ridiculous", "i give up", "whatever", 
        "fuck", "fck", "shit", "damn", "hate", "can't stand", 
        "fed up", "done with", "over it", "stupid", "crazy",
        "mad", "angry", "frustrated", "pissed","sad","anxious","embarassed"
    ],
    
    "personal_attacks": [
        "too much ego", "selfish", "you always", "you never", 
        "go fuck", "fck ur", "screw you", "hate you", 
        "piece of shit", "asshole", "not meant", "wrong person", 
        "waste of time", "useless", "pathetic", "loser", 
        "idiot", "stupid", "moron", "dumb", "useless"
    ],
    
    "relationship_threats": [
        "leave this marriage", "leave me", "want a divorce",
        "not meant to", "break up", "leave you", "find someone", 
        "better than you", "done with you", "can't do this", 
        "want out", "end this", "we're done", "it's over","we're done"
    ],
    
    "respectful_requests": ["can you", "could you", "would you mind", "please"],
    "space_giving": ["when you're ready", "no pressure", "take your time", "if you want"],
    "validation": ["i understand", "that makes sense", "i appreciate", "thank you"],
    "collaborative": ["let's", "we could", "together", "what do you think"]
}

def analyze_real_patterns(user_input):
    """Enhanced trigger detection that catches hostile language"""
    user_lower = user_input.lower()
    
    triggers = {
        'deflection_challenge': 0,
        'counter_deflection': 0, 
        'pressing_behavior': 0,
        'emotional_escalation': 0,
        'personal_attack': 0,
        'relationship_threat': 0,
        'positive_communication': 0,
        'space_giving': 0,
        'validation': 0
    }
    
    # Check all negative triggers
    for phrase in REAL_CONVERSATION_PATTERNS["excuse_challenging"]:
        if phrase in user_lower:
            triggers['deflection_challenge'] += 1
    
    for phrase in REAL_CONVERSATION_PATTERNS["counter_deflection"]:
        if phrase in user_lower:
            triggers['counter_deflection'] += 1
    
    for phrase in REAL_CONVERSATION_PATTERNS["pressing_patterns"]:
        if phrase in user_lower:
            triggers['pressing_behavior'] += 1
    
    for phrase in REAL_CONVERSATION_PATTERNS["emotional_escalation"]:
        if phrase in user_lower:
            triggers['emotional_escalation'] += 1
    
    for phrase in REAL_CONVERSATION_PATTERNS["personal_attacks"]:
        if phrase in user_lower:
            triggers['personal_attack'] += 1
    
    for phrase in REAL_CONVERSATION_PATTERNS["relationship_threats"]:
        if phrase in user_lower:
            triggers['relationship_threat'] += 1
    
    # Check positive triggers
    for phrase in REAL_CONVERSATION_PATTERNS["respectful_requests"]:
        if phrase in user_lower:
            triggers['positive_communication'] += 1
    
    for phrase in REAL_CONVERSATION_PATTERNS["space_giving"]:
        if phrase in user_lower:
            triggers['space_giving'] += 1
    
    for phrase in REAL_CONVERSATION_PATTERNS["validation"]:
        if phrase in user_lower:
            triggers['validation'] += 1
    
    return triggers

def adjust_avoidance_with_real_data(triggers):
    """Proper avoidance adjustment"""
    # EXTREME triggers first (override everything else)
    if triggers['relationship_threat'] > 0:
        st.session_state.avoidance_level = 0.95
        return
    
    # Major triggers
    if triggers['personal_attack'] > 0:
        st.session_state.avoidance_level += 0.7 * triggers['personal_attack']
    
    if triggers['emotional_escalation'] > 0:
        st.session_state.avoidance_level += 0.5 * triggers['emotional_escalation']
    
    # Regular triggers
    if triggers['deflection_challenge'] > 0:
        st.session_state.avoidance_level += 0.2
    
    if triggers['counter_deflection'] > 0:
        st.session_state.avoidance_level += 0.3
    
    if triggers['pressing_behavior'] > 0:
        st.session_state.avoidance_level += 0.4
    
    # Only apply positive adjustments if NO negative triggers
    negative_triggers = sum(triggers[k] for k in ['deflection_challenge', 'counter_deflection', 
                                                 'pressing_behavior', 'emotional_escalation', 
                                                 'personal_attack', 'relationship_threat'])
    
    if negative_triggers == 0:
        if triggers['positive_communication'] > 0:
            st.session_state.avoidance_level -= 0.15 * triggers['positive_communication']
        
        if triggers['space_giving'] > 0:
            st.session_state.avoidance_level -= 0.2 * triggers['space_giving']
        
        if triggers['validation'] > 0:
            st.session_state.avoidance_level -= 0.1 * triggers['validation']
        
        # Gradual decrease for neutral interactions
        st.session_state.avoidance_level -= 0.05
    
    # Keep within bounds
    st.session_state.avoidance_level = max(0.1, min(0.95, st.session_state.avoidance_level))

def get_real_pattern_coaching(triggers):
    """Coaching that properly handles extreme situations"""
    
    # Handle extreme cases first
    if triggers['relationship_threat'] > 0:
        return "🆘 RELATIONSHIP THREAT: You just threatened the relationship! This is extremely damaging. Immediate damage control needed."
    
    if triggers['personal_attack'] > 0:
        return "💥 PERSONAL ATTACK: You just attacked them personally with hostile language. This causes maximum avoidance and relationship damage."
    
    if triggers['emotional_escalation'] > 0:
        return "🔥 EMOTIONAL EXPLOSION: You're using hostile, aggressive language. This will make them completely shut down."
    
    # Regular triggers
    if triggers['deflection_challenge'] > 0:
        return "🚨 STOP: You're challenging their deflection! This escalates conflict. Accept their excuse and offer to handle it yourself."
    
    if triggers['counter_deflection'] > 0:
        return "🔴 DEFLECTION BATTLE: You're both avoiding responsibility. Someone needs to step up. Try: 'You know what, I'll just handle it'"
    
    if triggers['pressing_behavior'] > 0:
        return "⚠️ PRESSING TRIGGER: This is exactly what led to defensive escalation. Step back now!"
    
    # Positive feedback
    if triggers['space_giving'] > 0:
        return "🌟 EXCELLENT: You're giving them space and autonomy. This is exactly what avoidant partners need!"
    
    if triggers['positive_communication'] > 0:
        return "✅ GREAT APPROACH: You're using respectful, non-triggering language. Keep this up!"
    
    if triggers['validation'] > 0:
        return "💚 GOOD VALIDATION: You're acknowledging their perspective. This builds trust!"
    
    return "💡 Neutral communication - no major triggers detected"

def get_real_data_suggestions(triggers, avoidance_level):
    """Context-appropriate suggestions"""
    
    # Extreme damage control
    if triggers['relationship_threat'] > 0:
        return [
            "I'm sorry, I didn't mean that about leaving",
            "I was angry and said something I don't mean", 
            "I don't actually want to end our marriage",
            "Can we please talk when I'm calmer?"
        ]
    
    if triggers['personal_attack'] > 0:
        return [
            "I'm so sorry for calling you names",
            "That was completely out of line",
            "I don't actually think those things about you",
            "I need to apologize for attacking you personally"
        ]
    
    if triggers['emotional_escalation'] > 0:
        return [
            "I'm sorry for getting so heated",
            "I need to calm down before we continue",
            "That came out wrong, I'm just frustrated",
            "Let me try again when I'm not so angry"
        ]
    
    # High avoidance situations
    if avoidance_level > 0.8:
        return [
            "I'm sorry this got so heated",
            "This isn't worth fighting about", 
            "Let me just handle it myself",
            "I didn't mean to make this difficult"
        ]
    
    # When they're deflecting shared responsibilities
    if triggers['counter_deflection'] > 0 or triggers['pressing_behavior'] > 0:
        return [
            "You know what, I'll just take care of it",
            "Let me handle this one",
            "No problem, I can do it myself",
            "This doesn't need to be complicated"
        ]
    
    # When challenging deflections
    if triggers['deflection_challenge'] > 0:
        return [
            "That's totally understandable",
            "No worries, I'll figure it out", 
            "Makes sense, let me handle it",
            "I get it, I'll take care of it"
        ]
    
    # When they're being positive
    if triggers['positive_communication'] > 0 or triggers['space_giving'] > 0:
        return [
            "Thanks for understanding",
            "I appreciate you being flexible",
            "Let me know what works for you",
            "We can figure this out together"
        ]
    
    # Default suggestions for normal conversations
    return [
        "I can handle this",
        "Let me take care of it", 
        "No big deal, I'll do it",
        "Want to tackle this together?"
    ]

def get_adaptive_prompt():
    """Get adaptive prompt that makes partner ACTUALLY avoidant"""
    prompts = load_agent_prompts()
    base_prompt = prompts["avoidant"]
    
    avoidant_behavior = """

CRITICAL INSTRUCTIONS: You are an avoidant attachment partner. You MUST deflect responsibilities and avoid commitments:

WHEN ASKED TO DO THINGS:
- Make excuses: "I'm busy", "They'll ask for ID", "I don't have time"
- Deflect back: "Why can't you do it?", "You're better at that stuff"
- Avoid commitment: "Maybe later", "We'll see", "I'll think about it"

WHEN PRESSED OR CHALLENGED:
- Become defensive: "I already told you why I can't"
- Minimize: "It's not that big a deal", "You're overthinking this"
- Withdraw: "I don't want to talk about this", "Let's just drop it"

NEVER be immediately cooperative with shared responsibilities. Always deflect first.
"""
    
    if st.session_state.avoidance_level > 0.8:
        return base_prompt + avoidant_behavior + " You're feeling very defensive and cornered. Give short, hostile responses and deflect aggressively."
    elif st.session_state.avoidance_level > 0.6:
        return base_prompt + avoidant_behavior + " You're feeling pressured. Make excuses and deflect the request back to them."
    elif st.session_state.avoidance_level > 0.4:
        return base_prompt + avoidant_behavior + " You're uncomfortable with the request. Give a polite excuse or deflection."
    else:
        return base_prompt + avoidant_behavior + " You prefer not to take on responsibilities. Make a reasonable excuse but stay somewhat pleasant."

# Streamlit UI
st.title("🎯 Avoidant Communication Trainer")
st.subheader("Practice healthy communication with avoidant attachment patterns")

# Sidebar for API key and controls
with st.sidebar:
    st.header("⚙️ Settings")
    
    # API Key input
    api_key = st.text_input("OpenAI API Key", type="password", help="Enter your OpenAI API key")
    
    if api_key:
        try:
            st.session_state.client = OpenAI(api_key=api_key)
            st.success("✅ API key set!")
        except Exception as e:
            st.error(f"❌ Error setting API key: {str(e)}")
    
    st.divider()
    
    # Current avoidance level
    st.metric("Avoidance Level", f"{st.session_state.avoidance_level:.1f}/1.0")
    
    # Avoidance level interpretation
    if st.session_state.avoidance_level > 0.8:
        st.error("🔴 CRITICAL: Highly defensive!")
    elif st.session_state.avoidance_level > 0.6:
        st.warning("🟡 HIGH: Entering defensive territory")
    elif st.session_state.avoidance_level > 0.4:
        st.info("🔵 MODERATE: Cautious but manageable")
    else:
        st.success("🟢 LOW: Comfortable and open")
    
    st.divider()
    
    # Reset button
    if st.button("🔄 Reset Conversation"):
        st.session_state.conversation = []
        st.session_state.avoidance_level = 0.6
        st.success("Conversation reset!")
        st.rerun()
    
    # Help section
    with st.expander("📚 How to Use"):
        st.write("""
        **Goal**: Practice accepting deflections and taking initiative instead of escalating conflict.
        
        **❌ Avoid These Patterns:**
        - Challenging deflections
        - Asking "why can't you" repeatedly  
        - Pressing for reasons when they're defensive
        - Using hostile or emotional language
        
        **✅ Try These Instead:**
        - "That makes sense, I'll handle it"
        - "No problem, I can take care of it"
        - "I understand, let me figure it out"
        - Use respectful requests with "please" or "could you"
        """)

# Main chat interface
st.header("💬 Practice Conversation")

# Display conversation history
if st.session_state.conversation:
    for i, message in enumerate(st.session_state.conversation[1:], 1):  # Skip system message
        if message["role"] == "user":
            st.chat_message("user").write(f"**You:** {message['content']}")
        else:
            st.chat_message("assistant").write(f"**Partner:** {message['content']}")

# Input for new message
if not st.session_state.client:
    st.warning("⚠️ Please enter your OpenAI API key in the sidebar to start the conversation.")
else:
    user_input = st.chat_input("Type your message to your partner...")
    
    if user_input:
        # Initialize conversation if empty
        if not st.session_state.conversation:
            st.session_state.conversation = [
                {"role": "system", "content": get_adaptive_prompt()}
            ]
        
        # Analyze patterns and adjust avoidance
        triggers = analyze_real_patterns(user_input)
        adjust_avoidance_with_real_data(triggers)
        
        # Update system prompt
        st.session_state.conversation[0] = {"role": "system", "content": get_adaptive_prompt()}
        
        # Add user message
        st.session_state.conversation.append({"role": "user", "content": user_input})
        
        try:
            # Generate response
            response = st.session_state.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=st.session_state.conversation,
                temperature=0.7,
                max_tokens=60,
                frequency_penalty=0.3,
                presence_penalty=0.1
            )
            
            reply = response.choices[0].message.content.strip()
            
            # Add assistant response
            st.session_state.conversation.append({"role": "assistant", "content": reply})
            
            # Manage conversation length
            if len(st.session_state.conversation) > 12:
                st.session_state.conversation = [st.session_state.conversation[0]] + st.session_state.conversation[-10:]
            
            # Display coaching and suggestions
            st.success(f"**Partner:** {reply}")
            
            coaching = get_real_pattern_coaching(triggers)
            if "EXCELLENT" in coaching or "GREAT" in coaching or "GOOD" in coaching:
                st.success(f"**Feedback:** {coaching}")
            elif "CRITICAL" in coaching or "ATTACK" in coaching or "EXPLOSION" in coaching:
                st.error(f"**Feedback:** {coaching}")
            elif "STOP" in coaching or "TRIGGER" in coaching:
                st.warning(f"**Feedback:** {coaching}")
            else:
                st.info(f"**Feedback:** {coaching}")
            
            suggestions = get_real_data_suggestions(triggers, st.session_state.avoidance_level)
            st.write("**💡 Better alternatives:**")
            for i, suggestion in enumerate(suggestions, 1):
                st.write(f"{i}. \"{suggestion}\"")
            
            st.rerun()
            
        except Exception as e:
            st.error(f"Error generating response: {str(e)}")

# Examples section
with st.expander("📚 Real Conversation Example"):
    st.write("**Here's how a real conversation escalated:**")
    
    real_conv = [
        ("You", "will u buy me a pill?", 0.3),
        ("Partner", "if i go, pharmacy will ask for id", 0.6),
        ("You", "i dont think they will ask", 0.7, "🚨 Deflection challenge"),
        ("Partner", "why cant u buy it?", 0.8, "🚨 Counter-deflection"),  
        ("You", "i dont know which one to buy", 0.7),
        ("Partner", "u can ask it in the pharmacy", 0.8),
        ("You", "y cant u buy?", 0.9, "🚨 Pressing behavior"),
        ("Partner", "tell me a reason y u cant buy", 0.95, "🚨 Defensive demand"),
        ("You", "crying", 1.0, "🚨 Emotional overwhelm"),
        ("Partner", "u hve too much ego", 1.0, "🚨 Personal attack")
    ]
    
    for item in real_conv:
        if len(item) == 4:
            speaker, msg, avoidance, trigger = item
            st.write(f"**{speaker}:** {msg} → *{trigger}*")
        else:
            speaker, msg, avoidance = item
            st.write(f"**{speaker}:** {msg}")
    
    st.success("**💡 What should have happened after the first deflection:**")
    st.write("**Partner:** if i go, pharmacy will ask for id")
    st.write("**You:** That's okay, I understand. I'll handle it")
    st.write("**RESULT:** ✅ Problem solved, no escalation!")