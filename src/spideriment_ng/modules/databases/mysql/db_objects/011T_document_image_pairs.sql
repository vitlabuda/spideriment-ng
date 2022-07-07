CREATE TABLE IF NOT EXISTS `document_image_pairs` (
    `document_image_pair_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `document_image_pair_document_id` BIGINT UNSIGNED NOT NULL,
    `document_image_pair_image_id` BIGINT UNSIGNED NOT NULL,
    `document_image_pair_image_alt_text` TINYTEXT NOT NULL,
    `document_image_pair_image_title_text` TINYTEXT NOT NULL,
    PRIMARY KEY(`document_image_pair_id`),
    CONSTRAINT `fk_document_image_pair_document` FOREIGN KEY(`document_image_pair_document_id`) REFERENCES `documents`(`document_id`) ON UPDATE RESTRICT ON DELETE RESTRICT,
    CONSTRAINT `fk_document_image_pair_image` FOREIGN KEY(`document_image_pair_image_id`) REFERENCES `images`(`image_id`) ON UPDATE RESTRICT ON DELETE RESTRICT,
    INDEX(`document_image_pair_document_id`),
    INDEX(`document_image_pair_image_id`),
    FULLTEXT(`document_image_pair_image_alt_text`),
    FULLTEXT(`document_image_pair_image_title_text`)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci
