-- Schema simplifié correspondant aux modèles Python
CREATE DATABASE IF NOT EXISTS vinted_bot DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE vinted_bot;

-- Utiliser directement la migration existante qui correspond aux modèles
SOURCE database/migrations/001_auth_billing.sql;

-- Ajouter les tables manquantes pour alerts et filters
CREATE TABLE IF NOT EXISTS vinted_filters (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  name VARCHAR(200) NOT NULL,
  category VARCHAR(100) NULL,
  brand VARCHAR(100) NULL,
  size VARCHAR(50) NULL,
  color VARCHAR(50) NULL,
  min_price DECIMAL(8,2) NULL,
  max_price DECIMAL(8,2) NULL,
  keywords VARCHAR(500) NULL,
  snipping_enabled BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS alerts (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  filter_id INT NOT NULL,
  vinted_item_id VARCHAR(100) NOT NULL,
  item_title VARCHAR(500) NULL,
  item_price DECIMAL(8,2) NULL,
  item_url VARCHAR(1000) NULL,
  action_taken ENUM('alert', 'sniped', 'failed') DEFAULT 'alert',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (filter_id) REFERENCES vinted_filters(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
