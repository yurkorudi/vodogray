ALTER TABLE cottages
    ADD COLUMN name_uk VARCHAR(150) NULL AFTER name,
    ADD COLUMN name_en VARCHAR(150) NULL AFTER name_uk,
    ADD COLUMN description_uk TEXT NULL AFTER description,
    ADD COLUMN description_en TEXT NULL AFTER description_uk,
    ADD COLUMN features_uk TEXT NULL AFTER features,
    ADD COLUMN features_en TEXT NULL AFTER features_uk;

UPDATE cottages
SET
    name_uk = COALESCE(name_uk, name),
    description_uk = COALESCE(description_uk, description),
    features_uk = COALESCE(features_uk, features);

ALTER TABLE halls
    ADD COLUMN name_uk VARCHAR(150) NULL AFTER name,
    ADD COLUMN name_en VARCHAR(150) NULL AFTER name_uk,
    ADD COLUMN description_uk TEXT NULL AFTER description,
    ADD COLUMN description_en TEXT NULL AFTER description_uk,
    ADD COLUMN features_uk TEXT NULL AFTER features,
    ADD COLUMN features_en TEXT NULL AFTER features_uk;

UPDATE halls
SET
    name_uk = COALESCE(name_uk, name),
    description_uk = COALESCE(description_uk, description),
    features_uk = COALESCE(features_uk, features);
