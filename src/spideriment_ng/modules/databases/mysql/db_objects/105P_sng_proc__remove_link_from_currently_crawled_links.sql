CREATE PROCEDURE IF NOT EXISTS `sng_proc__remove_link_from_currently_crawled_links`
(
    IN `param_link_id` BIGINT UNSIGNED
)
NOT DETERMINISTIC SQL SECURITY INVOKER
BEGIN
    IF `param_link_id` IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'The input parameters of this procedure/function must not be NULL!';
    END IF;

    DELETE FROM `currently_crawled_links` WHERE `currently_crawled_links`.`currently_crawled_link_link_id` = `param_link_id`;

    IF ROW_COUNT() != 1 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'The procedure/function was supposed to delete one row, but it did not!';
    END IF;
END
