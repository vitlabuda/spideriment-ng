CREATE FUNCTION IF NOT EXISTS `sng_fn__handle_redirected_url_in_delayed_links`
(
    `param_crawler_id` BIGINT UNSIGNED,
    `param_redirected_url` VARCHAR(1024)
)
RETURNS BIGINT UNSIGNED
NOT DETERMINISTIC SQL SECURITY INVOKER
BEGIN
    DECLARE `var_redirected_url_link_id` BIGINT UNSIGNED DEFAULT NULL;

    IF `param_crawler_id` IS NULL OR `param_redirected_url` IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'The input parameters of this procedure/function must not be NULL!';
    END IF;

    -- If the redirected URL is part of an delayed link whose delay has already expired, select it and return it
    SELECT `link_crawling_delays`.`link_crawling_delay_link_id` INTO `var_redirected_url_link_id` FROM `link_crawling_delays`
        INNER JOIN `links` ON `link_crawling_delays`.`link_crawling_delay_link_id` = `links`.`link_id`
        WHERE `links`.`link_href_url` = `param_redirected_url`
        AND DATE_ADD(`link_crawling_delays`.`link_crawling_delay_delayed_since`, INTERVAL `link_crawling_delays`.`link_crawling_delay_delayed_for` SECOND) < CURRENT_TIMESTAMP
        LIMIT 1;
    IF `var_redirected_url_link_id` IS NOT NULL THEN
        CALL `sng_proc__remove_link_from_link_crawling_delays`(`var_redirected_url_link_id`);
        CALL `sng_proc__store_link_to_currently_crawled_links`(`param_crawler_id`, `var_redirected_url_link_id`);
        RETURN `var_redirected_url_link_id`;
    END IF;

    RETURN NULL;
END
