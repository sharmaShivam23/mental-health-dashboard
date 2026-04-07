import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Student Mental Health Analytics", layout="wide", page_icon="🎓")


st.sidebar.title("Navigation Menu")
st.sidebar.write("Choose a feature below:")
page = st.sidebar.radio("Go to:", [
    "📊 1. Pre-built Dashboard", 
    "📝 2. Personal Wellness Tracker", 
    "📁 3. Custom Data Uploader"
])

st.sidebar.divider()
st.sidebar.info("Developed for Data Analysis Lab 💻")


if page == "📊 1. Pre-built Dashboard":
    st.title("📊 Main Student Dashboard")
    st.write("Comprehensive analysis of our primary student mental health dataset.")
    
    try:
       
        df_static = pd.read_csv("student_data.csv")
        
       
        numeric_columns = ['cgpa', 'daily_study_hours', 'daily_sleep_hours', 'anxiety_score', 
                           'depression_score', 'screen_time_hours', 'academic_pressure_score']
        
        for col in numeric_columns:
            if col in df_static.columns:
                df_static[col] = pd.to_numeric(df_static[col], errors='coerce')
        
        st.success("Primary dataset loaded and matched to correct data types!")
        
     
        st.subheader("Overall Class Averages")
        
    
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Students Analyzed", len(df_static))
        with col2:
            st.metric("Average CGPA", round(df_static['cgpa'].mean(), 2))
        with col3:
            st.metric("Avg Daily Study Hours", round(df_static['daily_study_hours'].mean(), 1))
        with col4:
            st.metric("Avg Daily Sleep Hours", round(df_static['daily_sleep_hours'].mean(), 1))
            
        st.write("") # Spacer
        
     
        col5, col6, col7, col8 = st.columns(4)
        with col5:
            st.metric("Avg Anxiety Score", round(df_static['anxiety_score'].mean(), 1))
        with col6:
            st.metric("Avg Depression Score", round(df_static['depression_score'].mean(), 1))
        with col7:
            st.metric("Avg Academic Pressure", round(df_static['academic_pressure_score'].mean(), 1))
        with col8:
            st.metric("Avg Screen Time (hrs)", round(df_static['screen_time_hours'].mean(), 1))
            
        st.divider()
  
        st.subheader("📈 In-Depth Visual Analytics")
        
        # Chart Row 1
        c_left1, c_right1 = st.columns(2)
        with c_left1:
            fig1 = px.histogram(df_static, x="gender", y="anxiety_score", color="gender", 
                                title="1. Average Anxiety by Gender", histfunc="avg", text_auto='.1f')
            st.plotly_chart(fig1, use_container_width=True)
            
        with c_right1:
      
            fig2 = px.scatter(df_static, x="daily_study_hours", y="cgpa", color="stress_level", 
                              title="2. Study Hours vs. CGPA (Colored by Stress)",
                              category_orders={"stress_level": ["Low", "Medium", "High"]})
            st.plotly_chart(fig2, use_container_width=True)

        # Chart Row 2
        c_left2, c_right2 = st.columns(2)
        with c_left2:
            # Box plot to show distribution
            fig3 = px.box(df_static, x="year", y="depression_score", color="year", 
                          title="3. Depression Scores across Years of Study",
                          category_orders={"year": ["1st", "2nd", "3rd", "4th"]})
            st.plotly_chart(fig3, use_container_width=True)
            
        with c_right2:
            # Bar chart grouping categorical 'sleep_quality' vs numeric 'anxiety_score'
            sleep_df = df_static.dropna(subset=['sleep_quality', 'anxiety_score'])
            sleep_anx = sleep_df.groupby('sleep_quality')['anxiety_score'].mean().reset_index()
            fig4 = px.bar(sleep_anx, x='sleep_quality', y='anxiety_score', color='sleep_quality',
                          title="4. How Sleep Quality Affects Average Anxiety",
                          category_orders={"sleep_quality": ["Poor", "Average", "Good"]})
            st.plotly_chart(fig4, use_container_width=True)
            
        # Chart Row 3 (Full Width)
        st.write("")
        st.markdown("#### 5. Academic Pressure vs. Reported Stress Levels")
        st.write("This heatmap shows the concentration of students based on numeric academic pressure and their reported text-based stress level.")
        
        heatmap_df = df_static.dropna(subset=['academic_pressure_score', 'stress_level'])
        fig5 = px.density_heatmap(heatmap_df, x="academic_pressure_score", y="stress_level", 
                                  title="Heatmap: Academic Pressure vs. Stress Status",
                                  category_orders={"stress_level": ["Low", "Medium", "High"]},
                                  color_continuous_scale="Blues")
        st.plotly_chart(fig5, use_container_width=True)
                
    except Exception as e:
        st.error(f"🚨 Error: {e}")


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
            # Changed slider to match your dataset's text format!
            stress_level = st.selectbox("Current Stress Level", ["Low", "Medium", "High"])
            
        submit = st.form_submit_button("Get Insights & Submit Data")
        
        if submit:
            # Wellness logic adapted for text-based stress
            burnout_risk = "Low"
            if stress_level == "High" and sleep_hours <= 5: burnout_risk = "High"
            elif stress_level in ["Medium", "High"] or study_hours >= 8: burnout_risk = "Moderate"
            
            st.divider()
            st.subheader(f"Your Burnout Risk: **{burnout_risk}**")
            if burnout_risk == "High": st.error("Please prioritize sleep and take a break!")
            elif burnout_risk == "Moderate": st.warning("You are working hard. Don't forget to hydrate and rest.")
            else: st.success("Great job maintaining a healthy balance!")
            
            new_entry = pd.DataFrame([{"Gender": gender, "Year": year, "Study_Hours": study_hours, "Sleep_Hours": sleep_hours, "Stress_Level": stress_level, "Burnout_Risk": burnout_risk}])
            new_entry.to_csv(LIVE_FILE, mode='a', header=False, index=False)
            st.toast("Data saved to live database!")

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
elif page == " 3. Custom Data Uploader":
    st.title("Custom Data Uploader")
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
            # Scatter plots are safest for custom dynamic data
            fig_custom = px.scatter(df_upload, x=x_axis, y=y_axis, title=f"{y_axis} vs {x_axis}")
            st.plotly_chart(fig_custom, use_container_width=True)
            st.info("Tip: Try uploading different datasets to see how dynamic this tool is!")