import streamlit as st
import sqlite3
import pandas as pd

conn = sqlite3.connect("data.db", check_same_thread=False)
c = conn.cursor()

# ================= DATABASE =================
c.execute("CREATE TABLE IF NOT EXISTS projects (id INTEGER PRIMARY KEY, nama TEXT, client TEXT, nilai REAL, progress REAL)")
c.execute("CREATE TABLE IF NOT EXISTS rab (id INTEGER PRIMARY KEY, project_id INTEGER, item TEXT, total REAL)")
c.execute("CREATE TABLE IF NOT EXISTS progress (id INTEGER PRIMARY KEY, project_id INTEGER, tanggal TEXT, progress REAL)")
c.execute("CREATE TABLE IF NOT EXISTS pembelian (id INTEGER PRIMARY KEY, project_id INTEGER, material TEXT, total REAL)")
c.execute("CREATE TABLE IF NOT EXISTS termin (id INTEGER PRIMARY KEY, project_id INTEGER, termin INTEGER, nilai REAL, status TEXT)")
conn.commit()

st.set_page_config(layout="wide")
st.title("🧱 Dashboard Kontraktor")

menu = st.sidebar.selectbox("Menu", ["Dashboard", "Proyek", "RAB", "Progress", "Pembelian", "Termin", "Cashflow"])

# ================= DASHBOARD =================
if menu == "Dashboard":
    st.subheader("Overview")

    df = pd.read_sql("SELECT * FROM projects", conn)

    if not df.empty:
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Proyek", len(df))
        col2.metric("Total Nilai", int(df["nilai"].sum()))
        col3.metric("Avg Progress", round(df["progress"].mean(), 2))

        st.dataframe(df)
    else:
        st.info("Belum ada proyek")

# ================= PROYEK =================
elif menu == "Proyek":
    st.subheader("Data Proyek")

    nama = st.text_input("Nama Proyek")
    client = st.text_input("Client")
    nilai = st.number_input("Nilai")

    if st.button("Simpan Proyek"):
        c.execute("INSERT INTO projects (nama, client, nilai, progress) VALUES (?, ?, ?, ?)",
                  (nama, client, nilai, 0))
        conn.commit()
        st.success("Berhasil ditambah")

    df = pd.read_sql("SELECT * FROM projects", conn)
    st.dataframe(df)

# ================= RAB =================
elif menu == "RAB":
    st.subheader("RAB")

    projects = pd.read_sql("SELECT * FROM projects", conn)
    if projects.empty:
        st.warning("Buat proyek dulu")
    else:
        project_id = st.selectbox("Pilih Proyek", projects["id"])

        item = st.text_input("Item")
        total = st.number_input("Total")

        if st.button("Tambah RAB"):
            c.execute("INSERT INTO rab (project_id, item, total) VALUES (?, ?, ?)",
                      (project_id, item, total))
            conn.commit()
            st.success("RAB ditambah")

        df = pd.read_sql(f"SELECT * FROM rab WHERE project_id={project_id}", conn)
        st.dataframe(df)

# ================= PROGRESS =================
elif menu == "Progress":
    st.subheader("Progress")

    projects = pd.read_sql("SELECT * FROM projects", conn)
    if projects.empty:
        st.warning("Buat proyek dulu")
    else:
        project_id = st.selectbox("Pilih Proyek", projects["id"])

        tanggal = st.date_input("Tanggal")
        prog = st.slider("Progress (%)", 0, 100)

        if st.button("Update Progress"):
            c.execute("INSERT INTO progress (project_id, tanggal, progress) VALUES (?, ?, ?)",
                      (project_id, str(tanggal), prog))
            c.execute("UPDATE projects SET progress=? WHERE id=?", (prog, project_id))
            conn.commit()
            st.success("Progress diupdate")

        df = pd.read_sql(f"SELECT * FROM progress WHERE project_id={project_id}", conn)
        if not df.empty:
            st.line_chart(df["progress"])

# ================= PEMBELIAN =================
elif menu == "Pembelian":
    st.subheader("Pembelian")

    projects = pd.read_sql("SELECT * FROM projects", conn)
    if projects.empty:
        st.warning("Buat proyek dulu")
    else:
        project_id = st.selectbox("Pilih Proyek", projects["id"])

        material = st.text_input("Material")
        total = st.number_input("Total")

        if st.button("Tambah Pembelian"):
            c.execute("INSERT INTO pembelian (project_id, material, total) VALUES (?, ?, ?)",
                      (project_id, material, total))
            conn.commit()
            st.success("Berhasil")

        df = pd.read_sql(f"SELECT * FROM pembelian WHERE project_id={project_id}", conn)
        st.dataframe(df)

# ================= TERMIN =================
elif menu == "Termin":
    st.subheader("Termin")

    projects = pd.read_sql("SELECT * FROM projects", conn)
    if projects.empty:
        st.warning("Buat proyek dulu")
    else:
        project_id = st.selectbox("Pilih Proyek", projects["id"])

        termin = st.number_input("Termin ke-", 1)
        nilai = st.number_input("Nilai")
        status = st.selectbox("Status", ["Pending", "Lunas"])

        if st.button("Tambah Termin"):
            c.execute("INSERT INTO termin (project_id, termin, nilai, status) VALUES (?, ?, ?, ?)",
                      (project_id, termin, nilai, status))
            conn.commit()
            st.success("Berhasil")

        df = pd.read_sql(f"SELECT * FROM termin WHERE project_id={project_id}", conn)
        st.dataframe(df)

# ================= CASHFLOW =================
elif menu == "Cashflow":
    st.subheader("Cashflow")

    pemasukan = pd.read_sql("SELECT SUM(nilai) as total FROM termin WHERE status='Lunas'", conn)
    pengeluaran = pd.read_sql("SELECT SUM(total) as total FROM pembelian", conn)

    in_val = pemasukan["total"][0] if pemasukan["total"][0] else 0
    out_val = pengeluaran["total"][0] if pengeluaran["total"][0] else 0

    st.metric("Total Masuk", int(in_val))
    st.metric("Total Keluar", int(out_val))
    st.metric("Saldo", int(in_val - out_val))
