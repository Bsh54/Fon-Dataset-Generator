import asyncio
import httpx
import json
import os
import random
import re
from datetime import datetime
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# --- CONFIGURATION ---
# L'utilisateur peut utiliser OpenAI, DeepSeek ou n'importe quel service compatible OpenAI
LLM_API_URL = os.getenv("LLM_API_URL", "https://api.openai.com/v1/chat/completions")
LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-3.5-turbo")

# Service de traduction (par défaut un Worker Cloudflare ou une autre API)
TRANSLATE_API_URL = os.getenv("TRANSLATE_API_URL")
TRANSLATE_API_KEY = os.getenv("TRANSLATE_API_KEY")

OUTPUT_FILE = os.path.join("data", "dataset_fr_fon.jsonl")
BATCH_SIZE = 50

# --- ARCHITECTURE DES DONNÉES ---
TYPES_DE_PHRASES = [
    {"categorie": "Interactions Sociales", "prompt": "salutations, remerciements, excuses, présentations, politesse."},
    {"categorie": "Questions & Besoins", "prompt": "localisation, prix, heure, aide, permissions, opinions."},
    {"categorie": "Temps & Conjugaison", "prompt": "présent, passé composé, futur, indicateurs temporels."},
    {"categorie": "Négations & Oppositions", "prompt": "ne...pas, ne...jamais, mais, cependant, seulement."},
    {"categorie": "Émotions & État physique", "prompt": "joie, tristesse, colère, peur, faim, soif, fatigue."},
    {"categorie": "Ordres & Instructions", "prompt": "impératif, conseils, recommandations, interdictions."},
    {"categorie": "Sagesse & Culture", "prompt": "proverbes béninois, expressions imagées, valeurs locales."},
    {"categorie": "Descriptions", "prompt": "objets, couleurs, positions, quantités, comparaisons."},
    {"categorie": "Commerce", "prompt": "achats, ventes, négociations, paiements, marchés."},
    {"categorie": "Santé", "prompt": "symptômes, hôpital, médicaments, bien-être, urgences."},
    {"categorie": "Éducation", "prompt": "école, apprentissage, explications, questions scolaires."},
    {"categorie": "Transport", "prompt": "directions, bus, taxi, horaires, billets, trajets."}
]

PROFILS_LONGUEUR = [
    {"nom": "court", "desc": "2-5 mots (ex: 'Où vas-tu ?')"},
    {"nom": "moyen", "desc": "6-12 mots (ex: 'Je vais au marché pour acheter des fruits.')"},
    {"nom": "long", "desc": "13-25 mots (ex: 'Puis-je avoir du pain s'il vous plaît, car j'ai des invités ce soir ?')"}
]

class DatasetGenerator:
    def __init__(self):
        self.seen_phrases = set()
        self.lock = asyncio.Lock()
        self._load_existing_data()

    def _load_existing_data(self):
        if os.path.exists(OUTPUT_FILE):
            try:
                with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            data = json.loads(line)
                            phrase_fr = data['messages'][0]['content'].replace("Traduire en fon : ", "")
                            self.seen_phrases.add(phrase_fr.lower())
                print(f"✅ Mémoire chargée : {len(self.seen_phrases)} phrases.")
            except Exception as e:
                print(f"⚠️ Erreur lors du chargement des données : {e}")

    def clean_text(self, text):
        return re.sub(r'^[\d\s\.\-\)\*]+', '', text).strip()

    async def generate_phrases(self, client):
        type_p = random.choice(TYPES_DE_PHRASES)
        longueur = random.choice(PROFILS_LONGUEUR)

        prompt = (
            f"Génère exactement 50 phrases uniques en Français.\n"
            f"Catégorie: {type_p['categorie']} ({type_p['prompt']})\n"
            f"Longueur: {longueur['desc']}\n"
            f"Contexte: Vie quotidienne au Bénin.\n"
            f"Format: Une phrase par ligne, sans numérotation."
        )

        try:
            resp = await client.post(
                LLM_API_URL,
                headers={"Authorization": f"Bearer {LLM_API_KEY}"},
                json={
                    "model": LLM_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.8
                },
                timeout=60.0
            )
            resp.raise_for_status()
            data = resp.json()
            raw_content = data['choices'][0]['message']['content']

            phrases = []
            for line in raw_content.split('\n'):
                cleaned = self.clean_text(line)
                if cleaned and len(cleaned) > 2 and cleaned.lower() not in self.seen_phrases:
                    phrases.append(cleaned)

            return phrases, type_p['categorie'], longueur['nom']
        except Exception as e:
            print(f"❌ Erreur lors de la génération : {e}")
            return [], "Erreur", "N/A"

    async def translate_to_fon(self, client, phrase):
        if not TRANSLATE_API_URL:
            return "TRADUCTION_MANQUANTE"

        try:
            resp = await client.post(
                TRANSLATE_API_URL,
                headers={"Authorization": f"Bearer {TRANSLATE_API_KEY}"},
                json={
                    "model": "google-translate", # Ou votre modèle de traduction
                    "messages": [{"role": "user", "content": phrase}],
                    "source_lang": "fr",
                    "target_lang": "fon"
                },
                timeout=30.0
            )
            if resp.status_code != 200: return None
            data = resp.json()
            return data['choices'][0]['message']['content'].strip()
        except:
            return None

    async def run(self):
        if not LLM_API_KEY:
            print("❌ Erreur : LLM_API_KEY n'est pas configurée dans le fichier .env")
            return

        print(f"🚀 Démarrage du générateur (Modèle: {LLM_MODEL})")

        async with httpx.AsyncClient() as client:
            while True:
                phrases, cat, taille = await self.generate_phrases(client)
                if not phrases:
                    await asyncio.sleep(5)
                    continue

                print(f"\n📦 Nouveau lot | Catégorie: {cat} | {len(phrases)} phrases")

                for p in phrases:
                    fon = await self.translate_to_fon(client, p)
                    if fon:
                        entry = {
                            "messages": [
                                {"role": "user", "content": f"Traduire en fon : {p}"},
                                {"role": "assistant", "content": fon}
                            ],
                            "metadata": {"categorie": cat, "taille": taille, "timestamp": datetime.now().isoformat()}
                        }
                        async with self.lock:
                            with open(OUTPUT_FILE, mode='a', encoding='utf-8') as f:
                                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
                            self.seen_phrases.add(p.lower())
                        print(f"  ✅ OK: {p[:50]}...")

                    await asyncio.sleep(0.2)

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    generator = DatasetGenerator()
    try:
        asyncio.run(generator.run())
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du script. Dataset sauvegardé.")
