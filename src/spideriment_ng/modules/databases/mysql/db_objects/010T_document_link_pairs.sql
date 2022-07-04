CREATE TABLE IF NOT EXISTS `document_link_pairs` (
    `document_link_pair_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `document_link_pair_document_id` BIGINT UNSIGNED NOT NULL,
    `document_link_pair_link_id` BIGINT UNSIGNED NOT NULL,
    `document_link_pair_link_text` TINYTEXT NOT NULL,
    PRIMARY KEY(`document_link_pair_id`),
    CONSTRAINT `fk_document_link_pair_document` FOREIGN KEY(`document_link_pair_document_id`) REFERENCES `documents`(`document_id`) ON UPDATE RESTRICT ON DELETE RESTRICT,
    CONSTRAINT `fk_document_link_pair_link` FOREIGN KEY(`document_link_pair_link_id`) REFERENCES `links`(`link_id`) ON UPDATE RESTRICT ON DELETE RESTRICT
) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci
