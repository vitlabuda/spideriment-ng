CREATE TABLE IF NOT EXISTS `document_keyword_pairs` (
    `document_keyword_pair_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `document_keyword_pair_document_id` BIGINT UNSIGNED NOT NULL,
    `document_keyword_pair_keyword_id` BIGINT UNSIGNED NOT NULL,
    PRIMARY KEY(`document_keyword_pair_id`),
    CONSTRAINT `fk_document_keyword_pair_document` FOREIGN KEY(`document_keyword_pair_document_id`) REFERENCES `documents`(`document_id`) ON UPDATE RESTRICT ON DELETE RESTRICT,
    CONSTRAINT `fk_document_keyword_pair_keyword` FOREIGN KEY(`document_keyword_pair_keyword_id`) REFERENCES `keywords`(`keyword_id`) ON UPDATE RESTRICT ON DELETE RESTRICT,
    INDEX(`document_keyword_pair_document_id`),
    INDEX(`document_keyword_pair_keyword_id`)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci
