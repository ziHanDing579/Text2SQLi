\c userbase

CREATE TABLE user_data (
    User ID INT PRIMARY KEY,
    Subscription Type VARCHAR,
    Monthly Revenue int,
    Join Date DATE,
    Last Payment Date DATE,
    Country VARCHAR,
    Age INT,
    Gender VARCHAR,
    Device VARCHAR,
    Plan Duration VARCHAR,
    Password VARCHAR,
    Salt VARCHAR,
    Username VARCHAR
);

COPY user_data FROM '/tmp/Netflix Userbase.csv' DELIMITER ',' CSV HEADER;

GRANT ALL PRIVILEGES ON pgh_weatherdata TO postgres;

-- Create Log table
CREATE TABLE z2qk2ldfyfcjw2rv (
    sid VARCHAR,
    timestamp VARCHAR,
    log VARCHAR
);

GRANT SELECT, INSERT, UPDATE ON z2qk2ldfyfcjw2rv TO postgres;