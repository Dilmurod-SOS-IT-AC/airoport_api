INSERT INTO airports (code, name, city, country) VALUES
    ('TAS', 'Tashkent International Airport', 'Tashkent', 'Uzbekistan'),
    ('NBO', 'Jomo Kenyatta International Airport', 'Nairobi', 'Kenya'),
    ('JFK', 'John F. Kennedy International Airport', 'New York', 'USA'),
    ('LHR', 'Heathrow Airport', 'London', 'UK'),
    ('CDG', 'Charles de Gaulle Airport', 'Paris', 'France');

INSERT INTO flights (flight_number, origin_id, destination_id, daparture_time, base_price, total_sests) VALUES
    ("HY101", (SELECT id FROM airports WHERE code = 'TAS'), (SELECT id FROM airports WHERE code = 'NBO'), '2024-07-01 08:00:00', 500, 150),
    ("HY102", (SELECT id FROM airports WHERE code = 'NBO'), (SELECT id FROM airports WHERE code = 'JFK'), '2024-07-02 10:00:00', 700, 200),
    ("HY103", (SELECT id FROM airports WHERE code = 'JFK'), (SELECT id FROM airports WHERE code = 'LHR'), '2024-07-03 12:00:00', 800, 250),
    ("HY104", (SELECT id FROM airports WHERE code = 'LHR'), (SELECT id FROM airports WHERE code = 'CDG'), '2024-07-04 14:00:00', 600, 180),
    ("HY105", (SELECT id FROM airports WHERE code = 'CDG'), (SELECT id FROM airports WHERE code = 'TAS'), '2024-07-05 16:00:00', 900, 220);