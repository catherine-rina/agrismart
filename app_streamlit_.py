"""
AgriSmart — Interface Streamlit autonome (sans API)
Fonctionne directement avec le modèle TFLite
"""

import streamlit as st
import numpy as np
from PIL import Image
import io

# ── Config page ─────────────────────────────────────────────
st.set_page_config(
    page_title="AgriSmart — Diagnostic IA",
    page_icon="🌿",
    layout="centered"
)

# ── CSS ─────────────────────────────────────────────────────
st.markdown("""
<style>
.hero {
    background: linear-gradient(135deg, #0d2b1e 0%, #1a5c35 100%);
    border-radius: 16px;
    padding: 2.5rem 2rem;
    text-align: center;
    margin-bottom: 2rem;
}
.hero h1 { color: #4ade80; font-size: 2.4rem; font-weight: 700; margin: 0; }
.hero p  { color: #a7f3c0; font-size: 1rem; margin: 0.5rem 0 0; }
.hero small { color: #6ee7a0; font-size: 0.8rem; opacity: 0.8; }

.result-card {
    border-radius: 12px;
    padding: 1.4rem 1.6rem;
    margin: 1rem 0;
    border-left: 5px solid;
}
.card-saine   { background: #f0fdf4; border-color: #22c55e; }
.card-rust    { background: #fff7ed; border-color: #f97316; }
.card-blight  { background: #fef2f2; border-color: #ef4444; }

.stat-row { display: flex; gap: 12px; margin: 14px 0; }
.stat-box {
    flex: 1; background: white; border-radius: 10px;
    padding: 0.9rem; text-align: center;
    box-shadow: 0 1px 6px rgba(0,0,0,0.07);
    border: 1px solid #e5e7eb;
}
.stat-val  { font-size: 1.6rem; font-weight: 700; color: #111827; }
.stat-lbl  { font-size: 0.75rem; color: #6b7280; margin-top: 2px; }
.prob-row  { margin: 5px 0; }
.prob-bar  { height: 10px; border-radius: 5px; margin-top: 3px; }
.conseil   {
    background: #fffbeb; border: 1px solid #fcd34d;
    border-radius: 10px; padding: 1rem 1.2rem;
    font-size: 0.92rem; line-height: 1.6; margin-top: 1rem;
}
footer { visibility: hidden; }
#MainMenu { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Constantes ───────────────────────────────────────────────
IMG_SIZE = (160, 160)
CLASS_NAMES = [
    "Corn_(maize)___Common_rust_",
    "Corn_(maize)___Northern_Leaf_Blight",
    "Corn_(maize)___healthy"
]
DISEASE_INFO = {
    "Corn_(maize)___healthy": {
        "label"      : "Feuille saine ✅",
        "urgence"    : "faible",
        "couleur"    : "#22c55e",
        "css"        : "card-saine",
        "conseil"    : "Votre culture est en bonne santé. Continuez l'arrosage régulier et la surveillance.",
        "description": "Aucun signe de maladie détecté sur cette feuille."
    },
    "Corn_(maize)___Common_rust_": {
        "label"      : "Rouille commune ⚠️",
        "urgence"    : "modérée",
        "couleur"    : "#f97316",
        "css"        : "card-rust",
        "conseil"    : "Appliquez un fongicide homologué dans les 48h. Évitez l'irrigation par aspersion.",
        "description": "Infection fongique (Puccinia sorghi). Taches rouille-orange sur les feuilles."
    },
    "Corn_(maize)___Northern_Leaf_Blight": {
        "label"      : "Brûlure des feuilles 🔴",
        "urgence"    : "élevée",
        "couleur"    : "#ef4444",
        "css"        : "card-blight",
        "conseil"    : "Isolez la plante immédiatement. Contactez un technicien agricole.",
        "description": "Maladie fongique sévère (Exserohilum turcicum). Lésions grises allongées."
    }
}
CLASS_LABELS = {
    "Corn_(maize)___healthy"              : "Saine",
    "Corn_(maize)___Common_rust_"         : "Rouille commune",
    "Corn_(maize)___Northern_Leaf_Blight" : "Brûlure des feuilles",
}

# ── Chargement modèle TFLite ─────────────────────────────────
@st.cache_resource
def load_model():
    try:
        import tflite_runtime.interpreter as tflite
        interp = tflite.Interpreter(model_path="agrismart_model.tflite")
    except ImportError:
        import tensorflow as tf
        interp = tf.lite.Interpreter(model_path="agrismart_model.tflite")
    interp.resize_tensor_input(
        interp.get_input_details()[0]['index'], [1, 160, 160, 3]
    )
    interp.allocate_tensors()
    return interp

# ── Inférence ────────────────────────────────────────────────
def predict(image: Image.Image):
    import time
    img = image.convert("RGB").resize(IMG_SIZE, Image.LANCZOS)
    arr = np.array(img, dtype=np.float32) / 255.0
    arr = np.expand_dims(arr, axis=0)

    interp = load_model()
    inp = interp.get_input_details()
    out = interp.get_output_details()

    t0 = time.time()
    interp.set_tensor(inp[0]['index'], arr)
    interp.invoke()
    probs = interp.get_tensor(out[0]['index'])[0]
    elapsed_ms = round((time.time() - t0) * 1000, 1)

    pred_idx   = int(np.argmax(probs))
    pred_class = CLASS_NAMES[pred_idx]
    confidence = float(probs[pred_idx])
    all_probs  = {CLASS_NAMES[i]: round(float(probs[i]), 4) for i in range(len(CLASS_NAMES))}

    return pred_class, confidence, all_probs, elapsed_ms

# ── Header ───────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>🌿 AgriSmart</h1>
    <p>Diagnostic IA des maladies du maïs</p>
    <small>Programme D-CLIC • Organisation Internationale de la Francophonie</small>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🌱 Classes détectées")
    st.markdown("- ✅ **Saine** — pas d'infection")
    st.markdown("- ⚠️ **Rouille commune** — fongique")
    st.markdown("- 🔴 **Brûlure des feuilles** — sévère")
    st.markdown("---")
    st.markdown("**Modèle** : MobileNetV2 TFLite")
    st.markdown("**Précision** : 99.85%")
    st.markdown("**Cultures** : Maïs")
    st.markdown("---")
    st.caption("AgriSmart v1.0 • Lomé, Togo")

# ── Upload ───────────────────────────────────────────────────
st.markdown("### 📸 Uploadez une photo de feuille de maïs")
uploaded = st.file_uploader(
    "Choisir une image (JPG ou PNG)",
    type=["jpg", "jpeg", "png", "webp"]
)

if uploaded:
    image = Image.open(uploaded)
    col1, col2 = st.columns([1, 1])

    with col1:
        st.image(image, caption="Image uploadée", use_column_width=True)

    with col2:
        if st.button("🔍 Lancer le diagnostic", type="primary", use_container_width=True):
            with st.spinner("Analyse en cours..."):
                try:
                    pred_class, confidence, all_probs, elapsed_ms = predict(image)
                    info = DISEASE_INFO[pred_class]

                    # Carte résultat
                    st.markdown(f"""
                    <div class="result-card {info['css']}">
                        <h3 style="margin:0 0 4px">{info['label']}</h3>
                        <p style="margin:0;color:#4b5563;font-size:0.9rem">{info['description']}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    # Stats
                    st.markdown(f"""
                    <div class="stat-row">
                        <div class="stat-box">
                            <div class="stat-val">{confidence:.1%}</div>
                            <div class="stat-lbl">Confiance</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-val">{elapsed_ms} ms</div>
                            <div class="stat-lbl">Temps d'analyse</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Probabilités
                    st.markdown("**Probabilités par classe :**")
                    for cls, prob in sorted(all_probs.items(), key=lambda x: -x[1]):
                        color = DISEASE_INFO[cls]["couleur"]
                        lbl   = CLASS_LABELS.get(cls, cls)
                        pct   = int(prob * 100)
                        st.markdown(f"""
                        <div class="prob-row">
                            <span style="font-size:0.85rem">
                                <b>{lbl}</b>
                                <span style="float:right">{prob:.1%}</span>
                            </span>
                            <div class="prob-bar" style="width:{pct}%;background:{color}"></div>
                        </div>
                        """, unsafe_allow_html=True)

                    # Conseil
                    st.markdown(f"""
                    <div class="conseil">
                        💡 <b>Conseil :</b> {info['conseil']}
                    </div>
                    """, unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"Erreur : {str(e)}")

# ── À propos ─────────────────────────────────────────────────
with st.expander("ℹ️ À propos d'AgriSmart"):
    st.markdown("""
    **AgriSmart** est une solution IA pour détecter les maladies des cultures en Afrique de l'Ouest.

    **Modèle** : MobileNetV2 fine-tuné | **Précision** : 99.85% | **Format** : TFLite

    *Programme D-CLIC / Organisation Internationale de la Francophonie*
    """)
