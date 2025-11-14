# main_agent.py
# This is the MAIN BRAIN of our AI system

# ============================================
# STEP 1: Import Tools (Like getting tools from a toolbox)
# ============================================

import google.generativeai as genai  # Google's AI tool
from config import GEMINI_API_KEY, GEMINI_MODEL, TEMPERATURE  # Our secret key
import json  # Tool for reading JSON files
from datetime import datetime  # Tool for dates/times

# ============================================
# STEP 2: Create the AI Agent Class
# ============================================
# Think of a "class" as a blueprint for building a robot

class BehaviorChangeAgent:
    """
    This is our AI psychologist robot!
    It can:
    1. Listen to problems
    2. Figure out what's wrong (capability/opportunity/motivation)
    3. Pick the right technique
    4. Give personalized advice
    """
    
    def __init__(self):
        """
        __init__ = "Initialize" = Set up the robot when it's first created
        This runs ONCE when you create the agent
        """
        
        # Connect to Google Gemini using our API key
        genai.configure(api_key='AIzaSyD3kNAUNVxtmo7TlGDy76ysgix3WYds-Fc')
        
        # Set up the AI model with settings
        self.model = genai.GenerativeModel(
            model_name=GEMINI_MODEL,  # Which AI to use
            generation_config={
                "temperature": 0.8,  # How creative (0.7 = balanced)
                "top_p": 0.95,  # Controls randomness
                "top_k": 40,  # Controls variety
                "max_output_tokens": 8192,  # Maximum response length
            }
        )
        
        # Load all 10 psychology techniques from JSON file
        self.techniques = self._load_techniques()
        
        print("✅ AI Brain is ready!")
    
    def _load_techniques(self):
        """
        Load the 10 techniques from techniques_library.json
        _ before name means "private function" (only used inside this class)
        """
        try:
            # Open the JSON file and read it
            with open('techniques_library.json', 'r', encoding='utf-8') as f:
                return json.load(f)  # Convert JSON to Python list
        except FileNotFoundError:
            print("⚠️ ERROR: techniques_library.json not found!")
            return []  # Return empty list if file missing
    
    def analyze_barrier(self, barrier_text):
        """
        STEP 1: Figure out if problem is Capability, Opportunity, or Motivation
        
        Example:
        Input: "I don't know how to start exercising"
        Output: "capability"
        """
        try:
            # Create a prompt (question) for AI
            prompt = f"""You are a psychology expert. Analyze this barrier:

"{barrier_text}"

Which COM-B component is missing?
- Capability: lack of skills, knowledge, or ability (they don't know HOW)
- Opportunity: lack of time, resources, or external support (external barriers)
- Motivation: lack of desire, willpower, or interest (they don't WANT to)

Respond with ONLY ONE WORD: Capability, Opportunity, or Motivation

Answer:"""
            
            # Ask Gemini AI
            response = self.model.generate_content(prompt)
            component = response.text.strip().lower()  # Get answer and make it lowercase
            
            # Convert AI's answer to our format
            if 'capab' in component:
                return 'capability'
            elif 'opportun' in component:
                return 'opportunity'
            else:
                return 'motivation'
        
        except Exception as e:
            # If something goes wrong, default to motivation
            print(f"⚠️ Error: {e}")
            return 'motivation'
    
    def select_technique(self, barrier_text, target_component):
        """
        STEP 2: Pick the BEST technique from our 10 options
        
        How it works:
        1. Look for techniques that match the component (capability/opportunity/motivation)
        2. Check if any keywords match the user's barrier
        3. Return the best match
        """
        try:
            barrier_lower = barrier_text.lower()  # Make barrier text lowercase
            
            # Loop through all 10 techniques
            for tech in self.techniques:
                # First check: Does it target the right component?
                if tech['target_component'] == target_component:
                    # Second check: Do any keywords match?
                    for keyword in tech['barrier_keywords']:
                        if keyword in barrier_lower:
                            return tech  # Found a match!
            
            # If no keyword match, return first technique with right component
            for tech in self.techniques:
                if tech['target_component'] == target_component:
                    return tech
            
            # Last resort: return first technique
            return self.techniques[0] if self.techniques else None
        
        except Exception as e:
            print(f"⚠️ Error: {e}")
            return self.techniques[0] if self.techniques else None
    
    def generate_intervention(self, user_goal, technique, barrier_text):
        """
        STEP 3: Create a personalized message using Gemini AI
        
        Example:
        Input: 
        - Goal: "exercise more"
        - Technique: "Temptation Bundling"
        - Barrier: "too boring"
        
        Output: "Let's make exercise fun! Only allow yourself to watch your favorite show while on the treadmill. Suddenly, you'll look forward to gym time!"
        """
        try:
            # Replace [GOAL] in the template with actual goal
            prompt_template = technique['prompt_template'].replace('[GOAL]', user_goal)
            
            # Create a detailed instruction for Gemini
            final_prompt = f"""You are a warm, supportive behavior change coach.

User's Goal: {user_goal}
User's Barrier: {barrier_text}
Technique: {technique['name']} (based on {technique['theory']})

Your task:
Create a personalized, friendly micro-intervention (2-3 sentences) using this framework:
{prompt_template}

Requirements:
- Be warm and empathetic, like a supportive friend
- Make it personal to THEIR specific situation
- Be specific and actionable
- Keep it under 100 words
- Sound encouraging, not preachy

Generate the intervention now:"""
            
            # Ask Gemini to create the message
            response = self.model.generate_content(final_prompt)
            intervention_text = response.text.strip()
            
            # Return all the information as a dictionary
            return {
                'intervention_text': intervention_text,
                'technique_name': technique['name'],
                'theory': technique['theory'],
                'duration_minutes': technique['duration_minutes'],
                'evidence': technique['evidence_base'],
                'target_component': technique['target_component']
            }
        
        except Exception as e:
            print(f"⚠️ Error: {e}")
            # Fallback if AI fails
            return {
                'intervention_text': f"Let's work on {user_goal}. {technique['prompt_template'].replace('[GOAL]', user_goal)}",
                'technique_name': technique['name'],
                'theory': technique['theory'],
                'duration_minutes': technique['duration_minutes'],
                'evidence': technique['evidence_base'],
                'target_component': technique['target_component']
            }
    
    def run(self, user_goal, user_barrier):
        """
        MAIN FUNCTION: Runs the complete workflow
        
        Steps:
        1. Analyze barrier → Get component (capability/opportunity/motivation)
        2. Select technique → Pick best match from 10 techniques
        3. Generate intervention → Create personalized message
        
        This is what you call from outside to use the AI!
        """
        print("\n🔍 Analyzing your barrier...")
        target_component = self.analyze_barrier(user_barrier)
        print(f"   Identified: {target_component.upper()} component needed\n")
        
        print("📚 Selecting best technique...")
        technique = self.select_technique(user_barrier, target_component)
        
        if not technique:
            print("❌ No techniques available")
            return None
        
        print(f"   Selected: {technique['name']}\n")
        
        print("✨ Creating your personalized intervention...\n")
        intervention = self.generate_intervention(user_goal, technique, user_barrier)
        
        return intervention


# ============================================
# TESTING SECTION (Only runs if you run this file directly)
# ============================================

if __name__ == "__main__":
    print("🧪 Testing the AI Agent\n")
    print("="*60)
    
    # Create the agent
    agent = BehaviorChangeAgent()
    
    # Test with an example
    goal = "exercise regularly"
    barrier = "I'm always too tired after work"
    
    # Run the agent
    result = agent.run(goal, barrier)
    
    # Display results
    if result:
        print("\n" + "="*60)
        print("💡 YOUR PERSONALIZED INTERVENTION")
        print("="*60)
        print(f"\n{result['intervention_text']}\n")
        print(f"📖 Technique: {result['technique_name']}")
        print(f"🔬 Based on: {result['theory']}")
        print(f"🎯 Targets: {result['target_component'].upper()}")
        print(f"⏱️  Duration: {result['duration_minutes']} minutes")
        print(f"📊 Evidence: {result['evidence']}\n")
