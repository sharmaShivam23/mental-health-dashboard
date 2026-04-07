import streamlit as st
import pandas as pd
import plotly.express as px
import os


st.set_page_config(page_title="Student Mental Health Analytics", layout="wide", page_icon="🎓")


@st.cache_data
def load_primary_data():
    try:
        df = pd.read_csv("student_data.csv")
        # Clean data silently
        numeric_columns = ['cgpa', 'daily_study_hours', 'daily_sleep_hours', 'anxiety_score', 
                           'depression_score', 'screen_time_hours', 'academic_pressure_score']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        return df
    except FileNotFoundError:
        return None


st.sidebar.title("Navigation Menu")
page = st.sidebar.radio("Go to:", [
    "📊 1. Pre-built Dashboard", 
    "📝 2. Personal Wellness Tracker", 
    "📁 3. Custom Data Uploader"
])
st.sidebar.divider()
st.sidebar.info("Developed for Data Analysis Lab 💻")

# ==========================================
# --- FEATURE 1: PRE-BUILT DASHBOARD ---
# ==========================================
if page == "📊 1. Pre-built Dashboard":
    st.title("📊 Main Student Dashboard")
    st.write("Comprehensive analysis of our primary student mental health dataset.")
    
    df_static = load_primary_data()
    
    if df_static is not None:
        
      
        st.sidebar.subheader("🎯 Filter Dashboard Data")
        
       
        years = df_static['year'].dropna().unique()
        selected_years = st.sidebar.multiselect("Select Year of Study:", years, default=years)
        
    
        genders = df_static['gender'].dropna().unique()
        selected_genders = st.sidebar.multiselect("Select Gender:", genders, default=genders)
        
     
        filtered_df = df_static[(df_static['year'].isin(selected_years)) & (df_static['gender'].isin(selected_genders))]
        
        if filtered_df.empty:
            st.warning("No data available for the selected filters. Please adjust your selection in the sidebar.")
        else:
            st.success(f"Showing data for {len(filtered_df)} students based on your filters!")
            
           
            st.subheader("📌 Filtered Class Averages")
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Students Analyzed", len(filtered_df))
            col2.metric("Average CGPA", round(filtered_df['cgpa'].mean(), 2))
            col3.metric("Avg Daily Study Hours", round(filtered_df['daily_study_hours'].mean(), 1))
            col4.metric("Avg Daily Sleep Hours", round(filtered_df['daily_sleep_hours'].mean(), 1))
                
            st.write("") 
            
            col5, col6, col7, col8 = st.columns(4)
            col5.metric("Avg Anxiety Score", round(filtered_df['anxiety_score'].mean(), 1))
            col6.metric("Avg Depression Score", round(filtered_df['depression_score'].mean(), 1))
            col7.metric("Avg Academic Pressure", round(filtered_df['academic_pressure_score'].mean(), 1))
            col8.metric("Avg Screen Time (hrs)", round(filtered_df['screen_time_hours'].mean(), 1))
                
            st.divider()
            
            
            st.subheader("📈 In-Depth Visual Analytics")
            
            c_left1, c_right1 = st.columns(2)
            with c_left1:
                fig1 = px.histogram(filtered_df, x="gender", y="anxiety_score", color="gender", 
                                    title="1. Average Anxiety by Gender", histfunc="avg", text_auto='.1f')
                st.plotly_chart(fig1, use_container_width=True)
                
            with c_right1:
                fig2 = px.scatter(filtered_df, x="daily_study_hours", y="cgpa", color="stress_level", 
                                  title="2. Study Hours vs. CGPA (Colored by Stress)",
                                  category_orders={"stress_level": ["Low", "Medium", "High"]})
                st.plotly_chart(fig2, use_container_width=True)

            c_left2, c_right2 = st.columns(2)
            with c_left2:
                fig3 = px.box(filtered_df, x="year", y="depression_score", color="year", 
                              title="3. Depression Scores across Years of Study",
                              category_orders={"year": ["1st", "2nd", "3rd", "4th"]})
                st.plotly_chart(fig3, use_container_width=True)
                
            with c_right2:
                sleep_df = filtered_df.dropna(subset=['sleep_quality', 'anxiety_score'])
                sleep_anx = sleep_df.groupby('sleep_quality')['anxiety_score'].mean().reset_index()
                fig4 = px.bar(sleep_anx, x='sleep_quality', y='anxiety_score', color='sleep_quality',
                              title="4. How Sleep Quality Affects Average Anxiety",
                              category_orders={"sleep_quality": ["Poor", "Average", "Good"]})
                st.plotly_chart(fig4, use_container_width=True)
                
            st.write("")
            st.markdown("#### 5. Academic Pressure vs. Reported Stress Levels")
            
            heatmap_df = filtered_df.dropna(subset=['academic_pressure_score', 'stress_level'])
            fig5 = px.density_heatmap(heatmap_df, x="academic_pressure_score", y="stress_level", 
                                      title="Heatmap: Academic Pressure vs. Stress Status",
                                      category_orders={"stress_level": ["Low", "Medium", "High"]},
                                      color_continuous_scale="Blues")
            st.plotly_chart(fig5, use_container_width=True)
            
            # --- NEW: DOWNLOAD FILTERED DATA BUTTON ---
            st.divider()
            st.subheader("📥 Export Data")
            st.write("Download the customized dataset based on your current sidebar filters.")
            csv_export = filtered_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Filtered CSV",
                data=csv_export,
                file_name='custom_student_data.csv',
                mime='text/csv',
            )
            
    else:
        st.error(" Error: 'student_data.csv' not found. Please ensure it is in your project folder.")

# ==================================================
# --- FEATURE 2: PERSONAL WELLNESS TRACKER ---
# ==================================================
elif page == "📝 2. Personal Wellness Tracker":
    st.title("📝 Personal Wellness Tracker")
    st.write("Fill out the form to get personal insights. Your data will be added anonymously to the live database!")
    
    LIVE_FILE = "live_student_data.csv"
    
    if not os.path.exists(LIVE_FILE):
        pd.DataFrame(columns=["Gender", "Year", "Study_Hours", "Sleep_Hours", "Stress_Level", "Burnout_Risk"]).to_csv(LIVE_FILE, index=False)

    with st.form("wellness_form"):
        col1, col2 = st.columns(2)
        with col1:
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            year = st.selectbox("Year of Study", ["1st", "2nd", "3rd", "4th"])
            study_hours = st.number_input("Daily Study Hours", min_value=0.0, max_value=24.0, value=4.0)
        with col2:
            sleep_hours = st.number_input("Daily Sleep Hours", min_value=0.0, max_value=24.0, value=6.0)
            stress_level = st.selectbox("Current Stress Level", ["Low", "Medium", "High"])
            
        submit = st.form_submit_button("Get Insights & Submit Data")
        
    if submit:
        # Core Logic
        burnout_risk = "Low"
        if stress_level == "High" and sleep_hours <= 5: burnout_risk = "High"
        elif stress_level in ["Medium", "High"] or study_hours >= 8: burnout_risk = "Moderate"
        
        st.divider()
        st.subheader(f"Your Burnout Risk: **{burnout_risk}**")
        
        advice_text = ""
        if burnout_risk == "High": 
            advice_text = "🚨 You are at high risk of burnout! Please prioritize getting at least 7 hours of sleep and consider taking a break from studying."
            st.error(advice_text)
        elif burnout_risk == "Moderate": 
            advice_text = "⚠️ You are pushing your limits. Don't forget to hydrate, schedule short breaks, and rest."
            st.warning(advice_text)
        else: 
            advice_text = " Great job maintaining a healthy academic and lifestyle balance!"
            st.success(advice_text)
            
        # Database Save
        new_entry = pd.DataFrame([{"Gender": gender, "Year": year, "Study_Hours": study_hours, "Sleep_Hours": sleep_hours, "Stress_Level": stress_level, "Burnout_Risk": burnout_risk}])
        new_entry.to_csv(LIVE_FILE, mode='a', header=False, index=False)
        st.toast("Data saved to live database!")
        
        # --- NEW: DOWNLOAD PERSONAL REPORT BUTTON ---
        report_content = f"""--- MENTAL HEALTH & WELLNESS REPORT ---

Student Profile:
- Gender: {gender}
- Year of Study: {year}

Daily Metrics:
- Study Hours: {study_hours}
- Sleep Hours: {sleep_hours}
- Self-Reported Stress: {stress_level}

ASSESSMENT RESULT:
Burnout Risk Level: {burnout_risk.upper()}
Recommendations: {advice_text}

Generated by the AKGEC Student Analytics System.
"""
        st.download_button(
            label="📥 Download My Official Report",
            data=report_content,
            file_name="My_Wellness_Report.txt",
            mime="text/plain"
        )

    st.divider()
    st.subheader("Live Database Trends")
    try:
        df_live = pd.read_csv(LIVE_FILE)
        if len(df_live) > 0:
            fig_live = px.pie(df_live, names="Burnout_Risk", title="Class Burnout Distribution (Live)")
            st.plotly_chart(fig_live, use_container_width=True)
        else:
            st.info("Submit the first entry to see live charts!")
    except:
        pass

# ============================================
# --- FEATURE 3: CUSTOM DATA UPLOADER ---
# ============================================
elif page == "📁 3. Custom Data Uploader":
    st.title("📁 Custom Data Uploader")
    st.write("Upload any CSV dataset. You can manually choose which columns to visualize!")
    
    uploaded_file = st.file_uploader("Drop your CSV file here", type=["csv"])
    
    if uploaded_file is not None:
        df_upload = pd.read_csv(uploaded_file)
        st.success("File uploaded successfully!")
        
        with st.expander("Preview Uploaded Data"):
            st.dataframe(df_upload.head())
            
        st.subheader("Build Your Own Chart")
        columns = df_upload.columns.tolist()
        
        col1, col2 = st.columns(2)
        with col1:
            x_axis = st.selectbox("Choose X-Axis Column", columns)
        with col2:
            y_axis = st.selectbox("Choose Y-Axis Column", columns)
            
        if st.button("Generate Chart"):
            fig_custom = px.scatter(df_upload, x=x_axis, y=y_axis, title=f"{y_axis} vs {x_axis}")
            st.plotly_chart(fig_custom, use_container_width=True)
            st.info("Tip: Try uploading different datasets to see how dynamic this tool is!")