-- Nouveaux produits Marasses (catalogue photos réelles, prix FCFA).
-- Réexécutable : met à jour les fiches et remet le stock à 30 à chaque exécution.
-- Met le stock de toutes les variantes (existantes et nouvelles) à 30.
BEGIN;

INSERT INTO products (category_id, name, slug, description, is_discreet, is_active)
SELECT c.id, p.name, p.slug, p.description, true, true
FROM (VALUES
  ('Protection & Santé Intime', 'Lubrifiant Vibrant Kiss Menthe (70 ml)', 'vibrant-kiss-menthe', 'Lubrifiant à base d’eau, parfum menthe. Consulter les indications de l’emballage.'),
  ('Protection & Santé Intime', 'Gel Mami — lot de 3', 'gel-mami-lot-3', 'Lot de trois gels. Se référer à l’emballage pour la composition et les précautions.'),
  ('Protection & Santé Intime', 'Produit Manar aromatisé — Fraise', 'manar-fraise', 'Produit aromatisé pour adultes. Vérifier l’usage et les précautions indiqués sur l’emballage.'),
  ('Protection & Santé Intime', 'Produit Manar aromatisé — Menthe', 'manar-menthe', 'Produit aromatisé pour adultes. Vérifier l’usage et les précautions indiqués sur l’emballage.'),
  ('Protection & Santé Intime', 'Produit Manar aromatisé — Chocolat', 'manar-chocolat', 'Produit aromatisé pour adultes. Vérifier l’usage et les précautions indiqués sur l’emballage.'),
  ('Protection & Santé Intime', 'Spray retardateur pour homme', 'spray-retardateur-homme', 'Spray à usage externe. Lire et suivre les précautions indiquées sur l’emballage.'),
  ('Sensualité, Jeux & Accessoires', 'Jouet intime Kiki', 'jouet-intime-kiki', 'Accessoire intime pour adulte. Nettoyer selon les indications du fabricant.'),
  ('Sensualité, Jeux & Accessoires', 'Vibro en forme de rouge à lèvres', 'vibro-rouge-a-levres', 'Accessoire intime pour adulte. Nettoyer selon les indications du fabricant.'),
  ('Sensualité, Jeux & Accessoires', 'Smart Scalp Massager', 'smart-scalp-massager', 'Masseur du cuir chevelu. Suivre le mode d’emploi du fabricant.'),
  ('Sensualité, Jeux & Accessoires', 'Appareil de massage multi-embouts', 'appareil-massage', 'Appareil de massage avec accessoires. Suivre le mode d’emploi du fabricant.'),
  ('Sensualité, Jeux & Accessoires', 'Accessoire intime en forme de langue', 'jouet-langue', 'Accessoire intime pour adulte. Nettoyer selon les indications du fabricant.'),
  ('Sensualité, Jeux & Accessoires', 'Œuf intime', 'oeuf-intime', 'Accessoire intime pour adulte. Nettoyer selon les indications du fabricant.'),
  ('Sensualité, Jeux & Accessoires', 'Mousse de massage Vibrant Kiss (150 ml)', 'mousse-massage-vibrant-kiss', 'Mousse de massage parfum menthe. Lire les précautions sur l’emballage.'),
  ('Sensualité, Jeux & Accessoires', 'Kit de jeu avec accessoires', 'kit-torture', 'Kit d’accessoires pour adultes. Utiliser selon les indications du fabricant.'),
  ('Sensualité, Jeux & Accessoires', 'Kit secret avec perles et cadenas', 'kit-secret-perles-cadenas', 'Kit d’accessoires livré avec des perles. Vérifier le contenu à la réception.'),
  ('Sensualité, Jeux & Accessoires', 'Parfum excitant Maxman', 'parfum-intimite', 'Spray pour homme à usage externe. Suivre les précautions indiquées sur l’emballage; les effets annoncés ne sont pas garantis.'),
  ('Secrets de Femmes', 'Parfum traditionnel — lot de 3', 'parfum-argent-lot-3', 'Lot de trois parfums. Les promesses de résultats ou d’effets ne sont pas garanties.')
) AS p(category_name, name, slug, description)
JOIN categories c ON c.name = p.category_name
ON CONFLICT (slug) DO UPDATE SET
  category_id = EXCLUDED.category_id,
  name = EXCLUDED.name,
  description = EXCLUDED.description,
  is_discreet = EXCLUDED.is_discreet,
  is_active = EXCLUDED.is_active;

-- Si une ancienne version du fichier a déjà été exécutée, masquer l’entrée
-- temporaire « menthe-manar » sans supprimer son historique de commandes.
UPDATE products SET is_active = false WHERE slug = 'menthe-manar';

INSERT INTO product_variants (product_id, sku, variant_name, price, stock_quantity)
SELECT p.id, v.sku, v.variant_name, v.price, 30
FROM (VALUES
  ('vibrant-kiss-menthe', 'MAR-VK-MENTHE-70', 'Tube 70 ml', 3000),
  ('gel-mami-lot-3', 'MAR-GEL-MAMI-3', 'Lot de 3', 3000),
  ('manar-fraise', 'MAR-MANAR-FRAISE', 'Unité · Fraise', 2500),
  ('manar-menthe', 'MAR-MANAR-MENTHE', 'Unité · Menthe', 2500),
  ('manar-chocolat', 'MAR-MANAR-CHOCOLAT', 'Unité · Chocolat', 2500),
  ('spray-retardateur-homme', 'MAR-SPRAY-RETARD-45', 'Unité', 1000),
  ('jouet-intime-kiki', 'MAR-JOUET-KIKI', 'Unité', 25000),
  ('vibro-rouge-a-levres', 'MAR-VIBRO-ROUGE', 'Unité', 2500),
  ('smart-scalp-massager', 'MAR-SCALP-MASSAGER', 'Unité', 6000),
  ('appareil-massage', 'MAR-MASSAGE-MULTI', 'Unité', 7500),
  ('jouet-langue', 'MAR-JOUET-LANGUE', 'Unité', 7500),
  ('oeuf-intime', 'MAR-OEUF-INTIME', 'Unité', 4500),
  ('mousse-massage-vibrant-kiss', 'MAR-VK-MOUSSE-150', 'Flacon 150 ml', 6000),
  ('kit-torture', 'MAR-KIT-JEU', 'Kit', 7500),
  ('kit-secret-perles-cadenas', 'MAR-KIT-PERLES', 'Kit', 4500),
  ('parfum-intimite', 'MAR-PARFUM-INTIMITE', 'Unité', 4000),
  ('parfum-argent-lot-3', 'MAR-PARFUM-ARGENT-3', 'Lot de 3', 5000)
) AS v(slug, sku, variant_name, price)
JOIN products p ON p.slug = v.slug
ON CONFLICT (sku) DO UPDATE SET
  product_id = EXCLUDED.product_id,
  variant_name = EXCLUDED.variant_name,
  price = EXCLUDED.price,
  stock_quantity = 30;

-- La demande porte sur tout le catalogue, y compris les articles plus anciens.
UPDATE product_variants SET stock_quantity = 30;

COMMIT;
