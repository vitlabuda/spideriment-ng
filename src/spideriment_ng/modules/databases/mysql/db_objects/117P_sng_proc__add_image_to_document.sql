CREATE PROCEDURE IF NOT EXISTS `sng_proc__add_image_to_document`
(
    IN `param_document_id` BIGINT UNSIGNED,
    IN `param_image_url` VARCHAR(1024),
    IN `param_image_alt_text` TINYTEXT,
    IN `param_image_title_text` TINYTEXT
)
NOT DETERMINISTIC SQL SECURITY INVOKER
BEGIN
    DECLARE `var_image_id` BIGINT UNSIGNED DEFAULT NULL;

    IF `param_document_id` IS NULL OR `param_image_url` IS NULL OR `param_image_alt_text` IS NULL OR `param_image_title_text` IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'The input parameters of this procedure/function must not be NULL!';
    END IF;

    -- Get the ID of the supplied image (add it, if it is not present in the database)
    SELECT `images`.`image_id` INTO `var_image_id` FROM `images`
        WHERE `images`.`image_src_url` = `param_image_url`
        LIMIT 1;
    IF `var_image_id` IS NULL THEN
        INSERT INTO `images` (`image_src_url`) VALUES (`param_image_url`);
        SELECT LAST_INSERT_ID() INTO `var_image_id`;
    END IF;

    INSERT INTO `document_image_pairs` (`document_image_pair_document_id`, `document_image_pair_image_id`, `document_image_pair_image_alt_text`, `document_image_pair_image_title_text`)
        VALUES (`param_document_id`, `var_image_id`, `param_image_alt_text`, `param_image_title_text`);
END
