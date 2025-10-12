CREATE TABLE IF NOT EXISTS Users_log_before (
    user_id BIGINT,
    login VARCHAR(255) NOT NULL,
    gravatar_ID VARCHAR(255),
    avatar_url VARCHAR(255),
    url VARCHAR(255),
    state VARCHAR(10),
    changed_at TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP(3)
);

CREATE TABLE IF NOT EXISTS Users_log_after (
    user_id BIGINT,
    login VARCHAR(255) NOT NULL,
    gravatar_ID VARCHAR(255),
    avatar_url VARCHAR(255),
    url VARCHAR(255),
    state VARCHAR(10),
    changed_at TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP(3)
);

DELIMITER //

CREATE TRIGGER before_insert_Users
BEFORE INSERT ON Users
FOR EACH ROW
BEGIN
    INSERT INTO Users_log_before(user_id, login, gravatar_ID, avatar_url, url, state, changed_at)
    VALUES (NEW.user_id, NEW.login, NEW.gravatar_ID, NEW.avatar_url, NEW.url, 'INSERT', NOW(3));
END;
//

CREATE TRIGGER before_update_Users
BEFORE UPDATE ON Users
FOR EACH ROW
BEGIN
    INSERT INTO Users_log_before(user_id, login, gravatar_ID, avatar_url, url, state, changed_at)
    VALUES (OLD.user_id, OLD.login, OLD.gravatar_ID, OLD.avatar_url, OLD.url, 'UPDATE', NOW(3));
END;
//

CREATE TRIGGER before_delete_Users
BEFORE DELETE ON Users
FOR EACH ROW
BEGIN
    INSERT INTO Users_log_before(user_id, login, gravatar_ID, avatar_url, url, state, changed_at)
    VALUES (OLD.user_id, OLD.login, OLD.gravatar_ID, OLD.avatar_url, OLD.url, 'DELETE', NOW(3));
END;
//

CREATE TRIGGER after_insert_Users
AFTER INSERT ON Users
FOR EACH ROW
BEGIN
    INSERT INTO Users_log_after(user_id, login, gravatar_ID, avatar_url, url, state, changed_at)
    VALUES (NEW.user_id, NEW.login, NEW.gravatar_ID, NEW.avatar_url, NEW.url, 'INSERT', NOW(3));
END;
//

CREATE TRIGGER after_update_Users
AFTER UPDATE ON Users
FOR EACH ROW
BEGIN
    INSERT INTO Users_log_after(user_id, login, gravatar_ID, avatar_url, url, state, changed_at)
    VALUES (NEW.user_id, NEW.login, NEW.gravatar_ID, NEW.avatar_url, NEW.url, 'UPDATE', NOW(3));
END;
//

CREATE TRIGGER after_delete_Users
AFTER DELETE ON Users
FOR EACH ROW
BEGIN
    INSERT INTO Users_log_after(user_id, login, gravatar_ID, avatar_url, url, state, changed_at)
    VALUES (OLD.user_id, OLD.login, OLD.gravatar_ID, OLD.avatar_url, OLD.url, 'DELETE', NOW(3));
END;
//

DELIMITER ;

INSERT INTO Users (user_id, login, gravatar_ID, avatar_url, url) VALUES
(1, 'alice', 'abc123', 'https://example.com/avatar1.png', 'https://example.com/alice'),
(2, 'bob', 'def456', 'https://example.com/avatar2.png', 'https://example.com/bob'),
(3, 'carol', 'ghi789', 'https://example.com/avatar3.png', 'https://example.com/carol'),
(4, 'dave', 'jkl012', 'https://example.com/avatar4.png', 'https://example.com/dave'),
(5, 'eve', 'mno345', 'https://example.com/avatar5.png', 'https://example.com/eve'),
(6, 'frank', 'pqr678', 'https://example.com/avatar6.png', 'https://example.com/frank'),
(7, 'grace', 'stu901', 'https://example.com/avatar7.png', 'https://example.com/grace'),
(8, 'heidi', 'vwx234', 'https://example.com/avatar8.png', 'https://example.com/heidi'),
(9, 'ivan', 'yz1234', 'https://example.com/avatar9.png', 'https://example.com/ivan'),
(10, 'judy', 'zab567', 'https://example.com/avatar10.png', 'https://example.com/judy');

UPDATE Users SET avatar_url = 'https://example.com/avatar1-new.png' WHERE user_id = 1;
UPDATE Users SET avatar_url = 'https://example.com/avatar2-new.png' WHERE user_id = 2;
UPDATE Users SET avatar_url = 'https://example.com/avatar3-new.png' WHERE user_id = 3;
UPDATE Users SET avatar_url = 'https://example.com/avatar4-new.png' WHERE user_id = 4;
UPDATE Users SET avatar_url = 'https://example.com/avatar5-new.png' WHERE user_id = 5;

DELETE FROM Users WHERE user_id IN (6,7,8,9,10);
