CREATE FUNCTION IF NOT EXISTS `sng_fn__register_active_crawler`
(
    `param_instance_name` VARCHAR(64),
    `param_program_name` VARCHAR(32),
    `param_program_version` VARCHAR(32)
)
RETURNS BIGINT UNSIGNED
NOT DETERMINISTIC SQL SECURITY INVOKER
BEGIN
    IF `param_instance_name` IS NULL OR `param_program_name` IS NULL OR `param_program_version` IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'The input parameters of this procedure/function must not be NULL!';
    END IF;

    INSERT INTO `active_crawlers` (`active_crawler_instance_name`, `active_crawler_program_name`, `active_crawler_program_version`)
        VALUES (`param_instance_name`, `param_program_name`, `param_program_version`);
    RETURN LAST_INSERT_ID();
END
