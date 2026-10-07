# Mise en ligne — marche à suivre

État au 7 octobre 2026 : **le site est déployé et il fonctionne.** 39 pages,
trois langues, 0 anomalie.

| | |
|---|---|
| Dépôt | `github.com/hamedouattaradesign-sys/sankara-eternel-veilleur`, public, 28 commits |
| Hébergement | **Vercel**, projet `sankara-eternel-veilleur`, équipe *Studio Hamed Ouattara* |
| Déploiement | production, depuis le commit `4cdc321`, construit en trois secondes |
| Adresse publique | `https://sankara.hamedouattara.com` — **en attente du DNS** |

Il ne reste que des gestes qui demandent vos accès.

---

## 1. L'enregistrement DNS — chez IONOS, c'est le seul vrai blocage

Le domaine `hamedouattara.com` est rattaché à votre compte Vercel, mais sa zone
DNS reste gérée chez **IONOS** (`ns1022.ui-dns.biz` et les trois autres). C'est
donc chez IONOS que l'enregistrement se crée, et personne ne peut le faire à
votre place.

Dans la gestion DNS de `hamedouattara.com`, ajouter :

| Type | Nom | Valeur | TTL |
|---|---|---|---|
| CNAME | `sankara` | `cname.vercel-dns.com` | 3600 |

Au 7 octobre, `sankara.hamedouattara.com` ne résout encore vers rien. La
propagation prend de une à quelques heures, et le certificat TLS n'est émis
qu'une fois le nom résolu.

**Rien n'est public avant ce geste**, et c'est voulu : la protection Vercel
couvre toutes les adresses `.vercel.app` du projet et laisse passer le seul
domaine propre. Tant que le CNAME n'existe pas, le site est déployé mais
personne ne peut le lire. **C'est vous qui choisissez le moment de l'ouverture,
et c'est ce geste-là qui l'ouvre.**

---

## 2. Connecter le dépôt à Vercel — trois clics, facultatif

Le projet Vercel n'est pas encore *lié* au dépôt GitHub. Le site est bien
déployé depuis le dépôt, mais je désigne le commit à chaque fois : un envoi sur
`main` ne déclenche donc rien tout seul.

Pour que chaque envoi déploie sans intervention :

**Vercel → projet `sankara-eternel-veilleur` → Settings → Git → Connect Git
Repository**, choisir `hamedouattaradesign-sys/sankara-eternel-veilleur`,
branche de production `main`.

Si vous ne le faites pas, rien n'est cassé : je lance le déploiement moi-même à
chaque fois, cela prend quelques secondes. La connexion sert surtout à ce que le
site ne dépende pas de moi.

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
prend quelques secondes, et peut se faire après l'ouverture du site.

---

## 4. Une fois le DNS propagé

- **Vérifier l'adresse** : `curl -I https://sankara.hamedouattara.com` doit
  répondre `HTTP/2 200`.
- **Déclarer le site** à Google Search Console et à Bing, et leur soumettre
  `https://sankara.hamedouattara.com/sitemap.xml`.
- **Envoyer la demande au Mémorial** (`outils/presse/demande-image-memorial.md`)
  avec le dossier signé.

---

## Le cycle de publication, ensuite

```bash
python3 outils/build.py        # reconstruit public/
python3 outils/verifier.py     # doit dire 0 anomalie
git add -A && git commit -m "…"
git push
```

Puis le déploiement : automatique si le dépôt est connecté (section 2), sinon je
le déclenche. Il n'y a rien d'autre à faire : pas de compilation, pas de
dépendance, pas de serveur.

---

## Ce que le site envoie comme en-têtes

Vérifié sur le déploiement en production, pas seulement écrit dans
`vercel.json`. La politique est stricte, et elle le peut parce que le site
n'appelle aucun service extérieur :

- `default-src 'none'` — rien n'est autorisé par défaut ;
- `connect-src 'none'` — le site ne peut faire aucune requête réseau ;
- `frame-ancestors 'none'` — il ne peut pas être encadré par un autre site ;
- le seul script en ligne est autorisé par son empreinte, pas par une
  permission générale.

S'y ajoutent `strict-transport-security` sur deux ans avec `preload`,
`x-content-type-options`, `referrer-policy`, et une `permissions-policy` qui
coupe la géolocalisation, la caméra, le micro et le pistage publicitaire.

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

Les images, le CSS, les polices et le JS sont mis en cache un an. Les pages HTML
ne sont jamais mises en cache : une correction est visible immédiatement.
