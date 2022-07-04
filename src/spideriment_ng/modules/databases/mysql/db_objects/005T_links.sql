CREATE TABLE IF NOT EXISTS `links` (
    `link_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `link_href_url` VARCHAR(1024) NOT NULL,
    PRIMARY KEY(`link_id`),
    UNIQUE KEY(`link_href_url`)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci
