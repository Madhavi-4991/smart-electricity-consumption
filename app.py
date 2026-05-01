import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import json, os, hashlib, secrets
from datetime import datetime, timedelta

# ---------------- CONFIG ----------------
st.set_page_config(page_title="EcoWatt India", page_icon="⚡", layout="wide")

# ---------------- CONSTANTS ----------------
COST_PER_KWH = 7.5
CO2_PER_KWH = 0.82

# ---------------- CSS ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg,#1f4037,#99f2c8);
    color:#111;
}

/* Card Style */
.card {
    background: white;
    padding:15px;
    border-radius:15px;
    box-shadow:0 4px 10px rgba(0,0,0,0.1);
    text-align:center;
}

/* Equal Image Size */
.card img {
    height:200px;
    object-fit:cover;
    border-radius:10px;
    width:100%;
}

/* Titles */
h1,h2,h3 {color:#0b3d2e;}
</style>
""", unsafe_allow_html=True)

USER_FILE = "users.json"

# ---------------- AUTH ----------------
def hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_hex(16)
    return salt + ":" + hashlib.sha256((password+salt).encode()).hexdigest()

def verify_password(stored, password):
    try:
        salt, hashed = stored.split(":")
        return hashed == hashlib.sha256((password+salt).encode()).hexdigest()
    except:
        return False

def load_users():
    if not os.path.exists(USER_FILE): return {}
    return json.load(open(USER_FILE))

def save_user(u,p):
    users = load_users()
    if u in users: return False
    users[u] = hash_password(p)
    json.dump(users, open(USER_FILE,"w"))
    return True

def auth(u,p):
    users = load_users()
    return u in users and verify_password(users[u],p)

# ---------------- SESSION ----------------
if "login" not in st.session_state:
    st.session_state.login=False
if "df" not in st.session_state:
    st.session_state.df=pd.DataFrame(columns=["Date","Usage"])

# ---------------- LOGIN ----------------
def login():
    st.title("⚡ Smart Electricity Consumption Analysis")

    tab1, tab2 = st.tabs(["Login","Signup"])

    with tab1:
        u=st.text_input("Username",key="l1")
        p=st.text_input("Password",type="password",key="l2")

        if st.button("Login"):
            if auth(u,p):
                st.session_state.login=True
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        u=st.text_input("New Username",key="s1")
        p=st.text_input("New Password",type="password",key="s2")

        if st.button("Create"):
            if save_user(u,p):
                st.success("Account created")
            else:
                st.error("User exists")

# ---------------- DASHBOARD ----------------
def dashboard():
    st.title("⚡ Smart Electricity Consumption Analysis")

    col1,col2,col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="card">
            <img src="https://images.unsplash.com/photo-1559305616-3f99cd43e353">
            <h4>Track Usage</h4>
            <p>Monitor daily electricity consumption</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="card">
            <img src="https://images.unsplash.com/photo-1581092918056-0c4c3acd3789">
            <h4>Analyze Trends</h4>
            <p>Visualize patterns with charts</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="card">
            <img src="https://images.unsplash.com/photo-1509395176047-4a66953fd231">
            <h4>AI Prediction</h4>
            <p>Forecast future consumption</p>
        </div>
        """, unsafe_allow_html=True)

# ---------------- INPUT ----------------
def input_page():
    st.header("📥 Enter Data")

    d=st.date_input("Date",datetime.today())
    u=st.number_input("Units",min_value=0.0)

    if st.button("Add"):
        new=pd.DataFrame([[d,u]],columns=["Date","Usage"])
        st.session_state.df=pd.concat([st.session_state.df,new],ignore_index=True)

    st.dataframe(st.session_state.df)

# ---------------- ANALYSIS ----------------
def analysis():
    st.header("📊 Analysis")

    df=st.session_state.df
    if df.empty:
        st.warning("No data")
        return

    df["Date"]=pd.to_datetime(df["Date"])

    total=df["Usage"].sum()
    avg=df["Usage"].mean()
    cost=total*COST_PER_KWH
    co2=total*CO2_PER_KWH
    peak=df.loc[df["Usage"].idxmax()]

    st.metric("Total Usage", f"{total:.2f} kWh")
    st.metric("Cost", f"₹{cost:.2f}")
    st.metric("Carbon", f"{co2:.2f} kg")
    st.metric("Peak Usage", f"{peak['Usage']} kWh on {peak['Date']}")

    fig=px.line(df,x="Date",y="Usage",markers=True)
    st.plotly_chart(fig,use_container_width=True)

# ---------------- PREDICTION ----------------
def prediction():
    st.header("🔮 Prediction")

    st.image("https://images.unsplash.com/photo-1451187580459-43490279c0fa",
             use_container_width=True)

    df=st.session_state.df
    if len(df)<2:
        st.warning("Need more data")
        return

    df["t"]=np.arange(len(df))
    coef=np.polyfit(df["t"],df["Usage"],1)

    future=[df["t"].max()+i for i in range(1,8)]
    preds=[coef[0]*t+coef[1] for t in future]

    dates=[df["Date"].max()+timedelta(days=i) for i in range(1,8)]

    fig=px.line()
    fig.add_scatter(x=df["Date"],y=df["Usage"],name="Actual")
    fig.add_scatter(x=dates,y=preds,name="Prediction")

    st.plotly_chart(fig,use_container_width=True)

# ---------------- SUGGESTIONS ----------------
def suggestions():
    st.header("💡 Smart Energy Suggestions")

    df = st.session_state.df
    if df.empty:
        st.warning("No data available")
        return

    avg = df["Usage"].mean()
    peak = df["Usage"].max()
    total = df["Usage"].sum()

    st.markdown("### 🌱 Personalized Energy Optimization Tips")

    # ---------- CARD 1 ----------
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("""
        <div class="card">
            <img src="https://images.unsplash.com/photo-1584277261846-c6a1672ed979">
            <h4>Energy Efficient Appliances</h4>
            <p>Use 5-star rated devices to reduce electricity consumption and long-term cost.</p>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="card">
            <img src="https://images.unsplash.com/photo-1521207418485-99c705420785">
            <h4>Off-Peak Usage</h4>
            <p>Run heavy appliances during night hours to reduce grid load and bill cost.</p>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown("""
        <div class="card">
            <img src="https://images.unsplash.com/photo-1592833159155-c62df1b65634">
            <h4>Solar Energy Adoption</h4>
            <p>Install solar panels to significantly reduce dependency on grid electricity.</p>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    # ---------- CARD 2 ----------
    c4, c5, c6 = st.columns(3)

    with c4:
        st.markdown("""
        <div class="card">
            <img src="https://images.unsplash.com/photo-1508514177221-188b1cf16e9d">
            <h4>Reduce Peak Load</h4>
            <p>Avoid running multiple heavy appliances together to prevent usage spikes.</p>
        </div>
        """, unsafe_allow_html=True)

    with c5:
        st.markdown("""
        <div class="card">
            <img src="https://images.unsplash.com/photo-1559305616-3f99cd43e353">
            <h4>Monitor Daily Usage</h4>
            <p>Track daily consumption patterns to identify and reduce unnecessary usage.</p>
        </div>
        """, unsafe_allow_html=True)

    with c6:
        st.markdown("""
        <div class="card">
            <img src="https://images.unsplash.com/photo-1509395176047-4a66953fd231">
            <h4>Switch to LED Lighting</h4>
            <p>LED lights consume far less power compared to traditional bulbs.</p>
        </div>
        """, unsafe_allow_html=True)

# ---------------- REPORT ----------------
def report():
    st.header("📄 Download Report")

    st.image("https://images.unsplash.com/photo-1554224155-6726b3ff858f",
             use_container_width=True)

    df=st.session_state.df
    if df.empty: return

    df["Cost"]=df["Usage"]*COST_PER_KWH
    df["CO2"]=df["Usage"]*CO2_PER_KWH

    st.download_button("Download CSV",df.to_csv(index=False),"report.csv")

# ---------------- MAIN ----------------
if not st.session_state.login:
    login()
else:
    page=st.sidebar.radio("Menu",
        ["Dashboard","Input","Analysis","Prediction","Suggestions","Report"])

    if page=="Dashboard":
        dashboard()
    elif page=="Input":
        input_page()
    elif page=="Analysis":
        analysis()
    elif page=="Prediction":
        prediction()
    elif page=="Suggestions":
        suggestions()
    elif page=="Report":
        report()

    if st.sidebar.button("Logout"):
        st.session_state.login=False
        st.rerun()
