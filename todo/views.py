from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Todo
from .forms import TodoForm


@login_required
def todo_list(request):
    todos = Todo.objects.filter(user=request.user)
    
    # Filter by completion status
    status_filter = request.GET.get('status')
    if status_filter == 'completed':
        todos = todos.filter(completed=True)
    elif status_filter == 'pending':
        todos = todos.filter(completed=False)
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        todos = todos.filter(title__icontains=search)
    
    # Pagination
    paginator = Paginator(todos, 6)  # Show 6 todos per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'status_filter': status_filter,
    }
    return render(request, 'todo/todo_list.html', context)


@login_required
def todo_detail(request, pk):
    todo = get_object_or_404(Todo, pk=pk, user=request.user)
    return render(request, 'todo/todo_detail.html', {'todo': todo})


@login_required
def todo_create(request):
    if request.method == 'POST':
        form = TodoForm(request.POST, request.FILES)
        if form.is_valid():
            todo = form.save(commit=False)
            todo.user = request.user
            todo.save()
            messages.success(request, 'Todo created successfully!')
            return redirect('todo:todo_list')
    else:
        form = TodoForm()
    
    return render(request, 'todo/todo_form.html', {'form': form, 'title': 'Create Todo'})


@login_required
def todo_update(request, pk):
    todo = get_object_or_404(Todo, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = TodoForm(request.POST, request.FILES, instance=todo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Todo updated successfully!')
            return redirect('todo:todo_detail', pk=todo.pk)
    else:
        form = TodoForm(instance=todo)
    
    return render(request, 'todo/todo_form.html', {'form': form, 'todo': todo, 'title': 'Update Todo'})


@login_required
def todo_delete(request, pk):
    todo = get_object_or_404(Todo, pk=pk, user=request.user)
    
    if request.method == 'POST':
        todo.delete()
        messages.success(request, 'Todo deleted successfully!')
        return redirect('todo:todo_list')
    
    return render(request, 'todo/todo_confirm_delete.html', {'todo': todo})


@login_required
def toggle_todo_status(request, pk):
    todo = get_object_or_404(Todo, pk=pk, user=request.user)
    todo.completed = not todo.completed
    todo.save()
    
    status = "completed" if todo.completed else "marked as pending"
    messages.success(request, f'Todo {status}!')
    
    return redirect('todo:todo_list')
