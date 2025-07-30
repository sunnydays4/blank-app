import streamlit as st
from PIL import Image
import io
from fpdf import FPDF
import numpy as np

import streamlit as st

def get_image_download_link(img,filename,text):
    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    href =  f'<a href="data:file/txt;base64,{img_str}" download="{filename}">{text}</a>'
    return href

st.set_page_config(page_title="Analyse numérique du plan de masse", layout="centered")

# Logo depuis une URL (exemple : logo Paris-Saclay)
logo_url = "https://epa-paris-saclay.fr/wp-content/uploads/2021/12/00_paris-saclay-logo-012-scaled.jpg"

#with st.sidebar:
#    st.image(logo_url, width=120)  # Affiche le logo dans la sidebar

st.title("🖼️ Analyse d'images - Plan de masse")

st.write("Pour savoir ce que fait cet outil, et comment l'utiliser, vous pouvez consulter la [documentation.](https://docs.google.com/presentation/d/e/2PACX-1vRxz5DE5uva9u3Uvqn1mU_ylCjGdndhxH_I_OZOBeHeFB6kRP1bo-b7rqyquY4hJ_0dxUsGc_hejEEd/pub?start=false&loop=false&delayms=3000)")

st.write("Outil développé par [Mathias Pisch](https://www.linkedin.com/in/mathiaspisch/)")
st.image(logo_url, width=200)
# Upload de l'image
uploaded_file = st.file_uploader("Glissez-déposez une image ici", type=["png", "jpg", "jpeg"])
if uploaded_file :
    st.image(uploaded_file, width=400)

# Choix des couleurs
st.markdown("### Couleurs à détecter")
col1, col2 = st.columns(2)
with col1:
    #st.badge("label", icon=None, color="blue", width="content")
    couleur_background = st.color_picker("Couleur du **background**", "#004DA9")
    couleur_naturelle_artificielle = st.color_picker("Couleur **naturelle artificielle**", "#90EE90")
with col2:
    couleur_urbanisation = st.color_picker("Couleur **urbanisée**", "#FFFFFF")
    couleur_naturelle_existante = st.color_picker("Couleur **naturelle existante**", "#006400")
seuil = st.slider("**Seuil de tolérance** à utiliser lors de la détection des couleurs", 0, 150, 10)
#st.write("Vous avez réglé le seuil de tolérance à ", seuil)
st.write("Une valeur typique est 10. Pour en savoir plus sur cette valeur, vous pouvez consulter la [documentation.](https://docs.google.com/presentation/d/e/2PACX-1vRxz5DE5uva9u3Uvqn1mU_ylCjGdndhxH_I_OZOBeHeFB6kRP1bo-b7rqyquY4hJ_0dxUsGc_hejEEd/pub?start=false&loop=false&delayms=3000)")

#st.divider() 

st.markdown("### Couleurs à utiliser pour annoter la carte")

# Convertir RGB → hexadécimal (pour color_picker)
def rgb_to_hex(rgb):
    return '#%02x%02x%02x' % rgb

# Conversion HEX → RGB
def hex_to_rgb(hex_code):
    hex_code = hex_code.strip()
    return tuple(int(hex_code[i:i+2], 16) for i in (1, 3, 5))

col1, col2 = st.columns(2)
with col1:
    couleur_marqueur_urbanisation = st.color_picker("Couleur des zones **urbanisées**", rgb_to_hex((255, 0, 0)))
    couleur_marqueur_naturelle_artificielle = st.color_picker("Couleur des zones **naturelles artificelles**", rgb_to_hex((255, 165, 0)))

with col2:
    couleur_marqueur_naturelle_existante = st.color_picker("Couleur des zones **naturelles pré-existantes**", rgb_to_hex((235, 246, 0)))

rgb_marqueur_urbanisation = hex_to_rgb(couleur_marqueur_urbanisation)
rgb_marqueur_naturelle_artificielle = hex_to_rgb(couleur_marqueur_naturelle_artificielle)
rgb_marqueur_naturelle_existante = hex_to_rgb(couleur_marqueur_naturelle_existante)

# === BOUTON D'ANALYSE ===
if uploaded_file and st.button("🔍 Lancer l’analyse"):

    image = Image.open(uploaded_file).convert("RGB")
    largeur, longueur = image.size
    st.image(image, caption="Image originale", use_container_width =True)

    surface_urbanisation = 0
    surface_naturelle_artificielle = 0
    surface_naturelle_existante = 0
    surface_background = 0
    surface_non_classee = 0

    image_annotée = image.copy()
    pixels_annotés = image_annotée.load()

    def couleurs_proches(c1, c2): # ajouter seuil=10): si on veut qu'il soit fixé
        return all(abs(c1[i] - c2[i]) <= seuil for i in range(3))

    rgb_background = (*hex_to_rgb(couleur_background), 100)
    rgb_urbanisation = (*hex_to_rgb(couleur_urbanisation), 100)
    rgb_naturelle_artificielle = (*hex_to_rgb(couleur_naturelle_artificielle), 100)
    rgb_naturelle_existante = (*hex_to_rgb(couleur_naturelle_existante), 100)

    with st.spinner("🔍 Analyse en cours..."):
        for i in range(longueur):
            for j in range(largeur):
                couleur = image.getpixel((j, i))
                if couleurs_proches(couleur, rgb_background):
                    surface_background += 1
                elif couleurs_proches(couleur, rgb_naturelle_existante):
                    surface_naturelle_existante += 1
                    pixels_annotés[j, i] = rgb_marqueur_naturelle_existante
                elif couleurs_proches(couleur, rgb_naturelle_artificielle):
                    surface_naturelle_artificielle += 1
                    pixels_annotés[j, i] = rgb_marqueur_naturelle_artificielle
                elif couleurs_proches(couleur, rgb_urbanisation):
                    surface_urbanisation += 1
                    pixels_annotés[j, i] = rgb_marqueur_urbanisation
                else :
                    surface_non_classee += 1

        st.success("✅ Analyse terminée !")
        st.image(image_annotée, caption="Image annotée", use_container_width =True)

        total_pixels = largeur * longueur
        total_analyse = total_pixels - surface_background

        st.markdown("### Résultats")
        st.write(f"📏 Surface totale : {total_pixels} pixels")

        st.markdown(f"""**Background** :  
- Pixels : `{surface_background}`  
- Pourcentage : `{(surface_background / total_pixels * 100):.2f} %`
""")

        st.markdown(f"""**Urbanisée** :  
- Pixels : `{surface_urbanisation}`  
- Pourcentage (hors background) : `{(surface_urbanisation / total_analyse * 100):.2f} %`
""")

        st.markdown(f"""**Naturelle artificielle** :  
- Pixels : `{surface_naturelle_artificielle}`  
- Pourcentage (hors background) : `{(surface_naturelle_artificielle / total_analyse * 100):.2f} %`
""")

        st.markdown(f"""**Naturelle existante** :  
- Pixels : `{surface_naturelle_existante}`  
- Pourcentage (hors background) : `{(surface_naturelle_existante / total_analyse * 100):.2f} %`
""")

        st.markdown(f"""**Surface non classée** :  
- Pixels : `{surface_non_classee}`  
- Pourcentage (hors background) : `{(surface_non_classee / total_analyse * 100):.2f} %`
""")
        
    if True == True :
        # Génération du PDF comme dans ton code
        if isinstance(image_annotée, np.ndarray):
            image_annotée = Image.fromarray(image_annotée)
        image_annotée = image_annotée.convert("RGB")
        image_annotee_path_temp = "/tmp/image_annotee.jpg"
        image_annotée.save(image_annotee_path_temp, "JPEG")

        st.session_state["image_annotée"] = image_annotée
        st.session_state["total_pixels"] = total_pixels
        st.session_state["surface_background"] = surface_background
        st.session_state["total_analyse"] = total_analyse
        st.session_state["surface_urbanisation"] = surface_urbanisation
        st.session_state["surface_naturelle_artificielle"] = surface_naturelle_artificielle
        st.session_state["surface_naturelle_existante"] = surface_naturelle_existante
        st.session_state["surface_non_classee"] = surface_non_classee


if all(key in st.session_state for key in [
    "image_annotée",
    "total_pixels",
    "surface_background",
    "total_analyse",
    "surface_urbanisation",
    "surface_naturelle_artificielle",
    "surface_naturelle_existante",
    "surface_non_classee"
]):

    image_annotée = st.session_state["image_annotée"]
    total_pixels = st.session_state["total_pixels"]
    surface_background = st.session_state["surface_background"]
    total_analyse = st.session_state["total_analyse"]
    surface_urbanisation = st.session_state["surface_urbanisation"]
    surface_naturelle_artificielle = st.session_state["surface_naturelle_artificielle"]
    surface_naturelle_existante = st.session_state["surface_naturelle_existante"]
    surface_non_classee = st.session_state["surface_non_classee"]

    # Convertir image en JPEG
    if isinstance(image_annotée, np.ndarray):
        image_annotée = Image.fromarray(image_annotée)
    image_annotée = image_annotée.convert("RGB")
    image_annotee_path_temp = "/tmp/image_annotee.jpg"
    image_annotée.save(image_annotee_path_temp, "JPEG")

    # Génération du PDF
    class PDF(FPDF):
        def header(self):
            self.set_font("Arial", "B", 12)
            self.cell(0, 10, "Analyse du plan de masse", ln=True, align="C")
            self.ln(5)

        def footer(self):
            self.set_y(-15)
            self.set_font("Arial", "I", 8)
            self.cell(0, 10, f"Page {self.page_no()}", align="C")

    resultats = f"""
    Surface totale : {total_pixels} pixels

    Background :
    - Pixels : {surface_background}
    - Pourcentage : {(surface_background / total_pixels * 100):.2f} %

    Urbanisée :
    - Pixels : {surface_urbanisation}
    - Pourcentage (hors background) : {(surface_urbanisation / total_analyse * 100):.2f} %

    Naturelle artificielle :
    - Pixels : {surface_naturelle_artificielle}
    - Pourcentage (hors background) : {(surface_naturelle_artificielle / total_analyse * 100):.2f} %

    **Naturelle existante** :
    - Pixels : {surface_naturelle_existante}
    - Pourcentage (hors background) : {(surface_naturelle_existante / total_analyse * 100):.2f} %

    **Non classée** :
    - Pixels : {surface_non_classee}
    - Pourcentage (hors background) : {(surface_non_classee / total_analyse * 100):.2f} %
    """

    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, resultats)
    pdf.add_page()
    pdf.image(image_annotee_path_temp, x=10, y=pdf.get_y() + 5, w=180)

    pdf_output_path = "/tmp/resultats_analyse.pdf"
    pdf.output(pdf_output_path)

    with open(pdf_output_path, "rb") as f:
        st.download_button("📄 Télécharger le dernier rapport PDF", f, file_name="resultats_analyse.pdf", mime="application/pdf")
