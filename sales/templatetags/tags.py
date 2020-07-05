from django import template
from django.urls import reverse
from django.http.request import QueryDict


register = template.Library()


@register.simple_tag
def reverse_url(request):
    if request.path == reverse('customer'):
        return '公户信息'
    else:
        return '我的客户信息'

@register.simple_tag
def resolve_url(request, url_name,customer_pk):
    next_url = request.get_full_path()  # 客户信息页面/customers/?page=3
    reverse_url = reverse(url_name,args=(customer_pk,))  # 编辑页面/edit_customer/214/
    q = QueryDict(mutable=True)
    q['next'] = next_url
    next_url = q.urlencode()
    full_url = reverse_url + '?' + next_url
    return full_url
