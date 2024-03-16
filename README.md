# 基于自动爬虫的电影资源搜索器
## 界面：
<img width="801" alt="界面" src="https://github.com/gujiprogram/Bf4_Movie/assets/118802992/940097b4-ad67-4e0e-ad18-c31186ca9b02">  

## 代码解释：
1. 主要文件有form.ui界面文件，还有weight.py和crawl.py
3. 前端使用Qt for Python生成form.ui文件，在Pychram中下载PySide2即可使用python代码调用Qt界面组件。
4. crawl.py文件为自动爬虫文件，内有Crawl对象和Crawl_paCrawlnsearch对象，分别对应不同的资源网站进行爬取，其中提供了requests访问与webdriver模拟浏览器访问，也提供多个模拟UA,以对应不同资源网站的反爬虫措施，为了提升资源获取速度，我实现了异步请求资源网站，优先处理最先获的的html。
5. weight.py为前后端链接文件，爬取的数据依靠Qt的signal进行线程之间的信息传输，其中值得注意是界面程序的运行与爬虫程序的运行会产生冲突，当爬虫程序运行时，界面程序会卡住，为此需要进行多线程处理，将爬虫程序作为新线程进行运行，防止用户在爬虫程序运行时再次点击搜索按钮，还需加入中止线程的机制，保障程序的稳定运行。



