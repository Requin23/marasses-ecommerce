# Marasses

Base e-commerce discrète : Nuxt 3 + Tailwind + Pinia, API FastAPI et PostgreSQL. Les prix et stocks sont recalculés côté serveur à chaque commande.

## Démarrage

1. Copiez `.env.example` vers `.env` et renseignez `DATABASE_URL`.
2. `docker compose up --build`
3. Frontend : http://localhost:3000 · API : http://localhost:8000/docs

Le schéma initial est dans `database/schema.sql`. Configurez des zones et produits avant les commandes. Le mode discret remplace le titre de l’onglet et bascule vers une page neutre; il ne supprime pas l’historique du navigateur.
