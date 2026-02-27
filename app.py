import streamlit as st
import requests
from datetime import date

# ==============================
# BASIC CONFIG & STYLING
# ==============================
st.set_page_config(
    page_title="Jowar Harvest & Price Predictor",
    page_icon="🌾",
    layout="wide",
)

# Custom CSS for nicer look
st.markdown(
    """
    <style>
    .main {
        background: #f5f7fb;
    }
    .big-title {
        font-size: 32px !important;
        font-weight: 700 !important;
        color: #14365d;
    }
    .sub-title {
        font-size: 16px !important;
        color: #4a4a4a;
    }
    .card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 18px 22px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        margin-bottom: 12px;
    }
    .metric-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 12px 16px;
        box-shadow: 0 1px 6px rgba(0,0,0,0.06);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

BASE_URL = "http://127.0.0.1:8000"

# ==============================
# HEADER
# ==============================
st.markdown('<div class="big-title">🌾 Jowar Crop Harvest & Price Prediction</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">AI-powered system using real-time weather & market data to help farmers plan harvest and pricing decisions.</div>',
    unsafe_allow_html=True,
)
st.write("")

# ==============================
# LAYOUT: LEFT (Inputs) / RIGHT (Results)
# ==============================
left_col, right_col = st.columns([1.1, 1])

with left_col:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📥 Input Details")

    # Use a form so values only submit when button pressed
    with st.form("prediction_form"):
        sowing_date = st.date_input("Sowing Date", value=date.today())
        lat = st.number_input("Latitude", value=17.385, format="%.4f")
        lon = st.number_input("Longitude", value=78.486, format="%.4f")

        state = st.text_input("State", value="Karnataka")
        market = st.text_input("Market (Mandi)", value="Gulbarga")

        st.caption("ℹ️ Tip: Use valid State & Market names present in AGMARKNET data for best results.")

        submit_btn = st.form_submit_button("🔮 Predict Harvest & Price")

    st.markdown('</div>', unsafe_allow_html=True)

with right_col:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📊 Prediction Results")

    if submit_btn:
        payload = {
            "sowing_date": str(sowing_date),
            "lat": float(lat),
            "lon": float(lon),
            "state": state.strip(),
            "market": market.strip(),
        }

        with st.spinner("Running AI models and fetching live data… Please wait ⏳"):
            try:
                resp = requests.post(f"{BASE_URL}/predict-all", json=payload, timeout=40)
            except requests.exceptions.RequestException:
                st.error("❌ Could not connect to backend API. Make sure FastAPI (`main.py`) is running.")
            else:
                if resp.status_code != 200:
                    st.error(f"❌ Backend error: {resp.status_code}")
                    st.json(resp.text)
                else:
                    result = resp.json()
                    if "error" in result:
                        st.error(result["error"])
                        if "details" in result:
                            st.caption(result["details"])
                    else:
                        # Top metrics row
                        m1, m2, m3 = st.columns(3)
                        m1.markdown('<div class="metric-card">', unsafe_allow_html=True)
                        m1.metric("Harvest Date", result["harvest_date"], help="Predicted harvest completion date")
                        m1.markdown('</div>', unsafe_allow_html=True)

                        m2.markdown('<div class="metric-card">', unsafe_allow_html=True)
                        m2.metric("Predicted Price (₹/quintal)", result["predicted_price"])
                        m2.markdown('</div>', unsafe_allow_html=True)

                        m3.markdown('<div class="metric-card">', unsafe_allow_html=True)
                        m3.metric("Market", f"{result['market']}, {result['state']}")
                        m3.markdown('</div>', unsafe_allow_html=True)

                        st.write("")
                        st.markdown("### 📈 Price Context (Lag Values)")
                        c1, c2 = st.columns(2)
                        with c1:
                            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                            st.metric("Lag 3 Price (₹)", result.get("lag_3_price", "N/A"))
                            st.markdown('</div>', unsafe_allow_html=True)
                        with c2:
                            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                            st.metric("Lag 7 Price (₹)", result.get("lag_7_price", "N/A"))
                            st.markdown('</div>', unsafe_allow_html=True)

                        st.write("")
                        st.success("✅ Prediction completed successfully!")

                        st.markdown("#### 🔍 Summary")
                        st.write(
                            f"- **Sowing Date:** {result['sowing_date']}\n"
                            f"- **Estimated Harvest Date:** {result['harvest_date']}\n"
                            f"- **Predicted Jowar Price:** ₹ {result['predicted_price']} per quintal\n"
                            f"- **Market:** {result['market']} ({result['state']})"
                        )
    else:
        st.info("Fill in the details on the left and click **'🔮 Predict Harvest & Price'** to see results here.")

    st.markdown('</div>', unsafe_allow_html=True)

# ==============================
# FOOTER
# ==============================
st.write("")
st.markdown(
    "<center>🧪 Major Project – Dayananda Sagar Academy of Technology and Management</center>",
    unsafe_allow_html=True,
)
