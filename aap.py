# app.py
# This creates the WEBSITE interface using Streamlit

import streamlit as st  # Tool for making websites easily
from main_agent import BehaviorChangeAgent  # Our AI brain
from feedback_manager import FeedbackManager  # Feedback system
import time  # Tool for adding delays

# ============================================
# PAGE SETUP
# ============================================

st.set_page_config(
    page_title="Behavior Change AI",  # Tab title
    page_icon="🧠",  # Emoji in browser tab
    layout="wide",  # Use full screen width
    initial_sidebar_state="expanded"  # Show sidebar by default
)

# ============================================
# CUSTOM STYLING (Make it look pretty)
# ============================================

st.markdown("""
<style>
    .intervention-box {
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 15px;
        font-size: 1.1rem;
        line-height: 1.6;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# INITIALIZE COMPONENTS (Create AI brain and feedback system)
# ============================================

@st.cache_resource  # Cache = Save in memory so it doesn't recreate every time
def initialize_agent():
    """Create the AI agent once and reuse it"""
    return BehaviorChangeAgent()

@st.cache_resource
def initialize_feedback():
    """Create feedback manager once and reuse it"""
    return FeedbackManager()

# Load components
try:
    agent = initialize_agent()
    feedback_manager = initialize_feedback()
except Exception as e:
    st.error(f"⚠️ Error: {e}")
    st.info("💡 Make sure to set your GEMINI_API_KEY in config.py")
    st.stop()  # Stop here if error

# ============================================
# SESSION STATE (Remember things across page refreshes)
# ============================================

if 'history' not in st.session_state:
    st.session_state.history = []  # Create empty history list

# ============================================
# MAIN TITLE
# ============================================

st.title("🧠 Behavior Change AI Assistant")
st.markdown("""
<div style='text-align: center; margin-bottom: 2rem;'>
    <p>Powered by <b>Google Gemini 2.0</b> & Evidence-Based Psychology</p>
    <p style='font-size: 0.9rem; color: #666;'>
        COM-B Model • Self-Determination Theory • Motivational Interviewing • Behavioral Economics
    </p>
</div>
""", unsafe_allow_html=True)

st.divider()  # Horizontal line

# ============================================
# MAIN INTERFACE (Two columns)
# ============================================

col1, col2 = st.columns([2, 1])  # Left column is 2x wider than right

# LEFT COLUMN: User inputs
with col1:
    st.subheader("💬 Tell Me About Your Goal")
    
    # Text input for goal
    user_goal = st.text_input(
        "What behavior do you want to change?",
        placeholder="e.g., exercise regularly, study more, eat healthier...",
        help="Be specific about what you want to accomplish"
    )
    
    # Text area for barrier (bigger than text input)
    user_barrier = st.text_area(
        "What's stopping you?",
        placeholder="e.g., I'm too tired, I don't have time, I keep forgetting...",
        height=100,
        help="Describe your main challenge"
    )
    
    # Optional context (hidden by default)
    with st.expander("🔍 Add Context (Optional)"):
        user_context = st.text_area(
            "Any additional context?",
            placeholder="e.g., I'm a student, I work night shifts...",
            height=80
        )
    
    # Big button to generate intervention
    generate_button = st.button(
        "✨ Get Personalized Intervention", 
        type="primary",  # Makes it blue and prominent
        use_container_width=True  # Full width
    )

# RIGHT COLUMN: Instructions
with col2:
    st.markdown("### 🎯 How It Works")
    st.markdown("""
    **1️⃣** Share your goal and barrier
    
    **2️⃣** AI analyzes using COM-B model
    
    **3️⃣** Selects evidence-based technique
    
    **4️⃣** Creates personalized intervention
    
    **5️⃣** You provide feedback
    
    ---
    
    🚀 **Powered by Gemini 2.0**  
    🔬 **10 Evidence-Based Techniques**  
    ⚡ **< 30 Second Response Time**
    """)

# ============================================
# GENERATE INTERVENTION (When button is clicked)
# ============================================

if generate_button:
    # Input validation (check if fields are filled)
    if not user_goal or not user_barrier:
        st.error("⚠️ Please fill in both your goal and barrier!")
    elif len(user_goal) < 5:
        st.error("⚠️ Please describe your goal in more detail")
    elif len(user_barrier) < 10:
        st.error("⚠️ Please describe your barrier in more detail")
    else:
        # Show loading animation
        with st.spinner("🤔 Analyzing with Gemini AI..."):
            time.sleep(0.5)  # Brief pause for effect
            
            try:
                # Call our AI agent
                result = agent.run(user_goal, user_barrier)
                
                if not result:
                    st.error("❌ Error generating intervention")
                else:
                    # SUCCESS! Show results
                    st.success("✅ Your intervention is ready!")
                    st.markdown("---")
                    
                    # Display intervention in pretty box
                    st.markdown("### 💡 Your Personalized Intervention")
                    st.markdown(
                        f'<div class="intervention-box">{result["intervention_text"]}</div>', 
                        unsafe_allow_html=True
                    )
                    
                    st.markdown("---")
                    
                    # Show details in 4 columns
                    col_a, col_b, col_c, col_d = st.columns(4)
                    
                    with col_a:
                        st.metric("📖 Technique", result['technique_name'])
                    
                    with col_b:
                        st.metric("🔬 Theory", result['theory'])
                    
                    with col_c:
                        st.metric("🎯 Targets", result['target_component'].title())
                    
                    with col_d:
                        st.metric("⏱️ Duration", f"{result['duration_minutes']} min")
                    
                    # Expandable section for evidence
                    with st.expander("📊 Scientific Evidence"):
                        st.write(result['evidence'])
                    
                    # Save to history
                    st.session_state.history.append({
                        'goal': user_goal,
                        'barrier': user_barrier,
                        'component': result['target_component'],
                        'technique': result['technique_name'],
                        'intervention': result['intervention_text'],
                        'theory': result['theory']
                    })
                    
                    # ============================================
                    # FEEDBACK SECTION
                    # ============================================
                    
                    st.markdown("---")
                    st.subheader("📝 Your Feedback")
                    
                    feedback_col1, feedback_col2 = st.columns(2)
                    
                    with feedback_col1:
                        rating = st.slider(
                            "How helpful is this?",
                            min_value=1,
                            max_value=5,
                            value=3,
                            help="1 = Not helpful, 5 = Very helpful"
                        )
                    
                    with feedback_col2:
                        would_try = st.radio(
                            "Would you try this?",
                            ["Yes", "Maybe", "No"],
                            horizontal=True
                        )
                    
                    feedback_text = st.text_area(
                        "Additional thoughts? (Optional)",
                        placeholder="What did you like? What could be improved?",
                        height=80
                    )
                    
                    # Submit feedback button
                    if st.button("✅ Submit Feedback"):
                        success = feedback_manager.save_feedback(
                            user_goal=user_goal,
                            user_barrier=user_barrier,
                            target_component=result['target_component'],
                            technique_name=result['technique_name'],
                            theory=result['theory'],
                            rating=rating,
                            would_try=would_try,
                            feedback_text=feedback_text
                        )
                        
                        if success:
                            st.success("✅ Thank you! Feedback saved.")
                            st.balloons()  # Celebration animation!
                        else:
                            st.error("⚠️ Error saving feedback")
            
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.info("💡 Check your Gemini API key in config.py")

# ============================================
# SIDEBAR: Statistics & History
# ============================================

st.sidebar.title("📊 System Statistics")

# Get statistics from feedback manager
stats = feedback_manager.get_statistics()

if stats:
    # Display metrics
    st.sidebar.metric("🎯 Total Interventions", stats['total_responses'])
    st.sidebar.metric("⭐ Average Rating", f"{stats['average_rating']:.2f}/5")
    st.sidebar.metric("✅ Would Try", f"{stats['would_try_percent']:.1f}%")
    
    # Show top techniques
    st.sidebar.markdown("### 🏆 Top Techniques")
    sorted_techniques = sorted(
        stats['technique_performance'].items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    for tech, avg in sorted_techniques[:5]:
        st.sidebar.write(f"**{tech}:** {avg:.2f}/5")
    
    # Show barrier type distribution
    if 'component_distribution' in stats:
        st.sidebar.markdown("### 🎯 Barrier Types")
        for comp, count in stats['component_distribution'].items():
            percent = (count / stats['total_responses']) * 100
            st.sidebar.write(f"**{comp.title()}:** {count} ({percent:.1f}%)")

else:
    st.sidebar.info("No data yet. Start using the system!")

# Download feedback button
st.sidebar.markdown("---")
if st.sidebar.button("📥 Download Data"):
    try:
        with open('feedback_data.csv', 'r', encoding='utf-8') as f:
            csv_data = f.read()
        st.sidebar.download_button(
            label="💾 Download CSV",
            data=csv_data,
            file_name=f"feedback_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    except:
        st.sidebar.warning("No data yet")

# Show session history
if len(st.session_state.history) > 0:
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📜 Session History")
    
    for i, item in enumerate(reversed(st.session_state.history[-5:]), 1):
        with st.sidebar.expander(f"{i}. {item['goal'][:25]}..."):
            st.write(f"**Barrier:** {item['barrier']}")
            st.write(f"**Type:** {item['component'].title()}")
            st.write(f"**Technique:** {item['technique']}")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("### 🤖 About")
st.sidebar.info("""
**Built with:**
- Google Gemini 2.0
- LangChain
- Streamlit
- Psychology science

**100% Free & Open Source**
""")
