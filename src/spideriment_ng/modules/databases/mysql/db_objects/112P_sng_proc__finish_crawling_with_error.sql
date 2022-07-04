CREATE PROCEDURE IF NOT EXISTS `sng_proc__finish_crawling_with_error`
(
    IN `param_link_id` BIGINT UNSIGNED,
    IN `param_error_reason` ENUM(
        'fetch_connection_error',
        'fetch_not_found',
        'fetch_forbidden',
        'fetch_server_error',
        'fetch_too_many_redirects',
        'fetch_uncategorized_error',
        'robots_forbidden',
        'robots_delay_too_long',
        'robots_uncategorized_error',
        'parse_unsupported_type',
        'parse_cut_off_content',
        'parse_invalid_format',
        'parse_invalid_content',
        'parse_forbidden',
        'parse_uncategorized_error',
        'validation_url_problem',
        'validation_document_problem',
        'validation_uncategorized_error',
        'final_url_not_crawlable',
        'uncategorized_error',
        'unknown_error'
    )
)
NOT DETERMINISTIC SQL SECURITY INVOKER
BEGIN
    IF `param_link_id` IS NULL OR `param_error_reason` IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'The input parameters of this procedure/function must not be NULL!';
    END IF;

    CALL `sng_proc__remove_link_from_currently_crawled_links`(`param_link_id`);

    INSERT INTO `link_crawling_errors` (`link_crawling_error_link_id`, `link_crawling_error_reason`)
        VALUES (`param_link_id`, `param_error_reason`);
END
