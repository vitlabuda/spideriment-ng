CREATE PROCEDURE IF NOT EXISTS `sng_proc__add_link_to_document`
(
    IN `param_document_id` BIGINT UNSIGNED,
    IN `param_link_url` VARCHAR(1024),
    IN `param_link_text` TINYTEXT
)
NOT DETERMINISTIC SQL SECURITY INVOKER
BEGIN
    DECLARE `var_link_id` BIGINT UNSIGNED DEFAULT NULL;

    IF `param_document_id` IS NULL OR `param_link_url` IS NULL OR `param_link_text` IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'The input parameters of this procedure/function must not be NULL!';
    END IF;

    -- Get the ID of the supplied link (add it, if it is not present in the database)
    SELECT `links`.`link_id` INTO `var_link_id` FROM `links`
        WHERE `links`.`link_href_url` = `param_link_url`
        LIMIT 1;
    IF `var_link_id` IS NULL THEN
        INSERT INTO `links` (`link_href_url`) VALUES (`param_link_url`);
        SELECT LAST_INSERT_ID() INTO `var_link_id`;
    END IF;

    INSERT INTO `document_link_pairs` (`document_link_pair_document_id`, `document_link_pair_link_id`, `document_link_pair_link_text`)
        VALUES (`param_document_id`, `var_link_id`, `param_link_text`);
END
