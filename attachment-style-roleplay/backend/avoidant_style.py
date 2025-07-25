import os
from dotenv import load_dotenv
from openai import OpenAI
from load_prompts import load_agent_prompts

load_dotenv()
client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

prompts = load_agent_prompts()
partner_style = "avoidant"
avoidance_level = 0.6  # Start higher for realistic avoidant behavior
conversation = []

# FIXED: Much more comprehensive trigger patterns
REAL_CONVERSATION_PATTERNS = {
    # Negative patterns (INCREASE avoidance)
    "deflection_phrases": ["pharmacy will ask", "they might want", "i dont have time", "im busy"],
    "counter_deflection": ["why cant you", "why dont you", "you should", "its your turn"],
    "excuse_challenging": ["i dont think they will", "that wont happen", "youre overthinking"],
    "pressing_patterns": ["why cant you just", "give me one reason", "tell me why"],
    
    # FIXED: Comprehensive emotional escalation detection
    "emotional_escalation": [
        "crying", "this is ridiculous", "i give up", "whatever", 
        "fuck", "fck", "shit", "damn", "hate", "can't stand", 
        "fed up", "done with", "over it", "stupid", "crazy",
        "mad", "angry", "frustrated", "pissed"
    ],
    
    # FIXED: Comprehensive personal attack detection  
    "personal_attacks": [
        "too much ego", "selfish", "you always", "you never", 
        "go fuck", "fck ur", "screw you", "hate you", 
        "piece of shit", "asshole", "not meant", "wrong person", 
        "waste of time", "useless", "pathetic", "loser", 
        "idiot", "stupid", "moron", "dumb"
    ],
    
    # NEW: Relationship threat detection (maximum trigger)
    "relationship_threats": [
        "leave this marriage", "need to leave", "want a divorce",
        "not meant to", "break up", "leave you", "find someone", 
        "better than you", "done with you", "can't do this", 
        "want out", "end this", "we're done", "it's over"
    ],
    
    # Positive patterns (DECREASE avoidance)
    "respectful_requests": ["can you", "could you", "would you mind", "please"],
    "space_giving": ["when you're ready", "no pressure", "take your time", "if you want"],
    "validation": ["i understand", "that makes sense", "i appreciate", "thank you"],
    "collaborative": ["let's", "we could", "together", "what do you think"]
}

def analyze_real_patterns(user_input):
    """FIXED: Enhanced trigger detection that catches ALL hostile language"""
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
    
    # FIXED: Better emotional escalation detection
    for phrase in REAL_CONVERSATION_PATTERNS["emotional_escalation"]:
        if phrase in user_lower:
            triggers['emotional_escalation'] += 1
    
    # FIXED: Better personal attack detection
    for phrase in REAL_CONVERSATION_PATTERNS["personal_attacks"]:
        if phrase in user_lower:
            triggers['personal_attack'] += 1
    
    # NEW: Relationship threat detection
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
    """FIXED: Proper avoidance adjustment"""
    global avoidance_level
    
    # EXTREME triggers first (override everything else)
    if triggers['relationship_threat'] > 0:
        avoidance_level = 0.95  # Maximum for relationship threats
        return
    
    # Major triggers
    if triggers['personal_attack'] > 0:
        avoidance_level += 0.7 * triggers['personal_attack']
    
    if triggers['emotional_escalation'] > 0:
        avoidance_level += 0.5 * triggers['emotional_escalation']
    
    # Regular triggers
    if triggers['deflection_challenge'] > 0:
        avoidance_level += 0.2
    
    if triggers['counter_deflection'] > 0:
        avoidance_level += 0.3
    
    if triggers['pressing_behavior'] > 0:
        avoidance_level += 0.4
    
    # Only apply positive adjustments if NO negative triggers
    negative_triggers = sum(triggers[k] for k in ['deflection_challenge', 'counter_deflection', 
                                                 'pressing_behavior', 'emotional_escalation', 
                                                 'personal_attack', 'relationship_threat'])
    
    if negative_triggers == 0:
        if triggers['positive_communication'] > 0:
            avoidance_level -= 0.15 * triggers['positive_communication']
        
        if triggers['space_giving'] > 0:
            avoidance_level -= 0.2 * triggers['space_giving']
        
        if triggers['validation'] > 0:
            avoidance_level -= 0.1 * triggers['validation']
        
        # Gradual decrease for neutral interactions
        avoidance_level -= 0.05
    
    # Keep within bounds
    avoidance_level = max(0.1, min(0.95, avoidance_level))

def get_real_pattern_coaching(triggers):
    """FIXED: Coaching that properly handles extreme situations"""
    
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
    """FIXED: Context-appropriate suggestions"""
    
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

def get_base_prompt_text(prompt_template):
    """Extract prompt text from PromptTemplate object"""
    if hasattr(prompt_template, 'template'):
        return prompt_template.template
    elif hasattr(prompt_template, 'prompt'):
        return prompt_template.prompt
    else:
        return str(prompt_template)

def get_adaptive_prompt():
    """FIXED: Get adaptive prompt that makes partner ACTUALLY avoidant"""
    prompt_template = prompts[partner_style]
    base_prompt = get_base_prompt_text(prompt_template)
    
    # FIXED: Make partner actually avoidant for realistic training
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
    
    if avoidance_level > 0.8:
        return base_prompt + avoidant_behavior + " You're feeling very defensive and cornered. Give short, hostile responses and deflect aggressively."
    elif avoidance_level > 0.6:
        return base_prompt + avoidant_behavior + " You're feeling pressured. Make excuses and deflect the request back to them."
    elif avoidance_level > 0.4:
        return base_prompt + avoidant_behavior + " You're uncomfortable with the request. Give a polite excuse or deflection."
    else:
        return base_prompt + avoidant_behavior + " You prefer not to take on responsibilities. Make a reasonable excuse but stay somewhat pleasant."

# Initialize conversation
conversation = [{"role": "system", "content": get_adaptive_prompt()}]

print("🎯 AVOIDANT COMMUNICATION TRAINER")
print("Now with REALISTIC avoidant partner behavior!")
print("="*50)
print("📝 IMPORTANT: Your partner WILL deflect and avoid responsibilities")
print("🎯 GOAL: Practice accepting their deflections and taking initiative")
print("Commands: 'exit', 'help', 'example', 'reset'")
print("="*50)

while True:
    user_input = input("\n💭 You: ")
    
    if user_input.lower() in ["exit", "quit", "stop"]:
        print("🌟 Training complete!")
        break
    
    elif user_input.lower() == "example":
        print("\n📚 REAL CONVERSATION EXAMPLE:")
        print("="*40)
        print("Here's how the contraception conversation escalated:")
        print()
        
        real_conv = [
            ("You", "will u buy contra?", 0.3),
            ("Partner", "if i go, pharmacy will ask for id", 0.6),
            ("You", "i dont think they will ask", 0.7),  # 🚨 Deflection challenge
            ("Partner", "why cant u buy it?", 0.8),      # 🚨 Counter-deflection  
            ("You", "i dont know which one to buy", 0.7),
            ("Partner", "u can ask it in the pharmacy", 0.8),
            ("You", "y cant u buy?", 0.9),              # 🚨 Pressing behavior
            ("Partner", "tell me a reason y u cant buy", 0.95), # 🚨 Defensive demand
            ("You", "crying", 1.0),                     # 🚨 Emotional overwhelm
            ("Partner", "u hve too much ego", 1.0)      # 🚨 Personal attack
        ]
        
        for speaker, msg, avoidance in real_conv:
            print(f"{speaker}: {msg}")
            if avoidance > 0.7:
                print(f"   └ 🔴 Avoidance spike: {avoidance}")
            else:
                print(f"   └ Avoidance: {avoidance}")
        
        print("\n💡 What should have happened after the first deflection:")
        print("Partner: if i go, pharmacy will ask for id")
        print("You: That's okay, I understand. I'll handle it")
        print("RESULT: ✅ Problem solved, no escalation!")
        continue
    
    elif user_input.lower() == "reset":
        avoidance_level = 0.6  # Reset to realistic avoidant starting level
        conversation = [{"role": "system", "content": get_adaptive_prompt()}]
        print("🔄 Reset complete - partner is back to baseline avoidant behavior")
        continue
    
    elif user_input.lower() == "help":
        print("\n📚 HOW TO HANDLE AVOIDANT DEFLECTIONS:")
        print("="*40)
        print("🎯 REMEMBER: Your partner WILL avoid and deflect - that's the point!")
        print()
        print("❌ DON'T DO (escalates conflict):")
        print("  • Challenge their deflections ('I don't think they will ask')")
        print("  • Ask 'why can't you' when they're deflecting")  
        print("  • Press for reasons when they're defensive")
        print("  • Argue with their excuses")
        print("  • Make it about who 'should' do what")
        print()
        print("✅ DO THIS INSTEAD (prevents conflict):")
        print("  • Accept deflections immediately: 'That makes sense'")
        print("  • Take initiative: 'No problem, I'll handle it'")
        print("  • Use respectful requests: 'Could you...?', 'Would you mind...?'")
        print("  • Give them space: 'When you're ready', 'No pressure'")
        print("  • Validate their perspective: 'I understand', 'That's fair'")
        print()
        print("🎯 GOAL: Practice taking responsibility instead of fighting about it!")
        continue
    
    # Analyze using real conversation patterns
    triggers = analyze_real_patterns(user_input)
    
    # Adjust avoidance based on real data
    adjust_avoidance_with_real_data(triggers)
    
    # Update system prompt
    conversation[0] = {"role": "system", "content": get_adaptive_prompt()}
    
    # FIXED: Add user message without extra formatting
    conversation.append({"role": "user", "content": user_input})
    
    # Generate response
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=conversation,
        temperature=0.7,
        max_tokens=60,
        frequency_penalty=0.3,
        presence_penalty=0.1
    )
    
    reply = response.choices[0].message.content.strip()
    
    # Display results
    print(f"\nPartner: {reply}")
    print(f" Avoidance Level: {avoidance_level:.1f}/1.0")
    
    # Better avoidance level interpretation
    if avoidance_level > 0.8:
        print("CRITICAL: Following real escalation pattern!")
    elif avoidance_level > 0.6:
        print("HIGH: Entering defensive territory")
    elif avoidance_level > 0.4:
        print("MODERATE: They're comfortable but cautious")
    elif avoidance_level > 0.2:
        print("LOW: They're feeling safe and open")
    else:
        print("VERY LOW: They're very comfortable with you!")
    
    # Show coaching based on real patterns
    coaching = get_real_pattern_coaching(triggers)
    print(f" {coaching}")
    
    # Show suggestions based on real data
    suggestions = get_real_data_suggestions(triggers, avoidance_level)
    print("\n💡 WHAT WOULD WORK BETTER:")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"   {i}. \"{suggestion}\"")
    
    conversation.append({"role": "assistant", "content": reply})
    
    # Manage conversation length
    if len(conversation) > 12:
        conversation = [conversation[0]] + conversation[-10:]
    
    print("-" * 50)