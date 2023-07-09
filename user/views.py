from django.shortcuts import render
from paper.models import Paper, Library
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from .forms import LoginForm, UserRegistrationForm
from django.contrib.auth.models import User
from django.http import JsonResponse
from user.serializers import UserSerializer, AccountSerializer
from .models import Account
from rest_framework import viewsets


def index(request):
    # Get the user id
    user_id = request.user.id

    # Now we get the papers owned by the user
    libraries = Library.objects.filter(owner=user_id)
    paper_ids = []
    for library in libraries:
       paper_ids += library.papers.all().values_list('id', flat=True)
    papers = Paper.objects.filter(paperId__in=paper_ids)
    return render(request, "user/index.html", {"my_library": papers})


class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    def search(self, request):
        """
        Searches for accounts based on the given fields in the request data.
        
        Args:
            request: The HTTP request object containing the data to search for.
            
        Returns:
            A JSON response containing the serialized data of the matching accounts.
        """
        fields = request.data
        users = User.objects.filter(**fields)
        accounts = self.queryset.filter(user__in=users)
        serializer = self.serializer_class(accounts, many=True)
        
        return JsonResponse(serializer.data, safe=False)

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request,
                username=cd['username'],
                password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Authenticated Successfully')
                else:
                    return HttpResponse('Disabled account')
            else:
                return HttpResponse('Invalid login')
    else:
        form = LoginForm()
        return render(request, 'user/login.html', {'form': form})

def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            # Create a new user object but avoid saving it yet
            new_user = user_form.save(commit=False)
            # Set the chosen password
            new_user.set_password(user_form.cleaned_data['password'])
            # Save the User object
            new_user.save()
            # create associated account 
            Account.objects.create(user=new_user)
            return render(request, 'user/register_done.html', {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request, 'user/register.html', {'user_form': user_form})
