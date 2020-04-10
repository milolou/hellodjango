from django import forms
from django.forms import ValidationError
import re,hashlib
from vote.models import User

USERNAME_PATTERN = re.compile(r'\w{4,20}')

def to_md5_hex(message):
    return hashlib.md5(message.encode()).hexdigest()

class RegisterForm(forms.ModelForm):
    repassword = forms.CharField(min_length=8,max_length=20)

    def clean_username(self):
        username = self.cleaned_data['username']
        if not USERNAME_PATTERN.fullmatch(username):
            raise ValidationError('用户名由字母、数字和下划线构成且长度为4-20个字符')
        return username

    def clean_password(self):
        password = self.cleaned_data['password']
        if len(password) < 8 or len(password) > 20:
            raise ValidationError('无效的密码，密码长度为8-20个字符')
        return to_md5_hex(self.cleaned_data['password'])

    def clean_repassword(self):
        repassword = to_md5_hex(self.cleaned_data['repassword'])
        if repassword != self.cleaned_data['password']:
            raise ValidationError('密码和确认密码不一致')
        return repassword

    class Meta:
        model = User
        exclude = ('no','regdate')

class LoginForm(forms.Form):
    username = forms.CharField(min_length=4,max_length=20)
    password = forms.CharField(min_length=8,max_length=20)
    captcha = forms.CharField(min_length=4,max_length=4)

    def clean_username(self):
        username = self.cleaned_data['username']
        if not USERNAME_PATTERN.fullmatch(username):
            raise ValidationError('无效的用户名')
        return username

    def clean_password(self):
        return to_md5_hex(self.cleaned_data['password'])

class UserForm(forms.ModelForm):
    password = forms.CharField(min_length=8,max_length=20,widget=forms.PasswordInput,label='密码')

    def clean_username(self):
        username = self.cleaned_data['username']
        if not USERNAME_PATTERN.fullmatch(username):
            raise ValidationError('用户名由字母、数字和下划线构成且长度为4-20个字符')
        return username

    def clean_password(self):
        password = self.cleaned_data['password']
        return to_md5_hex(self.cleaned_data['password'])

    class Meta:
        model = User
        exclude = ('no',)


