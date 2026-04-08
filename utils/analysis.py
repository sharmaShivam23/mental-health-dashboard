"""
utils/analysis.py
Shared analysis engine for Student Mental Health Analytics Platform.
"""

import pandas as pd

TEACHER_REQUIRED_COLUMNS = [
    "student_id", "name", "year", "gender",
    "daily_study_hours", "daily_sleep_hours", "screen_time_hours",
    "assignment_load", "physical_activity_hours", "diet_quality",
    "social_support", "loneliness_level", "self_esteem",
    "motivation_level", "late_night_usage",
]

LIVE_FILE_COLUMNS = [
    "Student_Name", "Student_ID", "Gender", "Year",
    "Study_Hours", "Sleep_Hours", "Screen_Time", "Assignment_Load",
    "Physical_Activity", "Diet_Quality", "Social_Support",
    "Loneliness_Level", "Self_Esteem", "Motivation_Level",
    "Late_Night_Usage", "Stress_Score", "Stress_Level",
]


def compute_full_analysis(data: dict) -> dict:
    def _get(key, default=0):
        try:
            return float(data.get(key, default) or default)
        except (ValueError, TypeError):
            return float(default)

    score = 0
    contributors = []
    recommendations = []

    # Academic
    study_h = _get("daily_study_hours")
    assign = _get("assignment_load", 5)
    pressure = _get("academic_pressure_score", assign)

    if study_h > 10:
        score += 15
        contributors.append("📚 Extremely high daily study hours (>10 hrs)")
        recommendations.append("Cap active study sessions at 8–9 hrs and use the Pomodoro technique.")
    elif study_h > 7:
        score += 8

    norm_assign = min(pressure / 10.0, 1.0)
    score += int(norm_assign * 15)
    if pressure >= 7:
        contributors.append(f"📝 High assignment/academic pressure ({pressure:.0f}/10)")
        recommendations.append("Break large assignments into daily sub-tasks to reduce perceived pressure.")

    # Lifestyle
    sleep_h = _get("daily_sleep_hours", 7)
    activity = _get("physical_activity_hours", 1)
    diet = _get("diet_quality", 5)

    if sleep_h < 5:
        score += 20
        contributors.append(f"😴 Critically low sleep ({sleep_h:.1f} hrs/day)")
        recommendations.append("Prioritise 7–8 hours of sleep. Poor sleep amplifies every other stressor.")
    elif sleep_h < 7:
        score += 10
        contributors.append(f"😴 Below-optimal sleep ({sleep_h:.1f} hrs/day)")
        recommendations.append("Aim for at least 7 hours of sleep. Try a consistent bedtime routine.")

    if activity < 0.5:
        score += 8
        contributors.append("🏃 Little to no physical activity")
        recommendations.append("Add 30 minutes of walking or any exercise daily — it cuts anxiety significantly.")
    elif activity < 1:
        score += 4

    diet_penalty = int((1 - min(diet / 10.0, 1.0)) * 8)
    score += diet_penalty
    if diet < 5:
        contributors.append(f"🥗 Poor diet quality ({diet:.0f}/10)")
        recommendations.append("Improve meal regularity and include fruits/vegetables to support cognitive function.")

    # Behavioral
    screen = _get("screen_time_hours", 3)
    late_nt = _get("late_night_usage", 0)

    if screen > 6:
        score += 10
        contributors.append(f"📱 High screen time ({screen:.1f} hrs/day)")
        recommendations.append("Use app timers to limit recreational screen time to under 4 hrs/day.")
    elif screen > 4:
        score += 5

    if late_nt > 2:
        score += 8
        contributors.append(f"🌙 Excessive late-night device usage ({late_nt:.1f} hrs past midnight)")
        recommendations.append("Set a device curfew 1 hour before sleep to protect sleep quality.")
    elif late_nt > 1:
        score += 4

    # Social
    support = _get("social_support", 5)
    loneliness = _get("loneliness_level", 5)

    support_penalty = int((1 - min(support / 10.0, 1.0)) * 5)
    score += support_penalty
    if support < 4:
        contributors.append(f"🤝 Low social support ({support:.0f}/10)")
        recommendations.append("Schedule regular time with friends or join a student club to build support networks.")

    if loneliness > 7:
        score += 5
        contributors.append(f"😔 High loneliness level ({loneliness:.0f}/10)")
        recommendations.append("Talk to a counsellor or trusted friend. Loneliness is a strong stress amplifier.")

    # Psychological
    esteem = _get("self_esteem", 5)
    motivation = _get("motivation_level", 5)

    esteem_penalty = int((1 - min(esteem / 10.0, 1.0)) * 5)
    score += esteem_penalty
    if esteem < 4:
        contributors.append(f"💭 Low self-esteem ({esteem:.0f}/10)")
        recommendations.append("Maintain a daily achievement log — small wins rebuild confidence over time.")

    motivation_penalty = int((1 - min(motivation / 10.0, 1.0)) * 5)
    score += motivation_penalty
    if motivation < 4:
        contributors.append(f"⚡ Low motivation ({motivation:.0f}/10)")
        recommendations.append("Set short-term achievable goals and reward yourself to rebuild intrinsic motivation.")

    stress_score = max(0, min(100, score))
    if stress_score >= 60:
        stress_level = "High"
    elif stress_score >= 35:
        stress_level = "Medium"
    else:
        stress_level = "Low"

    if not contributors:
        contributors.append("✅ No major stress contributors detected.")
    if not recommendations:
        recommendations.append("✅ Keep up your current healthy habits!")

    return {
        "stress_score": stress_score,
        "stress_level": stress_level,
        "contributors": contributors,
        "recommendations": recommendations,
    }


def process_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    results = df.to_dict(orient="records")
    scores, levels, recs = [], [], []
    for row in results:
        out = compute_full_analysis(row)
        scores.append(out["stress_score"])
        levels.append(out["stress_level"])
        recs.append(out["recommendations"][0] if out["recommendations"] else "—")
    df = df.copy()
    df["stress_score"] = scores
    df["stress_level"] = levels
    df["recommendation"] = recs
    return df


def validate_teacher_csv(df: pd.DataFrame) -> list:
    return [col for col in TEACHER_REQUIRED_COLUMNS if col not in df.columns]


def compute_class_health_score(group_df: pd.DataFrame) -> int:
    if group_df.empty:
        return 0
    avg_stress = group_df["stress_score"].mean() if "stress_score" in group_df.columns else 50
    return max(0, min(100, int(100 - avg_stress)))


def generate_class_recommendations(group_df: pd.DataFrame) -> list:
    recs = []
    if group_df.empty:
        return ["No data available."]

    def avg(col):
        return group_df[col].mean() if col in group_df.columns else None

    if (v := avg("daily_sleep_hours")) and v < 6.5:
        recs.append(f"🛌 Class avg sleep is {v:.1f} hrs — run sleep hygiene awareness sessions.")
    if (v := avg("daily_study_hours")) and v > 8:
        recs.append(f"📚 Avg study load ({v:.1f} hrs/day) is high — explore structured timetable workshops.")
    if (v := avg("screen_time_hours")) and v > 5:
        recs.append(f"📱 Screen time averaging {v:.1f} hrs — recommend a digital detox initiative.")
    if (v := avg("physical_activity_hours")) and v < 0.5:
        recs.append("🏃 Very low physical activity — organise short daily exercise breaks.")
    if (v := avg("stress_score")) and v >= 60:
        recs.append(f"🚨 Avg stress score {v:.0f}/100 — immediate counselling outreach needed.")
    elif (v := avg("stress_score")) and v >= 40:
        recs.append(f"⚠️ Moderate avg stress ({v:.0f}/100) — introduce weekly mindfulness activities.")
    if (v := avg("loneliness_level")) and v > 6:
        recs.append("😔 High avg loneliness — organise more peer-bonding activities.")
    if (v := avg("social_support")) and v < 4:
        recs.append("🤝 Low social support — consider mentorship pairing programmes.")
    if not recs:
        recs.append("✅ This class is in good health. Maintain current balance.")
    return recs


def generate_auto_insights(df: pd.DataFrame) -> list:
    insights = []
    if df.empty:
        return insights

    if "stress_level" in df.columns:
        high_pct = (df["stress_level"] == "High").mean() * 100
        if high_pct > 30:
            insights.append(f"🚨 {high_pct:.0f}% of students at HIGH stress — immediate intervention recommended.")
        elif high_pct > 15:
            insights.append(f"⚠️ {high_pct:.0f}% of students show HIGH stress — monitor closely.")

    if "daily_sleep_hours" in df.columns:
        low_sleep_pct = (df["daily_sleep_hours"] < 6).mean() * 100
        if low_sleep_pct > 40:
            insights.append(f"😴 {low_sleep_pct:.0f}% of students sleep fewer than 6 hours.")

    if "physical_activity_hours" in df.columns:
        no_act_pct = (df["physical_activity_hours"] < 0.5).mean() * 100
        if no_act_pct > 50:
            insights.append(f"🏃 {no_act_pct:.0f}% of students have near-zero physical activity.")

    if "screen_time_hours" in df.columns:
        hi_screen_pct = (df["screen_time_hours"] > 6).mean() * 100
        if hi_screen_pct > 40:
            insights.append(f"📱 {hi_screen_pct:.0f}% of students have screen time above 6 hrs/day.")

    if not insights:
        insights.append("✅ No critical cohort-wide risk flags detected.")
    return insights


def get_sample_csv() -> str:
    sample_data = {
        "student_id":              [101, 102, 103],
        "name":                    ["Alice Sharma", "Bob Verma", "Carol Singh"],
        "year":                    ["2nd", "3rd", "1st"],
        "gender":                  ["Female", "Male", "Female"],
        "daily_study_hours":       [6, 9, 4],
        "daily_sleep_hours":       [7, 5, 8],
        "screen_time_hours":       [3, 7, 2],
        "assignment_load":         [6, 8, 4],
        "physical_activity_hours": [1, 0.5, 2],
        "diet_quality":            [7, 4, 8],
        "social_support":          [7, 3, 9],
        "loneliness_level":        [3, 8, 2],
        "self_esteem":             [7, 4, 8],
        "motivation_level":        [7, 4, 9],
        "late_night_usage":        [0.5, 3, 0],
    }
    return pd.DataFrame(sample_data).to_csv(index=False)
