# SANKARA, L'ÉTERNEL VEILLEUR — site du monument

Site du monument **SANKARA, L'ÉTERNEL VEILLEUR**, sculpture monumentale de
Hamed Ouattara destinée au Parco Thomas Sankara de Rome.

Destination : `https://sankara.hamedouattara.com`
Inauguration : fin octobre 2026.

---

## 1. Un seul site, deux états

Le monument n'est pas encore installé. Plutôt que deux projets successifs, le
site est **un seul ouvrage qui change d'état** le jour de l'inauguration. Mêmes
adresses, mêmes textes, même structure : rien à refaire.

| | **Phase 1 — aujourd'hui** | **Phase 2 — après l'inauguration** |
|---|---|---|
| Ce que le site montre | le projet : rendus, plans, portrait vectoriel, fabrication | l'œuvre installée : photographies |
| Page d'entrée des images | Maquettes et plans | Galerie |
| Visite virtuelle | en attente | ouverte, rotation sur 36 vues |
| Journal du projet | fabrication, installation, inauguration | se poursuit |

Tout ce qui concerne la phase 2 attend dans `_phase2/`, prêt à être remis en
place. La marche à suivre est dans `_phase2/LISEZ-MOI.md`.

**Raccourci possible.** Si le modèle 3D du monument existe, trente-six rendus
pris tous les 10° suffisent à ouvrir la visite virtuelle **sans attendre
l'inauguration**. Les photographies prendraient ensuite leur place sans toucher
au site.

---

## 2. Pourquoi le site est statique, et pourquoi il est quand même vivant

« Dynamique » recouvre deux choses qu'il faut séparer.

**Techniquement**, le site est statique : des fichiers, pas de base de données,
pas de back-office, pas de serveur applicatif. C'est un choix, pas une
limitation :

- l'hébergement est **gratuit** et le certificat HTTPS automatique ;
- il n'y a **rien à mettre à jour** — pas de faille à corriger, pas de version
  à suivre, rien qui se périme en silence ;
- les frais récurrents étant à la charge du Mémorial Thomas Sankara, le site
  doit pouvoir durer des années sans coût ni surveillance ;
- rien à pirater : il n'y a ni formulaire, ni compte, ni base.

**Éditorialement**, le site est vivant, et c'est là que tout se joue :

- la **ligne d'état du projet**, en page d'accueil, dit où en est le monument.
  Une ligne de texte à changer à chaque étape ;
- le **journal du projet** suit les étapes, de la découpe à l'inauguration.
  Une étape = un bloc à copier en tête de liste ;
- les **maquettes, plans et images d'atelier** montrent une œuvre en train de
  se faire, ce qu'une photographie d'œuvre finie ne montre jamais.

Pour ajouter une actualité, il faut aujourd'hui passer par moi ou par quelqu'un
qui touche aux fichiers. **Si l'autonomie devient nécessaire**, il existe une
solution sans serveur ni frais : un back-office qui écrit directement dans le
dépôt (type Decap CMS), ajouté en une demi-journée, et qui laisse le site aussi
statique qu'avant. À décider une fois le site en ligne, pas avant :
l'inauguration est dans trois semaines.

---

## 3. État d'avancement

| Élément | État |
|---|---|
| Structure, gabarit, charte | fait |
| Les douze pages, en français | fait, à relire par l'auteur |
| Journal du projet | fait, à enrichir au fil des étapes |
| Schéma des faces et comptage des bossages | fait |
| Référencement, JSON-LD, Open Graph, sitemap | fait |
| Accessibilité : contrastes, clavier, HTML sémantique | fait, contrôlé |
| **Les six dossiers PDF, trois langues** | **faits** |
| Visite virtuelle | prête, en attente de vues — `_phase2/` |
| Photographies de l'œuvre, du parc et de l'atelier | installées |
| **Version italienne, 12 pages** | **faite** |
| **Version anglaise, 12 pages** | **faite** |
| **Image d'archive du Camarade Président** | **attendue** |
| **Dépôt GitHub et mise en ligne** | à faire |

Tout ce qui est provisoire est **signalé à l'écran**, pour qu'aucun placeholder
ne passe inaperçu à la mise en ligne.

---

## 4. Ce qu'il reste à fournir

1. **Les visuels** — la liste exacte, avec les noms de fichiers attendus, est
   dans `VISUELS.md`. Onze emplacements sont déjà en place dans le site, chacun
   portant son libellé.
2. **La ligne de crédit de l'image d'archive** du Camarade Président Thomas
   Sankara. C'est la seule image du site qui ne soit pas une création de
   l'auteur : elle ne doit pas être publiée sans son crédit exact.
3. **Les accès au registrar** de `hamedouattara.com`.
4. **Quatre validations** : la note d'intention, le choix de rédaction sur
   l'amitié d'enfance (`CHOIX-DE-REDACTION.md`), l'ordre exact des prénoms
   gravés dans l'acier, et la date exacte de l'inauguration.

---

## 5. Comment le site est fait

Pas de base de données, pas de back-office, pas de dépendance à installer.
Un générateur de 400 lignes en Python, sans aucune bibliothèque extérieure.

```
contenu/fr/           le texte des pages, un fichier par page
contenu/it/ en/       les traductions, à venir
gabarits/base.html    le gabarit commun
statique/             ce qui est recopié tel quel : CSS, JS, images, PDF
outils/               le générateur et les contrôles
_phase2/              ce qui attend l'inauguration
public/               LE SITE PRODUIT — c'est ce dossier que l'on publie
```

Chaque page est un fragment HTML précédé de ses métadonnées en JSON. Le
générateur fabrique autour la navigation, le pied de page, les liens entre
langues et le JSON-LD.

```bash
python3 outils/build.py        # écrit public/
python3 outils/verifier.py     # structure, SEO, liens, accessibilité

cd public && python3 -m http.server 8765      # regarder en local

node outils/verification/navigateur.js        # contrôles en navigateur réel
```

Le contrôle en navigateur vérifie, page par page : erreurs de console,
ressources manquantes, débordement horizontal sur écran de 360 px, textes
alternatifs, unicité du h1. Quand la visite virtuelle sera publiée, il
contrôlera aussi la rotation au curseur, au clavier, au glissement, sans
JavaScript et en économie de données. Nécessite Playwright.

### Les autres outils

```bash
python3 outils/emplacements-photo.py       # régénère les emplacements de visuels
python3 outils/vues-de-substitution.py     # régénère les 36 vues provisoires
node outils/dossiers-pdf.js                # régénère les cinq dossiers PDF
node outils/dossiers-pdf.js en             # ou une seule langue
outils/optimiser-images.sh galerie  <dossier>   # vos images → WebP
outils/optimiser-images.sh rotation <dossier>   # 36 vues → WebP (phase 2)
```

**`public/` est versionné volontairement.** Le site peut être publié sans que
personne ait à exécuter quoi que ce soit — une sécurité pour un site maintenu
dans la durée, et par d'autres mains. Après toute modification de `contenu/`,
relancer `build.py` et committer `public/` dans le même commit.

---

## 6. Poids des pages

Mesuré en gzip, ce que paie réellement un visiteur en données :

| Page | Poids |
|---|---|
| Accueil | ~10 Ko |
| Les autres pages | 7 à 11 Ko |
| Site publié, tout compris | 4,4 Mo |
| dont les six dossiers PDF | 1,9 Mo, jamais chargés sans clic |
| dont les images | 1,8 Mo, servies au besoin |
| dont les pages, le CSS et le JS | 588 Ko pour les trente-trois pages |

Aucune police n'est téléchargée : la typographie est celle du système. Aucune
requête n'est faite hors du domaine du site.

**Quand vos visuels arriveront**, tenir le budget : 120 Ko par image de
galerie, 40 Ko par vue de rotation. `outils/optimiser-images.sh` applique ces
réglages.

---

## 7. Mise en ligne, pas à pas

### 7.1 Créer le dépôt

Le dépôt doit être **public** : GitHub Pages est gratuit sur un dépôt public, et
le site a vocation à être lu de tous. Sur github.com : *New repository*, nom
`sankara-eternel-veilleur`, visibilité *Public*, sans README ni .gitignore.

```bash
git remote add origin https://github.com/hamedouattaradesign-sys/sankara-eternel-veilleur.git
git push -u origin main
```

### 7.2 Publier par GitHub Pages

Le site produit est dans `public/`, et GitHub Pages ne sert d'office que la
racine ou `/docs`. On passe donc par une action, fournie :

```bash
mkdir -p .github/workflows
cp deploiement/github-pages.yml .github/workflows/
git add .github && git commit -m "Publication par GitHub Pages" && git push
```

Puis, sur github.com : **Settings → Pages → Build and deployment → Source :
GitHub Actions**. Le premier déploiement part tout seul.

### 7.3 Configurer le sous-domaine chez le registrar

Dans la zone DNS de `hamedouattara.com`, créer **un seul** enregistrement :

| Champ | Valeur |
|---|---|
| Type | `CNAME` |
| Nom / Hôte | `sankara` |
| Valeur / Cible | `hamedouattaradesign-sys.github.io.` |
| TTL | 3600 (ou la valeur par défaut) |

Selon le registrar, le champ « Nom » attend `sankara` seul, ou
`sankara.hamedouattara.com.` en entier. Ne créer aucun enregistrement A, et ne
toucher à rien d'autre : le site principal n'est pas concerné.

Ensuite, sur github.com : **Settings → Pages → Custom domain**, saisir
`sankara.hamedouattara.com`. Le fichier `CNAME` est déjà dans `public/`.

### 7.4 Vérifier la propagation et le certificat

```bash
dig +short sankara.hamedouattara.com CNAME
# attendu : hamedouattaradesign-sys.github.io.

curl -sI https://sankara.hamedouattara.com | head -3
# attendu : HTTP/2 200

echo | openssl s_client -servername sankara.hamedouattara.com \
    -connect sankara.hamedouattara.com:443 2>/dev/null \
  | openssl x509 -noout -subject -dates
```

Quelques minutes à quelques heures pour la propagation DNS, jusqu'à 24 heures
pour le certificat. Tant qu'il n'est pas émis, la case **Enforce HTTPS** reste
grisée : il faut y revenir la cocher.

### 7.5 Si l'on préfère Netlify

Netlify sert aussi les dépôts privés, gratuitement. Réglages : **Build command**
vide, **Publish directory** `public`. C'est aussi la voie la plus simple si vous
voulez plus tard un back-office sans serveur.

---

## 8. Les langues

**Les trois langues sont en ligne**, douze pages chacune : français, italien,
anglais. Le sélecteur de langue apparaît en tête, les balises `hreflang` sont
posées, et le sitemap déclare les trente-trois adresses.

Le générateur ne produit une langue que si les fichiers existent, et le
sélecteur ne s'affiche que sur les pages réellement traduites : aucune page
morte n'est possible.

Le français reste la langue de référence : il n'est la traduction de rien.

**Le registre est conservé dans les trois langues.** Ce n'est pas une
préférence de style, c'est la règle éditoriale du projet :

| Français | Italien | Anglais |
|---|---|---|
| Camarade Président Thomas Sankara | Compagno Presidente Thomas Sankara | Comrade President Thomas Sankara |
| Camarade Ministre | Compagno Ministro | Comrade Minister |
| Révolution Démocratique et Populaire | Rivoluzione Democratica e Popolare | Democratic and Popular Revolution |
| bossage | bugna | boss |
| acier Corten | acciaio Corten | Corten steel |

Jamais *il Presidente* seul, jamais *Mr President*, jamais *Mr Sankara*. Les
mots interdits en français le sont dans les trois langues : *junte*, *régime
militaire*, *putsch*, et leurs équivalents italiens et anglais.

Restent en français dans les trois versions, parce que ce sont des noms
propres : le titre de l'œuvre, *Ma brique pour Sankara* (marqué `lang="fr"`
pour les lecteurs d'écran), le Conseil National de la Révolution, le Haut
Conseil des Burkinabè de l'Étranger, le Bureau Burkinabè du Droit d'Auteur, et
le nom gravé dans l'acier.

Les champs de texte libre du JSON-LD — métier, forme, matériau, ligne de crédit,
description du parc — sont traduits eux aussi, dans `MOTS_DONNEES` au début de
`outils/build.py`. Un libellé oublié y arrête la génération : le script refuse
d'émettre un `null` dans les données structurées.

### Ajouter une quatrième langue

```bash
# 1. déclarer la langue dans LANGUES et MOTS_DONNEES, dans outils/build.py
# 2. ajouter son dictionnaire dans MOTS, dans outils/planche-faces.py
# 3. puis, fichier par fichier :
cp contenu/fr/02-oeuvre.html contenu/xx/02-oeuvre.html
# traduire le corps, puis dans les métadonnées :
#   "slug" : l'adresse traduite     "nav" : le libellé de navigation
#   "titre" : 75 caractères au plus  "description" : 165 au plus
# 4. ajouter les adresses dans PAGES, dans outils/verification/navigateur.js
python3 outils/build.py && python3 outils/verifier.py
```

### La planche des faces

Elle est tracée par `outils/planche-faces.py`, aux cotes réelles du plan
FACE PORTRAIT INDICE E, avec un dictionnaire de libellés par langue.

Le script **refuse de produire le dessin** si le compte ne tombe pas juste. Il
contrôle trois choses, dans cet ordre :

1. **Les marges.** Avec un entraxe vertical de 165 mm et des bossages de
   139 mm, douze rangées laissent 23 mm en haut et en bas d'une face de
   2000 mm, à comparer aux 30 mm de marge latérale. Si les deux marges
   divergent, le nombre de rangées est faux et le script s'arrête.
2. **Le compte des faces** : 4 × 12 = 48, 4 + 24 = 28, 2 × 48 + 2 × 28 = 152.
3. **Le lien entre les deux** : 48 − 28 = 20 = 4 × 4 + 4, soit ce que le visage
   et le bloc du nom rendent au vide.

Le premier de ces contrôles n'existait pas, et c'est lui qui aurait évité de
publier onze rangées pendant plusieurs jours sur la foi d'un document signé qui
se trompait. Voir `NOTES-DE-VIGILANCE.md`, §4.

```bash
python3 outils/planche-faces.py fr    # ou it, ou en
```

---

## 8 bis. Les six dossiers PDF

Deux documents, trois langues.

| Document | Français | Italien | Anglais |
|---|---|---|---|
| Dossier institutionnel, 6 à 7 pages | référence | traduction | traduction |
| Dossier de presse, 4 pages | référence | traduction | traduction |

Les six sont générés. Le français est la référence ; en cas de divergence
d'interprétation, c'est lui qui fait foi, et les deux traductions le disent en
tête et au pied.

Le dossier institutionnel français en est la **deuxième édition**, datée du
6 octobre 2026. La première, signée le 17 août 2026, portait un comptage faux —
onze rangées, 144 bossages — et a été **retirée du site**. Elle est conservée,
non publiée, dans `outils/presse/archive/`, parce qu'elle fait foi de ce qui a
été soumis aux autorités burkinabè en août : si une institution en détient un
exemplaire, c'est celui-là. Voir `NOTES-DE-VIGILANCE.md`, §4.

La deuxième édition **attend la signature de l'auteur** : une zone de paraphe
lui est réservée en fin de document. La signature autographe n'est reproduite
sur aucune traduction — c'est la règle usuelle, et c'est ce qui protège l'auteur
si un texte traduit lui était un jour opposé.

```bash
node outils/dossiers-pdf.js        # les six sorties
node outils/dossiers-pdf.js it     # ou une seule langue
```

Trois choses sont à vérifier avant de signer, et un commentaire en tête de
`institutionnel-fr.html` les rappelle : le **lieu** et la **date** du bloc de
signature, et la section **« Orienté nord-sud »**, qui n'était pas dans la
première édition et consigne une décision d'implantation prise depuis.

Les sources sont dans `outils/presse/`, avec une **feuille de style unique**,
`dossier.css` : une correction de mise en page vaut pour les six documents.
La planche des faces n'est pas collée dans les sources — elle est **tracée à
la demande** par `outils/planche-faces.py` et injectée à la place du
commentaire `<!--PLANCHE-->`. Elle ne peut donc pas se désynchroniser des
cotes.

Les noms de fichiers sont dans la langue du lecteur, pour que le document
arrive dans son dossier de téléchargement sous un nom qu'il comprend :

```
dossier-institutionnel-sankara-eternel-veilleur.pdf       fr, 2e édition
dossier-de-presse-sankara-eternel-veilleur.pdf            fr
dossier-istituzionale-sankara-eternel-veilleur-it.pdf     it
dossier-stampa-sankara-eternel-veilleur-it.pdf            it
institutional-dossier-sankara-eternel-veilleur-en.pdf     en
press-kit-sankara-eternel-veilleur-en.pdf                 en
```

`outils/verifier.py` exige les six : un lien de page institutionnelle vers un
PDF absent serait invisible à la relecture, et c'est exactement le genre
d'oubli qui se découvre après la mise en ligne.

La planche des faces de chaque dossier est tracée au moment de produire le PDF,
par `outils/planche-faces.py`. Les six documents ne peuvent donc pas porter un
comptage différent de celui du site, ni l'un de l'autre.

---

## 9. Charges

Conception et réalisation : à la charge de Hamed Ouattara.
Nom de domaine, hébergement et maintenance : à la charge du Mémorial Thomas
Sankara, par le Projet de Construction des Infrastructures du Mémorial Isidore
Noël Thomas Sankara.

Avec GitHub Pages, l'hébergement est gratuit et le certificat automatique. La
seule dépense récurrente est le nom de domaine `hamedouattara.com`, déjà
détenu.

---

## 10. À lire aussi

- `VISUELS.md` — la liste exacte des images à fournir, et leurs consignes.
- `CHOIX-DE-REDACTION.md` — les formulations à arbitrer par l'auteur.
- `NOTES-DE-VIGILANCE.md` — les points sensibles et leur traitement.
- `QUESTIONS-AU-COMMANDITAIRE.md` — ce qu'il faut demander au Camarade Madi
  Sakandé, classé par urgence.
- `outils/presse/prompt-image-monument.md` — le prompt de génération d'image.
- `_phase2/LISEZ-MOI.md` — comment ouvrir la visite virtuelle le moment venu.
