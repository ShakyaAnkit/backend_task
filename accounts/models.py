from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


# Create your models here.
class DateTimeModel(models.Model):
	created_at = models.DateTimeField(auto_now_add=True, auto_now=False,)
	updated_at = models.DateTimeField(auto_now_add=False, auto_now=True,)
	deleted_at = models.DateTimeField(null=True, blank=True)
	
	class Meta:
		abstract = True

	def delete(self, hard=False):
		if not hard:
			self.deleted_at = timezone.now()
			super().save(update_fields=['deleted_at'])
		else:
			super().delete()

class Document(DateTimeModel):
	file = models.FileField(upload_to='documents')

	class Meta:
		ordering = ('-id',)

	def __str__(self):
		return '{}, Size: {}{}, Image: {}'.format(self.file.name, self.file_size, self.file_type, self.is_image)

	def get_human_readable_size(self):
		size = self.file.size
		for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
			if size < 1024.0 or unit == 'PB':
				break
			size /= 1024.0
		return (round(size, 2), unit)

	@property
	def is_image(self):
		return self.file.url.split('.')[-1].lower() in ['jpeg', 'jpg', 'png', 'gif']

	@property
	def file_size(self):
		return self.get_human_readable_size()[0]

	@property
	def file_type(self):
		return self.get_human_readable_size()[1]

	@property
	def file_name(self):
		return self.file.name.replace('documents/', '')

class Interest(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'Interest'
        verbose_name_plural = 'Interests'

    def __str__(self):
        return self.name

class Location(models.Model):
    latitude = models.DecimalField(max_digits=10, decimal_places=8)
    longitude = models.DecimalField(max_digits=10, decimal_places=8)

    class Meta:
        verbose_name = 'Location'
        verbose_name_plural = 'Locations'

    def str(self):
        return '{}-{}'.format(self.latitude, self.longitude)

class Account(User):
	country = models.CharField(max_length=255)
	bio = models.TextField(null=True, blank=True)
	phone_number = models.CharField(max_length=255, unique=True, null=True, blank=True)
	areas_of_interest = models.ManyToManyField(Interest, related_name='account', blank=True)
	user_documents = models.ManyToManyField(Document, related_name='account', blank=True)
	date_of_birth = models.DateField()
	location_of_home = models.ForeignKey(Location, related_name='accounts_home', null=True, blank=True, on_delete=models.SET_NULL)
	location_of_office = models.ForeignKey(Location, related_name='accounts_office', null=True, blank=True, on_delete=models.SET_NULL)

	class Meta:
		verbose_name = 'Account'
		verbose_name_plural = 'Accounts'

	def save(self, *args, **kwargs):
		self.username = self.email
		return super().save(*args, **kwargs)

	def __str__(self):
		return self.username