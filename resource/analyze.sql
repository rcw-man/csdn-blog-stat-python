/** 查看博客详情 */
select * from info_blog

/** 查看文章详情 */
select * from info_article order by `read`

/** 查看博客变化详情（快照列表） */
select k, `time`, `user_name`, `title`, summary, article_summary from ops_blog_snapshot order by `time`

/** 分析文章增长量 */
select temp.*, a.title from (select k, max(`read`) mx, min(`read`) mn, max(`read`) - min(`read`) as incr
  from ops_article_snapshot group by k having mx > 50) temp
  left join info_article a on temp.k=a.k order by incr;