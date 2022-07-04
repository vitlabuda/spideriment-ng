CREATE TABLE IF NOT EXISTS `keywords` (
    `keyword_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `keyword_text` VARCHAR(64) NOT NULL,
    PRIMARY KEY(`keyword_id`),
    UNIQUE KEY(`keyword_text`)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci
