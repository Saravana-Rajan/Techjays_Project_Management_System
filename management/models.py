from django.db import models
from django.contrib.auth.models import User
from django import forms
from datetime import datetime
from decimal import Decimal

# Employee model: Represents the employee of the organization
class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Link to the built-in Django User model
    role = models.CharField(max_length=100)  # Role such as "Team Lead" or "Manager"

    def __str__(self):
        return self.user.username



# Project model: Represents the project created by the manager
class Project(models.Model):
    name = models.CharField(max_length=200)  # Name of the project
    description = models.TextField()  # Description of the project
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)  # The manager who created the project
    employees = models.ManyToManyField(Employee, through='ProjectResource')  # Many-to-Many relation with Employee through ProjectResource
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when the project was created

    def __str__(self):
        return self.name

# ProjectBudget model: Represents the budget allocation for each month and year
class ProjectBudget(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='budgets')  # Links to a specific project
    month = models.CharField(max_length=2)  # e.g., '01' for January
    year = models.CharField(max_length=4)  # e.g., '2024'
    budget = models.DecimalField(max_digits=10, decimal_places=2)  # Budget for the specific month and year

    class Meta:
        unique_together = ('project', 'month', 'year')  # Ensures that each project can have only one budget per month/year combination

    def __str__(self):
        return f"{self.project.name} - {self.month}/{self.year}"


# ProjectResource model: Represents the resources allocated to a project (employee + ratio)


class ProjectResource(models.Model):
    MONTH_CHOICES = [
        ('01', 'January'), ('02', 'February'), ('03', 'March'), ('04', 'April'),
        ('05', 'May'), ('06', 'June'), ('07', 'July'), ('08', 'August'),
        ('09', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December')
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    allocation_ratio = models.FloatField()
    month = models.CharField(max_length=2, choices=MONTH_CHOICES)  # Store month as '01', '02', etc.
    year = models.CharField(max_length=4)  # Store year as '2024', etc.
    actual_resource = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.employee.user.username} - {self.project.name}"

# Comment model: Represents comments added by team lead or manager to a project



class Comment(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    month = models.IntegerField(null=True, blank=True)
    year = models.IntegerField(null=True, blank=True)
    comment_text = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # Allowing null
    created_at = models.DateTimeField(auto_now_add=True)

# Profit and PnL Calculations

# Function to calculate profit rating based on the budget and actual resource

class ProjectComment(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    month = models.IntegerField(null=True, blank=True)
    year = models.IntegerField(null=True, blank=True)
    comment_text = models.TextField()  # Renamed field to avoid conflict
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)



def calculate_profit_rating(budget, actual_budget):
    # Ensure both inputs are Decimals
    budget = Decimal(budget)
    actual_budget = Decimal(actual_budget)

    if budget == 0:
        return Decimal('0')  # Avoid division by zero

    profit_rating = (budget - actual_budget) 
    return profit_rating

# Function to calculate PnL percentage based on the budget and actual resource
def calculate_pnl_percentage(budget, actual_resource):
    return ((budget - actual_resource) / budget) * 100 if budget else 0


# Form for Month and Year Selection
class MonthYearForm(forms.Form):
    MONTH_CHOICES = [(f"{i:02d}", datetime.strptime(f"{i}", "%m").strftime("%B")) for i in range(1, 13)]
    YEAR_CHOICES = [(str(year), str(year)) for year in range(datetime.now().year - 5, datetime.now().year + 6)]  # Last 5 years to next 5 years

    month = forms.ChoiceField(choices=MONTH_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    year = forms.ChoiceField(choices=YEAR_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))


# Employee Assignment Form
class EmployeeAssignmentForm(forms.Form):
    employee = forms.ModelChoiceField(queryset=Employee.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))
    allocation_ratio = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter resource ratio (e.g., 1 or 0.5)'}))
