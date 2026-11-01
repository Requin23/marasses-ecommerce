-- Marasses: données d’initialisation pour PostgreSQL / Supabase.
-- Réexécutable. Ne supprime aucune commande.
-- Attention: rejouer ce seed remet les stocks aux quantités ci-dessous.
-- Supabase: exécuter après database/schema.sql depuis SQL Editor.
-- Docker: exécuté lors de la création initiale du volume PostgreSQL.

BEGIN;
-- Clean & Reset (Optionnel pour réinitialiser les tables de démo)
-- Réinitialisation destructive omise : les commandes existantes sont conservées.

-- 1. CATÉGORIES
INSERT INTO categories (id, name, slug, description, is_active) VALUES
('c1111111-1111-1111-1111-111111111111', 'Protection & Santé Intime', 'protection-sante-intime', 'Préservatifs, lubrifiants et soins de prévention.', true),
('c2222222-2222-2222-2222-222222222222', 'Secrets de Femmes', 'secrets-de-femmes', 'Soins d''hygiène intime, astuces et bien-être féminin.', true),
('c3333333-3333-3333-3333-333333333333', 'Sensualité, Jeux & Accessoires', 'sensualite-jeux-accessoires', 'Jeux de cartes, huiles de massage et complicité de couple.', true),
('c4444444-4444-4444-4444-444444444444', 'Packs & Coffrets', 'packs-coffrets', 'Ensembles complets et avantageux sous packaging discret.', true)
ON CONFLICT (slug) DO UPDATE SET name=EXCLUDED.name, description=EXCLUDED.description, is_active=EXCLUDED.is_active;

-- 2. ZONES DE LIVRAISON (Ouagadougou)
INSERT INTO delivery_zones (id, name, neighborhoods, fee, estimated_delay, is_active) VALUES
('a1111111-1111-1111-1111-111111111111', 'Zone A - Centre-Ville & Proche', 'Koulouba, Zogona, Dapoya, Projet ZACA, 1200 Logements', 1000.00, 'Moins de 2h', true),
('a2222222-2222-2222-2222-222222222222', 'Zone B - Ouaga 2000 & Environs', 'Ouaga 2000, Patte d''Oie, Pissy, Dassasgho, Gounghin', 1500.00, '2h à 4h', true),
('a3333333-3333-3333-3333-333333333333', 'Zone C - Périphérie', 'Saaba, Tanghin, Kamboinsin, Nagrin', 2000.00, '24h max', true)
ON CONFLICT (id) DO UPDATE SET name=EXCLUDED.name, neighborhoods=EXCLUDED.neighborhoods, fee=EXCLUDED.fee, estimated_delay=EXCLUDED.estimated_delay, is_active=EXCLUDED.is_active;

-- 3. PRODUITS
INSERT INTO products (id, category_id, name, slug, description, is_discreet, is_active) VALUES
-- Protection
('f1111111-1111-1111-1111-111111111111', 'c1111111-1111-1111-1111-111111111111', 'Préservatifs Manix / Durex Classique', 'preservatifs-classiques', 'Préservatifs de haute résistance et lubrification optimale.', true, true),
('f1222222-1111-1111-1111-111111111111', 'c1111111-1111-1111-1111-111111111111', 'Préservatifs Ultra-Fins / Sensations', 'preservatifs-ultra-fins', 'Ultra-finesse pour une sensation naturelle et intacte.', true, true),
('f2222222-2222-2222-2222-222222222222', 'c1111111-1111-1111-1111-111111111111', 'Gel Lubrifiant Base d''Eau (Naturel)', 'gel-lubrifiant-naturel', 'Formule douce à pH neutre, incolore et compatible préservatifs.', true, true),
('f2333333-2222-2222-2222-222222222222', 'c1111111-1111-1111-1111-111111111111', 'Gel Lubrifiant Aromatisé / Chauffant', 'gel-lubrifiant-aromatise', 'Gel stimulant aux parfums gourmands pour un confort ludique.', true, true),

-- Secrets de Femmes
('f3333333-3333-3333-3333-333333333333', 'c2222222-2222-2222-2222-222222222222', 'Pot de Gowé & Encens Supérieur', 'gowe-encens-superieur', 'Encens traditionnel raffiné pour la séduction et la fraîcheur.', true, true),
('f4444444-4444-4444-4444-444444444444', 'c2222222-2222-2222-2222-222222222222', 'Gel Intime Tonifiant & Soin Raffermissant', 'gel-intime-tonifiant', 'Soin naturel d''hygiène, de tonification et de confort féminin.', true, true),
('f4555555-4444-4444-4444-444444444444', 'c2222222-2222-2222-2222-222222222222', 'Préparation Kayanmata Miel & Herbes', 'kayanmata-miel-herbes', 'Mélange traditionnel de plantes et miel pour l''épanouissement.', true, true),

-- Sensualité & Jeux
('f5555555-5555-5555-5555-555555555555', 'c3333333-3333-3333-3333-333333333333', 'Huile de Massage Gourmande', 'huile-massage-gourmande', 'Huile parfumée comestible pour massages relaxants et sensuels.', true, true),
('f9999999-9999-9999-9999-999999999999', 'c3333333-3333-3333-3333-333333333333', 'Jeu de Cartes "Défis & Coquin"', 'jeu-cartes-defis-coquin', 'Jeu de cartes interactif avec gages, questions et défis de couple.', true, true),
('fa111111-1111-1111-1111-111111111111', 'c3333333-3333-3333-3333-333333333333', 'Dés Coquins Phosphorescents', 'des-coquins-phosphorescents', 'Set de 3 dés décisionnels phosphorescents pour jouer dans le noir.', true, true),
('fa222222-1111-1111-1111-111111111111', 'c3333333-3333-3333-3333-333333333333', 'Perles de Taille (Baya) Séduction', 'perles-taille-baya', 'Accessoire traditionnel fait main pour pimenter la complicité.', true, true),

-- Packs & Coffrets
('f6666666-6666-6666-6666-666666666666', 'c4444444-4444-4444-4444-444444444444', 'Pack Découverte & Sécurité', 'pack-decouverte-securite', '1 Boîte de 3 préservatifs + 1 Gel Lubrifiant 50ml.', true, true),
('f7777777-7777-7777-7777-777777777777', 'c4444444-4444-4444-4444-444444444444', 'Pack Secrets de Séduction', 'pack-secrets-seduction', '1 Pot de Gowé + 1 Préparation Kayanmata + 1 Baya offert.', true, true),
('f8888888-8888-8888-8888-888888888888', 'c4444444-4444-4444-4444-444444444444', 'Pack Soirée en Couple', 'pack-soiree-couple', '1 Boîte de 12 préservatifs + 1 Gel 80ml + 1 Huile Gourmande.', true, true),
('fb222222-2222-2222-2222-222222222222', 'c4444444-4444-4444-4444-444444444444', 'Pack Soirée Pimentée', 'pack-soiree-pimentee', '1 Jeu de Cartes Coquin + 1 Gel Aromatisé + 1 Huile Gourmande.', true, true)
ON CONFLICT (slug) DO UPDATE SET category_id=EXCLUDED.category_id, name=EXCLUDED.name, description=EXCLUDED.description, is_discreet=EXCLUDED.is_discreet, is_active=EXCLUDED.is_active;

-- 4. VARIANTES ET PRIX (FCFA)
INSERT INTO product_variants (product_id, sku, variant_name, price, stock_quantity) VALUES
('f1111111-1111-1111-1111-111111111111', 'PRE-CLA-03', 'Boîte de 3', 1200.00, 50),
('f1111111-1111-1111-1111-111111111111', 'PRE-CLA-12', 'Boîte de 12', 4500.00, 30),
('f1222222-1111-1111-1111-111111111111', 'PRE-UF-10', 'Boîte de 10', 5500.00, 20),
('f2222222-2222-2222-2222-222222222222', 'LUB-NAT-80', 'Flacon 80ml', 4800.00, 25),
('f2333333-2222-2222-2222-222222222222', 'LUB-ARO-50', 'Flacon 50ml', 3500.00, 20),
('f3333333-3333-3333-3333-333333333333', 'GOW-ENC-100', 'Pot de 100g', 2500.00, 40),
('f4444444-4444-4444-4444-444444444444', 'SEC-TON-50', 'Flacon 50ml', 6500.00, 15),
('f4555555-4444-4444-4444-444444444444', 'KAY-MIE-100', 'Pot 100g', 4000.00, 20),
('f5555555-5555-5555-5555-555555555555', 'HUI-GOU-100', 'Flacon 100ml', 3500.00, 25),
('f9999999-9999-9999-9999-999999999999', 'JEU-CAR-50', 'Boîte de 50 cartes', 3500.00, 30),
('fa111111-1111-1111-1111-111111111111', 'JEU-DES-03', 'Lot de 3 dés', 2500.00, 25),
('fa222222-1111-1111-1111-111111111111', 'BAY-TAI-01', 'Unité', 1500.00, 50),
('f6666666-6666-6666-6666-666666666666', 'PAK-DEC-01', 'Coffret Découverte', 4500.00, 20),
('f7777777-7777-7777-7777-777777777777', 'PAK-SEC-01', 'Coffret Séduction', 7500.00, 15),
('f8888888-8888-8888-8888-888888888888', 'PAK-COU-01', 'Grand Coffret Couple', 12500.00, 10),
('fb222222-2222-2222-2222-222222222222', 'PAK-PIM-01', 'Coffret Soirée Pimentée', 10000.00, 15)
ON CONFLICT (sku) DO UPDATE SET product_id=EXCLUDED.product_id, variant_name=EXCLUDED.variant_name, price=EXCLUDED.price, stock_quantity=EXCLUDED.stock_quantity;

COMMIT;
