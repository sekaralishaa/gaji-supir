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
JAM_KERJA_NORMAL = 9.5  # jam kerja wajib (weekday)

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
    else:  # weekend
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

    col1, col2, col3, col4 = st.columns([2, 1.2, 1.2, 0.3])

    with col1:
        tanggal = st.date_input(
            f"Tanggal {i+1}",
            value=data["tanggal"],
            key=f"tgl_{i}"
        )

    with col2:
        jam_masuk_str = st.text_input(
            f"Jam Masuk {i+1} (format 06:00)",
            value=data["jam_masuk"].strftime("%H:%M"),
            key=f"in_{i}"
        )

    with col3:
        jam_keluar_str = st.text_input(
            f"Jam Keluar {i+1} (format 23:00)",
            value=data["jam_keluar"].strftime("%H:%M"),
            key=f"out_{i}"
        )

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
# Simpan data ketika klik "Selesai"
# ------------------------------
if selesai_btn:
    if not st.session_state.lembur_data:
        st.warning("Belum ada data lembur yang dimasukkan.")
    else:
        hasil = []

        for i, data in enumerate(st.session_state.lembur_data):

            tgl = st.session_state[f"tgl_{i}"]
            jam_in = datetime.strptime(st.session_state[f"in_{i}"], "%H:%M").time()
            jam_out = datetime.strptime(st.session_state[f"out_{i}"], "%H:%M").time()

            dt_in = datetime.combine(tgl, jam_in)
            dt_out = datetime.combine(tgl, jam_out)

            total_jam = (dt_out - dt_in).total_seconds() / 3600

            # Tentukan hari & jenis hari (weekday / weekend)
            hari = tgl.strftime("%A")
            jenis = "weekend" if hari in ["Saturday", "Sunday"] else "weekday"

            # LOGIKA BARU:
            # - weekday  : lembur = total_jam - 9.5 (min 0)
            # - weekend  : semua jam dihitung lembur
            if jenis == "weekend":
                jam_lembur = total_jam
            else:
                jam_lembur = max(total_jam - JAM_KERJA_NORMAL, 0)

            total_rp = hitung_lembur(jenis, jam_lembur)

            hasil.append([
                "-",                                      # Nama Supir
                tgl.strftime("%d/%m/%Y"),                 # Tanggal
                hari,                                    # Hari
                jenis,                                   # Jenis Hari
                jam_in.strftime("%H:%M"),                # Jam Masuk
                jam_out.strftime("%H:%M"),               # Jam Keluar
                round(total_jam, 2),                     # Total Jam Kerja
                round(jam_lembur, 2),                    # Jam Lembur
                round(total_rp, 0),                      # Total Lembur (Rp)
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Waktu Input
            ])

        df_new = pd.DataFrame(hasil, columns=[
            "Nama Supir",
            "Tanggal",
            "Hari",
            "Jenis Hari",
            "Jam Masuk",
            "Jam Keluar",
            "Total Jam Kerja",
            "Jam Lembur",
            "Total Lembur (Rp)",
            "Waktu Input"
        ])

        if os.path.exists(FILE_PATH):
            df_new.to_csv(FILE_PATH, mode="a", index=False, header=False)
        else:
            df_new.to_csv(FILE_PATH, index=False)

        st.success("✅ Data berhasil disimpan!")
        st.session_state.lembur_data = []

# ------------------------------
# AREA ADMIN
# ------------------------------
st.markdown("---")

if "show_admin" not in st.session_state:
    st.session_state.show_admin = False

if st.button("🔒 Khusus Admin", key="admin_btn"):
    st.session_state.show_admin = not st.session_state.show_admin

if st.session_state.show_admin:

    st.subheader("📊 Lihat Data (Admin Only)")
    password = st.text_input("Masukkan password admin:", type="password")

    if password == "admin123":

        if os.path.exists(FILE_PATH):

            df_show = pd.read_csv(FILE_PATH)
            st.write("### Semua Data Lembur")

            # Baris data + tombol hapus baris
            for i in range(len(df_show)):
                cols = st.columns([6, 1])

                with cols[0]:
                    row = df_show.iloc[i]
                    st.write(
                        f"**{row['Nama Supir']}** — {row['Tanggal']} "
                        f"({row['Hari']}, {row['Jenis Hari']}) "
                        f"🕒 {row['Jam Masuk']} - {row['Jam Keluar']} | "
                        f"Lembur: {row['Jam Lembur']} jam | "
                        f"Total: Rp{int(row['Total Lembur (Rp)']):,}".replace(",", ".")
                    )

                with cols[1]:
                    if st.button("❌", key=f"del_row_{i}"):
                        df_show = df_show.drop(index=i).reset_index(drop=True)
                        df_show.to_csv(FILE_PATH, index=False)
                        st.success("Baris berhasil dihapus.")
                        st.rerun()

            st.markdown("---")

            # Tombol Hapus Semua Data
            st.warning("⚠ Menghapus semua data tidak bisa dibatalkan.")
            if st.button("🗑 Hapus Semua Data", key="hapus_semua"):
                os.remove(FILE_PATH)
                st.success("Data berhasil dihapus seluruhnya!")
                st.rerun()

            # Rekap Bulanan
            df_show['Bulan'] = pd.to_datetime(df_show['Tanggal'], format="%d/%m/%Y").dt.strftime('%B %Y')
            rekap = df_show.groupby(['Nama Supir', 'Bulan'])['Total Lembur (Rp)'].sum().reset_index()
            rekap["Total Lembur (Rp)"] = rekap["Total Lembur (Rp)"].apply(
                lambda x: f"Rp{int(x):,}".replace(",", ".")
            )

            st.subheader("💰 Rekap Total Lembur per Bulan")
            st.dataframe(rekap, use_container_width=True)

        else:
            st.warning("Belum ada data lembur yang tersimpan.")

    elif password != "":
        st.error("Password salah.")
