CREATE TABLE IF NOT EXISTS `images` (
    `image_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `image_src_url` VARCHAR(1024) NOT NULL,
    PRIMARY KEY(`image_id`),
    UNIQUE KEY(`image_src_url`)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci
