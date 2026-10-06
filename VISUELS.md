# Visuels à fournir

Deux temps : ce qu'il faut **maintenant**, pour que le site existe avant
l'inauguration, et ce qu'il faudra **après**, pour la visite virtuelle.

Les fichiers sources restent en pleine définition et ne vont pas sur le site :
`outils/optimiser-images.sh` en tire les versions servies.

---

## 1. Maintenant — onze visuels

Les emplacements sont déjà en place dans le site, chacun portant son libellé.
Déposez les fichiers à ce nommage exact, en WebP ou en JPEG de bonne qualité
(la conversion se fait ensuite), dans le dossier indiqué.

### Maquettes et rendus → `statique/assets/img/maquettes/`

| Fichier | Sujet | Format |
|---|---|---|
| `01-rendu-ensemble` | Le monument dans le Parco Thomas Sankara | horizontal |
| `02-rendu-face-portrait` | La face portrait, à hauteur de regard | vertical |
| `03-rendu-face-texture` | Une face de texture, bossages lisibles | vertical |
| `04-rendu-detail-decoupe` | Détail de la découpe du visage, à contre-jour | horizontal |

`01-rendu-ensemble` est l'image d'ouverture du site et sert aussi à l'image de
partage sur les réseaux : c'est elle qui compte le plus.

`04-rendu-detail-decoupe` doit être pris **à contre-jour**, la lumière
traversant les découpes. C'est la seule image qui montre que le portrait est
fait de vide et non de matière.

### Plans et dessins → `statique/assets/img/maquettes/`

| Fichier | Sujet | Format |
|---|---|---|
| `05-planche-deux-faces` | La planche illustrative des deux faces | horizontal |
| `06-plan-socle` | Le plan du socle de béton armé à gradins | horizontal |
| `07-portrait-vectoriel` | Le portrait vectoriel de la découpe | vertical |

`05-planche-deux-faces` sert aussi à **corriger le schéma** de la page « lecture
des nombres » : la disposition des 28 bossages de la face portrait y est
aujourd'hui approximative, et c'est signalé à l'écran.

### Fabrication → `statique/assets/img/maquettes/`

| Fichier | Sujet | Format |
|---|---|---|
| `08-atelier-decoupe` | La découpe de la tôle d'acier Corten | horizontal |
| `09-atelier-emboutissage` | L'emboutissage des bossages à la presse | horizontal |
| `10-atelier-assemblage` | L'assemblage du prisme | horizontal |

`09-atelier-emboutissage` demande une **lumière rasante** : c'est l'ombre portée
de chaque calotte qui rend le relief. En lumière frontale, les bossages
disparaissent.

### L'auteur et les archives

| Fichier | Dossier | Sujet | Format |
|---|---|---|---|
| `11-artiste` | `maquettes/` | Hamed Ouattara | vertical |
| `01-thomas-sankara` | `archives/` | Le Camarade Président Thomas Sankara | vertical |

**L'image d'archive est la seule du site qui ne soit pas votre création.** Elle
ne doit pas être publiée sans sa ligne de crédit exacte. Un commentaire le
rappelle dans les trois versions de `05-sankara.html`.

#### Trois images libres de droits, à vérifier

Le conteneur de travail n'a pas accès à Wikimedia : je ne peux ni les
télécharger ni lire leur page de licence. Les trois sont données ici d'après la
recherche, **à vérifier une par une avant usage** — ouvrir la page du fichier et
lire la mention de licence, l'auteur et la date.

| Fichier sur Wikimedia Commons | Ce qu'il montre | Licence annoncée |
|---|---|---|
| `Thomas Sankara in Harlem (1984).png` | Il parle à Harlem, New York, 1984 | domaine public — publié aux États-Unis entre 1978 et 1989 sans mention de copyright. Source *The Militant* / Ernest Harsch |
| `Thomas Sankara photo.png` | Portrait | domaine public, même motif. Source *The Militant* / Sam Manuel |
| `Photo of Thomas Sankara by CIA.png` | Portrait, août 1986 | domaine public — œuvre d'un agent du gouvernement des États-Unis |

**Ma recommandation : la photographie de Harlem, 1984.**

C'est celle qui tient le mieux pour ce site. Elle date du voyage de New York,
le même que le discours aux Nations unies du 4 octobre 1984 que la page cite
quatre paragraphes plus haut — l'image et la citation se répondent. Et sa
provenance est digne : *The Militant* est le journal qui a couvert la
Révolution, et dont la maison d'édition a publié *Thomas Sankara parle*.

**N'utilisez pas la troisième.** Elle est juridiquement la plus solide, et c'est
la seule qui soit à écarter sans discussion : porter « photographie : Central
Intelligence Agency » sous le portrait du Camarade Président, sur un site
mémoriel burkinabè, serait retourné contre vous en une journée. La licence n'a
rien à voir avec la question.

#### La ligne de crédit, une fois l'image choisie

Elle se met sous l'image, dans les trois langues, sur le modèle :

> Le Camarade Président Thomas Sankara, Harlem, New York, octobre 1984.
> Photographie Ernest Harsch / *The Militant*. Domaine public.

#### L'installer

Déposer le fichier, puis :

```bash
outils/optimiser-images.sh galerie <dossier-contenant-l-image>
```

Il reste à remplacer, dans les trois `05-sankara.html`, le chemin
`/assets/img/archives/01-thomas-sankara.svg` par le `.webp` produit, ses
dimensions réelles, et la ligne de crédit. Dites-moi quand le fichier est là :
je fais les trois en une passe.

Si plusieurs images sont disponibles, me le dire : la notice historique peut en
accueillir deux ou trois.

### Conversion

```bash
outils/optimiser-images.sh galerie <dossier-de-vos-images>
```

Puis retirer les emplacements `.svg` remplacés, et passer l'extension à `.webp`
dans `contenu/fr/07-maquettes.html`.

---

## 2. Après l'inauguration — la rotation

**36 vues, une tous les 10 degrés, sur 360 degrés.**

C'est la pièce maîtresse de la visite virtuelle, et sa qualité tient
entièrement à la constance d'une vue à l'autre.

| Point | Consigne |
|---|---|
| Nombre | 36 vues exactement, tous les 10° |
| Appareil | sur pied, **immobile** — on contourne le monument, on ne déplace pas l'appareil à vue |
| Hauteur | constante, à hauteur de regard, environ 1,60 m |
| Distance | constante ; le monument occupe la même part du cadre à chaque vue |
| Cadrage | vertical, monument entier **socle compris**, de l'air au-dessus et au-dessous |
| Objectif | focale fixe, autour de 50 mm en équivalent plein format ; pas de grand angle, qui déforme les arêtes |
| Exposition | **manuelle et verrouillée** : mêmes vitesse, ouverture, ISO et balance des blancs pour les 36 vues |
| Lumière | ciel couvert, ou tôt le matin ; le soleil dur change d'une vue à l'autre et détruit la continuité |
| Mise au point | manuelle, verrouillée sur la face avant |
| Format | RAW si possible, sinon JPEG de qualité maximale |
| Nommage | `rot-01.jpg` à `rot-36.jpg`, dans l'ordre de rotation |

**Repérage.** Marquer au sol 36 positions sur un cercle centré sur le monument.
Faire le tour dans un seul sens, sans revenir en arrière.

**Point de départ.** La première vue est la **face portrait, de face** : c'est
elle qui s'affiche à l'ouverture de la page.

**Avant de quitter le parc.** Faire défiler les 36 vues rapidement : si le
monument « saute » ou change de taille, la rotation sera inutilisable. Mieux
vaut recommencer sur place.

```bash
outils/optimiser-images.sh rotation <dossier-des-36-vues>
```

Puis suivre `_phase2/LISEZ-MOI.md`.

### Le raccourci par la maquette 3D

Si le modèle tridimensionnel existe, **trente-six rendus** pris tous les 10°
autour de l'axe vertical ouvrent la visite virtuelle dès maintenant, sans
attendre l'inauguration. Mêmes consignes : même hauteur de caméra, même
distance, même éclairage, même cadrage. Les photographies prendraient ensuite
leur place sans toucher au site.

C'est, de loin, le meilleur rapport entre l'effort et ce que le site y gagne.

---

## 3. Droits et crédits

Pour toute image dont vous n'êtes pas l'auteur — archives, photographies
d'atelier prises par un tiers, rendus confiés à un prestataire — prévoir une
cession écrite pour l'usage en ligne, en presse et en édition institutionnelle.
Le crédit du photographe s'ajoute à celui de l'œuvre, sans jamais le remplacer :

> *SANKARA, L'ÉTERNEL VEILLEUR*, Hamed Ouattara, 2026, acier Corten.
> Photographie : <nom>.
