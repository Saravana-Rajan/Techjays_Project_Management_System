from django import forms
from .models import Project, ProjectResource, Comment, Employee
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from datetime import datetime

from .models import Comment
# Form for creating or editing a Project

from .models import Project

from .models import Comment

from .models import ProjectBudget
# Form for creating or editing a Project
class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description']  # Removed the 'budget' field
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Project Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Project Description', 'rows': 3}),
        }

# Form for allocating resources to a project (employee + ratio)
class ResourceAllocationForm(forms.ModelForm):
    MONTH_CHOICES = [(f"{i:02d}", month) for i, month in enumerate(
        ["January", "February", "March", "April", "May", "June", 
         "July", "August", "September", "October", "November", "December"], start=1)]
    
    YEAR_CHOICES = [(str(year), str(year)) for year in range(2015, 2036)]  # Allow years between 2015 and 2035

    month = forms.ChoiceField(choices=MONTH_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    year = forms.ChoiceField(choices=YEAR_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = ProjectResource
        fields = ['employee', 'allocation_ratio', 'month', 'year']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-control'}),
            'allocation_ratio': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter allocation ratio'}),
        }


# Form for adding comments to a project


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment_text', 'month', 'year']  # Match the model's fields
        widgets = {
            'comment_text': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Add a comment'}),
            'month': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Month'}),
            'year': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Year'}),
        }

# Custom User Creation Form with Role
class CustomUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(
        choices=[('manager', 'Manager'), ('team_lead', 'Team Lead'), ('employee', 'Employee')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ['username', 'role', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}),
        }

    def clean_role(self):
        role = self.cleaned_data.get('role')
        if role not in ['manager', 'team_lead', 'employee']:
            raise forms.ValidationError('Invalid role selected.')
        return role

# Employee Management Form
class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['user', 'role']  # Adjust fields as needed
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'role': forms.Select(choices=[('manager', 'Manager'), ('team_lead', 'Team Lead'), ('employee', 'Employee')], attrs={'class': 'form-control'}),
        }

# Month-Year Selection Form
class MonthYearForm(forms.Form):
    MONTH_CHOICES = [(f"{i:02d}", datetime.strptime(f"{i}", "%m").strftime("%B")) for i in range(1, 13)]
    YEAR_CHOICES = [(str(year), str(year)) for year in range(datetime.now().year - 5, datetime.now().year + 6)]

    month = forms.ChoiceField(choices=MONTH_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    year = forms.ChoiceField(choices=YEAR_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))

# Employee Assignment Form
class EmployeeAssignmentForm(forms.Form):
    employee = forms.ModelChoiceField(queryset=Employee.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))
    allocation_ratio = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter resource ratio (e.g., 1 or 0.5)'}))

    # Year and Month Fields
    MONTH_CHOICES = [(f"{i:02d}", datetime.strptime(f"{i}", "%m").strftime("%B")) for i in range(1, 13)]
    YEAR_CHOICES = [(str(year), str(year)) for year in range(datetime.now().year - 5, datetime.now().year + 6)]

    month = forms.ChoiceField(choices=MONTH_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    year = forms.ChoiceField(choices=YEAR_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))


from django import forms
from .models import ProjectResource

# Form for Budget Management
class BudgetForm(forms.Form):
    MONTH_CHOICES = [(f"{i:02d}", datetime(2000, i, 1).strftime('%B')) for i in range(1, 13)]
    YEAR_CHOICES = [(str(i), str(i)) for i in range(2015, 2036)]

    month = forms.ChoiceField(choices=MONTH_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    year = forms.ChoiceField(choices=YEAR_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    budget_value = forms.DecimalField(max_digits=10, decimal_places=2, widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter budget'}))

    class Meta:
        fields = ['month', 'year', 'budget_value']





class ProjectBudgetForm(forms.ModelForm):
    MONTH_CHOICES = [(f"{i:02d}", month) for i, month in enumerate(
        ["January", "February", "March", "April", "May", "June",
         "July", "August", "September", "October", "November", "December"], start=1)]
    
    YEAR_CHOICES = [(str(year), str(year)) for year in range(2015, 2036)]

    month = forms.ChoiceField(choices=MONTH_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    year = forms.ChoiceField(choices=YEAR_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = ProjectBudget
        fields = ['month', 'year', 'budget']
        widgets = {
            'budget': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter budget'}),
        }


from django import forms
from .models import ProjectBudget

class BudgetForm(forms.ModelForm):
    MONTH_CHOICES = [(f"{i:02d}", month) for i, month in enumerate(
        ["January", "February", "March", "April", "May", "June", 
         "July", "August", "September", "October", "November", "December"], start=1)]
    
    YEAR_CHOICES = [(str(year), str(year)) for year in range(2015, 2036)]  # From 2015 to 2035

    month = forms.ChoiceField(choices=MONTH_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    year = forms.ChoiceField(choices=YEAR_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    budget = forms.DecimalField(max_digits=10, decimal_places=2, widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter budget'}))

    class Meta:
        model = ProjectBudget
        fields = ['month', 'year', 'budget']


