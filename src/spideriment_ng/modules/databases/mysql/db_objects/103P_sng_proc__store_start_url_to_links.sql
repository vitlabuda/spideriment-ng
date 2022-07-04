CREATE PROCEDURE IF NOT EXISTS `sng_proc__store_start_url_to_links`
(
    IN `param_start_url` VARCHAR(1024)
)
NOT DETERMINISTIC SQL SECURITY INVOKER
BEGIN
    IF `param_start_url` IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'The input parameters of this procedure/function must not be NULL!';
    END IF;

    IF NOT EXISTS(SELECT 1 FROM `links` WHERE `links`.`link_href_url` = `param_start_url` LIMIT 1) THEN
        INSERT INTO `links` (`link_href_url`) VALUES (`param_start_url`);
    END IF;
END
