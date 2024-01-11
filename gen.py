import os
import sys
from openai import OpenAI
client = OpenAI(api_key="YOUR_API_KEY")
pwd = os.getenv('PWD')

fileArray = []

def lister_fichiers_dossier(chemin_du_dossier, niveau=0):
    if os.path.isdir(chemin_du_dossier):
        contenu_dossier = os.listdir(chemin_du_dossier)
        for fichier in contenu_dossier:
            chemin_complet = os.path.join(chemin_du_dossier, fichier)
            if os.path.isdir(chemin_complet):
                lister_fichiers_dossier(chemin_complet, niveau + 1)
            else:
                if fichier.endswith(".cpp") or fichier.endswith(".hpp"):
                    fileArray.append(chemin_complet)

def creer_nom_fichier_unique(chemin_dossier, nom_base, extension):

    numero = 1
    nouveau_nom = nom_base
    chemin_nouveau_fichier = os.path.join(chemin_dossier, nouveau_nom + extension)

    # Vérifiez si le fichier existe et créez un nouveau nom si nécessaire
    while os.path.exists(chemin_nouveau_fichier):
        nouveau_nom = f"{nom_base}{numero}"
        chemin_nouveau_fichier = os.path.join(chemin_dossier, nouveau_nom + extension)
        numero += 1

    return chemin_nouveau_fichier

def lire_fichier(chemin_fichier):
    try:
        with open(chemin_fichier, 'r') as fichier:
            contenu = fichier.read()
            return contenu
    except IOError as e:
        print(f"Erreur lors de la lecture du fichier {chemin_fichier}: {e}")
        return None

def genDoc(contenu):
    try:
        completion = client.chat.completions.create(model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "assistant",
                    "content": f"Tu es un développeur C++ français, tu dois faire de la documentation en format Markdown. Peux-tu me faire une documentation dans le format : Nom du composant/fonction, Argument pris en compte, et petite description de à quoi ça sert pour ce code : {contenu} (écris la doc en francais)"
                }
            ])
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Erreur lors de la génération de la documentation : {e}")
        return ""


lister_fichiers_dossier(sys.argv[1])

# Crée le dossier pour la documentation
chemin_du_dossier = os.path.join(pwd, "Doc")
try:
    os.makedirs(chemin_du_dossier)
except FileExistsError:
    pass  # Le dossier existe déjà
except OSError as error:
    print(f"Erreur lors de la création du dossier '{chemin_du_dossier}': {error}")
    sys.exit(1)  # Arrête le script en cas d'erreur

# Génère la documentation pour chaque fichier
for fichier in fileArray:
    contenu = lire_fichier(fichier)
    if contenu is not None:
        try:
            nom_base = os.path.splitext(os.path.basename(fichier))[0]
            chemin_nouveau_fichier = creer_nom_fichier_unique(chemin_du_dossier, nom_base, ".md")
            with open(chemin_nouveau_fichier, 'w') as newFile:
                doc = genDoc(contenu)
                if doc:
                    newFile.write(doc)
            print(f"Fichier '{os.path.basename(chemin_nouveau_fichier)}' créé avec succès.")
        except IOError as e:
            print(f"Erreur lors de la création du fichier '{os.path.basename(chemin_nouveau_fichier)}': {e}")
