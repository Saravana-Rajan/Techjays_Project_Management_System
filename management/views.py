from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from datetime import datetime
from decimal import Decimal
from .models import Project, Employee, ProjectComment, ProjectResource, ProjectBudget, calculate_profit_rating
from .forms import (CustomUserCreationForm, EmployeeForm, MonthYearForm, ProjectForm, 
                    ResourceAllocationForm, CommentForm, EmployeeAssignmentForm, BudgetForm, ProjectBudgetForm)
from .models import Project, ProjectComment, Comment
from .forms import CommentForm

# Home Page View
def home(request):
    return render(request, 'management/home.html')

# Registration View
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Create the user
            role = form.cleaned_data.get('role')  # Get the selected role
            
            # Create an Employee based on the selected role
            Employee.objects.create(user=user, role=role)

            # Log the user in automatically after registration
            login(request, user)
            return redirect('home')
        else:
            print(form.errors)  # Debugging line to see if there are validation errors
    else:
        form = CustomUserCreationForm()
    return render(request, 'management/register.html', {'form': form})

# Custom Login View
def custom_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # Redirect based on user role
                try:
                    employee = Employee.objects.get(user=user)
                    if employee.role == 'manager':
                        return redirect('manager_dashboard')
                    elif employee.role == 'team_lead':
                        return redirect('team_lead_dashboard')
                except Employee.DoesNotExist:
                    return redirect('home')  # Redirect to home if role not found
    else:
        form = AuthenticationForm()
    return render(request, 'management/login.html', {'form': form})

# Manager Dashboard: List all projects created by the manager
@login_required
def manager_dashboard(request):
    projects = Project.objects.filter(created_by=request.user)
    return render(request, 'management/manager_dashboard.html', {'projects': projects})




@login_required
def add_comment(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.method == 'POST':
        month = request.POST.get('month')
        year = request.POST.get('year')
        comment_text = request.POST.get('comment')

        # Save the comment with the project, month, and year
        comment = ProjectComment.objects.create(
            project=project,
            month=month,
            year=year,
            comment_text=comment_text,  # Use comment_text instead of comment
            created_by=request.user
        )
        comment.save()

        messages.success(request, 'Comment added successfully!')
        return redirect('project_details', project_id=project.id)

    # Pass the years dynamically if needed
    years = range(2020, 2030)

    return render(request, 'management/add_comment.html', {'project': project, 'years': years})



@login_required
def project_details(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    resources = ProjectResource.objects.filter(project=project)

    project_data = {}

    # Fetch month-wise budgets for the project
    budgets = ProjectBudget.objects.filter(project=project)

    for resource in resources:
        month_year = f"{resource.month}/{resource.year}"  # Dynamic month and year
        if month_year not in project_data:
            project_data[month_year] = {
                'resources': [],
                'actual_budget': 0,
                'budget': 0,
                'profit_rating': 0,
                'pnl_percentage': 0,
                'comments': []  # Initialize an empty list for comments
            }

        # Fetch the budget for this month/year
        budget_entry = budgets.filter(month=resource.month, year=resource.year).first()
        budget_value = float(budget_entry.budget) if budget_entry else 0

        # Sum up actual budget by adding allocation for all resources
        project_data[month_year]['actual_budget'] += resource.allocation_ratio

        # Set the budget for the specific month/year
        project_data[month_year]['budget'] = budget_value

        # Add resource details
        project_data[month_year]['resources'].append({
            'id': resource.id,
            'resource_name': resource.employee.user.username,
            'allocation': resource.allocation_ratio,
        })

        # Calculate PnL% and profit rating
        actual_budget = project_data[month_year]['actual_budget']
        budget = project_data[month_year]['budget']
        if budget > 0:
            pnl_percentage = ((budget - actual_budget) / budget) * 100
            project_data[month_year]['pnl_percentage'] = pnl_percentage
            project_data[month_year]['profit_rating'] = calculate_profit_rating(budget, actual_budget)

        # Fetch the comments for the specific month/year
        comments = ProjectComment.objects.filter(
            project=project, month=resource.month, year=resource.year
        )
        project_data[month_year]['comments'] = comments

    return render(request, 'management/project_details.html', {'project': project, 'project_data': project_data})

# Create a new project (Manager Only)


@login_required
def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user  # Assign the current logged-in user
            project.save()
            return redirect('manager_dashboard')  # Redirect to manager dashboard after project creation
    else:
        form = ProjectForm()

    return render(request, 'management/create_project.html', {'form': form})

# Edit project details (Manager Only)
@login_required
def edit_project(request, project_id):
    project = Project.objects.get(id=project_id)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect('manager_dashboard')
    else:
        form = ProjectForm(instance=project)
    return render(request, 'management/edit_project.html', {'form': form, 'project': project})

# Assign resources to a project (Manager Only)
@login_required
def assign_resources(request, project_id):
    project = Project.objects.get(id=project_id)
    
    if request.method == 'POST':
        form = ResourceAllocationForm(request.POST)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.project = project  # Assign resource to the project
            resource.save()
            return redirect('manager_dashboard')
    else:
        form = ResourceAllocationForm()
    
    resources = ProjectResource.objects.filter(project=project)
    return render(request, 'management/assign_resources.html', {
        'form': form,
        'project': project,
        'resources': resources
    })


@login_required
def assign_employee(request, project_id):
    project = Project.objects.get(id=project_id)
    form = EmployeeAssignmentForm()

    if request.method == 'POST':
        form = EmployeeAssignmentForm(request.POST)
        if form.is_valid():
            # Process the assignment of the employee to the project
            employee = form.cleaned_data['employee']
            allocation_ratio = form.cleaned_data['allocation_ratio']
            month = form.cleaned_data['month']
            year = form.cleaned_data['year']

            # Save resource with month and year
            ProjectResource.objects.create(
                project=project,
                employee=employee,
                allocation_ratio=allocation_ratio,
                month=month,  # Store month
                year=year     # Store year
            )
            return redirect('team_lead_dashboard')

    return render(request, 'management/assign_employee.html', {'form': form, 'project': project})

# View for adding an employee
from django.contrib.auth.models import User
@login_required
def add_employee(request):
    if request.method == 'POST':
        # Create a new Employee instance based on the submitted data
        name = request.POST.get('name')
        role = request.POST.get('role')

        # You can create a User instance here if needed, or you may already have a User
        # For example, creating a new user could be:
        user = User.objects.create(username=name)  # Assuming the username is the same as the name for simplicity

        # Now create the Employee
        employee = Employee.objects.create(user=user, role=role)

        return redirect('employee_list')  # Redirect to employee list after adding
    else:
        return render(request, 'management/add_employee.html')
# Employee List View
@login_required
def employee_list(request):
    employees = Employee.objects.all()  # Adjust this query if you need to filter by specific criteria
    return render(request, 'management/employee_list.html', {'employees': employees})
# Edit Employee View
@login_required
def edit_employee(request, employee_id):
    employee = Employee.objects.get(id=employee_id)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            return redirect('employee_list')  # Redirect to the employee list after editing
    else:
        form = EmployeeForm(instance=employee)
    return render(request, 'management/edit_employee.html', {'form': form, 'employee': employee})

# Budget Editing
@login_required
def edit_budget(request, project_id):
    project = Project.objects.get(id=project_id)
    if request.method == 'POST':
        # Update the budget based on submitted data
        # Assume you have a field for budget in the Project model
        project.budget = request.POST.get('budget')
        project.save()
        return redirect('manager_dashboard')
    return render(request, 'management/edit_budget.html', {'project': project})

# Add and view comments on a project (Manager and Team Lead)
@login_required
def project_comments(request, project_id):
    project = Project.objects.get(id=project_id)
    comments = Comment.objects.filter(project=project)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.project = project  # Link comment to the project
            comment.user = request.user  # Set the user who made the comment
            comment.save()
            return redirect('project_comments', project_id=project.id)
    else:
        form = CommentForm()

    return render(request, 'management/project_comments.html', {
        'project': project,
        'comments': comments,
        'form': form
    })



 # Correct form
@login_required
def allocate_resources(request, project_id):
    project = Project.objects.get(id=project_id)
    if request.method == 'POST':
        form = ResourceAllocationForm(request.POST)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.project = project  # Assign the resource to the project
            resource.save()
            return redirect('project_details', project_id=project.id)
    else:
        form = ResourceAllocationForm()

    resources = ProjectResource.objects.filter(project=project)

    return render(request, 'management/allocate_resources.html', {
        'form': form,
        'project': project,
        'resources': resources,
    })

@login_required
def update_resources(request, project_id):
    project = Project.objects.get(id=project_id)
    resources = ProjectResource.objects.filter(project=project)

    if request.method == 'POST':
        for resource in resources:
            allocation = request.POST.get(f'allocation_{resource.id}')
            if allocation:
                allocation_value = float(allocation)
                if 0 <= allocation_value <= 1:  # Validate allocation ratio
                    resource.allocation_ratio = allocation_value
                    resource.save()  # Save updated resource ratio

        messages.success(request, 'Resources updated successfully.')
        return redirect('manager_dashboard')  # Redirect after updating

    return render(request, 'management/update_resources.html', {'project': project, 'resources': resources})


@login_required
def update_actual_resources(request, project_id):
    project = Project.objects.get(id=project_id)
    resources = ProjectResource.objects.filter(project=project)

    if request.method == 'POST':
        for resource in resources:
            allocation = request.POST.get(f'allocation_{resource.id}')
            if allocation:
                allocation_value = float(allocation)
                if 0 <= allocation_value <= 1:  # Validate allocation ratio
                    resource.allocation_ratio = allocation_value
                    resource.save()
                else:
                    messages.error(request, f'Invalid allocation for {resource.employee.user.username}. Must be between 0 and 1.')

        messages.success(request, 'Actual resources updated successfully.')
        return redirect('team_lead_dashboard')  # Adjust based on where you want to redirect

    return render(request, 'management/update_actual_resources.html', {'project': project, 'resources': resources})





@login_required
def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'POST':
        project.delete()
        messages.success(request, 'Project deleted successfully.')
        return redirect('manager_dashboard')
    return render(request, 'management/delete_project_confirm.html', {'project': project})




@login_required
def edit_resource(request, resource_id):
    resource = get_object_or_404(ProjectResource, id=resource_id)

    if request.method == 'POST':
        form = ResourceAllocationForm(request.POST, instance=resource)
        if form.is_valid():
            form.save()
            messages.success(request, 'Resource updated successfully.')
            return redirect('project_details', project_id=resource.project.id)
    else:
        form = ResourceAllocationForm(instance=resource)

    return render(request, 'management/edit_resource.html', {'form': form, 'resource': resource})



@login_required
def budget_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            month = form.cleaned_data['month']
            year = form.cleaned_data['year']
            budget_value = form.cleaned_data['budget_value']

            # Save or update the budget in the ProjectResource model
            ProjectResource.objects.update_or_create(
                project=project, 
                month=month, 
                year=year, 
                defaults={'budget': budget_value}
            )
            return redirect('project_details', project_id=project.id)
    else:
        form = BudgetForm()

    return render(request, 'management/budget_form.html', {'form': form, 'project': project})




@login_required
def add_budget(request, project_id):
    project = Project.objects.get(id=project_id)
    
    if request.method == 'POST':
        form = ProjectBudgetForm(request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.project = project
            budget.save()
            return redirect('project_details', project_id=project_id)
    else:
        form = ProjectBudgetForm()
    
    return render(request, 'management/add_budget.html', {'form': form, 'project': project})




@login_required
def budget_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            # Create or update the ProjectBudget instance
            month = form.cleaned_data['month']
            year = form.cleaned_data['year']
            budget = form.cleaned_data['budget']
            
            # Check if a budget already exists for this month/year
            project_budget, created = ProjectBudget.objects.update_or_create(
                project=project, 
                month=month, 
                year=year,
                defaults={'budget': budget}
            )
            
            return redirect('project_details', project_id=project.id)
    else:
        form = BudgetForm()

    return render(request, 'management/budget.html', {'form': form, 'project': project})


@login_required
def total_project_profit(request):
    projects = Project.objects.all()
    project_profit_data = []

    for project in projects:
        resources = ProjectResource.objects.filter(project=project)
        budgets = ProjectBudget.objects.filter(project=project)
        
        for resource in resources:
            month_year = f"{resource.month}/{resource.year}"
            budget_entry = budgets.filter(month=resource.month, year=resource.year).first()
            budget_value = float(budget_entry.budget) if budget_entry else 0
            actual_budget = resource.allocation_ratio
            
            # Calculate PnL % and Profit Rating
            if budget_value > 0:
                pnl_percentage = ((budget_value - actual_budget) / budget_value) * 100
                profit_rating = calculate_profit_rating(budget_value, actual_budget)
            else:
                pnl_percentage = 0
                profit_rating = 0

            project_profit_data.append({
                'project_name': project.name,
                'month_year': month_year,
                'profit_rating': profit_rating,
                'pnl_percentage': pnl_percentage
            })

    return render(request, 'management/total_project_profit.html', {'project_profit_data': project_profit_data})
