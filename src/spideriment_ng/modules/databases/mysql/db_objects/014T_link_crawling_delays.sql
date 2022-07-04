CREATE TABLE IF NOT EXISTS `link_crawling_delays` (
    `link_crawling_delay_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `link_crawling_delay_link_id` BIGINT UNSIGNED NOT NULL,
    `link_crawling_delay_delayed_since` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `link_crawling_delay_delayed_for` INT UNSIGNED NOT NULL,
    PRIMARY KEY(`link_crawling_delay_id`),
    UNIQUE KEY(`link_crawling_delay_link_id`),
    CONSTRAINT `fk_link_crawling_delay_link` FOREIGN KEY (`link_crawling_delay_link_id`) REFERENCES `links`(`link_id`) ON UPDATE RESTRICT ON DELETE RESTRICT
) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci
