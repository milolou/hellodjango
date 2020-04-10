from django.http import JsonResponse,HttpResponseRedirect

LOGIN_REQUIRED_URLS = {
    '/vote/subjects/teachers/praise/','/vote/subjects/teachers/criticize/','/vote/excel/','/vote/echart/',
}

def check_login_middleware(get_resp):
    def wrapper(request,*args,**kwargs):
        if request.path in LOGIN_REQUIRED_URLS:
            if 'userid' not in request.session:
                if request.is_ajax():
                    return JsonResponse({'code': 401, 'message': '请先登录'})
                else:
                    backurl = request.get_full_path()
                    return HttpResponseRedirect(f'/vote/login/?backurl={backurl}')
        return get_resp(request,*args,**kwargs)
    return wrapper
