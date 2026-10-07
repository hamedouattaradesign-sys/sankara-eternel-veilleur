#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Générateur du site « SANKARA, L'ÉTERNEL VEILLEUR ».

Sans aucune dépendance : Python 3.8 ou plus récent suffit.
Usage :  python3 outils/build.py
Sortie :  public/

Chaque page est un fragment HTML dans contenu/<langue>/, précédé d'un
commentaire HTML contenant ses métadonnées au format JSON. Le gabarit
commun est dans gabarits/base.html. Les fichiers de statique/ sont
recopiés tels quels.
"""

import json
import os
import re
import shutil
import sys
from datetime import date

RACINE = os.path.dirname(os.path.abspath(os.path.join(__file__, "..")))
CONTENU = os.path.join(RACINE, "contenu")
GABARITS = os.path.join(RACINE, "gabarits")
STATIQUE = os.path.join(RACINE, "statique")
SORTIE = os.path.join(RACINE, "public")

SITE = "https://sankara.hamedouattara.com"

# Ordre de la navigation. Les identifiants sont stables ; les slugs et les
# libellés sont définis langue par langue dans les métadonnées des fragments.
#
# PHASE 1, avant l'inauguration : le monument n'est pas encore installé. Le site
# présente le projet, ses maquettes, ses plans et sa fabrication.
#
# PHASE 2, après l'inauguration : réintégrer "visite" juste après "accueil", et
# juste après "accueil". La page attend dans _phase2/ ; il suffit de la remettre
# dans contenu/fr/ et de la déclarer ici. Rien d'autre à changer : adresses,
# gabarit et mécanique des langues sont inchangés.
ORDRE = [
    "accueil",
    # "visite",        ← phase 2
    "oeuvre",
    "nombres",
    "histoire",
    "sankara",
    "dynamique",
    "artiste",
    "galerie",
    "visiter",
    "journal",
    "institutionnel",
    "contact",
]

# Pages volontairement absentes de la navigation principale.
HORS_NAV = {"404"}

LANGUES = {
    "fr": {
        "etiquette": "Français",
        "prefixe": "",
        "og_locale": "fr_FR",
        "saut": "Aller au contenu",
        "menu": "Menu",
        "nav_label": "Navigation principale",
        "marque_sous": "L'éternel veilleur",
        "pied_atelier": "Studio Hamed Ouattara",
        "pied_nav": "Le site",
        "langues_label": "Langue",
        "pied_mention": (
            "Toute reproduction de l'œuvre ou de ses images doit porter la mention&nbsp;: "
            "<em>SANKARA, L'ÉTERNEL VEILLEUR</em>, Hamed Ouattara, 2026, acier Corten. "
            "Œuvre déposée auprès du Bureau Burkinabè du Droit d'Auteur."
        ),
        "fil": "Accueil",
    },
    "it": {
        "etiquette": "Italiano",
        "prefixe": "/it",
        "og_locale": "it_IT",
        "saut": "Vai al contenuto",
        "menu": "Menu",
        "nav_label": "Navigazione principale",
        "marque_sous": "L'eterno vigile",
        "pied_atelier": "Studio Hamed Ouattara",
        "pied_nav": "Il sito",
        "langues_label": "Lingua",
        "pied_mention": (
            "Ogni riproduzione dell'opera o delle sue immagini deve riportare la dicitura&nbsp;: "
            "<em>SANKARA, L'ÉTERNEL VEILLEUR</em>, Hamed Ouattara, 2026, acciaio Corten. "
            "Opera depositata presso il Bureau Burkinabè du Droit d'Auteur."
        ),
        "fil": "Home",
    },
    "en": {
        "etiquette": "English",
        "prefixe": "/en",
        "og_locale": "en_GB",
        "saut": "Skip to content",
        "menu": "Menu",
        "nav_label": "Main navigation",
        "marque_sous": "The eternal watchman",
        "pied_atelier": "Studio Hamed Ouattara",
        "pied_nav": "This site",
        "langues_label": "Language",
        "pied_mention": (
            "Any reproduction of the work or of its images must carry the credit line&nbsp;: "
            "<em>SANKARA, L'ÉTERNEL VEILLEUR</em>, Hamed Ouattara, 2026, Corten steel. "
            "Work registered with the Bureau Burkinabè du Droit d'Auteur."
        ),
        "fil": "Home",
    },
}

LANGUE_DEFAUT = "fr"


# --------------------------------------------------------------------------
# Lecture des fragments
# --------------------------------------------------------------------------

ENTETE_JSON = re.compile(r"\A\s*<!--(.*?)-->", re.DOTALL)


def lire_fragment(chemin):
    """Renvoie (métadonnées, corps HTML) pour un fragment de page."""
    with open(chemin, encoding="utf-8") as f:
        brut = f.read()
    trouve = ENTETE_JSON.match(brut)
    if not trouve:
        raise SystemExit(
            "%s : il manque le commentaire de métadonnées JSON en tête de fichier." % chemin
        )
    try:
        meta = json.loads(trouve.group(1))
    except json.JSONDecodeError as err:
        raise SystemExit("%s : métadonnées JSON invalides — %s" % (chemin, err))
    corps = brut[trouve.end():].strip()
    return meta, corps


def charger_pages():
    """pages[langue][identifiant] = (métadonnées, corps)."""
    pages = {}
    for langue in LANGUES:
        dossier = os.path.join(CONTENU, langue)
        if not os.path.isdir(dossier):
            continue
        pages[langue] = {}
        for nom in sorted(os.listdir(dossier)):
            if not nom.endswith(".html"):
                continue
            identifiant = re.sub(r"^\d+-", "", nom[:-5])
            meta, corps = lire_fragment(os.path.join(dossier, nom))
            meta.setdefault("slug", identifiant)
            pages[langue][identifiant] = (meta, corps)
    return pages


# --------------------------------------------------------------------------
# Adresses
# --------------------------------------------------------------------------

def chemin_page(langue, meta):
    """Chemin absolu servi pour une page, p. ex. /it/opera/ ou /."""
    prefixe = LANGUES[langue]["prefixe"]
    slug = meta["slug"]
    if slug == "accueil" or slug == "":
        return prefixe + "/"
    if slug == "404":
        return prefixe + "/404.html"
    return "%s/%s/" % (prefixe, slug)


def fichier_sortie(langue, meta):
    chemin = chemin_page(langue, meta)
    if chemin.endswith(".html"):
        return os.path.join(SORTIE, chemin.lstrip("/"))
    return os.path.join(SORTIE, chemin.strip("/"), "index.html")


# --------------------------------------------------------------------------
# Données structurées JSON-LD
# --------------------------------------------------------------------------

# Les champs de texte libre du JSON-LD sont lus par les moteurs dans la langue
# déclarée par la page. Les identifiants, les dates, les cotes et les codes pays
# sont les mêmes partout ; seuls ces libellés changent.
MOTS_DONNEES = {
    "fr": {
        "metier": "Artiste designer",
        "forme": "Sculpture monumentale",
        "medium": "Acier Corten, épaisseur 6 mm",
        "matiere": "Acier Corten",
        "fabrique": "Région de Bologne, Italie",
        "credit": "SANKARA, L'ÉTERNEL VEILLEUR, Hamed Ouattara, 2026, acier Corten",
        "parc": ("Seul espace public d'Europe entièrement dédié à la mémoire du Camarade "
                 "Président Thomas Sankara."),
        "inauguration": "Inauguration de SANKARA, L'ÉTERNEL VEILLEUR",
        "inauguration_desc": ("Inauguration de la sculpture monumentale en acier Corten de "
                              "Hamed Ouattara au Parco Thomas Sankara de Rome. Entrée libre."),
    },
    "it": {
        "metier": "Artista designer",
        "forme": "Scultura monumentale",
        "medium": "Acciaio Corten, spessore 6 mm",
        "matiere": "Acciaio Corten",
        "fabrique": "Regione di Bologna, Italia",
        "credit": "SANKARA, L'ÉTERNEL VEILLEUR, Hamed Ouattara, 2026, acciaio Corten",
        "parc": ("Unico spazio pubblico d'Europa interamente dedicato alla memoria del "
                 "Compagno Presidente Thomas Sankara."),
        "inauguration": "Inaugurazione di SANKARA, L'ÉTERNEL VEILLEUR",
        "inauguration_desc": ("Inaugurazione della scultura monumentale in acciaio Corten di "
                              "Hamed Ouattara al Parco Thomas Sankara di Roma. Ingresso libero."),
    },
    "en": {
        "metier": "Artist designer",
        "forme": "Monumental sculpture",
        "medium": "Corten steel, 6 mm thick",
        "matiere": "Corten steel",
        "fabrique": "Bologna area, Italy",
        "credit": "SANKARA, L'ÉTERNEL VEILLEUR, Hamed Ouattara, 2026, Corten steel",
        "parc": ("The only public space in Europe given over entirely to the memory of "
                 "Comrade President Thomas Sankara."),
        "inauguration": "Unveiling of SANKARA, L'ÉTERNEL VEILLEUR",
        "inauguration_desc": ("Unveiling of Hamed Ouattara's monumental Corten steel sculpture "
                              "at the Parco Thomas Sankara in Rome. Free entry."),
    },
}

PERSONNE = {
    "@type": "Person",
    "@id": SITE + "/#hamed-ouattara",
    "name": "Hamed Ouattara",
    "alternateName": "Ouattara Mohamed Sékou",
    "jobTitle": None,          # posé par bloc_personne()
    "nationality": {"@type": "Country", "name": "Burkina Faso"},
    "url": "https://hamedouattara.com",
    "sameAs": [
        "https://hamedouattara.com",
        "https://studiohamedouattara.com",
    ],
    "worksFor": {
        "@type": "Organization",
        "name": "Studio Hamed Ouattara",
        "foundingDate": "2002",
        "url": "https://studiohamedouattara.com",
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "Route du SIAO",
            "addressLocality": "Ouagadougou",
            "addressCountry": "BF",
        },
    },
}

LIEU = {
    "@type": "Place",
    "@id": SITE + "/#parco-thomas-sankara",
    "name": "Parco Thomas Sankara",
    "description": None,       # posée par bloc_lieu()
    "address": {
        "@type": "PostalAddress",
        "streetAddress": "Via Ugo della Seta",
        "addressLocality": "Rome",
        "addressRegion": "Latium",
        "addressCountry": "IT",
    },
    # Coordonnées relevées en octobre 2026 sur les répertoires d'adresses romains,
    # non auprès du III Municipio. Elles tombent bien sur la Via Ugo della Seta,
    # à Val Melaina, mais elles désignent la rue, pas l'emplacement du monument
    # dans le parc. À REPRENDRE après l'installation, au point exact de l'œuvre.
    "geo": {
        "@type": "GeoCoordinates",
        "latitude": 41.9600,
        "longitude": 12.5255,
    },
    "publicAccess": True,
    "isAccessibleForFree": True,
}

OEUVRE = {
    "@type": "VisualArtwork",
    "@id": SITE + "/#sankara-eternel-veilleur",
    "name": "SANKARA, L'ÉTERNEL VEILLEUR",
    "creator": {"@id": SITE + "/#hamed-ouattara"},
    "dateCreated": "2026",
    "artform": None,           # les cinq champs de texte libre
    "artMedium": None,         # sont posés par bloc_oeuvre(),
    "artworkSurface": None,    # dans la langue de la page
    "material": None,
    "height": {"@type": "QuantitativeValue", "value": 200, "unitCode": "CMT"},
    "width": {"@type": "QuantitativeValue", "value": 70, "unitCode": "CMT"},
    "depth": {"@type": "QuantitativeValue", "value": 70, "unitCode": "CMT"},
    "about": {
        "@type": "Person",
        "name": "Thomas Isidore Noël Sankara",
        "birthDate": "1949",
        "deathDate": "1987",
    },
    "contentLocation": {"@id": SITE + "/#parco-thomas-sankara"},
    "locationCreated": {
        "@type": "Place",
        "name": None,
        "address": {"@type": "PostalAddress", "addressCountry": "IT"},
    },
    "copyrightHolder": {"@id": SITE + "/#hamed-ouattara"},
    "creditText": None,
}


def _traduit(gabarit, remplacements):
    """Copie le gabarit en y posant les libellés de la langue demandée.

    Une valeur None restée en place signalerait un libellé oublié dans
    MOTS_DONNEES : on refuse de publier plutôt que d'émettre un null.
    """
    import copy
    bloc = copy.deepcopy(gabarit)
    for chemin, valeur in remplacements.items():
        cible = bloc
        *parents, feuille = chemin.split(".")
        for cle in parents:
            cible = cible[cle]
        cible[feuille] = valeur

    def controle(noeud, voie=""):
        if isinstance(noeud, dict):
            for cle, val in noeud.items():
                controle(val, voie + "." + cle)
        elif noeud is None:
            raise SystemExit("JSON-LD : libellé manquant pour %s" % voie.lstrip("."))

    controle(bloc)
    return bloc


def bloc_personne(langue):
    m = MOTS_DONNEES[langue]
    return _traduit(PERSONNE, {"jobTitle": m["metier"]})


def bloc_lieu(langue):
    m = MOTS_DONNEES[langue]
    return _traduit(LIEU, {"description": m["parc"]})


def bloc_oeuvre(langue):
    m = MOTS_DONNEES[langue]
    return _traduit(OEUVRE, {
        "artform": m["forme"],
        "artMedium": m["medium"],
        "artworkSurface": m["matiere"],
        "material": m["matiere"],
        "locationCreated.name": m["fabrique"],
        "creditText": m["credit"],
    })


INAUGURATION = {
    "@type": "Event",
    "@id": SITE + "/#inauguration",
    "startDate": "2026-10-24",
    "eventStatus": "https://schema.org/EventScheduled",
    "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
    "location": {"@id": SITE + "/#parco-thomas-sankara"},
    "about": {"@id": SITE + "/#sankara-eternel-veilleur"},
    "performer": {"@id": SITE + "/#hamed-ouattara"},
    "isAccessibleForFree": True,
    "name": None,          # posés par bloc_inauguration(), dans la langue
    "description": None,   # de la page
    # À COMPLÉTER quand l'heure sera arrêtée : "startDate" accepte
    # "2026-10-24T11:00:00+02:00". Tant que l'heure n'est pas connue, la date
    # seule est publiée — mieux vaut une donnée partielle qu'une heure inventée.
}


def bloc_inauguration(langue):
    m = MOTS_DONNEES[langue]
    return _traduit(INAUGURATION, {
        "name": m["inauguration"],
        "description": m["inauguration_desc"],
    })


def bloc_site(langue):
    return {
        "@type": "WebSite",
        "@id": SITE + "/#site",
        "url": SITE + LANGUES[langue]["prefixe"] + "/",
        "name": "SANKARA, L'ÉTERNEL VEILLEUR",
        "inLanguage": langue,
        "author": {"@id": SITE + "/#hamed-ouattara"},
        "about": {"@id": SITE + "/#sankara-eternel-veilleur"},
    }


BLOCS = {
    "oeuvre": bloc_oeuvre,
    "lieu": bloc_lieu,
    "personne": bloc_personne,
    "site": bloc_site,
    "inauguration": bloc_inauguration,
}


def fil_ariane(langue, meta, pages):
    """BreadcrumbList : accueil puis page courante."""
    accueil = pages[langue].get("accueil")
    if accueil is None or meta.get("slug") == "accueil":
        return None
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": 1,
                "name": LANGUES[langue]["fil"],
                "item": SITE + chemin_page(langue, accueil[0]),
            },
            {
                "@type": "ListItem",
                "position": 2,
                "name": meta.get("nav") or meta.get("h1") or meta["titre"],
                "item": SITE + chemin_page(langue, meta),
            },
        ],
    }


def rendre_jsonld(langue, meta, pages):
    demandes = meta.get("donnees", [])
    graphe = [BLOCS["site"](langue)]
    for nom in demandes:
        if nom not in BLOCS:
            raise SystemExit("Bloc JSON-LD inconnu : %s" % nom)
        graphe.append(BLOCS[nom](langue))
    fil = fil_ariane(langue, meta, pages)
    if fil:
        graphe.append(fil)
    charge = {"@context": "https://schema.org", "@graph": graphe}
    return (
        '<script type="application/ld+json">\n%s\n</script>'
        % json.dumps(charge, ensure_ascii=False, indent=1)
    )


# --------------------------------------------------------------------------
# Navigation, langues, hreflang
# --------------------------------------------------------------------------

def rendre_nav(langue, courant, pages):
    lignes = []
    for identifiant in ORDRE:
        entree = pages[langue].get(identifiant)
        if entree is None:
            continue
        meta = entree[0]
        libelle = meta.get("nav") or meta["titre"]
        href = chemin_page(langue, meta)
        if identifiant == courant:
            lignes.append(
                '      <li class="nav__item"><a class="nav__lien nav__lien--courant"'
                ' href="%s" aria-current="page">%s</a></li>' % (href, libelle)
            )
        else:
            lignes.append(
                '      <li class="nav__item"><a class="nav__lien" href="%s">%s</a></li>'
                % (href, libelle)
            )
    return "\n".join(lignes)


def rendre_pied_nav(langue, pages):
    lignes = []
    for identifiant in ORDRE:
        entree = pages[langue].get(identifiant)
        if entree is None or identifiant == "accueil":
            continue
        meta = entree[0]
        lignes.append(
            '        <li><a href="%s">%s</a></li>'
            % (chemin_page(langue, meta), meta.get("nav") or meta["titre"])
        )
    return "\n".join(lignes)


def rendre_langues(langue, identifiant, pages):
    """Sélecteur de langue : n'affiche que les langues où la page existe."""
    disponibles = [
        autre for autre in LANGUES
        if autre in pages and identifiant in pages[autre]
    ]
    if len(disponibles) < 2:
        return ""
    elements = []
    for autre in disponibles:
        meta = pages[autre][identifiant][0]
        href = chemin_page(autre, meta)
        etiquette = LANGUES[autre]["etiquette"]
        if autre == langue:
            elements.append(
                '      <li><span class="langues__courante" lang="%s">%s</span></li>'
                % (autre, etiquette)
            )
        else:
            elements.append(
                '      <li><a href="%s" lang="%s" hreflang="%s">%s</a></li>'
                % (href, autre, autre, etiquette)
            )
    return (
        '    <ul class="langues" aria-label="%s">\n%s\n    </ul>'
        % (LANGUES[langue]["langues_label"], "\n".join(elements))
    )


def rendre_hreflang(identifiant, pages):
    lignes = []
    for autre in LANGUES:
        if autre in pages and identifiant in pages[autre]:
            href = SITE + chemin_page(autre, pages[autre][identifiant][0])
            lignes.append('<link rel="alternate" hreflang="%s" href="%s">' % (autre, href))
    if LANGUE_DEFAUT in pages and identifiant in pages[LANGUE_DEFAUT]:
        href = SITE + chemin_page(LANGUE_DEFAUT, pages[LANGUE_DEFAUT][identifiant][0])
        lignes.append('<link rel="alternate" hreflang="x-default" href="%s">' % href)
    return "\n".join(lignes)


# --------------------------------------------------------------------------
# Assemblage
# --------------------------------------------------------------------------

def remplir(gabarit, valeurs):
    sortie = gabarit
    for cle, valeur in valeurs.items():
        sortie = sortie.replace("{{%s}}" % cle, valeur)
    restes = re.findall(r"\{\{(\w+)\}\}", sortie)
    if restes:
        raise SystemExit("Marqueurs de gabarit non remplis : %s" % ", ".join(sorted(set(restes))))
    return sortie


def construire():
    with open(os.path.join(GABARITS, "base.html"), encoding="utf-8") as f:
        gabarit = f.read()

    pages = charger_pages()
    if LANGUE_DEFAUT not in pages or "accueil" not in pages[LANGUE_DEFAUT]:
        raise SystemExit("Il faut au minimum contenu/fr/00-accueil.html.")

    for identifiant in ORDRE:
        if identifiant not in pages[LANGUE_DEFAUT]:
            print("  avertissement : page française manquante — %s" % identifiant)

    if os.path.isdir(SORTIE):
        shutil.rmtree(SORTIE)
    os.makedirs(SORTIE)

    # Fichiers servis tels quels.
    for nom in sorted(os.listdir(STATIQUE)):
        source = os.path.join(STATIQUE, nom)
        cible = os.path.join(SORTIE, nom)
        if os.path.isdir(source):
            shutil.copytree(source, cible)
        else:
            shutil.copy2(source, cible)

    ecrites = []
    for langue in pages:
        strings = LANGUES[langue]
        accueil_meta = pages[langue].get("accueil", pages[LANGUE_DEFAUT]["accueil"])[0]
        accueil_href = chemin_page(
            langue if "accueil" in pages[langue] else LANGUE_DEFAUT, accueil_meta
        )
        for identifiant, (meta, corps) in sorted(pages[langue].items()):
            canonical = SITE + chemin_page(langue, meta)
            valeurs = {
                "lang": langue,
                "base": "",
                "titre": meta["titre"],
                "description": meta["description"],
                "canonical": canonical,
                "hreflang": rendre_hreflang(identifiant, pages),
                "og_type": meta.get("og_type", "website"),
                "og_locale": strings["og_locale"],
                "og_titre": meta.get("og_titre", meta["titre"]),
                "og_image_alt": meta.get(
                    "og_image_alt",
                    "SANKARA, L'ÉTERNEL VEILLEUR, sculpture monumentale en acier Corten "
                    "de Hamed Ouattara, Parco Thomas Sankara, Rome",
                ),
                "jsonld": rendre_jsonld(langue, meta, pages),
                "accueil": accueil_href,
                "nav": rendre_nav(langue, identifiant, pages),
                "pied_nav": rendre_pied_nav(langue, pages),
                "langues": rendre_langues(langue, identifiant, pages),
                "contenu": corps,
                "scripts": meta.get("scripts", ""),
                "i18n_saut": strings["saut"],
                "i18n_menu": strings["menu"],
                "i18n_nav_label": strings["nav_label"],
                "i18n_marque_sous": strings["marque_sous"],
                "i18n_pied_atelier": strings["pied_atelier"],
                "i18n_pied_nav": strings["pied_nav"],
                "i18n_pied_mention": strings["pied_mention"],
            }
            page = remplir(gabarit, valeurs)
            cible = fichier_sortie(langue, meta)
            os.makedirs(os.path.dirname(cible), exist_ok=True)
            with open(cible, "w", encoding="utf-8") as f:
                f.write(page)
            if identifiant not in HORS_NAV:
                ecrites.append((canonical, meta.get("priorite", "0.6")))
            print("  %s" % os.path.relpath(cible, RACINE))

    ecrire_sitemap(ecrites)
    ecrire_robots()
    print("\n%d pages dans %s" % (len(ecrites), os.path.relpath(SORTIE, RACINE)))


def ecrire_sitemap(entrees):
    aujourdhui = date.today().isoformat()
    lignes = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for url, priorite in sorted(entrees):
        lignes.append("  <url>")
        lignes.append("    <loc>%s</loc>" % url)
        lignes.append("    <lastmod>%s</lastmod>" % aujourdhui)
        lignes.append("    <priority>%s</priority>" % priorite)
        lignes.append("  </url>")
    lignes.append("</urlset>")
    with open(os.path.join(SORTIE, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write("\n".join(lignes) + "\n")


def ecrire_robots():
    contenu = (
        "User-agent: *\n"
        "Allow: /\n"
        "\n"
        "Sitemap: %s/sitemap.xml\n" % SITE
    )
    with open(os.path.join(SORTIE, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(contenu)


if __name__ == "__main__":
    sys.exit(construire())
