# General Description: Online Cinema
An online cinema is a digital platform that allows users to select, watch, and purchase access to movies and other video materials via the internet. These services have become popular due to their convenience, a wide selection of content, and the ability to personalize the user experience.

# Key Features of Online Cinema
## 1. Authorization and Authentication
- **User Registration:**
    - Users should be able to register using their email. After registration, an email is sent with a link to activate their account. If the user does not activate their account within 24 hours, the link becomes invalid.
    - If the user fails to activate their account within 24 hours, they should have the option to enter their email to receive a new activation link, valid for another 24 hours.
    - Use celery-beat to periodically delete expired activation tokens.
    - Ensure email uniqueness before registration.
- **Login and Logout:**
    - Provide a logout feature that deletes the user's JWT token, making it unusable for further logins.
- **Password Management:**
    - Users can change their password if they remember the old one by entering the old password and a new password.
    - Users who forget their password can enter their email. If the email is registered and active, a reset link is sent, allowing them to set a new password without confirming the old one.
    - Enforce password complexity validation.
- **JWT Token Management:**
    - Users receive a pair of JWT tokens (access and refresh) upon login.
    - Users can use the refresh token to obtain a new access token with a shorter time-to-live (TTL).
- **User Groups:**
    - Create three user groups:
        - **User:** Access to the basic user interface.
        - **Moderator:** In addition to catalog and user interface access, can manage movies on the site through the admin panel, view sales, etc.
        - **Admin:** Inherits all permissions from the above roles and can manage users, change group memberships, and manually activate accounts.

**Entities and Their Attributes**

**UserGroupEnum (enum)** Enumeration of possible user groups (roles):
- **USER:** A regular user with basic interface access.
- **MODERATOR:** A user who, in addition to the basic interface, can manage content (e.g., movies), view sales, and perform some administrative tasks.
- **ADMIN:** A user with extended rights. Can manage other users, change their groups, and manually activate accounts.

**GenderEnum (enum)** Enumeration for storing a user’s gender:
- **MAN**
- **WOMAN**

This field is optional.

**UserGroup (user_groups table)** Stores user groups. **Attributes:**
- `id`: Primary key (int).
- `name`: Name of the group (USER, MODERATOR, ADMIN), unique field.

**Relationships:**
- One-to-many: One `UserGroup` can be related to many `User` records.

**User (users table)** Represents registered users. **Attributes:**
- `id`: Primary key (int).
- `email`: User’s email, unique and required, used for login and identification.
- `hashed_password`: User’s password hash, stored securely (not in plain text).
- `is_active`: Boolean field indicating whether the account is activated. Initially `False`, becomes `True` after activation.
- `created_at`: Timestamp of when the user was created.
- `updated_at`: Timestamp of the user’s last data update.
- `group_id`: Foreign key referencing `UserGroup`, indicating the group the user belongs to (User, Moderator, Admin).

**Relationships:**
- One-to-many with `UserGroup` (via `group_id`): Each user belongs to exactly one group.
- One-to-one with `UserProfile`: Each user can have one profile with additional information.
- One-to-many with `ActivationToken`, `PasswordResetToken`, `RefreshToken`.

**UserProfile (user_profiles table)** Additional user information. **Attributes:**
- `id`: Primary key (int).
- `user_id`: Foreign key referencing `users`. Unique, ensuring a one-to-one relationship with `User`.
- `first_name`: User’s first name (optional).
- `last_name`: User’s last name (optional).
- `avatar`: A link or identifier for the user’s avatar (e.g., a key in S3 storage).
- `gender`: Gender (MAN/WOMAN), optional.
- `date_of_birth`: Date of birth, optional.
- `info`: A text field for a short bio or additional user info.

**Relationships:**
- One-to-one with `User`.

**ActivationToken (activation_tokens table)** A token for account activation, sent to the user’s email after registration. **Attributes:**
- `id`: Primary key (int).
- `user_id`: Foreign key referencing `users`. Unique, ensuring a one-to-one relationship with `User`.
- `token`: A unique token.
- `expires_at`: The token’s expiration time (24 hours after issuance).

**Tasks:**
- Create a new `ActivationToken` upon registration.
- If the user does not activate their account within 24 hours, the token becomes invalid.
- Allow resending a new token if the old one expires.
- Use `celery-beat` to periodically remove expired tokens.

**PasswordResetToken (password_reset_tokens table)** A token for resetting a forgotten password, sent to the user’s email upon request. **Attributes:**
- `id`: Primary key (int).
- `user_id`: Foreign key referencing `users`. Unique, ensuring a one-to-one relationship with `User`.
- `token`: A unique password reset token.
- `expires_at`: The token’s expiration time.

**Tasks:**
- If a user forgets their password, generate and send a reset token via email.
- With this token, the user can set a new password without knowing the old one.
- Check the token’s validity period.

**RefreshToken (refresh_tokens table)** A refresh token to obtain a new access token without re-entering login credentials. **Attributes:**
- `id`: Primary key (int).
- `user_id`: Foreign key referencing `users`.
- `token`: A unique refresh token.
- `expires_at`: The refresh token’s expiration time.

**Tasks:**
- On login, the user receives a pair of tokens: access and refresh.
- When the access token expires, the user can use the refresh token to get a new access token.
- On logout, the refresh token is deleted, preventing further use.

**Functional Requirements (Summary):**
- Registration with an activation email.
- Account activation using the received token.
- Resending the activation token if the previous one expires.
- Use `celery-beat` to periodically remove expired tokens.
- Login that issues JWT tokens (access and refresh).
- Logout that revokes the refresh token.
- Password reset with a token sent via email.
- Enforce password complexity checks when changing or setting a new password.
- User groups (User, Moderator, Admin) with different sets of permissions.
- Allow administrators to change a user’s group and manually activate accounts.

**DB schema**
- [Accounts DB schema](https://dbdiagram.io/d/Accounts-app-675ef6bee763df1f00fd8ed1)
