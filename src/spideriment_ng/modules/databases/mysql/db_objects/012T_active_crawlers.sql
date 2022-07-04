CREATE TABLE IF NOT EXISTS `active_crawlers` (
    `active_crawler_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `active_crawler_instance_name` VARCHAR(64) NOT NULL,
    `active_crawler_program_name` VARCHAR(32) NOT NULL,
    `active_crawler_program_version` VARCHAR(32) NOT NULL,
    `active_crawler_active_since` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(`active_crawler_id`)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci
