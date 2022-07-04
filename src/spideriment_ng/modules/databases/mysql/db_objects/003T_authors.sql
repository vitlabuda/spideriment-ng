CREATE TABLE IF NOT EXISTS `authors` (
    `author_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `author_name` VARCHAR(128) NOT NULL,
    PRIMARY KEY(`author_id`),
    UNIQUE KEY(`author_name`)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci
