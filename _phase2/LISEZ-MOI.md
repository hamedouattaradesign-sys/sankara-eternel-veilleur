# Phase 2 — à réactiver après l'inauguration

Tout ce qui attend les photographies du monument installé. Rien n'est à
réécrire : il suffit de remettre ces fichiers en place.

## Ce qu'il y a ici

```
contenu/01-visite.html          la page de la visite virtuelle
contenu/07-galerie.html         la galerie des photographies de l'œuvre
statique/assets/visite.js       le script de la rotation
statique/assets/img/visite/     36 vues volumétriques de substitution
```

## Comment réactiver, une fois les photographies reçues

```bash
# 1. Convertir les 36 vues photographiques (voir VISUELS.md)
outils/optimiser-images.sh rotation <dossier-des-36-vues>

# 2. Remettre les fichiers en place
mv _phase2/contenu/01-visite.html  contenu/fr/01-visite.html
mv _phase2/contenu/07-galerie.html contenu/fr/08-galerie.html
mv _phase2/statique/assets/visite.js statique/assets/js/visite.js

# 3. Dans contenu/fr/01-visite.html, passer data-ext=".svg" à data-ext=".webp"
#    et retirer les mentions « images de substitution ».

# 4. Dans outils/build.py, décommenter "visite" et "galerie" dans ORDRE.

# 5. Reconstruire et contrôler
python3 outils/build.py && python3 outils/verifier.py
node outils/verification/navigateur.js
```

## Si les maquettes 3D permettent de ne pas attendre

Si le modèle tridimensionnel du monument existe, trente-six rendus pris tous
les 10° autour de l'axe vertical suffisent à ouvrir la visite virtuelle
**dès maintenant**, sans attendre l'inauguration. Mêmes consignes que pour les
photographies : même hauteur de caméra, même distance, même éclairage, même
cadrage. La rotation passerait ensuite des rendus aux photographies sans
toucher au site.
