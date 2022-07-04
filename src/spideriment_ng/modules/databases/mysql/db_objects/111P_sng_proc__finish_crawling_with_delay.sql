CREATE PROCEDURE IF NOT EXISTS `sng_proc__finish_crawling_with_delay`
(
    IN `param_link_id` BIGINT UNSIGNED,
    IN `param_delayed_for` INT UNSIGNED
)
NOT DETERMINISTIC SQL SECURITY INVOKER
BEGIN
    IF `param_link_id` IS NULL OR `param_delayed_for` IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'The input parameters of this procedure/function must not be NULL!';
    END IF;

    CALL `sng_proc__remove_link_from_currently_crawled_links`(`param_link_id`);

    INSERT INTO `link_crawling_delays` (`link_crawling_delay_link_id`, `link_crawling_delay_delayed_for`)
        VALUES (`param_link_id`, `param_delayed_for`);
END
