USE `NFLStats1`;
DROP procedure IF EXISTS `extract_game_info`;

DELIMITER $$
USE `NFLStats1`$$
CREATE DEFINER=`derrick`@`%` PROCEDURE `extract_game_info`(In seasonId int,
                                  In position varchar(3),
                                  In byeFlag Bool)
BEGIN


  select p.playerId, l.locationId as location, tf.turfId as turf, tm.teamNumber as opp
  from   Players p, TeamLocations l, TurfTypes tf, Teams tm, PlayerTeam pt, Games g
  where  p.playerId = pt.playerId and pt.teamId = g.homeTeam and tm.teamId = g.awayTeam
        and l.teamId = g.homeTeam and tf.turf = l.turf
        and g.seasonId = seasonId and p.position = position
  Union

  select p.playerId, l.locationId as location, tf.turfId as turf, tm.teamNumber as opp
  from   Players p, TeamLocations l, TurfTypes tf, Teams tm, PlayerTeam pt, Games g
  where  p.playerId = pt.playerId and pt.teamId = g.awayTeam and tm.teamId = g.homeTeam
         and l.teamId = g.awayTeam and tf.turf = l.turf
         and g.seasonId = seasonId and p.position = position

  Union

    select p.playerId, 0 as location, 0 as turf, 0 as opp
    from   Players p, PlayerTeam t, ByeWeeks b
    where  p.playerId = t.playerId and t.teamId = b.teamId
           and p.position = position and b.seasonId = seasonId
           and byeFlag = True;
END$$

DELIMITER ;


USE `NFLStats1`;
DROP procedure IF EXISTS `extract_statistics`;
DELIMITER $$
USE `NFLStats1`$$
CREATE DEFINER=`derrick`@`%` PROCEDURE `extract_statistics`(
                                        In position varchar(3),
                                        In seasonId int(10),
                                        In playerId int(10))
BEGIN
  if (seasonId is NULL) Then
    if (playerId is NULL) then
      select p.playerId, se.seasonYear, se.week, st.stat_name, s.statValue
        from Players p, Season se, PlayerStats s, Statistics st
        where p.playerId = s.playerId and p.position = position
            and s.seasonId = se.seasonId and s.statId = st.statId
        order by p.playerId;
    else
      select p.playerId, se.seasonYear, se.week, st.stat_name, s.statValue
        from Players p, Season se, PlayerStats s, Statistics st
        where p.playerId = s.playerId and p.position = position
            and s.seasonId = se.seasonId and p.playerId = playerId
                      and s.statId = st.statId
        order by p.playerId;
    end if;
    else
    if (playerId is NULL) then
      select p.playerId, se.seasonYear, se.week, st.stat_name, s.statValue
        from Players p, Season se, PlayerStats s, Statistics st
        where p.playerId = s.playerId and p.position = position
            and s.seasonId = se.seasonId and s.seasonId = seasonId
                      and s.statId = st.statId
        order by p.playerId;
    else
      select p.playerId, se.seasonYear, se.week, st.stat_name, s.statValue
        from Players p, Season se, PlayerStats s, Statistics st
        where p.playerId = s.playerId and p.position = position
            and s.seasonId = se.seasonId and s.seasonId = seasonId
                      and p.playerId = playerId and s.statId = st.statId
        order by p.playerId;
    end if;
  end if;
END$$

DELIMITER ;

