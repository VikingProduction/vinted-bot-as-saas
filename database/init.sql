-- Schéma de base de données pour le bot Vinted SAAS
-- MySQL 8.0

SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;
SET time_zone = '+00:00';
SET foreign_key_checks = 0;
SET sql_mode = 'NO_AUTO_VALUE_ON_ZERO';

-- Base de données
CREATE DATABASE IF NOT EXISTS `vinted_bot` 
DEFAULT CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE `vinted_bot`;

-- Table des utilisateurs
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `email` varchar(255) NOT NULL,
  `username` varchar(100) NOT NULL,
  `hashed_password` varchar(255) NOT NULL,
  `first_name` varchar(100) DEFAULT NULL,
  `last_name` varchar(100) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT '1',
  `is_verified` tinyint(1) DEFAULT '0',
  `subscription_plan` enum('gratuit','starter','pro','business') DEFAULT 'gratuit',
  `subscription_status` enum('active','canceled','past_due','trialing') DEFAULT 'active',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `last_login` timestamp NULL DEFAULT NULL,
  `email_verified_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `username` (`username`),
  KEY `subscription_plan` (`subscription_plan`),
  KEY `is_active` (`is_active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table des filtres Vinted
CREATE TABLE `vinted_filters` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `name` varchar(200) NOT NULL,
  `description` text,
  `is_active` tinyint(1) DEFAULT '1',
  
  -- Filtres de recherche
  `category` varchar(100) DEFAULT NULL,
  `brand` varchar(100) DEFAULT NULL,
  `size` varchar(50) DEFAULT NULL,
  `color` varchar(50) DEFAULT NULL,
  `material` varchar(50) DEFAULT NULL,
  `condition` varchar(100) DEFAULT NULL,
  `min_price` decimal(8,2) DEFAULT NULL,
  `max_price` decimal(8,2) DEFAULT NULL,
  `keywords` text,
  
  -- Configuration snipping
  `snipping_enabled` tinyint(1) DEFAULT '0',
  `max_snipping_price` decimal(8,2) DEFAULT NULL,
  `auto_buy` tinyint(1) DEFAULT '0',
  
  -- Configuration alertes
  `email_alerts` tinyint(1) DEFAULT '1',
  `push_alerts` tinyint(1) DEFAULT '0',
  `webhook_url` varchar(500) DEFAULT NULL,
  
  -- Métadonnées
  `last_check` timestamp NULL DEFAULT NULL,
  `check_frequency` int DEFAULT '300', -- en secondes
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `is_active` (`is_active`),
  KEY `last_check` (`last_check`),
  CONSTRAINT `fk_filters_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table des alertes
CREATE TABLE `alerts` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `filter_id` int NOT NULL,
  `vinted_item_id` varchar(100) NOT NULL,
  
  -- Données de l'article
  `item_title` varchar(500) DEFAULT NULL,
  `item_price` decimal(8,2) DEFAULT NULL,
  `item_currency` varchar(3) DEFAULT 'EUR',
  `item_url` varchar(1000) DEFAULT NULL,
  `item_image_url` varchar(1000) DEFAULT NULL,
  `item_brand` varchar(100) DEFAULT NULL,
  `item_size` varchar(50) DEFAULT NULL,
  `item_condition` varchar(100) DEFAULT NULL,
  `item_user_id` varchar(100) DEFAULT NULL,
  `item_username` varchar(100) DEFAULT NULL,
  
  -- Actions prises
  `action_taken` enum('alert','sniped','failed','skipped') DEFAULT 'alert',
  `snipping_attempted` tinyint(1) DEFAULT '0',
  `snipping_success` tinyint(1) DEFAULT '0',
  `snipping_error` text,
  
  -- Status notifications
  `email_sent` tinyint(1) DEFAULT '0',
  `push_sent` tinyint(1) DEFAULT '0',
  `webhook_sent` tinyint(1) DEFAULT '0',
  
  -- Timestamps
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `processed_at` timestamp NULL DEFAULT NULL,
  
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_item_filter` (`filter_id`, `vinted_item_id`),
  KEY `user_id` (`user_id`),
  KEY `vinted_item_id` (`vinted_item_id`),
  KEY `action_taken` (`action_taken`),
  KEY `created_at` (`created_at`),
  CONSTRAINT `fk_alerts_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_alerts_filter_id` FOREIGN KEY (`filter_id`) REFERENCES `vinted_filters` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table des abonnements Stripe
CREATE TABLE `subscriptions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `stripe_subscription_id` varchar(255) DEFAULT NULL,
  `stripe_customer_id` varchar(255) DEFAULT NULL,
  `stripe_price_id` varchar(255) DEFAULT NULL,
  
  -- Détails abonnement
  `plan_name` enum('gratuit','starter','pro','business') NOT NULL,
  `status` enum('active','canceled','past_due','trialing','incomplete') NOT NULL,
  `billing_cycle` enum('monthly','yearly') DEFAULT 'monthly',
  
  -- Limites du plan
  `max_filters` int DEFAULT NULL,
  `max_alerts_per_day` int DEFAULT NULL,
  `snipping_enabled` tinyint(1) DEFAULT '0',
  `api_access_enabled` tinyint(1) DEFAULT '0',
  
  -- Dates importantes
  `current_period_start` timestamp NULL DEFAULT NULL,
  `current_period_end` timestamp NULL DEFAULT NULL,
  `trial_start` timestamp NULL DEFAULT NULL,
  `trial_end` timestamp NULL DEFAULT NULL,
  `canceled_at` timestamp NULL DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  PRIMARY KEY (`id`),
  UNIQUE KEY `stripe_subscription_id` (`stripe_subscription_id`),
  KEY `user_id` (`user_id`),
  KEY `status` (`status`),
  KEY `plan_name` (`plan_name`),
  CONSTRAINT `fk_subscriptions_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table des sessions utilisateur (JWT refresh tokens)
CREATE TABLE `user_sessions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `refresh_token` varchar(500) NOT NULL,
  `device_info` text,
  `ip_address` varchar(45) DEFAULT NULL,
  `user_agent` text,
  `is_active` tinyint(1) DEFAULT '1',
  `expires_at` timestamp NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `last_used` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  PRIMARY KEY (`id`),
  UNIQUE KEY `refresh_token` (`refresh_token`),
  KEY `user_id` (`user_id`),
  KEY `expires_at` (`expires_at`),
  KEY `is_active` (`is_active`),
  CONSTRAINT `fk_sessions_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table des statistiques quotidiennes
CREATE TABLE `daily_stats` (
  `id` int NOT NULL AUTO_INCREMENT,
  `date` date NOT NULL,
  `user_id` int DEFAULT NULL,
  
  -- Statistiques scraping
  `scraping_requests` int DEFAULT '0',
  `items_found` int DEFAULT '0',
  `alerts_sent` int DEFAULT '0',
  `snipping_attempts` int DEFAULT '0',
  `snipping_success` int DEFAULT '0',
  
  -- Statistiques utilisateur (si user_id NULL = stats globales)
  `active_filters` int DEFAULT '0',
  `new_users` int DEFAULT '0',
  `subscription_changes` int DEFAULT '0',
  
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_date_user` (`date`, `user_id`),
  KEY `date` (`date`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `fk_stats_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table des logs système
CREATE TABLE `system_logs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `level` enum('DEBUG','INFO','WARNING','ERROR','CRITICAL') NOT NULL,
  `component` varchar(100) NOT NULL,
  `message` text NOT NULL,
  `context` json DEFAULT NULL,
  `user_id` int DEFAULT NULL,
  `ip_address` varchar(45) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  
  PRIMARY KEY (`id`),
  KEY `level` (`level`),
  KEY `component` (`component`),
  KEY `created_at` (`created_at`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `fk_logs_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table des webhooks Stripe
CREATE TABLE `stripe_webhooks` (
  `id` int NOT NULL AUTO_INCREMENT,
  `stripe_event_id` varchar(255) NOT NULL,
  `event_type` varchar(100) NOT NULL,
  `processed` tinyint(1) DEFAULT '0',
  `processing_error` text,
  `data` json NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `processed_at` timestamp NULL DEFAULT NULL,
  
  PRIMARY KEY (`id`),
  UNIQUE KEY `stripe_event_id` (`stripe_event_id`),
  KEY `event_type` (`event_type`),
  KEY `processed` (`processed`),
  KEY `created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Index composites pour performance
CREATE INDEX `idx_alerts_user_date` ON `alerts` (`user_id`, `created_at`);
CREATE INDEX `idx_filters_user_active` ON `vinted_filters` (`user_id`, `is_active`);
CREATE INDEX `idx_alerts_filter_date` ON `alerts` (`filter_id`, `created_at`);

-- Données de test/démo
INSERT INTO `users` (`email`, `username`, `hashed_password`, `first_name`, `last_name`, `subscription_plan`) VALUES
('demo@vintedbot.com', 'demo', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LEP.RT.HyE8H/7FWG', 'Demo', 'User', 'gratuit'),
('pro@vintedbot.com', 'prouser', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LEP.RT.HyE8H/7FWG', 'Pro', 'User', 'pro');

-- Trigger pour mise à jour automatique des timestamps
DELIMITER $$
CREATE TRIGGER `update_user_timestamp` 
BEFORE UPDATE ON `users` 
FOR EACH ROW BEGIN
    SET NEW.updated_at = CURRENT_TIMESTAMP;
END$$

CREATE TRIGGER `update_filter_timestamp` 
BEFORE UPDATE ON `vinted_filters` 
FOR EACH ROW BEGIN
    SET NEW.updated_at = CURRENT_TIMESTAMP;
END$$

CREATE TRIGGER `update_subscription_timestamp` 
BEFORE UPDATE ON `subscriptions` 
FOR EACH ROW BEGIN
    SET NEW.updated_at = CURRENT_TIMESTAMP;
END$$
DELIMITER ;

-- Vue pour les statistiques utilisateur
CREATE VIEW `user_stats` AS
SELECT 
    u.id,
    u.username,
    u.subscription_plan,
    COUNT(DISTINCT f.id) as total_filters,
    COUNT(DISTINCT CASE WHEN f.is_active = 1 THEN f.id END) as active_filters,
    COUNT(DISTINCT a.id) as total_alerts,
    COUNT(DISTINCT CASE WHEN a.created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY) THEN a.id END) as alerts_last_30_days,
    COUNT(DISTINCT CASE WHEN a.action_taken = 'sniped' THEN a.id END) as successful_snipes,
    u.created_at as user_since
FROM users u
LEFT JOIN vinted_filters f ON u.id = f.user_id
LEFT JOIN alerts a ON u.id = a.user_id
GROUP BY u.id;

-- Vue pour le dashboard admin
CREATE VIEW `admin_dashboard` AS
SELECT 
    COUNT(DISTINCT u.id) as total_users,
    COUNT(DISTINCT CASE WHEN u.created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY) THEN u.id END) as new_users_30d,
    COUNT(DISTINCT CASE WHEN u.subscription_plan != 'gratuit' THEN u.id END) as paid_users,
    COUNT(DISTINCT f.id) as total_filters,
    COUNT(DISTINCT CASE WHEN f.is_active = 1 THEN f.id END) as active_filters,
    COUNT(DISTINCT a.id) as total_alerts,
    COUNT(DISTINCT CASE WHEN a.created_at >= CURDATE() THEN a.id END) as alerts_today,
    COUNT(DISTINCT CASE WHEN a.action_taken = 'sniped' AND a.created_at >= CURDATE() THEN a.id END) as snipes_today
FROM users u
LEFT JOIN vinted_filters f ON u.id = f.user_id
LEFT JOIN alerts a ON u.id = a.user_id;

SET foreign_key_checks = 1;