from django import forms 
from django.forms import Form
from student_management_app.models import Group, SessionYearModel, Subjects


class DateInput(forms.DateInput):
    input_type = "date"


class AddStudentForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=50, widget=forms.EmailInput(attrs={"class":"form-control"}))
    password = forms.CharField(label="Parol", max_length=50, widget=forms.PasswordInput(attrs={"class":"form-control"}))
    first_name = forms.CharField(label="Ad", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    last_name = forms.CharField(label="Soyad", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    username = forms.CharField(label="İstifadəçi Adı", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    address = forms.CharField(label="Adres", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    gender_list = (
        ('Male','Male'),
        ('Female','Female')
    )
    gender = forms.ChoiceField(label="Cins", choices=gender_list, widget=forms.Select(attrs={"class":"form-control"}))
    profile_pic = forms.FileField(label="Profil Şəkli", required=False, widget=forms.FileInput(attrs={"class":"form-control"}))

    def __init__(self, *args, **kwargs):
        super(AddStudentForm, self).__init__(*args, **kwargs)
        self.fields['subject_id'] = forms.ModelMultipleChoiceField(label="Fənlər", queryset=Subjects.objects.all(), widget=forms.CheckboxSelectMultiple)
        self.fields['group_id'] = forms.ModelMultipleChoiceField(label="Qruplar", queryset=Group.objects.all(), widget=forms.CheckboxSelectMultiple)
        self.fields['session_year_id'] = forms.ChoiceField(label="Sessiya İli", choices=[(session_year.id, str(session_year.session_start_year)+" - "+str(session_year.session_end_year)) for session_year in SessionYearModel.objects.all()], widget=forms.Select(attrs={"class":"form-control"}))

class AddStaffForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=50, widget=forms.EmailInput(attrs={"class":"form-control"}))
    password = forms.CharField(label="Parol", max_length=50, widget=forms.PasswordInput(attrs={"class":"form-control"}))
    first_name = forms.CharField(label="Ad", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    last_name = forms.CharField(label="Soyad", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    username = forms.CharField(label="İstifadəçi Adı", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    address = forms.CharField(label="Adres", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    
    def __init__(self, *args, **kwargs):
        super(AddStaffForm, self).__init__(*args, **kwargs)
        self.fields['group_id'] = forms.ModelMultipleChoiceField(label="Qruplar", queryset=Group.objects.all(), widget=forms.CheckboxSelectMultiple)


class EditStaffForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=50, widget=forms.EmailInput(attrs={"class":"form-control"}))
    password = forms.CharField(required=False, label="Parol (Boş buraxıla bilər)", max_length=50, widget=forms.PasswordInput(attrs={"class":"form-control"}))
    first_name = forms.CharField(label="Ad", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    last_name = forms.CharField(label="Soyad", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    username = forms.CharField(label="İstifadəçi Adı", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    address = forms.CharField(label="Adres", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    
    def __init__(self, *args, **kwargs):
        super(EditStaffForm, self).__init__(*args, **kwargs)
        self.fields['group_id'] = forms.ModelMultipleChoiceField(label="Qruplar", queryset=Group.objects.all(), widget=forms.CheckboxSelectMultiple)

class EditStudentForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=50, widget=forms.EmailInput(attrs={"class":"form-control"}))
    first_name = forms.CharField(label="Ad", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    last_name = forms.CharField(label="Soyad", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    password = forms.CharField(required=False, label="Parol (Boş buraxıla bilər)", max_length=50, widget=forms.PasswordInput(attrs={"class":"form-control"}))
    username = forms.CharField(label="İstifadəçi Adı", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    address = forms.CharField(label="Adres", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    gender_list = (
        ('Male','Male'),
        ('Female','Female')
    )
    gender = forms.ChoiceField(label="Cin", choices=gender_list, widget=forms.Select(attrs={"class":"form-control"}))

    def __init__(self, *args, **kwargs):
        super(EditStudentForm, self).__init__(*args, **kwargs)
        self.fields['subject_id'] = forms.ModelMultipleChoiceField(label="Fənlər", queryset=Subjects.objects.all(), widget=forms.CheckboxSelectMultiple)
        self.fields['group_id'] = forms.ModelMultipleChoiceField(label="Qruplar", queryset=Group.objects.all(), widget=forms.CheckboxSelectMultiple)
        self.fields['session_year_id'] = forms.ChoiceField(label="Sessiya İli", choices=[(session_year.id, str(session_year.session_start_year)+" - "+str(session_year.session_end_year)) for session_year in SessionYearModel.objects.all()], widget=forms.Select(attrs={"class":"form-control"}))
