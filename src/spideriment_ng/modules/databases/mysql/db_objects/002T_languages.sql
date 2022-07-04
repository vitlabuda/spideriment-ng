CREATE TABLE IF NOT EXISTS `languages` (
    `language_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `language_code` VARCHAR(32) NOT NULL,
    PRIMARY KEY(`language_id`),
    UNIQUE KEY(`language_code`)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci
