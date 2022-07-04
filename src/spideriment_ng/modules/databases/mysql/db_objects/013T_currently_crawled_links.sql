CREATE TABLE IF NOT EXISTS `currently_crawled_links` (
    `currently_crawled_link_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `currently_crawled_link_active_crawler_id` BIGINT UNSIGNED NOT NULL,
    `currently_crawled_link_link_id` BIGINT UNSIGNED NOT NULL,
    `currently_crawled_link_crawled_since` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(`currently_crawled_link_id`),
    UNIQUE KEY(`currently_crawled_link_link_id`),
    CONSTRAINT `fk_currently_crawled_link_active_crawler` FOREIGN KEY (`currently_crawled_link_active_crawler_id`) REFERENCES `active_crawlers`(`active_crawler_id`) ON UPDATE RESTRICT ON DELETE RESTRICT,
    CONSTRAINT `fk_currently_crawled_link_link` FOREIGN KEY (`currently_crawled_link_link_id`) REFERENCES `links`(`link_id`) ON UPDATE RESTRICT ON DELETE RESTRICT
) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci
