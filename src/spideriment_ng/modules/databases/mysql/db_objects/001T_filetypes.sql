CREATE TABLE IF NOT EXISTS `filetypes` (
    `filetype_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `filetype_name` VARCHAR(32) NOT NULL,
    PRIMARY KEY(`filetype_id`),
    UNIQUE KEY(`filetype_name`)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci
