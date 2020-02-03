 CREATE TABLE IF NOT EXISTS entity (
	entity_id INT AUTO_INCREMENT NOT NULL UNIQUE,
    entity_type ENUM('route', 'object', 'place', 'public_place', 'historical_person') NOT NULL,
    PRIMARY KEY (entity_id)
 );
 
 CREATE TABLE IF NOT EXISTS category (
	category_id INT AUTO_INCREMENT NOT NULL UNIQUE,
    category_name VARCHAR(30) NOT NULL UNIQUE,
    PRIMARY KEY (category_id)
);
    
CREATE TABLE IF NOT EXISTS city (
	city_id INT AUTO_INCREMENT NOT NULL UNIQUE,
    city_name VARCHAR(30) NOT NULL UNIQUE,
    city_image_link VARCHAR(250) NOT NULL,
    city_description TEXT  NOT NULL,
    PRIMARY KEY (city_id)
);
    
CREATE TABLE IF NOT EXISTS object (
	object_id INT NOT NULL UNIQUE REFERENCES entity(entity_id),
    object_type ENUM('place', 'public_place', 'historical_person') NOT NULL,
    object_city_id INT NOT NULL REFERENCES city(city_id),
    object_image_link VARCHAR(250) NOT NULL,
    object_audioguide_link VARCHAR(250),
    object_description TEXT NOT NULL,
    PRIMARY KEY (object_id)
);
    
CREATE TABLE IF NOT EXISTS category_object (
	object_id INT NOT NULL REFERENCES object(object_id),
    category_id INT NOT NULL REFERENCES category(category_id),
    PRIMARY KEY (object_id, category_id)
);
    
CREATE TABLE IF NOT EXISTS geolocation (
	geolocation_id INT AUTO_INCREMENT NOT NULL UNIQUE,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    PRIMARY KEY (geolocation_id)
);
    
CREATE TABLE IF NOT EXISTS place (
	object_id INT NOT NULL UNIQUE REFERENCES object(object_id),
    place_name VARCHAR(100) NOT NULL,
    place_address VARCHAR(200) NOT NULL DEFAULT '',
    place_geolocation_id INT NOT NULL REFERENCES geolocation(geolocation_id),
    PRIMARY KEY (object_id)
);
    
CREATE TABLE IF NOT EXISTS public_place (
	object_id INT NOT NULL UNIQUE REFERENCES object(object_id),
    PRIMARY KEY (object_id)
);
    
CREATE TABLE IF NOT EXISTS timetable (
	public_place_id INT NOT NULL REFERENCES public_place(object_id),
    week_day ENUM('mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun') NOT NULL,
    open_time TIME NOT NULL,
    close_time TIME NOT NULL,
    PRIMARY KEY (public_place_id, week_day)
);
    
CREATE TABLE IF NOT EXISTS historical_person (
	object_id INT NOT NULL REFERENCES object(object_id),
    person_name VARCHAR(20) NOT NULL,
    person_second_name VARCHAR(30) NOT NULL,
    person_patronymic VARCHAR(30) NOT NULL DEFAULT '',
    person_birthdate DATE NOT NULL,
    person_deathdate DATE,
    PRIMARY KEY (object_id)
);
    
CREATE TABLE IF NOT EXISTS historical_person_related_objects (
	historical_person_id INT NOT NULL REFERENCES historical_person(object_id),
    object_id INT NOT NULL REFERENCES object(object_id),
    PRIMARY KEY (historical_person_id, object_id)
);

CREATE TABLE IF NOT EXISTS route (
	route_id INT NOT NULL UNIQUE REFERENCES entity(entity_id),
    route_name VARCHAR(100) NOT NULL,
    route_description TEXT NOT NULL,
    PRIMARY KEY (route_id)
);

CREATE TABLE IF NOT EXISTS route_place_info (
	route_id INT NOT NULL REFERENCES route(route_id),
    place_id INT NOT NULL REFERENCES place(object_id),
    route_place_order INT NOT NULL,
    route_place_description TEXT,
    route_place_audioguide_link VARCHAR(250),
    PRIMARY KEY (route_id, place_id)
);

CREATE TABLE IF NOT EXISTS user (
	user_id INT NOT NULL UNIQUE AUTO_INCREMENT,
    user_name VARCHAR(100) NOT NULL UNIQUE,
    user_password VARCHAR(100) NOT NULL,
    user_email VARCHAR(200) NOT NULL UNIQUE,
    PRIMARY KEY (user_id)
);

CREATE TABLE IF NOT EXISTS review (
	user_id INT NOT NULL REFERENCES user(user_id),
    entity_id INT NOT NULL REFERENCES entity(entity_id),
    review_rating TINYINT NOT NULL,
    review_time DATETIME NOT NULL DEFAULT NOW(),
    review_text TEXT,
    PRIMARY KEY (user_id, entity_id)
);

CREATE TABLE IF NOT EXISTS role (
	role_id INT NOT NULL UNIQUE AUTO_INCREMENT,
    role_name VARCHAR(20) NOT NULL,
    PRIMARY KEY role(role_id)
);

CREATE TABLE IF NOT EXISTS user_role (
	user_id INT NOT NULL REFERENCES user(user_id),
    role_id INT NOT NULL REFERENCES role(role_id),
    PRIMARY KEY (user_id, role_id)
);

#PROCEDURES

DELIMITER //
DROP PROCEDURE IF EXISTS raise_error //

CREATE PROCEDURE raise_error(IN message VARCHAR(200))
BEGIN 
	SIGNAL sqlstate '45000' SET message_text = message;
END//

DELIMITER ;
