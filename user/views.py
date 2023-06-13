from django.shortcuts import render
from paper.models import Paper, Library
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from .forms import LoginForm, UserRegistrationForm

def index(request):
    # user_id = request.session['user_id']
    user_id = '6484e94301a4909fb6c81438' # test user

    # Now we get the papers owned by the user
    libraries = Library.objects.filter(owner=user_id)
    paper_ids = []
    for library in libraries:
       paper_ids += library.papers.all().values_list('_id', flat=True)
    papers = Paper.objects.filter(_id__in=paper_ids)
    return render(request, "user/index.html", {"my_library": papers})

# Create your views here.
def search(request):
    # paper = Paper.objects.get(_id='9a39635c92641f9eeb297e5f6f9b61cf4392f04c')
    papers = Paper.objects.all()
    print(papers)
    return render(request, 'user/index.html')
    # db = database.clients["infiniCite"]
    # collection = db["paper"]
    # documents = collection.find()
    # for doc in documents:
    #     print(doc)

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
    return render(request, 'login.html', {'form': form})

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
            return render(request, 'register_done.html', {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request, 'register.html', {'user_form': user_form})
