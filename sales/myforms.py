import re
from django import forms
from django.forms.fields import DateField,BooleanField
from django.core.exceptions import ValidationError
from multiselectfield import MultiSelectFormField
from sales import models


# 手机校验
def mobile_validate(value):
    mobile_re = re.compile(r'^(13[0-9]|15[012356789]|17[678]|18[0-9]|14[57])[0-9]{8}$')
    if not mobile_re.match(value):
        raise ValidationError('手机号码格式错误')


# 生成注册标签
class RegisterForm(forms.Form):
    username = forms.CharField(
        min_length=3,
        max_length=16,
        label='用户名',
        widget=forms.widgets.TextInput(attrs={'class': 'username', 'placeholder': '您的用户名', 'autocomplete': 'off', }),
        error_messages={
            'required': '用户名不能为空',
            'min_length': '不能小于3位',
            'max_length': '不能大于16位',
        }
    )
    password = forms.CharField(
        max_length=32,
        min_length=6,
        label='密码',
        widget=forms.widgets.PasswordInput(
            attrs={'class': 'password', 'placeholder': "输入密码", 'oncontextmenu': "return false", 'onpaste': 'return false'}),
        error_messages={
            'required': '密码不能为空',
            'min_length': '不能小于6位',
            'max_length': '不能大于32位',
        }
    )
    r_password = forms.CharField(
        max_length=32,
        min_length=6,
        label='确认密码',
        widget=forms.widgets.PasswordInput(
            attrs={'class': 'password', 'placeholder': '再次输入密码', 'oncontextmenu': 'return false',
                   'onpaste': 'return false'}),
        error_messages={
            'required': '密码不能为空',
        }
    )
    telephone = forms.CharField(
        validators=[mobile_validate, ],
        error_messages={
            'required': '手机号码不能为空'
        },
        widget=forms.TextInput(attrs={
            'type': "phone_number",
            'placeholder': '输入手机号码',
            'autocomplete': 'off',
            'id': 'number',
        })
    )
    email = forms.EmailField(
        label='邮箱',
        widget=forms.widgets.TextInput(attrs={
            'placeholder': '输入邮箱地址',
            'oncontextmenu': 'return false',
            'type': 'email',
        }),
        error_messages={
            'required': '邮箱不能为空',
            'invalid': "邮箱格式不正确"
        }
    )

    def clean(self):
        values = self.cleaned_data
        pwd = values.get('password')
        r_pwd = values.get('r_password')
        if pwd == r_pwd:
            return values
        else:
            self.add_error('r_password', '两次输入的密码不一致！')


# 生成客户添加标签
class CustomerForm(forms.ModelForm):
    class Meta:
        model = models.Customer
        fields = '__all__'
        error_messages = {
            'qq': {'required': '不能为空'},
            'name': {'required': '不能为空'},
            'course': {'required': '不能为空'},
            'sex': {'required': '不能为空'},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field, MultiSelectFormField):
                field.widget.attrs.update({'class': 'form-control'})
            if isinstance(field, DateField):
                field.widget.attrs.update({'type': 'date'})


# 跟踪记录添加标签
class ConsultRecordForm(forms.ModelForm):
    class Meta:
        model = models.ConsultRecord
        fields = '__all__'
        exclude = ['delete_status', ]

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
            if field_name == 'customer':
                field.queryset = models.Customer.objects.filter(consultant=request.user_obj)
            elif field_name == 'consultant':
                field.choices = ((request.user_obj.id, request.user_obj.username),)


# 生成报名记录添加标签
class EnrollRecordForm(forms.ModelForm):
    class Meta:
        model = models.Enrollment
        fields = '__all__'
    def __init__(self,request,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for field_name,field in self.fields.items():
            if field_name == 'customer':
                field.queryset = models.Customer.objects.filter(consultant=request.user_obj)
            if not isinstance(field,BooleanField):
                field.widget.attrs.update({'class': 'form-control'})


# 生成课程记录添加标签
class CourseRecordForm(forms.ModelForm):
    class Meta:
        model = models.CourseRecord
        fields = "__all__"
    def __init__(self,request,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for field_name,field in self.fields.items():
            if not isinstance(field,BooleanField):
                field.widget.attrs.update({'class':'form-control'})


# 生成学习记录标签
class StudyRecordForm(forms.ModelForm):
    class Meta:
        model = models.StudyRecord
        fields = '__all__'
