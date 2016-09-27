Stored Procedures
*****************
There are stored procedures available in the database that preform useful and
common queries. Below is a list of the current stored procedures defined for
this application.

.. highlight:: py

================== ======================================== ============ =============================================================
procedure Name     Parameters                               Required     returns
================== ======================================== ============ =============================================================
extract_game_info  int seasonId, str position, int playerId No, No, No   int playerId, int locationId, int turfId, int opp
------------------ ---------------------------------------- ------------ -------------------------------------------------------------
extract_statistics str position, int seasonId, Bool byeFlag Yes, Yes, No int playerId, int year, int week, str statName, int statValue
================== ======================================== ============ =============================================================
