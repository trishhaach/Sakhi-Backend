from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class MongoAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        # Custom logic to save the user data
        user = super().save_user(request, user, form, commit=False)
        user.save()  # Save the user to the database (PostgreSQL)
        return user
