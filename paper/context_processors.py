from .models import Library

def library_data(request):
    # Get library data for logged in user
    libraries = Library.objects.filter(owner_id=request.user.account.id).order_by('name') if request.user.is_authenticated else []
    return {'libraries': libraries}

def shared_library_data(request):
    # Get shared library data for logged in user
    shared_libraries = Library.objects.filter(sharedWith__id=request.user.account.id).order_by("name") if request.user.is_authenticated else []
    return {'shared_libraries': shared_libraries}