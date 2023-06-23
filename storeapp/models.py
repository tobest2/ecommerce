from django.db import models
from io import BytesIO
from PIL import Image
from django.contrib.auth.models import User
from django.core.files import File
from email.policy import default
import uuid
from  django.conf import settings
# from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
import cloudinary
from cloudinary.models import CloudinaryField

class Category(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, unique=True)

    class Meta:
        ordering = ('name',)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return f'/{self.slug}/'


class Review(models.Model):
    product = models.ForeignKey("Product", on_delete=models.CASCADE, related_name = "reviews")
    date_created = models.DateTimeField(auto_now_add=True)
    description = models.TextField(default="description")
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.description  


class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='product_creator')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='images/')
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)
    slug = models.SlugField(max_length=255)
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, unique=True)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    in_stock = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Products'
        ordering = ('-created',)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/{self.category.slug}/{self.slug}/'

    def get_image(self):

        if self.image:
            return '' + self.image.url
        return ''

    # def get_thumbnail(self):
    #     if self.thumbnail:
    #         return self.thumbnail.url
    #     else:
    #         if self.image:
    #             self.thumbnail = self.make_thumbnail(self.image)
    #             self.save()
    #
    #             return self.thumbnail.url
    #         else:
    #             return ''

    # def get_thumbnail(self):
    #     if self.thumbnail:
    #         return self.thumbnail.url
    #     else:
    #         if self.image:
    #             self.thumbnail = self.make_thumbnail(self.image)
    #             self.save()
    #             return self.thumbnail.url if self.thumbnail else ''
    #         else:
    #             return ''

    def get_thumbnail(self):
        if self.thumbnail:
            return self.extract_secure_url(self.thumbnail.url)
        else:
            if self.image:
                self.thumbnail = self.make_thumbnail(self.image)
                self.save()
                return self.extract_secure_url(self.thumbnail.url) if self.thumbnail else ''
            else:
                return ''

    def extract_secure_url(self, url):
        return url.split('/media/')[1]
    def make_thumbnail(self, image, size=(300, 200)):
        img = Image.open(image)
        img.convert('RGB')
        img.thumbnail(size)

        thumb_io = BytesIO()
        img.save(thumb_io, 'JPEG', quality=90)
        thumb_io.seek(0)

        thumbnail_data = thumb_io.read()

        thumbnail = cloudinary.uploader.upload(thumbnail_data, folder='thumbnails')

        return thumbnail['secure_url']
    # def make_thumbnail(self, image, size=(300, 200)):
    #     img = Image.open(image)
    #     img.convert('RGB')
    #     img.thumbnail(size)
    #
    #     thumb_io = BytesIO()
    #     img.save(thumb_io, 'JPEG', quality=85)
    #
    #     thumbnail = File(thumb_io, name=image.name)
    #
    #     return thumbnail
    # def get_thumbnail(self):
    #     if self.thumbnail:
    #         thumbnail_url = self.thumbnail.url
    #
    #         # Open the image using PIL
    #         image = Image.open(self.thumbnail)
    #
    #         # Define the maximum thumbnail size (e.g., maximum width of 100 pixels)
    #         max_thumbnail_width = 100
    #
    #         # Calculate the aspect ratio
    #         aspect_ratio = image.width / image.height
    #
    #         # Calculate the maximum thumbnail height based on the aspect ratio
    #         max_thumbnail_height = int(max_thumbnail_width / aspect_ratio)
    #
    #         # Resize the image while preserving the aspect ratio
    #         image.thumbnail((max_thumbnail_width, max_thumbnail_height))
    #
    #         # Create a file-like object to store the resized image
    #         thumbnail_file = BytesIO()
    #         image.save(thumbnail_file, format='JPEG')
    #
    #         # Create an InMemoryUploadedFile from the file-like object
    #         thumbnail = InMemoryUploadedFile(
    #             thumbnail_file,
    #             None,
    #             f"{self.thumbnail.name.split('.')[0]}.jpg",
    #             'image/jpeg',
    #             thumbnail_file.tell,
    #             None
    #         )
    #
    #         # Save the resized thumbnail in the same field
    #         self.thumbnail = thumbnail
    #
    #         return thumbnail_url
    #
    #     return ''
    #


class Order(models.Model):
    user = models.ForeignKey(User, related_name='orders', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='pending')
    tx_ref = models.CharField(max_length=255, blank=True, null=True)
    paid_amount = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)

    class Meta:
        ordering = ['-created_at',]
    
    def __str__(self):
        return str(self.user)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='items', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.IntegerField(default=1)
    delivery_status = models.CharField(max_length=20, default='Not Shipped')

    def __str__(self):
        return '%s' % self.id