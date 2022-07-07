CREATE TABLE IF NOT EXISTS `content_snippets` (
    `content_snippet_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `content_snippet_document_id` BIGINT UNSIGNED NOT NULL,
    `content_snippet_type` ENUM(
        'heading_1',
        'heading_2',
        'heading_3',
        'heading_4',
        'heading_5',
        'emphasized_text',
        'regular_text',
        'list_item_text',
        'uncategorized_text',
        'fallback_text'
    ) NOT NULL,
    `content_snippet_text` TEXT NOT NULL,
    PRIMARY KEY(`content_snippet_id`),
    CONSTRAINT `fk_content_snippet_document` FOREIGN KEY(`content_snippet_document_id`) REFERENCES `documents`(`document_id`) ON UPDATE RESTRICT ON DELETE RESTRICT,
    INDEX(`content_snippet_document_id`),
    INDEX(`content_snippet_type`),
    FULLTEXT(`content_snippet_text`)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci
