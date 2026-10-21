# Logos d'impression

Ces fichiers ne servent qu'aux PDF, et **ne sont pas publiés sur le site**.
Ils pèsent plusieurs mégaoctets, aucune page ne les affiche, et ce site est lu
depuis le Burkina Faso sur des forfaits comptés.

`bandeau.py` compose la bande des partenaires du cartel à partir des quatre
marques. **Chacune est un fichier à part, et se remplace sans toucher aux
autres** — c'est tout l'intérêt : la bande était auparavant découpée d'un seul
bloc dans l'invitation de l'Ambassade, et elle portait de ce fait une ancienne
version d'un logo que rien ne permettait de corriger.

```bash
python3 outils/presse/logos/bandeau.py   # refait bandeau-partenaires.png
node outils/dossiers-pdf.js fr           # puis le cartel
```

## Les quatre marques de la bande

| Fichier | Marque | Origine | Qualité |
|---|---|---|---|
| `pcim-ints.pdf` | PCIM-INTS | Fourni par l'auteur, 21 octobre 2026 | **Vectoriel** — Illustrator |
| `musee-national-burkina-faso.png` | Musée National du Burkina Faso | Fourni par l'auteur, 21 octobre 2026 | 4890 × 3533, fond transparent |
| `aes-confederation-etats-sahel.png` | Confédération des États du Sahel | **Découpé dans l'invitation de l'Ambassade** | 252 × 276 — à remplacer |
| `municipio-iii-roma.webp` | Roma Capitale, Municipio III | Déjà dans le dépôt | 440 × 193 |

**Le seul à remplacer est celui de la Confédération des États du Sahel.** C'est
un recadrage de JPEG : il tient à la taille où la bande l'affiche, mais une
marque institutionnelle se donne en vectoriel, pas en découpage.

## Ce qui manque

**La communauté burkinabè d'Italie.** L'auteur n'a pas son logo, et le site de
l'Ambassade mentionne une *Fédération des Associations des Burkinabè en Italie
(FABI)* sans que cette page ait pu être lue depuis l'atelier. Ni le nom ni la
marque ne sont donc écrits nulle part, sur le site comme sur le cartel.

## Le logo retiré

La bande de l'invitation portait aussi le **CIM-TS**, Comité International du
Mémorial Thomas Sankara, dans une version que l'auteur a signalée comme
ancienne. Il n'y figure plus. S'il doit revenir, c'est avec son fichier à jour,
ajouté à `MARQUES` dans `bandeau.py`.

## Hors bande

`armoiries-burkina-faso.png` — les armoiries du Burkina Faso, en tête du
cartel, découpées dans le cartouche de l'invitation. Fond ramené au blanc par
une transition douce : un seuil net aurait rongé les bords adoucis du dessin.
