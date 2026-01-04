"""
Sphota - Cognitive Meaning Engine Demo

Streamlit interface demonstrating the "Flash of Insight" through
Context Resolution Matrix (CRM) with Bhartṛhari's 12 factors.

This demo shows the critical difference between:
- Standard AI: Raw semantic similarity
- Sphota AI: Context-aware intent resolution
"""

import streamlit as st
from pathlib import Path
import sys
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core import PasyantiEngine, ContextResolutionMatrix
from core.context_manager import ContextManager


# Page configuration
st.set_page_config(
    page_title="Sphota - Cognitive Meaning Engine",
    page_icon="🕉️",
    layout="wide",
    initial_sidebar_state="expanded"
)


@st.cache_resource
def load_engine():
    """Load and cache the Paśyantī Engine."""
    intents_path = Path(__file__).parent / "data" / "intents.json"
    return PasyantiEngine(intents_path=str(intents_path))


@st.cache_resource
def load_context_manager():
    """Load and cache the Context Manager."""
    return ContextManager()



def main():
    """Main application entry point."""
    
    # Header
    st.title("🕉️ Sphota: Cognitive Meaning Engine")
    st.markdown("*Based on Bhartṛhari's Akhaṇḍapakṣa (Sentence Holism)*")
    st.markdown("---")
    
    # Load engines
    with st.spinner("Loading Paśyantī Engine & Context Manager..."):
        engine = load_engine()
        context_mgr = load_context_manager()
    
    # ============================================================================
    # SIDEBAR: Input Simulation
    # ============================================================================
    st.sidebar.header("🎯 Context Simulation")
    st.sidebar.markdown("*Configure the 12 Bhartṛhari Determinants*")
    st.sidebar.markdown("---")
    
    # Standard Controls
    st.sidebar.subheader("📍 Location")
    location = st.sidebar.selectbox(
        "Current Location",
        ["Home", "City", "Nature", "Office", "Kitchen", "Car", "Gym"],
        index=0,
        help="Where is the user located? (Deśa)"
    )
    
    st.sidebar.subheader("⏰ Time")
    time_mode = st.sidebar.radio("Time Mode", ["Current", "Manual"], index=0)
    
    if time_mode == "Current":
        current_hour = datetime.now().hour
        st.sidebar.info(f"🕐 {datetime.now().strftime('%I:%M %p')}")
    else:
        current_hour = st.sidebar.slider("Hour of Day", 0, 23, 12)
        st.sidebar.info(f"🕐 {current_hour:02d}:00")
    
    # Advanced Context Simulation Toggle
    st.sidebar.markdown("---")
    show_advanced = st.sidebar.checkbox("⚙️ Show Advanced Factors", value=False)
    
    if show_advanced:
        st.sidebar.markdown("### Advanced Context Factors")
        
        # Social Mode (Tests Aucitī - Propriety)
        social_mode = st.sidebar.selectbox(
            "Social Mode (Aucitī)",
            ["Casual", "Business"],
            index=0,
            help="Affects how formal/informal inputs are interpreted"
        )
        
        # System State (Tests Virodhitā - Conflict Check)
        system_state = st.sidebar.selectbox(
            "System State (Virodhitā)",
            ["ON", "OFF"],
            index=1,
            help="Current state of the controlled device. Detects contradictions."
        )
        
        # User History (Tests Sahacarya - Association)
        history_type = st.sidebar.selectbox(
            "Recent User Activity (Sahacarya)",
            ["None", "Travel", "Restaurant", "Shopping"],
            index=0,
            help="What has the user been doing? Boosts relevant intents."
        )
        
        # Voice Pitch (Tests Svara - Intonation)
        audio_pitch = st.sidebar.selectbox(
            "Voice Pitch (Svara)",
            ["Neutral", "Flat", "Rising", "High"],
            index=0,
            help="Audio pitch affects intent interpretation"
        )
        
        # Additional advanced factors
        st.sidebar.markdown("#### Confidence Sliders")
        input_confidence = st.sidebar.slider(
            "Input Quality (Apabhraṃśa Fidelity)",
            0.5, 1.0, 0.9, 0.05,
            help="How clear is the input? Low confidence widens search threshold."
        )
        
        user_demographic = st.sidebar.selectbox(
            "User Demographic (Vyakti)",
            ["Gen Z", "Millennial", "Gen X", "Boomer"],
            index=1,
            help="Affects vocabulary matching"
        )
        
    else:
        # Default values when advanced is off
        social_mode = "Casual"
        system_state = "OFF"
        history_type = "None"
        audio_pitch = "Neutral"
        input_confidence = 0.9
        user_demographic = "Millennial"
    
    # ============================================================================
    # MAIN AREA: Input and Results
    # ============================================================================
    st.header("🎤 Voice Command Input")
    
    # Quick example buttons
    col_ex1, col_ex2, col_ex3 = st.columns(3)
    
    with col_ex1:
        if st.button("🏞️ 'Bank' (River)", use_container_width=True):
            st.session_state.user_input = "bank"
            st.session_state.example_context = {
                "location": "Nature",
                "history_type": "None"
            }
    
    with col_ex2:
        if st.button("🏦 'Bank' (Finance)", use_container_width=True):
            st.session_state.user_input = "bank"
            st.session_state.example_context = {
                "location": "City",
                "history_type": "Shopping"
            }
    
    with col_ex3:
        if st.button("💡 'Turn on lights'", use_container_width=True):
            st.session_state.user_input = "turn on the lights"
            st.session_state.example_context = {
                "location": "Home",
                "system_state": "OFF"
            }
    
    # Apply example preset if selected
    if "example_context" in st.session_state:
        preset = st.session_state.example_context
        if "location" in preset:
            location = preset["location"]
        if "history_type" in preset:
            history_type = preset["history_type"]
        if "system_state" in preset:
            system_state = preset["system_state"]
        del st.session_state.example_context
    
    # User input text area
    user_input = st.text_area(
        "Enter your command",
        value=st.session_state.get("user_input", ""),
        placeholder="e.g., 'take me to the bank' or 'turn on the lights'",
        height=80,
        key="input_area"
    ) or ""
    
    # Process button
    col_btn1, col_btn2 = st.columns([3, 1])
    with col_btn1:
        process_clicked = st.button(
            "🔮 Resolve Intent (Paśyantī)",
            type="primary",
            use_container_width=True
        )
    
    with col_btn2:
        st.metric("Input Confidence", f"{input_confidence:.0%}")
    
    # ============================================================================
    # INTENT RESOLUTION WITH 12-FACTOR ANALYSIS
    # ============================================================================
    if process_clicked and user_input.strip():
        st.markdown("---")
        st.header("⚡ Intent Resolution Result")
        
        # Build context data for ContextManager
        command_history = []
        if history_type != "None":
            command_history = {
                "Travel": ["Search flights to Paris", "Check travel dates"],
                "Restaurant": ["Search restaurants near me", "Check cuisines"],
                "Shopping": ["Browse products", "Add to cart"]
            }.get(history_type, [])
        
        context_data = {
            "command_history": command_history,
            "system_state": system_state,
            "current_task_id": "demo_task",
            "current_screen": "Home",
            "social_mode": social_mode,
            "gps_tag": location,
            "current_hour": current_hour,
            "user_demographic": user_demographic,
            "audio_pitch": audio_pitch,
            "input_confidence": input_confidence,
            "user_input": user_input
        }
        
        # Resolve intent using engine
        with st.spinner("Analyzing context with 12-Factor Matrix..."):
            resolved_intents = engine.resolve_intent(
                user_input=user_input,
                current_context={
                    "desa": location.lower(),
                    "kala": datetime.now().replace(hour=current_hour),
                    "sahacarya": [history_type.lower()] if history_type != "None" else None
                },
                return_top_k=5
            )
        
        # Calculate confidence scores using ContextManager
        scored_results = []
        for result in resolved_intents[:3]:
            try:
                # Create a mock intent dict for context manager
                intent_dict = {
                    "type": result.intent.id,
                    "keywords": result.intent.id.split("_"),
                    "register": "Casual",
                    "vocabulary_level": "Neutral",
                    "urgency": "Normal",
                    "valid_screens": ["Home"],
                    "required_location": location,
                    "valid_time_range": (0, 23)
                }
                
                # Calculate confidence with 12-factor matrix
                twelve_factor_score = context_mgr.calculate_confidence(
                    intent=intent_dict,
                    context_data=context_data,
                    base_score=result.raw_similarity
                )
                
                scored_results.append({
                    "intent": result.intent.id,
                    "description": result.intent.description,
                    "raw_score": result.raw_similarity,
                    "twelve_factor_score": twelve_factor_score,
                    "boost": twelve_factor_score - result.raw_similarity
                })
            except Exception as e:
                # Fallback if context manager fails
                scored_results.append({
                    "intent": result.intent.id,
                    "description": result.intent.description,
                    "raw_score": result.raw_similarity,
                    "twelve_factor_score": result.context_adjusted_score,
                    "boost": result.context_adjusted_score - result.raw_similarity
                })
        
        # Display winning intent prominently
        winner = scored_results[0]
        
        st.success("")
        col_result1, col_result2, col_result3 = st.columns(3)
        
        with col_result1:
            st.metric("🎯 Winning Intent", winner["intent"].replace("_", " ").title())
        
        with col_result2:
            st.metric("Raw Score", f"{winner['raw_score']:.1%}")
        
        with col_result3:
            st.metric("12-Factor Score", f"{winner['twelve_factor_score']:.1%}")
        
        st.info(f"**Description:** {winner['description']}")
        
        # Expandable "Why" section
        with st.expander("🔍 Why did Sphota choose this?", expanded=True):
            st.markdown(f"""
            ### Context Resolution Analysis
            
            **Input:** "{user_input}"
            
            **Applied Context Factors:**
            - 📍 Location (Deśa): {location}
            - ⏰ Time (Kāla): {current_hour:02d}:00
            - 🔗 History (Sahacarya): {history_type if history_type != 'None' else 'None'}
            - 💬 Social Mode (Aucitī): {social_mode}
            - 📱 System State (Virodhitā): {system_state}
            - 🎙️ Voice Pitch (Svara): {audio_pitch}
            - 👤 Demographic (Vyakti): {user_demographic}
            - 🎤 Input Quality (Apabhraṃśa): {input_confidence:.0%}
            """)
            
            # Bar chart comparing top 3 intents
            st.markdown("#### Score Comparison: Top 3 Intents")
            
            chart_data = pd.DataFrame(scored_results[:3])
            
            fig = go.Figure(data=[
                go.Bar(
                    name="Raw Similarity",
                    x=chart_data["intent"],
                    y=chart_data["raw_score"],
                    marker_color="rgba(100, 150, 255, 0.7)"
                ),
                go.Bar(
                    name="12-Factor Score",
                    x=chart_data["intent"],
                    y=chart_data["twelve_factor_score"],
                    marker_color="rgba(0, 200, 100, 0.7)"
                )
            ])
            
            fig.update_layout(
                barmode="group",
                title="Raw Similarity vs. Context-Adjusted Score",
                xaxis_title="Intent",
                yaxis_title="Score",
                hovermode="x unified",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Detailed factor breakdown table
            st.markdown("#### Detailed Intent Scores")
            
            table_data = []
            for result in scored_results:
                table_data.append({
                    "Intent": result["intent"].replace("_", " ").title(),
                    "Raw Score": f"{result['raw_score']:.2%}",
                    "12-Factor Score": f"{result['twelve_factor_score']:.2%}",
                    "Boost/Penalty": f"{result['boost']:+.2%}",
                    "Description": result["description"][:50] + "..."
                })
            
            st.dataframe(
                pd.DataFrame(table_data),
                use_container_width=True,
                hide_index=True
            )
        
        # Show system info in sidebar
        st.sidebar.markdown("---")
        st.sidebar.info(f"✅ Context factors applied: 12-factor matrix")
        st.sidebar.info(f"📊 Intents analyzed: {len(scored_results)}")
    
    elif process_clicked:
        st.warning("⚠️ Please enter a voice command or text input first.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 20px;">
        <p><strong>Sphota: A Cognitive Meaning Engine</strong></p>
        <p>Based on Bhartṛhari's Akhaṇḍapakṣa (Sentence Holism)</p>
        <p><em>The 12-Factor Context Resolution Matrix disambiguates polysemic intents.</em></p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
