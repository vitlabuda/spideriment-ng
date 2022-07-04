CREATE FUNCTION IF NOT EXISTS `sng_fn__handle_redirected_url_in_links`
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

    -- Check if the redirected URL is part of a link already present in the links table
    SELECT `links`.`link_id` INTO `var_redirected_url_link_id` FROM `links`
        WHERE `links`.`link_href_url` = `param_redirected_url`
        LIMIT 1;
    IF `var_redirected_url_link_id` IS NOT NULL THEN
        -- If so, check if it can be crawled - if so, return it; otherwise return NULL
        IF NOT EXISTS(SELECT 1 FROM `documents` WHERE `documents`.`document_original_link_id` = `var_redirected_url_link_id` OR `documents`.`document_final_link_id` = `var_redirected_url_link_id` LIMIT 1)
           AND NOT EXISTS(SELECT 1 FROM `currently_crawled_links` WHERE `currently_crawled_links`.`currently_crawled_link_link_id` = `var_redirected_url_link_id` LIMIT 1)
           AND NOT EXISTS(SELECT 1 FROM `link_crawling_delays` WHERE `link_crawling_delays`.`link_crawling_delay_link_id` = `var_redirected_url_link_id` LIMIT 1)
           AND NOT EXISTS(SELECT 1 FROM `link_crawling_errors` WHERE `link_crawling_errors`.`link_crawling_error_link_id` = `var_redirected_url_link_id` LIMIT 1)
        THEN
            CALL `sng_proc__store_link_to_currently_crawled_links`(`param_crawler_id`, `var_redirected_url_link_id`);
            RETURN `var_redirected_url_link_id`;
        END IF;

        RETURN NULL;
    END IF;

    -- Otherwise, add a new link with the redirected URL to the links table and return it
    INSERT INTO `links` (`link_href_url`) VALUES (`param_redirected_url`);
    SELECT LAST_INSERT_ID() INTO `var_redirected_url_link_id`;
    CALL `sng_proc__store_link_to_currently_crawled_links`(`param_crawler_id`, `var_redirected_url_link_id`);
    RETURN `var_redirected_url_link_id`;
END
