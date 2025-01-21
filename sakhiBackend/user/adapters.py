from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class PostgreSQLAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        """
        Custom logic to save the user data in a PostgreSQL database.
        """
        # Call the parent method to handle the standard saving process
        user = super().save_user(request, user, form, commit=False)

        # Add any additional customizations here if needed
        if commit:
            user.save()  # Save the user to the PostgreSQL database

        return user
