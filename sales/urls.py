from django.conf.urls import url
from sales.views import (auth,customer)


urlpatterns = [
    # 登陆
    url(r'^login/', auth.login, name='login'),
    # 注册
    url(r'^register/', auth.register, name='register'),
    # 公户
    url(r'^customers/', customer.CustomersView.as_view(), name='customer'),
    # 私户
    url(r'^mycustomers/', customer.CustomersView.as_view(), name='mycustomers'),
    # 添加客户
    url(r'^add_customer/', customer.add_edit_customer, name='add_customer'),
    # 编辑客户
    url(r'^edit_customer/(\d+)/', customer.add_edit_customer, name='edit_customer'),
    # 跟进记录
    url(r'^consultrecord/', customer.ConsultRecordView.as_view(), name='consultrecord'),
    # 添加跟进记录
    url(r'^add_consultrecord/', customer.add_edit_consultrecord, name='add_consultrecord'),
    # 编辑跟进记录
    url(r'^edit_consultrecord/(\d+)/', customer.add_edit_consultrecord, name='edit_consultrecord'),
    # 报名信息
    url(r'^enrollment/', customer.EnrollmentView.as_view(), name='enrollment'),
    # 添加报名信息
    url(r'^add_enrollment/', customer.Add_Edit_EnrollRecord.as_view(), name='add_enrollment'),
    # 编辑报名信息
    url(r'^edit_enrollment/(\d+)/', customer.Add_Edit_EnrollRecord.as_view(), name='edit_enrollment'),
    # 班级记录
    url(r'^course_record/', customer.CourseRecordView.as_view(), name='course_record'),
    # 添加班级记录
    url(r'^add_course_record/', customer.Add_Edit_CourseRecord.as_view(), name='add_course_record'),
    # 编辑班级记录
    url(r'^edit_course_record/(\d+)/', customer.Add_Edit_CourseRecord.as_view(), name='edit_course_record'),
    # 查看学习记录
    url(r'^study_record/(\d+)/', customer.StudyRecordView.as_view(), name='single_study_record'),
]