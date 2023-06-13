from django.shortcuts import render
from paper.models import Paper, Library
from pymongo import MongoClient

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
