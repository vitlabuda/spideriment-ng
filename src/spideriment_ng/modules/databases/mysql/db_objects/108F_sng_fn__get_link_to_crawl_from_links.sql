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

    -- OPTIMIZATION: Select a small amount of random links from the huge links table and apply the WHERE conditions on it -->
    --  on a links table with 500 000 rows, this takes about 0.1 seconds; however, this query might incorrectly assume
    --  that there are no more links to crawl if all of the randomly selected links have been already crawled (the probability
    --  of this happening is EXTREMELY SMALL, but it is possible)
    SELECT `tmp_links`.`link_id` INTO `var_link_to_crawl_id`
        FROM (
            SELECT `links`.`link_id` AS `link_id` FROM `links`
            ORDER BY RAND()
            LIMIT 100
        ) `tmp_links`
        WHERE NOT EXISTS(SELECT 1 FROM `documents` WHERE `documents`.`document_original_link_id` = `tmp_links`.`link_id` OR `documents`.`document_final_link_id` = `tmp_links`.`link_id` LIMIT 1)
        AND NOT EXISTS(SELECT 1 FROM `currently_crawled_links` WHERE `currently_crawled_links`.`currently_crawled_link_link_id` = `tmp_links`.`link_id` LIMIT 1)
        AND NOT EXISTS(SELECT 1 FROM `link_crawling_delays` WHERE `link_crawling_delays`.`link_crawling_delay_link_id` = `tmp_links`.`link_id` LIMIT 1)
        AND NOT EXISTS(SELECT 1 FROM `link_crawling_errors` WHERE `link_crawling_errors`.`link_crawling_error_link_id` = `tmp_links`.`link_id` LIMIT 1)
        LIMIT 1;
    IF `var_link_to_crawl_id` IS NOT NULL THEN
        CALL `sng_proc__store_link_to_currently_crawled_links`(`param_crawler_id`, `var_link_to_crawl_id`);
        RETURN `var_link_to_crawl_id`;
    END IF;

    -- If the above query fails (which it might), resort to using this WAY SLOWER query, which, however, always returns
    --  a "correct" result --> on a links table with 500 000 rows, this takes about 22 seconds!
    -- PS: An attempt was made to optimize this query using LEFT OUTER JOIN, but it proved to be even slower.
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
