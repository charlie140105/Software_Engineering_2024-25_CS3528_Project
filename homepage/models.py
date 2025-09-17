from django.contrib.auth.models import User
from django.db import models
from datetime import date
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.conf import settings

#from django.contrib.auth.models import User

"""
property is for quickly specified the name.
"""


class Author(models.Model):
    Last_Name = models.CharField(max_length=50)
    First_Name = models.CharField(max_length=50)
    #Email = models.CharField(max_length=100) #Now don't need it

    @property
    def Name(self):
        return f"{self.Last_Name} {self.First_Name}"

    def full_name(self, new_name):
        self.Last_Name, self.First_Name = new_name.split(' ', 1)
        self.save()

    def __str__(self) -> str:
        return self.First_Name + " " + self.Last_Name


"""
Media means how many images in this item
Title is the name of the item, it will be showed in homepage
Miniature_Image use for thumbnail 
Upload_Date is exectly as it's name
"""


# main image
class Item(models.Model):

    # customise the upload directory path of main image
    def uploadDirectoryPath(instance, filename):
        #TODO: different items with same name may lead to images all go to the same folder
        title = instance.Title
        folderName = "".join(x for x in title if x.isalnum() or x in [" ", "_"]).rstrip()
        return f'{folderName}/{filename}'

    Title = models.CharField(max_length=255)
    Miniature_Image = models.ImageField(upload_to=uploadDirectoryPath, null=True,
                                        blank=True)  # location of miniature image file in server storage
    Author = models.ManyToManyField(Author, related_name="items")  # Multiple photographers of the item


    Upload_Date = models.DateField(default=timezone.now) #Change to Era of item

    #optional
    Alternate_Title = models.CharField(max_length=255, null=True, blank=True)  # new

    Language = models.CharField(max_length=255, null=True, blank=True)  # new

    Provenance = models.CharField(max_length=255, null=True, blank=True)  # new
    Current_Collection_Location = models.CharField(max_length=255, null=True, blank=True)  # new
    Dimensions = models.CharField(max_length=255, null=True, blank=True)  # new
    Accession_Number = models.CharField(max_length=255, null=True, blank=True)  # new

    Tags = models.CharField(max_length=255, null=True, blank=True)  # new

    Bibliography = models.TextField(null=True, blank=True)  # new

    #the status of sandbox
    approve_status = models.IntegerField(default=0)
    Media = models.IntegerField()
    Description = models.TextField(null=True, blank=True)  # new
    Uploader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_items',
                                 null=True)
    
    def __str__(self) -> str:
        return "Item " + str(self.Title)


# private class to standardize the name of file types
"""
This class is a private class in models.py 
This is to standardise the file_type inside Item_Image
"""


class _FileType(models.TextChoices):
    Still_Image = 'file_stillimages'
    RTI_File = 'file_rti'
    Three_Dimension_File = 'files_3d'


"""
Index is the sequence of the image.
View_Deatil is a brief of this image, usually just a sentence.
Image is the key field which stores the image's locations
File_type only have three value. This is for search from. 
"""


# each image is related to item and recieves a unique index indicating its position in carousell
class Item_Image(models.Model):

    # customise the upload directory path of each file
    def uploadDirectoryPath(instance, filename):
        #TODO: different items with same name may lead to images all go to the same folder
        title = instance.Item.Title
        folderName = "".join(x for x in title if x.isalnum() or x in [" ", "_"]).rstrip()
        return f'{folderName}/{filename}'

    Item = models.ForeignKey(Item, related_name='images', on_delete=models.CASCADE)
    Image = models.ImageField('Attachment', upload_to=uploadDirectoryPath, null=True, blank=True)
    View_Detail = models.CharField(max_length=75, default="Null")
    # File_type = models.CharField(max_length=20, choices=_FileType.choices, default=_FileType.Still_Image)
    Index = models.IntegerField()

    def __str__(self) -> str:
        return "Item_Image " + str(self.Image)


"""
RTI_File is a one to one relationship though it is a foreign key. Has_DZI, Has_TZI, Has_Image is for constructing 
RTI files in rti.html. Info_File is a important file which tell us the argument of the rti file
the whole rti zip is like:
    folder---
        plane_0.xxx
        plane_1.xxx
            ....
        plane_x.xxx
        info.json
"""


class RTI_File(models.Model):

    def uploadDirectoryPath(instance, filename):
        #TODO: different items with same name may lead to images all go to the same folder
        title = instance.Item.Title
        folderName = "".join(x for x in title if x.isalnum() or x in [" ", "_"]).rstrip()
        return f'{folderName}/{filename}'

    Has_Image = models.BooleanField(default=True)
    Info_File = models.FileField()  # store info.json
    PTM_File = models.FileField(upload_to="ptm_files/", blank=True, null=True)
    #RTI_Zip = models.FileField(upload_to=uploadDirectoryPath, default=None, null=True)
    
    Item = models.ForeignKey(Item, related_name='rti', on_delete=models.CASCADE)


"""
Planes is for stroing rti files. Usually those file end up with .dzi .tzi or .jpg.
A one to many relationship is used in this model with only one file field.
Just for robustness, actually all kinds of file is accecptable. If clients accidently 
add extra files, code still works.
"""


class Planes(models.Model):
    File = models.FileField()
    RTI_File = models.ForeignKey(RTI_File, related_name='planes', on_delete=models.CASCADE)

    def __str__(self) -> str:
        return str(self.File)


"""
Architectture of the database  ----> means one to many relationship ----means one to one relationship
Author <----
            Item<----
                     Item_Image
                                ----RTI_FIle
                                             ----> Planes
                                            
"""
'''
@receiver(post_save, sender=Item_Image)
def update_miniature_image(sender, instance, created, **kwargs):
    if created:
        item = instance.Item
        if item.Miniature_Image is None:
            item.Miniature_Image = instance.Image
            item.save()
'''

"""
Approve Record is for recording the approval of items
"""


class Approve_Record(models.Model):
    Item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="Approval")
    Approval_Admin = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="Approval")
    Approval_Date = models.DateField(default=timezone.now)
    Approval_Status = models.IntegerField(default=0)
    # When return the item, admin might upload file to uploader.
    Approval_File = models.FileField(upload_to='approval_files/', null=True, blank=True)
    # When reject the item, admin might comment to uploader.
    Approval_Comment = models.TextField(null=True, blank=True)

    def __str__(self) -> str:
        return "Approval " + str(self.Item)

    @classmethod
    def create(cls, item, admin, status, file, comment):
        approval = cls(Item=item, Approval_Admin=admin, Approval_Status=status, Approval_File=file,
                       Approval_Comment=comment)
        return approval

#class HelpPage(models.Model):
    #content = models.TextField(help_text="Editable content for the Help Page.")
    #last_updated = models.DateTimeField(auto_now=True)

    #def __str__(self):
        #return "Help Page Content"
