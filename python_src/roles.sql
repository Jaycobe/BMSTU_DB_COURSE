create user "admin" password 'admin';
create user "organizer" password 'organizer';
create user "captain" password 'captain';
create user "participant" password 'participant';

grant select on teams, hackathons to "participant";
grant insert on requests to "participant";

grant select on teams, hackathons to "captain";
grant insert on requests to "captain";
grant update, delete on CaptainTeamView to "captain";

grant select on teams, hackathons to "organizer";
grant insert on requests to "organizer";
grant update, delete on OrganizerHackathonView to "organizer";

alter role "admin" superuser;
