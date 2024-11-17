\c admt_chatbot

CREATE TABLE pgh_weatherdata (
    STATION VARCHAR,
    NAME VARCHAR,
    DATE VARCHAR,
    ACMH INT,
    ACSH INT,
    AWND DOUBLE PRECISION,
    FMTM INT,
    PGTM INT,
    PRCP DOUBLE PRECISION,
    PSUN INT,
    SNOW DOUBLE PRECISION,
    SNWD DOUBLE PRECISION,
    TAVG INT,
    TMAX INT,
    TMIN INT,
    TSUN INT,
    WDF1 INT,
    WDF2 INT,
    WDF5 INT,
    WDFG INT,
    WESD DOUBLE PRECISION,
    WSF1 DOUBLE PRECISION,
    WSF2 DOUBLE PRECISION,
    WSF5 DOUBLE PRECISION,
    WSFG DOUBLE PRECISION,
    WT01 INT,
    WT02 INT,
    WT03 INT,
    WT04 INT,
    WT05 INT,
    WT06 INT,
    WT07 INT,
    WT08 INT,
    WT09 INT,
    WT11 INT,
    WT13 INT,
    WT14 INT,
    WT15 INT,
    WT16 INT,
    WT17 INT,
    WT18 INT,
    WT19 INT,
    WT21 INT,
    WT22 INT
);

COPY pgh_weatherdata FROM '/tmp/pgh_weatherdata.csv' DELIMITER ',' CSV HEADER;

GRANT SELECT ON pgh_weatherdata TO postgres;

-- Create Log table
CREATE TABLE z2qk2ldfyfcjw2rv (
    sid VARCHAR,
    timestamp VARCHAR,
    log VARCHAR
);

GRANT SELECT, INSERT, UPDATE ON z2qk2ldfyfcjw2rv TO postgres;


-- CREATE TABLE weatherdata (
    -- STATION VARCHAR,
    -- NAME VARCHAR,
    -- DATE VARCHAR,
    -- ACMH INT,
    -- ACSH INT,
    -- AWND DOUBLE PRECISION,
    -- FMTM INT,
    -- PGTM INT,
    -- PRCP DOUBLE PRECISION,
    -- PSUN INT,
    -- SNOW DOUBLE PRECISION,
    -- SNWD DOUBLE PRECISION,
    -- TAVG INT,
    -- TMAX INT,
    -- TMIN INT,
    -- TSUN INT,
    -- WDF1 INT,
    -- WDF2 INT,
    -- WDF5 INT,
    -- WDFG INT,
    -- WESD DOUBLE PRECISION,
    -- WSF1 DOUBLE PRECISION,
    -- WSF2 DOUBLE PRECISION,
    -- WSF5 DOUBLE PRECISION,
    -- WSFG DOUBLE PRECISION,
    -- WT01 INT,
    -- WT02 INT,
    -- WT03 INT,
    -- WT04 INT,
    -- WT05 INT,
    -- WT06 INT,
    -- WT07 INT,
    -- WT08 INT,
    -- WT09 INT,
    -- WT11 INT,
    -- WT13 INT,
    -- WT14 INT,
    -- WT15 INT,
    -- WT16 INT,
    -- WT17 INT,
    -- WT18 INT,
    -- WT19 INT,
    -- WT21 INT,
    -- WT22 INT
-- );

-- COPY weatherdata FROM '/tmp/weatherdata.csv' DELIMITER ',' CSV HEADER;
-- GRANT SELECT ON weatherdata TO postgres;