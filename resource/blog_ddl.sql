DROP TABLE IF EXISTS `info_blog`;
CREATE TABLE `info_blog` (
  `k` BIGINT(19) UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `user_name` VARCHAR(63) NOT NULL COMMENT '用户名',
  `title` VARCHAR(31) NOT NULL COMMENT '标题',
  `url` VARCHAR(255) NOT NULL COMMENT '博客地址',
  `summary` VARCHAR(256) NOT NULL COMMENT '摘要内容',
  `article_summary` VARCHAR(256) NOT NULL COMMENT '文章汇总摘要',
  `db_created` DATETIME(3) NOT NULL COMMENT '统计时间',
  `db_modified` TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '修改时间',
  PRIMARY KEY (`k`),
  UNIQUE KEY key_user (`user_name`),
  INDEX `idx_created` (`db_created`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='博客信息表';

DROP TABLE IF EXISTS `info_article`;
CREATE TABLE `info_article` (
  `k` BIGINT(19) UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `ID` BIGINT(19) UNSIGNED NOT NULL COMMENT 'ID',
  `blog_key` BIGINT(19) UNSIGNED NOT NULL COMMENT '博客主键',
  `title` VARCHAR(127) NOT NULL COMMENT '标题',
  `url` VARCHAR(255) NOT NULL COMMENT '博客地址',
  `read` INT NOT NULL COMMENT '阅读数',
  `favour` INT NOT NULL COMMENT '点赞数',
  `comment` INT NOT NULL COMMENT '评论数',
  `created` DATETIME(3) NOT NULL COMMENT '文章创建时间',
  `db_created` DATETIME(3) NOT NULL COMMENT '数据库创建时间',
  `db_modified` TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '数据库修改时间',
  PRIMARY KEY (`k`),
  UNIQUE KEY key_id (`ID`),
  INDEX `key_blog` (`blog_key`),
  INDEX `idx_read` (`read`),
  INDEX `idx_created` (`created`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='文章信息表';

DROP TABLE IF EXISTS `info_article_content`;
CREATE TABLE `info_article_content` (
  `k` BIGINT(19) UNSIGNED NOT NULL COMMENT '文章主键',
  `content` TEXT NOT NULL COMMENT '文章内容',
  `db_created` DATETIME(3) NOT NULL COMMENT '数据库创建时间',
  `db_modified` TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '数据库修改时间',
  PRIMARY KEY (`k`),
  INDEX `idx_modified` (`db_modified`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='文章内容表';


DROP TABLE IF EXISTS `ops_blog_snapshot`;
CREATE TABLE `ops_blog_snapshot` (
  `k` BIGINT(19) UNSIGNED NOT NULL COMMENT '博客主键',
  `time` DATETIME NOT NULL COMMENT '快照时间',
  `user_name` VARCHAR(63) NOT NULL COMMENT '用户名',
  `title` VARCHAR(31) NOT NULL COMMENT '标题',
  `url` VARCHAR(255) NOT NULL COMMENT '文章地址',
  `summary` VARCHAR(256) NOT NULL COMMENT '摘要内容',
  `article_summary` VARCHAR(256) NOT NULL COMMENT '文章摘要汇总',
  `db_created` DATETIME(3) NOT NULL COMMENT '数据库插入时间',
  `db_modified` TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '修改时间',
  PRIMARY KEY (`k`, `time`),
  INDEX `key_user` (`user_name`),
  INDEX `idx_created` (`db_created`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='博客快照表';


DROP TABLE IF EXISTS `ops_article_snapshot`;
CREATE TABLE `ops_article_snapshot` (
  `k` BIGINT(19) UNSIGNED NOT NULL COMMENT '文章主键',
  `time` DATETIME NOT NULL COMMENT '快照时间',
  `ID` BIGINT(19) UNSIGNED NOT NULL COMMENT '文章ID',
  `blog_key` BIGINT(19) UNSIGNED NOT NULL COMMENT '博客主键',
  `title` VARCHAR(127) NOT NULL COMMENT '标题',
  `url` VARCHAR(255) NOT NULL COMMENT '文章地址',
  `read` INT NOT NULL COMMENT '阅读数',
  `favour` INT NOT NULL COMMENT '点赞数',
  `comment` INT NOT NULL COMMENT '评论数',
  `db_created` DATETIME(3) NOT NULL COMMENT '数据库插入时间',
  `db_modified` TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '修改时间',
  PRIMARY KEY (`k`, `time`),
  INDEX `key_id` (`ID`),
  INDEX `key_blog` (`blog_key`),
  INDEX `idx_time` (`time`),
  INDEX `idx_created` (`db_created`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='文章快照表';