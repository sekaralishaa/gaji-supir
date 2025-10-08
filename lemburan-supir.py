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
# Fungsi hitung lembur
# ------------------------------
def hitung_lembur(jenis_hari, jam_lembur):
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
# Input user
# ------------------------------
nama_supir = st.text_input("Nama Supir")

if "lembur_data" not in st.session_state:
    st.session_state.lembur_data = []

st.subheader("Input Hari Lembur")

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
# Tombol di bagian bawah
# ------------------------------
colA, colB = st.columns([1, 1])

with colA:
    tambah_btn = st.button("➕ Tambah Hari Lembur", use_container_width=True, type="primary")
with colB:
    selesai_btn = st.button("✅ Selesai", use_container_width=True, type="primary")

# Styling tombol (warna hijau, tulisan putih tebal)
st.markdown("""
    <style>
    div.stButton > button:first-child {
        background-color: #28a745;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        border: none;
    }
    div.stButton > button:hover {
        background-color: #218838;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Tambah data baru kalau ditekan
if tambah_btn:
    st.session_state.lembur_data.append({"tanggal": datetime.today(), "jam": 0.0})
    st.rerun()

# ------------------------------
# Simpan data saat "Selesai"
# ------------------------------
if selesai_btn:
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

        if os.path.exists(FILE_PATH):
            df_baru.to_csv(FILE_PATH, mode="a", index=False, header=False)
        else:
            df_baru.to_csv(FILE_PATH, index=False)

        st.success("✅ Data berhasil dimasukkan!")
        st.session_state.lembur_data = []

# ------------------------------
# Area Admin tersembunyi
# ------------------------------
st.markdown("---")

if "show_admin" not in st.session_state:
    st.session_state.show_admin = False

# Tombol kecil untuk admin
if st.button("🔒 Khusus Admin"):
    st.session_state.show_admin = not st.session_state.show_admin

# Kalau ditekan baru muncul form password
if st.session_state.show_admin:
    st.subheader("📊 Lihat Data (Admin Only)")
    password = st.text_input("Masukkan password admin:", type="password")

    if password == "admin123":
        if os.path.exists(FILE_PATH):
            df_show = pd.read_csv(FILE_PATH)
            st.dataframe(df_show)
            # Tambahan: rekap total lembur per supir per bulan
            df_show['Bulan'] = pd.to_datetime(df_show['Tanggal'], format="%d/%m/%Y").dt.strftime('%B %Y')
            rekap = df_show.groupby(['Nama Supir', 'Bulan'])['Total Lembur (Rp)'].sum().reset_index()

            st.subheader("💰 Rekap Total Lembur per Bulan")
            st.dataframe(rekap)
        else:
            st.warning("Belum ada data lembur yang tersimpan.")
    elif password != "":
        st.error("Password salah.")


