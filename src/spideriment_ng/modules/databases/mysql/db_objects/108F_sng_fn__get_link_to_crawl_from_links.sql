CREATE FUNCTION IF NOT EXISTS `sng_fn__get_link_to_crawl_from_links`
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

    -- Get a link to crawl from the links table - links which have already been crawled/are currently crawled are not selected
    SELECT `links`.`link_id` INTO `var_link_to_crawl_id` FROM `links`
        WHERE NOT EXISTS(SELECT 1 FROM `documents` WHERE `documents`.`document_original_link_id` = `links`.`link_id` OR `documents`.`document_final_link_id` = `links`.`link_id` LIMIT 1)
        AND NOT EXISTS(SELECT 1 FROM `currently_crawled_links` WHERE `currently_crawled_links`.`currently_crawled_link_link_id` = `links`.`link_id` LIMIT 1)
        AND NOT EXISTS(SELECT 1 FROM `link_crawling_delays` WHERE `link_crawling_delays`.`link_crawling_delay_link_id` = `links`.`link_id` LIMIT 1)
        AND NOT EXISTS(SELECT 1 FROM `link_crawling_errors` WHERE `link_crawling_errors`.`link_crawling_error_link_id` = `links`.`link_id` LIMIT 1)
        LIMIT 1;
    IF `var_link_to_crawl_id` IS NOT NULL THEN
        CALL `sng_proc__store_link_to_currently_crawled_links`(`param_crawler_id`, `var_link_to_crawl_id`);
        RETURN `var_link_to_crawl_id`;
    END IF;

    RETURN NULL;
END
