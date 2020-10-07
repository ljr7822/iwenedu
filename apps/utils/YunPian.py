import requests
import json


def send_single_sms(apikey, code, mobile):
    # 发送单条短信
    url = "https://sms.yunpian.com/v2/sms/single_send.json"
    text = "【李俊然test】您的验证码是{}。如非本人操作，请忽略本短信".format(code)

    # key:14ed7814cb79725101f44787db3131c7
    res = requests.post(url, data={
        "apikey": apikey,
        "mobile": mobile,
        "text": text
    })
    re_json = json.loads(res.text)
    return re_json


if __name__ == "__main__":
    res = send_single_sms("14ed7814cb79725101f44787db3131c7", "123456", "18289816889")
    res_json = json.loads(res.text)
    code = res_json["code"]
    msg = res_json["msg"]
    if code == 0:
        print("发送成功")
    else:
        print("发送失败: {}".format(msg))
    print(res.text)
