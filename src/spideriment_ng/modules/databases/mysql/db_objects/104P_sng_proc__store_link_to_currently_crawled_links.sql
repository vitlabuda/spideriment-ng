CREATE PROCEDURE IF NOT EXISTS `sng_proc__store_link_to_currently_crawled_links`
(
    IN `param_crawler_id` BIGINT UNSIGNED,
    IN `param_link_id` BIGINT UNSIGNED
)
NOT DETERMINISTIC SQL SECURITY INVOKER
BEGIN
    IF `param_crawler_id` IS NULL OR `param_link_id` IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'The input parameters of this procedure/function must not be NULL!';
    END IF;

    INSERT INTO `currently_crawled_links` (`currently_crawled_link_active_crawler_id`, `currently_crawled_link_link_id`)
        VALUES (`param_crawler_id`, `param_link_id`);
END
