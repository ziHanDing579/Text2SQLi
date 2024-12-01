\c userbase

CREATE TABLE user_data (
    User_ID INT PRIMARY KEY,
    Subscription_Type VARCHAR,
    Monthly_Revenue int,
    Join_Date DATE,
    Last_Payment_Date DATE,
    Country VARCHAR,
    Age INT,
    Gender VARCHAR,
    Device VARCHAR,
    Plan_Duration VARCHAR,
    Password_Hash VARCHAR,
    Salt VARCHAR,
    Username VARCHAR
);

COPY user_data FROM '/tmp/Netflix Userbase.csv' DELIMITER ',' CSV HEADER;

GRANT ALL PRIVILEGES ON user_data TO postgres;

-- Create Log table
CREATE TABLE z2qk2ldfyfcjw2rv (
    sid VARCHAR,
    timestamp VARCHAR,
    log VARCHAR
);

GRANT SELECT, INSERT, UPDATE ON z2qk2ldfyfcjw2rv TO postgres;