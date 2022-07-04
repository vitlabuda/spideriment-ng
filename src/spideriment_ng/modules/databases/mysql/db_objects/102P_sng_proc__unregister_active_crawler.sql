CREATE PROCEDURE IF NOT EXISTS `sng_proc__unregister_active_crawler`
(
    IN `param_crawler_id` BIGINT UNSIGNED
)
NOT DETERMINISTIC SQL SECURITY INVOKER
BEGIN
    IF `param_crawler_id` IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'The input parameters of this procedure/function must not be NULL!';
    END IF;

    DELETE FROM `active_crawlers` WHERE `active_crawlers`.`active_crawler_id` = `param_crawler_id`;

    IF ROW_COUNT() != 1 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'The procedure/function was supposed to delete one row, but it did not!';
    END IF;
END
