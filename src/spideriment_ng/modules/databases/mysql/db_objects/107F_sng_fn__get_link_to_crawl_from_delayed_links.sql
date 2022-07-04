CREATE FUNCTION IF NOT EXISTS `sng_fn__get_link_to_crawl_from_delayed_links`
(
    `param_crawler_id` BIGINT UNSIGNED
)
RETURNS BIGINT UNSIGNED
NOT DETERMINISTIC SQL SECURITY INVOKER
BEGIN
    DECLARE `var_link_to_crawl_id` BIGINT UNSIGNED DEFAULT NULL;

    IF `param_crawler_id` IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'The input parameters of this procedure/function must not be NULL!';
    END IF;

    -- Get a link to crawl from the delayed links table, if a link whose delay has expired is there
    SELECT `link_crawling_delays`.`link_crawling_delay_link_id` INTO `var_link_to_crawl_id` FROM `link_crawling_delays`
        WHERE DATE_ADD(`link_crawling_delays`.`link_crawling_delay_delayed_since`, INTERVAL `link_crawling_delays`.`link_crawling_delay_delayed_for` SECOND) < CURRENT_TIMESTAMP
        LIMIT 1;
    IF `var_link_to_crawl_id` IS NOT NULL THEN
        CALL `sng_proc__remove_link_from_link_crawling_delays`(`var_link_to_crawl_id`);
        CALL `sng_proc__store_link_to_currently_crawled_links`(`param_crawler_id`, `var_link_to_crawl_id`);
        RETURN `var_link_to_crawl_id`;
    END IF;

    RETURN NULL;
END
