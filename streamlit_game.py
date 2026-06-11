import streamlit as st
import json
from google import genai
from google.genai import types

# Set page config
st.set_page_config(
    page_title="🕵️ Murder Mystery Detective",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Fallback data
FALLBACK_DATA = {
    "victim": "Lord Ashton",
    "suspects": {
        "1": {
            "name": "Butler (Arthur)",
            "alibi": "I was polishing silver in the dining room all evening.",
            "clue": "A broken clock in the dining room shows power was cut at 8 PM.",
            "contradiction": "The dining room was pitch black, so he couldn't polish silver!",
            "guilty": False,
        },
        "2": {
            "name": "Maid (Elena)",
            "alibi": "I was locked upstairs in the guest room sleeping soundly.",
            "clue": "Muddy footprints lead from the wet garden straight to her room.",
            "contradiction": "She couldn't be locked inside sleeping if she just walked in from the rain!",
            "guilty": False,
        },
        "3": {
            "name": "Chef (Marcus)",
            "alibi": "I was roasting the grand feast in the kitchen all night.",
            "clue": "The kitchen ovens are completely cold and covered in old dust.",
            "contradiction": "He claims he was roasting food, but the ovens haven't been used in days!",
            "guilty": True,
        },
    },
}

def generate_mystery_with_gemini():
    """Generates unique mystery from Gemini AI."""
    try:
        client = genai.Client
        prompt = """
        Generate a murder mystery game dataset.
        Return ONLY a raw JSON object with NO markdown formatting:
        {
          "victim": "Name of the victim",
          "suspects": {
            "1": {"name": "Suspect Name 1", "alibi": "Alibi 1", "clue": "Physical evidence 1", "contradiction": "Why alibi breaks", "guilty": false},
            "2": {"name": "Suspect Name 2", "alibi": "Alibi 2", "clue": "Physical evidence 2", "contradiction": "Why alibi breaks", "guilty": false},
            "3": {"name": "Suspect Name 3", "alibi": "Alibi 3", "clue": "Physical evidence 3", "contradiction": "Why alibi breaks", "guilty": true}
          }
        }
        Ensure exactly ONE suspect has "guilty": true. Use varied themes (sci-fi, medieval, modern mansion, etc).
        """
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json"),
        )
        
        data = json.loads(response.text)
        return data["victim"], data["suspects"]
    except Exception as e:
        st.warning(f"AI generation failed: {e}. Using fallback data.")
        return FALLBACK_DATA["victim"], FALLBACK_DATA["suspects"]

# Initialize session state
if "game_started" not in st.session_state:
    st.session_state.game_started = False
    st.session_state.victim = None
    st.session_state.suspects = None
    st.session_state.score = 0
    st.session_state.collected_clues = []
    st.session_state.discovered_lies = []
    st.session_state.game_over = False
    st.session_state.result = None

# Custom CSS for detective theme
st.markdown("""
<style>
    .detective-header {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
        padding: 30px;
        border-radius: 10px;
        border-left: 5px solid #ffcc00;
        color: #ffcc00;
        text-align: center;
        margin-bottom: 20px;
    }
    .suspect-card {
        background: linear-gradient(135deg, #2d2d2d 0%, #1a1a1a 100%);
        padding: 20px;
        border-radius: 8px;
        border-left: 4px solid #ff6b6b;
        margin: 10px 0;
        color: white;
    }
    .clue-box {
        background: #1a1a1a;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #4ecdc4;
        margin: 10px 0;
        color: #4ecdc4;
    }
    .score-box {
        background: #1a1a1a;
        padding: 20px;
        border-radius: 8px;
        border: 2px solid #ffcc00;
        text-align: center;
        color: #ffcc00;
        font-size: 20px;
        font-weight: bold;
    }
    .correct-answer {
        background: #1a4d2e;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #2ecc71;
        color: #2ecc71;
    }
    .wrong-answer {
        background: #4d1a1a;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #e74c3c;
        color: #e74c3c;
    }
    body {
        background-color: #0f0f0f;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Main title
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("""
    <div class="detective-header">
        <h1>🕵️ MURDER MYSTERY DETECTIVE 🕵️</h1>
        <p>Uncover the truth. Find the killer. Earn points.</p>
    </div>
    """, unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 🎮 GAME CONTROL")
    
    if st.button("🆕 New Game", use_container_width=True, key="new_game"):
        st.session_state.game_started = True
        with st.spinner("🔮 Generating mystery..."):
            victim, suspects = generate_mystery_with_gemini()
            st.session_state.victim = victim
            st.session_state.suspects = suspects
            st.session_state.score = 0
            st.session_state.collected_clues = []
            st.session_state.discovered_lies = []
            st.session_state.game_over = False
            st.session_state.result = None
        st.rerun()
    
    if st.session_state.game_started:
        st.divider()
        st.markdown("### 📊 DETECTIVE STATS")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="score-box">
                🏆 {st.session_state.score}<br><small>Points</small>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="score-box">
                📝 {len(st.session_state.collected_clues)}<br><small>Clues</small>
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        st.markdown("### 👁️ VICTIM")
        st.info(f"**{st.session_state.victim}** was found dead!")
        
        st.divider()
        st.markdown("### 📓 COLLECTED CLUES")
        if st.session_state.collected_clues:
            for i, clue in enumerate(st.session_state.collected_clues, 1):
                st.markdown(f"""
                <div class="clue-box">
                    <strong>{i}.</strong> {clue}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.caption("No clues collected yet. Start interrogating!")

# Main game area
if not st.session_state.game_started:
    st.info("👈 Click 'New Game' in the sidebar to start your investigation!")
else:
    if not st.session_state.game_over:
        # Tabs for actions
        tab1, tab2, tab3 = st.tabs(["🔍 Interrogate", "🚨 Accuse", "📍 Crime Scene"])
        
        # Interrogation Tab
        with tab1:
            st.markdown("### 🔍 INTERROGATE SUSPECTS")
            st.markdown("Question each suspect and look for contradictions in their alibis.")
            
            suspects = st.session_state.suspects
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("1️⃣ " + suspects["1"]["name"], use_container_width=True, key="suspect1"):
                    st.session_state.current_suspect = "1"
            
            with col2:
                if st.button("2️⃣ " + suspects["2"]["name"], use_container_width=True, key="suspect2"):
                    st.session_state.current_suspect = "2"
            
            with col3:
                if st.button("3️⃣ " + suspects["3"]["name"], use_container_width=True, key="suspect3"):
                    st.session_state.current_suspect = "3"
            
            if "current_suspect" in st.session_state:
                suspect_id = st.session_state.current_suspect
                person = suspects[suspect_id]
                
                st.divider()
                st.markdown(f"""
                <div class="suspect-card">
                    <h3>👤 {person['name']}</h3>
                    <p><strong>Detective:</strong> "Where were you at the time of the murder?"</p>
                    <p><strong>{person['name']}:</strong> "{person['alibi']}"</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Add clue to notebook
                if person["clue"] not in st.session_state.collected_clues:
                    st.session_state.collected_clues.append(person["clue"])
                
                st.markdown("### 🔎 EVIDENCE ANALYSIS")
                st.warning(f"**Evidence Found:** {person['clue']}")
                
                st.markdown("### ❓ Does this match their alibi?")
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("✅ Yes, story seems solid", use_container_width=True, key=f"accept_{suspect_id}"):
                        st.success("You accept their statement for now.")
                
                with col2:
                    if st.button("❌ Wait! They're lying!", use_container_width=True, key=f"accuse_{suspect_id}"):
                        if suspect_id not in st.session_state.discovered_lies:
                            st.session_state.discovered_lies.append(suspect_id)
                            st.session_state.score += 50
                            st.markdown(f"""
                            <div class="correct-answer">
                                <h4>💡 EXCELLENT DEDUCTION!</h4>
                                <p>{person['contradiction']}</p>
                                <p>🏆 +50 Detective Points!</p>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.info("You already exposed this lie.")
        
        # Crime Scene Investigation Tab
        with tab2:
            st.markdown("### 🚨 ACCUSATION")
            st.markdown("Based on your investigation, who is the murderer?")
            
            suspects = st.session_state.suspects
            st.divider()
            
            cols = st.columns(3)
            suspects_list = [("1", suspects["1"]["name"], cols[0]),
                            ("2", suspects["2"]["name"], cols[1]),
                            ("3", suspects["3"]["name"], cols[2])]
            
            for suspect_id, suspect_name, col in suspects_list:
                with col:
                    if st.button(f"⚖️ ACCUSE\n{suspect_name}", use_container_width=True, key=f"final_accuse_{suspect_id}"):
                        st.session_state.game_over = True
                        st.session_state.accused_id = suspect_id
                        st.rerun()
        
        # Third tab (placeholder)
        with tab3:
            st.markdown("### 📍 CRIME SCENE")
            st.info("🔍 Interrogate suspects to gather clues from the crime scene.")
            st.markdown("""
            Each suspect you interrogate will reveal clues found at the scene. 
            The physical evidence never lies - use it to catch contradictions in their alibis!
            """)
    
    # Game Over Screen
    if st.session_state.game_over:
        accused_id = st.session_state.accused_id
        person = st.session_state.suspects[accused_id]
        
        st.divider()
        
        if st.session_state.suspects[accused_id]["guilty"]:
            st.markdown(f"""
            <div class="correct-answer">
                <h1>🎉 CORRECT!</h1>
                <h2>{person['name']} is the killer!</h2>
                <p>Your deductions were flawless!</p>
                <p>🏆 +100 Bonus Points!</p>
            </div>
            """, unsafe_allow_html=True)
            st.session_state.score += 100
        else:
            st.markdown(f"""
            <div class="wrong-answer">
                <h1>❌ WRONG!</h1>
                <h2>You accused {person['name']}.</h2>
                <p>The real killer escaped! 💀</p>
                <p>-50 Penalty Points</p>
            </div>
            """, unsafe_allow_html=True)
            st.session_state.score = max(0, st.session_state.score - 50)
        
        st.divider()
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            final_score = st.markdown(f"""
            <div class="score-box">
                Final Score: {st.session_state.score} Points
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        col1, col2, col3 = st.columns(3)
        with col2:
            if st.button("🆕 Play Another Case", use_container_width=True):
                st.session_state.game_started = False
                st.session_state.game_over = False
                st.rerun()
                
