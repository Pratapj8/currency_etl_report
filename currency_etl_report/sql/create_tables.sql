CREATE DATABASE IF NOT EXISTS currency_rates;

USE currency_rates;

CREATE TABLE IF NOT EXISTS conversion_rates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    base_currency VARCHAR(10) NOT NULL,
    target_currency VARCHAR(10) NOT NULL,
    rate DECIMAL(20, 8) NOT NULL,
    date DATE NOT NULL,
    UNIQUE KEY unique_rate (base_currency, target_currency, date)
);

-- Optional indexes for performance
CREATE INDEX idx_base_target_date ON conversion_rates (base_currency, target_currency, date);




