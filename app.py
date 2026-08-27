import streamlit as st
import pandas as pd
from ortools.sat.python import cp_model
import io
import urllib.parse
from datetime import datetime

st.set_page_config(
    page_title="Iğdır AR-GE - Akıllı Okul Planlama Sistemi", 
    layout="wide", 
    page_icon="🏫"
)

# Temiz, Kontrastı Sabit ve Çıktı / Print Uyumlu CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    .stApp {
        background-color: #f8fafc;
        color: #0f172a;
    }
    
    /* Input ve Selectbox Renk Sabitleme */
    input, textarea, select, [data-baseweb="input"] > div, [data-baseweb="base-input"] > input, div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #0f172a !important;
        -webkit-text-fill-color: #0f172a !important;
        border-color: #cbd5e1 !important;
    }
    
    .hero-banner {
        background: linear-gradient(135deg, #0284c7 0%, #2563eb 50%, #1d4ed8 100%);
        border-radius: 16px;
        padding: 22px 30px;
        margin-bottom: 20px;
        box-shadow: 0 10px 25px -5px rgba(37, 99, 235, 0.2);
        display: flex;
        justify-content: space-between;
        align-items: center;
        color: #ffffff;
    }
    .hero-title {
        font-size: 22px;
        font-weight: 800;
        margin: 0;
        color: #ffffff !important;
    }
    .hero-desc {
        color: #e0f2fe;
        font-size: 13px;
        margin-top: 4px;
    }
    .badge-arge {
        background: #ffffff;
        color: #0284c7;
        padding: 6px 16px;
        border-radius: 30px;
        font-size: 12px;
        font-weight: 800;
    }
    .stButton > button {
        background-color: #ffffff !important;
        color: #1e293b !important;
        border: 1px solid #cbd5e1 !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
    }
    .stButton > button:hover {
        background-color: #f1f5f9 !important;
        border-color: #94a3b8 !important;
        color: #0f172a !important;
    }
    .stDownloadButton > button {
        background-color: #2563eb !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 8px !important;
    }
    .stDownloadButton > button:hover {
        background-color: #1d4ed8 !important;
        color: #ffffff !important;
    }
    .metric-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 4px 12px -2px rgba(0, 0, 0, 0.03);
    }
    .metric-val {
        font-size: 24px;
        font-weight: 800;
        color: #0284c7;
    }
    .metric-lbl {
        font-size: 11px;
        font-weight: 700;
        color: #64748b;
        text-transform: uppercase;
    }
    table.schedule-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 6px;
        margin-top: 15px;
    }
    table.schedule-table th {
        background: #1e293b;
        color: #ffffff;
        text-align: center;
        padding: 10px 6px;
        font-size: 13px;
        font-weight: 700;
        border-radius: 6px;
    }
    table.schedule-table td {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        padding: 6px;
        text-align: center;
        font-size: 12px;
        height: 55px;
    }
    table.schedule-table td.day-cell {
        background: #f1f5f9;
        font-weight: 700;
        color: #1e293b;
        width: 110px;
    }
    .lesson-box {
        background: #f0f9ff;
        border: 1px solid #bae6fd;
        border-radius: 6px;
        padding: 5px;
        color: #0369a1;
        font-weight: 600;
    }
    .lesson-box small {
        color: #0284c7;
        display: block;
        margin-top: 2px;
        font-weight: 500;
    }
    .nobet-col-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 4px 12px -2px rgba(0,0,0,0.03);
        border-top: 4px solid #0ea5e9;
    }
    .nobet-title {
        font-size: 15px;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 12px;
        padding-bottom: 8px;
        border-bottom: 1px solid #f1f5f9;
    }
    .nobet-teacher-pill {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 8px 12px;
        margin-bottom: 8px;
        font-size: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .location-tag {
        background: #e0f2fe;
        color: #0369a1;
        font-size: 11px;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 6px;
    }
    .signature-container {
        margin-top: 20px;
        display: flex;
        justify-content: space-between;
        padding: 15px 40px;
        border-top: 2px dashed #cbd5e1;
        background: #ffffff;
    }
    
    @media print {
        .hero-banner, .stSidebar, .stButton, header, footer, .stDownloadButton, [data-testid="stSidebarNav"] {
            display: none !important;
        }
        .page-break {
            page-break-after: always;
            break-after: page;
            padding-top: 20px;
        }
    }
</style>
""", unsafe_allow_html=True)

# Oturum Durumu
if "sayfa" not in st.session_state:
    st.session_state["sayfa"] = "Veri"

if "dersler" not in st.session_state:
    st.session_state["dersler"] = []

if "ogretmen_tercih" not in st.session_state:
    st.session_state["ogretmen_tercih"] = {}

if "nobet_yerleri" not in st.session_state:
    st.session_state["nobet_yerleri"] = ["Bahçe", "Zemin Kat", "1. Kat", "2. Kat", "Spor Salonu", "Pansiyon"]

if "sonuclar" not in st.session_state:
    st.session_state["sonuclar"] = None

if "bildirimler" not in st.session_state:
    st.session_state["bildirimler"] = [
        {"tarih": "2026-08-27", "baslik": "v3.0 - Excel Nöbet Yerleri & Güvenli İletişim", "icerik": "Nöbet yerleri Excel şablonuna dahil edildi ve okul hata bildirimleri doğrudan e-posta yönlendirmesine bağlandı."}
    ]

gunler = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"]

# Sol Menü
with st.sidebar:
    st.markdown("### 🏫 Okul Planlama")
    st.markdown("---")
    
    menuler = [
        ("✏️ Veri & Kısıt Yönetimi", "Veri"),
        ("🎓 Sınıf Programları", "Sınıflar"),
        ("👨‍🏫 Öğretmen Programları (A4)", "Öğretmenler"),
        ("📊 Genel Çarşaf Tablo & Excel", "Carsaf"),
        ("🛡️ Akıllı Nöbet & Doğrulama", "Nöbet"),
        ("💬 Hata & Talep Bildir", "HataBildir"),
        ("📜 Sürüm & Güncellemeler", "Guncellemeler")
    ]
    
    for baslik, key in menuler:
        if st.button(baslik, use_container_width=True, type="primary" if st.session_state["sayfa"] == key else "secondary"):
            st.session_state["sayfa"] = key
            st.rerun()

    st.markdown("---")
    st.subheader("⚙️ Günlük Ders Saatleri")
    
    gunluk_saatler = {}
    gunluk_saatler["Pazartesi"] = st.slider("Pazartesi Saati", 5, 10, 8)
    gunluk_saatler["Salı"] = st.slider("Salı Saati", 5, 10, 7)
    gunluk_saatler["Çarşamba"] = st.slider("Çarşamba Saati", 5, 10, 7)
    gunluk_saatler["Perşembe"] = st.slider("Perşembe Saati", 5, 10, 7)
    gunluk_saatler["Cuma"] = st.slider("Cuma Saati", 5, 10, 7)

# Üst Banner
st.markdown("""
<div class="hero-banner">
    <div>
        <h1 class="hero-title">Akıllı Okul Ders & Nöbet Dağıtım Sistemi</h1>
        <div class="hero-desc">Sıfır Çakışma • Kesintisiz Blok Dersler • Akıllı Nöbet Optimizasyonu</div>
    </div>
    <div class="badge-arge">Iğdır İl Millî Eğitim Müdürlüğü AR-GE Birimi</div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 1. VERİ & KISIT YÖNETİMİ
# ==========================================
if st.session_state["sayfa"] == "Veri":
    st.subheader("📥 Veri Girişi ve Excel Yönetimi")
    
    c_card1, c_card2 = st.columns([1, 1])
    with c_card1:
        st.markdown("##### 📥 Excel Şablonu")
        st.caption("Sınıfları 'Ders_Listesi'ne, okulun nöbet alanlarını ise 'Nobet_Yerleri' sayfasına girin:")
        
        sablon_d = st.session_state["dersler"] if st.session_state["dersler"] else [
            {"Sınıf": "9-A", "Ders": "Matematik", "Öğretmen": "Ahmet Yılmaz", "Saat Dağılımı": "2+2+2"}
        ]
        sablon_o = [
            {"Öğretmen": k, "Nöbet Günü": v.get("nobet", "Otomatik"), "Nöbet Yeri": v.get("yer", "Bahçe"), "Boş Gün İsteği": v.get("bos", ""), "Zaman Kısıtı": v.get("zaman", "Tüm Gün"), "Nöbetten Muaf": "Evet" if v.get("muaf") else "Hayır"}
            for k, v in st.session_state["ogretmen_tercih"].items()
        ] if st.session_state["ogretmen_tercih"] else [
            {"Öğretmen": "Ahmet Yılmaz", "Nöbet Günü": "Otomatik", "Nöbet Yeri": "Bahçe", "Boş Gün İsteği": "", "Zaman Kısıtı": "Tüm Gün", "Nöbetten Muaf": "Hayır"}
        ]
        sablon_yerler = [{"Nöbet Yeri Adı": y} for y in st.session_state["nobet_yerleri"] if y != "-"]
        
        buf_sablon = io.BytesIO()
        with pd.ExcelWriter(buf_sablon, engine="openpyxl") as writer:
            pd.DataFrame(sablon_d).to_excel(writer, sheet_name="Ders_Listesi", index=False)
            pd.DataFrame(sablon_o).to_excel(writer, sheet_name="Ogretmen_Nobet", index=False)
            pd.DataFrame(sablon_yerler).to_excel(writer, sheet_name="Nobet_Yerleri", index=False)
        
        st.download_button(
            label="📥 Excel Şablonunu İndir (.xlsx)",
            data=buf_sablon.getvalue(),
            file_name="Okul_Ders_Dagitim_Sablonu.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    with c_card2:
        st.markdown("##### 📤 Doldurulan Excel'i Yükle")
        uploaded_file = st.file_uploader("Dosyayı buraya bırakın", type=["xlsx", "xls"])
        if uploaded_file is not None:
            try:
                xls = pd.ExcelFile(uploaded_file)
                df_d = pd.read_excel(xls, sheet_name="Ders_Listesi").fillna("")
                df_o = pd.read_excel(xls, sheet_name="Ogretmen_Nobet").fillna("")
                
                # Nöbet Yerleri sayfasını kontrol et ve yükle
                if "Nobet_Yerleri" in xls.sheet_names:
                    df_y = pd.read_excel(xls, sheet_name="Nobet_Yerleri").fillna("")
                    yerler = [str(r).strip() for r in df_y["Nöbet Yeri Adı"].tolist() if str(r).strip()]
                    if yerler:
                        st.session_state["nobet_yerleri"] = yerler + ["-"]
                
                st.session_state["dersler"] = df_d[["Sınıf", "Ders", "Öğretmen", "Saat Dağılımı"]].to_dict("records")
                st.session_state["ogretmen_tercih"] = {}
                for _, row in df_o.iterrows():
                    ogr = str(row["Öğretmen"]).strip()
                    if ogr:
                        is_muaf = str(row.get("Nöbetten Muaf", "")).strip().lower() in ["evet", "true", "1"]
                        yer_val = str(row.get("Nöbet Yeri", "Bahçe")).strip()
                        if yer_val and yer_val not in st.session_state["nobet_yerleri"]:
                            st.session_state["nobet_yerleri"].insert(0, yer_val)
                        
                        st.session_state["ogretmen_tercih"][ogr] = {
                            "nobet": "Muaf" if is_muaf else (str(row.get("Nöbet Günü", "Otomatik")).strip() or "Otomatik"),
                            "yer": yer_val,
                            "bos": str(row.get("Boş Gün İsteği", "")).strip(),
                            "zaman": str(row.get("Zaman Kısıtı", "Tüm Gün")).strip() or "Tüm Gün",
                            "muaf": is_muaf
                        }
                st.success("✓ Veriler ve Nöbet Yerleri başarıyla aktarıldı!")
                st.rerun()
            except Exception as e:
                st.error(f"Excel şablon formatı geçersiz: {e}")

    st.markdown("---")

    # Manuel Ders Ekleme
    with st.expander("➕ Ekrandan Hızlı Ders Ekle / Sil", expanded=False):
        c1, c2, c3, c4, c5 = st.columns([1.5, 2, 2.5, 2, 1.5])
        with c1:
            in_sinif = st.text_input("Sınıf", placeholder="Örn: 9-A")
        with c2:
            in_ders = st.text_input("Ders Adı", placeholder="Örn: Matematik")
        with c3:
            in_ogr = st.text_input("Öğretmen", placeholder="Örn: Selin Korkmaz")
        with c4:
            in_blok = st.selectbox("Blok", ["2+2+2", "2+2", "2+2+1", "2+1", "2", "1"])
        with c5:
            st.write("")
            st.write("")
            if st.button("➕ Ekle", use_container_width=True):
                if in_sinif and in_ders and in_ogr:
                    st.session_state["dersler"].append({
                        "Sınıf": in_sinif.strip().upper(),
                        "Ders": in_ders.strip(),
                        "Öğretmen": in_ogr.strip(),
                        "Saat Dağılımı": in_blok
                    })
                    if in_ogr.strip() not in st.session_state["ogretmen_tercih"]:
                        st.session_state["ogretmen_tercih"][in_ogr.strip()] = {"nobet": "Otomatik", "yer": st.session_state["nobet_yerleri"][0], "bos": "", "zaman": "Tüm Gün", "muaf": False}
                    st.rerun()

    # Yüklü Dersler ve Filtre
    c_th1, c_th2 = st.columns([4, 1])
    with c_th1:
        st.markdown("##### 📋 Tanımlı Ders Listesi (" + str(len(st.session_state["dersler"])) + " Ders)")
    with c_th2:
        if st.button("🗑️ Temizle", use_container_width=True):
            st.session_state["dersler"] = []
            st.session_state["ogretmen_tercih"] = {}
            st.session_state["sonuclar"] = None
            st.rerun()

    if st.session_state["dersler"]:
        arama_kelimesi = st.text_input("🔍 Listede Ara:", placeholder="Örn: Matematik, Selin, 9-A...", key="srch_input_main")
        df_dersler = pd.DataFrame(st.session_state["dersler"])
        if arama_kelimesi:
            df_goster = df_dersler[
                df_dersler["Sınıf"].str.contains(arama_kelimesi, case=False, na=False) |
                df_dersler["Ders"].str.contains(arama_kelimesi, case=False, na=False) |
                df_dersler["Öğretmen"].str.contains(arama_kelimesi, case=False, na=False)
            ]
        else:
            df_goster = df_dersler
            
        st.dataframe(df_goster, use_container_width=True, hide_index=True)
    else:
        st.info("Henüz kayıtlı ders bulunmuyor. Yukarıdan Excel yükleyebilirsiniz.")

    # Kısıtlar ve Nöbet Yerleri
    if st.session_state["dersler"]:
        with st.expander("🛡️ Öğretmen Nöbet, İzin & Zaman Kısıtları", expanded=False):
            mevcut_ogretmenler = sorted(list(set([d["Öğretmen"] for d in st.session_state["dersler"]])))
            ogr_filtre = st.text_input("🔍 Öğretmen Ara:", placeholder="Öğretmen adı yazın...", key="filter_ogr_kisit")
            gosterilecek_ogretmenler = [o for o in mevcut_ogretmenler if ogr_filtre.lower() in o.lower()] if ogr_filtre else mevcut_ogretmenler

            sabit_yerler = st.session_state["nobet_yerleri"]

            for ogr in gosterilecek_ogretmenler:
                if ogr not in st.session_state["ogretmen_tercih"]:
                    st.session_state["ogretmen_tercih"][ogr] = {"nobet": "Otomatik", "yer": sabit_yerler[0], "bos": "", "zaman": "Tüm Gün", "muaf": False}
                
                c_o1, c_o2, c_o3, c_o4, c_o5, c_o6 = st.columns([2.5, 1.8, 1.8, 1.8, 1.8, 1.3])
                with c_o1:
                    st.write(f"**{ogr}**")
                with c_o2:
                    st.session_state["ogretmen_tercih"][ogr]["nobet"] = st.selectbox(
                        f"Nöbet ({ogr})", ["Otomatik", "Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Muaf"],
                        index=["Otomatik", "Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Muaf"].index(st.session_state["ogretmen_tercih"][ogr].get("nobet", "Otomatik")),
                        label_visibility="collapsed"
                    )
                with c_o3:
                    mevcut_yer = st.session_state["ogretmen_tercih"][ogr].get("yer", sabit_yerler[0])
                    yer_idx = sabit_yerler.index(mevcut_yer) if mevcut_yer in sabit_yerler else 0
                    st.session_state["ogretmen_tercih"][ogr]["yer"] = st.selectbox(
                        f"Yer ({ogr})", sabit_yerler, index=yer_idx, label_visibility="collapsed"
                    )
                with c_o4:
                    st.session_state["ogretmen_tercih"][ogr]["bos"] = st.selectbox(
                        f"Boş Gün ({ogr})", ["", "Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"],
                        index=["", "Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"].index(st.session_state["ogretmen_tercih"][ogr].get("bos", "")),
                        label_visibility="collapsed"
                    )
                with c_o5:
                    st.session_state["ogretmen_tercih"][ogr]["zaman"] = st.selectbox(
                        f"Zaman ({ogr})", ["Tüm Gün", "Sadece Sabah", "Sadece Öğle"],
                        index=["Tüm Gün", "Sadece Sabah", "Sadece Öğle"].index(st.session_state["ogretmen_tercih"][ogr].get("zaman", "Tüm Gün")),
                        label_visibility="collapsed"
                    )
                with c_o6:
                    st.session_state["ogretmen_tercih"][ogr]["muaf"] = st.checkbox("Muaf", value=st.session_state["ogretmen_tercih"][ogr].get("muaf", False), key=f"chk_m_{ogr}")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # HESAPLA BUTONU
    if st.button("🚀 Çakışmasız Ders & Nöbet Programını Hesapla", type="primary", use_container_width=True):
        dersler = [d for d in st.session_state["dersler"] if str(d.get("Sınıf","")).strip() and str(d.get("Öğretmen","")).strip()]
        if not dersler:
            st.error("Lütfen önce ders verisi ekleyin.")
        else:
            with st.spinner("Optimizasyon motoru çalışıyor..."):
                gun_sayisi = len(gunler)
                gun_baslangic = {}
                toplam_saat = 0
                for g in gunler:
                    gun_baslangic[g] = toplam_saat
                    toplam_saat += gunluk_saatler[g]
                
                siniflar = sorted(list(set(d["Sınıf"] for d in dersler)))
                ogretmenler = sorted(list(set(d["Öğretmen"] for d in dersler)))

                blok_listesi = []
                for d in dersler:
                    bloklar = str(d.get("Saat Dağılımı", "2")).split("+")
                    for b in bloklar:
                        try:
                            sure = int(b.strip())
                        except:
                            sure = 2
                        blok_listesi.append({
                            "sinif": d["Sınıf"], 
                            "ders": d["Ders"], 
                            "ogretmen": d["Öğretmen"], 
                            "sure": sure
                        })

                model = cp_model.CpModel()
                x = {}
                for b_idx, blok in enumerate(blok_listesi):
                    for t in range(toplam_saat):
                        x[(b_idx, t)] = model.NewBoolVar(f"b_{b_idx}_t_{t}")

                nobet_var = {}
                for ogr in ogretmenler:
                    for g_idx in range(gun_sayisi):
                        nobet_var[(ogr, g_idx)] = model.NewBoolVar(f"nobet_{ogr}_{g_idx}")

                for b_idx, blok in enumerate(blok_listesi):
                    gecerli = []
                    for g_idx, g in enumerate(gunler):
                        g_saat_sayisi = gunluk_saatler[g]
                        g_bas = gun_baslangic[g]
                        for s in range(g_saat_sayisi - blok["sure"] + 1):
                            gecerli.append(g_bas + s)
                    
                    model.Add(sum(x[(b_idx, t)] for t in gecerli) == 1)
                    for t in range(toplam_saat):
                        if t not in gecerli:
                            model.Add(x[(b_idx, t)] == 0)

                for s in siniflar:
                    for t in range(toplam_saat):
                        model.Add(sum([x[(b_idx, t - off)] for b_idx, blok in enumerate(blok_listesi) if blok["sinif"] == s for off in range(blok["sure"]) if t - off >= 0]) <= 1)

                for ogr in ogretmenler:
                    for t in range(toplam_saat):
                        model.Add(sum([x[(b_idx, t - off)] for b_idx, blok in enumerate(blok_listesi) if blok["ogretmen"] == ogr for off in range(blok["sure"]) if t - off >= 0]) <= 1)

                for s in siniflar:
                    for g_idx, g in enumerate(gunler):
                        g_bas = gun_baslangic[g]
                        g_sayi = gunluk_saatler[g]
                        for sa in range(1, g_sayi):
                            t = g_bas + sa
                            akt_t = sum([x[(b_idx, t - off)] for b_idx, blok in enumerate(blok_listesi) if blok["sinif"] == s for off in range(blok["sure"]) if t - off >= 0])
                            akt_p = sum([x[(b_idx, (t-1) - off)] for b_idx, blok in enumerate(blok_listesi) if blok["sinif"] == s for off in range(blok["sure"]) if (t-1) - off >= 0])
                            model.Add(akt_t <= akt_p)

                for ogr in ogretmenler:
                    trc = st.session_state["ogretmen_tercih"].get(ogr, {})
                    nobet_secim = trc.get("nobet", "Otomatik")
                    bos_g = trc.get("bos", "")
                    zaman = trc.get("zaman", "Tüm Gün")
                    is_muaf = trc.get("muaf", False) or (nobet_secim == "Muaf")

                    for g_idx, g in enumerate(gunler):
                        g_bas = gun_baslangic[g]
                        g_sayi = gunluk_saatler[g]
                        yarim = g_sayi // 2

                        if zaman == "Sadece Sabah":
                            for sa in range(yarim, g_sayi):
                                t = g_bas + sa
                                for b_idx, blok in enumerate(blok_listesi):
                                    if blok["ogretmen"] == ogr:
                                        model.Add(x[(b_idx, t)] == 0)
                        elif zaman == "Sadece Öğle":
                            for sa in range(0, yarim):
                                t = g_bas + sa
                                for b_idx, blok in enumerate(blok_listesi):
                                    if blok["ogretmen"] == ogr:
                                        model.Add(x[(b_idx, t)] == 0)

                        if bos_g == g:
                            for t in range(g_bas, g_bas + g_sayi):
                                for b_idx, blok in enumerate(blok_listesi):
                                    if blok["ogretmen"] == ogr:
                                        model.Add(x[(b_idx, t)] == 0)
                            model.Add(nobet_var[(ogr, g_idx)] == 0)

                    if is_muaf:
                        for g_idx in range(gun_sayisi):
                            model.Add(nobet_var[(ogr, g_idx)] == 0)
                    elif nobet_secim in gunler:
                        g_idx = gunler.index(nobet_secim)
                        model.Add(nobet_var[(ogr, g_idx)] == 1)
                        model.Add(sum(nobet_var[(ogr, g_i)] for g_i in range(gun_sayisi)) == 1)
                    else:
                        model.Add(sum(nobet_var[(ogr, g_i)] for g_i in range(gun_sayisi)) == 1)

                    if not is_muaf:
                        for g_idx, g in enumerate(gunler):
                            g_bas = gun_baslangic[g]
                            g_sayi = gunluk_saatler[g]
                            gunluk_ders_saati = sum(
                                x[(b_idx, t)] * blok["sure"]
                                for b_idx, blok in enumerate(blok_listesi)
                                if blok["ogretmen"] == ogr
                                for t in range(g_bas, g_bas + g_sayi)
                            )
                            model.Add(gunluk_ders_saati >= 2 * nobet_var[(ogr, g_idx)])

                solver = cp_model.CpSolver()
                solver.parameters.max_time_in_seconds = 30.0
                status = solver.Solve(model)

                if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
                    sonuclar = {
                        "sinif": {s: {g: [""] * gunluk_saatler[g] for g in gunler} for s in siniflar},
                        "ogretmen": {ogr: {g: [""] * gunluk_saatler[g] for g in gunler} for ogr in ogretmenler},
                        "ogretmen_gunluk_ders": {ogr: {g: 0 for g in gunler} for ogr in ogretmenler},
                        "siniflar": siniflar,
                        "ogretmenler": ogretmenler,
                        "otomatik_nobetler": {},
                        "toplam_ders_saati": sum(b["sure"] for b in blok_listesi),
                        "gunluk_saatler": gunluk_saatler,
                        "gun_baslangic": gun_baslangic
                    }

                    for ogr in ogretmenler:
                        for g_idx, gun in enumerate(gunler):
                            if solver.Value(nobet_var[(ogr, g_idx)]) == 1:
                                sonuclar["otomatik_nobetler"][ogr] = gun

                    for g_idx, gun in enumerate(gunler):
                        g_bas = gun_baslangic[gun]
                        g_sayi = gunluk_saatler[gun]
                        for saat in range(g_sayi):
                            t = g_bas + saat
                            for b_idx, blok in enumerate(blok_listesi):
                                for off in range(blok["sure"]):
                                    if t - off >= 0 and solver.Value(x[(b_idx, t - off)]) == 1:
                                        sonuclar["sinif"][blok["sinif"]][gun][saat] = f"<div class='lesson-box'>{blok['ders']}<small>{blok['ogretmen']}</small></div>"
                                        sonuclar["ogretmen"][blok["ogretmen"]][gun][saat] = f"<div class='lesson-box'>{blok['sinif']}<small>{blok['ders']}</small></div>"
                                        sonuclar["ogretmen_gunluk_ders"][blok["ogretmen"]][gun] += 1
                    
                    st.session_state["sonuclar"] = sonuclar
                    st.success("✓ Ders ve Nöbet Programı Başarıyla Oluşturuldu!")
                else:
                    st.session_state["sonuclar"] = None
                    st.error("✗ Çakışmasız çözüm bulunamadı. Lütfen kısıtları kontrol edin.")

    # İSTATİSTİK PANELİ
    if st.session_state["sonuclar"]:
        st.markdown("---")
        st.markdown("#### 📊 Okul Dağıtım İstatistikleri")
        res = st.session_state["sonuclar"]
        c_st1, c_st2, c_st3, c_st4 = st.columns(4)
        with c_st1:
            st.markdown(f'<div class="metric-card"><div class="metric-val">{len(res["siniflar"])}</div><div class="metric-lbl">Toplam Şube</div></div>', unsafe_allow_html=True)
        with c_st2:
            st.markdown(f'<div class="metric-card"><div class="metric-val">{len(res["ogretmenler"])}</div><div class="metric-lbl">Aktif Öğretmen</div></div>', unsafe_allow_html=True)
        with c_st3:
            st.markdown(f'<div class="metric-card"><div class="metric-val">{res["toplam_ders_saati"]}</div><div class="metric-lbl">Haftalık Toplam Ders</div></div>', unsafe_allow_html=True)
        with c_st4:
            ort_yuk = round(res["toplam_ders_saati"] / len(res["ogretmenler"]), 1) if res["ogretmenler"] else 0
            st.markdown(f'<div class="metric-card"><div class="metric-val">{ort_yuk} Sa</div><div class="metric-lbl">Ort. Öğretmen Yükü</div></div>', unsafe_allow_html=True)

# ==========================================
# 2. SINIF PROGRAMLARI
# ==========================================
elif st.session_state["sayfa"] == "Sınıflar":
    st.subheader("🎓 Sınıf Bazlı Ders Programları")
    if st.session_state["sonuclar"]:
        sonuclar = st.session_state["sonuclar"]
        g_saatler = sonuclar["gunluk_saatler"]
        max_saat = max(g_saatler.values())
        
        c_s1, c_s2 = st.columns([1, 3])
        with c_s1:
            ara_sinif = st.text_input("🔍 Şube Filtrele:", placeholder="Örn: 9-A...", key="srch_sinif")
        
        filtrelenen_siniflar = [s for s in sonuclar["siniflar"] if ara_sinif.lower() in s.lower()] if ara_sinif else sonuclar["siniflar"]
        
        if filtrelenen_siniflar:
            with c_s2:
                secili_s = st.selectbox("İncelemek İstediğiniz Sınıfı Seçin:", filtrelenen_siniflar)
            
            if secili_s:
                html = f"<table class='schedule-table'><tr><th>Gün</th>" + "".join([f"<th>{i+1}. Ders</th>" for i in range(max_saat)]) + "</tr>"
                for g in gunler:
                    g_saat = g_saatler[g]
                    html += f"<tr><td class='day-cell'>{g} ({g_saat} Sa)</td>"
                    for sa in range(max_saat):
                        if sa < g_saat:
                            val = sonuclar["sinif"][secili_s][g][sa]
                            html += f"<td>{val if val else '-'}</td>"
                        else:
                            html += "<td style='background:#f8fafc; color:#cbd5e1;'>-</td>"
                    html += "</tr>"
                html += "</table>"
                st.markdown(html, unsafe_allow_html=True)
        else:
            st.warning("Aramanıza uygun sınıf bulunamadı.")
    else:
        st.info("Lütfen önce 'Veri & Kısıt Yönetimi' menüsünden programı hesaplayın.")

# ==========================================
# 3. ÖĞRETMEN PROGRAMLARI (TEKLİ & TOPLU A4 YAZDIRMA)
# ==========================================
elif st.session_state["sayfa"] == "Öğretmenler":
    st.subheader("👨‍🏫 Öğretmen Haftalık Ders Programı & Resmi Tebliğ")
    if st.session_state["sonuclar"]:
        sonuclar = st.session_state["sonuclar"]
        g_saatler = sonuclar["gunluk_saatler"]
        max_saat = max(g_saatler.values())
        
        tab_tek, tab_toplu = st.tabs(["📄 Tek Öğretmen Yazdır", "📑 Tüm Öğretmenleri Toplu Yazdır (A4)"])
        
        with tab_tek:
            c_o_srch, c_o_sel, c_btn = st.columns([1.5, 2, 1.5])
            with c_o_srch:
                ara_ogr = st.text_input("🔍 Öğretmen Ara:", placeholder="İsim yazın...", key="srch_ogr_tek")
            
            filtrelenen_ogretmenler = [o for o in sonuclar["ogretmenler"] if ara_ogr.lower() in o.lower()] if ara_ogr else sonuclar["ogretmenler"]
            
            if filtrelenen_ogretmenler:
                with c_o_sel:
                    secili_o = st.selectbox("Öğretmen Seç:", filtrelenen_ogretmenler)
                with c_btn:
                    st.write("")
                    st.write("")
                    st.button("🖨️ Bu Sayfayı Yazdır (Ctrl + P)", use_container_width=True)
                
                if secili_o:
                    nobet_g = sonuclar["otomatik_nobetler"].get(secili_o, "Nöbetten Muaf")
                    yer = st.session_state["ogretmen_tercih"].get(secili_o, {}).get("yer", "-")
                    bos_istek = st.session_state["ogretmen_tercih"].get(secili_o, {}).get("bos", "Yok")
                    toplam_ogr_ders = sum(sonuclar["ogretmen_gunluk_ders"][secili_o].values())
                    
                    c1, c2, c3, c4 = st.columns(4)
                    with c1:
                        st.markdown(f"**Öğretmen:** {secili_o}")
                    with c2:
                        st.markdown(f"**Haftalık Yük:** {toplam_ogr_ders} Saat")
                    with c3:
                        st.markdown(f"**🛡️ Nöbet Durumu:** {nobet_g} ({yer})")
                    with c4:
                        st.markdown(f"**Boş Gün:** {bos_istek if bos_istek else 'Yok'}")

                    html = f"<table class='schedule-table'><tr><th>Gün</th>" + "".join([f"<th>{i+1}. Ders</th>" for i in range(max_saat)]) + "</tr>"
                    for g in gunler:
                        g_saat = g_saatler[g]
                        html += f"<tr><td class='day-cell'>{g}</td>"
                        for sa in range(max_saat):
                            if sa < g_saat:
                                val = sonuclar["ogretmen"][secili_o][g][sa]
                                html += f"<td>{val if val else '-'}</td>"
                            else:
                                html += "<td style='background:#f8fafc; color:#cbd5e1;'>-</td>"
                        html += "</tr>"
                    html += "</table>"
                    
                    html += """
                    <div class="signature-container">
                        <div style="text-align: center;">
                            <b>Teslim Eden</b><br>
                            Okul Müdürü<br>
                            İmza / Mühür
                        </div>
                        <div style="text-align: center;">
                            <b>Tebliğ Aldım</b><br>
                            Öğretmen İmza<br>
                            Tarih: ..... / ..... / 202...
                        </div>
                    </div>
                    """
                    st.markdown(html, unsafe_allow_html=True)
        
        with tab_toplu:
            st.info("💡 **İpucu:** Aşağıdaki 'Tüm Okulu Yazdır' butonuna bastıktan sonra veya tarayıcınızdan **Ctrl + P** yaparak tüm öğretmenlerin programlarını tek seferde A4 çıktısı alabilirsiniz.")
            st.button("🖨️ Tüm Öğretmenleri Yazdır (PDF / Çıktı)", use_container_width=True)
            
            tum_ogretmenler_html = ""
            for o in sonuclar["ogretmenler"]:
                nobet_g = sonuclar["otomatik_nobetler"].get(o, "Nöbetten Muaf")
                yer = st.session_state["ogretmen_tercih"].get(o, {}).get("yer", "-")
                toplam_ogr_ders = sum(sonuclar["ogretmen_gunluk_ders"][o].values())
                
                tum_ogretmenler_html += f"""
                <div class="page-break">
                    <div style="border-bottom: 2px solid #334155; padding-bottom: 8px; margin-bottom: 12px; display: flex; justify-content: space-between;">
                        <span style="font-size: 16px; font-weight: 800;">Öğretmen: {o}</span>
                        <span><b>Yük:</b> {toplam_ogr_ders} Sa | <b>Nöbet:</b> {nobet_g} ({yer})</span>
                    </div>
                    <table class='schedule-table'><tr><th>Gün</th>""" + "".join([f"<th>{i+1}. Ders</th>" for i in range(max_saat)]) + "</tr>"
                
                for g in gunler:
                    g_saat = g_saatler[g]
                    tum_ogretmenler_html += f"<tr><td class='day-cell'>{g}</td>"
                    for sa in range(max_saat):
                        if sa < g_saat:
                            val = sonuclar["ogretmen"][o][g][sa]
                            tum_ogretmenler_html += f"<td>{val if val else '-'}</td>"
                        else:
                            tum_ogretmenler_html += "<td style='background:#f8fafc; color:#cbd5e1;'>-</td>"
                    tum_ogretmenler_html += "</tr>"
                
                tum_ogretmenler_html += f"""
                    </table>
                    <div class="signature-container">
                        <div style="text-align: center;"><b>Teslim Eden</b><br>Okul Müdürü</div>
                        <div style="text-align: center;"><b>Tebliğ Aldım</b><br>{o}</div>
                    </div>
                </div><hr style="margin: 30px 0;">
                """
            st.markdown(tum_ogretmenler_html, unsafe_allow_html=True)
    else:
        st.info("Lütfen önce 'Veri & Kısıt Yönetimi' menüsünden programı hesaplayın.")

# ==========================================
# 4. GENEL ÇARŞAF TABLOLAR & EXCEL
# ==========================================
elif st.session_state["sayfa"] == "Carsaf":
    st.subheader("📊 Tüm Okulun Genel Çarşaf Listesi ve Excel Çıktısı")
    if st.session_state["sonuclar"]:
        sonuclar = st.session_state["sonuclar"]
        g_saatler = sonuclar["gunluk_saatler"]
        max_saat = max(g_saatler.values())
        
        tab_c1, tab_c2 = st.tabs(["📋 Tüm Sınıflar (Genel Çarşaf)", "👨‍🏫 Tüm Öğretmenler (Genel Çarşaf)"])
        
        with tab_c1:
            satirlar_sinif = []
            for s in sonuclar["siniflar"]:
                for g in gunler:
                    satir = {"Sınıf": s, "Gün": g}
                    g_saat = g_saatler[g]
                    for sa in range(max_saat):
                        if sa < g_saat:
                            val_raw = sonuclar["sinif"][s][g][sa].replace("<div class='lesson-box'>","").replace("</div>","").replace("<small>"," - ").replace("</small>","")
                            satir[f"{sa+1}. Ders"] = val_raw if val_raw else "-"
                        else:
                            satir[f"{sa+1}. Ders"] = "-"
                    satirlar_sinif.append(satir)
            df_carsaf_sinif = pd.DataFrame(satirlar_sinif)
            st.dataframe(df_carsaf_sinif, use_container_width=True, hide_index=True)
            
            buf_s = io.BytesIO()
            with pd.ExcelWriter(buf_s, engine="openpyxl") as w:
                df_carsaf_sinif.to_excel(w, sheet_name="Siniflar_Carsaf", index=False)
            st.download_button("📥 Sınıflar Çarşaf Listesini İndir (.xlsx)", buf_s.getvalue(), "Siniflar_Genel_Carsaf.xlsx", use_container_width=True)

        with tab_c2:
            satirlar_ogr = []
            for ogr in sonuclar["ogretmenler"]:
                for g in gunler:
                    satir = {"Öğretmen": ogr, "Gün": g}
                    g_saat = g_saatler[g]
                    for sa in range(max_saat):
                        if sa < g_saat:
                            val_raw = sonuclar["ogretmen"][ogr][g][sa].replace("<div class='lesson-box'>","").replace("</div>","").replace("<small>"," - ").replace("</small>","")
                            satir[f"{sa+1}. Ders"] = val_raw if val_raw else "-"
                        else:
                            satir[f"{sa+1}. Ders"] = "-"
                    satirlar_ogr.append(satir)
            df_carsaf_ogr = pd.DataFrame(satirlar_ogr)
            st.dataframe(df_carsaf_ogr, use_container_width=True, hide_index=True)
            
            buf_o = io.BytesIO()
            with pd.ExcelWriter(buf_o, engine="openpyxl") as w:
                df_carsaf_ogr.to_excel(w, sheet_name="Ogretmenler_Carsaf", index=False)
            st.download_button("📥 Öğretmenler Çarşaf Listesini İndir (.xlsx)", buf_o.getvalue(), "Ogretmenler_Genel_Carsaf.xlsx", use_container_width=True)
    else:
        st.info("Lütfen önce 'Veri & Kısıt Yönetimi' menüsünden programı hesaplayın.")

# ==========================================
# 5. AKILLI NÖBET & DEĞİŞİM ANALİZİ
# ==========================================
elif st.session_state["sayfa"] == "Nöbet":
    st.subheader("🛡️ Akıllı Nöbet Yönetimi ve Değişim Analizörü")

    if st.session_state["sonuclar"]:
        sonuclar = st.session_state["sonuclar"]
        aktif_ogretmenler = [o for o in sonuclar["ogretmenler"] if not st.session_state["ogretmen_tercih"].get(o,{}).get("muaf", False)]
        
        if aktif_ogretmenler:
            st.markdown("#### 🔄 Nöbet Değişimi & Uygunluk Kontrolü")
            c_n1, c_n2, c_n3 = st.columns([2.5, 2, 2])
            with c_n1:
                sec_ogr = st.selectbox("Öğretmen Seçin", aktif_ogretmenler)
            with c_n2:
                mevcut_nobet = sonuclar["otomatik_nobetler"].get(sec_ogr, "Pazartesi")
                yeni_gun = st.selectbox("Atanacak Nöbet Günü", gunler, index=gunler.index(mevcut_nobet) if mevcut_nobet in gunler else 0)
            with c_n3:
                yeni_yer = st.selectbox("Nöbet Yeri (Excel'den Gelen)", st.session_state["nobet_yerleri"])

            gunluk_dersler = sonuclar["ogretmen_gunluk_ders"][sec_ogr]
            secilen_gun_ders = gunluk_dersler.get(yeni_gun, 0)
            bos_istek = st.session_state["ogretmen_tercih"].get(sec_ogr, {}).get("bos", "")
            en_iyi_gun = max(gunluk_dersler, key=gunluk_dersler.get)
            max_saat = gunluk_dersler[en_iyi_gun]

            if yeni_gun == bos_istek:
                st.error(f"❌ Uygun Değil: {sec_ogr} öğretmeninin {yeni_gun} günü boş gün talebi var.")
            elif secilen_gun_ders == 0:
                st.warning(f"⚠️ Uyarı: {sec_ogr} öğretmeninin {yeni_gun} günü hiç dersi yok. (Öneri: {en_iyi_gun} günü - {max_saat} saat ders)")
            else:
                st.success(f"✓ Uygundur: {sec_ogr} öğretmeninin {yeni_gun} günü {secilen_gun_ders} saat dersi bulunmaktadır.")

            if st.button("💾 Nöbet Değişikliğini Kaydet", type="primary"):
                sonuclar["otomatik_nobetler"][sec_ogr] = yeni_gun
                if sec_ogr in st.session_state["ogretmen_tercih"]:
                    st.session_state["ogretmen_tercih"][sec_ogr]["yer"] = yeni_yer
                st.success(f"{sec_ogr} için nöbet {yeni_gun} ({yeni_yer}) olarak kaydedildi!")
                st.rerun()

        st.markdown("---")
        st.markdown("#### 📅 Haftalık Güncel Nöbet Çizelgesi")
        cols = st.columns(len(gunler))
        for idx, g in enumerate(gunler):
            with cols[idx]:
                st.markdown(f"""
                <div class="nobet-col-card">
                    <div class="nobet-title">📅 {g}</div>
                """, unsafe_allow_html=True)
                
                nobetciler = [o for o, nob_g in sonuclar["otomatik_nobetler"].items() if nob_g == g]
                if nobetciler:
                    for n in nobetciler:
                        yer = st.session_state["ogretmen_tercih"].get(n, {}).get("yer", "Bahçe")
                        saat_d = sonuclar['ogretmen_gunluk_ders'][n].get(g,0)
                        st.markdown(f"""
                        <div class="nobet-teacher-pill">
                            <span><b>{n}</b> <small>({saat_d} Sa)</small></span>
                            <span class="location-tag">{yer}</span>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.caption("Nöbetçi atanmadı")
                
                st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Lütfen önce 'Veri & Kısıt Yönetimi' menüsünden programı hesaplayın.")

# ==========================================
# 6. HATA & TALEP BİLDİR (GÜVENLİ E-POSTA BAĞLANTISI)
# ==========================================
elif st.session_state["sayfa"] == "HataBildir":
    st.subheader("💬 Okul Hata, Sorun & Talep Bildirim Merkezi")
    st.markdown("Karşılaştığınız hataları veya sistem önerilerinizi doğrudan Iğdır AR-GE birimine (**76etwinning@gmail.com**) e-posta olarak iletebilirsiniz.")
    
    with st.form("hata_formu"):
        okul_adi = st.text_input("Okul / Kurum Adı", placeholder="Örn: Iğdır Anadolu Lisesi")
        bildiren = st.text_input("Ad Soyad / Unvan", placeholder="Örn: Müdür Yardımcısı Ahmet Bey")
        kategori = st.selectbox("Bildirim Türü", ["Hata / Çalışmayan Özellik", "Öneri / Talep", "Excel Yükleme Sorunu", "Diğer"])
        mesaj = st.text_area("Mesajınız / Sorun Açıklaması", placeholder="Lütfen karşılaştığınız durumu detaylıca yazın...")
        
        gonder_btn = st.form_submit_button("📨 E-Posta ile Gönder", type="primary")
        if gonder_btn:
            if okul_adi and mesaj:
                konu = f"Okul Planlama Bildirimi: [{kategori}] - {okul_adi}"
                govde = f"Okul: {okul_adi}\nBildiren: {bildiren}\nTarih: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\nMesaj:\n{mesaj}"
                
                mailto_link = f"mailto:76etwinning@gmail.com?subject={urllib.parse.quote(konu)}&body={urllib.parse.quote(govde)}"
                
                st.success("✓ Bildirim taslağınız hazırlandı!")
                st.markdown(f'<a href="{mailto_link}" target="_blank" style="display:inline-block; background-color:#0284c7; color:#ffffff; padding:10px 20px; border-radius:8px; text-decoration:none; font-weight:700; margin-top:10px;">📧 E-Postayı Göndermek İçin Tıklayın (76etwinning@gmail.com)</a>', unsafe_allow_html=True)
            else:
                st.error("Lütfen Okul Adı ve Mesaj alanlarını doldurun.")

# ==========================================
# 7. GÜNCELLEME GEÇMİŞİ (CHANGELOG)
# ==========================================
elif st.session_state["sayfa"] == "Guncellemeler":
    st.subheader("📜 Sürüm ve Geliştirme Günlüğü")
    st.caption("Sisteme yapılan yeni eklemeler ve güncellemeler burada listelenir:")
    
    for b in st.session_state["bildirimler"]:
        st.markdown(f"""
        <div style="background: #ffffff; border: 1px solid #e2e8f0; padding: 16px; border-radius: 10px; border-left: 4px solid #0284c7; margin-bottom: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <b style="color: #0f172a; font-size: 15px;">{b['baslik']}</b>
                <small style="color: #64748b; font-weight: 600;">{b['tarih']}</small>
            </div>
            <p style="color: #334155; font-size: 13px; margin: 0;">{b['icerik']}</p>
        </div>
        """, unsafe_allow_html=True)