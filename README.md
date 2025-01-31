<div class="markdown"><a href="#general-description-online-cinema" target="_self" rel="noreferrer"><span class="icon icon-link"></span></a><h1 id="general-description-online-cinema" level="1" sourceposition="[object Object]" index="1" siblingcount="110" node="[object Object]"><strong>General Description: Online Cinema</strong></h1>
<p>An online cinema is a digital platform that allows users to select, watch, and purchase access to movies and other video materials via the internet. These services have become popular due to their convenience, a wide selection of content, and the ability to personalize the user experience.</p>
<a href="#key-features-of-online-cinema" target="_self" rel="noreferrer"><span class="icon icon-link"></span></a><h1 id="key-features-of-online-cinema" level="1" sourceposition="[object Object]" index="4" siblingcount="110" node="[object Object]"><strong>Key Features of Online Cinema</strong></h1>
<a href="#1-authorization-and-authentication" target="_self" rel="noreferrer"><span class="icon icon-link"></span></a><h2 id="1-authorization-and-authentication" level="2" sourceposition="[object Object]" index="6" siblingcount="110" node="[object Object]"><strong>1. Authorization and Authentication</strong></h2>
<ul>
<li>
<p><strong>User Registration:</strong></p>
<ul>
<li>Users should be able to register using their email. After registration, an email is sent with a link to activate their account. If the user does not activate their account within 24 hours, the link becomes invalid.</li>
<li>If the user fails to activate their account within 24 hours, they should have the option to enter their email to receive a new activation link, valid for another 24 hours.</li>
<li>Use <code>celery-beat</code> to periodically delete expired activation tokens.</li>
<li>Ensure email uniqueness before registration.</li>
</ul>
</li>
<li>
<p><strong>Login and Logout:</strong></p>
<ul>
<li>Provide a logout feature that deletes the user's JWT token, making it unusable for further logins.</li>
</ul>
</li>
<li>
<p><strong>Password Management:</strong></p>
<ul>
<li>Users can change their password if they remember the old one by entering the old password and a new password.</li>
<li>Users who forget their password can enter their email. If the email is registered and active, a reset link is sent, allowing them to set a new password without confirming the old one.</li>
<li>Enforce password complexity validation.</li>
</ul>
</li>
<li>
<p><strong>JWT Token Management:</strong></p>
<ul>
<li>Users receive a pair of JWT tokens (access and refresh) upon login.</li>
<li>Users can use the refresh token to obtain a new access token with a shorter time-to-live (TTL).</li>
</ul>
</li>
<li>
<p><strong>User Groups:</strong></p>
<ul>
<li>Create three user groups:
<ul>
<li><strong>User:</strong> Access to the basic user interface.</li>
<li><strong>Moderator:</strong> In addition to catalog and user interface access, can manage movies on the site through the admin panel, view sales, etc.</li>
<li><strong>Admin:</strong> Inherits all permissions from the above roles and can manage users, change group memberships, and manually activate accounts.</li>
</ul>
</li>
</ul>
</li>
</ul>
<p><strong>Entities and Their Attributes</strong></p>
<p><strong>UserGroupEnum (enum)</strong>
Enumeration of possible user groups (roles):</p>
<ul>
<li><strong>USER:</strong> A regular user with basic interface access.</li>
<li><strong>MODERATOR:</strong> A user who, in addition to the basic interface, can manage content (e.g., movies), view sales, and perform some administrative tasks.</li>
<li><strong>ADMIN:</strong> A user with extended rights. Can manage other users, change their groups, and manually activate accounts.</li>
</ul>
<p><strong>GenderEnum (enum)</strong>
Enumeration for storing a user’s gender:</p>
<ul>
<li><strong>MAN</strong></li>
<li><strong>WOMAN</strong></li>
</ul>
<p>This field is optional.</p>
<p><strong>UserGroup (user_groups table)</strong>
Stores user groups.
<strong>Attributes:</strong></p>
<ul>
<li><code>id</code>: Primary key (int).</li>
<li><code>name</code>: Name of the group (USER, MODERATOR, ADMIN), unique field.</li>
</ul>
<p><strong>Relationships:</strong></p>
<ul>
<li>One-to-many: One <code>UserGroup</code> can be related to many <code>User</code> records.</li>
</ul>
<p><strong>User (users table)</strong>
Represents registered users.
<strong>Attributes:</strong></p>
<ul>
<li><code>id</code>: Primary key (int).</li>
<li><code>email</code>: User’s email, unique and required, used for login and identification.</li>
<li><code>hashed_password</code>: User’s password hash, stored securely (not in plain text).</li>
<li><code>is_active</code>: Boolean field indicating whether the account is activated. Initially <code>False</code>, becomes <code>True</code> after activation.</li>
<li><code>created_at</code>: Timestamp of when the user was created.</li>
<li><code>updated_at</code>: Timestamp of the user’s last data update.</li>
<li><code>group_id</code>: Foreign key referencing <code>UserGroup</code>, indicating the group the user belongs to (User, Moderator, Admin).</li>
</ul>
<p><strong>Relationships:</strong></p>
<ul>
<li>One-to-many with <code>UserGroup</code> (via <code>group_id</code>): Each user belongs to exactly one group.</li>
<li>One-to-one with <code>UserProfile</code>: Each user can have one profile with additional information.</li>
<li>One-to-many with <code>ActivationToken</code>, <code>PasswordResetToken</code>, <code>RefreshToken</code>.</li>
</ul>
<p><strong>UserProfile (user_profiles table)</strong>
Additional user information.
<strong>Attributes:</strong></p>
<ul>
<li><code>id</code>: Primary key (int).</li>
<li><code>user_id</code>: Foreign key referencing <code>users</code>. Unique, ensuring a one-to-one relationship with <code>User</code>.</li>
<li><code>first_name</code>: User’s first name (optional).</li>
<li><code>last_name</code>: User’s last name (optional).</li>
<li><code>avatar</code>: A link or identifier for the user’s avatar (e.g., a key in S3 storage).</li>
<li><code>gender</code>: Gender (MAN/WOMAN), optional.</li>
<li><code>date_of_birth</code>: Date of birth, optional.</li>
<li><code>info</code>: A text field for a short bio or additional user info.</li>
</ul>
<p><strong>Relationships:</strong></p>
<ul>
<li>One-to-one with <code>User</code>.</li>
</ul>
<p><strong>ActivationToken (activation_tokens table)</strong>
A token for account activation, sent to the user’s email after registration.
<strong>Attributes:</strong></p>
<ul>
<li><code>id</code>: Primary key (int).</li>
<li><code>user_id</code>: Foreign key referencing <code>users</code>. Unique, ensuring a one-to-one relationship with <code>User</code>.</li>
<li><code>token</code>: A unique token.</li>
<li><code>expires_at</code>: The token’s expiration time (24 hours after issuance).</li>
</ul>
<p><strong>Tasks:</strong></p>
<ul>
<li>Create a new <code>ActivationToken</code> upon registration.</li>
<li>If the user does not activate their account within 24 hours, the token becomes invalid.</li>
<li>Allow resending a new token if the old one expires.</li>
<li>Use <code>celery-beat</code> to periodically remove expired tokens.</li>
</ul>
<p><strong>PasswordResetToken (password_reset_tokens table)</strong>
A token for resetting a forgotten password, sent to the user’s email upon request.
<strong>Attributes:</strong></p>
<ul>
<li><code>id</code>: Primary key (int).</li>
<li><code>user_id</code>: Foreign key referencing <code>users</code>. Unique, ensuring a one-to-one relationship with <code>User</code>.</li>
<li><code>token</code>: A unique password reset token.</li>
<li><code>expires_at</code>: The token’s expiration time.</li>
</ul>
<p><strong>Tasks:</strong></p>
<ul>
<li>If a user forgets their password, generate and send a reset token via email.</li>
<li>With this token, the user can set a new password without knowing the old one.</li>
<li>Check the token’s validity period.</li>
</ul>
<p><strong>RefreshToken (refresh_tokens table)</strong>
A refresh token to obtain a new access token without re-entering login credentials.
<strong>Attributes:</strong></p>
<ul>
<li><code>id</code>: Primary key (int).</li>
<li><code>user_id</code>: Foreign key referencing <code>users</code>.</li>
<li><code>token</code>: A unique refresh token.</li>
<li><code>expires_at</code>: The refresh token’s expiration time.</li>
</ul>
<p><strong>Tasks:</strong></p>
<ul>
<li>On login, the user receives a pair of tokens: access and refresh.</li>
<li>When the access token expires, the user can use the refresh token to get a new access token.</li>
<li>On logout, the refresh token is deleted, preventing further use.</li>
</ul>
<p><strong>Functional Requirements (Summary):</strong></p>
<ul>
<li>Registration with an activation email.</li>
<li>Account activation using the received token.</li>
<li>Resending the activation token if the previous one expires.</li>
<li>Use <code>celery-beat</code> to periodically remove expired tokens.</li>
<li>Login that issues JWT tokens (access and refresh).</li>
<li>Logout that revokes the refresh token.</li>
<li>Password reset with a token sent via email.</li>
<li>Enforce password complexity checks when changing or setting a new password.</li>
<li>User groups (User, Moderator, Admin) with different sets of permissions.</li>
<li>Allow administrators to change a user’s group and manually activate accounts.</li>
</ul>
<p><strong>DB schema</strong></p>
<ul>
<li><a href="https://dbdiagram.io/d/Accounts-app-675ef6bee763df1f00fd8ed1" target="_blank" rel="noreferrer">Accounts DB schema</a></li>
</ul>
<hr>
<a href="#2-movies" target="_self" rel="noreferrer"><span class="icon icon-link"></span></a><h2 id="2-movies" level="2" sourceposition="[object Object]" index="44" siblingcount="110" node="[object Object]"><strong>2. Movies</strong></h2>
<ul>
<li>
<p><strong>User Functionality:</strong></p>
<ul>
<li>Browse the movie catalog with pagination.</li>
<li>View detailed descriptions of movies.</li>
<li>Like or dislike movies.</li>
<li>Write comments on movies.</li>
<li>Filter movies by various criteria (e.g., release year, IMDb rating).</li>
<li>Sort movies by different attributes (e.g., price, release date, popularity).</li>
<li>Search for movies by title, description, actor, or director.</li>
<li>Add movies to favorites and perform all catalog functions (search, filter, sort) on the favorites list.</li>
<li>Remove movies from favorites.</li>
<li>View a list of genres with the count of movies in each. Clicking on a genre shows all related movies.</li>
<li>Rate movies on a 10-point scale.</li>
<li>Notify users when their comments receive replies or likes.</li>
</ul>
</li>
<li>
<p><strong>Moderator Functionality:</strong></p>
<ul>
<li>Perform CRUD operations on movies, genres, and actors.</li>
<li>Prevent the deletion of a movie if at least one user has purchased it.</li>
</ul>
</li>
</ul>
<p><strong>Entities and Their Attributes</strong></p>
<ol>
<li>
<p><strong>Genre (genres table)</strong>
Represents a movie genre (e.g., Action, Drama, Comedy).
<strong>Attributes:</strong></p>
<ul>
<li><code>id</code>: Primary key (int), auto-incremented.</li>
<li><code>name</code>: The genre’s name (e.g., "Action"). Must be unique and not null.</li>
</ul>
<p><strong>Relationships:</strong></p>
<ul>
<li>Many-to-many with <code>Movie</code> through the <code>movie_genres</code> association table. A single genre can be associated with multiple movies, and a single movie can belong to multiple genres.</li>
</ul>
</li>
<li>
<p><strong>Star (stars table)</strong>
Represents an actor or actress starring in a movie.
<strong>Attributes:</strong></p>
<ul>
<li><code>id</code>: Primary key (int), auto-incremented.</li>
<li><code>name</code>: The star’s name. Must be unique and not null.</li>
</ul>
<p><strong>Relationships:</strong></p>
<ul>
<li>Many-to-many with <code>Movie</code> through the <code>movie_stars</code> association table. A star can appear in multiple movies, and a movie can have multiple stars.</li>
</ul>
</li>
<li>
<p><strong>Director (directors table)</strong>
Represents a movie director.
<strong>Attributes:</strong></p>
<ul>
<li><code>id</code>: Primary key (int), auto-incremented.</li>
<li><code>name</code>: The director’s name. Must be unique and not null.</li>
</ul>
<p><strong>Relationships:</strong></p>
<ul>
<li>Many-to-many with <code>Movie</code> through the <code>movie_directors</code> association table. A director can direct multiple movies, and a movie can have multiple directors.</li>
</ul>
</li>
<li>
<p><strong>Certification (certifications table)</strong>
Represents the rating or certification of a movie (e.g., PG-13, R).
<strong>Attributes:</strong></p>
<ul>
<li><code>id</code>: Primary key (int), auto-incremented.</li>
<li><code>name</code>: The certification name. Must be unique and not null (e.g., "PG-13").</li>
</ul>
<p><strong>Relationships:</strong></p>
<ul>
<li>One-to-many with <code>Movie</code>: One certification can be applied to many movies, but each movie has exactly one certification.</li>
</ul>
</li>
<li>
<p><strong>Movie (movies table)</strong>
Represents a movie’s main data.
<strong>Attributes:</strong></p>
<ul>
<li><code>id</code>: Primary key (int), auto-incremented.</li>
<li><code>uuid</code>: A unique UUID for the movie, ensuring global uniqueness.</li>
<li><code>name</code>: The movie’s title (string, not null).</li>
<li><code>year</code>: The release year (int, not null).</li>
<li><code>time</code>: The movie’s duration in minutes (int, not null).</li>
<li><code>imdb</code>: The movie’s IMDb rating (float, not null).</li>
<li><code>votes</code>: The number of votes on IMDb (int, not null).</li>
<li><code>meta_score</code>: Metascore (float, optional).</li>
<li><code>gross</code>: Gross revenue (float, optional).</li>
<li><code>description</code>: A textual description or synopsis (text, not null).</li>
<li><code>price</code>: The price of the movie (DECIMAL(10,2)).</li>
<li><code>certification_id</code>: Foreign key to <code>certifications.id</code> (int, not null). This field ensures that the movie’s rating is always defined.</li>
</ul>
<p><strong>Constraints:</strong></p>
<ul>
<li>A unique constraint on <code>(name, year, time)</code>, ensuring that the combination of title, release year, and duration uniquely identifies a movie.</li>
</ul>
<p><strong>Relationships:</strong></p>
<ul>
<li>Many-to-one with <code>Certification</code> (via <code>certification_id</code>): Each movie has one certification.</li>
<li>Many-to-many with <code>Genre</code> (via <code>movie_genres</code>): A movie can belong to multiple genres.</li>
<li>Many-to-many with <code>Director</code> (via <code>movie_directors</code>): A movie can have multiple directors.</li>
<li>Many-to-many with <code>Star</code> (via <code>movie_stars</code>): A movie can feature multiple stars.</li>
</ul>
</li>
</ol>
<p><strong>Association Tables</strong></p>
<ul>
<li>
<p><strong>movie_genres</strong>: Connects <code>Movie</code> and <code>Genre</code> (many-to-many).
<strong>Columns:</strong></p>
<ul>
<li><code>movie_id</code>: Foreign key to <code>movies.id</code>, part of composite primary key.</li>
<li><code>genre_id</code>: Foreign key to <code>genres.id</code>, part of composite primary key.</li>
</ul>
</li>
<li>
<p><strong>movie_directors</strong>: Connects <code>Movie</code> and <code>Director</code> (many-to-many).
<strong>Columns:</strong></p>
<ul>
<li><code>movie_id</code>: Foreign key to <code>movies.id</code>, part of composite primary key.</li>
<li><code>director_id</code>: Foreign key to <code>directors.id</code>, part of composite primary key.</li>
</ul>
</li>
<li>
<p><strong>movie_stars</strong>: Connects <code>Movie</code> and <code>Star</code> (many-to-many).
<strong>Columns:</strong></p>
<ul>
<li><code>movie_id</code>: Foreign key to <code>movies.id</code>, part of composite primary key.</li>
<li><code>star_id</code>: Foreign key to <code>stars.id</code>, part of composite primary key.</li>
</ul>
</li>
</ul>
<p><strong>DB schema</strong></p>
<ul>
<li><a href="https://dbdiagram.io/d/Movies-app-675f03b9e763df1f00fe4769" target="_blank" rel="noreferrer">Movies DB schema</a></li>
</ul>
<hr>
<a href="#3-shopping-cart" target="_self" rel="noreferrer"><span class="icon icon-link"></span></a><h2 id="3-shopping-cart" level="2" sourceposition="[object Object]" index="54" siblingcount="110" node="[object Object]"><strong>3. Shopping Cart</strong></h2>
<ul>
<li>
<p><strong>User Functionality:</strong></p>
<ul>
<li>Users can add movies to the cart if they have not been purchased yet.</li>
<li>If the movie has already been purchased, a notification is displayed, indicating that repeat purchases are not allowed.</li>
<li>Users can remove movies from the cart if they decide not to proceed with the purchase.</li>
<li>Users can view a list of movies in their cart.</li>
<li>For each movie in the cart, the title, price, genre, and release year are displayed.</li>
<li>Users can pay for all movies in the cart at once.</li>
<li>After successful payment, movies are moved to the "Purchased" list.</li>
<li>Users can manually clear the cart entirely.</li>
<li><strong>Validation:</strong>
<ul>
<li>Ensure all movies are available for purchase before creating an order.</li>
<li>Exclude movies already purchased, notifying the user.</li>
<li>Prompt unregistered users to sign up before completing a purchase.</li>
<li>Prevent adding the same movie to the cart more than once.</li>
</ul>
</li>
</ul>
</li>
<li>
<p><strong>Moderator Functionality:</strong></p>
<ul>
<li>Admins can view the contents of users' carts for analysis or troubleshooting.</li>
<li>Notify moderators when attempting to delete a movie that exists in users' carts.</li>
</ul>
</li>
</ul>
<p>Below is a detailed description of the entities and their attributes for the <strong>Shopping Cart</strong> functionality. These entities assume that <code>User</code> and <code>Movie</code> are defined elsewhere and are imported into this module.</p>
<p><strong>Entities and Their Attributes</strong></p>
<ol>
<li>
<p><strong>Cart (carts table)</strong>
Represents a user's shopping cart. Each user can have exactly one cart.
<strong>Attributes:</strong></p>
<ul>
<li><code>id</code>: Primary key (int), auto-incremented.</li>
<li><code>user_id</code>: Foreign key referencing <code>users.id</code>, not null and unique, ensuring a one-to-one relationship with the user.</li>
</ul>
<p><strong>Relationships:</strong></p>
<ul>
<li>One-to-one with <code>User</code>: Each user has exactly one <code>Cart</code>, and each <code>Cart</code> belongs to one <code>User</code>.</li>
<li>One-to-many with <code>CartItem</code>: A cart can contain multiple cart items.</li>
</ul>
<p><strong>Key Points:</strong></p>
<ul>
<li>The unique constraint on <code>user_id</code> guarantees that each user can have only one cart.</li>
<li>Acts as a container for <code>CartItem</code> records.</li>
</ul>
</li>
<li>
<p><strong>CartItem (cart_items table)</strong>
Represents a single item (movie) placed in a user's cart.
<strong>Attributes:</strong></p>
<ul>
<li><code>id</code>: Primary key (int), auto-incremented.</li>
<li><code>cart_id</code>: Foreign key referencing <code>carts.id</code>, not null, indicating which cart the item belongs to.</li>
<li><code>movie_id</code>: Foreign key referencing <code>movies.id</code>, not null, indicating which movie is added to the cart.</li>
<li><code>added_at</code>: Timestamp of when the movie was added to the cart, defaults to the current time.</li>
</ul>
<p><strong>Relationships:</strong></p>
<ul>
<li>Many-to-one with <code>Cart</code>: Each <code>CartItem</code> belongs to exactly one <code>Cart</code>.</li>
<li>Optionally, a many-to-one relationship with <code>Movie</code> can be defined if needed. Each <code>CartItem</code> references exactly one <code>Movie</code>.</li>
</ul>
<p><strong>Constraints:</strong></p>
<ul>
<li>A unique constraint on <code>(cart_id, movie_id)</code> ensures that the same movie cannot be added to a single cart more than once.</li>
</ul>
</li>
</ol>
<p><strong>Summary of Relationships</strong></p>
<ul>
<li><strong>User - Cart (1:1)</strong>: Each user can have one unique cart.</li>
<li><strong>Cart - CartItem (1:n)</strong>: One cart can have many cart items.</li>
<li><strong>CartItem - Movie (n:1)</strong> (optional explicit relationship): Each cart item represents a single movie.</li>
</ul>
<p><strong>Functional Implications</strong></p>
<ul>
<li>A <code>User</code> can manage their cart (add, remove, or clear items).</li>
<li>A <code>Cart</code> ensures centralized management of all items a user wants to purchase.</li>
<li>The <code>CartItem</code> model enforces uniqueness of movies in a user's cart and tracks when items were added, which can be useful for UI features or analytics.</li>
</ul>
<p><strong>DB schema</strong></p>
<ul>
<li><a href="https://dbdiagram.io/d/Cart-app-675f0d88e763df1f00fed027" target="_blank" rel="noreferrer">Cart DB schema</a></li>
</ul>
<hr>
<a href="#4-order" target="_self" rel="noreferrer"><span class="icon icon-link"></span></a><h2 id="4-order" level="2" sourceposition="[object Object]" index="67" siblingcount="110" node="[object Object]"><strong>4. Order</strong></h2>
<ul>
<li>
<p><strong>User Functionality:</strong></p>
<ul>
<li>Users can place orders for movies in their cart.</li>
<li>If movies are unavailable (e.g., deleted, region-locked), they are excluded from the order with a notification to the user.</li>
<li>Users can view a list of all their orders.</li>
<li>For each order, the following details are displayed:
<ul>
<li>Date and time.</li>
<li>List of movies included.</li>
<li>Total amount.</li>
<li>Order status (paid, canceled, pending).</li>
</ul>
</li>
<li>After confirming an order, users are redirected to a payment gateway.</li>
<li>Users can cancel orders before payment is completed.</li>
<li>Once paid, orders can only be canceled via a refund request.</li>
<li>After successful payment, users receive an email confirmation.</li>
<li><strong>Validation:</strong>
<ul>
<li>Ensure the cart is not empty before placing an order.</li>
<li>Exclude movies already purchased by the user.</li>
<li>Ensure all movies in the order are available for purchase.</li>
<li>Check that no other orders with the same movies are already pending.</li>
<li>Revalidate the total amount before payment in case of price changes.</li>
</ul>
</li>
</ul>
</li>
<li>
<p><strong>Moderator Functionality:</strong></p>
<ul>
<li>Admins can view all user orders with filters for:
<ul>
<li>Users.</li>
<li>Dates.</li>
<li>Statuses (paid, canceled, etc.).</li>
</ul>
</li>
</ul>
</li>
</ul>
<p>Below is a detailed description of the <strong>Order</strong> and <strong>OrderItem</strong> entities and their attributes, including their relationships and significance within the ordering process.</p>
<p><strong>Entities and Their Attributes</strong></p>
<ol>
<li>
<p><strong>Order (orders table)</strong>
Represents a user's order containing one or more movies.</p>
<p><strong>Attributes:</strong></p>
<ul>
<li><code>id</code>: Primary key (int, auto-incremented).</li>
<li><code>user_id</code>: Foreign key referencing <code>users.id</code> (int, not null), indicating which user owns the order.</li>
<li><code>created_at</code>: The date and time the order was created (timestamp with time zone, defaults to the current time).</li>
<li><code>status</code>: The current status of the order. Stored as an enum with possible values:
<ul>
<li><code>pending</code>: The order has been placed but not paid yet.</li>
<li><code>paid</code>: The order has been successfully paid.</li>
<li><code>canceled</code>: The order has been canceled by the user or through another process.
Must not be null and defaults to <code>pending</code>.</li>
</ul>
</li>
<li><code>total_amount</code>: The total cost of all items in the order at the time of creation (DECIMAL(10, 2), optional and can be recalculated before payment).</li>
</ul>
<p><strong>Relationships:</strong></p>
<ul>
<li>One-to-many with <code>OrderItem</code>: An order can contain multiple order items, each representing a movie included in this order.</li>
<li>Many-to-one with <code>User</code>: Each order is associated with a single user, who can have many orders over time.</li>
</ul>
<p><strong>Key Points:</strong></p>
<ul>
<li><code>Order</code> provides a snapshot of which movies the user intends to purchase at a given moment.</li>
<li>The <code>status</code> field allows tracking the lifecycle of the order: pending, then paid, or canceled.</li>
<li>The <code>total_amount</code> can be checked or updated before finalizing payment, ensuring accurate billing.</li>
</ul>
</li>
<li>
<p><strong>OrderItem (order_items table)</strong>
Represents a single line item within an order, linking a specific movie to the order.</p>
<p><strong>Attributes:</strong></p>
<ul>
<li><code>id</code>: Primary key (int, auto-incremented).</li>
<li><code>order_id</code>: Foreign key referencing <code>orders.id</code> (int, not null), indicating which order this item belongs to.</li>
<li><code>movie_id</code>: Foreign key referencing <code>movies.id</code> (int, not null), indicating which movie is included in the order.</li>
<li><code>price_at_order</code>: The price of the movie at the time the order was created (DECIMAL(10, 2), not null). Storing the price at order time ensures price changes do not retroactively affect historical orders.</li>
</ul>
<p><strong>Relationships:</strong></p>
<ul>
<li>Many-to-one with <code>Order</code>: Each order item belongs to exactly one order.</li>
<li>Many-to-one with <code>Movie</code>: Each order item references exactly one movie.</li>
</ul>
<p><strong>Key Points:</strong></p>
<ul>
<li><code>OrderItem</code> provides a breakdown of the order contents.</li>
<li>Storing <code>price_at_order</code> ensures historical accuracy of the order data, even if movie prices change later.</li>
</ul>
</li>
</ol>
<p><strong>Summary of Relationships</strong></p>
<ul>
<li><strong>User (1) -- (n) Order</strong>: A single user can have multiple orders.</li>
<li><strong>Order (1) -- (n) OrderItem</strong>: A single order can contain multiple items.</li>
<li><strong>Movie (1) -- (n) OrderItem</strong>: A single movie can appear in many orders from various users.</li>
</ul>
<p><strong>Functional Implications</strong></p>
<ul>
<li>Users can track their order history, including the movies purchased, the final amount paid, and the current status of each order.</li>
<li>The presence of <code>price_at_order</code> in <code>OrderItem</code> ensures that financial records remain consistent over time, essential for audits, refunds, and reporting.</li>
<li>The <code>status</code> field in <code>Order</code> allows for workflow management, including pending payment, cancellation, and handling refunds.</li>
</ul>
<p><strong>DB schema</strong></p>
<ul>
<li><a href="https://dbdiagram.io/d/Order-app-675f141ce763df1f00ff29cb" target="_blank" rel="noreferrer">Order DB schema</a></li>
</ul>
<hr>
<a href="#5-payments" target="_self" rel="noreferrer"><span class="icon icon-link"></span></a><h2 id="5-payments" level="2" sourceposition="[object Object]" index="80" siblingcount="110" node="[object Object]"><strong>5. Payments</strong></h2>
<ul>
<li>
<p><strong>User Functionality:</strong></p>
<ul>
<li>Users can make payments using Stripe.</li>
<li>After payment, users receive a confirmation on the website and via email.</li>
<li>Users can view the history of all their payments, including:
<ul>
<li>Date and time.</li>
<li>Amount.</li>
<li>Status (successful, canceled, refunded).</li>
</ul>
</li>
<li><strong>Validation:</strong>
<ul>
<li>Verify the total amount of the order.</li>
<li>Check the availability of the selected payment method.</li>
<li>Ensure the user is authenticated.</li>
<li>Validate transactions through webhooks provided by the payment system.</li>
<li>Update the order status upon successful payment.</li>
<li>If a transaction is declined, display recommendations to the user (e.g., "Try a different payment method").</li>
</ul>
</li>
</ul>
</li>
<li>
<p><strong>Moderator Functionality:</strong></p>
<ul>
<li>Admins can view a list of all payments with filters for:
<ul>
<li>Users.</li>
<li>Dates.</li>
<li>Statuses (successful, refunded, canceled).</li>
</ul>
</li>
</ul>
</li>
</ul>
<p><strong>Entities and Their Attributes</strong></p>
<ol>
<li>
<p><strong>Payment (payments table)</strong>
Represents a payment transaction made by a user for an order.</p>
<p><strong>Attributes:</strong></p>
<ul>
<li><code>id</code>: Primary key (int, auto-incremented).</li>
<li><code>user_id</code>: Foreign key referencing <code>users.id</code> (int, not null), indicating which user made this payment.</li>
<li><code>order_id</code>: Foreign key referencing <code>orders.id</code> (int, not null), indicating which order this payment is associated with.</li>
<li><code>created_at</code>: Timestamp recording when the payment was created (timestamp with time zone, defaults to the current time).</li>
<li><code>status</code>: Current status of the payment, stored as an enum. Possible values include:
<ul>
<li><strong>successful:</strong> The payment has been completed successfully.</li>
<li><strong>canceled:</strong> The payment was canceled before completion.</li>
<li><strong>refunded:</strong> The amount was refunded after a successful payment.
Defaults to <code>successful</code>, but can be changed as the transaction progresses through its lifecycle.</li>
</ul>
</li>
<li><code>amount</code>: The total amount of the payment (DECIMAL(10,2), not null), ensuring accurate financial records even if the order's pricing changes.</li>
<li><code>external_payment_id</code>: An optional string field to store the external transaction ID from the payment provider (e.g., Stripe's charge_id), enabling easy cross-referencing and validation.</li>
</ul>
<p><strong>Relationships:</strong></p>
<ul>
<li>Many-to-one with <code>User</code>: Each payment is linked to a specific user.</li>
<li>Many-to-one with <code>Order</code>: Each payment is associated with a single order, though an order might have multiple payments if partial or incremental payments are allowed in the future.</li>
<li>One-to-many with <code>PaymentItem</code>: A payment can consist of multiple items, each corresponding to a line item in the order.</li>
</ul>
<p><strong>Key Points:</strong></p>
<ul>
<li><code>Payment</code> records serve as the financial transactions linked to orders.</li>
<li>Storing <code>external_payment_id</code> and <code>status</code> allows integration with payment gateways and easy tracking of payment lifecycle.</li>
</ul>
</li>
<li>
<p><strong>PaymentItem (payment_items table)</strong>
Represents an individual item paid for in a single payment, mirroring an order line item at the time of payment.</p>
<p><strong>Attributes:</strong></p>
<ul>
<li><code>id</code>: Primary key (int, auto-incremented).</li>
<li><code>payment_id</code>: Foreign key referencing <code>payments.id</code> (int, not null), indicating which payment this item belongs to.</li>
<li><code>order_item_id</code>: Foreign key referencing <code>order_items.id</code> (int, not null), linking back to the original order line item.</li>
<li><code>price_at_payment</code>: The price of the specific order item at the time of payment (DECIMAL(10,2), not null). This ensures the payment record remains historically accurate, even if prices change later.</li>
</ul>
<p><strong>Relationships:</strong></p>
<ul>
<li>Many-to-one with <code>Payment</code>: Each payment item belongs to exactly one payment.</li>
<li>Many-to-one with <code>OrderItem</code>: Each payment item references an <code>OrderItem</code> to provide context for what was actually paid for.</li>
</ul>
<p><strong>Key Points:</strong></p>
<ul>
<li><code>PaymentItem</code> captures a snapshot of the pricing and items at the exact moment of payment.</li>
<li>This granular data allows for detailed financial reporting, refunds of individual items, and easy reconciliation of payments against orders.</li>
</ul>
</li>
</ol>
<p><strong>Summary of Relationships</strong></p>
<ul>
<li><strong>User (1) -- (n) Payment</strong>: A user can have multiple payments over time.</li>
<li><strong>Order (1) -- (n) Payment</strong>: An order can be associated with one or more payments (if partial payments are introduced).</li>
<li><strong>Payment (1) -- (n) PaymentItem</strong>: A payment can cover multiple order items.</li>
<li><strong>OrderItem (1) -- (n) PaymentItem</strong>: Multiple payment items can reference different order items of potentially the same order, allowing flexible payment structures.</li>
</ul>
<p><strong>Functional Implications</strong></p>
<ul>
<li>Users have a clear history of all their payments, including details of when, how much, and which items were paid for.</li>
<li>The <code>status</code> field and <code>external_payment_id</code> facilitate robust integration with external payment gateways (like Stripe), enabling features like refunds, cancellations, and transaction validations through webhooks.</li>
<li>Detailed payment itemization (<code>PaymentItem</code>) supports precise financial audits, reporting, and troubleshooting in case of disputes or inquiries.</li>
</ul>
<p><strong>DB schema</strong></p>
<ul>
<li><a href="https://dbdiagram.io/d/Payment-app-675f1a65e763df1f00ff70c6" target="_blank" rel="noreferrer">Payment DB schema</a></li>
</ul>
<hr>
<a href="#6-docker-and-docker-compose" target="_self" rel="noreferrer"><span class="icon icon-link"></span></a><h2 id="6-docker-and-docker-compose" level="2" sourceposition="[object Object]" index="92" siblingcount="110" node="[object Object]"><strong>6. Docker and Docker Compose</strong></h2>
<ul>
<li><strong>Project Containerization:</strong>
<ul>
<li>Use Docker to containerize the project and manage related services efficiently.</li>
</ul>
</li>
<li><strong>Service Management:</strong>
<ul>
<li>Deploy multiple services like FastAPI, Redis, Celery, and MinIO using Docker Compose.</li>
</ul>
</li>
<li><strong>Custom Docker Images:</strong>
<ul>
<li>Create and maintain Docker images for the FastAPI application and related services.</li>
</ul>
</li>
<li><strong>Single Command Setup:</strong>
<ul>
<li>Use a single command to launch all services via Docker Compose for streamlined development and deployment.</li>
</ul>
</li>
</ul>
<hr>
<a href="#7-poetry-for-dependency-management" target="_self" rel="noreferrer"><span class="icon icon-link"></span></a><h2 id="7-poetry-for-dependency-management" level="2" sourceposition="[object Object]" index="96" siblingcount="110" node="[object Object]"><strong>7. Poetry for Dependency Management</strong></h2>
<ul>
<li><strong>Dependency Simplification:</strong>
<ul>
<li>Use Poetry for easy dependency management and virtual environment handling.</li>
</ul>
</li>
<li><strong>Project Dependencies:</strong>
<ul>
<li>Install required project dependencies via Poetry commands.</li>
</ul>
</li>
<li><strong>Configuration File:</strong>
<ul>
<li>Use <code>pyproject.toml</code> to specify all dependencies, versions, and additional configurations.</li>
</ul>
</li>
<li><strong>Environment Management:</strong>
<ul>
<li>Manage virtual environments seamlessly within the development workflow.</li>
</ul>
</li>
</ul>
<hr>
<a href="#8-cicd-with-github-actions" target="_self" rel="noreferrer"><span class="icon icon-link"></span></a><h2 id="8-cicd-with-github-actions" level="2" sourceposition="[object Object]" index="100" siblingcount="110" node="[object Object]"><strong>8. CI/CD with GitHub Actions</strong></h2>
<ul>
<li><strong>Automated Processes:</strong>
<ul>
<li>Configure GitHub Actions to automate code quality checks, testing, and deployment pipelines.</li>
</ul>
</li>
<li><strong>Code Quality Checks:</strong>
<ul>
<li>Run linters such as <code>flake8</code> or <code>black</code> to ensure code consistency.</li>
<li>Perform type checking with <code>mypy</code> to validate type annotations.</li>
</ul>
</li>
<li><strong>Testing Automation:</strong>
<ul>
<li>Execute all tests using <code>pytest</code> to validate functionality.</li>
<li>Generate and review code coverage reports for quality assurance.</li>
</ul>
</li>
<li><strong>Continuous Deployment:</strong>
<ul>
<li>Automatically deploy the application after passing all checks and merging pull requests to AWS EC2.</li>
</ul>
</li>
</ul>
<hr>
<a href="#9-swagger-documentation-requirements" target="_self" rel="noreferrer"><span class="icon icon-link"></span></a><h2 id="9-swagger-documentation-requirements" level="2" sourceposition="[object Object]" index="104" siblingcount="110" node="[object Object]"><strong>9. Swagger Documentation Requirements</strong></h2>
<ul>
<li><strong>OpenAPI Specification:</strong>
<ul>
<li>Use OpenAPI Specification (version 3.0 or above) for documentation.</li>
</ul>
</li>
<li><strong>Complete API Documentation:</strong>
<ul>
<li>Ensure all API endpoints are fully documented for developers and stakeholders.</li>
</ul>
</li>
<li><strong>Access Control:</strong>
<ul>
<li>Restrict access to API documentation, allowing visibility only for authorized users.</li>
</ul>
</li>
</ul>
<hr>
<a href="#10-writing-tests" target="_self" rel="noreferrer"><span class="icon icon-link"></span></a><h2 id="10-writing-tests" level="2" sourceposition="[object Object]" index="108" siblingcount="110" node="[object Object]"><strong>10. Writing Tests</strong></h2>
<ul>
<li><strong>API Endpoint Testing:</strong>
<ul>
<li>Verify that endpoints return correct responses.</li>
<li>Test error handling and ensure proper feedback for invalid inputs.</li>
</ul>
</li>
<li><strong>Validation Testing:</strong>
<ul>
<li>Ensure business rules and validation logic work correctly (e.g., authentication, filtering, and sorting).</li>
</ul>
</li>
<li><strong>Unit Tests:</strong>
<ul>
<li><strong>Coverage:</strong>
<ul>
<li>Data validation logic.</li>
<li>Utility functions.</li>
<li>Individual business rules.</li>
</ul>
</li>
</ul>
</li>
<li><strong>Integration Tests:</strong>
<ul>
<li><strong>Coverage:</strong>
<ul>
<li>Interaction between endpoints and the database.</li>
<li>Authentication workflows, including JWT processing.</li>
</ul>
</li>
</ul>
</li>
<li><strong>Functional Tests:</strong>
<ul>
<li>Cover end-to-end user scenarios such as registration, login, movie filtering, and order placement.</li>
</ul>
</li>
</ul></div>
