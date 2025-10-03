-- Active: 1758963992124@@127.0.0.1@3306
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL UNIQUE,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    role ENUM('user','reviewer','admin','sudo') NOT NULL DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

INSERT INTO `users` (`id`, `company_name`, `username`, `password`, `email`, `role`, `created_at`, `updated_at`) VALUES
(1, '天星旅行社有限公司', '84472643', 'scrypt:32768:8:1$jgCjctP9KnkgU7dl$27894c9b69b67f9e6cde66bd58cde32abf5f4984a5062ea61f56ec0e31727ee766851556d64b54e19f3b0fc7f52798b3b5867d7406a349f74202fc64005aa473', '84472643@example.com', 'admin', '2025-09-27 09:32:29', '2025-09-27 09:32:29'),
(2, '天星旅行社有限公司新竹分公司', '95472079', 'scrypt:32768:8:1$0gL4EuYQruEup9Od$8aeb777bb06d67b362a2102feb21e57d2d0d433ff238e748aae7afeaa731467278fc18518ee6392c6a44742ffaaabd111818ceefd778e31b8f98efe3c4eb458d', '95472079@example.com', 'admin', '2025-09-27 09:38:50', '2025-09-27 09:38:50'),
(3, '雄獅旅行社股份有限公司', '04655091', 'scrypt:32768:8:1$9rFFFxDaOtdqvtzj$221e445791fd21dcead3c71b94ce1c0764a95c37d92b532235e981c3af67e3d3ed8ced591ee02d5a86a64c8b5ec3d60f8a30cf98ae0306294e24dc4662ac95ef', '04655091@example.com', 'user', '2025-09-27 09:40:37', '2025-09-27 09:40:37'),
(4, '冠鵬旅行社股份有限公司', '84271836', 'scrypt:32768:8:1$oAGxyGrT5kcCLdmI$3ca8b56316ae9cd3c7560588f6c4b48ca5d24fbe0ae9bb71ac7450538c43ee9adbc9a1cf9d4018ed07948e3d73e16218fb34f0e69a9ba0425ec0586079909ede', '84271836@example.com', 'user', '2025-09-30 08:39:51', '2025-09-30 10:19:47'),
(5, '玩萬國際旅行社有限公司-臺中分公司', '56800074', 'scrypt:32768:8:1$oAGxyGrT5kcCLdmI$3ca8b56316ae9cd3c7560588f6c4b48ca5d24fbe0ae9bb71ac7450538c43ee9adbc9a1cf9d4018ed07948e3d73e16218fb34f0e69a9ba0425ec0586079909ede', '56800074@example.com', 'user', '2025-09-30 08:39:51', '2025-09-30 10:19:47'),
(6, '北賢旅行社有限公司', '80018501', 'scrypt:32768:8:1$oAGxyGrT5kcCLdmI$3ca8b56316ae9cd3c7560588f6c4b48ca5d24fbe0ae9bb71ac7450538c43ee9adbc9a1cf9d4018ed07948e3d73e16218fb34f0e69a9ba0425ec0586079909ede', '80018501@example.com', 'user', '2025-09-30 08:39:51', '2025-09-30 10:19:47'),
(7, '翱遊旅行社有限公司', '16480997', 'scrypt:32768:8:1$oAGxyGrT5kcCLdmI$3ca8b56316ae9cd3c7560588f6c4b48ca5d24fbe0ae9bb71ac7450538c43ee9adbc9a1cf9d4018ed07948e3d73e16218fb34f0e69a9ba0425ec0586079909ede', '16480997@example.com', 'user', '2025-09-30 08:39:51', '2025-09-30 10:19:47'),
(8, '鼎穩旅行社股份有限公司', '84348011', 'scrypt:32768:8:1$oAGxyGrT5kcCLdmI$3ca8b56316ae9cd3c7560588f6c4b48ca5d24fbe0ae9bb71ac7450538c43ee9adbc9a1cf9d4018ed07948e3d73e16218fb34f0e69a9ba0425ec0586079909ede', '84348011@example.com', 'user', '2025-09-30 08:39:51', '2025-09-30 10:19:47'),
(9, '玩萬國際旅行社有限公司', '29107109', 'scrypt:32768:8:1$oAGxyGrT5kcCLdmI$3ca8b56316ae9cd3c7560588f6c4b48ca5d24fbe0ae9bb71ac7450538c43ee9adbc9a1cf9d4018ed07948e3d73e16218fb34f0e69a9ba0425ec0586079909ede', '29107109@example.com', 'user', '2025-09-30 08:39:51', '2025-09-30 10:19:47'),
(10, '巨豐旅行社股份有限公司', '29161335', 'scrypt:32768:8:1$oAGxyGrT5kcCLdmI$3ca8b56316ae9cd3c7560588f6c4b48ca5d24fbe0ae9bb71ac7450538c43ee9adbc9a1cf9d4018ed07948e3d73e16218fb34f0e69a9ba0425ec0586079909ede', '29161335@example.com', 'user', '2025-09-30 08:39:51', '2025-09-30 10:19:47'),
(11, '山城旅行社有限公司', '69529610', 'scrypt:32768:8:1$oAGxyGrT5kcCLdmI$3ca8b56316ae9cd3c7560588f6c4b48ca5d24fbe0ae9bb71ac7450538c43ee9adbc9a1cf9d4018ed07948e3d73e16218fb34f0e69a9ba0425ec0586079909ede', '69529610@example.com', 'user', '2025-09-30 08:39:51', '2025-09-30 10:19:47');


CREATE TABLE individuals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    chinese_last_name VARCHAR(100) NOT NULL COMMENT '中文姓',
    chinese_first_name VARCHAR(100) NOT NULL COMMENT '中文名',
    english_last_name VARCHAR(100) NOT NULL COMMENT '英文姓',
    english_first_name VARCHAR(100) NOT NULL COMMENT '英文名',
    national_id VARCHAR(20) NOT NULL UNIQUE COMMENT '身分證字號',
    gender ENUM('男', '女') NOT NULL COMMENT '性別',
    passport_infomation_image LONGBLOB COMMENT '護照資訊頁圖片',
    id_card_front_image LONGBLOB COMMENT '身分證正面圖片',
    id_card_back_image LONGBLOB COMMENT '身分證背面圖片',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE applications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    individual_id INT NOT NULL,
    application_type ENUM('首來族', '換證', '遺失件') NOT NULL,
    urgency ENUM('急件', '普通件') NOT NULL,
    application_date DATE NOT NULL DEFAULT (CURRENT_DATE),
    customer_name VARCHAR(255) NOT NULL,
    status ENUM('草稿','待審核', '補件','送件中' ,'已完成') DEFAULT '草稿',
    substatus ENUM('失敗','成功', '補繳費用') DEFAULT NULL,
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (individual_id) REFERENCES individuals(id)
);

CREATE TABLE notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

