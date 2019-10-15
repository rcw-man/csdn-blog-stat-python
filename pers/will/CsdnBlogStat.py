# coding=utf-8

from selenium import webdriver
from datetime import datetime as Date
import time
import sys
import mysql.connector

import logging

# 在这里设置记录的是什么等级以上的日志
logging.basicConfig(filename='run.log', format='%(asctime)s - %(name)s - %(levelname)s -%(module)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S', level=20)


class Worker(object):
    def __init__(self, driver, blog):
        option = webdriver.ChromeOptions()
        # 静默模式、无图形、工具等，以最小代价运行
        option.add_argument('headless')
        option.add_argument('--no-sandbox')
        option.add_argument('--disable-gpu')
        option.add_argument('--disable-dev-shm-usage')

        logging.info("任务开始执行")
        # 打开chrome浏览器
        self._driver = webdriver.Chrome(executable_path=driver, options=option)
        try:
            self._driver.implicitly_wait(15)
            self._driver.set_page_load_timeout(45)

            self._driver.get(blog)
            # 等待页面装载完；实际上webdriver.get会自动等待，但为了保险，多加一段延时
            time.sleep(0.5)
            self._info = {}
            self.stat()
            logging.info("任务执行结束")
        except Exception:
            logging.error("任务运行错误", exc_info=True)
        finally:
            self._driver.close()

    def stat(self):
        self._info = {"time": Date.now().strftime('%Y-%m-%d %H:%M:%S'), "data": [], "user_name": "", "grade": [],
                      "url": "", "title": "", "articles": []}
        self._statSummary()
        self._statArticles()
        self._record()

    def _statSummary(self):
        ## 获取博客信息
        profile = self._driver.find_element_by_xpath("//div[@id='asideProfile']")
        # 用户信息
        user = profile.find_element_by_xpath("div//a[@id='uid']")
        self._info["user_name"] = user.find_element_by_xpath("..").get_attribute("username")
        self._info["url"] = user.get_attribute("href")
        self._info["title"] = user.text
        # 博客信息
        data = profile.find_elements_by_xpath("./div[2]/dl")
        for d in data:
            self._info["data"].append(d.find_element_by_xpath("dt").text + d.find_element_by_xpath("dd").text)

        # 等级信息
        summary = profile.find_elements_by_xpath("./div[3]/dl")
        for s in summary:
            label = s.find_element_by_xpath("dt").text
            value = s.find_element_by_xpath("dd").text
            if value is None or value == '':
                # 处理等级信息
                title = s.find_element_by_xpath("dd/*[1]").get_attribute("title")
                value = title[0:title.find("级")]
            self._info["grade"].append(label + value)

    def _statArticles(self):
        # 获取文章列表
        total, excludes = 0, set(["82762601"])

        while True:
            articles = self._driver.find_elements_by_xpath(
                "//div[@id='mainBox']/main/div[@class='article-list']/div")
            for article in articles:
                domID, aid = article.get_attribute("id"), article.get_attribute("data-articleid")
                if domID == "pageBox":
                    # 翻页
                    btn = article.find_element_by_xpath("div/ul/li[text()='下一页']")
                    if "ui-pager-disabled" in btn.get_attribute("class"):
                        continue
                    btn.click()
                    time.sleep(15)
                    break
                # csdn头部有一个隐藏的文章，无用可排除
                if aid in excludes:
                    continue
                try:
                    header = article.find_element_by_xpath("h4/*[1]")
                    desc = article.find_element_by_xpath("div[1]")
                    read = desc.find_element_by_xpath("*[3]//span[@class='num']").text
                    total += int(read)
                    article.click()
                    # TODO 统计点赞数
                    favour = 0
                    # favour = $x("//*[@id='supportCount']")[0]

                    self._info["articles"].append(
                        {"id": aid, "created": desc.find_element_by_xpath("*[1]").text, "read": read, "favour": favour,
                         "comment": desc.find_element_by_xpath("*[5]//span[@class='num']").text,
                         "title": header.text,
                         "url": header.get_attribute("href")})
                    logging.debug("访问" + header.get_attribute("href"))
                    time.sleep(2)
                except Exception as e:
                    logging.error("获取文章详情错误，文章：%s" % aid, exc_info=True)
            else:
                break

        self._info["count"] = len(self._info["articles"])
        self._info["sum"] = total
        logging.info(self._info)

    def _record(self):
        # 打开数据库连接（请根据自己的用户名、密码及数据库名称进行修改）
        conn = mysql.connector.connect(user='root', passwd='123456', database='blog')
        try:
            # 使用cursor()方法获取操作游标
            cursor = conn.cursor()
            try:
                user_name, time = self._info["user_name"], self._info["time"]

                # 获取博客主键
                sql = '''select `k` from `info_blog` where `user_name` = '%s' ''' % user_name
                cursor.execute(sql)

                # 保存博客最新信息、新增博客快照
                data = cursor.fetchone()
                blog_params = list((user_name, self._info["title"], self._info["url"],
                                    ",".join(self._info["data"]) + "," + ",".join(self._info["grade"]),
                                    "文章总数：%s, 文章总阅读数：%s" % (self._info["count"], self._info["sum"])))
                if data is None:
                    # 新增博客
                    blog = ('''insert into `info_blog` 
                        (`user_name`, `title`, `url`, `summary`, `article_summary`, `db_created`) values 
                        (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP ); ''')
                    cursor.execute(blog, blog_params)
                    blog_key = cursor.lastrowid
                else:
                    # 更新博客
                    blog_key = data[0]
                    update_params = blog_params.copy()
                    blog = ('''update `info_blog` 
                    set `user_name` = %s, `title` = %s, `url` = %s, `summary` = %s, `article_summary` = %s 
                    where `k` = %s''')
                    update_params.append(blog_key)
                    cursor.execute(blog, update_params)

                if blog_key is None:
                    raise RuntimeError('Found none key which user is %s' % user_name)

                # 新增博客快照
                snap = '''insert into `ops_blog_snapshot` 
                        (`k`, `time`, `user_name`, `title`, `url`, `summary`, `article_summary`, `db_created`) values 
                        (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP );'''
                blog_params.insert(0, time)
                blog_params.insert(0, blog_key)
                cursor.execute(snap, blog_params)

                # 遍历保存文章最新信息、新增文章快照
                articles = self._info["articles"]
                if articles is not None:
                    ids = list(map(lambda a: a["id"], articles))
                    cursor.execute(
                        "select `k`, `ID` from `info_article` where `id` in (%s)" % ','.join(['%s'] * len(ids)),
                        ids)
                    keys = {}
                    for (key, id) in cursor:
                        keys[id] = key

                    sql_at_insert = '''insert into `info_article` 
                            (`id`, `blog_key`, `title`, `url`, `read`, `favour`, `comment`, `created`, `db_created`) values 
                            (%s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)'''
                    sql_at_update = '''update `info_article` 
                                    set `id` = %s, `blog_key` = %s, `title` = %s, `url` = %s, 
                                    `read` = %s, `favour` = %s, `comment` = %s
                                    where `k` = %s'''
                    data_at_snap = []
                    sql_at_snap = '''insert into `ops_article_snapshot` 
                                 (`k`, `time`, `id`, `blog_key`, `title`, `url`, `read`, `favour`, `comment`, `db_created`) values 
                                 (%s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)'''
                    for article in articles:
                        aid = article["id"]
                        ak = keys.get(int(aid))
                        base_param = (aid, blog_key, article["title"], article["url"],
                                      article["read"], article["favour"], article["comment"])
                        # 文章新增或更新
                        if ak is None:
                            insert_param = list(base_param)
                            insert_param.append(article["created"])
                            cursor.execute(sql_at_insert, insert_param)
                            ak = cursor.lastrowid
                        else:
                            update_param = list(base_param)
                            update_param.append(ak)
                            cursor.execute(sql_at_update, update_param)

                        # 文章快照
                        snap_param = list(base_param)
                        snap_param.insert(0, time)
                        snap_param.insert(0, ak)
                        data_at_snap.append(snap_param.copy())
                    cursor.executemany(sql_at_snap, data_at_snap)
            finally:
                conn.commit()
                cursor.close()
        finally:
            # 执行sql语句
            conn.close()


if __name__ == '__main__':
    Worker(sys.argv[1], sys.argv[2])
