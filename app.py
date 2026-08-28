import streamlit as st
import pandas as pd
from ortools.sat.python import cp_model
import io
import os
import json
from datetime import datetime

st.set_page_config(
    page_title="Iğdır MEM AR-GE - Akıllı Okul Planlama Sistemi", 
    layout="wide", 
    page_icon="🏫"
)

# Kalıcı Veri Klasörü
DATA_DIR = "okul_verileri"
FEEDBACK_FILE = "okul_verileri/sistem_bildirimleri.json"

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def veri_kaydet(kurum_kodu, veri_dict):
    dosya_yolu = os.path.join(DATA_DIR, f"{kurum_kodu}.json")
    with open(dosya_yolu, "w", encoding="utf-8") as f:
        json.dump(veri_dict, f, ensure_ascii=False, indent=2)

def veri_yukle(kurum_kodu):
    dosya_yolu = os.path.join(DATA_DIR, f"{kurum_kodu}.json")
    if os.path.exists(dosya_yolu):
        with open(dosya_yolu, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def bildirim_kaydet(yeni_bildirim):
    mevcut = []
    if os.path.exists(FEEDBACK_FILE):
        try:
            with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
                mevcut = json.load(f)
        except:
            mevcut = []
    mevcut.insert(0, yeni_bildirim)
    with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
        json.dump(mevcut, f, ensure_ascii=False, indent=2)

def bildirimleri_getir():
    if os.path.exists(FEEDBACK_FILE):
        try:
            with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

# Oturum Durumu Başlatma
if "giris_yapildi" not in st.session_state:
    st.session_state["giris_yapildi"] = False

if "kurum_kodu" not in st.session_state:
    st.session_state["kurum_kodu"] = ""

if "okul_adi" not in st.session_state:
    st.session_state["okul_adi"] = ""

if "sayfa" not in st.session_state:
    st.session_state["sayfa"] = "Veri"

if "dersler" not in st.session_state:
    st.session_state["dersler"] = []

if "ogretmen_tercih" not in st.session_state:
    st.session_state["ogretmen_tercih"] = {}

if "nobet_yerleri" not in st.session_state:
    st.session_state["nobet_yerleri"] = ["Bahçe", "Zemin Kat", "1. Kat", "2. Kat"]

if "sonuclar" not in st.session_state:
    st.session_state["sonuclar"] = None

if "aylik_nobet_gecmisi" not in st.session_state:
    st.session_state["aylik_nobet_gecmisi"] = {}

gunler = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"]

tum_bildirimler = [
    {"tarih": "2026-08-28", "baslik": "v3.6 - Temiz Kurumsal Arayüz", "icerik": "Giriş ekranı ve logo render hataları giderildi, kurumsal yapı stabilize edildi."},
    {"tarih": "2026-08-28", "baslik": "v3.5 - Eşit Dağıtımlı Aylık Nöbet & Gizli AR-GE Paneli", "icerik": "Nöbetlerin günlere eşit dağıtımı, eksik kadroda çoklu nöbet rotasyonu ve şifreli AR-GE gelen kutusu eklendi."},
    {"tarih": "2026-08-28", "baslik": "v3.4 - Kurumsal Okul Oturumu & Kalıcı Hafıza", "icerik": "MEB Kurum Kodu ile okul profili sistemi getirildi. Programlar ve öğretmen değişiklikleri hafızaya kaydediliyor."},
    {"tarih": "2026-08-27", "baslik": "v3.3 - Akıllı Haftalık Saat Dağıtımı", "icerik": "Ders saatleri doğrudan Excel'deki yükten hesaplanacak şekilde otomatikleştirildi; artık gün tercihi eklendi."}
]

# ==========================================
# GİRİŞ EKRANI
# ==========================================
if not st.session_state["giris_yapildi"]:
    _, col_main, _ = st.columns([1, 2, 1])
    with col_main:
        st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/Meb.png/180px-Meb.png", width=100)
        st.title("Iğdır İl Millî Eğitim Müdürlüğü")
        st.subheader("AR-GE BİRİMİ")
        st.caption("Akıllı Okul Ders & Nöbet Dağıtım Sistemi")
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("---")
        girilen_kod = st.text_input("MEB Kurum Kodu", placeholder="Kurum kodunu yazınız...")
        girilen_okul = st.text_input("Kurum İsmi", placeholder="Kurumun tam adını yazınız...")
        
        if st.button("🚀 Kurumsal Giriş Yap", type="primary", use_container_width=True):
            if girilen_kod.strip() and girilen_okul.strip():
                st.session_state["giris_yapildi"] = True
                st.session_state["kurum_kodu"] = girilen_kod.strip()
                st.session_state["okul_adi"] = girilen_okul.strip()
                
                kayitli_veri = veri_yukle(girilen_kod.strip())
                if kayitli_veri:
                    st.session_state["dersler"] = kayitli_veri.get("dersler", [])
                    st.session_state["ogretmen_tercih"] = kayitli_veri.get("ogretmen_tercih", {})
                    st.session_state["nobet_yerleri"] = kayitli_veri.get("nobet_yerleri", ["Bahçe", "Zemin Kat", "1. Kat", "2. Kat"])
                    st.session_state["sonuclar"] = kayitli_veri.get("sonuclar", None)
                    st.session_state["aylik_nobet_gecmisi"] = kayitli_veri.get("aylik_nobet_gecmisi", {})
                    st.success("✓ Kurum verileri yüklendi!")
                else:
                    st.info("ℹ️ Yeni kurum kaydı oluşturuldu.")
                st.rerun()
            else:
                st.error("Lütfen MEB Kurum Kodu ve Kurum İsmi alanlarını doldurun.")

        st.markdown("---")
        st.markdown("#### 📢 Son Sistem Güncellemeleri & Duyurular")
        for b in tum_bildirimler[:4]:
            with st.container():
                st.markdown(f"**{b['baslik']}** — *{b['tarih']}*")
                st.caption(b['icerik'])
        
    st.stop()

# ==========================================
# ANA PANEL
# ==========================================

sinif_yukleri = {}
for d in st.session_state["dersler"]:
    s = d.get("Sınıf", "")
    bloklar = str(d.get("Saat Dağılımı", "2")).split("+")
    toplam_s = sum([int(b.strip()) for b in bloklar if b.strip().isdigit()])
    if s:
        sinif_yukleri[s] = sinif_yukleri.get(s, 0) + toplam_s

max_sinif_yuku = max(sinif_yukleri.values()) if sinif_yukleri else 35

with st.sidebar:
    st.markdown(f"### 🏫 {st.session_state['okul_adi']}")
    st.caption(f"Kurum Kodu: **{st.session_state['kurum_kodu']}**")
    if st.button("🚪 Çıkış Yap", use_container_width=True):
        st.session_state["giris_yapildi"] = False
        st.rerun()
        
    st.markdown("---")
    menuler = [
        ("✏️ Veri & Öğretmen Hafızası", "Veri"),
        ("🎓 Sınıf Programları", "Sınıflar"),
        ("👨‍🏫 Öğretmen Programları (A4)", "Öğretmenler"),
        ("📊 Genel Çarşaf Tablo & Excel", "Carsaf"),
        ("🛡️ Aylık Eşit Nöbet Dağıtımı", "Nöbet"),
        ("💬 Hata & Talep Bildir", "HataBildir"),
        ("🔒 AR-GE Yönetici Paneli", "YoneticiPanel")
    ]
    
    for baslik, key in menuler:
        if st.button(baslik, use_container_width=True, type="primary" if st.session_state["sayfa"] == key else "secondary"):
            st.session_state["sayfa"] = key
            st.rerun()

    st.markdown("---")
    st.subheader("⚙️ Akıllı Saat Dağıtımı")
    taban_saat = max_sinif_yuku // 5
    kalan_saat = max_sinif_yuku % 5
    
    if kalan_saat > 0:
        st.caption(f"Haftalık {max_sinif_yuku} saat ({taban_saat} + 1)")
        artik_gunler = st.multiselect("Artık ders günleri:", options=gunler, default=gunler[:kalan_saat], max_selections=kalan_saat)
    else:
        artik_gunler = []

    gunluk_saatler = {g: (taban_saat + 1) if g in artik_gunler else taban_saat for g in gunler}

st.markdown(f"""
<div style="background: linear-gradient(135deg, #0284c7 0%, #2563eb 50%, #1d4ed8 100%); border-radius: 12px; padding: 18px 24px; color: white; display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
    <div>
        <h3 style="margin: 0; color: white;">{st.session_state['okul_adi']}</h3>
        <span style="font-size: 13px; color: #e0f2fe;">Akıllı Okul Planlama Sistemi • Kurum Kodu: {st.session_state['kurum_kodu']}</span>
    </div>
    <div style="background: white; color: #0284c7; padding: 4px 12px; border-radius: 20px; font-weight: 800; font-size: 12px;">Iğdır MEM AR-GE</div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 1. VERİ & ÖĞRETMEN HAFIZASI
# ==========================================
if st.session_state["sayfa"] == "Veri":
    st.subheader("📥 Veri Girişi & Okul Hafızası")
    
    mevcut_ogretmenler = sorted(list(set([d["Öğretmen"] for d in st.session_state["dersler"]])))
    if mevcut_ogretmenler:
        with st.expander("🔄 Hızlı Öğretmen Değişimi (Öğretmen Ayrıldı / Yeni Öğretmen Geldi)", expanded=False):
            c_dev1, c_dev2, c_dev3 = st.columns([2, 2, 1.5])
            with c_dev1:
                giden_ogr = st.selectbox("Ayrılan Öğretmen", mevcut_ogretmenler)
            with c_dev2:
                yeni_ogr = st.text_input("Yeni Öğretmenin Adı", placeholder="Örn: Mehmet Demir")
            with c_dev3:
                st.write("")
                st.write("")
                if st.button("🔄 Devret ve Kaydet", use_container_width=True):
                    if yeni_ogr.strip():
                        yeni_ad = yeni_ogr.strip()
                        for d in st.session_state["dersler"]:
                            if d["Öğretmen"] == giden_ogr:
                                d["Öğretmen"] = yeni_ad
                        if giden_ogr in st.session_state["ogretmen_tercih"]:
                            st.session_state["ogretmen_tercih"][yeni_ad] = st.session_state["ogretmen_tercih"].pop(giden_ogr)
                        
                        veri_kaydet(st.session_state["kurum_kodu"], {
                            "dersler": st.session_state["dersler"],
                            "ogretmen_tercih": st.session_state["ogretmen_tercih"],
                            "nobet_yerleri": st.session_state["nobet_yerleri"],
                            "sonuclar": st.session_state["sonuclar"],
                            "aylik_nobet_gecmisi": st.session_state["aylik_nobet_gecmisi"]
                        })
                        st.success(f"✓ {giden_ogr} öğretmeninin dersleri {yeni_ad} öğretmenine devredildi!")
                        st.rerun()

    c_card1, c_card2 = st.columns([1, 1])
    with c_card1:
        st.markdown("##### 📥 Excel Şablonu")
        sablon_d = st.session_state["dersler"] if st.session_state["dersler"] else [{"Sınıf": "9-A", "Ders": "Matematik", "Öğretmen": "Ahmet Yılmaz", "Saat Dağılımı": "2+2+2"}]
        sablon_o = [{"Öğretmen": k, "Boş Gün İsteği": v.get("bos", ""), "Zaman Kısıtı": v.get("zaman", "Tüm Gün"), "Nöbetten Muaf": "Evet" if v.get("muaf") else "Hayır"} for k, v in st.session_state["ogretmen_tercih"].items()] if st.session_state["ogretmen_tercih"] else [{"Öğretmen": "Ahmet Yılmaz", "Boş Gün İsteği": "", "Zaman Kısıtı": "Tüm Gün", "Nöbetten Muaf": "Hayır"}]
        sablon_yerler = [{"Nöbet Yeri Adı": y} for y in st.session_state["nobet_yerleri"] if y != "-"]
        
        buf_sablon = io.BytesIO()
        with pd.ExcelWriter(buf_sablon, engine="openpyxl") as writer:
            pd.DataFrame(sablon_d).to_excel(writer, sheet_name="Ders_Listesi", index=False)
            pd.DataFrame(sablon_o).to_excel(writer, sheet_name="Ogretmenler", index=False)
            pd.DataFrame(sablon_yerler).to_excel(writer, sheet_name="Nobet_Yerleri", index=False)
        
        st.download_button("📥 Excel Şablonunu İndir (.xlsx)", buf_sablon.getvalue(), f"Okul_Sablon_{st.session_state['kurum_kodu']}.xlsx", use_container_width=True)

    with c_card2:
        st.markdown("##### 📤 Doldurulan Excel'i Yükle")
        uploaded_file = st.file_uploader("Dosyayı buraya bırakın", type=["xlsx", "xls"])
        if uploaded_file is not None:
            try:
                xls = pd.ExcelFile(uploaded_file)
                df_d = pd.read_excel(xls, sheet_name="Ders_Listesi").fillna("")
                df_o = pd.read_excel(xls, sheet_name="Ogretmenler").fillna("") if "Ogretmenler" in xls.sheet_names else pd.DataFrame()
                
                if "Nobet_Yerleri" in xls.sheet_names:
                    df_y = pd.read_excel(xls, sheet_name="Nobet_Yerleri").fillna("")
                    yerler = [str(r).strip() for r in df_y["Nöbet Yeri Adı"].tolist() if str(r).strip()]
                    if yerler:
                        st.session_state["nobet_yerleri"] = yerler
                
                st.session_state["dersler"] = df_d[["Sınıf", "Ders", "Öğretmen", "Saat Dağılımı"]].to_dict("records")
                st.session_state["ogretmen_tercih"] = {}
                for _, row in df_o.iterrows():
                    ogr = str(row.get("Öğretmen", "")).strip()
                    if ogr:
                        is_muaf = str(row.get("Nöbetten Muaf", "")).strip().lower() in ["evet", "true", "1"]
                        st.session_state["ogretmen_tercih"][ogr] = {
                            "bos": str(row.get("Boş Gün İsteği", "")).strip(),
                            "zaman": str(row.get("Zaman Kısıtı", "Tüm Gün")).strip() or "Tüm Gün",
                            "muaf": is_muaf
                        }
                
                veri_kaydet(st.session_state["kurum_kodu"], {
                    "dersler": st.session_state["dersler"],
                    "ogretmen_tercih": st.session_state["ogretmen_tercih"],
                    "nobet_yerleri": st.session_state["nobet_yerleri"],
                    "sonuclar": st.session_state["sonuclar"],
                    "aylik_nobet_gecmisi": st.session_state["aylik_nobet_gecmisi"]
                })
                st.success("✓ Veriler aktarıldı ve okul hafızasına kaydedildi!")
                st.rerun()
            except Exception as e:
                st.error(f"Excel şablon formatı geçersiz: {e}")

    st.markdown("---")

    with st.expander("➕ Ekrandan Hızlı Tekil Ders Ekle", expanded=False):
        c1, c2, c3, c4, c5 = st.columns([1.5, 2, 2.5, 2, 1.5])
        with c1:
            in_sinif = st.text_input("Sınıf", placeholder="Örn: 9-A")
        with c2:
            in_ders = st.text_input("Ders Adı", placeholder="Örn: Matematik")
        with c3:
            in_ogr = st.text_input("Öğretmen", placeholder="Örn: Selin Korkmaz")
        with c4:
            in_blok = st.selectbox("Saat Dağılımı (Blok)", ["2+2+2 (6 Sa)", "2+2 (4 Sa)", "2+2+1 (5 Sa)", "2+1 (3 Sa)", "2 (2 Sa)", "1 (1 Sa)", "3+3 (6 Sa)", "3 (3 Sa)"])
            temiz_blok = in_blok.split(" ")[0]
        with c5:
            st.write("")
            st.write("")
            if st.button("➕ Ekle", use_container_width=True):
                if in_sinif and in_ders and in_ogr:
                    st.session_state["dersler"].append({"Sınıf": in_sinif.strip().upper(), "Ders": in_ders.strip(), "Öğretmen": in_ogr.strip(), "Saat Dağılımı": temiz_blok})
                    if in_ogr.strip() not in st.session_state["ogretmen_tercih"]:
                        st.session_state["ogretmen_tercih"][in_ogr.strip()] = {"bos": "", "zaman": "Tüm Gün", "muaf": False}
                    veri_kaydet(st.session_state["kurum_kodu"], {
                        "dersler": st.session_state["dersler"], "ogretmen_tercih": st.session_state["ogretmen_tercih"], "nobet_yerleri": st.session_state["nobet_yerleri"], "sonuclar": st.session_state["sonuclar"], "aylik_nobet_gecmisi": st.session_state["aylik_nobet_gecmisi"]
                    })
                    st.rerun()

    c_th1, c_th2 = st.columns([4, 1])
    with c_th1:
        st.markdown(f"##### 📋 Tanımlı Ders Listesi ({len(st.session_state['dersler'])} Ders)")
    with c_th2:
        if st.button("🗑️ Verileri Sıfırla", use_container_width=True):
            st.session_state["dersler"] = []
            st.session_state["ogretmen_tercih"] = {}
            st.session_state["sonuclar"] = None
            veri_kaydet(st.session_state["kurum_kodu"], {"dersler": [], "ogretmen_tercih": {}, "nobet_yerleri": st.session_state["nobet_yerleri"], "sonuclar": None, "aylik_nobet_gecmisi": {}})
            st.rerun()

    if st.session_state["dersler"]:
        arama_kelimesi = st.text_input("🔍 Listede Ara:", placeholder="Örn: Matematik, Selin, 9-A...", key="srch_main")
        df_dersler = pd.DataFrame(st.session_state["dersler"])
        if arama_kelimesi:
            df_goster = df_dersler[df_dersler["Sınıf"].str.contains(arama_kelimesi, case=False, na=False) | df_dersler["Ders"].str.contains(arama_kelimesi, case=False, na=False) | df_dersler["Öğretmen"].str.contains(arama_kelimesi, case=False, na=False)]
        else:
            df_goster = df_dersler
        st.dataframe(df_goster, use_container_width=True, hide_index=True)

    if st.session_state["dersler"]:
        with st.expander("🛡️ Öğretmen İzin & Zaman Kısıtları", expanded=False):
            ogr_filtre = st.text_input("🔍 Öğretmen Ara:", placeholder="İsim...", key="filter_ogr_kisit")
            gosterilecek_ogretmenler = [o for o in mevcut_ogretmenler if ogr_filtre.lower() in o.lower()] if ogr_filtre else mevcut_ogretmenler

            for ogr in gosterilecek_ogretmenler:
                if ogr not in st.session_state["ogretmen_tercih"]:
                    st.session_state["ogretmen_tercih"][ogr] = {"bos": "", "zaman": "Tüm Gün", "muaf": False}
                
                c_o1, c_o2, c_o3, c_o4 = st.columns([3, 2.5, 2.5, 1.5])
                with c_o1:
                    st.write(f"**{ogr}**")
                with c_o2:
                    st.session_state["ogretmen_tercih"][ogr]["bos"] = st.selectbox(
                        f"Boş Gün ({ogr})", ["", "Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"],
                        index=["", "Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"].index(st.session_state["ogretmen_tercih"][ogr].get("bos", "")),
                        label_visibility="collapsed"
                    )
                with c_o3:
                    st.session_state["ogretmen_tercih"][ogr]["zaman"] = st.selectbox(
                        f"Zaman ({ogr})", ["Tüm Gün", "Sadece Sabah", "Sadece Öğle"],
                        index=["Tüm Gün", "Sadece Sabah", "Sadece Öğle"].index(st.session_state["ogretmen_tercih"][ogr].get("zaman", "Tüm Gün")),
                        label_visibility="collapsed"
                    )
                with c_o4:
                    st.session_state["ogretmen_tercih"][ogr]["muaf"] = st.checkbox("Nöbetten Muaf", value=st.session_state["ogretmen_tercih"][ogr].get("muaf", False), key=f"chk_m_{ogr}")

    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("🚀 Çakışmasız Ders Programını Hesapla ve Okul Hafızasına Kaydet", type="primary", use_container_width=True):
        dersler = [d for d in st.session_state["dersler"] if str(d.get("Sınıf","")).strip() and str(d.get("Öğretmen","")).strip()]
        if not dersler:
            st.error("Lütfen önce ders verisi ekleyin.")
        else:
            with st.spinner("Optimizasyon motoru çalışıyor..."):
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
                        blok_listesi.append({"sinif": d["Sınıf"], "ders": d["Ders"], "ogretmen": d["Öğretmen"], "sure": sure})

                model = cp_model.CpModel()
                x = {}
                for b_idx, blok in enumerate(blok_listesi):
                    for t in range(toplam_saat):
                        x[(b_idx, t)] = model.NewBoolVar(f"b_{b_idx}_t_{t}")

                for b_idx, blok in enumerate(blok_listesi):
                    gecerli = []
                    for g in gunler:
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
                    for g in gunler:
                        g_bas = gun_baslangic[g]
                        g_sayi = gunluk_saatler[g]
                        for sa in range(1, g_sayi):
                            t = g_bas + sa
                            akt_t = sum([x[(b_idx, t - off)] for b_idx, blok in enumerate(blok_listesi) if blok["sinif"] == s for off in range(blok["sure"]) if t - off >= 0])
                            akt_p = sum([x[(b_idx, (t-1) - off)] for b_idx, blok in enumerate(blok_listesi) if blok["sinif"] == s for off in range(blok["sure"]) if (t-1) - off >= 0])
                            model.Add(akt_t <= akt_p)

                for ogr in ogretmenler:
                    trc = st.session_state["ogretmen_tercih"].get(ogr, {})
                    bos_g = trc.get("bos", "")
                    zaman = trc.get("zaman", "Tüm Gün")

                    for g in gunler:
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
                        "toplam_ders_saati": sum(b["sure"] for b in blok_listesi),
                        "gunluk_saatler": gunluk_saatler,
                        "gun_baslangic": gun_baslangic
                    }

                    for g in gunler:
                        g_bas = gun_baslangic[g]
                        g_sayi = gunluk_saatler[g]
                        for saat in range(g_sayi):
                            t = g_bas + saat
                            for b_idx, blok in enumerate(blok_listesi):
                                for off in range(blok["sure"]):
                                    if t - off >= 0 and solver.Value(x[(b_idx, t - off)]) == 1:
                                        sonuclar["sinif"][blok["sinif"]][gun][saat] = f"<div style='background:#f0f9ff; border:1px solid #bae6fd; border-radius:6px; padding:4px; color:#0369a1; font-weight:600;'>{blok['ders']}<small style='display:block; color:#0284c7;'>{blok['ogretmen']}</small></div>"
                                        sonuclar["ogretmen"][blok["ogretmen"]][gun][saat] = f"<div style='background:#f0f9ff; border:1px solid #bae6fd; border-radius:6px; padding:4px; color:#0369a1; font-weight:600;'>{blok['sinif']}<small style='display:block; color:#0284c7;'>{blok['ders']}</small></div>"
                                        sonuclar["ogretmen_gunluk_ders"][blok["ogretmen"]][gun] += 1
                    
                    st.session_state["sonuclar"] = sonuclar
                    
                    veri_kaydet(st.session_state["kurum_kodu"], {
                        "dersler": st.session_state["dersler"],
                        "ogretmen_tercih": st.session_state["ogretmen_tercih"],
                        "nobet_yerleri": st.session_state["nobet_yerleri"],
                        "sonuclar": sonuclar,
                        "aylik_nobet_gecmisi": st.session_state["aylik_nobet_gecmisi"]
                    })
                    st.success("✓ Ders Programı Başarıyla Oluşturuldu ve Kaydedildi!")
                else:
                    st.session_state["sonuclar"] = None
                    st.error("✗ Çakışmasız çözüm bulunamadı. Lütfen kısıtları kontrol edin.")

# ==========================================
# 2. SINIF PROGRAMLARI
# ==========================================
elif st.session_state["sayfa"] == "Sınıflar":
    st.subheader(f"🎓 {st.session_state['okul_adi']} - Sınıf Ders Programları")
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
                secili_s = st.selectbox("Sınıf Seçin:", filtrelenen_siniflar)
            if secili_s:
                html = "<table style='width:100%; border-collapse:separate; border-spacing:6px;'><tr><th style='background:#1e293b; color:white; padding:10px; border-radius:6px;'>Gün</th>" + "".join([f"<th style='background:#1e293b; color:white; padding:10px; border-radius:6px;'>{i+1}. Ders</th>" for i in range(max_saat)]) + "</tr>"
                for g in gunler:
                    g_saat = g_saatler[g]
                    html += f"<tr><td style='background:#f1f5f9; font-weight:700; text-align:center; padding:8px; border-radius:6px;'>{g} ({g_saat} Sa)</td>"
                    for sa in range(max_saat):
                        if sa < g_saat:
                            val = sonuclar["sinif"][secili_s][g][sa]
                            html += f"<td style='background:white; border:1px solid #e2e8f0; text-align:center; padding:6px; border-radius:6px; height:50px;'>{val if val else '-'}</td>"
                        else:
                            html += "<td style='background:#f8fafc; border:1px solid #e2e8f0; text-align:center; padding:6px; border-radius:6px; color:#cbd5e1;'>-</td>"
                    html += "</tr>"
                html += "</table>"
                st.markdown(html, unsafe_allow_html=True)
    else:
        st.info("Kayıtlı program bulunamadı.")

# ==========================================
# 3. ÖĞRETMEN PROGRAMLARI
# ==========================================
elif st.session_state["sayfa"] == "Öğretmenler":
    st.subheader(f"👨‍🏫 {st.session_state['okul_adi']} - Öğretmen Ders Programları & Tebliğ")
    if st.session_state["sonuclar"]:
        sonuclar = st.session_state["sonuclar"]
        g_saatler = sonuclar["gunluk_saatler"]
        max_saat = max(g_saatler.values())
        
        tab_tek, tab_toplu = st.tabs(["📄 Tek Öğretmen Yazdır", "📑 Tüm Öğretmenleri Toplu Yazdır (A4)"])
        with tab_tek:
            c_o_srch, c_o_sel, c_btn = st.columns([1.5, 2, 1.5])
            with c_o_srch:
                ara_ogr = st.text_input("🔍 Öğretmen Ara:", placeholder="İsim...", key="srch_ogr_tek")
            filtrelenen_ogretmenler = [o for o in sonuclar["ogretmenler"] if ara_ogr.lower() in o.lower()] if ara_ogr else sonuclar["ogretmenler"]
            
            if filtrelenen_ogretmenler:
                with c_o_sel:
                    secili_o = st.selectbox("Öğretmen Seç:", filtrelenen_ogretmenler)
                with c_btn:
                    st.write("")
                    st.write("")
                    st.button("🖨️ Yazdır (Ctrl + P)", use_container_width=True)
                
                if secili_o:
                    toplam_ogr_ders = sum(sonuclar["ogretmen_gunluk_ders"][secili_o].values())
                    st.markdown(f"**Öğretmen:** {secili_o} | **Haftalık Ders Yükü:** {toplam_ogr_ders} Saat")
                    
                    html = "<table style='width:100%; border-collapse:separate; border-spacing:6px;'><tr><th style='background:#1e293b; color:white; padding:10px; border-radius:6px;'>Gün</th>" + "".join([f"<th style='background:#1e293b; color:white; padding:10px; border-radius:6px;'>{i+1}. Ders</th>" for i in range(max_saat)]) + "</tr>"
                    for g in gunler:
                        g_saat = g_saatler[g]
                        html += f"<tr><td style='background:#f1f5f9; font-weight:700; text-align:center; padding:8px; border-radius:6px;'>{g}</td>"
                        for sa in range(max_saat):
                            if sa < g_saat:
                                val = sonuclar["ogretmen"][secili_o][g][sa]
                                html += f"<td style='background:white; border:1px solid #e2e8f0; text-align:center; padding:6px; border-radius:6px; height:50px;'>{val if val else '-'}</td>"
                            else:
                                html += "<td style='background:#f8fafc; border:1px solid #e2e8f0; text-align:center; padding:6px; border-radius:6px; color:#cbd5e1;'>-</td>"
                        html += "</tr>"
                    html += "</table>"
                    html += f"""
                    <div style="margin-top:20px; display:flex; justify-content:space-between; padding:15px 40px; border-top:2px dashed #cbd5e1; background:white;">
                        <div style="text-align: center;"><b>Teslim Eden</b><br>{st.session_state['okul_adi']} Müdürü<br>İmza / Mühür</div>
                        <div style="text-align: center;"><b>Tebliğ Aldım</b><br>{secili_o}<br>Tarih: ..... / ..... / 202...</div>
                    </div>
                    """
                    st.markdown(html, unsafe_allow_html=True)
        
        with tab_toplu:
            st.button("🖨️ Tüm Öğretmenleri Toplu Yazdır (PDF / Çıktı)", use_container_width=True)
            tum_ogretmenler_html = ""
            for o in sonuclar["ogretmenler"]:
                toplam_ogr_ders = sum(sonuclar["ogretmen_gunluk_ders"][o].values())
                tum_ogretmenler_html += f"""
                <div style="page-break-after: always; padding-top: 15px;">
                    <div style="border-bottom: 2px solid #334155; padding-bottom: 8px; margin-bottom: 12px; display: flex; justify-content: space-between;">
                        <span style="font-size: 16px; font-weight: 800;">{st.session_state['okul_adi']} - Öğretmen: {o}</span>
                        <span><b>Yük:</b> {toplam_ogr_ders} Saat</span>
                    </div>
                    <table style='width:100%; border-collapse:separate; border-spacing:6px;'><tr><th style='background:#1e293b; color:white; padding:8px; border-radius:6px;'>Gün</th>""" + "".join([f"<th style='background:#1e293b; color:white; padding:8px; border-radius:6px;'>{i+1}. Ders</th>" for i in range(max_saat)]) + "</tr>"
                for g in gunler:
                    g_saat = g_saatler[g]
                    tum_ogretmenler_html += f"<tr><td style='background:#f1f5f9; font-weight:700; text-align:center; padding:6px; border-radius:6px;'>{g}</td>"
                    for sa in range(max_saat):
                        if sa < g_saat:
                            val = sonuclar["ogretmen"][o][g][sa]
                            tum_ogretmenler_html += f"<td style='background:white; border:1px solid #e2e8f0; text-align:center; padding:6px; border-radius:6px;'>{val if val else '-'}</td>"
                        else:
                            tum_ogretmenler_html += "<td style='background:#f8fafc; border:1px solid #e2e8f0; text-align:center; padding:6px; border-radius:6px; color:#cbd5e1;'>-</td>"
                    tum_ogretmenler_html += "</tr>"
                tum_ogretmenler_html += f"""
                    </table>
                    <div style="margin-top:20px; display:flex; justify-content:space-between; padding:15px 40px; border-top:2px dashed #cbd5e1; background:white;">
                        <div style="text-align: center;"><b>Teslim Eden</b><br>Okul Müdürü</div>
                        <div style="text-align: center;"><b>Tebliğ Aldım</b><br>{o}</div>
                    </div>
                </div><hr style="margin: 30px 0;">
                """
            st.markdown(tum_ogretmenler_html, unsafe_allow_html=True)
    else:
        st.info("Kayıtlı program bulunamadı.")

# ==========================================
# 4. GENEL ÇARŞAF TABLOLAR & EXCEL
# ==========================================
elif st.session_state["sayfa"] == "Carsaf":
    st.subheader(f"📊 {st.session_state['okul_adi']} - Genel Çarşaf Listesi")
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
                            val_raw = sonuclar["sinif"][s][g][sa].replace("<div style='background:#f0f9ff; border:1px solid #bae6fd; border-radius:6px; padding:4px; color:#0369a1; font-weight:600;'>","").replace("</div>","").replace("<small style='display:block; color:#0284c7;'>"," - ").replace("</small>","")
                            satir[f"{sa+1}. Ders"] = val_raw if val_raw else "-"
                        else:
                            satir[f"{sa+1}. Ders"] = "-"
                    satirlar_sinif.append(satir)
            df_carsaf_sinif = pd.DataFrame(satirlar_sinif)
            st.dataframe(df_carsaf_sinif, use_container_width=True, hide_index=True)
            
            buf_s = io.BytesIO()
            with pd.ExcelWriter(buf_s, engine="openpyxl") as w:
                df_carsaf_sinif.to_excel(w, sheet_name="Siniflar_Carsaf", index=False)
            st.download_button("📥 Sınıflar Çarşafını İndir (.xlsx)", buf_s.getvalue(), f"Siniflar_Carsaf_{st.session_state['kurum_kodu']}.xlsx", use_container_width=True)

        with tab_c2:
            satirlar_ogr = []
            for ogr in sonuclar["ogretmenler"]:
                for g in gunler:
                    satir = {"Öğretmen": ogr, "Gün": g}
                    g_saat = g_saatler[g]
                    for sa in range(max_saat):
                        if sa < g_saat:
                            val_raw = sonuclar["ogretmen"][ogr][g][sa].replace("<div style='background:#f0f9ff; border:1px solid #bae6fd; border-radius:6px; padding:4px; color:#0369a1; font-weight:600;'>","").replace("</div>","").replace("<small style='display:block; color:#0284c7;'>"," - ").replace("</small>","")
                            satir[f"{sa+1}. Ders"] = val_raw if val_raw else "-"
                        else:
                            satir[f"{sa+1}. Ders"] = "-"
                    satirlar_ogr.append(satir)
            df_carsaf_ogr = pd.DataFrame(satirlar_ogr)
            st.dataframe(df_carsaf_ogr, use_container_width=True, hide_index=True)
            
            buf_o = io.BytesIO()
            with pd.ExcelWriter(buf_o, engine="openpyxl") as w:
                df_carsaf_ogr.to_excel(w, sheet_name="Ogretmenler_Carsaf", index=False)
            st.download_button("📥 Öğretmenler Çarşafını İndir (.xlsx)", buf_o.getvalue(), f"Ogretmenler_Carsaf_{st.session_state['kurum_kodu']}.xlsx", use_container_width=True)
    else:
        st.info("Kayıtlı program bulunamadı.")

# ==========================================
# 5. AYLIK EŞİT NÖBET DAĞITIMI
# ==========================================
elif st.session_state["sayfa"] == "Nöbet":
    st.subheader("🛡️ Akıllı Aylık Eşit Nöbet Dağıtım Motoru")
    st.caption("Her güne nöbet yerleri kadar eşit sayıda öğretmen atanır. Kadro azsa öğretmenlere birden fazla nöbet yazılır.")

    if st.session_state["sonuclar"]:
        sonuclar = st.session_state["sonuclar"]
        ogretmenler = [o for o in sonuclar["ogretmenler"] if not st.session_state["ogretmen_tercih"].get(o, {}).get("muaf", False)]
        yerler = st.session_state["nobet_yerleri"]
        
        c_ay1, c_ay2 = st.columns([2, 2])
        with c_ay1:
            secili_ay = st.selectbox("Planlanacak Ay:", ["Eylül", "Ekim", "Kasım", "Aralık", "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran"])
        with c_ay2:
            hafta_secim = st.selectbox("Görüntülenecek Hafta:", ["1. Hafta", "2. Hafta", "3. Hafta", "4. Hafta"])

        haftalik_toplam_ihtiyac = len(gunler) * len(yerler)
        st.info(f"📌 Haftalık Nöbet İhtiyacı: **{len(gunler)} Gün × {len(yerler)} Yer = {haftalik_toplam_ihtiyac} Nöbet Görevi** | Nöbetçi Öğretmen Sayısı: **{len(ogretmenler)}**")

        if st.button("⚖️ Aylık Nöbeti Eşit Dağıt ve Kaydet", type="primary"):
            if not ogretmenler or not yerler:
                st.error("Nöbetçi öğretmen veya nöbet yeri bulunamadı.")
            else:
                model_n = cp_model.CpModel()
                y = {}
                hafta_sayisi = 4
                
                for o in ogretmenler:
                    for h in range(hafta_sayisi):
                        for g_idx in range(len(gunler)):
                            for r_idx in range(len(yerler)):
                                y[(o, g_idx, r_idx, h)] = model_n.NewBoolVar(f"nob_{o}_{g_idx}_{r_idx}_{h}")

                for h in range(hafta_sayisi):
                    for g_idx in range(len(gunler)):
                        for r_idx in range(len(yerler)):
                            model_n.Add(sum(y[(o, g_idx, r_idx, h)] for o in ogretmenler) == 1)

                for o in ogretmenler:
                    for h in range(hafta_sayisi):
                        for g_idx in range(len(gunler)):
                            model_n.Add(sum(y[(o, g_idx, r_idx, h)] for r_idx in range(len(yerler))) <= 1)

                for o in ogretmenler:
                    bos_g = st.session_state["ogretmen_tercih"].get(o, {}).get("bos", "")
                    for g_idx, g in enumerate(gunler):
                        ders_saati = sonuclar["ogretmen_gunluk_ders"][o].get(g, 0)
                        if g == bos_g or ders_saati == 0:
                            for h in range(hafta_sayisi):
                                for r_idx in range(len(yerler)):
                                    model_n.Add(y[(o, g_idx, r_idx, h)] == 0)

                solver_n = cp_model.CpSolver()
                solver_n.parameters.max_time_in_seconds = 15.0
                status_n = solver_n.Solve(model_n)

                if status_n in (cp_model.OPTIMAL, cp_model.FEASIBLE):
                    aylik_cizelge = {f"{h+1}. Hafta": {g: [] for g in gunler} for h in range(hafta_sayisi)}
                    
                    for h in range(hafta_sayisi):
                        h_adi = f"{h+1}. Hafta"
                        for g_idx, g in enumerate(gunler):
                            for r_idx, yer in enumerate(yerler):
                                for o in ogretmenler:
                                    if solver_n.Value(y[(o, g_idx, r_idx, h)]) == 1:
                                        saat_d = sonuclar["ogretmen_gunluk_ders"][o].get(g, 0)
                                        aylik_cizelge[h_adi][g].append({"ogretmen": o, "yer": yer, "ders_saati": saat_d})
                                        st.session_state["aylik_nobet_gecmisi"][o] = st.session_state["aylik_nobet_gecmisi"].get(o, 0) + 1

                    st.session_state["aylik_nobetler"] = aylik_cizelge
                    
                    veri_kaydet(st.session_state["kurum_kodu"], {
                        "dersler": st.session_state["dersler"],
                        "ogretmen_tercih": st.session_state["ogretmen_tercih"],
                        "nobet_yerleri": st.session_state["nobet_yerleri"],
                        "sonuclar": sonuclar,
                        "aylik_nobetler": aylik_cizelge,
                        "aylik_nobet_gecmisi": st.session_state["aylik_nobet_gecmisi"]
                    })
                    st.success(f"✓ {secili_ay} Ayı Nöbet Dağılımı Eşit Olarak Tamamlandı!")
                    st.rerun()
                else:
                    st.error("Nöbet kısıtları nedeniyle çözüm üretilemedi.")

        if "aylik_nobetler" in st.session_state and st.session_state["aylik_nobetler"]:
            st.markdown(f"#### 📅 {secili_ay} Ayı - {hafta_secim} Nöbet Dağılımı")
            c_cols = st.columns(len(gunler))
            secili_hafta_verisi = st.session_state["aylik_nobetler"].get(hafta_secim, {})
            
            for idx, g in enumerate(gunler):
                with c_cols[idx]:
                    st.markdown(f"""
                    <div style="background:white; border:1px solid #e2e8f0; border-top:4px solid #0ea5e9; border-radius:10px; padding:12px;">
                        <b style="color:#1e293b;">📅 {g}</b><hr style="margin:8px 0;">
                    """, unsafe_allow_html=True)
                    
                    nobetciler = secili_hafta_verisi.get(g, [])
                    if nobetciler:
                        for n in nobetciler:
                            st.markdown(f"""
                            <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; padding:6px 10px; margin-bottom:6px; font-size:12px; display:flex; justify-content:space-between;">
                                <span><b>{n['ogretmen']}</b> <small>({n['ders_saati']} Sa)</small></span>
                                <span style="background:#e0f2fe; color:#0369a1; padding:2px 6px; border-radius:4px; font-weight:700;">{n['yer']}</span>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.caption("Nöbetçi atanmadı")
                    st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Lütfen önce ders programını oluşturun.")

# ==========================================
# 6. HATA & TALEP BİLDİR
# ==========================================
elif st.session_state["sayfa"] == "HataBildir":
    st.subheader("💬 Okul Hata, Sorun & Talep Bildirim Merkezi")
    st.markdown("Sistemle ilgili yaşadığınız tüm durumları doğrudan Iğdır AR-GE birimine iletebilirsiniz.")
    
    with st.form("hata_formu"):
        okul_adi = st.text_input("Kurum İsmi", value=st.session_state["okul_adi"])
        bildiren = st.text_input("Ad Soyad / Unvan", placeholder="Örn: Müdür Yardımcısı Ahmet Bey")
        kategori = st.selectbox("Bildirim Türü", ["Hata / Çalışmayan Özellik", "Öneri / Talep", "Excel Yükleme Sorunu", "Nöbet Dağıtım Sorunu", "Diğer"])
        mesaj = st.text_area("Mesajınız / Sorun Açıklaması", placeholder="Lütfen durumu detaylıca yazın...")
        
        gonder_btn = st.form_submit_button("📨 Bildirimi Sisteme İlet", type="primary")
        if gonder_btn:
            if okul_adi and mesaj:
                yeni_bildirim = {
                    "tarih": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "kurum_kodu": st.session_state["kurum_kodu"],
                    "okul": okul_adi,
                    "kisi": bildiren,
                    "kategori": kategori,
                    "mesaj": mesaj
                }
                bildirim_kaydet(yeni_bildirim)
                st.success("✓ Bildiriminiz AR-GE birimine başarıyla iletildi. Teşekkür ederiz!")
            else:
                st.error("Lütfen Kurum İsmi ve Mesaj alanlarını doldurun.")

# ==========================================
# 7. GİZLİ AR-GE YÖNETİCİ PANELİ
# ==========================================
elif st.session_state["sayfa"] == "YoneticiPanel":
    st.subheader("🔒 Iğdır AR-GE Özel Yönetim Paneli")
    st.caption("Bu bölüm yalnızca AR-GE birimi yetkilileri içindir.")
    
    sifre = st.text_input("Yönetici Giriş Şifresi", type="password", placeholder="Şifrenizi girin...")
    
    if sifre == "76arge76":
        st.success("✓ Yönetici Yetkisi Doğrulandı.")
        gelen_bildirimler = bildirimleri_getir()
        
        if gelen_bildirimler:
            st.markdown(f"#### 📬 Gelen Okul Bildirimleri ({len(gelen_bildirimler)} Bildirim)")
            for b in gelen_bildirimler:
                st.markdown(f"""
                <div style="background:#ffffff; border:1px solid #cbd5e1; border-left:5px solid #0284c7; padding:14px; border-radius:8px; margin-bottom:10px;">
                    <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
                        <b>🏫 {b['okul']} (Kod: {b.get('kurum_kodu','-')})</b>
                        <small style="color:#64748b;">{b['tarih']}</small>
                    </div>
                    <b>Yetkili:</b> {b['kisi']} | <b>Tür:</b> <span style="color:#0284c7; font-weight:700;">{b['kategori']}</span><br>
                    <p style="margin-top:6px; margin-bottom:0; color:#334155;">{b['mesaj']}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Henüz yeni bildirim bulunmuyor.")
    elif sifre:
        st.error("Hatalı yönetici şifresi!")