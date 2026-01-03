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

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core import PasyantiEngine, ContextResolutionMatrix


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


def main():
    """Main application entry point."""
    
    # Header
    st.title("🕉️ Sphota: Cognitive Meaning Engine")
    st.markdown("*Based on Bhartṛhari's Akhaṇḍapakṣa (Sentence Holism)*")
    st.markdown("---")
    
    # Load engine
    with st.spinner("Loading Paśyantī Engine..."):
        engine = load_engine()
    
    # Sidebar - Context Configuration
    st.sidebar.header("🎯 Context Factors")
    st.sidebar.markdown("*Configure the 12 Bhartṛhari Determinants*")
    st.sidebar.markdown("---")
    
    # === Spatiotemporal Factors ===
    st.sidebar.subheader("📍 Deśa (Place)")
    desa = st.sidebar.selectbox(
        "Current Location",
        ["home", "nature", "city", "kitchen", "car", "office", "gym"],
        index=0,
        help="Where is the user located?"
    )
    
    st.sidebar.subheader("⏰ Kāla (Time)")
    kala_mode = st.sidebar.radio(
        "Time Mode",
        ["Auto (Current)", "Manual"],
        index=0
    )
    
    if kala_mode == "Auto (Current)":
        kala = datetime.now()
        st.sidebar.info(f"Current: {kala.strftime('%I:%M %p')}")
    else:
        hour = st.sidebar.slider("Hour", 0, 23, 12)
        kala = datetime.now().replace(hour=hour, minute=0)
    
    # === Associative Factors ===
    st.sidebar.subheader("🔗 Sahacārya (Association)")
    sahacarya_input = st.sidebar.text_input(
        "Recent Context (comma-separated)",
        placeholder="e.g., fishing, outdoor",
        help="What has the user been doing recently?"
    )
    sahacarya = [s.strip() for s in sahacarya_input.split(",")] if sahacarya_input else None
    
    # === Semantic Factors ===
    st.sidebar.subheader("🎯 Artha (Purpose)")
    artha = st.sidebar.selectbox(
        "User's Goal",
        ["None", "productivity", "entertainment", "information", "communication", "automation"],
        index=0
    )
    artha = artha if artha != "None" else None
    
    st.sidebar.subheader("📋 Prakaraṇa (Situation)")
    prakarana = st.sidebar.selectbox(
        "Current Situation",
        ["None", "morning_routine", "cooking", "travel", "work_session", "evening_relaxation"],
        index=0
    )
    prakarana = prakarana if prakarana != "None" else None
    
    # Advanced factors (collapsible)
    with st.sidebar.expander("⚙️ Advanced Factors"):
        vyakti = st.text_input("Vyakti (User Profile)", placeholder="user_id")
        vyakti = vyakti if vyakti else None
        
        shabda_samarthya = st.slider(
            "Śabda-sāmarthya (Word Capacity)",
            0.0, 1.0, 0.8, 0.1,
            help="Semantic richness of input"
        )
        
        auciti = st.slider(
            "Aucitī (Propriety)",
            -1.0, 1.0, 0.0, 0.1,
            help="Contextual appropriateness"
        )
    
    # Main area
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.header("🎤 Vaikharī Layer (Input)")
        
        # Polysemic example selector
        st.subheader("Quick Examples")
        example_col1, example_col2, example_col3 = st.columns(3)
        
        with example_col1:
            if st.button("🏞️ River Bank", use_container_width=True):
                st.session_state.user_input = "take me to the bank"
                st.session_state.preset_context = {
                    "desa": "nature",
                    "sahacarya": ["fishing", "outdoor"]
                }
        
        with example_col2:
            if st.button("🏦 Financial Bank", use_container_width=True):
                st.session_state.user_input = "take me to the bank"
                st.session_state.preset_context = {
                    "desa": "city",
                    "sahacarya": ["money", "atm"]
                }
        
        with example_col3:
            if st.button("💡 Lights On", use_container_width=True):
                st.session_state.user_input = "turn on the lights"
                st.session_state.preset_context = {
                    "desa": "home",
                    "artha": "automation"
                }
        
        # Apply preset if exists
        if "preset_context" in st.session_state:
            preset = st.session_state.preset_context
            if "desa" in preset:
                desa = preset["desa"]
            if "sahacarya" in preset:
                sahacarya = preset["sahacarya"]
            if "artha" in preset:
                artha = preset["artha"]
            del st.session_state.preset_context
        
        # User input
        user_input = st.text_area(
            "Voice Command / Text Input",
            value=st.session_state.get("user_input", ""),
            placeholder="e.g., 'take me to the bank' or 'turn on lights'",
            height=100,
            key="input_area"
        ) or ""  # Ensure it's always a string, never None
        
        # Process button
        process_clicked = st.button(
            "🔮 Resolve Intent (Paśyantī)",
            type="primary",
            use_container_width=True
        )
    
    with col2:
        st.header("ℹ️ System Info")
        
        model_info = engine.get_model_info()
        st.metric("Loaded Intents", model_info["intent_count"])
        st.metric("Embedding Dim", model_info["embedding_dimension"])
        
        st.info(f"**📍 Location:** {desa.title()}")
        st.info(f"**⏰ Time:** {kala.strftime('%I:%M %p')}")
        
        if sahacarya:
            st.info(f"**🔗 Context:** {', '.join(sahacarya)}")
    
    # Process intent resolution
    if process_clicked and user_input.strip():
        st.markdown("---")
        st.header("⚡ The Flash of Insight (Paśyantī)")
        
        # Build context dictionary
        context = {
            "desa": desa,
            "kala": kala,
            "sahacarya": sahacarya,
            "artha": artha,
            "prakarana": prakarana,
            "vyakti": vyakti,
            "shabda_samarthya": shabda_samarthya,
            "auciti": auciti
        }
        
        # Resolve intent
        with st.spinner("Resolving Vākyasphoṭa..."):
            resolved_intents = engine.resolve_intent(
                user_input=user_input,
                current_context=context,
                return_top_k=5
            )
        
        # Display results
        col_result1, col_result2 = st.columns(2)
        
        with col_result1:
            st.subheader("🤖 Standard AI (Raw Similarity)")
            st.caption("Pure semantic matching - context-blind")
            
            for i, result in enumerate(resolved_intents[:3], 1):
                score_pct = result.raw_similarity * 100
                
                # Create colored box
                if i == 1:
                    st.markdown(f"""
                    <div style="padding: 15px; border-radius: 10px; background-color: #f0f0f0; margin-bottom: 10px;">
                        <h4>#{i} {result.intent.id}</h4>
                        <p><strong>Score:</strong> {score_pct:.1f}%</p>
                        <p style="font-size: 0.9em;">{result.intent.description}</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="padding: 10px; border-radius: 5px; background-color: #fafafa; margin-bottom: 5px;">
                        <p><strong>#{i} {result.intent.id}</strong> - {score_pct:.1f}%</p>
                    </div>
                    """, unsafe_allow_html=True)
        
        with col_result2:
            st.subheader("🕉️ Sphota AI (Context-Resolved)")
            st.caption("12-factor contextual resolution")
            
            for i, result in enumerate(resolved_intents[:3], 1):
                score_pct = result.context_adjusted_score * 100
                boost = (result.context_adjusted_score - result.raw_similarity) * 100
                
                # Determine color based on boost
                if boost > 0:
                    bg_color = "#d4edda"  # Green
                    border_color = "#28a745"
                elif boost < 0:
                    bg_color = "#f8d7da"  # Red
                    border_color = "#dc3545"
                else:
                    bg_color = "#f0f0f0"
                    border_color = "#6c757d"
                
                if i == 1:
                    st.markdown(f"""
                    <div style="padding: 15px; border-radius: 10px; background-color: {bg_color}; 
                                border: 3px solid {border_color}; margin-bottom: 10px;">
                        <h4>✨ #{i} {result.intent.id}</h4>
                        <p><strong>Score:</strong> {score_pct:.1f}% 
                           <span style="color: {'green' if boost > 0 else 'red'};">
                           ({boost:+.1f}%)
                           </span>
                        </p>
                        <p style="font-size: 0.9em;">{result.intent.description}</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="padding: 10px; border-radius: 5px; background-color: {bg_color}; 
                                border-left: 3px solid {border_color}; margin-bottom: 5px;">
                        <p><strong>#{i} {result.intent.id}</strong> - {score_pct:.1f}% 
                           <span style="color: {'green' if boost > 0 else 'red'};">
                           ({boost:+.1f}%)
                           </span>
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Winner announcement
        winner = resolved_intents[0]
        st.markdown("---")
        st.success(f"""
        ### 🎯 Resolved Vākyasphoṭa: **{winner.intent.id.upper()}**
        
        **Pure Meaning:** {winner.intent.pure_text}
        
        **Confidence:** {winner.confidence * 100:.1f}%
        """)
        
        # Show active factors
        if winner.active_factors:
            st.info(f"**Active Context Factors:** {', '.join(winner.active_factors)}")
        
        # Detailed comparison table
        with st.expander("📊 Detailed Score Comparison"):
            st.markdown("#### Top 5 Intents")
            
            comparison_data = []
            for result in resolved_intents[:5]:
                comparison_data.append({
                    "Intent": result.intent.id,
                    "Raw Score": f"{result.raw_similarity * 100:.1f}%",
                    "Context Score": f"{result.context_adjusted_score * 100:.1f}%",
                    "Boost/Penalty": f"{(result.context_adjusted_score - result.raw_similarity) * 100:+.1f}%",
                    "Description": result.intent.description
                })
            
            st.table(comparison_data)
        
        # Explanation
        with st.expander("🔍 Resolution Explanation"):
            explanation = engine.explain_resolution(user_input, context)
            
            st.json(explanation)
    
    elif process_clicked:
        st.warning("⚠️ Please enter a voice command or text input first.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 20px;">
        <p><strong>Sphota: A Cognitive Meaning Engine</strong></p>
        <p>Based on Bhartṛhari's Akhaṇḍapakṣa (Sentence Holism)</p>
        <p><em>Unlike LLMs that predict tokens, Sphota extracts holistic meaning.</em></p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
