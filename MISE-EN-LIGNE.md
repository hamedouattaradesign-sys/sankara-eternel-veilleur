# Mise en ligne — marche à suivre

Le site est prêt. Il ne reste que des gestes qui demandent vos accès.

État au 7 octobre 2026 : 39 pages, trois langues, 0 anomalie. Hébergement
**Vercel**, projet `sankara-eternel-veilleur` déjà créé dans l'équipe *Studio
Hamed Ouattara*, domaine `sankara.hamedouattara.com` déjà rattaché au projet.

---

## 1. Créer le dépôt GitHub — une minute

Je ne peux pas le créer moi-même : l'intégration GitHub de cette session n'a pas
ce droit, et elle répond `403`. C'est le seul geste qui bloque.

Sur **github.com → New repository** :

| Champ | Valeur |
|---|---|
| Repository name | `sankara-eternel-veilleur` |
| Visibilité | **Public** |
| Add a README | **non**, décoché |
| .gitignore / licence | **aucun** |

Le dépôt doit rester **vide**. S'il contient un README, le premier envoi sera
refusé.

Dites-le-moi ensuite : je pousse les vingt-six commits, et Vercel déploie tout
seul dans la minute.

---

## 2. L'enregistrement DNS — à faire chez IONOS

Le domaine `hamedouattara.com` est bien rattaché à votre compte Vercel, mais sa
zone DNS reste gérée chez **IONOS** (`ns1022.ui-dns.biz` et les trois autres).
C'est donc chez IONOS que l'enregistrement se crée, et personne ne peut le faire
à votre place.

Dans la gestion DNS de `hamedouattara.com`, ajouter :

| Type | Nom | Valeur | TTL |
|---|---|---|---|
| CNAME | `sankara` | `cname.vercel-dns.com` | 3600 |

**À faire dès maintenant, avant même la mise en ligne.** La propagation prend de
une à quelques heures, et le certificat TLS n'est émis qu'une fois le nom
résolu. Autant que cela tourne pendant que le reste se termine.

Tant que le DNS n'a pas basculé, le site reste accessible sur l'adresse
`.vercel.app` du projet.

---

## 3. Signer le dossier institutionnel

La deuxième édition réserve une zone de paraphe en fin de document. Trois points
à vérifier avant de signer :

- le **lieu** et la **date** du bloc de signature — aujourd'hui Ouagadougou,
  6 octobre 2026 ;
- la section **« Orienté nord-sud »**, qui n'existait pas dans la première
  édition ;
- le comptage : **douze rangées, 48 par face de texture, 152 au total**.

Renvoyez-moi le PDF signé : je le mets en place et je redéploie. L'opération
prend quelques secondes, et peut se faire après la mise en ligne du site.

---

## 4. Après la mise en ligne

- **Vérifier l'adresse** une fois le DNS propagé :
  `curl -I https://sankara.hamedouattara.com` doit répondre `HTTP/2 200`.
- **Déclarer le site** à Google Search Console et à Bing, et leur soumettre
  `https://sankara.hamedouattara.com/sitemap.xml`.
- **Envoyer la demande au Mémorial** (`outils/presse/demande-image-memorial.md`)
  avec le dossier signé.

---

## Ce qui déclenche un déploiement, ensuite

Chaque envoi sur la branche principale. Le cycle complet est :

```bash
python3 outils/build.py        # reconstruit public/
python3 outils/verifier.py     # doit dire 0 anomalie
git add -A && git commit -m "…"
git push
```

Vercel reconstruit et met en ligne dans la minute. Il n'y a rien d'autre à
faire : pas de compilation, pas de dépendance, pas de serveur.

---

## Ce que le site envoie comme en-têtes

`vercel.json` pose une politique de sécurité stricte, possible parce que le site
n'appelle aucun service extérieur :

- `default-src 'none'` — rien n'est autorisé par défaut ;
- `connect-src 'none'` — le site ne peut faire aucune requête réseau ;
- `frame-ancestors 'none'` — il ne peut pas être encadré par un autre site ;
- le seul script en ligne est autorisé par son empreinte, pas par une
  permission générale.

**Si un script en ligne est un jour ajouté ou modifié**, son empreinte change et
il sera bloqué. Recalculer la nouvelle valeur et la reporter dans
`vercel.json` :

```bash
python3 -c "
import hashlib, base64, re, io
s = io.open('public/index.html', encoding='utf-8').read()
for m in re.findall(r'<script>(.*?)</script>', s, re.S):
    print('sha256-' + base64.b64encode(hashlib.sha256(m.encode()).digest()).decode())
"
```

Les images, le CSS et le JS sont mis en cache un an — leurs noms changent quand
leur contenu change. Les pages HTML ne sont jamais mises en cache : une
correction est visible immédiatement.
