from django.shortcuts import render
from vote.models import Subject,Teacher
from django.http import JsonResponse,HttpResponse,HttpResponseRedirect
from vote import userForm
from vote.login import Captcha
from vote import login
from vote.models import User
import random,xlwt
from io import BytesIO
from urllib.parse import quote
from bpmappers.djangomodel import ModelMapper
from bpmappers import RawField
# Create your views here.
ALL_CHARS = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

class SubjectMapper(ModelMapper):
    isHot = RawField('is_hot')
    class Meta:
        model = Subject
        exclude = ('create_date','is_hot')

def show_subjects(request):
    subjects = Subject.objects.all()
    return render(request,'subject.html',{'subjects':subjects})

def subjects_json(request):
    queryset = Subject.objects.all()
    subjects = []
    for subject in queryset:
        subjects.append(SubjectMapper(subject).as_dict())
    return JsonResponse(subjects,safe=False)

def show_teachers(request):
    try:
        sno = int(request.GET['sno'])
        subject = Subject.objects.get(no=sno)
        teachers = subject.teacher_set.all()
        return render(request,'teachers.html',{'subject':subject,'teachers':teachers})
    except (KeyError,ValueError,Subject.DoesNotExist):
        return HttpResponseRedirect('/vote/subjects/')

def praise_or_criticize(request):
    try:
        tno = int(request.GET['tno'])
        teacher = Teacher.objects.get(no=tno)
        if request.path.endswith('/praise/'):
            teacher.good_count += 1
        else:
            teacher.bad_count += 1
        teacher.save()
        data = {'code':200,'hint':'操作成功'}
    except (KeyError,ValueError,Teacher.DoesNotExist):
        data = {'code':404,'hint':'操作失败'}
    return JsonResponse(data)

def register(request):
    page,hint = 'register.html',''
    if request.method == 'POST':
        form = userForm.RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            page = 'login.html'
            hint = '注册成功，请登录'
        else:
            hint = '请输入有效的注册信息'
    return render(request,page,{'hint':hint})

def get_captcha_text(length=4):
    selected_chars = random.choices(ALL_CHARS,k=length)
    return ''.join(selected_chars)

def get_captcha(request):
    captcha_text = get_captcha_text()
    request.session['captcha'] = captcha_text
    image = Captcha.instance().generate(captcha_text)
    return HttpResponse(image,content_type='image/png')

def login(request):
    hint = ''
    if request.method == 'POST':
        if request.session.test_cookie_worked():
            request.session.delete_test_cookie()
            form = userForm.LoginForm(request.POST)
            if form.is_valid():
                captcha_from_user = form.cleaned_data['captcha']
                captcha_from_sess = request.session.get('captcha','')
                if captcha_from_sess.lower() != captcha_from_user.lower():
                    hint = '请输入正确的验证码'
                else:
                    username = form.cleaned_data['username']
                    password = form.cleaned_data['password']
                    user = User.objects.filter(username=username,password=password).first()
                    if user:
                        request.session['userid'] = user.no
                        request.session['username'] = user.username
                        try:
                            url = str(request.GET['backurl'])
                            if url.startswith('http'):
                                url = url[21:]
                            return HttpResponseRedirect(f'{url}')
                        except:
                            return HttpResponseRedirect(f'/vote/subjects/')
                    else:
                        hint = '用户名或密码错误'
            else:
                hint = '请输入有效的登录信息'
        else:
            return HttpResponse("Please enable cookies and try again.")
    request.session.set_test_cookie()
    return render(request,'login.html',{'hint':hint})

def logout(request):
    request.session.flush()
    return HttpResponseRedirect('/vote/subjects/')

def export_teachers_excel(request):
    wb = xlwt.Workbook()
    sheet = wb.add_sheet('老师信息表')
    queryset = Teacher.objects.all().select_related('subject')
    colnames = ('姓名', '介绍', '好评数', '差评数', '学科')
    for index,name in enumerate(colnames):
        sheet.write(0,index,name)
    props = ('name','detail','goof_count','bad_count','subject')
    for row,teacher in enumerate(queryset):
        for col,prop in enumerate(props):
            value = getattr(teacher,prop,'')
            if isinstance(value,Subject):
                value = value.name
            sheet.write(row + 1,col,value)
    buffer = BytesIO()
    wb.save(buffer)
    resp = HttpResponse(buffer.getvalue(),content_type='application/vnd.ms-excel')
    filename = quote('老师.xls')
    resp['content-disposition'] = f'attachment:filename="{filename}"'
    return resp

def get_teachers_data(request):
    queryset = Teacher.objects.all().only('name','good_count','bad_count')
    names = [teacher.name for teacher in queryset]
    good = [teacher.good_count for teacher in queryset]
    bad = [teacher.bad_count for teacher in queryset]
    return JsonResponse({'names':names,'good':good,'bad':bad})

def get_echart(request):
        return render(request,'echart.html')

def jsubjects(request):
    return render(request,'jsubjects.html')
