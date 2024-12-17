CREATE TABLE IF NOT EXISTS gen.calls 
(
	id VARCHAR PRIMARY KEY,
	start_time VARCHAR,
	end_time VARCHAR,
	originating_direction VARCHAR,
	dl_imported_at TIMESTAMP WITHOUT TIME ZONE
);

CREATE TABLE IF NOT EXISTS gen.participants 
(
	conversation_id VARCHAR,
	id VARCHAR,
	name VARCHAR,
	purpose VARCHAR,
	team_id VARCHAR,
	user_id VARCHAR,
	session_id VARCHAR,
	session_ani VARCHAR,
	session_dnis VARCHAR,
	talk_time NUMERIC(12,1),
	dl_imported_at TIMESTAMP WITHOUT TIME ZONE,
	PRIMARY KEY(conversation_id, id)
);

CREATE TABLE IF NOT EXISTS gen.segments 
(	
	id BIGSERIAL PRIMARY KEY,
	conversation_id VARCHAR,
	type VARCHAR,
	start_time VARCHAR,
	end_time VARCHAR,
	session_id VARCHAR,
	dl_imported_at TIMESTAMP WITHOUT TIME ZONE
);

CREATE TABLE IF NOT EXISTS gen.users 
(	
	id VARCHAR PRIMARY KEY,
	name VARCHAR,
	email VARCHAR,
	phone_mobile VARCHAR,
	phone_work VARCHAR,
	dl_imported_at TIMESTAMP WITHOUT TIME ZONE
);

CREATE TABLE IF NOT EXISTS gen.contacts 
(	
	id VARCHAR PRIMARY KEY,
	first_name VARCHAR,
	last_name VARCHAR,
	email_work VARCHAR,
	email_private VARCHAR,
	phone_work VARCHAR,
	phone_mobile VARCHAR,
	dl_imported_at TIMESTAMP WITHOUT TIME ZONE
);



CREATE TABLE IF NOT EXISTS gen_stg.calls 
(
	id VARCHAR PRIMARY KEY,
	start_time VARCHAR,
	end_time VARCHAR,
	originating_direction VARCHAR,
	dl_imported_at TIMESTAMP WITHOUT TIME ZONE
);

CREATE TABLE IF NOT EXISTS gen_stg.participants 
(
	conversation_id VARCHAR,
	id VARCHAR,
	name VARCHAR,
	purpose VARCHAR,
	team_id VARCHAR,
	user_id VARCHAR,
	session_id VARCHAR,
	session_ani VARCHAR,
	session_dnis VARCHAR,
	talk_time NUMERIC(12,1),
	dl_imported_at TIMESTAMP WITHOUT TIME ZONE,
	PRIMARY KEY(conversation_id, id)
);

CREATE TABLE IF NOT EXISTS gen_stg.segments 
(	
	id BIGSERIAL PRIMARY KEY,
	conversation_id VARCHAR,
	type VARCHAR,
	start_time VARCHAR,
	end_time VARCHAR,
	session_id VARCHAR,
	dl_imported_at TIMESTAMP WITHOUT TIME ZONE
);

CREATE TABLE IF NOT EXISTS gen_stg.users 
(	
	id VARCHAR PRIMARY KEY,
	name VARCHAR,
	email VARCHAR,
	phone_mobile VARCHAR,
	phone_work VARCHAR,
	dl_imported_at TIMESTAMP WITHOUT TIME ZONE
);

CREATE TABLE IF NOT EXISTS gen_stg.contacts 
(	
	id VARCHAR PRIMARY KEY,
	first_name VARCHAR,
	last_name VARCHAR,
	email_work VARCHAR,
	email_private VARCHAR,
	phone_work VARCHAR,
	phone_mobile VARCHAR,
	dl_imported_at TIMESTAMP WITHOUT TIME ZONE
);

ALTER TABLE gen.calls
ADD CONSTRAINT gen_calls_constraint UNIQUE (id);

ALTER TABLE gen.participants
ADD CONSTRAINT gen_participants_constraint UNIQUE (conversation_id, id);

ALTER TABLE gen.segments
ADD CONSTRAINT gen_segments_constraint UNIQUE (conversation_id, type, start_time, end_time, session_id);

ALTER TABLE gen.users
ADD CONSTRAINT gen_users_constraint UNIQUE (id);

ALTER TABLE gen.contacts
ADD CONSTRAINT gen_contacts_constraint UNIQUE (id);

ALTER TABLE gen_stg.calls
ADD CONSTRAINT gen_stg_calls_constraint UNIQUE (id);

ALTER TABLE gen_stg.participants
ADD CONSTRAINT gen_stg_participants_constraint UNIQUE (conversation_id, id);

ALTER TABLE gen_stg.segments
ADD CONSTRAINT gen_stg_segments_constraint UNIQUE (conversation_id, type, start_time, end_time, session_id);

ALTER TABLE gen_stg.users
ADD CONSTRAINT gen_stg_users_constraint UNIQUE (id);

ALTER TABLE gen_stg.contacts
ADD CONSTRAINT gen_stg_contacts_constraint UNIQUE (id);