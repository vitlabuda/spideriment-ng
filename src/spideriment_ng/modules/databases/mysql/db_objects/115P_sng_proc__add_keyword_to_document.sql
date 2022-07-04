CREATE PROCEDURE IF NOT EXISTS `sng_proc__add_keyword_to_document`
(
    IN `param_document_id` BIGINT UNSIGNED,
    IN `param_keyword` VARCHAR(64)
)
NOT DETERMINISTIC SQL SECURITY INVOKER
BEGIN
    DECLARE `var_keyword_id` BIGINT UNSIGNED DEFAULT NULL;

    IF `param_document_id` IS NULL OR `param_keyword` IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'The input parameters of this procedure/function must not be NULL!';
    END IF;

    -- Get the ID of the supplied keyword (add it, if it is not present in the database)
    SELECT `keywords`.`keyword_id` INTO `var_keyword_id` FROM `keywords`
        WHERE `keywords`.`keyword_text` = `param_keyword`
        LIMIT 1;
    IF `var_keyword_id` IS NULL THEN
        INSERT INTO `keywords` (`keyword_text`) VALUES (`param_keyword`);
        SELECT LAST_INSERT_ID() INTO `var_keyword_id`;
    END IF;

    INSERT INTO `document_keyword_pairs` (`document_keyword_pair_document_id`, `document_keyword_pair_keyword_id`)
        VALUES (`param_document_id`, `var_keyword_id`);
END
