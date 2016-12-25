drop table if exists users;
create table users (
  id integer primary key autoincrement,
  username text not null,
  password_hash text not null
);

drop table if exists entries;
create table entries (
    id integer primary key autoincrement,
    userid integer,
    title text not null,
    entry text not null
);
