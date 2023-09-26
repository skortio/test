

#FROM_EMAIL = "vegasfriendsofficial@gmail.com"

PRODUCT = 'product'
PRODUCT_RO = 'product_ro'
VEGAS_RO = 'vegas_ro'

MAX_SEND_LIMIT = 50000
ONE_SECOND_COUNT = 500
QUERY_ONE_TIME = 10000
QUERY_GROUP = 20

#VF_REDIRECT_URL = 'http://tester.boledragon.com:8070'
VF_REDIRECT_URL = 'http://webpage.boledragon.com:8070'
#VF_REDIRECT_URL = 'http://127.0.0.1:8000'
VF_REPLACE_UNSUBSCRIBE = "{{vegasFriendsUnsubscribe}}"
VF_REPLACE_OPENED = "{{vegasFriendsOpened}}"
VF_REPLACE_CLICKED = "{{vegasFriendsCliend}}"


def create_url_unsub(uid):
    return "%s/unsubscribe/%s/" % (VF_REDIRECT_URL, uid)


def create_url_opened(uid, send_id):
    return "%s/opened/%s/%s/" % (VF_REDIRECT_URL, uid, send_id)


def create_url_clicked(uid, send_id):
    return "%s/clicked/%s/%s/" % (VF_REDIRECT_URL, uid, send_id)


def replace_html(html_str, uid, send_id):
    html_str = html_str.replace(VF_REPLACE_UNSUBSCRIBE, create_url_unsub(uid))
    #html_str = html_str.replace(VF_REPLACE_OPENED, create_url_opened(uid, send_id))
    #html_str = html_str.replace(VF_REPLACE_CLICKED, create_url_clicked(uid, send_id))

    return html_str
