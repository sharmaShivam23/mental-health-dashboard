import streamlit as st
import pandas as pd
import plotly.express as px
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from utils.analysis import (
    compute_full_analysis,
    process_dataframe,
    validate_teacher_csv,
    compute_class_health_score,
    generate_class_recommendations,
    generate_auto_insights,
    get_sample_csv,
    LIVE_FILE_COLUMNS,
)

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Student Mental Health Analytics",
    layout="wide",
    page_icon="🎓",
)

LIVE_FILE = "live_student_data.csv"

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------
@st.cache_data
def load_primary_data():
    try:
        df = pd.read_csv("student_data.csv")
        numeric_cols = [
            "cgpa", "daily_study_hours", "daily_sleep_hours",
            "anxiety_score", "depression_score", "screen_time_hours",
            "academic_pressure_score",
        ]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        return df
    except FileNotFoundError:
        return None


def ensure_live_file():
    if not os.path.exists(LIVE_FILE):
        pd.DataFrame(columns=LIVE_FILE_COLUMNS).to_csv(LIVE_FILE, index=False)


def level_color(level):
    return {"Low": "✅ Low", "Medium": "⚠️ Medium", "High": "🚨 High"}.get(level, level)


# ---------------------------------------------------------------------------
# SIDEBAR NAVIGATION
# ---------------------------------------------------------------------------
st.sidebar.title("🎓 Navigation")
page = st.sidebar.radio("Go to:", [
    "📊 1. Pre-built Dashboard",
    "📝 2. Personal Wellness Tracker",
    "👩‍🏫 3. Teacher Dashboard",
    "📁 4. Custom Data Uploader",
])
st.sidebar.divider()
st.sidebar.info("Developed for Data Analysis Lab 💻")


# ===========================================================================
# PAGE 1 — PRE-BUILT DASHBOARD
# ===========================================================================
if page == "📊 1. Pre-built Dashboard":
    st.title("📊 Main Student Dashboard")
    st.write("Comprehensive analysis of our primary student mental health dataset.")

    df_static = load_primary_data()

    if df_static is None:
        st.error("🚨 'student_data.csv' not found in the working directory.")
        st.stop()

    # Individual lookup
    st.subheader("🔍 Individual Student Lookup")
    search_id = st.text_input("Enter Student ID (e.g., 100001):")
    if search_id:
        try:
            rec = df_static[df_static["student_id"].astype(str) == str(search_id)]
            if not rec.empty:
                st.success(f"Record found for Student ID: {search_id}")
                st.dataframe(rec)
            else:
                st.warning("Student ID not found.")
        except KeyError:
            st.error("Dataset does not contain a 'student_id' column.")

    st.divider()

    # Sidebar filters
    st.sidebar.subheader("🎯 Filter Dashboard Data")
    years = df_static["year"].dropna().unique()
    selected_years = st.sidebar.multiselect("Year of Study:", years, default=years)
    genders = df_static["gender"].dropna().unique()
    selected_genders = st.sidebar.multiselect("Gender:", genders, default=genders)

    fdf = df_static[
        df_static["year"].isin(selected_years) & df_static["gender"].isin(selected_genders)
    ]

    if fdf.empty:
        st.warning("No data for selected filters.")
        st.stop()

    # Scorecards
    st.subheader("📌 Filtered Class Averages")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Students", len(fdf))
    c2.metric("Avg CGPA", round(fdf["cgpa"].mean(), 2))
    c3.metric("Avg Study Hrs", round(fdf["daily_study_hours"].mean(), 1))
    c4.metric("Avg Sleep Hrs", round(fdf["daily_sleep_hours"].mean(), 1))

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Avg Anxiety", round(fdf["anxiety_score"].mean(), 1))
    c6.metric("Avg Depression", round(fdf["depression_score"].mean(), 1))
    c7.metric("Avg Academic Pressure", round(fdf["academic_pressure_score"].mean(), 1))
    c8.metric("Avg Screen Time", round(fdf["screen_time_hours"].mean(), 1))

    st.divider()

    # Charts
    st.subheader("📈 Visual Analytics")

    cl1, cr1 = st.columns(2)
    with cl1:
        fig1 = px.histogram(
            fdf, x="gender", y="anxiety_score", color="gender",
            title="1. Average Anxiety by Gender", histfunc="avg", text_auto=".1f",
        )
        st.plotly_chart(fig1, use_container_width=True)
    with cr1:
        fig2 = px.scatter(
            fdf, x="daily_study_hours", y="cgpa", color="stress_level",
            title="2. Study Hours vs. CGPA (by Stress)",
            category_orders={"stress_level": ["Low", "Medium", "High"]},
        )
        st.plotly_chart(fig2, use_container_width=True)

    cl2, cr2 = st.columns(2)
    with cl2:
        fig3 = px.box(
            fdf, x="year", y="depression_score", color="year",
            title="3. Depression Scores by Year",
            category_orders={"year": ["1st", "2nd", "3rd", "4th"]},
        )
        st.plotly_chart(fig3, use_container_width=True)
    with cr2:
        s_df = fdf.dropna(subset=["sleep_quality", "anxiety_score"])
        s_avg = s_df.groupby("sleep_quality")["anxiety_score"].mean().reset_index()
        fig4 = px.bar(
            s_avg, x="sleep_quality", y="anxiety_score", color="sleep_quality",
            title="4. Sleep Quality vs. Avg Anxiety",
            category_orders={"sleep_quality": ["Poor", "Average", "Good"]},
        )
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown("#### 5. Academic Pressure vs. Stress Level Heatmap")
    hdf = fdf.dropna(subset=["academic_pressure_score", "stress_level"])
    fig5 = px.density_heatmap(
        hdf, x="academic_pressure_score", y="stress_level",
        title="Academic Pressure vs. Stress",
        category_orders={"stress_level": ["Low", "Medium", "High"]},
        color_continuous_scale="Blues",
    )
    st.plotly_chart(fig5, use_container_width=True)

    st.divider()
    st.subheader("📥 Export")
    st.download_button(
        "Download Filtered CSV",
        data=fdf.to_csv(index=False).encode("utf-8"),
        file_name="filtered_student_data.csv",
        mime="text/csv",
    )


# ===========================================================================
# PAGE 2 — PERSONAL WELLNESS TRACKER
# ===========================================================================
elif page == "📝 2. Personal Wellness Tracker":
    st.title("📝 Personal Wellness Tracker")
    st.write("Complete the form to receive a personalised stress analysis. Your entry is saved to the live database.")

    ensure_live_file()

    with st.form("wellness_form"):
        st.subheader("👤 Student Identity")
        id_c1, id_c2 = st.columns(2)
        student_name = id_c1.text_input("Full Name")
        student_id   = id_c2.text_input("College / Student ID")

        st.subheader("📚 Academic Factors")
        ac1, ac2, ac3 = st.columns(3)
        study_hours    = ac1.number_input("Daily Study Hours", 0.0, 24.0, 4.0, 0.5)
        assign_load    = ac2.slider("Assignment Load (1–10)", 1, 10, 5)
        acad_pressure  = ac3.slider("Academic Pressure (1–10)", 1, 10, 5)

        st.subheader("🌙 Lifestyle Factors")
        lc1, lc2, lc3, lc4 = st.columns(4)
        sleep_hours    = lc1.number_input("Daily Sleep Hours", 0.0, 24.0, 7.0, 0.5)
        activity_hours = lc2.number_input("Physical Activity (hrs/day)", 0.0, 10.0, 1.0, 0.25)
        diet_quality   = lc3.slider("Diet Quality (1–10)", 1, 10, 6)
        screen_time    = lc4.number_input("Screen Time (hrs/day)", 0.0, 24.0, 3.0, 0.5)

        st.subheader("🌃 Behavioral & Social Factors")
        bc1, bc2, bc3, bc4, bc5 = st.columns(5)
        late_night     = bc1.number_input("Late Night Usage (hrs past midnight)", 0.0, 8.0, 0.0, 0.5)
        social_support = bc2.slider("Social Support (1–10)", 1, 10, 6)
        loneliness     = bc3.slider("Loneliness Level (1–10)", 1, 10, 4)
        self_esteem    = bc4.slider("Self-Esteem (1–10)", 1, 10, 6)
        motivation     = bc5.slider("Motivation Level (1–10)", 1, 10, 6)

        st.subheader("🗂️ Demographics")
        dc1, dc2, dc3 = st.columns(3)
        gender = dc1.selectbox("Gender", ["Male", "Female", "Other"])
        year   = dc2.selectbox("Year of Study", ["1st", "2nd", "3rd", "4th"])

        submitted = st.form_submit_button("🔍 Analyse My Wellness")

    is_valid = False
    report_content = ""

    if submitted:
        if not student_name or not student_id:
            st.error("Please enter both Name and Student ID.")
        else:
            is_valid = True
            form_data = {
                "daily_study_hours":       study_hours,
                "assignment_load":         assign_load,
                "academic_pressure_score": acad_pressure,
                "daily_sleep_hours":       sleep_hours,
                "physical_activity_hours": activity_hours,
                "diet_quality":            diet_quality,
                "screen_time_hours":       screen_time,
                "late_night_usage":        late_night,
                "social_support":          social_support,
                "loneliness_level":        loneliness,
                "self_esteem":             self_esteem,
                "motivation_level":        motivation,
            }

            result = compute_full_analysis(form_data)
            stress_score = result["stress_score"]
            stress_level = result["stress_level"]
            contributors = result["contributors"]
            recs         = result["recommendations"]

            st.divider()
            st.markdown(f"### 🎯 Personalised Diagnostic for **{student_name}**")

            # Progress bar
            st.write("#### Overall Stress Score")
            st.progress(stress_score / 100.0)
            if stress_level == "Low":
                st.success(f"**Score: {stress_score}/100 — Low Stress.** Great balance!")
            elif stress_level == "Medium":
                st.warning(f"**Score: {stress_score}/100 — Medium Stress.** Some areas need attention.")
            else:
                st.error(f"**Score: {stress_score}/100 — High Stress.** Immediate self-care recommended.")

            st.write("")

            # Metrics row
            m1, m2, m3, m4 = st.columns(4)
            sleep_deficit = max(0, 8.0 - sleep_hours)
            m1.metric("Stress Score", f"{stress_score}/100")
            m2.metric("Stress Level", level_color(stress_level))
            m3.metric("Sleep Deficit", f"{sleep_deficit:.1f} hrs/day",
                      delta_color="inverse" if sleep_deficit > 0 else "normal")
            study_sleep_ratio = round(study_hours / sleep_hours, 2) if sleep_hours > 0 else "N/A"
            m4.metric("Study:Sleep Ratio", f"{study_sleep_ratio}x",
                      help="Above 1.0 = studying more than sleeping.")

            st.write("")

            # Contributors
            st.write("#### ⚠️ Stress Contributors")
            for c in contributors:
                st.warning(c)

            st.write("")

            # Recommendations
            st.write("#### 💡 Personalised Recommendations")
            for r in recs:
                st.info(r)

            st.write("")

            # Peer comparison
            df_static = load_primary_data()
            if df_static is not None:
                st.write("#### 📈 Peer Comparison")
                peer_study = round(df_static[df_static["year"] == year]["daily_study_hours"].mean(), 1)
                peer_sleep = round(df_static[df_static["year"] == year]["daily_sleep_hours"].mean(), 1)
                st.info(f"💡 You study **{study_hours} hrs/day** vs. {year}-year peer avg of **{peer_study} hrs**.")
                st.info(f"💡 You sleep **{sleep_hours} hrs/day** vs. {year}-year peer avg of **{peer_sleep} hrs**.")

            st.write("")

            # Raw entry preview
            st.markdown("#### 📋 Your Database Entry")
            preview_df = pd.DataFrame([{
                "Name": student_name, "ID": student_id, "Gender": gender, "Year": year,
                "Study Hrs": study_hours, "Sleep Hrs": sleep_hours,
                "Stress Score": stress_score, "Stress Level": stress_level,
            }])
            st.dataframe(preview_df)

            # Persist to CSV
            new_entry = pd.DataFrame([{
                "Student_Name": student_name, "Student_ID": student_id,
                "Gender": gender, "Year": year,
                "Study_Hours": study_hours, "Sleep_Hours": sleep_hours,
                "Screen_Time": screen_time, "Assignment_Load": assign_load,
                "Physical_Activity": activity_hours, "Diet_Quality": diet_quality,
                "Social_Support": social_support, "Loneliness_Level": loneliness,
                "Self_Esteem": self_esteem, "Motivation_Level": motivation,
                "Late_Night_Usage": late_night,
                "Stress_Score": stress_score, "Stress_Level": stress_level,
            }])
            new_entry.to_csv(LIVE_FILE, mode="a", header=False, index=False)

            # Report text
            report_content = f"""--- OFFICIAL WELLNESS DIAGNOSTIC REPORT ---
Name: {student_name}  |  ID: {student_id}
Year: {year}  |  Gender: {gender}

--- ACADEMIC ---
Daily Study Hours: {study_hours}
Assignment Load: {assign_load}/10
Academic Pressure: {acad_pressure}/10

--- LIFESTYLE ---
Daily Sleep Hours: {sleep_hours}
Physical Activity: {activity_hours} hrs/day
Diet Quality: {diet_quality}/10
Screen Time: {screen_time} hrs/day
Late Night Usage: {late_night} hrs past midnight

--- SOCIAL & PSYCHOLOGICAL ---
Social Support: {social_support}/10
Loneliness: {loneliness}/10
Self-Esteem: {self_esteem}/10
Motivation: {motivation}/10

--- RESULTS ---
Stress Score: {stress_score}/100
Stress Level: {stress_level}
Sleep Deficit: {sleep_deficit:.1f} hrs/day
Study:Sleep Ratio: {study_sleep_ratio}x

--- CONTRIBUTORS ---
{chr(10).join(contributors)}

--- RECOMMENDATIONS ---
{chr(10).join(recs)}

Generated by the AKGEC Student Analytics System.
"""

    # Live database section
    st.divider()
    st.subheader("📊 Live Database Trends")
    try:
        df_live = pd.read_csv(LIVE_FILE)
        if len(df_live) > 0:
            if is_valid:
                st.success("Assessment complete! Download your report below:")
                st.download_button(
                    "📥 Download My Official Report",
                    data=report_content,
                    file_name=f"{student_id}_Wellness_Report.txt",
                    mime="text/plain",
                )
                st.write("")

            st.markdown("#### 📖 Full Student Health Directory")
            st.dataframe(df_live)
            st.write("")

            st.markdown("#### 🍩 Class Stress Level Distribution")
            if "Stress_Level" in df_live.columns:
                fig_pie = px.pie(df_live, names="Stress_Level",
                                 title="Live Stress Level Distribution",
                                 color="Stress_Level",
                                 color_discrete_map={"Low": "#2ecc71", "Medium": "#f39c12", "High": "#e74c3c"})
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("Stress data will appear after entries are submitted.")
        else:
            st.info("Submit the first entry above to generate live trends.")
    except Exception as e:
        st.error(f"Could not load live database: {e}")


# ===========================================================================
# PAGE 3 — TEACHER DASHBOARD
# ===========================================================================
elif page == "👩‍🏫 3. Teacher Dashboard":
    st.title("👩‍🏫 Teacher Dashboard")
    st.write("Upload your class roster CSV to get a comprehensive mental health analysis for your students.")

    # Step 1 — Sample CSV
    st.subheader("📥 Step 1: Download Sample CSV Template")
    st.write("Use this template to prepare your class data with the required columns.")
    st.download_button(
        "⬇️ Download Sample CSV",
        data=get_sample_csv(),
        file_name="sample_class_data.csv",
        mime="text/csv",
    )

    st.divider()

    # Step 2 — Upload
    st.subheader("📤 Step 2: Upload Your Class CSV")
    uploaded = st.file_uploader("Upload CSV", type=["csv"], key="teacher_upload")

    if uploaded is None:
        st.info("Awaiting CSV upload…")
        st.stop()

    df_raw = pd.read_csv(uploaded)
    st.success(f"File uploaded: **{uploaded.name}** ({len(df_raw)} rows)")

    # Step 3 — Validation
    st.subheader("✅ Step 3: Validation")
    missing = validate_teacher_csv(df_raw)
    if missing:
        st.error(f"Missing required columns: `{'`, `'.join(missing)}`")
        st.write("Please add the missing columns and re-upload.")
        st.stop()
    st.success("All required columns present. Processing data…")

    # Step 4 — Process
    df_proc = process_dataframe(df_raw)

    # Step 5 — Dashboard
    st.divider()
    st.subheader("📊 Step 4: Class Overview")

    ov1, ov2, ov3, ov4 = st.columns(4)
    ov1.metric("Total Students", len(df_proc))
    ov2.metric("Avg Stress Score", round(df_proc["stress_score"].mean(), 1))
    ov3.metric("Avg Sleep (hrs)", round(df_proc["daily_sleep_hours"].mean(), 1))
    ov4.metric("Avg Study (hrs)", round(df_proc["daily_study_hours"].mean(), 1))

    st.write("")

    # Auto insights
    st.subheader("🔔 Auto Insights")
    for insight in generate_auto_insights(df_proc):
        if insight.startswith("✅"):
            st.success(insight)
        elif insight.startswith("🚨"):
            st.error(insight)
        else:
            st.warning(insight)

    st.divider()

    # Class-wise analysis
    st.subheader("📚 Class-wise Analysis")
    year_order = ["1st", "2nd", "3rd", "4th"]
    years_present = [y for y in year_order if y in df_proc["year"].values]

    for yr in years_present:
        grp = df_proc[df_proc["year"] == yr]
        health = compute_class_health_score(grp)
        level_counts = grp["stress_level"].value_counts().to_dict()
        high_n = level_counts.get("High", 0)

        with st.expander(f"📖 {yr} Year — {len(grp)} students | Health Score: {health}/100 | High Risk: {high_n}"):
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Avg Stress Score", round(grp["stress_score"].mean(), 1))
            c2.metric("Avg Sleep (hrs)", round(grp["daily_sleep_hours"].mean(), 1))
            c3.metric("Avg Study (hrs)", round(grp["daily_study_hours"].mean(), 1))
            c4.metric("Avg Physical Activity", round(grp["physical_activity_hours"].mean(), 2))

            st.markdown("**Class Recommendations:**")
            for rec in generate_class_recommendations(grp):
                if rec.startswith("✅"):
                    st.success(rec)
                else:
                    st.warning(rec)

    st.divider()

    # High-risk students
    st.subheader("🚨 High-Risk Students")
    high_risk_df = df_proc[df_proc["stress_level"] == "High"]
    if high_risk_df.empty:
        st.success("No high-risk students detected.")
    else:
        st.error(f"{len(high_risk_df)} student(s) flagged as HIGH stress.")
        cols_to_show = ["student_id", "name", "year", "stress_score", "daily_sleep_hours",
                        "daily_study_hours", "recommendation"]
        show_cols = [c for c in cols_to_show if c in high_risk_df.columns]
        st.dataframe(high_risk_df[show_cols])

    st.divider()

    # Full student table
    st.subheader("📋 Full Student Table")
    extra = ["stress_score", "stress_level", "recommendation"]
    show_all = [c for c in df_proc.columns if c not in extra] + [c for c in extra if c in df_proc.columns]
    st.dataframe(df_proc[show_all])

    st.divider()

    # Charts
    st.subheader("📈 Visual Analytics")

    ch1, ch2 = st.columns(2)
    with ch1:
        fig_stress = px.box(
            df_proc, x="year", y="stress_score", color="year",
            title="Stress Score by Year",
            category_orders={"year": year_order},
        )
        st.plotly_chart(fig_stress, use_container_width=True)
    with ch2:
        fig_sleep = px.box(
            df_proc, x="year", y="daily_sleep_hours", color="year",
            title="Sleep Hours by Year",
            category_orders={"year": year_order},
        )
        st.plotly_chart(fig_sleep, use_container_width=True)

    ch3, ch4 = st.columns(2)
    with ch3:
        fig_dist = px.histogram(
            df_proc, x="stress_level", color="stress_level",
            title="Stress Level Distribution",
            category_orders={"stress_level": ["Low", "Medium", "High"]},
            color_discrete_map={"Low": "#2ecc71", "Medium": "#f39c12", "High": "#e74c3c"},
        )
        st.plotly_chart(fig_dist, use_container_width=True)
    with ch4:
        fig_scatter = px.scatter(
            df_proc, x="daily_sleep_hours", y="stress_score",
            color="stress_level", size="daily_study_hours",
            title="Sleep vs. Stress (size = study hours)",
            color_discrete_map={"Low": "#2ecc71", "Medium": "#f39c12", "High": "#e74c3c"},
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    st.divider()

    # Export
    st.subheader("📥 Export Analysed Data")
    st.download_button(
        "⬇️ Download Analysed CSV",
        data=df_proc.to_csv(index=False).encode("utf-8"),
        file_name="analysed_class_data.csv",
        mime="text/csv",
    )


# ===========================================================================
# PAGE 4 — CUSTOM DATA UPLOADER
# ===========================================================================
elif page == "📁 4. Custom Data Uploader":
    st.title("📁 Custom Data Uploader")
    st.write("Upload any CSV dataset. Optionally apply the stress analysis engine if your data has the required columns.")

    uploaded_file = st.file_uploader("Drop your CSV file here", type=["csv"])

    if uploaded_file is None:
        st.info("Awaiting CSV upload…")
        st.stop()

    df_upload = pd.read_csv(uploaded_file)
    st.success(f"**{uploaded_file.name}** uploaded ({len(df_upload)} rows, {len(df_upload.columns)} columns).")

    # Search
    st.subheader("🔍 Search Records")
    columns = df_upload.columns.tolist()
    sc1, sc2 = st.columns(2)
    search_col  = sc1.selectbox("Search by column:", columns)
    search_term = sc2.text_input(f"Search value in '{search_col}':")

    if search_term:
        filtered = df_upload[df_upload[search_col].astype(str).str.contains(search_term, case=False, na=False)]
        if not filtered.empty:
            st.dataframe(filtered)
        else:
            st.warning("No matching records found.")

    st.divider()

    with st.expander("👁️ Preview Full Data"):
        st.dataframe(df_upload.head(20))

    # Optional stress analysis
    st.subheader("🧠 Optional: Apply Stress Analysis Engine")
    missing = validate_teacher_csv(df_upload)
    if missing:
        st.info(f"Stress analysis requires these additional columns: `{'`, `'.join(missing)}`")
        apply_analysis = False
    else:
        apply_analysis = st.checkbox("✅ Apply stress analysis to this dataset", value=True)

    if apply_analysis:
        df_analysed = process_dataframe(df_upload)
        st.success("Stress analysis applied successfully!")
        st.dataframe(df_analysed)

        # Auto insights
        st.subheader("🔔 Auto Insights")
        for insight in generate_auto_insights(df_analysed):
            if insight.startswith("✅"):
                st.success(insight)
            elif insight.startswith("🚨"):
                st.error(insight)
            else:
                st.warning(insight)

        export_df = df_analysed
    else:
        export_df = df_upload

    st.divider()

    # Custom chart builder
    st.subheader("📊 Build Your Own Chart")
    chart_cols = export_df.columns.tolist()
    cc1, cc2 = st.columns(2)
    x_axis = cc1.selectbox("X-Axis", chart_cols, key="x")
    y_axis = cc2.selectbox("Y-Axis", chart_cols, index=min(1, len(chart_cols) - 1), key="y")

    chart_type = st.selectbox("Chart Type", ["Scatter", "Bar", "Box", "Histogram"])

    if st.button("Generate Chart"):
        if chart_type == "Scatter":
            fig_c = px.scatter(export_df, x=x_axis, y=y_axis, title=f"{y_axis} vs {x_axis}")
        elif chart_type == "Bar":
            fig_c = px.bar(export_df, x=x_axis, y=y_axis, title=f"{y_axis} by {x_axis}")
        elif chart_type == "Box":
            fig_c = px.box(export_df, x=x_axis, y=y_axis, title=f"{y_axis} by {x_axis}")
        else:
            fig_c = px.histogram(export_df, x=x_axis, title=f"Distribution of {x_axis}")
        st.plotly_chart(fig_c, use_container_width=True)

    st.divider()

    # Export
    st.subheader("📥 Export Data")
    st.download_button(
        "⬇️ Download CSV",
        data=export_df.to_csv(index=False).encode("utf-8"),
        file_name="exported_data.csv",
        mime="text/csv",
    )