drop table t_p_list, users, hackathons, teams, h_t_list, ratings cascade;

create table if not exists Roles
(
    id serial primary key,
    description text unique
);

create table if not exists Request_Types
(
    id serial primary key,
    description text unique
);


create table if not exists Statuses
(
  id serial primary key,
  description text unique
);

create table if not exists Users
(
  id serial primary key,
  name text,
  login text,
  password text,
  role int,
  foreign key (role) references Roles(id),
  unique (login)
);

create table if not exists Teams
(
    id serial primary key,
    name text,
    n_members int,
    rating float,
    cap_id int,
    foreign key (cap_id) references Users(id)
);


create table if not exists T_P_List
(
    team_id int not null,
    part_id int not null,
    foreign key (team_id) references Teams(id) on delete cascade,
    foreign key (part_id) references Users(id)
);

create table if not exists Hackathons
(
    id serial primary key,
    name text,
    address text,
    date date,
    theme text,
    duration float,
    org_id int,
    id_first int references Teams(id),
    id_second int references Teams(id),
    id_third int references Teams(id),
    foreign key (org_id) references Users(id)
);


create table if not exists h_t_list
(
    hack_id int not null,
    team_id int not null,
    foreign key (team_id) references Teams(id),
    foreign key (hack_id) references Hackathons(id)
);

create table if not exists Requests
(
    id serial primary key,
    type int,
    requester_id int,
    requester_role int,
    status int,
    target_team_id int references Teams(id),
    target_hackathon_id int references Hackathons(id),
    name text,
    adm_id int references Users(id),
    comment text,
    adm_comment text,
    foreign key (type) references Request_Types(id),
    foreign key (requester_id) references Users(id),
    foreign key (requester_role) references Roles(id),
    foreign key (status) references Statuses(id)
);

create table if not exists Ratings
(
  id int not null,
  rating int,
  foreign key (id) references Users(id)
);

insert into users values (default, 'SuperAdmin', 'admin', 'admin', 1);
insert into users values (default, 'Test Organizer', 'organizer', 'organizer', 2);
insert into users values (default, 'Test Captain', 'captain', 'captain', 3);
insert into users values (default, 'Test Participant 1', 'participant1', 'participant1', 4);
insert into users values (default, 'Test Participant 2', 'participant2', 'participant2', 4);
insert into users values (default, 'Test Participant 3', 'participant3', 'participant3', 4);
insert into users values (default, 'Test Participant 4', 'participant4', 'participant4', 4);
insert into users values (default, 'Test Participant 5', 'participant5', 'participant5', 4);
insert into ratings values(1108, 8);
insert into ratings values(1109, 3);
insert into ratings values(1110, 0);
insert into ratings values(1111, 0);
insert into ratings values(1112, 0);
insert into ratings values(1113, 0);

select 'drop table if exists "' || tablename || '" cascade;'
  from pg_tables
 where schemaname = 'public'; -- or any other schema



