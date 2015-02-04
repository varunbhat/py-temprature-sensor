SQL_QUERIES = {
    'PUT_MIN_COUNT':            """INSERT INTO `temp_min`  (`temp`) VALUES (%s)""",
    'PUT_HOURLY_COUNT':         """INSERT INTO `temp_hour` (`temp_min`,`temp_max`,`temp_avg`) VALUES(%s,%s,%s)""",
    'PUT_DAILY_COUNT':          """INSERT INTO `temp_day`  (`temp_min`,`temp_max`,`temp_avg`) VALUES(%s,%s,%s)""",

    'CONSOLIDATE_RAW_COUNT':    """SELECT MAX(`temp`), SUM(`temp`)/COUNT(`temp`), MIN(`temp`) FROM `temp_min` where `timestamp` > (CURRENT_TIMESTAMP - INTERVAL 1 HOUR)""",
    'CONSOLIDATE_HOURLY_COUNT': """SELECT MAX(`temp_max`), SUM(`temp_avg`)/COUNT(`temp_avg`),MIN(`temp_min`)  FROM `temp_hour` where `timestamp` > (CURRENT_TIMESTAMP - INTERVAL 1 DAY)""",

    'PURGE_RAW_COUNT':          """DELETE FROM `temp_min` WHERE `timestamp` >= (CURRENT_TIMESTAMP - INTERVAL 1 DAY)""",
}