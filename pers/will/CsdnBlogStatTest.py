#coding=utf-8

import CsdnBlogStat as cbs


class Test(object):
    def __init__(self):
        print("Test")


if __name__ == '__main__':
    cbs.Worker("/Users/wxp/Downloads/chromedriver", "http://learn.blog.csdn.net");
else:
    exit("非法调用")
