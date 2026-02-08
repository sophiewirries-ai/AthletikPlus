import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json
import os
from datetime import date, datetime

# -----------------------------
# Page config (muss früh kommen)
# -----------------------------
st.set_page_config(page_title="AthletikPlus", layout="wide")

# -----------------------------
# Global CSS (Figma Look + stabile Cards + Feinschliff)
# -----------------------------
st.markdown(
    """
<style>
/* Background */
.stApp { background: #F5F6FA; }

/* Streamlit Sidebar komplett ausblenden (wir nutzen eigene) */
[data-testid="stSidebar"] { display: none; }

/* Cards via JS marker */
.ap-card-parent{
  background:#FFFFFF !important;
  border-radius:16px !important;
  border: 0px solid transparent !important;
  box-shadow: 0 6px 18px rgba(0,0,0,0.08) !important;
  padding: 18px !important;
}

.ap-card-parent > div{
  background:#FFFFFF !important;
  border-radius:16px !important;
}

/* Optional: falls irgendwo noch "Hintergrundkarten" auftauchen, neutralisieren wir Schatten sehr breit */
div[style*="box-shadow"]{
  box-shadow: none !important;
}

/* Überschriften */
.ap-label{
  font-size:14px;
  color:#6B7280;
  font-weight:600;
  margin-bottom:4px;
}
.ap-title{
  font-size:34px;
  font-weight:800;
  color:#111827;
  margin: 0 0 18px 0;
}

/* KPI */
.ap-kpi-label{
  color:#6B7280;
  font-size:13px;
  font-weight:500;
  margin-bottom:4px !important;
}
.ap-kpi-value{
  font-size:28px;
  font-weight:800;
  color:#111827;
  line-height:1.05 !important;
  margin-top:0 !important;
}

/* Sidebar / Menu */
.ap-nav-title{
  font-weight:800;
  font-size:18px;
  color:#1F2937;
  margin-bottom:14px;
}

/* Radio als Menü */
div[data-testid="stRadio"] > label { display:none; }
div[data-testid="stRadio"] div[role="radiogroup"]{
  display:flex;
  flex-direction:column;
  gap:10px;
}

/* Option Card Look */
div[data-testid="stRadio"] div[role="radiogroup"] label{
  border-radius:12px;
  padding:10px 12px;
  border:1px solid transparent;
  background: transparent;
  color:#374151;
  font-weight:600;
  cursor:pointer;
}
div[data-testid="stRadio"] div[role="radiogroup"] label:hover{
  background:#F5F7FF;
}

/* Markdown Standard-Margins in Cards entfernen */
.ap-card-parent div[data-testid="stMarkdownContainer"]{
  margin:0 !important;
  padding:0 !important;
}
.ap-card-parent div[data-testid="stMarkdownContainer"] p{
  margin:0 !important;
  line-height:1.25 !important;
}

/* Checkbox spacing kleiner */
div[data-testid="stCheckbox"] label p { margin-bottom:0; }
</style>
""",
    unsafe_allow_html=True,
)

# -----------------------------
# JS: Marker -> Parent bekommt Klasse ap-card-parent
# -----------------------------
components.html(
    """
<script>
(function(){
  function markCards(){
    const markers = window.parent.document.querySelectorAll('.ap-card-marker');
    markers.forEach(m => {
      let el = m;
      let best = null;

      for (let i = 0; i < 18; i++){
        if (!el || !el.parentElement) break;
        el = el.parentElement;

        const dt = el.getAttribute && el.getAttribute('data-testid');
        const cls = (el.className || "").toString();

        if (el.tagName === 'DIV' && (dt || cls.includes('st'))){
          best = el;
        }

        if (dt && (dt.toLowerCase().includes('border') || dt.toLowerCase().includes('wrapper'))){
          best = el;
          break;
        }
      }

      if (best) best.classList.add('ap-card-parent');
    });
  }

  markCards();
  setTimeout(markCards, 80);
  setTimeout(markCards, 250);
  setTimeout(markCards, 600);
  setTimeout(markCards, 1200);
})();
</script>
""",
    height=0,
)

# -----------------------------
# Storage files
# -----------------------------
ATHLETES_FILE = "athletes.csv"
PLANS_FILE = "training_plans.json"
PERFORMANCE_FILE = "performance_data.json"
SETTINGS_FILE = "settings.json"

# -----------------------------
# Data load/save
# -----------------------------
def load_data():
    # Settings
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                st.session_state.settings = json.load(f)
        except Exception:
            st.session_state.settings = {"trainer_name": "Trainer"}
    else:
        st.session_state.settings = {"trainer_name": "Trainer"}

    # Athletes
    if os.path.exists(ATHLETES_FILE):
        df = pd.read_csv(ATHLETES_FILE)
        if "Löschen" not in df.columns:
            df["Löschen"] = False
        st.session_state.athletes = df
    else:
        st.session_state.athletes = pd.DataFrame(
            columns=["Löschen", "Name", "Alter", "Größe (cm)", "Gewicht (kg)", "Mannschaft", "Sportart"]
        )

    # Plans (+ statuses)
    if os.path.exists(PLANS_FILE):
        try:
            with open(PLANS_FILE, "r") as f:
                data = json.load(f)
                if isinstance(data, dict) and "plans" in data:
                    st.session_state.training_plans = data["plans"]
                    st.session_state.plan_statuses = data.get("statuses", {})
                else:
                    st.session_state.training_plans = data
                    st.session_state.plan_statuses = {name: True for name in data.keys()}
        except Exception:
            st.session_state.training_plans = {}
            st.session_state.plan_statuses = {}
    else:
        st.session_state.training_plans = {}
        st.session_state.plan_statuses = {}

    # Performance
    if os.path.exists(PERFORMANCE_FILE):
        try:
            with open(PERFORMANCE_FILE, "r") as f:
                st.session_state.performance_data = json.load(f)
        except Exception:
            st.session_state.performance_data = {}
    else:
        st.session_state.performance_data = {}

def save_data():
    st.session_state.athletes.to_csv(ATHLETES_FILE, index=False)

    plans_to_save = {
        "plans": st.session_state.training_plans,
        "statuses": st.session_state.plan_statuses,
    }
    with open(PLANS_FILE, "w") as f:
        json.dump(plans_to_save, f)

    with open(PERFORMANCE_FILE, "w") as f:
        json.dump(st.session_state.performance_data, f)

    with open(SETTINGS_FILE, "w") as f:
        json.dump(st.session_state.settings, f)

# -----------------------------
# Init
# -----------------------------
if "data_loaded" not in st.session_state:
    load_data()
    st.session_state.data_loaded = True

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

def set_page(new_page: str):
    st.session_state.page = new_page
    st.rerun()

# -----------------------------
# Header (über beide Spalten)
# -----------------------------
trainer_name = st.session_state.settings.get("trainer_name", "Trainer")
if st.session_state.page == "Dashboard":
    st.markdown('<div class="ap-label">Dashboard</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="ap-title">Willkommen, {trainer_name}!</div>', unsafe_allow_html=True)

# -----------------------------
# Layout: Nav + Main
# -----------------------------
col_nav, col_main = st.columns([1.15, 3.4], gap="large")

# --- LEFT NAV ---
with col_nav:
    trainer_name = st.session_state.settings.get("trainer_name", "Trainer")

    with st.container(border=True):
        st.markdown('<div class="ap-card-marker"></div>', unsafe_allow_html=True)
        st.markdown('<div class="ap-nav-title">AthletikPlus</div>', unsafe_allow_html=True)

        nav_labels = ["📊 Dashboard", "🧍 Athlet:innen", "📁 Trainingspläne", "📈 Entwicklung", "⚙️ Einstellungen"]
        nav_pages = ["Dashboard", "Athletenverwaltung", "Trainingspläne", "Entwicklung", "Settings"]

        idx = nav_pages.index(st.session_state.page) if st.session_state.page in nav_pages else 0
        choice = st.radio("Navigation", nav_labels, index=idx, key="ap_nav_radio")

        new_page = nav_pages[nav_labels.index(choice)]
        if new_page != st.session_state.page:
            set_page(new_page)

        st.markdown("---")
        st.markdown(
            f"""
            <div style="font-size:12px; color:#6B7280;">
              <div style="font-weight:700; color:#111827;">{trainer_name}</div>
              <div>Trainer Profil</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# --- MAIN ---
with col_main:
    trainer_name = st.session_state.settings.get("trainer_name", "Trainer")

    # -------- DASHBOARD --------
    if st.session_state.page == "Dashboard":
        k1, k2 = st.columns(2, gap="large")
        with k1:
            with st.container(border=True):
                st.markdown('<div class="ap-card-marker"></div>', unsafe_allow_html=True)
                st.markdown('<div class="ap-kpi-label">Athlet:innen gesamt</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="ap-kpi-value">{len(st.session_state.athletes)}</div>', unsafe_allow_html=True)

        with k2:
            with st.container(border=True):
                st.markdown('<div class="ap-card-marker"></div>', unsafe_allow_html=True)
                st.markdown('<div class="ap-kpi-label">Trainingspläne gesamt</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="ap-kpi-value">{len(st.session_state.training_plans)}</div>', unsafe_allow_html=True)

        # --- Heute ---
        today_str = str(pd.Timestamp.now().date())
        units_today = []
        for plan_name, units in st.session_state.training_plans.items():
            for u in units:
                if isinstance(u, dict) and u.get("datum") == today_str:
                    units_today.append(f"{plan_name}: {u.get('schwerpunkt','')}")

        with st.container(border=True):
            st.markdown('<div class="ap-card-marker"></div>', unsafe_allow_html=True)
            st.markdown('<div class="ap-kpi-label">Das steht heute an</div>', unsafe_allow_html=True)
            if units_today:
                st.markdown(
                    "<div style='color:#111827; font-weight:700; font-size:16px;'>"
                    + "<br>".join(units_today[:4])
                    + "</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    "<div style='color:#6B7280; font-size:14px;'>Heute keine Einheit geplant.</div>",
                    unsafe_allow_html=True,
                )

        # --- To Do ---
        with st.container(border=True):
            st.markdown('<div class="ap-card-marker"></div>', unsafe_allow_html=True)
            st.markdown('<div class="ap-kpi-label">To Do:</div>', unsafe_allow_html=True)

            def todo_row(key: str, text: str):
                c1, c2 = st.columns([0.08, 0.92])
                with c1:
                    st.checkbox("", key=key, label_visibility="collapsed")
                with c2:
                    st.markdown(
                        f"<div style='color:#111827; font-weight:400; margin-top:2px;'>{text}</div>",
                        unsafe_allow_html=True,
                    )

            todo_row("todo_1", "Athlet:innen check-in")
            todo_row("todo_2", "Trainingsplan aktualisieren")
            todo_row("todo_3", "Messwerte eintragen")
            todo_row("todo_4", "Woche planen")

    # -------- ATHLETENVERWALTUNG --------
    elif st.session_state.page == "Athletenverwaltung":
        st.title("Athletenverwaltung")

        with st.form("athlete_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            name = c1.text_input("Name")
            alter = c2.number_input("Alter", 1, 100, 20)
            groese = c1.number_input("Größe (cm)", 50, 250, 180)
            gewicht = c2.number_input("Gewicht (kg)", 10, 250, 80)
            mannschaft = c1.text_input("Mannschaft")
            sportart = c2.text_input("Sportart")

            if st.form_submit_button("Athlet speichern"):
                if not name:
                    st.error("Bitte Name eingeben.")
                else:
                    new_athlete = pd.DataFrame([{
                        "Löschen": False,
                        "Name": name,
                        "Alter": alter,
                        "Größe (cm)": groese,
                        "Gewicht (kg)": gewicht,
                        "Mannschaft": mannschaft,
                        "Sportart": sportart,
                    }])
                    st.session_state.athletes = pd.concat([st.session_state.athletes, new_athlete], ignore_index=True)
                    save_data()
                    st.success("Gespeichert!")
                    st.rerun()

        st.subheader("Athlet:innen")
        edited = st.data_editor(
            st.session_state.athletes,
            num_rows="dynamic",
            use_container_width=True,
            key="athlete_editor",
        )
        if not edited.equals(st.session_state.athletes):
            st.session_state.athletes = edited
            save_data()

    # -------- TRAININGSPLÄNE --------
    elif st.session_state.page == "Trainingspläne":
        st.title("Trainingspläne")

        with st.expander("➕ Neuen Plan erstellen"):
            new_plan_name = st.text_input("Name des neuen Plans", key="new_plan_name")
            if st.button("Plan anlegen"):
                if not new_plan_name:
                    st.error("Bitte einen Namen eingeben.")
                elif new_plan_name in st.session_state.training_plans:
                    st.warning("Plan existiert bereits.")
                else:
                    st.session_state.training_plans[new_plan_name] = []
                    st.session_state.plan_statuses[new_plan_name] = True
                    save_data()
                    st.success("Plan angelegt!")
                    st.rerun()

        if not st.session_state.training_plans:
            st.info("Noch keine Trainingspläne vorhanden.")
        else:
            for plan_name, units in st.session_state.training_plans.items():
                with st.expander(f"📁 {plan_name}", expanded=False):
                    is_active = st.session_state.plan_statuses.get(plan_name, True)
                    new_status = st.toggle("Aktiv", value=is_active, key=f"status_{plan_name}")
                    if new_status != is_active:
                        st.session_state.plan_statuses[plan_name] = new_status
                        save_data()
                        st.rerun()

                    st.write("---")
                    
                    # Tabs für bessere Organisation
                    tab1, tab2 = st.tabs(["📋 Einheiten", "➕ Neue Einheit"])
                    
                    with tab2:
                        st.write("**Neue Trainingseinheit erstellen**")
                        
                        # Einheits-Grunddaten
                        col1, col2 = st.columns(2)
                        unit_datum = col1.text_input("Datum (TT.MM.JJJJ)", placeholder="01.02.2026", key=f"unit_datum_{plan_name}")
                        unit_schwerpunkt = col2.text_input("Schwerpunkt", placeholder="z.B. Kraft", key=f"unit_schwerpunkt_{plan_name}")
                        
                        st.write("---")
                        st.write("**Übungen hinzufügen**")
                        
                        # Session State für temporäre Übungen
                        if f"temp_exercises_{plan_name}" not in st.session_state:
                            st.session_state[f"temp_exercises_{plan_name}"] = []
                        
                        # Übungsformular
                        with st.form(f"exercise_form_{plan_name}", clear_on_submit=True):
                            st.write("**Neue Übung**")
                            exc1, exc2 = st.columns(2)
                            ex_name = exc1.text_input("Übungsname", placeholder="z.B. Kniebeugen")
                            ex_saetze = exc2.number_input("Sätze", min_value=1, max_value=20, value=3)
                            
                            exc3, exc4 = st.columns(2)
                            ex_wdh = exc3.text_input("Wiederholungen", placeholder="z.B. 10 oder 8-12")
                            ex_intensitaet = exc4.text_input("Intensität/Gewicht", placeholder="z.B. 80% oder 60kg")
                            
                            if st.form_submit_button("Übung hinzufügen ➕"):
                                if ex_name:
                                    new_exercise = {
                                        "name": ex_name,
                                        "saetze": ex_saetze,
                                        "wiederholungen": ex_wdh,
                                        "intensitaet": ex_intensitaet
                                    }
                                    st.session_state[f"temp_exercises_{plan_name}"].append(new_exercise)
                                    st.rerun()
                                else:
                                    st.error("Bitte Übungsname eingeben!")
                        
                        # Zeige hinzugefügte Übungen
                        if st.session_state[f"temp_exercises_{plan_name}"]:
                            st.write("---")
                            st.write("**Übungen in dieser Einheit:**")
                            
                            for idx, ex in enumerate(st.session_state[f"temp_exercises_{plan_name}"]):
                                col_ex1, col_ex2 = st.columns([0.85, 0.15])
                                with col_ex1:
                                    st.markdown(f"**{idx+1}. {ex['name']}**")
                                    st.caption(f"Sätze: {ex['saetze']} | Wiederholungen: {ex['wiederholungen']} | Intensität: {ex['intensitaet']}")
                                with col_ex2:
                                    if st.button("🗑️", key=f"delete_temp_ex_{plan_name}_{idx}"):
                                        st.session_state[f"temp_exercises_{plan_name}"].pop(idx)
                                        st.rerun()
                        
                        st.write("---")
                        
                        # Einheit speichern
                        col_save1, col_save2 = st.columns([0.7, 0.3])
                        with col_save1:
                            if st.button("💾 Einheit speichern", type="primary", key=f"save_unit_{plan_name}"):
                                if not unit_datum or not unit_schwerpunkt:
                                    st.error("Bitte Datum und Schwerpunkt eingeben!")
                                elif not st.session_state[f"temp_exercises_{plan_name}"]:
                                    st.error("Bitte mindestens eine Übung hinzufügen!")
                                else:
                                    try:
                                        # Datum parsen
                                        if "." in unit_datum:
                                            dt = datetime.strptime(unit_datum.strip(), "%d.%m.%Y")
                                        else:
                                            dt = datetime.fromisoformat(unit_datum.strip())
                                        
                                        # Neue Einheit erstellen
                                        new_unit = {
                                            "datum": dt.date().isoformat(),
                                            "schwerpunkt": unit_schwerpunkt,
                                            "uebungen": st.session_state[f"temp_exercises_{plan_name}"].copy()
                                        }
                                        
                                        st.session_state.training_plans[plan_name].append(new_unit)
                                        st.session_state[f"temp_exercises_{plan_name}"] = []  # Reset
                                        save_data()
                                        st.success("✅ Einheit gespeichert!")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Fehler beim Datum-Format. Bitte TT.MM.JJJJ verwenden (z.B. 01.02.2026)")
                        
                        with col_save2:
                            if st.button("🗑️ Alle löschen", key=f"clear_temp_{plan_name}"):
                                st.session_state[f"temp_exercises_{plan_name}"] = []
                                st.rerun()
                    
                    with tab1:
                        # Bestehende Einheiten anzeigen
                        if not units:
                            st.info("Noch keine Einheiten vorhanden. Wechsle zum Tab '➕ Neue Einheit'.")
                        else:
                            # Sortiere nach Datum
                            sorted_units = sorted(enumerate(units), 
                                                key=lambda x: x[1].get("datum", ""), 
                                                reverse=True)
                            
                            for original_idx, u in sorted_units:
                                if isinstance(u, dict):
                                    st.markdown('<div class="ap-card-marker"></div>', unsafe_allow_html=True)
                                    with st.container(border=True):
                                        col_header1, col_header2 = st.columns([0.85, 0.15])
                                        
                                        with col_header1:
                                            dt_val = pd.to_datetime(u.get("datum", ""), errors="coerce")
                                            display_date = dt_val.strftime("%d.%m.%Y") if not pd.isna(dt_val) else "?"
                                            st.markdown(f"### 📅 {display_date}")
                                            st.markdown(f"**🎯 {u.get('schwerpunkt','Kein Schwerpunkt')}**")
                                        
                                        with col_header2:
                                            if st.button("🗑️", key=f"delete_unit_{plan_name}_{original_idx}"):
                                                st.session_state.training_plans[plan_name].pop(original_idx)
                                                save_data()
                                                st.rerun()
                                        
                                        st.write("---")
                                        
                                        # Übungen anzeigen
                                        uebungen = u.get("uebungen", [])
                                        
                                        if uebungen:
                                            for idx, ex in enumerate(uebungen):
                                                if isinstance(ex, dict):
                                                    # Neue strukturierte Übungen
                                                    st.markdown(f"**{idx+1}. {ex.get('name', 'Übung')}**")
                                                    
                                                    col_detail1, col_detail2, col_detail3 = st.columns(3)
                                                    with col_detail1:
                                                        st.caption(f"🔢 Sätze: {ex.get('saetze', '-')}")
                                                    with col_detail2:
                                                        st.caption(f"🔁 Wdh: {ex.get('wiederholungen', '-')}")
                                                    with col_detail3:
                                                        st.caption(f"💪 Intensität: {ex.get('intensitaet', '-')}")
                                                    
                                                    if idx < len(uebungen) - 1:
                                                        st.write("")
                                                
                                                elif isinstance(ex, str):
                                                    # Alte einfache Übungen (Rückwärtskompatibilität)
                                                    st.markdown(f"**{idx+1}.** {ex}")
                                                    if idx < len(uebungen) - 1:
                                                        st.write("")
                                        else:
                                            st.caption("Keine Übungen eingetragen.")
                                    
                                    st.write("")  # Abstand zwischen Karten

    # -------- ENTWICKLUNG --------
    elif st.session_state.page == "Entwicklung":
        st.title("Entwicklung")
        st.info("Dieser Bereich kommt als nächstes (Charts, Messwerte, Trends).")

    # -------- SETTINGS --------
    elif st.session_state.page == "Settings":
        st.title("Einstellungen")
        new_name = st.text_input("Trainer Name", trainer_name)
        if st.button("Speichern"):
            st.session_state.settings["trainer_name"] = new_name
            save_data()
            st.success("Gespeichert!")
            st.rerun()
