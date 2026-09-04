import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="Dashboard Tracer Study Alumni SMAN 2 Sukatani",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS untuk warna khas SMAN 2 Sukatani (Merah Maroon dan Emas/Kuning)
st.markdown("""
    <style>
    .main-header {
        color: #8B0000;
        font-family: 'Trebuchet MS', sans-serif;
        font-weight: bold;
        text-align: center;
        margin-bottom: 5px;
    }
    .sub-header {
        color: #DAA520;
        font-family: 'Trebuchet MS', sans-serif;
        text-align: center;
        font-size: 1.2rem;
        margin-bottom: 25px;
    }
    .card-kpi {
        background-color: #fcfcfc;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #8B0000;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
        text-align: center;
    }
    .card-kpi-title {
        color: #555;
        font-size: 0.9rem;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .card-kpi-val {
        color: #8B0000;
        font-size: 1.8rem;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Tautan Spreadsheet Google Sheets Alumni SMAN 2 Sukatani (Telah Dikonfigurasi)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1Zt24-BXfXXuvDR7j79BTJy1UdTrXfTgBI9kg8ok01t8/edit?usp=drive_link"

# Fungsi untuk mengonversi URL Google Sheets biasa menjadi format ekspor CSV langsung
def convert_google_sheet_url(url):
    try:
        if "docs.google.com/spreadsheets" in url:
            parts = url.split("/")
            sheet_id = parts[parts.index("d") + 1]
            return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
        return url
    except Exception:
        return url

# Memuat data secara dinamis dari Google Sheets (dengan Cache 10 Menit untuk Kecepatan Pemuatan)
@st.cache_data(ttl=600)
def load_data_from_sheets(url):
    csv_url = convert_google_sheet_url(url)
    return pd.read_csv(csv_url)

# Header Dashboard (Logo dan Judul)
col_logo_1, col_logo_2, col_logo_3 = st.columns([1, 2, 1])

with col_logo_2:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=140, use_container_width=False)
    else:
        st.markdown("<h1 style='text-align: center; font-size: 5rem;'>🏫</h1>", unsafe_allow_html=True)
        st.info("💡 **Tips untuk GitHub**: Unggah file `logo.png` ke repositori GitHub Anda bersama file ini agar logo resmi SMAN 2 Sukatani otomatis muncul!")

st.markdown("<h1 class='main-header'>TRACER STUDY ALUMNI SMAN 2 SUKATANI</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>Sistem Pemantauan Perkembangan Karier, Perguruan Tinggi, dan Kewirausahaan Alumni</p>", unsafe_allow_html=True)

# --- SIDEBAR: STATUS DATA & REFRESH ---
st.sidebar.markdown("## ⚙️ Status Koneksi")
st.sidebar.success("🔗 Terhubung langsung ke Google Sheets (Dinamis)")

# Tombol Refresh Data untuk Membersihkan Cache Secara Instan
if st.sidebar.button("🔄 Perbarui Data Sekarang"):
    st.cache_data.clear()
    st.rerun()

load_success = False
df_raw = None

# Memuat Data Langsung dari Google Drive
try:
    df_raw = load_data_from_sheets(SHEET_URL)
    load_success = True
except Exception as e:
    st.error("❌ **Gagal Memuat Data dari Google Sheets!**")
    st.markdown(f"""
    **Kemungkinan Penyebab & Cara Mengatasi:**
    1. **Akses Berbagi Belum Dibuka**: 
       Buka Spreadsheet Google Drive Anda -> Klik **Bagikan (Share)** -> Ubah status akses umum menjadi **"Siapa saja yang memiliki link dapat melihat"** (*Anyone with link can view*).
    2. **Koneksi Jaringan**: 
       Pastikan server Streamlit dan jaringan Anda stabil.
    
    *Detail Error Teknis:* `{e}`
    """)

# --- DATA PREPROCESSING & STANDARDIZATION ---
if load_success and df_raw is not None:
    # Pemetaan kolom sesuai spesifikasi yang diminta
    kolom_map = {
        "NAMA LENGKAP": "Nama",
        "KELAS": "Kelas",
        "KARIER": "Karier",
        "UNIVERSITAS/INSTANSI/PERUSAHAAN": "Universitas/Instansi/Perusahaan",
        "JURUSAN": "Jurusan",
        "TAHUN LULUS": "Tahun Lulus"
    }
    
    # Menyamakan nama kolom dari spreadsheet (case insensitive matching)
    df_columns = {col.upper().strip(): col for col in df_raw.columns}
    clean_cols = {}
    for k_key, v_val in kolom_map.items():
        if k_key in df_columns:
            clean_cols[df_columns[k_key]] = v_val
            
    df = df_raw.rename(columns=clean_cols)
    
    # Ambil hanya kolom yang dibutuhkan, buat default kosong jika kolom tidak ditemukan
    keep_cols = list(kolom_map.values())
    for col in keep_cols:
        if col not in df.columns:
            df[col] = "-"
            
    df = df[keep_cols]
    
    # Standarisasi nilai Karier
    df["Karier"] = df["Karier"].astype(str).str.upper().str.strip()
    df["Karier"] = df["Karier"].replace({
        "BEBEKERJA": "BEKERJA",
        "KERJA": "BEKERJA",
        "WIRASWASTA": "WIRAUSAHA",
        "MEMBANTU ORANG TUA": "WIRAUSAHA"
    })
    
    # Membersihkan karakter NaN atau sel kosong
    df = df.fillna("-")
    for col in df.columns:
        df[col] = df[col].astype(str).str.strip().replace({"nan": "-", "": "-"})
        
    # Pastikan format Tahun Lulus adalah angka bersih
    df["Tahun Lulus"] = pd.to_numeric(df["Tahun Lulus"], errors='coerce').fillna(0).astype(int)
    df = df[df["Tahun Lulus"] > 0] # Menyembunyikan baris kosong yang tidak valid

    # --- SIDEBAR: FILTER PENCARIAN ---
    st.sidebar.markdown("## 🔍 Filter Alumni")

    # Filter 1: Pencarian Nama Lengkap (Text Input)
    search_name = st.sidebar.text_input("Cari Nama Alumni:", "")

    # Filter 2: Tahun Lulus (Multiselect)
    list_tahun = sorted(df["Tahun Lulus"].unique().tolist(), reverse=True)
    selected_tahun = st.sidebar.multiselect("Tahun Lulus:", list_tahun, default=list_tahun)

    # Filter 3: Kelas (Multiselect)
    list_kelas = sorted(df["Kelas"].unique().tolist())
    selected_kelas = st.sidebar.multiselect("Kelas:", list_kelas, default=list_kelas)

    # Filter 4: Karier (Multiselect)
    list_karier = sorted(df["Karier"].unique().tolist())
    list_karier = [k for k in list_karier if k != "-"]
    selected_karier = st.sidebar.multiselect("Karier:", list_karier, default=list_karier)

    # Filter 5: Universitas/Instansi/Perusahaan (Multiselect)
    list_instansi = sorted([i for i in df["Universitas/Instansi/Perusahaan"].unique().tolist() if i not in ["-", "_", ""]])
    selected_instansi = st.sidebar.multiselect("Universitas/Instansi/Perusahaan:", list_instansi)

    # Filter 6: Jurusan (Multiselect)
    list_jurusan = sorted([j for j in df["Jurusan"].unique().tolist() if j not in ["-", "_", ""]])
    selected_jurusan = st.sidebar.multiselect("Jurusan Kuliah:", list_jurusan)

    # --- MEMULAI PENYARINGAN DATA ---
    df_filtered = df.copy()

    if search_name:
        df_filtered = df_filtered[df_filtered["Nama"].str.contains(search_name, case=False, na=False)]

    if selected_tahun:
        df_filtered = df_filtered[df_filtered["Tahun Lulus"].isin(selected_tahun)]

    if selected_kelas:
        df_filtered = df_filtered[df_filtered["Kelas"].isin(selected_kelas)]

    if selected_karier:
        df_filtered = df_filtered[df_filtered["Karier"].isin(selected_karier)]

    if selected_instansi:
        df_filtered = df_filtered[df_filtered["Universitas/Instansi/Perusahaan"].isin(selected_instansi)]

    if selected_jurusan:
        df_filtered = df_filtered[df_filtered["Jurusan"].isin(selected_jurusan)]

    # --- METRICS & KPI SECTION ---
    st.markdown("### 📊 Ringkasan Statistik Alumni")
    total_alumni = len(df_filtered)

    if total_alumni > 0:
        bekerja_count = len(df_filtered[df_filtered["Karier"] == "BEKERJA"])
        kuliah_count = len(df_filtered[df_filtered["Karier"] == "KULIAH"])
        wirausaha_count = len(df_filtered[df_filtered["Karier"] == "WIRAUSAHA"])
        
        pct_bekerja = (bekerja_count / total_alumni) * 100
        pct_kuliah = (kuliah_count / total_alumni) * 100
        pct_wirausaha = (wirausaha_count / total_alumni) * 100
        
        # Menampilkan Metric Cards secara horizontal
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
                <div class='card-kpi'>
                    <div class='card-kpi-title'>TOTAL ALUMNI TERFILTER</div>
                    <div class='card-kpi-val'>{total_alumni}</div>
                    <p style='color:gray; font-size:0.8rem; margin:0;'>Orang</p>
                </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
                <div class='card-kpi'>
                    <div class='card-kpi-title'>🎓 KULIAH</div>
                    <div class='card-kpi-val'>{pct_kuliah:.1f}%</div>
                    <p style='color:gray; font-size:0.8rem; margin:0;'>{kuliah_count} Alumni</p>
                </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
                <div class='card-kpi'>
                    <div class='card-kpi-title'>💼 BEKERJA</div>
                    <div class='card-kpi-val'>{pct_bekerja:.1f}%</div>
                    <p style='color:gray; font-size:0.8rem; margin:0;'>{bekerja_count} Alumni</p>
                </div>
            """, unsafe_allow_html=True)
        with col4:
            st.markdown(f"""
                <div class='card-kpi'>
                    <div class='card-kpi-title'>🚀 WIRAUSAHA</div>
                    <div class='card-kpi-val'>{pct_wirausaha:.1f}%</div>
                    <p style='color:gray; font-size:0.8rem; margin:0;'>{wirausaha_count} Alumni</p>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Tidak ada data alumni yang cocok dengan kriteria filter Anda.")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- CHARTS AND VISUALIZATION ---
    if total_alumni > 0:
        st.markdown("### 📈 Visualisasi Analisis")
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.subheader("Persentase Karier Alumni")
            karier_df = df_filtered["Karier"].value_counts().reset_index()
            karier_df.columns = ["Karier", "Jumlah"]
            
            fig_pie = px.pie(
                karier_df, 
                values="Jumlah", 
                names="Karier",
                color_discrete_sequence=["#8B0000", "#DAA520", "#32CD32", "#808080"],
                hole=0.4
            )
            fig_pie.update_layout(
                margin=dict(l=20, r=20, t=10, b=10),
                height=350,
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with col_chart2:
            st.subheader("Top Perguruan Tinggi / Universitas Tujuan")
            kuliah_only = df_filtered[
                (df_filtered["Karier"] == "KULIAH") & 
                (~df_filtered["Universitas/Instansi/Perusahaan"].isin(["-", "_", "secret", ""]))
            ]
            
            if len(kuliah_only) > 0:
                univ_counts = kuliah_only["Universitas/Instansi/Perusahaan"].value_counts().reset_index()
                univ_counts.columns = ["Universitas", "Jumlah Alumni"]
                
                total_kuliah_valid = univ_counts["Jumlah Alumni"].sum()
                univ_counts["Persentase"] = (univ_counts["Jumlah Alumni"] / total_kuliah_valid) * 100
                
                top_univ = univ_counts.head(8).sort_values(by="Jumlah Alumni", ascending=True)
                
                fig_bar = px.bar(
                    top_univ,
                    x="Jumlah Alumni",
                    y="Universitas",
                    orientation="h",
                    text=top_univ.apply(lambda row: f"{row['Jumlah Alumni']} orang ({row['Persentase']:.1f}%)", axis=1),
                    color_discrete_sequence=["#DAA520"]
                )
                fig_bar.update_layout(
                    margin=dict(l=20, r=20, t=10, b=10),
                    height=350,
                    xaxis_title="Jumlah Alumni",
                    yaxis_title=""
                )
                fig_bar.update_traces(textposition="inside")
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("Pilih kategori 'KULIAH' pada filter karier untuk melihat sebaran Universitas.")

    # --- DETAILED DATA TABLE AND DOWNLOAD ---
    st.markdown("### 📋 Tabel Data Alumni Terfilter")

    st.dataframe(
        df_filtered,
        use_container_width=True,
        column_config={
            "Nama": st.column_config.TextColumn("Nama Lengkap", width="medium"),
            "Kelas": st.column_config.TextColumn("Kelas", width="small"),
            "Karier": st.column_config.TextColumn("Status Karier", width="small"),
            "Universitas/Instansi/Perusahaan": st.column_config.TextColumn("Universitas / Instansi / Perusahaan", width="large"),
            "Jurusan": st.column_config.TextColumn("Program Studi / Jurusan", width="medium"),
            "Tahun Lulus": st.column_config.NumberColumn("Tahun Lulus", format="%d")
        }
    )

    st.markdown("<br>", unsafe_allow_html=True)
    csv_data = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Unduh Data Alumni (Format CSV)",
        data=csv_data,
        file_name="tracer_study_filtered_alumni.csv",
        mime="text/csv"
    )

    st.markdown("""
    <hr style="border:0.5px solid #eaeaea;">
    <p style="text-align:center; color:gray; font-size:0.8rem;">
        Dashboard Tracer Study SMAN 2 Sukatani © 2026. Terkoneksi otomatis dengan Google Sheets secara real-time.
    </p>
    """, unsafe_allow_html=True)
else:
    st.info("Menunggu data dari Google Sheets terisi...")
