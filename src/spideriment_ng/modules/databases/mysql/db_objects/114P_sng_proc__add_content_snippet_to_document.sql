CREATE PROCEDURE IF NOT EXISTS `sng_proc__add_content_snippet_to_document`
(
    IN `param_document_id` BIGINT UNSIGNED,
    IN `param_snippet_type` ENUM(
        'heading_1',
        'heading_2',
        'heading_3',
        'heading_4',
        'heading_5',
        'emphasized_text',
        'regular_text',
        'list_item_text',
        'uncategorized_text',
        'fallback_text'
    ),
    IN `param_snippet_text` TEXT
)
NOT DETERMINISTIC SQL SECURITY INVOKER
BEGIN
    IF `param_document_id` IS NULL OR `param_snippet_type` IS NULL OR `param_snippet_text` IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'The input parameters of this procedure/function must not be NULL!';
    END IF;

    INSERT INTO `content_snippets` (`content_snippet_document_id`, `content_snippet_type`, `content_snippet_text`)
        VALUES (`param_document_id`, `param_snippet_type`, `param_snippet_text`);
END
