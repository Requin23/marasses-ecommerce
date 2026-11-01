# Marasses

Base e-commerce discrète : Nuxt 3 + Tailwind + Pinia, API FastAPI et PostgreSQL. Les prix et stocks sont recalculés côté serveur à chaque commande.

## Démarrage

1. Copiez `.env.example` vers `.env` et renseignez `DATABASE_URL`.
2. Pour utiliser Supabase, copiez l’URI PostgreSQL depuis **Project → Connect** et mettez-la dans `DATABASE_URL` du fichier `.env` (choisir **Session pooler** si le réseau ne prend pas en charge IPv6). L’API accepte les URI `postgres://` et `postgresql://` de Supabase et utilise psycopg. Ne collez jamais cette URL dans le frontend ou dans GitHub.
3. `docker compose up --build`
4. Frontend : http://localhost:3000 · API : http://localhost:8000/docs · Santé DB : http://localhost:8000/api/health

Le schéma est dans `database/schema.sql` et les catégories, produits, variantes et zones de démonstration dans `database/seed.sql`. Sur Supabase, exécutez les deux fichiers dans cet ordre depuis SQL Editor. Le seed peut être relancé sans supprimer les commandes; il remet toutefois les stocks aux valeurs fournies. Docker exécute le schéma et le seed à la création initiale du volume PostgreSQL. Supprimer le volume `pgdata` réinitialise toute la base. Le mode discret remplace le titre de l’onglet et bascule vers une page neutre; il ne supprime pas l’historique du navigateur.


### Vérifier la connexion Supabase

Après avoir configuré `DATABASE_URL`, démarrez avec `docker compose up --build`. La route `/api/health` doit répondre `{"status":"ok","database":"connected"}`. Ensuite, ouvrez le site pour vérifier les produits et la page checkout. Une commande de test crée une vraie commande et décrémente le stock : faites-la seulement avec des données de test.


### Paiement GeniusPay (mode Sandbox)

1. Avant de redémarrer une base Supabase déjà existante, exécute `database/migrations/001_geniuspay.sql` dans le SQL Editor. Les installations neuves reçoivent ces colonnes via `database/schema.sql`.
2. Dans le fichier `.env` local, renseigne `GENIUSPAY_API_KEY` et `GENIUSPAY_API_SECRET` avec les clés **Sandbox** de GeniusPay. Ne les mets jamais dans le frontend ou dans GitHub.
3. Garde `GENIUSPAY_ENVIRONMENT=sandbox` pendant les essais et `APP_PUBLIC_URL=http://localhost:3000` en local. Reconstruis avec `docker compose up --build`.
4. À la validation, l’API crée la commande et la session GeniusPay, puis le navigateur ouvre le checkout hébergé. Le retour vérifie l’état directement auprès de GeniusPay; l’URL de retour seule n’est jamais considérée comme une preuve de paiement.
5. En production, configure le webhook GeniusPay vers `https://marasses.bf/api/webhooks/geniuspay`, renseigne `GENIUSPAY_WEBHOOK_SECRET` et mets `APP_PUBLIC_URL=https://marasses.bf`. Une adresse `localhost` ne peut pas recevoir de webhook public.

Le flux Sandbox n’a pas été testé contre un paiement réel.


### Position de livraison facultative

Au checkout, la personne peut cocher son accord puis cliquer pour déclencher la demande de localisation du navigateur. Si elle accepte et confirme la commande, la latitude, la longitude, la précision estimée et l’heure du consentement sont enregistrées avec la commande. L’affichage de la carte OpenStreetMap transmet également les coordonnées à OpenStreetMap. La localisation reste facultative.

Pour une base Supabase existante, exécutez `database/migrations/002_delivery_location.sql` dans le SQL Editor **avant de publier** la version qui enregistre les coordonnées. Une nouvelle base ajoute les colonnes directement via `database/schema.sql`.

### Aide et réclamations

La page `/assistance` enregistre les demandes dans la table Supabase `support_requests`. Après déploiement, consultez ces demandes dans **Supabase → Table Editor → support_requests**. Pour afficher le bouton WhatsApp, définissez `NUXT_PUBLIC_WHATSAPP_NUMBER` dans les variables Vercel au format international sans `+`, espaces ou tirets (par exemple `226XXXXXXXX`), puis redéployez le frontend. Pour une base existante, exécutez `database/migrations/003_support_requests.sql` avant de publier cette version.


### Prévisualisation gratuite (pas pour une boutique en production)

Le dépôt contient `render.yaml` pour publier l’API FastAPI sur Render. Pour une prévisualisation, le site Nuxt peut être publié sur Vercel en reliant le dépôt GitHub et en choisissant `frontend` comme répertoire racine. L’offre Hobby de Vercel est réservée à un usage personnel non commercial; l’offre gratuite Render est également limitée et Render déconseille de l’utiliser pour une application en production. Une boutique qui vend réellement ne doit donc pas compter sur ces offres gratuites.

1. Sur Render, crée un **Blueprint** à partir du dépôt GitHub et choisis `render.yaml`. Le service API demande les variables `DATABASE_URL`, `CORS_ORIGINS` et `APP_PUBLIC_URL`; garde `GENIUSPAY_ENVIRONMENT=sandbox`.
2. Une fois l’API publiée, copie son adresse `https://…onrender.com`.
3. Sur Vercel, importe le dépôt, choisis `frontend` comme **Root Directory** et le preset Nuxt. Ajoute `NUXT_PUBLIC_API_BASE` et `NUXT_API_INTERNAL_BASE`, toutes deux avec l’adresse de l’API suivie de `/api` (par exemple `https://…onrender.com/api`). Publie le site.
4. Copie l’adresse `https://…vercel.app` du site et retourne sur Render pour mettre cette adresse dans `CORS_ORIGINS` et `APP_PUBLIC_URL`, puis redéploie l’API.
5. Vérifie `/api/health`, le catalogue, le panier et le checkout. L’API gratuite Render peut s’endormir après 15 minutes sans visite, puis prendre environ une minute à se réveiller. Laisse les paiements GeniusPay en Sandbox.

Les adresses gratuites `vercel.app` et `onrender.com` conviennent à une prévisualisation. Un domaine personnalisé comme `marasses.bf` doit être acheté séparément, puis relié dans le tableau de bord de l’hébergeur.

### Administration

La page privée est disponible à l’adresse `https://votre-site.vercel.app/admin`. Dans Render, ajoutez une variable secrète `ADMIN_API_KEY` d’au moins 32 caractères au service `marasses-api`, puis redéployez l’API. Utilisez un mot de passe aléatoire distinct; ne le mettez ni dans GitHub ni dans Vercel. La page permet de consulter les 100 dernières commandes, voir l’adresse et la position éventuellement partagée par le client, faire avancer leur état, et modifier le prix ou le stock des variantes. La session expire après 12 heures.


### Mise en ligne sur un serveur Linux

Le dépôt GitHub relié à Supabase gère l’intégration de la base; il ne publie pas à lui seul le site Nuxt ni l’API FastAPI. Le fichier `docker-compose.prod.yml` lance l’API, le site et Caddy (HTTPS automatique) sur un serveur disposant de Docker Compose.

1. Vérifie que `marasses.bf` pointe par DNS vers l’adresse IP publique du serveur et que les ports 80/443 sont accessibles.
2. Sur le serveur, copie `.env.production.example` en `.env.production` et renseigne le domaine, l’URI Supabase et les clés GeniusPay choisies. Ne transfère jamais ce fichier dans GitHub.
3. Assure-toi que `database/migrations/001_geniuspay.sql` a été exécuté sur Supabase.
4. Dans le dossier du projet sur le serveur, lance `docker compose --env-file .env.production -f docker-compose.prod.yml up -d --build`.
5. Vérifie `https://marasses.bf` et `https://marasses.bf/api/health`.

Le fichier `.env.production.example` part en Sandbox par défaut. Les clés Live doivent être placées uniquement sur le serveur de production, après validation du checkout Sandbox. Configure ensuite dans GeniusPay le webhook `https://marasses.bf/api/webhooks/geniuspay` avec son secret.
