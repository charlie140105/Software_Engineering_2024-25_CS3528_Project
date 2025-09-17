import shutil

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.conf import settings, global_settings
from django.urls import reverse
from django.utils.functional import SimpleLazyObject
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.views.decorators.http import require_POST
from datetime import datetime, timedelta
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib import messages
from homepage.models import Item

from homepage.models import Item, Author, Item_Image, RTI_File, Planes, Approve_Record
from homepage.forms import SearchForm, ItemInfoForm, RegisterForm, LoginForm, EditForm
from django.core.paginator import Paginator
from django.core.files import File
from django.core.exceptions import SuspiciousFileOperation
from django.http import Http404
from django.db.models import Q
from django.core.files.base import ContentFile
import json
import os
import sys
import subprocess
import zipfile

from django.contrib.auth import login, authenticate, logout, get_user_model
import logging
from django.core.mail import EmailMessage

def test(request):
    return render(request, "test.html",{})

nameStillImage = "file_stillimages"
nameRtiImage = "file_rti"

"""
This function is for searching in homepage. First, Retrieve 
specific file type queries from the search conditions
Next,determine which file types are included in the search
Third, If any file type is needed, filter the data accordingly
Then return the file we need.
"""

def searchFunction(dataToFilter, searchCondition):
    form = SearchForm(searchCondition)
    # print('searching')

    # filter by file types
    # Names of varibles are not standardized
    queryStillImage = searchCondition.get('files_Still_Images', '')
    queryRtiImage = searchCondition.get('file_RTI', '')
    # query3dImage = searchCondition.get('files_3d')
    fileTypeDict = {}

    # check what file type is searched for
    if queryStillImage != '':
        fileTypeDict[nameStillImage] = True
    else:
        fileTypeDict[nameStillImage] = False
    if queryRtiImage != '':
        fileTypeDict[nameRtiImage] = True
    else:
        fileTypeDict[nameRtiImage] = False

    # search rti included files
    if fileTypeDict[nameRtiImage] == True:
        dataToFilter = dataToFilter.filter(rti__isnull=False).distinct()

    # search still image included files
    if fileTypeDict[nameStillImage] == True:
        dataToFilter = dataToFilter.filter(images__isnull=False).distinct()

    # filter by date
    dateFrom = searchCondition.get('datefrom', None)
    dateTo = searchCondition.get('dateto', None)

    if dateFrom != None and dateFrom != '':
        # print("filtering by date")
        # dataToFilter = dataToFilter.filter(Upload_Date__gte=searchCondition['datefrom'])
        dataToFilter = dataToFilter.filter(Upload_Date__gte=dateFrom)

    if dateTo != None and dateTo != '':
        # print("filtering by date")
        # dataToFilter = dataToFilter.filter(Upload_Date__lt=searchCondition['dateto'])
        dateTo = (datetime.strptime(dateTo, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
        dataToFilter = dataToFilter.filter(Upload_Date__lt=dateTo)

    # filter by author
    author = searchCondition.get('author', None)
    if author:
        # Split the author string by space to handle first name and last name
        names = author.strip().split()

        if len(names) == 1:
            # Search by first name or last name if only one name provided
            first_name = names[0]
            last_name = names[0]  # Both first name and last name are the same
            dataToFilter = dataToFilter.filter(
                Q(Author__First_Name__iexact=first_name) | Q(Author__Last_Name__iexact=last_name)
            ).distinct()

        elif len(names) >= 2:
            # Search by full name if both first name and last name provided
            first_name = names[0]
            last_name = names[-1]
            dataToFilter = dataToFilter.filter(
                Q(Author__First_Name__iexact=first_name) & Q(Author__Last_Name__iexact=last_name)
            ).distinct()

    # filter by title
    title = searchCondition.get('title', None)
    if title != None and title != '':
        # print("filtering by title")
        dataToFilter = dataToFilter.filter(Title__icontains=searchCondition['title'])

    # filter by status
    status = searchCondition.get('status', None)
    if status != None and status != '':
        # print("filtering by status")
        dataToFilter = dataToFilter.filter(approve_status__icontains=searchCondition['status'])

    # filter by tags
    tags_to_search = searchCondition.get('tag', None)
    if tags_to_search:
        search_tag_list = [tag.strip() for tag in tags_to_search.split(',')]  # 处理搜索条件中的标签列表
    else:
        search_tag_list = []

    # print("tags_to_search:", tags_to_search)
    # print("search_tag_list:", search_tag_list)

    if search_tag_list:
        # print("filtering by tags")
        filtered_data = []
        for item in dataToFilter:
            item_tags = item.Tags.split(',') if item.Tags else []
            item_tags = [t.strip() for t in item_tags]

            if all(tag in item_tags for tag in search_tag_list):
                filtered_data.append(item)
        # make sure return a QuerySet object
        dataToFilter = Item.objects.filter(id__in=[item.id for item in filtered_data])
    else:
        filtered_data = list(dataToFilter)

    dataToFilter = filtered_data

    return form, dataToFilter


"""
This one is for homepage sorting.
There are currently six sorting methods
"""


def sortFunction(dataToSort, selectedOption):
    """logic to deal with sort function"""
    if selectedOption == "relevancy":  # This part is related to the tag system which has not been impletemeted
        pass
    elif selectedOption == "date-old-to-new":
        dataToSort = dataToSort.order_by("Upload_Date")
    elif selectedOption == "date-new-to-old":
        dataToSort = dataToSort.order_by("-Upload_Date")
    elif selectedOption == "title-asc":
        dataToSort = dataToSort.order_by("Title")
    elif selectedOption == "title-des":
        dataToSort = dataToSort.order_by("-Title")
    elif selectedOption == "tags-asc":
        dataToSort = dataToSort.order_by("Tags")
    elif selectedOption == "tags-des":
        dataToSort = dataToSort.order_by("-Tags")
    elif selectedOption == "status-asc":
        dataToSort = dataToSort.order_by("approve_status")
    elif selectedOption == "status-des":
        dataToSort = dataToSort.order_by("-approve_status")
    # Not implemented, sorting bug
    # elif selectedOption == "author-asc":
    #    dataToSort = dataToSort.order_by("Author__First_Name", "Author__Last_Name")
    # elif selectedOption == "author-des":
    #    dataToSort = dataToSort.order_by("-Author__First_Name", "-Author__Last_Name")

    return dataToSort


"""
Abstracted zip file handling functions.
"""


def zip_file_handler(rti_file_path, title, rti_instance):
    with zipfile.ZipFile(rti_file_path, 'r') as zip_ref:
        for fileInfo in zip_ref.infolist():
            if '/' in fileInfo.filename:
                print(fileInfo.filename)
                print("skip one folder")
                continue
            with zip_ref.open(fileInfo) as file:
                fileName = os.path.basename(fileInfo.filename)

                uploadPath = f'{title}/{fileName}'

                _, file_extension = os.path.splitext(fileName)

                if not rti_instance.Has_Image:
                        rti_instance.Has_Image = True

                # Create and save a new Planes object for each extracted file
                planes_instance = Planes()
                planes_instance.RTI_File = rti_instance
                file_content = file.read()
                planes_instance.File.save(uploadPath, ContentFile(file_content))

                planes_instance.save()
    return rti_instance


"""
Abstracted ptm/hsh file handling functions.
"""


def ptm_hsh_file_handler(ptm_file_path, title, rti_instance):
    # return three tuples:
    # root: the root directory of the extracted files
    # dirs: a list of directories in the root directory (not including subdirectories)
    # files: a list of files in the root directory
    # topdown: whether to walk down the directory tree in top-down order (True) or bottom-up order (False)
    for root, dirs, files in os.walk(ptm_file_path, topdown=False):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            uploadPath = f'{title}/{file_name}'

            _, file_extension = os.path.splitext(file_name)

            with open(file_path, 'rb') as file:
                if file_name.lower() == 'info.xml':
                    infoxml = ContentFile(file.read(), name=file_name)
                    rti_instance.Info_File.save(file_path, infoxml)
                        

                # Create and save a new Planes object for each extracted file
                rti_instance.Has_Image = True
                planes_instance = Planes()
                planes_instance.RTI_File = rti_instance
                file_content = file.read()
                planes_instance.File.save(uploadPath, ContentFile(file_content))

    return rti_instance


"""
Storing incoming parameters into the database.  
First create a new item, then check if the author exists. 
If it doesn't exist then create a new author.
Next create the rti_file and its associated planes
Finally, create the item_image
"""


def uploadItemFunction(
        authorNames, title, images, uploadDate, Uploader, description,
        alternateTitle, tags, language, provenance, currentCollectionLocation, dimensions,
        accessionNumber, bibliography, details: list, rtiComp=None, rtiFile = None, rtiFilePath=None,
) -> Item:
    """create an Item and save it to database"""
    print("views.py >> uploadItemFunction")

    # Split author names and create or get authors
    # Create a list to store multiple photographer's names
    authors = []
    # Split name to first name and last for searching function
    for author_name in authorNames:
        name_parts = author_name.strip().split()
        first_name = name_parts[0]
        last_name = name_parts[-1] if len(name_parts) > 1 else ""

        # Check if the author already exists in the database
        author, created = Author.objects.get_or_create(
            Last_Name=last_name,
            First_Name=first_name,
        )
        authors.append(author)  # If no, adding to db

    # Get the miniature image from the list of images
    miniatureImage = images[0]

    print("Uploader type:", type(Uploader))
    print("Uploader is_authenticated:", Uploader.is_authenticated)

    # Create a new Item object and save it to the database
    newItem = Item(
        Title=title, Miniature_Image=None,
        Upload_Date=uploadDate, Media=len(images), Description=description, Uploader=Uploader,
        Alternate_Title=alternateTitle, Tags=tags, Language=language, Provenance=provenance,
        Current_Collection_Location=currentCollectionLocation, Dimensions=dimensions,
        Accession_Number=accessionNumber, Bibliography=bibliography,
    )
    newItem.save()

    newItem.Author.add(*authors)  # Add all authors to the item

    # get rti files and store them in database
    # We get a zip include serveral planes, then we extract all files in that zip and store in database
    # In fact, for the sake of robustness, users who upload files other than plane in the zip will still be able to keep extracting them correctly
    # TODO: handle exception for not uploading a zip file here

    #if rtiFilePath is not None and rtiComp != '':
    if rtiFile:
        rtiInstance = RTI_File()
        rtiInstance.Item = newItem
        rtiInstance.PTM_File = rtiFile
        rtiFilePath = os.path.join(settings.MEDIA_ROOT ,'temp', newItem.Title + '.ptm')
        infoxmlPath =os.path.join(settings.MEDIA_ROOT , 'temp',newItem.Title, 'info.xml')
        infoxml = None
        try:
            sub_result = subprocess.run([settings.RTI_FILE_CONTENT_EXTRACTOR_DIR, rtiFilePath ,'-p', '--png'])
            print(sub_result)
            if sub_result.returncode == 0:
                print("Successful Extraction")
                with open(infoxmlPath, 'rb') as file:
                    infoxml = ContentFile(file.read(), name='info.xml')
                rtiInstance.Info_File.save(newItem.Title +'/info.xml', infoxml)
            else:
                print(f"Error during Extraction")
                print(sub_result.stderr)
        except subprocess.CalledProcessError as e:
            print(f"Error during Extraction: {e}")

        
        rtiInstance.Has_Image = True
        rtiInstance.save()
    print(f"rtifilepath is {rtiFilePath}")

    #  Process and save each image associated with the item
    for i in range(len(images)):
        newItemImage = uploadImageFunction(newItem, images[i], details[i], i + 1)
    return newItem


"""
This function creates the item_image.
"""


def uploadImageFunction(item: Item, image, detail, index) -> Item_Image:
    """upload a new image to an item"""
    print("views.py >> uploadImageFunction")
    itemImage = Item_Image(Item=item, Image=image, View_Detail=detail, Index=index)
    itemImage.save()
    return itemImage


"""
The function responsible for homepage rendering. It first handles the sorting of 
the main page's items. And if there is a search then search is performed.
The rest of the part is pagination. Also in pagination and searching, we used cookies
for storing searching result to make sure the result of pagination always correct.
"""


def home(request):
    # results = Item.objects.all()  # homepage is a list view, it display all images
    results = Item.objects.filter(approve_status=1).order_by('Upload_Date')  # Set Upload_Date to ensure result consistence

    # isSearched = False

    prevSearchCondition = {}

    # handle POST request
    if request.method == "POST":
        if "sort" in request.POST:
            selectedOption = request.POST.get('sort-order')

            # if not isSearched:
            #    results = sortFunction(results, selectedOption)
            # else:
            #    filteredData = searchFunction(results, prevSearchCondition)
            #    results = sortFunction(filteredData, selectedOption)

            results = sortFunction(results, selectedOption)

            request.session['sort_option'] = selectedOption
            form = SearchForm()

            # new
            messages.success(request, "Sorting successfully")

            # return page 1
            return redirect('/?page=1')

        elif "search" in request.POST:

            """logic to deal with search function"""
            # form, results = searchFunction(results, request.POST)
            # isSearched = True
            # prevSearchCondition = request.POST.dict()

            # clear sort option because there has a bug
            if 'sort_option' in request.session:
                del request.session['sort_option']
            form, results = searchFunction(results, request.POST)
            request.session['prev_search_condition'] = request.POST.dict()

            # new
            messages.success(request, "Search successfully")

            # return page 1
            return redirect('/?page=1')

    elif request.method == "GET":
        if 'page' in request.GET:
            sort_option = request.session.get('sort_option')
            if sort_option:
                results = sortFunction(results, sort_option)

            prevSearchCondition = request.session.get('prev_search_condition', {})
            if prevSearchCondition:
                form, results = searchFunction(results, prevSearchCondition)
                if isinstance(results, list):
                    results = sorted(results, key=lambda x: x.Upload_Date)
                else:
                    results = results.order_by('Upload_Date')
            else:
                form = SearchForm()  #

        elif 'search' in request.GET:
            """searched and turning page"""
            # form, results = searchFunction(results, request.GET)
            # isSearched = True
            # prevSearchCondition = request.GET.dict()
            form, results = searchFunction(results, request.GET)
            request.session['prev_search_condition'] = request.GET.dict()

        else:
            form = SearchForm()
    else:
        form = SearchForm()

    """Pagination"""
    """Use the paginator to cut results from the database into pieces
  and render one piece per time with the number of page from GET request"""

    numOfItem = 10
    paginator = Paginator(results, numOfItem)
    pageNum = request.GET.get('page', 1)
    results = paginator.get_page(pageNum)

    context = {
        'form': form,
        'results': results,
        'num_of_pages': paginator.num_pages,
        'prevSearchCondition': prevSearchCondition
    }
    renderedTemplate = render(request, 'home_index.html', context)
    response = HttpResponse(renderedTemplate.content)

    # set COOKIES data
    serializedData = json.dumps(prevSearchCondition)
    response.set_cookie('filterCondition', serializedData)

    # print("Final prevSearchCondition:", prevSearchCondition)

    return response


"""
Function for uploading page. It render the form for the page.
Once it receive the form, it handle with it and call uploadItemFunction.
There is a inline function for extract zip file. zip file alway for rti,
it's also a optional file.
"""


@login_required
def uploadImage(request):
    if request.method == 'POST':
        itemForm = ItemInfoForm(request.POST, request.FILES)
        if itemForm.is_valid():

            # deal with the item info form
            # TODO: handle invalid input or illegal input
            title = request.POST.get('Title')
            print(title)
            # author = itemForm.cleaned_data['Author'].split(',')
            # print(author)

            authorNames = request.POST.getlist('Author')
            # change Author field to list, handling multiple authors

            # for author in authorNames:
            #    print(author)

            upload_date = request.POST.get('Upload_Date')
            upload_images_list = request.FILES.getlist('Upload_Images')
            upload_rti_comp = request.FILES.get('rti_file', '')
            print("--------------------------------")
            print(upload_rti_comp)
            # email = request.POST.get('Email')
            viewDetailList = request.POST.getlist('View_Detail')
            description = request.POST.get('Description')

            language = request.POST.get('Language')
            alternate_title = request.POST.get('Alternate_Title')
            provenance = request.POST.get('Provenance')
            current_collection_location = request.POST.get('Current_Collection_Location')
            dimensions = request.POST.get('Dimensions')
            accession_number = request.POST.get('Accession_Number')

            tags = request.POST.get('Tags')  # Get tags from POST request
            if tags:  # Check if tags is not None or empty
                tag_list = tags.split(',')  # Split the tags by comma
                cleaned_tags = [tag.strip() for tag in tag_list]  # Strip whitespace from each tag
            else:
                cleaned_tags = []  # If no tags, initialize as empty list

            bibliography = request.POST.get('Bibliography')
            # urls = bibliography.split(',')
            # cleaned_urls = []
            # for url in urls:
            #    url = url.strip()
            #    if url and not (url.startswith('http://') or url.startswith('https://')):
            #        url = 'http://' + url
            #    cleaned_urls.append(url)

            # decompress the rti file and store it in a folder
            rti_file_path = None
            if upload_rti_comp != '':

                # Define functions for processing uploaded files
                def handle_uploaded_file(f, filename):
                    # save the file to a temporary folder
                    directory = os.path.join(settings.MEDIA_ROOT, 'temp')
                    if not os.path.exists(directory):
                        os.makedirs(directory)
                    file_path = os.path.join(directory, filename + os.path.splitext(f.name)[1])
                    with open(file_path, 'wb+') as destination:
                        for chunk in f.chunks():
                            destination.write(chunk)
                    return file_path

                rti_file_path = handle_uploaded_file(upload_rti_comp, title)

            # newItem = uploadItemFunction(
            #     author, title, upload_images_list, upload_date, email, description, viewDetailList, upload_rti_comp,
            #     rti_file_path
            # )
            newItem = uploadItemFunction(
                authorNames,  # This should be a string containing the author's name
                title=title,
                images=upload_images_list,
                uploadDate=upload_date,

                description=description,
                details=viewDetailList,
                rtiFile=upload_rti_comp,
                rtiFilePath=rti_file_path,
                Uploader=request.user,  # 传递当前登录的用户

                alternateTitle=alternate_title,
                language=language,
                provenance=provenance,
                currentCollectionLocation=current_collection_location,
                dimensions=dimensions,
                accessionNumber=accession_number,
                tags=','.join(cleaned_tags),
                bibliography=bibliography,
            )
            messages.success(request, "Upload successfully, please wait for review")
            return redirect('homepage:home')

        else:
            print(itemForm.cleaned_data)
            print(itemForm.errors.as_data())
            print('form validation fail')

    else:
        itemForm = ItemInfoForm()

    return render(request, 'upload_index.html', {'item_form': itemForm})


"""
This is for the detail page. Triggered by clicking 
on the item title in the homepage, simply return the item
"""


def detail_page(request, pk):  # Triggered by clicking on the item title in the homepage, simply return the item
    item = get_object_or_404(Item, pk=pk)
    language_code = item.Language
    language_name = dict(global_settings.LANGUAGES).get(language_code, '')
    tag_list = item.Tags.split(',') if item.Tags else []
    bibliography_list = item.Bibliography.split(',') if item.Bibliography else []
    images = Item_Image.objects.filter(Item=item)
    return render(request, 'item_display.html',
                  {'item': item, 'images': images, 'bibliography_list': bibliography_list, 'tag_list': tag_list,
                   'language_name': language_name})


def help_page(request):
    return render(request, 'help_page.html', {})


def success(request):
    return HttpResponse('successfully uploaded')


"""
If an item has an rti file, then it's able to go into this page.
We prepare the parameters and files needed to build rti and pass them
into the template. filetype is the criterion for determining whether this item
has an rti file. If it does, then pass planes and filetype together. 
"""

def rti_page(request, pk):
    try:
        item = get_object_or_404(Item, pk=pk)
        RTI_item = item.rti.first()

        print(f"RTI Item: {RTI_item}")
        if RTI_item:
            print(f"PTM File: {RTI_item.PTM_File}")

        if not RTI_item or not RTI_item.PTM_File:
            print("PTM File is missing or not found!")
            raise Http404("RTI item not found")

        ptm_file_path = os.path.join(settings.MEDIA_ROOT, RTI_item.PTM_File.name)
        ptm_url = RTI_item.PTM_File.url

        info_url = settings.MEDIA_URL

        planes = RTI_item.planes.all()
        planes_url = [plane.File.url for plane in planes]

        # Determine RTI file type
        if RTI_item.Has_Image:
            file_type = "image"
        else:
            raise Http404("No valid RTI file type found")

        return render(request, 'rti.html', {
            'planes_url': planes_url,
            'rti': RTI_item,
            'info_url': info_url,
            'planes': planes,
            'layout': file_type,
            'name': item.Title
        })

    except Http404 as e:
        messages.error(request, str(e))
        return redirect("homepage:detail_page", pk=pk)
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect("homepage:detail_page", pk=pk)



"""
workflow of sandbox
"""

@user_passes_test(lambda u: u.is_authenticated and u.is_superuser, login_url='/login/', redirect_field_name=None)
def review_items(request):
    
    # Users and Items Pending Approval
    active_users = User.objects.filter(is_active=True)
    pending_items_list = Item.objects.filter(approve_status=0).order_by('id')
    pending_users_list = User.objects.filter(is_active=False).order_by('date_joined')

    # Approved Items (For Management)
    active_items_list = Item.objects.filter(approve_status=1).order_by('-Upload_Date')

    # Set pagination
    items_per_page = 10
    paginator_pending_items = Paginator(pending_items_list, items_per_page)
    paginator_active_items = Paginator(active_items_list, items_per_page)
    paginator_users = Paginator(pending_users_list, items_per_page)

    # Get page numbers
    page_number_items = request.GET.get('page_items')
    page_number_active_items = request.GET.get('page_active_items')
    page_number_users = request.GET.get('page_users')

    # Paginate the queries
    pending_items = paginator_pending_items.get_page(page_number_items)
    active_items = paginator_active_items.get_page(page_number_active_items)
    pending_users = paginator_users.get_page(page_number_users)

    context = {
        'pending_items': pending_items,
        'active_items': active_items,
        'pending_users': pending_users,
        'active_users': active_users
    }

    return render(request, 'review_items.html', context)

@require_POST
def approve_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)  # More robust error handling
    item.approve_status = 1
    item.save()
    temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp', item.Title)
    target_dir = os.path.join(settings.MEDIA_ROOT, item.Title)

    Approve_Record.objects.create(
        Item=item,
        Approval_Admin=request.user,
        Approval_Status=1
    )
    messages.success(request, 'Approve successfully')

    try:
        # Ensure the target directory exists
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        # Move all files and directories from temp to the target directory
        if os.path.exists(temp_dir):
            for filename in os.listdir(temp_dir):
                source_path = os.path.join(temp_dir, filename)
                target_path = os.path.join(target_dir, filename)
                if os.path.exists(target_path):
                    os.remove(target_path)
                shutil.move(source_path, target_path)

            RTI_item = item.rti.first()
            if RTI_item:
                RTI_PTM_FILE_LOCATION = os.path.join(settings.MEDIA_ROOT,'temp', item.Title + '.ptm')
                os.remove(RTI_PTM_FILE_LOCATION) 
            shutil.rmtree(temp_dir)
        print(f"Files moved from {temp_dir} to {target_dir}")
    except Exception as e:
        print(f"Error moving files: {e}")
        messages.error(request, f"Error moving files: {e}")

    return redirect('homepage:review_items')


@require_POST
def reject_item(request, item_id):
    item = Item.objects.get(id=item_id)
    item.approve_status = 2
    item.save()
    Approve_Record.objects.create(
        Item=item,
        Approval_Admin=request.user,
        Approval_Status=2,
        Approval_Comment=request.POST.get('reject_reason')
    )
    messages.success(request, 'Reject successfully')
    return redirect('homepage:review_items')


"""
Edit data
"""


@staff_member_required
def item_edit(request, pk):
    item = get_object_or_404(Item, pk=pk)
    current_images = Item_Image.objects.filter(Item=item)
    authors = item.Author.all()

    # Check if the current user is the uploader or an admin
    if not (request.user == item.Uploader):
        raise Http404("You are not authorized to edit this item.")

    title = item.Title
    # authors = item.Author.all()
    # authors_names = ", ".join(author.Name for author in authors)
    # email = authors.first().Email if authors.exists() else ''
    # print('data:', authors_names)

    if request.method == "POST":
        form = EditForm(request.POST, request.FILES, instance=item)

        if form.is_valid():

            authorNames = request.POST.getlist('Author')
            if Author:
                # Split author names and create or get authors
                authors = []
                for author_name in authorNames:
                    name_parts = author_name.strip().split()
                    first_name = name_parts[0]
                    last_name = name_parts[-1] if len(name_parts) > 1 else ""
                    # Check if the author already exists in the database
                    author, created = Author.objects.get_or_create(
                        Last_Name=last_name,
                        First_Name=first_name,
                    )
                    authors.append(author)

            upload_images_list = request.FILES.getlist('Upload_Images')
            view_detail_list = request.POST.getlist('View_Detail')

            # Handle image deletion
            delete_image_ids = request.POST.getlist('delete_images')
            if delete_image_ids:
                Item_Image.objects.filter(id__in=delete_image_ids).delete()

            if upload_images_list:
                # Append new uploaded images to the existing images
                for i, image in enumerate(upload_images_list):
                    view_detail = view_detail_list[i] if i < len(view_detail_list) else ''
                    uploadImageFunction(item, image, view_detail, i + len(current_images) + 1)

            # authorNames = form.cleaned_data['Author'].split(',')
            # email = form.cleaned_data['Email']

            new_upload_rti_comp = request.FILES.get('rti_file', '')
            if new_upload_rti_comp:
                rti_files = RTI_File.objects.filter(Item=item)
                for rti_file in rti_files:
                    # Delete planes associated with this RTI file
                    planes = Planes.objects.filter(RTI_File=rti_file)
                    for plane in planes:
                        plane.File.delete()  # Delete associated files
                        plane.delete()  # Delete the plane instance
                    # Delete info.json file if exists
                    if rti_file.Info_File:
                        rti_file.Info_File.delete()
                    # Delete the RTI file instance itself
                    rti_file.RTI_Zip.delete()
                    rti_file.delete()

            # decompress the rti file and store it in a folder
            rti_file_path = None
            if new_upload_rti_comp:

                # Define functions for processing uploaded files
                def handle_uploaded_file(f, filename):
                    # save the file to a temporary folder
                    directory = os.path.join(settings.MEDIA_ROOT, 'temp')
                    if not os.path.exists(directory):
                        os.makedirs(directory)
                    file_path = os.path.join(directory, filename + os.path.splitext(f.name)[1])
                    with open(file_path, 'wb+') as destination:
                        for chunk in f.chunks():
                            destination.write(chunk)
                    return file_path

                # Define functions to decompress and move files
                def extract_and_move(zip_path, filename):
                    # Users uploading RTIs use a zip archive, so we got to unzip those file
                    # decompress files and move to target folder
                    rtiFilePath = os.path.join(settings.MEDIA_ROOT, filename)
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(rtiFilePath)
                    return rtiFilePath

                rti_file_path = handle_uploaded_file(new_upload_rti_comp, title)

                update_item = item
                rtiComp = new_upload_rti_comp
                rtiFilePath = rti_file_path

                if rtiFilePath is not None and rtiComp != '':
                    print("Balls23")
                    print("Balls")
                    rtiInstance = RTI_File()
                    rtiInstance.Item = update_item
                    rtiInstance.PTM_File = rti_file
                    rtiFilePath = settings.MEDIA_ROOT + rti_file.name + "/" + rti_file.name + ".ptm"
                    try:
                        sub_result = subprocess.run([settings.RTI_FILE_CONTENT_EXTRACTOR_DIR, rtiFilePath])
                        if sub_result.returncode == 0:
                            print("Successful Extraction")
                        else:
                            print(f"Error during Extraction: ")
                            print(sub_result.stderr)
                    except subprocess.CalledProcessError as e:
                        print(f"Error during Extraction: {e}")
                    rtiInstance = ptm_hsh_file_handler(rtiFilePath, title, rtiInstance)
                    rtiInstance.save()
                    update_item.save()

            # item = Item(
            #    Title=item.Title, Miniature_Image=None,
            #    Upload_Date=item.Upload_Date, Media=len(upload_images_list),
            #    Description=item.Description,
            #    Alternate_Title=item.Alternate_Title, Tags=item.Tags, Language=item.Language,
            #    Provenance=item.Provenance,
            #    Current_Collection_Location=item.Current_Collection_Location, Dimensions=item.Dimensions,
            #    Accession_Number=item.Accession_Number, Bibliography=item.Bibliography,
            # )

            # Update item fields
            item.Title = form.cleaned_data['Title']
            item.Upload_Date = form.cleaned_data['Upload_Date']
            item.Media = len(current_images) + len(upload_images_list)
            item.Description = form.cleaned_data['Description']
            item.Alternate_Title = form.cleaned_data['Alternate_Title']
            item.Tags = form.cleaned_data['Tags']
            item.Language = form.cleaned_data['Language']
            item.Provenance = form.cleaned_data['Provenance']
            item.Current_Collection_Location = form.cleaned_data['Current_Collection_Location']
            item.Dimensions = form.cleaned_data['Dimensions']
            item.Accession_Number = form.cleaned_data['Accession_Number']
            item.Bibliography = form.cleaned_data['Bibliography']
            item.save()

            item.Author.set(authors)

            item.Uploader = request.user  # Update the uploader to the current user
            item.approve_status = 0  # Re-review
            item.save()

            # print(f"rtifilepath is {rtiFilePath}")

            # for i in range(len(upload_images_list)):
            #    view_detail = view_detail_list[i] if i < len(
            #        view_detail_list) else ''  # Default to an empty string or another suitable default value
            #    uploadImageFunction(item, upload_images_list[i], view_detail, i + 1)

            messages.success(request, 'Edit successfully, please wait for review')
            return redirect('homepage:home')  # Redirect to the detail page


    else:
        initial_data = {
            'Title': item.Title,
            'Upload_Date': item.Upload_Date,
            'Description': item.Description,
            'Alternate_Title': item.Alternate_Title,
            'Tags': item.Tags,
            'Language': item.Language,
            'Provenance': item.Provenance,
            'Current_Collection_Location': item.Current_Collection_Location,
            'Dimensions': item.Dimensions,
            'Accession_Number': item.Accession_Number,
            'Bibliography': item.Bibliography,
        }
        form = EditForm(instance=item, initial=initial_data)

    return render(request, 'item_edit.html', {'form': form, 'item': item,
                                              'authors': authors, 'images': current_images, })


"""
Delete Item
"""


@staff_member_required
def item_delete(request, pk):
    item = get_object_or_404(Item, pk=pk)
    # Check if the current user is the uploader or an admin
    if not (request.user == item.Uploader or request.user.is_staff):
        raise Http404("You are not authorized to delete this item.")
    if request.method == 'POST':
        norm_dir = os.path.join(settings.MEDIA_ROOT, item.Title)
        temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp' , item.Title)
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        if os.path.exists(norm_dir):
            shutil.rmtree(norm_dir)
        item.delete()
        messages.success(request, 'Delete successfully')
        return redirect('homepage:home')
    return render(request, 'item_delete.html', {'item': item})


"""
Re upload
"""

'''
Handles the user registration process.
Parameters:
request (HttpRequest): The HTTP request object containing metadata about the request.
Returns:
HttpResponse: Renders the registration page with the form or redirects to the home page after successful registration.
'''
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Require approval before activation
            user.is_staff = False   # Ensure new users are NOT staff
            user.is_superuser = False  # Ensure they are not admins

            # save the data to the database
            user.save()

            # Save additional information about the user
            user.refresh_from_db()
            user.first_name = form.cleaned_data.get('first_name')
            user.last_name = form.cleaned_data.get('last_name')
            user.email = form.cleaned_data.get('email')
            user.save()

            # Send notifications to administrators (here you need to customize the function or logic that sends the email)
            # send_admin_notification(user)

            # Displaying a message to the user
            return render(request, 'registration_pending.html', {'message': 'Registered successfully'})
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})


'''
Handles the user login process.
Parameters:
request (HttpRequest): The HTTP request object containing metadata about the request.
Returns:
HttpResponse: Renders the login page with the form or redirects to the home page after successful login.
'''


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Login successful. Welcome!')
                return redirect('homepage:home')  # Redirect to main page after login
            else:
                # Authentication failed (incorrect password)
                messages.error(request, 'Invalid username or password. Please try again.')
        else:
            # Form is not valid, handle errors if any
            messages.error(request, 'Invalid username or password. Please try again.')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


def user_logout(request):
    if request.user.is_authenticated:
        logout(request)
    messages.success(request, 'Logged out')
    return redirect('homepage:home')


@login_required
def user_profile(request):
    return render(request, 'user_profile.html', {'user': request.user})


@staff_member_required
def user_approval_list(request):
    users = User.objects.filter(is_active=False)
    return render(request, 'admin_dashboard.html', {'users': users})


@staff_member_required
def approve_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    user.is_active = True
    user.save()
    print(user.email)

    # The demo of email service
    subject = "Your registration is approve"
    e_message = "Congratulations, you have successfully registered a UoA DHPA Database account"
    recipient_list = [user.email]

    send_email(subject, e_message, recipient_list)

    tab = request.GET.get('tab', 'users')
    messages.success(request, 'Approve successfully')
    return redirect(f'{reverse("homepage:review_items")}?tab={tab}')


@staff_member_required
def reject_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    user.delete()

    # The demo of email service
    subject = "Your registration is rejected"
    e_messages = "Sorry, your account registration for UoA DHPA Database has been rejected and your account has been deleted. Please contact the website administrator and resubmit the registration."
    recipient_list = [user.email]
    send_email(subject, e_messages, recipient_list)

    # Optional: Send email notification to user
    tab = request.GET.get('tab', 'users')
    messages.success(request, 'Reject successfully')
    return redirect(f'{reverse("homepage:review_items")}?tab={tab}')


def return_item(request, item_id):
    if request.method == 'POST':
        item = get_object_or_404(Item, pk=item_id)
        Uploader = get_object_or_404(User, id=item.Uploader_id)
        comment = request.POST.get('comment', '')

        # Optionally save the comment or handle it according to your application needs
        item.comment = comment  # Assuming your model has a 'comment' field
        item.approve_status = 3  # Update status or similar field
        item.save()

        Approve_Record.objects.create(
            Item=item,
            Approval_Admin=request.user,
            Approval_Status=3,
            Approval_File=request.FILES.get('approval_file')
        )

        # Retrieve the uploaded file
        approval_file = request.FILES.get('approval_file')

        # Optionally add a message to display to the user
        messages.add_message(request, messages.INFO, 'Item returned with upload file.')

        subject = "The comment of your upload"
        e_messages = "Sorry, there are some problems with the item you uploaded. Please check the attachment in your email."
        recipient_list = [Uploader.email]

        send_email(subject, e_messages, recipient_list, approval_file)

        # Redirect to a new URL or the same page to show status
        return redirect('homepage:review_items')  # Redirect as necessary
    else:
        # Handle non-POST request here if needed
        return HttpResponse("Method not allowed", status=405)


def user_item(request):
    # Get all items uploaded by the current user
    items = Item.objects.filter(Uploader=request.user).order_by(
        '-Upload_Date')  # Assuming 'uploader' is the field associated with the user

    prevSearchCondition = {}

    if request.method == "POST":
        if "sort" in request.POST:
            selectedOption = request.POST.get('sort-order')
            items = sortFunction(items, selectedOption)
            request.session['sort_option'] = selectedOption
            form = SearchForm()
        elif "search" in request.POST:
            form, items = searchFunction(items, request.POST)
            request.session['prev_search_condition'] = request.POST.dict()

    elif request.method == "GET":
        if 'page' in request.GET:
            sort_option = request.session.get('sort_option')
            if sort_option:
                items = sortFunction(items, sort_option)
            prevSearchCondition = request.session.get('prev_search_condition', {})
            form = SearchForm(initial=prevSearchCondition)
        elif 'search' in request.GET:
            form, items = searchFunction(items, request.GET)
            request.session['prev_search_condition'] = request.GET.dict()
        else:
            form = SearchForm()
    else:
        form = SearchForm()

    numOfItem = 10
    paginator = Paginator(items, numOfItem)
    pageNum = request.GET.get('page', 1)
    items = paginator.get_page(pageNum)

    context = {
        'form': form,
        'items': items,
        'num_of_pages': paginator.num_pages,
        'prevSearchCondition': prevSearchCondition
    }
    renderedTemplate = render(request, 'user_item.html', context)
    response = HttpResponse(renderedTemplate.content)

    serializedData = json.dumps(prevSearchCondition)
    response.set_cookie('filterCondition', serializedData)

    # print("Final prevSearchCondition:", prevSearchCondition)

    return response


@staff_member_required
@require_POST
def update_user_permission(request):
    if not request.user.is_superuser:  # Ensure only superusers can modify permissions
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)

    user_id = request.POST.get('user_id')
    permission = request.POST.get('permission')
    has_permission = request.POST.get('has_permission') == 'true'

    User = get_user_model()
    try:
        user = User.objects.get(id=user_id)
        
        # Only superusers should modify 'is_superuser'
        if permission == 'is_superuser':
            user.is_superuser = has_permission
        elif permission == 'is_staff':
            user.is_staff = has_permission

        user.save()
        return JsonResponse({'success': True})
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'User not found'}, status=404)


"""
Sends an email with the specified subject and message to the provided email address.
Optionally, an attachment can be included.

Parameters:
subject (str): The subject line of the email.
message (str): The body content of the email.
uploader_email (str): The recipient's email address.
attachment_file (file-like object, optional): A file-like object to attach to the email.
    It should have name, read(), and content_type attributes.

Returns:
None
"""


def send_email(subject, message, uploader_email, attachment_file=None):
    from_email = settings.EMAIL_HOST
    recipient_list = uploader_email

    try:
        # Create an EmailMessage instance
        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=from_email,
            to=recipient_list,
        )

        # Add the attachment if provided
        if attachment_file:
            email.attach(attachment_file.name, attachment_file.read(), attachment_file.content_type)

        # Send the email
        email.send()

        print("Email sent successfully.")

    except Exception as e:
        # Handle exceptions that may occur during email sending
        print(f"An error occurred while sending the email: {e}")


def error_400(request, exception):
    data = {'status_code': 400, 'error_message': 'bad request'}
    return render(request, 'error_page.html', data, status=400)


def error_403(request,exception):
    data = {'status_code': 403, 'error_message': 'Permission denied'}
    return render(request, 'error_page.html', data, status=403)


def error_404(request, exception):
    data = {'status_code': 404, 'error_message': 'Page not found'}
    return render(request, 'error_page.html', data, status=404)


def error_500(request):
    data = {'status_code': 500, 'error_message': 'Internal server error'}
    return render(request, 'error_page.html', data, status=500)

@staff_member_required
def admin_delete_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    
    if request.method == "POST":
        RTI_item = item.rti.first()
        if RTI_item:
            RTI_PTM_FILE_LOCATION = os.path.join(settings.MEDIA_ROOT, RTI_item.PTM_File.name)
            os.remove(RTI_PTM_FILE_LOCATION)
        item_dir = os.path.join(settings.MEDIA_ROOT, item.Title)
        shutil.rmtree(item_dir)
        item.delete()
        messages.success(request, "Item deleted successfully.")
        return redirect('homepage:review_items')

    return render(request, 'item_delete.html', {'item': item})
