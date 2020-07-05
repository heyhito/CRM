from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from django.urls import reverse
from sales import models


class UserAuth(MiddlewareMixin):

    def process_request(self,request):
        white_list = [reverse('login'),reverse('register')]
        if request.path in white_list:
            return
        user_id = request.session.get('user_id')
        if user_id:
            user_obj = models.UserInfo.objects.get(id=user_id)
            request.user_obj = user_obj  # 将用户对象封装到request中
            return
        else:
            return redirect('login')