import requests
import os
import random
import streamlit as st
from pprint import  pprint

# Define the base URI of the API
#   - Potential sources are in `.streamlit/secrets.toml` or in the Secrets section
#     on Streamlit Cloud
#   - The source selected is based on the shell variable passend when launching streamlit
#    (shortcuts are included in Makefile). By default it takes the cloud API url

if 'BASE_URI' in os.environ:
    BASE_URI = os.environ.get('BASE_URI')
else:
    BASE_URI = st.secrets['cloud_api_uri']
# Add a '/' at the end if it's not there
BASE_URI = BASE_URI if BASE_URI.endswith('/') else BASE_URI + '/'
# Define the url to be used by requests.get to get a prediction (adapt if needed)
url_base = BASE_URI + 'predict'

#Page setup
st.set_page_config(page_title="MarathonIQ", layout="wide")

with open('.streamlit/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Just displaying the source for the API. Remove this in your final version.

#st.markdown(f"Working with {url_base}")

#st.markdown("Now, the rest is up to you. Start creating your page.")

# ============================================================
# PAGE SETUP
# ============================================================

st.markdown("""
    <div style="
        background: transparent;
        padding: 1rem 0 0.5rem 0;
        margin: 0;
        text-align: center;
    ">
        <h1 style="color: black; margin-bottom: 0.5rem;">
            🏃 MarathonIQ 🏃
        </h1>
        <p style="color: black; font-size: 1.2rem;">
            Enter your training data. Get your predicted finish time.
        </p>
    </div>
""", unsafe_allow_html=True)
st.markdown("---")

# ============================================================
# SECTION 1 — USER INPUTS
# ============================================================

st.header("Your Profile")
level = st.radio("", ["🌞 First Marathon", "🏆 Already Ran a Marathon"], horizontal=True)

if level == "🌞 First Marathon":
    url = url_base + '/general'
    # --- MUST HAVE ---
    st.subheader("Tell us about your training")
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("Age", 18, 100, 35)
        running_experience_months = st.number_input("Running Experience (months)", 0, 240, 0)
        weekly_mileage_km = st.number_input("Weekly Mileage (km/week)", 0, 200, 0)

    with col2:
        injury_count = st.number_input("Injuries this training cycle", 0, 10, 0)
        injury_severity = st.selectbox(
            "Injury Severity",
            options=[0, 1, 2, 3],
            format_func=lambda x: {0: "None", 1: "Minor",
                                    2: "Moderate", 3: "Severe"}[x]
        )
        course_difficulty = st.selectbox(
            "Course Difficulty",
            options=[1, 2, 3],
            format_func=lambda x: {1: "Flat", 2: "Mixed", 3: "Hilly"}[x]
        )

    # --- NICE TO HAVE ---
    with st.expander("➕ Improve your prediction (optional)"):
        st.caption("Optional inputs — if not provided, values will be automatically set to 0 or to the median of our dataset.")

        col3, col4 = st.columns(2)

        with col3:
            vo2_max = st.number_input("VO2 Max", 30, 85, 45)
            resting_heart_rate = st.number_input("Resting Heart Rate (bpm)", 30, 100, 68)
            previous_marathon_count = st.number_input("Previous Marathons", 0, 100, 0)

        with col4:
            recovery_score = st.selectbox(
                "Recovery Score - Body Battery - Readiness Score - Nightly Recharge",
                options=[0, 3, 6, 7, 9],
                format_func=lambda x: {0: "I don't track this",
                                       3: "Low — fatigued, body clearly needs rest",
                                       6: "Moderate — somewhat tired, lighter day advised",
                                       7: "Good — well rested, moderate effort is fine",
                                       9: "High — fully recovered, ready to push hard"}[x]
            )

            run_club_attendance = st.selectbox(
                "Run Club Attendance",
                options=[12, 37, 62, 87],
                format_func=lambda x: {12: "Never",
                                       37: "Rarely — once a month or less",
                                       62: "Sometimes — a few times a month",
                                       87: "Often — weekly or more"}[x]
            )
            marathon_weather = st.selectbox(
                "Race Day Weather",
                options=["Neutral", "Cold", "Hot", "Rainy", "Windy"]
            )

    # Build feature vector
    feature_vector = {
        'age':                        age,
        'running_experience_months':  running_experience_months,
        'weekly_mileage_km':          weekly_mileage_km,
        'injury_count':               injury_count,
        'injury_severity':            injury_severity,
        'course_difficulty':          course_difficulty,
        'vo2_max':                    vo2_max,
        'resting_heart_rate_bpm':     resting_heart_rate,
        'recovery_score':             recovery_score,
        'previous_marathon_count':    previous_marathon_count,
        'run_club_attendance_rate':   run_club_attendance,
        'marathon_weather_Cold':      1 if marathon_weather == 'Cold'  else 0,
        'marathon_weather_Hot':       1 if marathon_weather == 'Hot'   else 0,
        'marathon_weather_Rainy':     1 if marathon_weather == 'Rainy' else 0,
        'marathon_weather_Windy':     1 if marathon_weather == 'Windy' else 0,
    }

    #response = requests.get(url, params=feature_vector)

# ============================================================
# DOING THE SAME FOR THE EXPERT MODEL
# ============================================================

else:
    url = url_base + '/expert'
    # --- MUST HAVE ---
    st.subheader("Tell us about your training")
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("Age", 18, 100, 35)
        running_experience_months = st.number_input("Running Experience (months)", 0, 240, 0)
        weekly_mileage_km = st.number_input("Weekly Mileage (km/week)", 0, 200, 0)
        personal_best = st.text_input("Personal Best (HH:MM:SS)", value="00:00:00", max_chars=8)
        st.caption("ex: 03:45:30")
        if personal_best and len(personal_best) == 8:
            parts = personal_best.split(":")
            personal_best_minutes = int(parts[0]) * 60 + int(parts[1]) + round(int(parts[2]) / 60)
        else:
            personal_best_minutes = None

    with col2:
        injury_count = st.number_input("Injuries this training cycle", 0, 10, 0)
        injury_severity = st.selectbox(
            "Injury Severity",
            options=[0, 1, 2, 3],
            format_func=lambda x: {0: "None", 1: "Minor",
                                    2: "Moderate", 3: "Severe"}[x]
        )
        course_difficulty = st.selectbox(
            "Course Difficulty",
            options=[1, 2, 3],
            format_func=lambda x: {1: "Flat", 2: "Mixed", 3: "Hilly"}[x]
        )

    # --- NICE TO HAVE ---
    with st.expander("➕ Improve your prediction (optional)"):
        st.caption("Optional inputs — if not provided, values will be automatically set to 0 or to the median of our dataset.")

        col3, col4 = st.columns(2)

        with col3:
            vo2_max = st.number_input("VO2 Max", 30, 85, 45)
            resting_heart_rate = st.number_input("Resting Heart Rate (bpm)", 30, 100, 68)
            previous_marathon_count = st.number_input("Previous Marathons", 0, 100, 0)

        with col4:
            recovery_score = st.selectbox(
                "Recovery Score - Body Battery - Readiness Score - Nightly Recharge",
                options=[0, 3, 6, 7, 9],
                format_func=lambda x: {0: "I don't track this",
                                       3: "Low — fatigued, body clearly needs rest",
                                       6: "Moderate — somewhat tired, lighter day advised",
                                       7: "Good — well rested, moderate effort is fine",
                                       9: "High — fully recovered, ready to push hard"}[x]
            )
            run_club_attendance = st.selectbox(
                "Run Club Attendance",
                options=[12, 37, 62, 87],
                format_func=lambda x: {12: "Never",
                                       37: "Rarely — once a month or less",
                                       62: "Sometimes — a few times a month",
                                       87: "Often — weekly or more"}[x]
            )
            marathon_weather = st.selectbox(
                "Race Day Weather",
                options=["Neutral", "Cold", "Hot", "Rainy", "Windy"]
            )


    # Build feature vector
    feature_vector = {
        'age':                        age,
        'running_experience_months':  running_experience_months,
        'weekly_mileage_km':          weekly_mileage_km,
        'personal_best_minutes':      personal_best_minutes,
        'injury_count':               injury_count,
        'injury_severity':            injury_severity,
        'course_difficulty':          course_difficulty,
        'vo2_max':                    vo2_max,
        'resting_heart_rate_bpm':     resting_heart_rate,
        'recovery_score':             recovery_score,
        'previous_marathon_count':    previous_marathon_count,
        'run_club_attendance_rate':   run_club_attendance,
        'marathon_weather_Cold':      1 if marathon_weather == 'Cold'  else 0,
        'marathon_weather_Hot':       1 if marathon_weather == 'Hot'   else 0,
        'marathon_weather_Rainy':     1 if marathon_weather == 'Rainy' else 0,
        'marathon_weather_Windy':     1 if marathon_weather == 'Windy' else 0,
    }

    #response = requests.get(url, params=feature_vector)

# ============================================================
# SECTION 3 — API CALL + PREDICTION
# ============================================================

missing_fields = []

if age == 0:
    missing_fields.append("Age")
if running_experience_months == 0:
    missing_fields.append("Running Experience")
if level == "🏆 Already Ran a Marathon":
    if personal_best_minutes is None or personal_best_minutes == 0:
        missing_fields.append("Personal Best")
if weekly_mileage_km < 10:
    missing_fields.append("Weekly Mileage (minimum 10km/week)")

if st.button("🏁 Predict My Finish Time"):

    if missing_fields:
        st.warning(f"⚠️ Please complete: {', '.join(missing_fields)}")

    else:
        with st.spinner("Crunching your training data..."):
            #st.write(feature_vector)
            response = requests.post(url, json=feature_vector)

        if response.status_code == 200:
            result = response.json()
            prediction = result.get("predicted_finish_time", None)

            if prediction is not None:

                hours = int(prediction // 60)
                minutes = int(prediction % 60)

                pace = prediction / 42.195

                pace_min = int(pace)
                pace_sec = int(round((pace - pace_min) * 60))

                if pace_sec == 60:
                    pace_min += 1
                    pace_sec = 0

                st.markdown("---")
                st.metric(
                    label="Predicted Finish Time",
                    value=f"{hours}h {minutes:02d}min ➡️ {pace_min}:{pace_sec:02d} min/km"
                )
                st.caption("Typical variance: +/- 15-20 min")
                st.caption("Based on a synthetic dataset of 80,000 runners.")

                st.info("📊 Feature breakdown — coming soon")

                gif = random.choice([
                    "media/forest.gif",
                    "media/rocket.gif",
                    "media/wonderwoman.gif"
                ])
                st.image(gif)

        else:
            st.error(f"API error: {response.status_code}")

        #with st.expander("🔍 Debug — Feature Vector"):
            #st.json(feature_vector)
else:
    st.info("Fill in your stats above to see your prediction!")
