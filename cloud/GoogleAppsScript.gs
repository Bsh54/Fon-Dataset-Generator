/**
 * GENERATEUR DE DATASET FR-FON (Google Apps Script Version)
 *
 * Ce script permet d'automatiser la génération de données de traduction
 * directement depuis Google Drive / Sheets.
 */

// --- CONFIGURATION ---
// Configurez ces valeurs dans : Exécuter > Configuration du projet > Propriétés du script
const props = PropertiesService.getScriptProperties();
const LLM_API_URL = props.getProperty('LLM_API_URL') || "https://api.openai.com/v1/chat/completions";
const LLM_API_KEY = props.getProperty('LLM_API_KEY');
const TRANSLATE_API_URL = props.getProperty('TRANSLATE_API_URL');
const TRANSLATE_API_KEY = props.getProperty('TRANSLATE_API_KEY');

const OUTPUT_FILENAME = "dataset_fr_fon.jsonl";
const MAX_EXECUTION_TIME_MS = 300000; // 5 minutes
const NOTIFICATION_INTERVAL = 500;

// --- ARCHITECTURE DES DONNÉES ---
const TYPES_DE_PHRASES = [
  { categorie: "Interactions Sociales", prompt: "salutations, remerciements, excuses, politesse" },
  { categorie: "Questions & Besoins", prompt: "localisation, prix, heure, aide" },
  { categorie: "Temps & Conjugaison", prompt: "passé, présent, futur" },
  { categorie: "Émotions", prompt: "sentiments et sensations physiques" },
  { categorie: "Sagesse & Culture", prompt: "proverbes et expressions béninoises" },
  { categorie: "Commerce", prompt: "achats, ventes et négociations" }
];

const PROFILS_LONGUEUR = [
  { nom: "court", desc: "2-5 mots" },
  { nom: "moyen", desc: "6-12 mots" },
  { nom: "long", desc: "13-25 mots" }
];

/**
 * FONCTION PRINCIPALE
 */
function runGenerator() {
  if (!LLM_API_KEY) {
    throw new Error("Veuillez configurer LLM_API_KEY dans les propriétés du script.");
  }

  const startTime = new Date().getTime();
  const seenPhrases = loadSeenPhrases();
  const sheet = getOrCreateSheet();

  console.log("Démarrage... Mémoire : " + seenPhrases.size + " phrases.");

  while (new Date().getTime() - startTime < MAX_EXECUTION_TIME_MS) {
    const typeP = TYPES_DE_PHRASES[Math.floor(Math.random() * TYPES_DE_PHRASES.length)];
    const longueur = PROFILS_LONGUEUR[Math.floor(Math.random() * PROFILS_LONGUEUR.length)];

    const frPhrases = getUniquePhrases(typeP, longueur, seenPhrases);
    if (frPhrases.length === 0) continue;

    for (let phrase of frPhrases) {
      if (new Date().getTime() - startTime > MAX_EXECUTION_TIME_MS) break;

      const fon = translatePhrase(phrase);
      if (fon) {
        const entry = {
          messages: [
            { role: "user", content: "Traduire en fon : " + phrase },
            { role: "assistant", content: fon }
          ],
          metadata: { categorie: typeP.categorie, date: new Date().toISOString() }
        };

        appendToFile(JSON.stringify(entry));
        sheet.appendRow([new Date(), typeP.categorie, phrase, fon]);
        seenPhrases.add(phrase.toLowerCase());

        if (seenPhrases.size % 50 === 0) checkAndSendNotification(seenPhrases.size);
      }
      Utilities.sleep(500); // Respect des quotas
    }
  }
}

// --- LOGIQUE API ---

function getUniquePhrases(typeP, longueur, seenPhrases) {
  const prompt = `Génère 20 phrases en Français. Catégorie: ${typeP.categorie}. Longueur: ${longueur.desc}. Une phrase par ligne.`;
  const options = {
    method: 'post',
    headers: { "Authorization": "Bearer " + LLM_API_KEY, "Content-Type": "application/json" },
    payload: JSON.stringify({
      model: props.getProperty('LLM_MODEL') || "gpt-3.5-turbo",
      messages: [{ role: "user", content: prompt }],
      temperature: 0.8
    }),
    muteHttpExceptions: true
  };

  try {
    const response = UrlFetchApp.fetch(LLM_API_URL, options);
    const data = JSON.parse(response.getContentText());
    return data.choices[0].message.content.split('\n')
      .map(line => line.replace(/^[\d\s\.\-\)\*]+/, '').trim())
      .filter(cleaned => cleaned.length > 3 && !seenPhrases.has(cleaned.toLowerCase()));
  } catch (e) { return []; }
}

function translatePhrase(frPhrase) {
  if (!TRANSLATE_API_URL) return null;

  const options = {
    method: 'post',
    headers: { "Authorization": "Bearer " + TRANSLATE_API_KEY, "Content-Type": "application/json" },
    payload: JSON.stringify({
      messages: [{ role: "user", content: frPhrase }],
      source_lang: "fr", target_lang: "fon"
    }),
    muteHttpExceptions: true
  };

  try {
    const response = UrlFetchApp.fetch(TRANSLATE_API_URL, options);
    const data = JSON.parse(response.getContentText());
    return data.choices[0].message.content.trim();
  } catch (e) { return null; }
}

// --- UTILITAIRES ---

function getOrCreateSheet() {
  const ssName = "Dataset_Fr_Fon_Export";
  let ss;
  const files = DriveApp.getFilesByName(ssName);
  if (files.hasNext()) {
    ss = SpreadsheetApp.open(files.next());
  } else {
    ss = SpreadsheetApp.create(ssName);
  }

  let sheet = ss.getSheetByName("Traductions") || ss.insertSheet("Traductions");
  if (sheet.getLastRow() === 0) {
    sheet.appendRow(["Date", "Catégorie", "Français", "Fon"]);
  }
  return sheet;
}

function loadSeenPhrases() {
  const seen = new Set();
  const files = DriveApp.getFilesByName(OUTPUT_FILENAME);
  if (files.hasNext()) {
    const content = files.next().getBlob().getDataAsString();
    content.split('\n').forEach(line => {
      if (!line.trim()) return;
      try {
        const p = JSON.parse(line).messages[0].content.replace("Traduire en fon : ", "");
        seen.add(p.toLowerCase());
      } catch(e) {}
    });
  }
  return seen;
}

function appendToFile(line) {
  const files = DriveApp.getFilesByName(OUTPUT_FILENAME);
  let file = files.hasNext() ? files.next() : DriveApp.createFile(OUTPUT_FILENAME, "");
  file.setContent(file.getBlob().getDataAsString() + line + "\n");
}

function checkAndSendNotification(count) {
  const last = parseInt(props.getProperty('LAST_NOTIFIED') || "0");
  if (count >= last + NOTIFICATION_INTERVAL) {
    const email = Session.getActiveUser().getEmail();
    GmailApp.sendEmail(email, "🚀 Dataset Update", `Votre dataset contient maintenant ${count} phrases.`);
    props.setProperty('LAST_NOTIFIED', count.toString());
  }
}
