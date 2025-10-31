-- ============================================================
-- SCHEMA: IDENTITY & ACCESS MANAGEMENT (IAM)
-- Version: 1.1.0 | Date: 2025-11-01
-- ============================================================

-- Create Database
CREATE DATABASE IF NOT EXISTS iam CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE iam;

-- ------------------------------------------------------------
-- TABLE: iam_user_account
-- Holds user identities, authentication method, tenant binding
-- ------------------------------------------------------------
CREATE TABLE iam_user_account (
    user_id             INT AUTO_INCREMENT PRIMARY KEY,
    parent_id           INT             NOT NULL,  -- tenant (ultimate parent)
    username            VARCHAR(150)    NOT NULL UNIQUE,
    email               VARCHAR(255)    NOT NULL UNIQUE,
    phone_number        VARCHAR(50)     NULL,
    display_name        VARCHAR(255)    NOT NULL,
    auth_provider       ENUM('local','azure_ad','okta','saml','other')
                        NOT NULL DEFAULT 'local',
    password_hash       VARCHAR(255)    NULL,
    is_active           BIT(1)          NOT NULL DEFAULT b'1',
    is_locked           BIT(1)          NOT NULL DEFAULT b'0',
    last_login_at       DATETIME        NULL,
    created_at          TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by          VARCHAR(255)    NULL,
    updated_by          VARCHAR(255)    NULL,
    CONSTRAINT uq_iam_user_email UNIQUE (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------
-- TABLE: iam_role
-- Role catalog (RBAC)
-- ------------------------------------------------------------
CREATE TABLE iam_role (
    role_id             INT AUTO_INCREMENT PRIMARY KEY,
    role_name           VARCHAR(100)    NOT NULL UNIQUE,
    role_description    VARCHAR(255)    NULL,
    created_at          TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------
-- TABLE: iam_user_role
-- Many-to-many: users ↔ roles
-- ------------------------------------------------------------
CREATE TABLE iam_user_role (
    user_id     INT NOT NULL,
    role_id     INT NOT NULL,
    assigned_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    assigned_by VARCHAR(255) NULL,
    PRIMARY KEY (user_id, role_id),
    CONSTRAINT fk_iam_user_role_user
        FOREIGN KEY (user_id) REFERENCES iam_user_account(user_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_iam_user_role_role
        FOREIGN KEY (role_id) REFERENCES iam_role(role_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------
-- TABLE: iam_auth_session
-- Login sessions and audit trail
-- ------------------------------------------------------------
CREATE TABLE iam_auth_session (
    session_id          CHAR(64)        PRIMARY KEY,
    user_id             INT             NOT NULL,
    login_time          DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    logout_time         DATETIME        NULL,
    ip_address          VARCHAR(64)     NULL,
    user_agent          VARCHAR(255)    NULL,
    sso_idp_session_ref VARCHAR(255)    NULL,
    created_at          TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_iam_auth_session_user
        FOREIGN KEY (user_id) REFERENCES iam_user_account(user_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------
-- TABLE: iam_mfa_method
-- MFA enrollments per user
-- ------------------------------------------------------------
CREATE TABLE iam_mfa_method (
    mfa_id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT             NOT NULL,
    method_type     ENUM('email_otp','totp','sms','whatsapp','webauthn','custom_app')
                    NOT NULL,
    totp_secret     VARCHAR(255)    NULL,  -- encrypted
    is_primary      BIT(1)          NOT NULL DEFAULT b'0',
    is_active       BIT(1)          NOT NULL DEFAULT b'1',
    created_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_iam_mfa_user
        FOREIGN KEY (user_id) REFERENCES iam_user_account(user_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------
-- TABLE: iam_mfa_challenge
-- Temporary OTP challenges for MFA verification
-- ------------------------------------------------------------
CREATE TABLE iam_mfa_challenge (
    challenge_id    INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT             NOT NULL,
    method_type     ENUM('email_otp','totp','sms','whatsapp','webauthn','custom_app')
                    NOT NULL,
    otp_code_hash   VARCHAR(255)    NULL,
    issued_at       TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at      TIMESTAMP       NOT NULL,
    consumed_at     TIMESTAMP       NULL,
    ip_address      VARCHAR(64)     NULL,
    purpose         ENUM('login','step_up','admin_action','view_confidential_data')
                    NOT NULL DEFAULT 'login',
    CONSTRAINT fk_iam_challenge_user
        FOREIGN KEY (user_id) REFERENCES iam_user_account(user_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------
-- TABLE: iam_auth_log
-- General-purpose audit log
-- ------------------------------------------------------------
CREATE TABLE iam_auth_log (
    log_id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT             NULL,
    event_type      ENUM('login_success','login_failed','logout','mfa_sent','mfa_verified','sso_login','lockout','password_reset')
                    NOT NULL,
    event_time      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ip_address      VARCHAR(64)     NULL,
    user_agent      VARCHAR(255)    NULL,
    details         TEXT            NULL,
    CONSTRAINT fk_iam_authlog_user
        FOREIGN KEY (user_id) REFERENCES iam_user_account(user_id)
        ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------
-- SEED DATA: Default Roles
-- ------------------------------------------------------------
INSERT INTO iam_role (role_name, role_description) VALUES
('admin','Full system access'),
('security','Manage users, roles, and MFA'),
('auditor','Read-only audit and session reports'),
('developer','Access API and integration features'),
('readonly','Limited read-only access');

-- ------------------------------------------------------------
-- VIEWS (optional)
-- ------------------------------------------------------------
CREATE OR REPLACE VIEW vw_iam_active_users AS
SELECT user_id, username, email, phone_number, auth_provider,
       is_active, is_locked, last_login_at
FROM iam_user_account
WHERE is_active = b'1';

CREATE OR REPLACE VIEW vw_iam_audit_summary AS
SELECT user_id,
       SUM(event_type = 'login_success') AS successful_logins,
       SUM(event_type = 'login_failed') AS failed_logins,
       MAX(event_time) AS last_event
FROM iam_auth_log
GROUP BY user_id;

-- ============================================================
-- END OF FILE
-- ============================================================