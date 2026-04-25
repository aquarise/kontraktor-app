import streamlit as st
import sqlite3
import pandas as pd

conn = sqlite3.connect("data.db", check_same_thread=False)
c = conn.cursor()

c.execute("CREATE TABLE IF NOT EXISTS projects (id INTEGER PRIMARY KEY, nama TEXT, client TEXT, nilai REAL, progress REAL)")
conn.commit()

st.title("Dashboard Kontraktor")

menu = st.sidebar.selectbox("Menu", ["Dashboard", "Proyek"])

if menu == "Dashboard":
    df = pd.read_sql("SELECT * FROM projects", conn)
    st.write("Total Proyek:", len(df))
    st.dataframe(df)

elif menu == "Proyek":
    nama = st.text_input("Nama Proyek")
    client = st.text_input("Client")
    nilai = st.number_input("Nilai")

    if st.button("Simpan"):
        c.execute("INSERT INTO projects (nama, client, nilai, progress) VALUES (?, ?, ?, ?)", (nama, client, nilai, 0))
        conn.commit()
        st.success("Berhasil")

    df = pd.read_sql("SELECT * FROM projects", conn)
    st.dataframe(df)
