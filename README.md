# Marasses

Base e-commerce discrète : Nuxt 3 + Tailwind + Pinia, API FastAPI et PostgreSQL. Les prix et stocks sont recalculés côté serveur à chaque commande.

## Démarrage

1. Copiez `.env.example` vers `.env` et renseignez `DATABASE_URL`.
2. `docker compose up --build`
3. Frontend : http://localhost:3000 · API : http://localhost:8000/docs

Le schéma est dans `database/schema.sql` et les catégories, produits, variantes et zones de démonstration dans `database/seed.sql`. Sur Supabase, exécutez les deux fichiers dans cet ordre depuis SQL Editor. Le seed peut être relancé sans supprimer les commandes; il remet toutefois les stocks aux valeurs fournies. Docker exécute le schéma et le seed à la création initiale du volume PostgreSQL. Supprimer le volume `pgdata` réinitialise toute la base. Le mode discret remplace le titre de l’onglet et bascule vers une page neutre; il ne supprime pas l’historique du navigateur.
