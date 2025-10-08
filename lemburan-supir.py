import streamlit as st
import pandas as pd
from datetime import datetime
import os

# ------------------------------
# Konfigurasi dasar
# ------------------------------
st.set_page_config(page_title="Form Lembur Supir", layout="centered")

st.title("🧾 Form Input Lembur Supir")

FILE_PATH = "data_lembur.csv"

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
# Tombol tambah hari lembur
# ------------------------------
if st.button("➕ Tambah Hari Lembur", use_container_width=True, key="tambah", 
             type="primary", help="Tambahkan baris lembur",
             ):
    st.session_state.lembur_data.append({"tanggal": datetime.today(), "jam": 0.0})

# ------------------------------
# Input tanggal & jam
# ------------------------------
for i, data in enumerate(st.session_state.lembur_data):
    col1, col2, col3 = st.columns([2, 1, 0.3])
    with col1:
        tanggal = st.date_input(f"Tanggal {i+1}", value=data["tanggal"], key=f"tanggal_{i}")
    with col2:
        jam = st.number_input(f"Jam {i+1}", min_value=0.0, step=0.5, key=f"jam_{i}")
    with col3:
        st.markdown(
            f"""
            <div style="text-align:center;">
                <button style="border:none;background:none;font-size:20px;cursor:pointer;color:#444;"
                onclick="window.parent.postMessage({{'delete_index': {i}}}, '*')">❌</button>
            </div>
            """,
            unsafe_allow_html=True
        )

# Handle hapus via JS event
delete_index = st.experimental_get_query_params().get("delete_index", [None])[0]
if delete_index is not None and delete_index.isdigit():
    idx = int(delete_index)
    if 0 <= idx < len(st.session_state.lembur_data):
        st.session_state.lembur_data.pop(idx)
        st.rerun()

# ------------------------------
# Tombol selesai
# ------------------------------
if st.button("✅ Selesai", use_container_width=True, key="selesai",
             type="primary"):
    if not st.session_state.lembur_data:
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
                "-",  # Nama supir dihapus
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
# Tombol khusus admin
# ------------------------------
if "show_admin" not in st.session_state:
    st.session_state.show_admin = False

if st.button("🔒 Khusus Admin", use_container_width=True):
    st.session_state.show_admin = not st.session_state.show_admin

if st.session_state.show_admin:
    st.subheader("Lihat Data (Admin Only)")
    admin_pass = st.text_input("Masukkan password admin:", type="password")
    if admin_pass == "admin123":
        if os.path.exists(FILE_PATH):
            df = pd.read_csv(FILE_PATH)
            st.dataframe(df)
        else:
            st.warning("Belum ada data lembur tersimpan.")
    elif admin_pass:
        st.error("Password salah.")

# ------------------------------
# CSS custom warna tombol
# ------------------------------
st.markdown("""
<style>
div.stButton > button:first-child {
    border-radius: 10px;
    font-weight: bold;
    color: white;
    height: 3em;
}
button[kind="primary"][key="tambah"] {
    background-color: #F0C42D !important;
}
button[kind="primary"][key="selesai"] {
    background-color: #65975E !important;
}
button[kind="primary"]:has(span:contains('Khusus Admin')) {
    background-color: #65975E !important;
}
</style>
""", unsafe_allow_html=True)
