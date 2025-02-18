from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.contrib.auth import get_user_model
from datetime import datetime
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    def create_user(self, email, name, password=None):
        if not email:
            raise ValueError("The Email field must be set")
        user = self.model(email=email, name=name)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None):
        user = self.create_user(email, name, password)
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin

class NonClinicalDetection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    skin_darkening = models.IntegerField(choices=[(0, 'No'), (1, 'Yes')])
    hair_growth = models.IntegerField(choices=[(0, 'No'), (1, 'Yes')])
    weight_gain = models.IntegerField(choices=[(0, 'No'), (1, 'Yes')])
    cycle_length = models.IntegerField()
    fast_food = models.FloatField()
    pimples = models.IntegerField(choices=[(0, 'No'), (1, 'Yes')])
    age = models.IntegerField()
    bmi = models.FloatField()
    prediction = models.CharField(max_length=255, null=True, blank=True)  # Store the prediction result
    prediction_probability = models.FloatField(null=True, blank=True)  # Store the prediction probability

    def __str__(self):
        return f"Non-Clinical Detection for {self.user.name}"


class AdvancedDetection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    follicle_no_r = models.IntegerField()
    follicle_no_l = models.IntegerField()
    skin_darkening = models.IntegerField(choices=[(0, 'No'), (1, 'Yes')])
    hair_growth = models.IntegerField(choices=[(0, 'No'), (1, 'Yes')])
    weight_gain = models.IntegerField(choices=[(0, 'No'), (1, 'Yes')])
    cycle_length = models.IntegerField()
    amh = models.FloatField()
    fast_food = models.FloatField()
    cycle_r_i = models.IntegerField(choices=[(0, 'Irregular'), (1, 'Regular')])
    fsh_lh = models.FloatField()
    prl = models.FloatField()
    pimples = models.IntegerField(choices=[(0, 'No'), (1, 'Yes')])
    age = models.IntegerField()
    bmi = models.FloatField()
    prediction = models.CharField(max_length=255, null=True, blank=True)  # Store the prediction result

    def __str__(self):
        return f"Advanced Detection for {self.user.name}"
    
class Period(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    period_date = models.DateField()
    
    def __str__(self):
        return f"User: {self.user.name}, Period Date: {self.period_date}"

    class Meta:
        ordering = ['period_date']


class SymptomCategory(models.Model):
    """Categories for symptoms."""
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Symptom(models.Model):
    """This model stores different types of symptoms."""
    name = models.CharField(max_length=100)
    category = models.ForeignKey(SymptomCategory, on_delete=models.CASCADE, related_name="symptoms")

    def __str__(self):
        return self.name


class SymptomTrack(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    period = models.ForeignKey(Period, on_delete=models.CASCADE)
    symptom = models.ForeignKey(Symptom, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Symptom {self.symptom.name} for {self.user.name} on {self.period.period_date}"

    class Meta:
        unique_together = ('user', 'period', 'symptom')  # Prevent the same user from logging the same symptom twice in the same period