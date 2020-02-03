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

DROP PROCEDURE IF EXISTS get_all_objects //

CREATE PROCEDURE get_all_objects()
BEGIN
	SELECT object_id, object_type, city_name, image_link, object_audioguide_link, object_description
    FROM object NATURAL JOIN city;
END//

# TRIGGERS

DROP TRIGGER IF EXISTS review_rating_range_check //

CREATE TRIGGER review_rating_range_check 
BEFORE INSERT ON review FOR EACH ROW
BEGIN 
	IF NEW.review_rating > 5 OR NEW.review_rating < 1 THEN
		CALL raise_error('Invalid review rating value');
	END IF;
END//

DROP TRIGGER IF EXISTS historical_person_death_date_check //

CREATE TRIGGER historical_person_death_date_check 
BEFORE INSERT ON historical_person FOR EACH ROW
BEGIN 
	IF NOT ISNULL(NEW.person_deathdate) AND NEW.person_deathdate < NEW.person_birthdate THEN
		CALL raise_error('Invalid death date.');
	END IF;
END //

DROP TRIGGER IF EXISTS historical_person_objects_list_check //

CREATE TRIGGER historical_person_objects_list_check
BEFORE INSERT ON historical_person_related_objects FOR EACH ROW
BEGIN
	IF EXISTS (
		SELECT object_id 
        FROM object NATURAL JOIN entity
        WHERE object_id = NEW.object_id AND entity.entity_type = 'historical_person'
    ) THEN 
		CALL raise_error('You can\'t add another person in related with historical person list.');
	END IF;
END //

DROP TRIGGER IF EXISTS timetable_close_time_check //

CREATE TRIGGER timetable_close_time_check 
BEFORE INSERT ON timetable FOR EACH ROW
BEGIN
	IF NEW.close_time < NEW.open_time THEN
		CALL raise_error('Close time must be later than open time');
	END IF;
END //

DROP TRIGGER IF EXISTS route_object_info_order_check //

CREATE TRIGGER route_object_info_order_check 
BEFORE INSERT ON route_place_info FOR EACH ROW
BEGIN
	IF EXISTS (
		SELECT route_place_order
		FROM route_place_info
        WHERE place_id = NEW.place_id AND route_id = NEW.route_id AND route_place_order = NEW.route_place_order
    ) THEN 
		CALL raise_error('Place with this order number already exists');
	END IF;
END //

DROP TRIGGER IF EXISTS route_object_info_person_check //

CREATE TRIGGER route_object_info_person_check 
BEFORE INSERT ON route_place_info FOR EACH ROW
BEGIN 
	IF EXISTS (
		SELECT *
        FROM object NATURAL JOIN entity
        WHERE object_id = NEW.object_id AND entity.entity_id = 'historical_person'
	) THEN
		CALL raise_error('Objects with type historical_person can\t be added to route');
	END IF;
END //


DELIMITER ;
