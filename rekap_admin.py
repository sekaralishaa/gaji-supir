import streamlit as st
import pandas as pd
from datetime import datetime, time
import os

# ------------------------------
# Konfigurasi dasar
# ------------------------------
st.set_page_config(page_title="Form Lembur Supir", layout="centered")
st.title("🧾 Form Input Lembur Supir (Jam Masuk - Jam Keluar)")

FILE_PATH = "data_lembur.csv"
GAJI_POKOK = 5_500_000
GAJI_PER_JAM = GAJI_POKOK / 173
JAM_KERJA_NORMAL = 9.5  # jam kerja wajib

# ------------------------------
# Fungsi hitung lembur
# ------------------------------
def hitung_lembur(jenis_hari, jam_lembur):
    if jam_lembur <= 0:
        return 0
    
    if jenis_hari == "weekday":
        if jam_lembur <= 6:
            return jam_lembur * 1.5 * GAJI_PER_JAM
        else:
            return (6 * 1.5 * GAJI_PER_JAM) + ((jam_lembur - 6) * 2 * GAJI_PER_JAM)
    else:
        if jam_lembur <= 6:
            return jam_lembur * 2 * GAJI_PER_JAM
        else:
            return (6 * 2 * GAJI_PER_JAM) + ((jam_lembur - 6) * 3 * GAJI_PER_JAM)

# ------------------------------
# State data lembur
# ------------------------------
if "lembur_data" not in st.session_state:
    st.session_state.lembur_data = []


# ------------------------------
# Input tanggal + jam masuk + jam keluar
# ------------------------------
for i, data in enumerate(st.session_state.lembur_data):
    col1, col2, col3, col4 = st.columns([2, 1, 1, 0.3])

    with col1:
        tanggal = st.date_input(f"Tanggal {i+1}", value=data["tanggal"], key=f"tgl_{i}")

    with col2:
        jam_masuk = st.time_input(f"Jam Masuk {i+1}", value=data["jam_masuk"], key=f"in_{i}")

    with col3:
        jam_keluar = st.time_input(f"Jam Keluar {i+1}", value=data["jam_keluar"], key=f"out_{i}")

    with col4:
        if st.button("❌", key=f"hapus_{i}"):
            st.session_state.lembur_data.pop(i)
            st.rerun()


# ------------------------------
# Tombol utama
# ------------------------------
colA, colB = st.columns([1, 1])
with colA:
    tambah_btn = st.button("➕ Tambah Hari Lembur", use_container_width=True, key="add_btn")
with colB:
    selesai_btn = st.button("✅ Selesai", use_container_width=True, key="done_btn")


# ------------------------------
# Tambah data baru
# ------------------------------
if tambah_btn:
    st.session_state.lembur_data.append({
        "tanggal": datetime.today(),
        "jam_masuk": time(8, 0),
        "jam_keluar": time(17, 0)
    })
    st.rerun()


# ------------------------------
# Simpan data saat "Selesai"
# ------------------------------
if selesai_btn:
    if not st.session_state.lembur_data:
        st.warning("Belum ada data lembur yang dimasukkan.")
    else:
        hasil = []

        for i, data in enumerate(st.session_state.lembur_data):
            tgl = st.session_state[f"tgl_{i}"]
            jam_in = st.session_state[f"in_{i}"]
            jam_out = st.session_state[f"out_{i}"]

            # Hitung selisih jam
            dt_in = datetime.combine(tgl, jam_in)
            dt_out = datetime.combine(tgl, jam_out)

            total_jam = (dt_out - dt_in).total_seconds() / 3600
            jam_lembur = max(total_jam - JAM_KERJA_NORMAL, 0)

            # Tentukan jenis hari
            hari = tgl.strftime("%A")
            jenis = "weekend" if hari in ["Saturday", "Sunday"] else "weekday"

            # Hitung total lembur
            total_rp = hitung_lembur(jenis, jam_lembur)

            hasil.append([
                "-",  # Nama supir dihapus
                tgl.strftime("%d/%m/%Y"),
                hari,
                jenis,
                round(total_jam, 2),
                round(jam_lembur, 2),
                round(total_rp, 0),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ])

        df_new = pd.DataFrame(hasil, columns=[
            "Nama Supir", "Tanggal", "Hari", "Jenis Hari",
            "Total Jam Kerja", "Jam Lembur",
            "Total Lembur (Rp)", "Waktu Input"
        ])

        if os.path.exists(FILE_PATH):
            df_new.to_csv(FILE_PATH, mode="a", index=False, header=False)
        else:
            df_new.to_csv(FILE_PATH, index=False)

        st.success("✅ Data berhasil disimpan!")
        st.session_state.lembur_data = []
