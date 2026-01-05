"""
Sphota: Cognitive Meaning Engine - Interactive Demo

A professional, interactive demonstration of the Sphota intent resolution system.
This app combines contextual analysis with multi-factor scoring to resolve user intents
with high accuracy and explainability.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import json
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

from core.intent_engine import IntentEngine
from core.context_manager import ContextManager


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Sphota: Cognitive Meaning Engine",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-title {
        text-align: center;
        color: #1f77b4;
        margin-bottom: 30px;
    }
    .winner-box {
        background-color: #d4edda;
        border: 2px solid #28a745;
        border-radius: 8px;
        padding: 20px;
        margin: 20px 0;
        text-align: center;
    }
    .winner-text {
        color: #155724;
        font-size: 28px;
        font-weight: bold;
    }
    .explanation-box {
        background-color: #e7f3ff;
        border-left: 4px solid #2196F3;
        padding: 15px;
        margin: 15px 0;
        border-radius: 4px;
    }
    .score-container {
        display: flex;
        justify-content: space-around;
        margin: 20px 0;
    }
    .score-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
        flex: 1;
        margin: 0 10px;
    }
    .metric-label {
        color: #666;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .metric-value {
        color: #1f77b4;
        font-size: 24px;
        font-weight: bold;
        margin-top: 5px;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# CACHE FUNCTIONS
# ============================================================================

@st.cache_resource
def load_intent_engine():
    """Load the Intent Engine once per session."""
    intents_path = Path(__file__).parent / "data" / "intents.json"
    return IntentEngine(intents_path=str(intents_path))


@st.cache_resource
def load_context_manager():
    """Load the Context Manager once per session."""
    return ContextManager()


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def load_intent_database(db_path: str = "data/intent_db.json") -> Dict[str, Any]:
    """
    Load the intent database from JSON file.
    Falls back to a minimal default if file is missing or empty.
    """
    try:
        if Path(db_path).exists():
            with open(db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if data and len(data) > 0:
                    return data
    except Exception as e:
        st.warning(f"Could not load intent database: {e}")
    
    # Fallback: Minimal default intent
    return {
        "default_fallback": {
            "intent_id": "fallback",
            "user_input": "fallback",
            "primary_type": "general",
            "keywords": ["default"],
            "register": "informal",
            "description": "Fallback intent for unrecognized inputs"
        }
    }


def build_context_object(
    location: str,
    time_period: str,
    social_mode: str,
    user_history: str
) -> Dict[str, Any]:
    """
    Construct a context object from sidebar selections.
    
    This is passed to the intent engine for multi-factor scoring.
    """
    from datetime import datetime
    
    # Map location to desa (string expected)
    location_map = {
        "City Center": "city",
        "Nature Reserve": "nature",
        "Home": "home",
        "Office": "office"
    }
    
    # Map user history to sahacarya (list of strings expected)
    history_map = {
        "Finance Related": ["finance", "banking", "money"],
        "Nature Related": ["nature", "outdoor", "wildlife"],
        "None": None
    }
    
    # Map social mode to auciti score (float expected: -1 to 1)
    # Formal/Business = 0.8 (high propriety), Casual = 0.0 (neutral)
    auciti_map = {
        "Business/Formal": 0.8,
        "Casual": 0.0
    }
    
    # Build context for IntentEngine
    context_map = {
        "location": location_map.get(location, "home"),
        "time": datetime.now(),
        "history": history_map.get(user_history),
        "propriety": auciti_map.get(social_mode, 0.0),  # Now a float!
        "user_profile": "professional" if social_mode == "Business/Formal" else "general"
    }
    
    return context_map


def process_intent(
    user_input: str,
    context_data: Dict[str, Any],
    intent_engine: IntentEngine,
    context_manager: ContextManager,
    intent_db: Dict[str, Any]
) -> Tuple[Optional[str], Dict[str, Any], List[Tuple[str, float]]]:
    """
    Process user input through the intent resolution pipeline.
    
    Returns:
        Tuple of (winning_intent, analysis_dict, top_3_scores)
    """
    if not user_input.strip():
        return None, {}, []
    
    try:
        # Resolve intent using the engine (returns List[ResolvedIntent])
        results = intent_engine.resolve_intent(user_input, context_data, return_top_k=3)
        
        if not results or len(results) == 0:
            return None, {}, []
        
        # Get the winning result
        winner = results[0]
        winning_intent = winner.intent.id
        base_score = winner.raw_similarity
        context_adjusted_score = winner.context_adjusted_score
        
        # Build context for ContextManager (additional 12-factor boost)
        time_obj = context_data.get("time")
        current_hour = time_obj.hour if time_obj else 12
        
        # Get sahacarya (command history) and ensure it's a list of strings
        history_data = context_data.get("history", [])
        if history_data is None:
            command_history_list = []
        elif isinstance(history_data, list):
            # Ensure all items are strings
            command_history_list = [str(item) for item in history_data if item]
        else:
            command_history_list = []
        
        cm_context = {
            "command_history": command_history_list,
            "system_state": "OFF",
            "social_mode": str(context_data.get("propriety", "casual")),
            "gps_tag": str(context_data.get("location", "home")),
            "current_hour": current_hour,
            "user_demographic": str(context_data.get("user_profile", "general")),
            "audio_pitch": "Neutral",
            "input_confidence": 0.9,
            "user_input": user_input
        }
        
        # Create mock intent dict for context manager with proper types
        intent_keywords = winning_intent.split("_")
        intent_dict = {
            "type": str(winning_intent),
            "keywords": intent_keywords,
            "register": str(context_data.get("propriety", "casual")).title(),
            "vocabulary_level": "Neutral",
            "urgency": "Normal",
            "valid_screens": ["Home"],
            "required_location": str(context_data.get("location", "home")),
            "valid_time_range": (0, 23)
        }
        
        # Apply additional context manager boost
        final_score = context_manager.calculate_confidence(
            intent=intent_dict,
            context_data=cm_context,
            base_score=context_adjusted_score
        )
        
        # Prepare analysis
        analysis = {
            "winning_intent": winning_intent,
            "base_score": base_score,
            "context_boost": final_score,
            "location": context_data.get("location", "Unknown"),
            "time": str(context_data.get("time", "Unknown")),
            "intent_data": intent_db.get(winning_intent, {}),
            "description": winner.intent.description
        }
        
        # Get top 3 scores for comparison
        top_3 = [(r.intent.id, r.confidence) for r in results[:3]]
        
        return winning_intent, analysis, top_3
    
    except Exception as e:
        st.error(f"Error processing intent: {e}")
        import traceback
        st.error(traceback.format_exc())
        return None, {}, []


def generate_explanation(analysis: Dict[str, Any]) -> str:
    """
    Generate a human-readable explanation of why the winning intent was chosen.
    """
    location = analysis.get("location", "Unknown")
    time = analysis.get("time", "Unknown")
    base_score = analysis.get("base_score", 0)
    boost = analysis.get("context_boost", 0)
    description = analysis.get("description", "No description available")
    
    explanation = (
        f"**Processing Analysis:**\n\n"
        f"• **Description:** {description}\n"
        f"• **Location Context:** {location} (contextual weighting applied)\n"
        f"• **Time of Day:** {time}\n"
        f"• **Raw Similarity Score:** {base_score:.2%}\n"
        f"• **Context Boost:** +{(boost - base_score):.2%}\n"
        f"• **Final Score:** {boost:.2%}\n\n"
        f"The selected intent best matches your input given the current context factors."
    )
    
    return explanation


# ============================================================================
# SIDEBAR: CONTEXT SIMULATION
# ============================================================================

st.sidebar.markdown("### 🎛️ Context Simulation Panel")
st.sidebar.markdown("Configure the contextual factors for intent resolution.")
st.sidebar.markdown("---")

# Location Control
location = st.sidebar.selectbox(
    label="📍 Location",
    options=["City Center", "Nature Reserve", "Home", "Office"],
    help="Current user location - affects intent interpretation"
)

# Time Control
time_period = st.sidebar.selectbox(
    label="⏰ Time of Day",
    options=["Morning", "Work Hours", "Evening", "Late Night"],
    help="Current time period - influences intent meaning"
)

# Social Mode Control
social_mode = st.sidebar.selectbox(
    label="👥 Social Mode",
    options=["Casual", "Business/Formal"],
    help="Communication formality level"
)

# User History Control
user_history = st.sidebar.selectbox(
    label="📚 User Background",
    options=["Finance Related", "Nature Related", "None"],
    help="User's domain expertise - affects disambiguation"
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    "**Note:** Context factors influence the confidence scoring for polysemic "
    "(multi-meaning) words and phrases."
)


# ============================================================================
# MAIN CONTENT AREA
# ============================================================================

# Title
st.markdown(
    '<h1 class="main-title">🧠 Sphota: Cognitive Meaning Engine</h1>',
    unsafe_allow_html=True
)

st.markdown(
    "<p style='text-align: center; color: #666;'>"
    "Advanced intent resolution with contextual disambiguation"
    "</p>",
    unsafe_allow_html=True
)

st.markdown("---")

# Load resources
intent_engine = load_intent_engine()
context_manager = load_context_manager()
intent_db = load_intent_database()

# Build context object from sidebar selections
context_data = build_context_object(location, time_period, social_mode, user_history)

# Input Section
col1, col2 = st.columns([3, 1])

with col1:
    user_input = st.text_area(
        label="Enter Voice Command (Text Simulation)",
        placeholder="Example: 'Show me the bank near here'",
        height=80,
        help="Enter a natural language command or query"
    )

with col2:
    st.markdown("<div style='height: 34px;'></div>", unsafe_allow_html=True)
    process_button = st.button(
        "⚡ Process Intent",
        use_container_width=True,
        key="process_btn"
    )

st.markdown("---")

# Process input if button clicked
if process_button:
    with st.spinner("Processing intent with multi-factor analysis..."):
        winning_intent, analysis, top_3_scores = process_intent(
            user_input,
            context_data,
            intent_engine,
            context_manager,
            intent_db
        )
    
    if winning_intent:
        # ====== RESULT SECTION ======
        st.markdown("### 📊 Resolution Results")
        
        # Winner Box
        st.markdown(
            f'<div class="winner-box"><div class="winner-text">{winning_intent}</div></div>',
            unsafe_allow_html=True
        )
        
        # Metrics Row
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<div class="score-card">', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Base Confidence</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="metric-value">{analysis["base_score"]:.1%}</div>',
                unsafe_allow_html=True
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="score-card">', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Context Boost</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="metric-value">+{(analysis["context_boost"] - analysis["base_score"]):.1%}</div>',
                unsafe_allow_html=True
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="score-card">', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Final Score</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="metric-value">{analysis["context_boost"]:.1%}</div>',
                unsafe_allow_html=True
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Explanation Section
        st.markdown("### 💡 Why This Choice?")
        st.markdown(
            '<div class="explanation-box">',
            unsafe_allow_html=True
        )
        st.markdown(generate_explanation(analysis))
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Score Comparison Chart
        if top_3_scores:
            st.markdown("### 📈 Top 3 Competing Intents")
            
            # Prepare data for chart
            intents_list = [score[0] for score in top_3_scores]
            scores_list = [score[1] for score in top_3_scores]
            
            df_chart = pd.DataFrame({
                "Intent": intents_list,
                "Confidence Score": scores_list,
                "Color": ["#28a745" if i == 0 else "#ffc107" if i == 1 else "#dc3545" for i in range(len(intents_list))]
            })
            
            fig = px.bar(
                df_chart,
                x="Intent",
                y="Confidence Score",
                color="Color",
                color_discrete_map={color: color for color in df_chart["Color"].unique()},
                labels={"Confidence Score": "Score", "Intent": "Intent"},
                title="Comparative Confidence Scores",
                range_y=[0, 1]
            )
            
            fig.update_layout(
                showlegend=False,
                height=400,
                xaxis_title="Intent",
                yaxis_title="Confidence Score",
                hovermode="x unified"
            )
            
            fig.update_traces(textposition="outside", text=[f"{s:.1%}" for s in scores_list])
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Detailed Analysis Table
        with st.expander("📋 Detailed Comparison Table", expanded=False):
            if top_3_scores:
                table_data = {
                    "Intent": [score[0] for score in top_3_scores],
                    "Score": [f"{score[1]:.2%}" for score in top_3_scores],
                    "Status": ["✓ Selected" if i == 0 else "Competing" for i in range(len(top_3_scores))]
                }
                
                df_table = pd.DataFrame(table_data)
                st.dataframe(df_table, use_container_width=True, hide_index=True)
        
        # Context Factors Used
        with st.expander("🎯 Context Factors Applied", expanded=False):
            st.markdown(f"""
            **Current Context:**
            - **Location:** {location}
            - **Time Period:** {time_period}
            - **Social Mode:** {social_mode}
            - **User Background:** {user_history}
            
            These factors were used to adjust the base confidence score through 
            the multi-factor context resolution matrix.
            """)
    
    else:
        st.warning("⚠️ No valid intent could be resolved from your input. Please try a different phrase.")

else:
    # Initial guidance
    st.info(
        "👋 **Getting Started:**\n\n"
        "1. Configure the context factors in the sidebar (Location, Time, etc.)\n"
        "2. Enter a command or query in the text box\n"
        "3. Click 'Process Intent' to see the cognitive analysis\n\n"
        "**Try These Examples:**\n"
        "- 'Show me the bank near here'\n"
        "- 'That's sick!'\n"
        "- 'Turn on the lights'\n"
        "- 'Book a table for tonight'"
    )

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #999; font-size: 12px;'>"
    "Sphota Cognitive Engine v1.0 | "
    "Advanced Intent Resolution with Contextual Disambiguation"
    "</p>",
    unsafe_allow_html=True
)
