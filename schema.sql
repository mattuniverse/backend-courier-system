-- =====================================================================
-- Courier & Parcel Management System - PostgreSQL Schema
-- =====================================================================

-- ---------------------------------------------------------------------
-- Users (staff / admin who log into the system)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'staff' CHECK (role IN ('admin','staff','cashier')),
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active','inactive')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ---------------------------------------------------------------------
-- Branches / Hubs
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS branches (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL,
    address VARCHAR(255),
    phone VARCHAR(30),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ---------------------------------------------------------------------
-- Customers (senders)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(30) NOT NULL,
    email VARCHAR(100),
    address VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ---------------------------------------------------------------------
-- Couriers (delivery riders/drivers)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS couriers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(30) NOT NULL,
    email VARCHAR(100),
    vehicle_no VARCHAR(50),
    branch_id INT REFERENCES branches(id) ON DELETE SET NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'available' CHECK (status IN ('available','busy','off_duty')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ---------------------------------------------------------------------
-- Parcels / Shipments
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS parcels (
    id SERIAL PRIMARY KEY,
    tracking_no VARCHAR(30) NOT NULL UNIQUE,
    sender_id INT NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    receiver_name VARCHAR(100) NOT NULL,
    receiver_phone VARCHAR(30) NOT NULL,
    receiver_address VARCHAR(255) NOT NULL,
    pickup_branch_id INT REFERENCES branches(id) ON DELETE SET NULL,
    delivery_branch_id INT REFERENCES branches(id) ON DELETE SET NULL,
    courier_id INT REFERENCES couriers(id) ON DELETE SET NULL,
    parcel_type VARCHAR(20) NOT NULL DEFAULT 'box' CHECK (parcel_type IN ('document','box','fragile','electronics','other')),
    weight_kg DECIMAL(6,2) NOT NULL DEFAULT 1.00,
    cost DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    payment_status VARCHAR(20) NOT NULL DEFAULT 'unpaid' CHECK (payment_status IN ('unpaid','paid')),
    status VARCHAR(30) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending','picked_up','in_transit','out_for_delivery','delivered','cancelled','returned')),
    booking_date DATE NOT NULL,
    expected_delivery_date DATE,
    delivered_at TIMESTAMP NULL,
    created_by INT REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ---------------------------------------------------------------------
-- Parcel tracking history (status trail)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS parcel_tracking (
    id SERIAL PRIMARY KEY,
    parcel_id INT NOT NULL REFERENCES parcels(id) ON DELETE CASCADE,
    status VARCHAR(30) NOT NULL,
    location VARCHAR(150),
    remarks VARCHAR(255),
    updated_by INT REFERENCES users(id) ON DELETE SET NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================================
-- Seed data
-- =====================================================================
INSERT INTO users (username, password, full_name, role) VALUES
  ('admin', '$2y$12$LJ3m4yHzNPG1VHdBPDxQTuMNOZ9C1gQXQ3JtOiFxVlGhNjKxHhKe', 'Administrator', 'admin'),
  ('cashier', '$2y$12$LJ3m4yHzNPG1VHdBPDxQTuMNOZ9C1gQXQ3JtOiFxVlGhNjKxHhKe', 'Cashier User', 'cashier')
ON CONFLICT DO NOTHING;

INSERT INTO branches (name, city, address, phone) VALUES
  ('Main Hub', 'Manila', '123 Rizal Ave', '09171234567'),
  ('Cebu Hub', 'Cebu City', '456 Osmeña Blvd', '09321234567'),
  ('Davao Hub', 'Davao City', '789 Claro M. Recto', '09231234567')
ON CONFLICT DO NOTHING;

INSERT INTO couriers (name, phone, vehicle_no, branch_id) VALUES
  ('Juan Dela Cruz', '09171111111', 'ABC-1234', 1),
  ('Pedro Santos', '09222222222', 'DEF-5678', 2),
  ('Maria Reyes', '09333333333', 'GHI-9012', 3)
ON CONFLICT DO NOTHING;

INSERT INTO customers (name, phone, email, address) VALUES
  ('Ana Garcia', '09170000001', 'ana@example.com', '101 Bonifacio St, Manila'),
  ('Luis Mendoza', '09220000002', 'luis@example.com', '202 Aguinaldo Hwy, Cavite')
ON CONFLICT DO NOTHING;
