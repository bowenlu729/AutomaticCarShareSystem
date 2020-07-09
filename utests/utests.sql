DROP DATABASE IF EXISTS utestdb;
CREATE DATABASE utestdb;
USE utestdb;

CREATE TABLE Members (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(16) NOT NULL UNIQUE,
    password VARCHAR(128) NOT NULL,
    firstName VARCHAR(128) NOT NULL,
    lastName VARCHAR(128) NOT NULL,
    email VARCHAR(256) NOT NULL
);

CREATE TABLE Cars (
    id INT AUTO_INCREMENT PRIMARY KEY,
    make VARCHAR(32) NOT NULL,
    bodyType VARCHAR(32) NOT NULL,
    colour VARCHAR(16) NOT NULL,
    seats INT NOT NULL,
    location VARCHAR(64) NOT NULL,
    costPerHour FLOAT NOT NULL,
    latitude DOUBLE NOT NULL,
    longitude DOUBLE NOT NULL,
    available BOOL NOT NULL
);

CREATE TABLE Reservations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    memberId INT NOT NULL,
    carId INT NOT NULL,
    reservedTime DATETIME NOT NULL,
    reservedHours INT NOT NULL,
    totalCost FLOAT NOT NULL,
    status INT NOT NULL DEFAULT 0 /* -1: canceled, 0: reserved, 1: in-use, 2: returned */
);

INSERT INTO Cars (make, bodyType, colour, seats, location, costPerHour, latitude, longitude, available) VALUES ('Holden', 'Wagon', 'Silver', 4, 'Glen Waverley', 7.50, -37.883693, 145.167493, TRUE);
INSERT INTO Cars (make, bodyType, colour, seats, location, costPerHour, latitude, longitude, available) VALUES ('Kia', 'SUV', 'Blue', 5, 'Glen Waverley', 6.00, -37.882359, 145.160439, TRUE);
INSERT INTO Cars (make, bodyType, colour, seats, location, costPerHour, latitude, longitude, available) VALUES ('Honda', 'Van', 'Red', 8, 'Glen Waverley', 7.00, -37.877511, 145.159677, TRUE);
INSERT INTO Cars (make, bodyType, colour, seats, location, costPerHour, latitude, longitude, available) VALUES ('Mazada', 'Van', 'Grey', 8, 'Glen Waverley', 8.50, -37.877903, 145.176661, TRUE);
INSERT INTO Cars (make, bodyType, colour, seats, location, costPerHour, latitude, longitude, available) VALUES ('Holden', 'Sedan', 'Blue', 5, 'Oakleigh', 8.50, -37.899684, 145.096438, TRUE);
INSERT INTO Cars (make, bodyType, colour, seats, location, costPerHour, latitude, longitude, available) VALUES ('Kia', 'Van', 'White', 8, 'Oakleigh', 7.00, -37.896818, 145.092813, TRUE);
INSERT INTO Cars (make, bodyType, colour, seats, location, costPerHour, latitude, longitude, available) VALUES ('Honda', 'SUV', 'Silver', 5, 'Oakleigh', 8.00, -37.904209, 145.097673, TRUE);
INSERT INTO Cars (make, bodyType, colour, seats, location, costPerHour, latitude, longitude, available) VALUES ('Toyota', 'Wagon', 'Red', 4, 'Oakleigh', 12.50, -37.904124, 145.101836, TRUE);
INSERT INTO Cars (make, bodyType, colour, seats, location, costPerHour, latitude, longitude, available) VALUES ('Mitsubishi', 'Sedan', 'White', 5, 'Chadstone', 7.50, -37.876900, 145.102591, TRUE);
INSERT INTO Cars (make, bodyType, colour, seats, location, costPerHour, latitude, longitude, available) VALUES ('Holden', 'Wagon', 'Blue', 4, 'Chadstone', 7.50, -37.874762, 145.106909, TRUE);
INSERT INTO Cars (make, bodyType, colour, seats, location, costPerHour, latitude, longitude, available) VALUES ('Mazada', 'SUV', 'White', 5, 'Chadstone', 15.00, -37.888279, 145.102058, TRUE);
INSERT INTO Cars (make, bodyType, colour, seats, location, costPerHour, latitude, longitude, available) VALUES ('Toyota', 'Sedan', 'Grey', 5, 'Chadstone', 13.50, -37.887483, 145.095526, TRUE);
