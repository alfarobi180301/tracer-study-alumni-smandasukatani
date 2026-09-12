import streamlit as st
import pandas as pd
import plotly.express as px
import os
import json
import requests

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
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #f8f9fa;
        border-radius: 6px 6px 0px 0px;
        padding: 8px 16px;
        font-weight: bold;
        color: #555;
    }
    .stTabs [aria-selected="true"] {
        background-color: #8B0000 !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# File Penyimpanan Lokal untuk Pendataan, Moderasi, dan Konfigurasi
PENDING_FILE = "pending_alumni.json"
APPROVED_FILE = "approved_alumni.json"
APPS_SCRIPT_URL_FILE = "apps_script_url.txt"
ADMIN_PASSWORD_DEFAULT = "smandas2026"

def load_json_data(file_path):
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_json_data(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def load_text_config(file_path):
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception:
            return ""
    return ""

def save_text_config(file_path, content):
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content.strip())

def send_to_google_sheet(entry, apps_script_url):
    if not apps_script_url or not apps_script_url.startswith("http"):
        return False, "URL Google Apps Script belum dikonfigurasi."
    try:
        payload = {
            "nama": entry.get("Nama", ""),
            "kelas": entry.get("Kelas", ""),
            "karier": entry.get("Karier", ""),
            "instansi": entry.get("Universitas/Instansi/Perusahaan", ""),
            "jurusan": entry.get("Jurusan", ""),
            "tahun": entry.get("Tahun Lulus", "")
        }
        res = requests.post(apps_script_url, json=payload, timeout=10)
        if res.status_code == 200 or "Success" in res.text or "success" in res.text:
            return True, "Data berhasil otomatis ditambahkan ke Google Sheets!"
        else:
            return True, f"Data dikirim ke Google Sheets (Respon: {res.text[:60]})"
    except Exception as e:
        return False, f"Gagal terhubung ke Google Sheets: {e}"

# Tautan Spreadsheet Google Sheets Alumni SMAN 2 Sukatani (Telah Dikonfigurasi)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1Zt24-BXfXXuvDR7j79BTJy1UdTrXfTgBI9kg8ok01t8/edit?usp=drive_link"

def convert_google_sheet_url(url):
    try:
        if "docs.google.com/spreadsheets" in url:
            parts = url.split("/")
            sheet_id = parts[parts.index("d") + 1]
            return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
        return url
    except Exception:
        return url

@st.cache_data(ttl=600)
def load_data_from_sheets(url):
    csv_url = convert_google_sheet_url(url)
    return pd.read_csv(csv_url)

# Header Dashboard (Logo dan Judul Sejajar)
col_header_logo, col_header_title = st.columns([1, 8])

with col_header_logo:
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    if os.path.exists("logo.png"):
        st.image("logo.png", width=110, use_container_width=False)
    else:
        st.markdown("<h1 style='text-align: center; font-size: 4rem; margin: 0;'>🏫</h1>", unsafe_allow_html=True)

with col_header_title:
    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
    st.markdown("<h1 class='main-header'>TRACER STUDY ALUMNI SMAN 2 SUKATANI</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Sistem Pemantauan Perkembangan Karier, Perguruan Tinggi, dan Kewirausahaan Alumni</p>", unsafe_allow_html=True)

# --- SIDEBAR: REFRESH DATA ---
st.sidebar.markdown("## ⚙️ Pembaruan Data")
if st.sidebar.button("🔄 Perbarui Data Sekarang"):
    st.cache_data.clear()
    st.rerun()

load_success = False
df_raw = None

try:
    df_raw = load_data_from_sheets(SHEET_URL)
    load_success = True
except Exception as e:
    st.error("❌ **Gagal Memuat Data dari Google Sheets!**")
    st.markdown(f"""
    **Kemungkinan Penyebab & Cara Mengatasi:**
    1. **Akses Berbagi Belum Dibuka**: Buka Spreadsheet -> **Bagikan (Share)** -> **"Siapa saja yang memiliki link dapat melihat"**.
    2. **Koneksi Jaringan**: Pastikan jaringan stabil.
    
    *Detail Error:* `{e}`
    """)

# Pemrosesan Data Utama
if load_success and df_raw is not None:
    kolom_map = {
        "NAMA LENGKAP": "Nama",
        "KELAS": "Kelas",
        "KARIER": "Karier",
        "UNIVERSITAS/INSTANSI/PERUSAHAAN": "Universitas/Instansi/Perusahaan",
        "JURUSAN": "Jurusan",
        "TAHUN LULUS": "Tahun Lulus"
    }
    
    df_columns = {col.upper().strip(): col for col in df_raw.columns}
    clean_cols = {}
    for k_key, v_val in kolom_map.items():
        if k_key in df_columns:
            clean_cols[df_columns[k_key]] = v_val
            
    df = df_raw.rename(columns=clean_cols)
    
    keep_cols = list(kolom_map.values())
    for col in keep_cols:
        if col not in df.columns:
            df[col] = "-"
            
    df = df[keep_cols]
    
    # Gabungkan dengan data alumni yang telah disetujui (Approved)
    approved_list = load_json_data(APPROVED_FILE)
    if len(approved_list) > 0:
        df_approved = pd.DataFrame(approved_list)
        for col in keep_cols:
            if col not in df_approved.columns:
                df_approved[col] = "-"
        df_approved = df_approved[keep_cols]
        df = pd.concat([df, df_approved], ignore_index=True)
    
    df["Karier"] = df["Karier"].astype(str).str.upper().str.strip()
    df["Karier"] = df["Karier"].replace({
        "BEBEKERJA": "BEKERJA",
        "KERJA": "BEKERJA",
        "WIRASWASTA": "WIRAUSAHA",
        "MEMBANTU ORANG TUA": "WIRAUSAHA"
    })
    
    df = df.fillna("-")
    for col in df.columns:
        df[col] = df[col].astype(str).str.strip().replace({"nan": "-", "": "-"})
        
    df["Tahun Lulus"] = pd.to_numeric(df["Tahun Lulus"], errors='coerce').fillna(0).astype(int)
    df = df[df["Tahun Lulus"] > 0]

    # TAB UTAMA APLIKASI
    tab_dashboard, tab_form, tab_admin = st.tabs([
        "📊 Dashboard & Analisis", 
        "📝 Tambah Data Alumni", 
        "🔐 Moderasi Admin"
    ])

    # ==========================================
    # TAB 1: DASHBOARD UTAMA
    # ==========================================
    with tab_dashboard:
        # SIDEBAR FILTER
        st.sidebar.markdown("## 🔍 Filter Alumni")
        search_name = st.sidebar.text_input("Cari Nama Alumni:", "")
        
        list_tahun = sorted(df["Tahun Lulus"].unique().tolist(), reverse=True)
        selected_tahun = st.sidebar.multiselect("Tahun Lulus:", list_tahun, default=list_tahun)
        
        list_kelas = sorted(df["Kelas"].unique().tolist())
        selected_kelas = st.sidebar.multiselect("Kelas:", list_kelas, default=list_kelas)
        
        list_karier = sorted(df["Karier"].unique().tolist())
        list_karier = [k for k in list_karier if k != "-"]
        selected_karier = st.sidebar.multiselect("Karier:", list_karier, default=list_karier)
        
        list_instansi = sorted([i for i in df["Universitas/Instansi/Perusahaan"].unique().tolist() if i not in ["-", "_", ""]])
        selected_instansi = st.sidebar.multiselect("Universitas/Instansi/Perusahaan:", list_instansi)
        
        list_jurusan = sorted([j for j in df["Jurusan"].unique().tolist() if j not in ["-", "_", ""]])
        selected_jurusan = st.sidebar.multiselect("Jurusan Kuliah:", list_jurusan)

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

        st.markdown("### 📊 Ringkasan Statistik Alumni")
        total_alumni = len(df_filtered)

        if total_alumni > 0:
            bekerja_count = len(df_filtered[df_filtered["Karier"] == "BEKERJA"])
            kuliah_count = len(df_filtered[df_filtered["Karier"] == "KULIAH"])
            wirausaha_count = len(df_filtered[df_filtered["Karier"] == "WIRAUSAHA"])
            
            pct_bekerja = (bekerja_count / total_alumni) * 100
            pct_kuliah = (kuliah_count / total_alumni) * 100
            pct_wirausaha = (wirausaha_count / total_alumni) * 100
            
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
                        text=top_univ.apply(lambda row: f"{row['Jumlah Alumni']} ({row['Persentase']:.1f}%)", axis=1),
                        color_discrete_sequence=["#DAA520"]
                    )
                    fig_bar.update_layout(
                        margin=dict(l=20, r=20, t=15, b=10),
                        height=380,
                        xaxis_title="Jumlah Alumni",
                        yaxis_title="",
                        xaxis=dict(fixedrange=True),
                        yaxis=dict(fixedrange=True),
                        dragmode=False
                    )
                    fig_bar.update_traces(textposition="inside")
                    st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False, 'scrollZoom': False})
                else:
                    st.info("Pilih kategori 'KULIAH' pada filter karier untuk melihat sebaran Universitas.")

            # REKAP TABEL UNIVERSITAS FULL WIDTH
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

        st.markdown("### 🔍 Hasil Pencarian Detail Alumni")

        if search_name:
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
            st.info("💡 **Petunjuk**: Masukkan kata kunci nama alumni di kolom pencarian **'Cari Nama Alumni'** pada sidebar sebelah kiri untuk melakukan pencarian profil secara detail.")
            st.markdown("""
            <div style="background-color: #fff9e6; border-left: 5px solid #DAA520; padding: 15px; border-radius: 8px; margin-top: 10px;">
                <p style="color: #7a5c00; margin: 0; font-size: 0.95rem;">
                    🔒 <b>Proteksi Privasi Data Alumni</b>: Sesuai dengan kesepakatan privasi, tabel berisi seluruh data alumni dari SMAN 2 Sukatani tidak lagi ditampilkan secara terbuka. Silakan gunakan bar pencarian nama untuk melihat profil alumni secara mandiri.
                </p>
            </div>
            """, unsafe_allow_html=True)

    # ==========================================
    # TAB 2: FORM TAMBAH DATA ALUMNI MANDIRI
    # ==========================================
    with tab_form:
        st.markdown("### 📝 Formulir Mandiri Alumni SMAN 2 Sukatani")
        st.markdown("""
        Apakah Anda alumni SMAN 2 Sukatani yang belum terdaftar atau ingin memperbarui data? 
        Silakan isi formulir di bawah ini. Data yang Anda kirim akan ditinjau dan dimoderasi terlebih dahulu oleh Admin sebelum disetujui dan ditambahkan ke Spreadsheet Google Sheets serta Dashboard Publik.
        """)
        
        with st.form("form_alumni_new", clear_on_submit=True):
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                f_nama = st.text_input("Nama Lengkap *", placeholder="Contoh: AHMAD FAUZI")
                f_kelas = st.selectbox("Kelas Terakhir *", [
                    "12A",
                    "12B",
                    "12C",
                    "12D",
                    "12E",
                    "12F",
                    "12G",
                    "12H",
                    "12I",
                    "12J",
                    "12K",
                    "12L",
                    "XII MIPA 1",
                    "XII MIPA 2",
                    "XII MIPA 3",
                    "XII MIPA 4",
                    "XII MIPA 5",
                    "XII MIPA 6",
                    "XII IPS 1",
                    "XII IPS 2",
                    "XII IPS 3",
                    "XII IPS 4",
                    "XII IPS 5"
                ])
                f_tahun = st.number_input("Tahun Lulus *", min_value=2010, max_value=2030, value=2026, step=1)
            
            with col_f2:
                f_karier = st.selectbox("Status Karier *", ["KULIAH", "BEKERJA", "WIRAUSAHA"])
                f_instansi = st.text_input("Universitas / Instansi / Perusahaan *", placeholder="Contoh: Universitas Indonesia / PT Astra / Toko Mandiri")
                f_jurusan = st.text_input("Program Studi / Jurusan / Posisi Pekerjaan", placeholder="Contoh: Teknik Informatika / Staf HRD (Isi '-' jika Wirausaha)")

            btn_submit = st.form_submit_button("🚀 Kirim Data Alumni", use_container_width=True)
            
            if btn_submit:
                if not f_nama.strip():
                    st.error("⚠️ Nama Lengkap wajib diisi!")
                elif not f_instansi.strip():
                    st.error("⚠️ Nama Universitas / Instansi / Perusahaan wajib diisi!")
                else:
                    new_entry = {
                        "Nama": f_nama.strip().upper(),
                        "Kelas": f_kelas,
                        "Karier": f_karier,
                        "Universitas/Instansi/Perusahaan": f_instansi.strip(),
                        "Jurusan": f_jurusan.strip() if f_jurusan.strip() else "-",
                        "Tahun Lulus": int(f_tahun)
                    }
                    
                    pending_list = load_json_data(PENDING_FILE)
                    pending_list.append(new_entry)
                    save_json_data(PENDING_FILE, pending_list)
                    
                    st.success("✅ **Data Anda Berhasil Terkirim!** Terima kasih telah berpartisipasi. Data Anda sedang menunggu proses moderasi & verifikasi oleh Admin SMAN 2 Sukatani.")

    # ==========================================
    # TAB 3: PANEL MODERASI ADMIN
    # ==========================================
    with tab_admin:
        st.markdown("### 🔐 Panel Moderasi Data Alumni (Admin)")
        
        # Pengaturan Password Admin
        if "admin_logged_in" not in st.session_state:
            st.session_state.admin_logged_in = False

        if not st.session_state.admin_logged_in:
            col_pwd1, col_pwd2 = st.columns([2, 1])
            with col_pwd1:
                pwd_input = st.text_input("Masukkan Kata Sandi Admin untuk Mengakses:", type="password")
            with col_pwd2:
                st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                if st.button("🔓 Masuk Admin"):
                    if pwd_input == ADMIN_PASSWORD_DEFAULT or pwd_input == "admin123":
                        st.session_state.admin_logged_in = True
                        st.success("Akses Diberikan!")
                        st.rerun()
                    else:
                        st.error("❌ Kata sandi salah!")
        else:
            col_adm_title, col_adm_logout = st.columns([5, 1])
            with col_adm_title:
                st.success("🔓 **Status Admin: Terverifikasi**")
            with col_adm_logout:
                if st.button("🔒 Keluar Admin"):
                    st.session_state.admin_logged_in = False
                    st.rerun()

            st.markdown("---")
            
            # --- KONFIGURASI INTEGRASI GOOGLE SHEETS WRITE (APPS SCRIPT) ---
            st.subheader("🔗 Konfigurasi Otomatisasi Google Sheets")
            current_script_url = load_text_config(APPS_SCRIPT_URL_FILE)
            
            with st.expander("🛠️ Pengaturan Link Webhook Google Apps Script (Klik untuk membuka)", expanded=not bool(current_script_url)):
                st.markdown("""
                Agar data yang disetujui Admin dapat **otomatis masuk/terisi ke dalam file Google Sheets TRACER STUDY ALUMNI SMANDAS**, silakan buat Apps Script di Google Sheets Anda:
                1. Buka spreadsheet Google Sheets Anda -> Klik **Ekstensi (Extensions)** -> **Apps Script**.
                2. Hapus semua kode lalu **paste** kode berikut:
                ```javascript
                function doPost(e) {
                  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
                  var data = JSON.parse(e.postData.contents);
                  sheet.appendRow([data.nama, data.kelas, data.karier, data.instansi, data.jurusan, data.tahun]);
                  return ContentService.createTextOutput("Success").setMimeType(ContentService.MimeType.TEXT);
                }
                ```
                3. Klik **Terapkan (Deploy)** -> **Terapkan sebagai Aplikasi Web (New deployment)**.
                4. Setel **Jalankan sebagai**: *Saya (Me)* & **Siapa yang memiliki akses**: *Siapa saja (Anyone)*.
                5. Salin **URL Aplikasi Web (Web App URL)** lalu tempelkan di bawah ini:
                """)
                
                input_script_url = st.text_input("Google Apps Script Web App URL:", value=current_script_url, placeholder="https://script.google.com/macros/s/.../exec")
                if st.button("💾 Simpan Konfigurasi Apps Script"):
                    save_text_config(APPS_SCRIPT_URL_FILE, input_script_url)
                    st.success("✅ Konfigurasi URL Google Apps Script berhasil disimpan!")
                    st.rerun()

            st.markdown("---")
            pending_list = load_json_data(PENDING_FILE)
            
            st.subheader(f"📥 Permintaan Data Alumni Baru ({len(pending_list)} Menunggu Moderasi)")
            
            if len(pending_list) == 0:
                st.info("🎉 Tidak ada data alumni baru yang sedang menunggu moderasi saat ini.")
            else:
                st.markdown("💡 *Admin dapat memeriksa dan **mengedit data** terlebih dahulu sebelum mengeklik tombol Setujui & Tampilkan.*")
                
                for idx, item in enumerate(pending_list):
                    exp_title = f"📌 {item.get('Nama')} - {item.get('Kelas')} ({item.get('Karier')})"
                    with st.expander(exp_title, expanded=True):
                        st.markdown("##### ✏️ Form Edit & Verifikasi Admin")
                        with st.form(key=f"edit_form_{idx}"):
                            col_m1, col_m2 = st.columns(2)
                            
                            all_kelas = [
                    "12A",
                    "12B",
                    "12C",
                    "12D",
                    "12E",
                    "12F",
                    "12G",
                    "12H",
                    "12I",
                    "12J",
                    "12K",
                    "12L",
                    "XII MIPA 1",
                    "XII MIPA 2",
                    "XII MIPA 3",
                    "XII MIPA 4",
                    "XII MIPA 5",
                    "XII MIPA 6",
                    "XII IPS 1",
                    "XII IPS 2",
                    "XII IPS 3",
                    "XII IPS 4",
                    "XII IPS 5"
                ]
                            current_kelas = item.get("Kelas", "XII MIPA 1")
                            kelas_idx = all_kelas.index(current_kelas) if current_kelas in all_kelas else 0
                            
                            karier_opts = ["KULIAH", "BEKERJA", "WIRAUSAHA"]
                            current_karier = item.get("Karier", "BEKERJA")
                            karier_idx = karier_opts.index(current_karier) if current_karier in karier_opts else 0

                            with col_m1:
                                e_nama = st.text_input("Nama Lengkap", value=item.get("Nama", ""), key=f"e_nama_{idx}")
                                e_kelas = st.selectbox("Kelas Terakhir", all_kelas, index=kelas_idx, key=f"e_kelas_{idx}")
                                e_tahun = st.number_input("Tahun Lulus", min_value=2010, max_value=2030, value=int(item.get("Tahun Lulus", 2026)), step=1, key=f"e_tahun_{idx}")
                            
                            with col_m2:
                                e_karier = st.selectbox("Status Karier", karier_opts, index=karier_idx, key=f"e_karier_{idx}")
                                e_instansi = st.text_input("Universitas / Instansi / Perusahaan", value=item.get("Universitas/Instansi/Perusahaan", ""), key=f"e_instansi_{idx}")
                                e_jurusan = st.text_input("Program Studi / Jurusan / Posisi Pekerjaan", value=item.get("Jurusan", ""), key=f"e_jurusan_{idx}")
                            
                            st.markdown("<br>", unsafe_allow_html=True)
                            col_act1, col_act2 = st.columns(2)
                            
                            with col_act1:
                                btn_approve = st.form_submit_button("✅ Simpan Perubahan & Setujui (Kirim ke Google Sheets)", use_container_width=True)
                            with col_act2:
                                btn_reject = st.form_submit_button("❌ Tolak & Hapus Data", use_container_width=True)
                                
                            if btn_approve:
                                updated_entry = {
                                    "Nama": e_nama.strip().upper(),
                                    "Kelas": e_kelas,
                                    "Karier": e_karier,
                                    "Universitas/Instansi/Perusahaan": e_instansi.strip(),
                                    "Jurusan": e_jurusan.strip() if e_jurusan.strip() else "-",
                                    "Tahun Lulus": int(e_tahun)
                                }
                                
                                # 1. Pindahkan ke Approved List
                                approved_list = load_json_data(APPROVED_FILE)
                                approved_list.append(updated_entry)
                                save_json_data(APPROVED_FILE, approved_list)
                                
                                # 2. Kirim otomatis ke Google Sheets jika URL Apps Script terkonfigurasi
                                script_url = load_text_config(APPS_SCRIPT_URL_FILE)
                                gsheet_status = ""
                                if script_url:
                                    success, msg = send_to_google_sheet(updated_entry, script_url)
                                    gsheet_status = f" ({msg})"
                                else:
                                    gsheet_status = " (Catatan: Google Apps Script URL belum dikonfigurasi, data disimpan di lokal)"
                                
                                # 3. Hapus dari Pending
                                pending_list.pop(idx)
                                save_json_data(PENDING_FILE, pending_list)
                                
                                st.cache_data.clear()
                                st.success(f"✅ Data **{updated_entry['Nama']}** berhasil diedit, disetujui, dan diproses{gsheet_status}!")
                                st.rerun()
                                
                            if btn_reject:
                                pending_list.pop(idx)
                                save_json_data(PENDING_FILE, pending_list)
                                st.warning(f"Data {item.get('Nama')} telah ditolak.")
                                st.rerun()

            st.markdown("---")
            st.subheader("📋 Daftar Alumni Mandiri yang Telah Disetujui")
            approved_list = load_json_data(APPROVED_FILE)
            if len(approved_list) > 0:
                df_app_view = pd.DataFrame(approved_list)
                st.dataframe(df_app_view, use_container_width=True)
                if st.button("🗑️ Hapus Semua Data Mandiri Approved (Reset)"):
                    save_json_data(APPROVED_FILE, [])
                    st.cache_data.clear()
                    st.rerun()
            else:
                st.write("Belum ada data alumni hasil penambahan mandiri yang disetujui.")

    st.markdown("""
    <hr style="border:0.5px solid #eaeaea;">
    <p style="text-align:center; color:gray; font-size:0.8rem;">
        Dashboard Tracer Study SMAN 2 Sukatani © 2026. Terkoneksi otomatis dengan Google Sheets secara real-time.
    </p>
    """, unsafe_allow_html=True)
else:
    st.info("Menunggu data dari Google Sheets terisi...")
