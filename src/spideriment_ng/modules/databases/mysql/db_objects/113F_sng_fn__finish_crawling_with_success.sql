CREATE FUNCTION IF NOT EXISTS `sng_fn__finish_crawling_with_success`
(
    `param_original_link_id` BIGINT UNSIGNED,
    `param_final_link_id` BIGINT UNSIGNED,
    `param_filetype` VARCHAR(32),
    `param_language` VARCHAR(32),
    `param_author` VARCHAR(128),
    `param_title` TINYTEXT,
    `param_description` TEXT
)
RETURNS BIGINT UNSIGNED
NOT DETERMINISTIC SQL SECURITY INVOKER
BEGIN
    DECLARE `var_filetype_id`, `var_language_id`, `var_author_id` BIGINT UNSIGNED DEFAULT NULL;

    IF `param_original_link_id` IS NULL
        OR `param_final_link_id` IS NULL
        OR `param_filetype` IS NULL
        OR `param_language` IS NULL
        OR `param_author` IS NULL
        OR `param_title` IS NULL
        OR `param_description` IS NULL
    THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'The input parameters of this procedure/function must not be NULL!';
    END IF;

    -- If the original link and the final link are the same, do not remove it "twice" (--> would result in an error)
    IF `param_original_link_id` = `param_final_link_id` THEN
        CALL `sng_proc__remove_link_from_currently_crawled_links`(`param_original_link_id`);
    ELSE
        CALL `sng_proc__remove_link_from_currently_crawled_links`(`param_original_link_id`);
        CALL `sng_proc__remove_link_from_currently_crawled_links`(`param_final_link_id`);
    END IF;

    -- Get the ID of the supplied filetype (add it, if it is not present in the database)
    SELECT `filetypes`.`filetype_id` INTO `var_filetype_id` FROM `filetypes`
        WHERE `filetypes`.`filetype_name` = `param_filetype`
        LIMIT 1;
    IF `var_filetype_id` IS NULL THEN
        INSERT INTO `filetypes` (`filetype_name`) VALUES (`param_filetype`);
        SELECT LAST_INSERT_ID() INTO `var_filetype_id`;
    END IF;

    -- Get the ID of the supplied language (add it, if it is not present in the database)
    SELECT `languages`.`language_id` INTO `var_language_id` FROM `languages`
        WHERE `languages`.`language_code` = `param_language`
        LIMIT 1;
    IF `var_language_id` IS NULL THEN
        INSERT INTO `languages` (`language_code`) VALUES (`param_language`);
        SELECT LAST_INSERT_ID() INTO `var_language_id`;
    END IF;

    -- Get the ID of the supplied author (add it, if it is not present in the database)
    SELECT `authors`.`author_id` INTO `var_author_id` FROM `authors`
        WHERE `authors`.`author_name` = `param_author`
        LIMIT 1;
    IF `var_author_id` IS NULL THEN
        INSERT INTO `authors` (`author_name`) VALUES (`param_author`);
        SELECT LAST_INSERT_ID() INTO `var_author_id`;
    END IF;

    INSERT INTO `documents` (`document_original_link_id`, `document_final_link_id`, `document_filetype_id`, `document_language_id`, `document_author_id`, `document_title`, `document_description`)
        VALUES (`param_original_link_id`, `param_final_link_id`, `var_filetype_id`, `var_language_id`, `var_author_id`, `param_title`, `param_description`);
    RETURN LAST_INSERT_ID();
END
