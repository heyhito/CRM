from django.utils.module_loading import import_string
from django.urls import (RegexURLResolver, RegexURLPattern)
from CRM import settings
from collections import OrderedDict

def recursion_urls(pre_namespace, pre_url, urlpatterns, url_ordered_dict):
    # None, '/', urlpatterns, url_ordered_dict
    '''
    第一次递归：
        url(r'^', include('web.urls')),
        url(r'^rbac/', include('rbac.urls', namespace='rbac')),
    第二次递归：
        'rbac','/^rbac/', rbac.urls文件下的urlpatterns变量, url_ordered_dict
    '''
    for url in urlpatterns:
        if isinstance(url, RegexURLResolver):
            if pre_namespace:
                if url.namespace:
                    namespace = '%s:%s' % (pre_namespace, url.namespace)
                else:
                    namespace = pre_namespace
            else:
                if url.namespace:
                    namespace = url.namespace  # 'rbac'
                else:
                    namespace = None
            recursion_urls(namespace, pre_url + url.regex.pattern, url.url_patterns, url_ordered_dict)

        else:
            if pre_namespace:
                name = '%s:%s' % (pre_namespace, url.name)  # rbac:role_list
            else:
                name = url.name
            if not url.name:
                raise Exception('URL路由中必须设置name属性')
            url = pre_url + url._regex  # /^^login/
            url_ordered_dict[name] = {
                'url_name': name, 'url': url.replace('^', '').replace('$', '')
            }  # {'login':{'url_name': name, 'url': /login/},}


def all_url(ignore_namespace_list=None):
    ignore_list = ignore_namespace_list or []
    # 存放项目所有URL的有序字典
    url_ordered_dict = OrderedDict()
    # 获取项目的所以URL
    urls = import_string(settings.ROOT_URLCONF)
    urlpatterns = []
    '''
    # urlpatterns = [
    #     url(r'^', include('web.urls')),
    #     url(r'^rbac/', include('rbac.urls', namespace='rbac')),
    # ]
    '''
    for url in urls.urlpatterns:
        if isinstance(url, RegexURLResolver) and url.namespace in ignore_list:
            continue
        urlpatterns.append(url)
    recursion_urls(None, '/', urlpatterns, url_ordered_dict)
    return url_ordered_dict

