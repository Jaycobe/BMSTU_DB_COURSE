create function updateteamrating(arg_team_id integer) returns void
    language plpgsql
as
$$
begin
    update teams
    set rating = (select sum(rating)
                  from ratings
                           join t_p_list on ratings.id = t_p_list.part_id
                  where t_p_list.team_id = arg_team_id)
    where id = arg_team_id;
end;
$$;

create function updateteamparticipantsrating(arg_team_id integer, rating_change integer) returns void
    language plpgsql
as
$$
begin
    update ratings
    set rating = rating + rating_change
    where id = (select id from t_p_list where team_id = arg_team_id);
end
$$;


create function update_team_n_members(arg_team_id integer) returns void
    language plpgsql as
$$
BEGIN
    update teams
    set n_members = (select count(*) from t_p_list where t_p_list.team_id = arg_team_id)
    where id = arg_team_id;
END
$$;


create function update_all_teams_data()
    returns void
    language plpgsql as
$$
begin
    perform update_team_n_members(teams.id) from teams;
    perform teams.id, updateteamrating(teams.id) from teams;
end
$$;

create or replace function updateRating()
    returns trigger as
$$
begin
    call updateTeamParticipantsRating(new.id_first, 3);
    call updateTeamParticipantsRating(new.id_second, 2);
    call updateTeamParticipantsRating(new.id_third, 1);

    call updateTeamRating(new.id_first);
    call updateTeamRating(new.id_second);
    call updateTeamRating(new.id_third);

end
$$
    language plpgsql;

create function update_team_data(arg_team_id integer) returns void
    language plpgsql as
$$
begin
    perform update_team_n_members(arg_team_id);
    perform updateteamrating(arg_team_id);

end
$$;

create trigger updateRatingTrigger
    after update of id_first, id_second, id_third
    on hackathons
    for each row
execute function updateRating();

