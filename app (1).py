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
        text-align: left;
        margin-top: 0px;
        margin-bottom: 2px;
    }
    .sub-header {
        color: #DAA520;
        font-family: 'Trebuchet MS', sans-serif;
        text-align: left;
        font-size: 1.15rem;
        margin-top: 0px;
        margin-bottom: 10px;
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

# Header Dashboard (Logo dan Judul Sejajar)
col_header_logo, col_header_title = st.columns([1, 8])

with col_header_logo:
    # Sedikit spacer atas agar logo sejajar dengan garis tengah judul
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    if os.path.exists("logo.png"):
        st.image("logo.png", width=110, use_container_width=False)
    else:
        st.markdown("<h1 style='text-align: center; font-size: 4rem; margin: 0;'>🏫</h1>", unsafe_allow_html=True)

with col_header_title:
    # Sedikit spacer atas agar judul sejajar dengan logo
    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
    st.markdown("<h1 class='main-header'>TRACER STUDY ALUMNI SMAN 2 SUKATANI</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Sistem Pemantauan Perkembangan Karier, Perguruan Tinggi, dan Kewirausahaan Alumni</p>", unsafe_allow_html=True)

# --- SIDEBAR: REFRESH DATA ---
st.sidebar.markdown("## ⚙️ Pembaruan Data")

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

        # --- REKAP TABEL UNIVERSITAS (FULL WIDTH / UJUNG KE UJUNG) ---
        kuliah_only_all = df_filtered[
            (df_filtered["Karier"] == "KULIAH") & 
            (~df_filtered["Universitas/Instansi/Perusahaan"].isin(["-", "_", "secret", ""]))
        ]
        if len(kuliah_only_all) > 0:
            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("📋 Rekap Tabel Jumlah Siswa per Universitas")
            univ_counts_all = kuliah_only_all["Universitas/Instansi/Perusahaan"].value_counts().reset_index()
            univ_counts_all.columns = ["Universitas", "Jumlah Alumni"]
            
            total_kuliah_valid_all = univ_counts_all["Jumlah Alumni"].sum()
            univ_counts_all["Persentase"] = (univ_counts_all["Jumlah Alumni"] / total_kuliah_valid_all) * 100
            
            rekap_univ = univ_counts_all.copy()
            rekap_univ["Persentase"] = rekap_univ["Persentase"].map("{:.1f}%".format)
            
            st.dataframe(
                rekap_univ,
                use_container_width=True,
                height=280,
                column_config={
                    "Universitas": st.column_config.TextColumn("Nama Universitas / Perguruan Tinggi", width="large"),
                    "Jumlah Alumni": st.column_config.NumberColumn("Jumlah Alumni", format="%d orang", width="small"),
                    "Persentase": st.column_config.TextColumn("Persentase dari Total Kuliah", width="small")
                },
                hide_index=True
            )

    # --- PENCARIAN PROFIL DETAIL ALUMNI (MENGGANTIKAN TABEL) ---
    st.markdown("### 🔍 Hasil Pencarian Detail Alumni")

    if search_name:
        # Cari data berdasarkan text input Nama
        matches = df_filtered[df_filtered["Nama"].str.contains(search_name, case=False, na=False)]
        
        if len(matches) == 0:
            st.warning("⚠️ Tidak ditemukan data alumni yang cocok dengan kata kunci nama tersebut.")
        elif len(matches) > 3:
            st.info(f"💡 Ditemukan {len(matches)} nama alumni yang cocok. Silakan pilih salah satu nama di bawah ini untuk melihat profil lengkap:")
            selected_alumni = st.selectbox("Pilih Alumni:", ["-- Pilih Alumni --"] + sorted(matches["Nama"].unique().tolist()))
            if selected_alumni != "-- Pilih Alumni --":
                row = matches[matches["Nama"] == selected_alumni].iloc[0]
                st.markdown(f"""
                <div style="background-color: #fcfcfc; padding: 20px; border-radius: 12px; border-left: 5px solid #8B0000; box-shadow: 0 4px 10px rgba(0,0,0,0.05); margin-top: 15px;">
                    <h3 style="color: #8B0000; margin-top: 0; margin-bottom: 15px; font-family: sans-serif;">🎓 PROFIL LENGKAP ALUMNI</h3>
                    <table style="width: 100%; border-collapse: collapse; font-size: 1.05rem;">
                        <tr style="border-bottom: 1px solid #eee;"><td style="padding: 10px 0; font-weight: bold; width: 35%; color: #555;">Nama Lengkap</td><td style="padding: 10px 0; font-weight: bold; color: #8B0000;">{row['Nama']}</td></tr>
                        <tr style="border-bottom: 1px solid #eee;"><td style="padding: 10px 0; font-weight: bold; color: #555;">Kelas Terakhir</td><td style="padding: 10px 0;">{row['Kelas']}</td></tr>
                        <tr style="border-bottom: 1px solid #eee;"><td style="padding: 10px 0; font-weight: bold; color: #555;">Tahun Lulus</td><td style="padding: 10px 0;">{row['Tahun Lulus']}</td></tr>
                        <tr style="border-bottom: 1px solid #eee;"><td style="padding: 10px 0; font-weight: bold; color: #555;">Status Karier</td><td style="padding: 10px 0;"><span style="background-color: #8B0000; color: white; padding: 4px 10px; border-radius: 4px; font-weight: bold; font-size: 0.85rem;">{row['Karier']}</span></td></tr>
                        <tr style="border-bottom: 1px solid #eee;"><td style="padding: 10px 0; font-weight: bold; color: #555;">Universitas / Instansi / Perusahaan</td><td style="padding: 10px 0;">{row['Universitas/Instansi/Perusahaan']}</td></tr>
                        <tr style="border-bottom: 1px solid #eee;"><td style="padding: 10px 0; font-weight: bold; color: #555;">Program Studi / Jurusan</td><td style="padding: 10px 0;">{row['Jurusan']}</td></tr>
                    </table>
                </div>
                """, unsafe_allow_html=True)
        else:
            # Jika matches <= 3, tampilkan langsung dalam bentuk kartu profil yang rapi
            for _, row in matches.iterrows():
                st.markdown(f"""
                <div style="background-color: #fcfcfc; padding: 20px; border-radius: 12px; border-left: 5px solid #8B0000; box-shadow: 0 4px 10px rgba(0,0,0,0.05); margin-bottom: 15px;">
                    <h3 style="color: #8B0000; margin-top: 0; margin-bottom: 15px; font-family: sans-serif;">👤 PROFIL ALUMNI</h3>
                    <table style="width: 100%; border-collapse: collapse; font-size: 1.05rem;">
                        <tr style="border-bottom: 1px solid #eee;"><td style="padding: 10px 0; font-weight: bold; width: 35%; color: #555;">Nama Lengkap</td><td style="padding: 10px 0; font-weight: bold; color: #8B0000;">{row['Nama']}</td></tr>
                        <tr style="border-bottom: 1px solid #eee;"><td style="padding: 10px 0; font-weight: bold; color: #555;">Kelas Terakhir</td><td style="padding: 10px 0;">{row['Kelas']}</td></tr>
                        <tr style="border-bottom: 1px solid #eee;"><td style="padding: 10px 0; font-weight: bold; color: #555;">Tahun Lulus</td><td style="padding: 10px 0;">{row['Tahun Lulus']}</td></tr>
                        <tr style="border-bottom: 1px solid #eee;"><td style="padding: 10px 0; font-weight: bold; color: #555;">Status Karier</td><td style="padding: 10px 0;"><span style="background-color: #DAA520; color: white; padding: 4px 10px; border-radius: 4px; font-weight: bold; font-size: 0.85rem;">{row['Karier']}</span></td></tr>
                        <tr style="border-bottom: 1px solid #eee;"><td style="padding: 10px 0; font-weight: bold; color: #555;">Universitas / Instansi / Perusahaan</td><td style="padding: 10px 0;">{row['Universitas/Instansi/Perusahaan']}</td></tr>
                        <tr style="border-bottom: 1px solid #eee;"><td style="padding: 10px 0; font-weight: bold; color: #555;">Program Studi / Jurusan</td><td style="padding: 10px 0;">{row['Jurusan']}</td></tr>
                    </table>
                </div>
                """, unsafe_allow_html=True)
    else:
        # Tampilan default saat user belum mencari nama
        st.info("💡 **Petunjuk**: Masukkan kata kunci nama alumni di kolom pencarian **'Cari Nama Alumni'** pada sidebar sebelah kiri untuk melakukan pencarian profil secara detail.")
        st.markdown("""
        <div style="background-color: #fff9e6; border-left: 5px solid #DAA520; padding: 15px; border-radius: 8px; margin-top: 10px;">
            <p style="color: #7a5c00; margin: 0; font-size: 0.95rem;">
                🔒 <b>Proteksi Privasi Data Alumni</b>: Sesuai dengan kesepakatan privasi, tabel berisi seluruh data alumni dari SMAN 2 Sukatani tidak lagi ditampilkan secara terbuka. Silakan gunakan bar pencarian nama untuk melihat profil alumni secara mandiri.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <hr style="border:0.5px solid #eaeaea;">
    <p style="text-align:center; color:gray; font-size:0.8rem;">
        Dashboard Tracer Study SMAN 2 Sukatani © 2026. Terkoneksi otomatis dengan Google Sheets secara real-time.
    </p>
    """, unsafe_allow_html=True)
else:
    st.info("Menunggu data dari Google Sheets terisi...")
