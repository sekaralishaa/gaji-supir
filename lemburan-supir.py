import streamlit as st
import pandas as pd
from datetime import datetime
import os

# ------------------------------
# Konfigurasi dasar
# ------------------------------
st.set_page_config(page_title="Form Lembur Supir", layout="centered")
st.title("🧾 Form Input Lembur Supir")
st.caption("Pastikan semua informasi valid sebelum dikirim.")

# File penyimpanan
FILE_PATH = "data_lembur.csv"

# Gaji dasar
GAJI_POKOK = 5_500_000
GAJI_PER_JAM = GAJI_POKOK / 173

# ------------------------------
# Fungsi perhitungan lembur
# ------------------------------
def hitung_lembur(jenis_hari, jam_lembur):
    if jenis_hari == "weekday":
        if jam_lembur <= 6:
            return jam_lembur * 1.5 * GAJI_PER_JAM
        else:
            return (6 * 1.5 * GAJI_PER_JAM) + ((jam_lembur - 6) * 2 * GAJI_PER_JAM)
    else:  # weekend
        if jam_lembur <= 6:
            return jam_lembur * 2 * GAJI_PER_JAM
        else:
            return (6 * 2 * GAJI_PER_JAM) + ((jam_lembur - 6) * 3 * GAJI_PER_JAM)

# ------------------------------
# Input user
# ------------------------------
nama_supir = st.text_input("Nama Supir")

if "lembur_data" not in st.session_state:
    st.session_state.lembur_data = []

st.subheader("Input Hari Lembur")

# Tombol tambah hari lembur
if st.button("➕ Tambah Hari Lembur"):
    st.session_state.lembur_data.append({"tanggal": datetime.today(), "jam": 0.0})

# Tampilkan input tanggal & jam
for i, data in enumerate(st.session_state.lembur_data):
    col1, col2, col3 = st.columns([2, 1, 0.5])
    with col1:
        tanggal = st.date_input(f"Tanggal {i+1}", value=data["tanggal"], key=f"tanggal_{i}")
    with col2:
        jam = st.number_input(f"Jam {i+1}", min_value=0.0, step=0.5, key=f"jam_{i}")
    with col3:
        if st.button("🗑️", key=f"hapus_{i}"):
            st.session_state.lembur_data.pop(i)
            st.rerun()

# ------------------------------
# Saat tombol selesai ditekan
# ------------------------------
if st.button("✅ Selesai"):
    if not nama_supir:
        st.warning("Masukkan nama supir terlebih dahulu.")
    elif not st.session_state.lembur_data:
        st.warning("Belum ada data lembur yang dimasukkan.")
    else:
        hasil = []
        for i, data in enumerate(st.session_state.lembur_data):
            tgl = st.session_state[f"tanggal_{i}"]
            jam = st.session_state[f"jam_{i}"]
            hari = tgl.strftime("%A")
            jenis = "weekend" if hari in ["Saturday", "Sunday"] else "weekday"
            total = hitung_lembur(jenis, jam)
            hasil.append([
                nama_supir,
                tgl.strftime("%d/%m/%Y"),
                hari,
                jenis,
                jam,
                round(total, 0),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ])

        df_baru = pd.DataFrame(hasil, columns=[
            "Nama Supir", "Tanggal", "Hari", "Jenis Hari", "Jam Lembur", "Total Lembur (Rp)", "Waktu Input"
        ])

        # Simpan ke CSV (append mode)
        if os.path.exists(FILE_PATH):
            df_baru.to_csv(FILE_PATH, mode="a", index=False, header=False)
        else:
            df_baru.to_csv(FILE_PATH, index=False)

        st.success("✅ Data berhasil dimasukkan!")
        st.session_state.lembur_data = []
