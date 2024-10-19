from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Home Page
    path('', views.home, name='home'),
    

    # Registration
    path('register/', views.register, name='register'),

    # Login and Logout
    path('login/', views.custom_login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='management/logout.html'), name='logout'),

    # Dashboard for Manager and Team Lead
    path('manager_dashboard/', views.manager_dashboard, name='manager_dashboard'),
    path('team_lead_dashboard/', views.team_lead_dashboard, name='team_lead_dashboard'),

    # Project Management (Create, Edit, Allocate Resources)
    path('create_project/', views.create_project, name='create_project'),
    path('edit_project/<int:project_id>/', views.edit_project, name='edit_project'),
    path('allocate_resources/<int:project_id>/', views.allocate_resources, name='allocate_resources'),
    
    path('assign_resources/<int:project_id>/', views.assign_resources, name='assign_resources'),

    # Update Actual Resources
    path('update_actual_resources/<int:project_id>/', views.update_actual_resources, name='update_actual_resources'),

    # Project Details and Comments
    path('project_details/<int:project_id>/', views.project_details, name='project_details'),
    path('project_comments/<int:project_id>/', views.project_comments, name='project_comments'),

    # Employee Management
    path('add_employee/', views.add_employee, name='add_employee'),
    path('employee_list/', views.employee_list, name='employee_list'),
    path('edit_employee/<int:employee_id>/', views.edit_employee, name='edit_employee'),

    # Edit Project Budget
    path('edit_budget/<int:project_id>/', views.edit_budget, name='edit_budget'),

    # Update Resources
    path('update_resources/<int:project_id>/', views.update_resources, name='update_resources'),

    # Assign Employee to Project
    path('assign_employee/<int:project_id>/', views.assign_employee, name='assign_employee'),

    path('delete_project/<int:project_id>/', views.delete_project, name='delete_project'),
    path('edit_resource/<int:resource_id>/', views.edit_resource, name='edit_resource'),
    path('create_employee/', views.add_employee, name='create_employee'),
    path('employee_list/', views.employee_list, name='employee_list'),
    path('budget/<int:project_id>/', views.budget_view, name='budget_view'),
    path('add_comment/<int:project_id>/', views.add_comment, name='add_comment'),
    path('total_project_profit/', views.total_project_profit, name='total_project_profit'),

    path('add_budget/<int:project_id>/', views.add_budget, name='add_budget'),
]
