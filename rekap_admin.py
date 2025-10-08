# rekap_admin.py
import streamlit as st
import pandas as pd
import os

FILE_PATH = "data_lembur supir.csv"

st.set_page_config(page_title="Rekap Lembur Bulanan", layout="centered")
st.title("📊 Rekap Total Lembur per Bulan")

if os.path.exists(FILE_PATH):
    df = pd.read_csv(FILE_PATH)
    df['Bulan'] = pd.to_datetime(df['Tanggal'], format="%d/%m/%Y").dt.strftime('%B %Y')
    rekap = df.groupby(['Nama Supir', 'Bulan'])['Total Lembur (Rp)'].sum().reset_index()

    st.dataframe(rekap)

    nama_filter = st.selectbox("Pilih Supir:", ["Semua"] + sorted(df["Nama Supir"].unique().tolist()))
    if nama_filter != "Semua":
        st.write(rekap[rekap["Nama Supir"] == nama_filter])
else:
    st.warning("Belum ada data lembur tersimpan.")
