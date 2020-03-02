import sinaweibopy3
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys #引入keys类操作
import time
import requests
from requests_toolbelt import MultipartEncoder


"""打开浏览器"""
def open_web():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    browser = webdriver.Chrome()
    return browser

"""通过微博API获得url"""
def get_url():
    APP_KEY = '2122800769'
    APP_SECRET = 'df544eed525171f054ac7a9be25bbdd6'
    REDIRECT_URL = 'http://www.csdn.net/greetings'
    client = sinaweibopy3.APIClient(app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=REDIRECT_URL,)
    url = client.get_authorize_url()
    print(url)
    return client,url

"""通过url获取登录code"""
def get_code(browser,url):
    browser.get(url)
    """我的google自动记住密码，不用二次登陆，想多了，还是得登陆"""
    browser.find_element_by_id('userId').send_keys('18868120580')
    time.sleep(1)
    browser.find_element_by_id('passwd').send_keys('ZHFZUISHUAI123')
    time.sleep(3)
    browser.find_element_by_class_name('WB_btn_login').send_keys(Keys.ENTER)
    time.sleep(3)
    #browser.find_element_by_class_name('WB_btn_oauth').send_keys(Keys.ENTER)
    #time.sleep(3)
    code_url = browser.current_url
    code = code_url.split('code=')[-1]
    return code

def get_access(code):
    result = client.request_access_token(code)
    client.set_access_token(result.access_token, result.expires_in)
    uid = client.get.account__get_uid()
    if uid['uid'] == 7281418978:
        print("登录成功")
    return result.access_token

"""完成评论功能"""
def post_comment(id,comment,access_token,data = {}):
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36'}
    url='https://api.weibo.com/2/comments/create.json'
    data['access_token'] = access_token
    data['id'] = id
    data['comment'] = comment
    r = requests.post(url=url,data=data,verify=False,headers = headers)
    return r

"""完成写微博功能"""
def post_new(sentence,pic,access_token):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36'}
    url = 'https://api.weibo.com/2/statuses/share.json'
    data = MultipartEncoder(
	fields={'access_token':access_token,'status':'{} http://zhfbloodz.pythonanywhere.com'.format(sentence),
            'pic': (pic, open(pic, 'rb'), 'image/jpeg'),
            })  
    headers['Content-Type'] = data.content_type
    r = requests.post(url,data,verify = False,headers = headers)
    return r

"""读取金山词霸每日一句"""
def get_ciba():
    content_url = 'http://open.iciba.com/dsapi/'
    res = requests.get(content_url)
    content_e = res.json()['content']
    content_c = res.json()['note']
    content = content_e + '\n' + content_c
    content_p = res.json()['picture2']
    pic = requests.get(content_p).content
    date = "{}-{:02d}-{:02d}".format(time.localtime().tm_year,time.localtime().tm_mon,time.localtime().tm_mday)
    pic_name = '{}.jpg'.format(date)
    with open('pic\\'+pic_name, 'wb') as f:
        f.write(pic)
    return content,pic_name

"""主函数"""
def main():
    browser = open_web()
    client,url = get_url()
    code = get_code(browser,url)
    access_token = get_access(code)
    sentence,pic = get_ciba()
    post_new(sentence,pic,access_token)

if __name__ == "__main__":
    main()