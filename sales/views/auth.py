from django.shortcuts import (render, redirect,)

from sales.utils.encryption import encrypt
from sales import models
from sales.myforms import RegisterForm
from rbac.server.permissions import add_permission

# 注册
def register(request):
    if request.method == 'GET':
        register_obj = RegisterForm()
        return render(request, 'register.html', {'register_obj': register_obj})
    else:
        register_obj = RegisterForm(request.POST)
        if register_obj.is_valid():
            r_password = register_obj.cleaned_data.pop('r_password')
            register_obj.cleaned_data['password'] = encrypt(r_password)
            models.UserInfo.objects.create(**register_obj.cleaned_data)
            return redirect('login')
        else:
            return render(request, 'register.html', {'register_obj': register_obj})


# 登陆
def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    else:
        username = request.POST.get('username')
        password = request.POST.get('password')
        user_info = models.UserInfo.objects.filter(username=username,password=encrypt(password)).first()
        if user_info:
            # 将用户信息保存在session中
            request.session['user_id'] = user_info.id
            # 将权限出入到session中
            add_permission(request, user_info)
            return redirect('customer')
        else:
            return render(request,'login.html',{'error': '用户名或密码错误!'})