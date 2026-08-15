# epub-sorter — Deep-dive technique

**Repo local :** `/home/anthony/Documents/perso/projects/chrysa/epub-sorter`
**Licence :** MIT (Anthony Gréau, 2026)
**But (1 phrase) :** Outil Python (GUI Tkinter + CLI à barres de progression) qui lit les
métadonnées EPUB via `ebookmeta` pour organiser une bibliothèque : regroupement par auteur,
export CSV des métadonnées, détection de doublons par identifiant (ISBN/UUID), renommage
depuis le titre, avec dossiers de tri `[processed]`/`[duplicates]`/`[failed]`/`[skipped]`.

## État du code actuel

- Cœur = `common.py`, dataclass `Common` (137 l.) : `detect_epubs` (rglob `*.epub`),
  `extract_metadata` (déplace vers `processed`/`failed`, remplit `self.data`),
  `generate_csv`, `rename_author`, `rename_file`, `update_data`.
- Front-ends : `cli.py` (progress bars `IncrementalBar`), `gui.py` (Tkinter), `main.py` (argparse).
- **Dédup = par `metadata.identifier`** accumulé dans `identifier_list` — pas de dédup
  fuzzy titre/auteur, pas de hash de contenu. C'est le point le plus faible vs l'état de l'art.
- Pas encore de tests réels (coverage configurée sur `common.py`, floor 85 %).

---

## 1. dnkorpushov/ebookmeta — la dépendance directe (à maîtriser)

- **owner/repo :** dnkorpushov/ebookmeta
- **stars :** ~52 · **activité :** ~72 commits, maintenu · **langage :** Python
- **licence :** **MIT** ✅ (copiable / vendorisable si besoin)
- **Pattern :** c'est LA lib que le projet utilise déjà (`ebookmeta==1.2.11`). Module
  cible : la classe `Metadata` + `get_metadata`/`set_metadata`.
- **Mécanisme réel :** `get_metadata(path)` → instance `Metadata` (title, `author_list`,
  `identifier`, series, tags, lang, cover). `set_metadata(path, meta)` réécrit dans le fichier.
- **Snippet portable :**
  ```python
  import ebookmeta
  meta = ebookmeta.get_metadata("book.epub")
  print(meta.title, meta.author_list, meta.identifier, meta.series, meta.tag_list)
  meta.title = "Corrected Title"
  ebookmeta.set_metadata("book.epub", meta)
  ```
- **Intégration ici :** déjà branché. À exploiter davantage : `series`/`series_index` (tri
  par série, non utilisé aujourd'hui), `tag_list` (genre), `cover_*` (dédup par cover hash).
- **Gotchas :** `identifier` peut être vide/non normalisé (URN, uuid, ISBN mêlés) → la dédup
  actuelle groupe des `None` ensemble. Normaliser (strip `urn:isbn:`, lower) avant compare.
  `set_metadata` réécrit le zip → faire une copie avant (voir bookery, non-destructif).

## 2. JoeCotellese/bookery — la référence d'architecture "metadata-first" (MIT)

- **owner/repo :** JoeCotellese/bookery
- **stars :** ~3 (jeune) · **activité :** active (~190 commits) · **langage :** Python
- **licence :** **MIT** ✅ (copiable)
- **Fichier/module du pattern :** `src/bookery/metadata/` — `normalizer.py`, `scoring.py`,
  `candidate.py`, `openlibrary.py` ; catalogue SQLite dans `src/bookery/db/`.
- **Mécanisme réel :** matching multi-provider (Open Library + Google Books) avec **consensus
  merger** (préfère les valeurs sur lesquelles ≥2 providers s'accordent), **scoring de
  confiance pondéré**, **normalisation titre/auteur** avant compare, et **write-back
  non-destructif** (écrit toujours sur une COPIE, l'original n'est jamais modifié). Catalogue
  SQLite avec provenance par champ.
- **Snippet portable (idée normalizer + candidate dataclass) :**
  ```python
  import re
  from dataclasses import dataclass

  def normalize_key(title: str, author: str) -> str:
      t = re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()
      a = re.sub(r"[^a-z0-9]+", " ", author.lower()).strip()
      return f"{a}::{t}"

  @dataclass
  class Candidate:
      title: str; author: str; identifier: str; confidence: float; source: str
  ```
- **Intégration ici :** (a) adopter la **clé normalisée `auteur::titre`** comme filet de dédup
  quand `identifier` est absent — comble le trou #1 de `common.py`. (b) passer `extract_metadata`
  en **non-destructif** (copier vers `processed` au lieu de `rename` in-place) pour ne jamais
  perdre l'original en cas de crash. (c) Remplacer le CSV plat par un catalogue **SQLite** avec
  provenance si le projet grossit.
- **Gotchas :** bookery vise Kobo/conversion — ne pas importer sa surface entière ; ne prendre
  que normalizer + le principe non-destructif. Providers réseau = hors périmètre offline-first
  (cf. standard chrysa "offline-first") → garder providers optionnels/pluggables.

## 3. raul23/organize-ebooks — la référence "tri par ISBN à niveaux" (GPL-3.0 → RÉIMPLÉMENTER)

- **owner/repo :** raul23/organize-ebooks
- **stars :** ~53 · **activité :** **archivé (mars 2025), read-only** · **langage :** Python
- **licence :** **GPL-3.0** ⚠️ **COPYLEFT — NE PAS COPIER LE CODE**, réimplémenter l'idée.
- **Fichier/module :** `organize_ebooks.py` (orchestration), `lib.py` (`organizer.organize()`).
- **Mécanisme réel :** extraction ISBN **progressive/à niveaux** : (1) nom de fichier →
  (2) contenu texte → (3) métadonnées via `ebook-meta` (calibre) → (4) décompression archive →
  (5) conversion texte → (6) OCR optionnel. Puis fetch métadonnées, renommage par variables
  (author/series/title/publisher/year) et distribution vers dossiers : organisés / incertains /
  corrompus / pamphlets (non-livres).
- **Snippet portable (idée seulement — réécrit, pas copié) :**
  ```python
  ISBN_RE = re.compile(r"(?:97[89][-\s]?)?(?:\d[-\s]?){9}[\dxX]")

  def find_isbn(epub_path, metadata):
      # niveau 1 : nom de fichier
      if m := ISBN_RE.search(epub_path.name):
          return m.group().replace("-", "").replace(" ", "")
      # niveau 2 : identifier metadata
      if metadata and metadata.identifier:
          return metadata.identifier
      return None  # niveaux OCR/contenu = optionnels
  ```
- **Intégration ici :** l'approche **cascade de fallback** (identifier → nom fichier → titre)
  est exactement ce qui manque à `extract_metadata`/dédup. La catégorie "corrompus" existe déjà
  (`[failed]`) ; ajouter "incertains" (identifier absent). Le niveau OCR/contenu est probablement
  trop lourd pour ce projet — s'arrêter au niveau nom-de-fichier + metadata.
- **Gotchas :** **GPL** → n'importe rien du code, ne pas copier de blocs ; réimplémenter la
  logique depuis la description. Dépend de calibre installé (lourd) — le projet epub-sorter s'en
  tient à `ebookmeta` pur, plus léger, garder cette autonomie.

## 4. ernestofgonzalez/epub-utils — la référence CLI/inspection (Apache-2.0)

- **owner/repo :** ernestofgonzalez/epub-utils
- **stars :** ~213 (le plus populaire du lot) · **activité :** récente/maintenue · **langage :** Python
- **licence :** **Apache-2.0** ✅ (copiable, attribution)
- **Fichier/module :** commandes CLI (`metadata`, `package`, `toc`, `manifest`, `content`,
  `files`) ; extraction via `package.metadata` (Dublin Core / OPF), méthode `to_kv()`.
- **Mécanisme réel :** lit directement `container.xml` → OPF package → métadonnées Dublin Core,
  sans dépendre de calibre. Sortie multi-format (XML colorisé, raw, key-value). Accès dynamique
  aux champs custom (ISBN, series).
- **Snippet portable (forme CLI sous-commandes) :**
  ```python
  # ergonomie CLI : `epub-sorter METADATA_PATH COMMAND [OPTIONS]`
  # sous-commandes claires plutôt que flags booléens empilés (--update-all etc.)
  import argparse
  p = argparse.ArgumentParser()
  sub = p.add_subparsers(dest="command", required=True)
  sub.add_parser("group-by-author")
  sub.add_parser("dedup")
  sub.add_parser("extract-metadata")
  sub.add_parser("rename")
  ```
- **Intégration ici :** deux apports. (a) **Ergonomie CLI** : epub-sorter utilise aujourd'hui
  des flags `--update-author/--update-title/--update-all` ; le modèle **sous-commandes** d'epub-utils
  est plus lisible et testable (cf. skill `ui-ux` CLI). (b) **Fallback lecture OPF pur** : si
  `ebookmeta` échoue sur un EPUB (→ `[failed]`), un parseur `container.xml`→OPF minimal (inspiré
  d'epub-utils, licence Apache donc copiable avec attribution) peut récupérer le titre/identifier
  avant d'abandonner, réduisant le taux de `[failed]`.
- **Gotchas :** Apache-2.0 = garder l'en-tête d'attribution si on copie du code. epub-utils est
  lecture-seule (pas d'écriture métadonnées) — complémentaire, pas substitut d'`ebookmeta`.

---

## Synthèse — quoi prendre

| Source | Licence | À reprendre |
|---|---|---|
| ebookmeta | MIT ✅ | Déjà la dép ; exploiter `series`/`tag_list`/`cover` ; normaliser `identifier` |
| bookery | MIT ✅ | Clé dédup normalisée `auteur::titre` ; write-back **non-destructif** ; catalogue SQLite |
| organize-ebooks | **GPL-3.0** ⚠️ | **Idée seulement** : cascade de fallback ISBN→nom→titre + catégorie "incertains" |
| epub-utils | Apache-2.0 ✅ | Ergonomie **sous-commandes** CLI ; fallback parse OPF pur pour réduire `[failed]` |

**Trou principal du projet :** dédup uniquement par `identifier` brut (groupe les `None`,
ne normalise pas les ISBN, aucun filet titre/auteur). Bookery (clé normalisée) + organize-ebooks
(cascade, réimplémentée) le comblent. Second : `rename` in-place destructif → adopter le
non-destructif de bookery. Rester **offline-first** (standard chrysa) : les providers réseau de
bookery/organize-ebooks restent optionnels, le cœur ne dépend que d'`ebookmeta`.

## Flags licence
- **organize-ebooks = GPL-3.0 (copyleft)** → réimplémenter, ne pas copier de code.
- ebookmeta (MIT), bookery (MIT), epub-utils (Apache-2.0) = permissives, copiables (attribution pour Apache).
