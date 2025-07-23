import streamlit as st
from PIL import Image
import io

st.set_page_config(page_title="Analyse d’image par couleurs", layout="centered")

st.title("🖼️ Analyse d’image par couleurs")

# Upload de l'image
uploaded_file = st.file_uploader("Glissez-déposez une image ici", type=["png", "jpg", "jpeg"])

# Choix des couleurs
st.markdown("### Paramètres des couleurs (à détecter)")
col1, col2 = st.columns(2)
with col1:
    couleur_background = st.color_picker("Couleur du **background**", "#004DA9")
    couleur_naturelle_artificielle = st.color_picker("Couleur **naturelle artificielle**", "#90EE90")
with col2:
    couleur_urbanisation = st.color_picker("Couleur **urbanisée**", "#FFFFFF")
    couleur_naturelle_existante = st.color_picker("Couleur **naturelle existante**", "#006400")

# Couleurs des surlignages
couleur_marqueur_urbanisation = (255, 0, 0)
couleur_marqueur_naturelle_artificielle = (255, 165, 0)
couleur_marqueur_naturelle_existante = (235, 246, 0)

# Conversion HEX → RGB
def hex_to_rgb(hex_code):
    hex_code = hex_code.strip()
    return tuple(int(hex_code[i:i+2], 16) for i in (1, 3, 5))

# === BOUTON D'ANALYSE ===
if uploaded_file and st.button("🔍 Lancer l’analyse"):

    image = Image.open(uploaded_file).convert("RGB")
    largeur, longueur = image.size
    st.image(image, caption="Image originale", use_column_width=True)

    surface_urbanisation = 0
    surface_naturelle_artificielle = 0
    surface_naturelle_existante = 0
    surface_background = 0

    image_annotée = image.copy()
    pixels_annotés = image_annotée.load()

    def couleurs_proches(c1, c2, seuil=10):
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
                    pixels_annotés[j, i] = couleur_marqueur_naturelle_existante
                elif couleurs_proches(couleur, rgb_naturelle_artificielle):
                    surface_naturelle_artificielle += 1
                    pixels_annotés[j, i] = couleur_marqueur_naturelle_artificielle
                elif couleurs_proches(couleur, rgb_urbanisation):
                    surface_urbanisation += 1
                    pixels_annotés[j, i] = couleur_marqueur_urbanisation

        st.success("✅ Analyse terminée !")
        st.image(image_annotée, caption="Image annotée", use_column_width=True)

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
