import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ======================
# CONFIG
# ======================
st.set_page_config(page_title="Bike Sharing Dashboard", layout="wide")
st.title("🚲 Bike Sharing Dashboard")

# ======================
# LOAD DATA
# ======================
day_df = pd.read_csv("day_clean.csv")
hour_df = pd.read_csv("hour_clean.csv")

# ======================
# MAPPING LABEL
# ======================
season_map = {1:"Spring", 2:"Summer", 3:"Fall", 4:"Winter"}
weather_map = {1:"Clear", 2:"Mist", 3:"Light Rain/Snow", 4:"Heavy Rain/Snow"}
workingday_map = {0:"Libur", 1:"Hari Kerja"}

day_df["season"] = day_df["season"].map(season_map)
day_df["weathersit"] = day_df["weathersit"].map(weather_map)
day_df["workingday"] = day_df["workingday"].map(workingday_map)

# ======================
# CLUSTERING
# ======================
def rental_category(x):
    if x <= 2000:
        return "Low"
    elif x <= 5000:
        return "Medium"
    else:
        return "High"

day_df["rental_category"] = day_df["cnt"].apply(rental_category)

# ======================
# SIDEBAR FILTER
# ======================
st.sidebar.header("🔎 Filter Data")

selected_season = st.sidebar.multiselect(
    "Musim",
    options=day_df["season"].unique(),
    default=day_df["season"].unique()
)

selected_weather = st.sidebar.multiselect(
    "Cuaca",
    options=day_df["weathersit"].unique(),
    default=day_df["weathersit"].unique()
)

selected_workingday = st.sidebar.multiselect(
    "Jenis Hari",
    options=day_df["workingday"].unique(),
    default=day_df["workingday"].unique()
)

min_cnt = int(day_df["cnt"].min())
max_cnt = int(day_df["cnt"].max())

cnt_range = st.sidebar.slider(
    "Range Penyewaan",
    min_value=min_cnt,
    max_value=max_cnt,
    value=(min_cnt, max_cnt)
)

# ======================
# APPLY FILTER
# ======================
filtered_day = day_df[
    (day_df["season"].isin(selected_season)) &
    (day_df["weathersit"].isin(selected_weather)) &
    (day_df["workingday"].isin(selected_workingday)) &
    (day_df["cnt"].between(cnt_range[0], cnt_range[1]))
]

filtered_hour = hour_df[
    hour_df["dteday"].isin(filtered_day["dteday"])
]

# ======================
# METRIC (FIX ERROR)
# ======================
st.subheader("📊 Ringkasan Data")

col1, col2, col3 = st.columns(3)

if filtered_day.empty:
    col1.metric("Total Penyewaan", 0)
    col2.metric("Rata-rata", 0)
    col3.metric("Jumlah Data", 0)
    st.warning("⚠️ Tidak ada data yang sesuai dengan filter.")
else:
    col1.metric("Total Penyewaan", int(filtered_day["cnt"].sum()))
    col2.metric("Rata-rata", int(filtered_day["cnt"].mean()))
    col3.metric("Jumlah Data", len(filtered_day))

# ======================
# VISUALISASI
# ======================
if not filtered_day.empty:

    col1, col2 = st.columns(2)

    # SEASON
    with col1:
        st.subheader("📈 Musim")
        season_avg = filtered_day.groupby("season")["cnt"].mean().sort_values(ascending=False)

        fig, ax = plt.subplots()
        sns.barplot(x=season_avg.index, y=season_avg.values, ax=ax)
        ax.set_title("Rata-rata Penyewaan")
        st.pyplot(fig)

    # WEATHER
    with col2:
        st.subheader("🌤️ Cuaca")
        weather_avg = filtered_day.groupby("weathersit")["cnt"].mean().sort_values(ascending=False)

        fig, ax = plt.subplots()
        sns.barplot(x=weather_avg.index, y=weather_avg.values, ax=ax)
        ax.set_title("Rata-rata Penyewaan")
        st.pyplot(fig)

    # WORKINGDAY
    st.subheader("📅 Hari Kerja vs Libur")

    working_avg = filtered_day.groupby("workingday")["cnt"].mean().sort_values(ascending=False)

    fig, ax = plt.subplots()
    sns.barplot(x=working_avg.index, y=working_avg.values, ax=ax)
    ax.set_title("Rata-rata Penyewaan")
    st.pyplot(fig)

    # POLA JAM
    if not filtered_hour.empty:
        st.subheader("⏰ Pola Jam")

        hour_avg = filtered_hour.groupby("hr")["cnt"].mean()

        fig, ax = plt.subplots(figsize=(10,4))
        sns.lineplot(x=hour_avg.index, y=hour_avg.values, marker="o", ax=ax)
        ax.set_xticks(range(0,24))
        ax.set_title("Pola Penyewaan")
        st.pyplot(fig)

    # CLUSTERING
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Kategori Penyewaan")

        fig, ax = plt.subplots()
        sns.countplot(
            data=filtered_day,
            x="rental_category",
            order=["Low","Medium","High"],
            ax=ax
        )
        st.pyplot(fig)

    with col2:
        st.subheader("🔍 Cluster vs Musim")
        cluster_season = filtered_day.groupby(["season", "rental_category"])["cnt"].count().unstack()
        st.dataframe(cluster_season)

# ======================
# INSIGHT
# ======================
st.subheader("💡 Insight")

st.write("""
- Musim Fall dan Summer memiliki penyewaan tertinggi.
- Cuaca cerah meningkatkan jumlah penyewaan secara signifikan.
- Hari kerja menunjukkan penggunaan yang lebih konsisten.
- Pola peak terjadi pada pagi dan sore hari.
- Clustering menunjukkan mayoritas berada pada kategori Medium dan High.
""")