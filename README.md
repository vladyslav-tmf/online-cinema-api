# **Online Cinema** 

## **Overview**
Welcome to **Online Cinema**, the perfect place for discovering and enjoying your favorite movies! Whether you're in the mood for the latest blockbuster or a timeless classic, our platform offers a rich catalog of films available to watch, purchase, and explore. With a user-friendly interface, personalized experience, and a variety of features, your movie experience has never been so convenient!

## **Check it Out**
The deployment link 

## **Installation Guide**

### **Pre-requisites**
Before you begin, ensure that the following tools are installed on your machine:

- **Python 3.12** or higher
- **Virtualenv** (optional but recommended for an isolated environment)
- **Poetry** (for managing project dependencies)
- **Alembic** (for database migrations)
- **Uvicorn** (for running the FastAPI app)

### **Steps to Install**
1. **Clone the repository**  
   First, clone the project repository to your local machine:
   ```bash
   git clone https://github.com/vladyslav-tmf/online-cinema-api.git
2. **Navigate to the project directory**
   Change into the project folder:
   ```bash
   cd online_cinema_fastapi
3. **Install Dependencies Using Poetry**
   Install all project dependencies:
   ```bash
   poetry install

4. **Activate the Virtual Environment**
   Launch the Poetry virtual environment:
   ```bash
   poetry shell
   
5. **Set up the database**
   Run Alembic to apply database migrations:
   ```bash
   alembic upgrade head

6. **Start the development server**
   Launch the app in development mode:
   ```bash
   uvicorn app.main:app --reload

## Features

### Authorization and Authentication

**User Registration**  
Sign up by providing your email, and receive an activation link that’s valid for 24 hours. Missed the deadline? You can always request a new activation link.

**Login and Logout**  
Secure authentication using JWT. Log in seamlessly and enjoy uninterrupted access. Logout securely when you're done.

**Password Management**  
Forgot your password? Request a reset link to set a new one. You can also change your current password directly if you’re logged in.

**JWT Token Management**  
Keep your sessions active with a refresh token and access token for secure, long-lasting authentication.

**User Roles**  
- **User**: Browse movies and enjoy content.
- **Moderator**: Manage content and track sales.
- **Admin**: Oversee everything, from user management to system settings.

### Movies

**User Features**
- Browse and explore a wide catalog of movies, each with descriptions and options to like, dislike, or comment.
- Search and filter movies by genres, price, release date, and more.
- Create a personalized list of favorite films.
- Rate movies on a 10-point scale and view ratings from other users.

**Moderator Features**
- Manage movies, genres, and actors.
- Protect purchased movies from being deleted.

### Shopping Cart

**User Features**
- Add movies to your cart and proceed to purchase if not already owned.
- Receive notifications if you attempt to add a movie you’ve already bought.
- Remove movies from the cart with ease.
- View movie details (title, price, genre, release year) in your cart.
- Complete your purchase and get immediate access to your movies.

**Moderator Features**
- Admins can review and monitor user carts for troubleshooting or analysis.
- Moderators will receive notifications if a movie is deleted while it’s in someone’s cart.

### Order Management

**User Features**
- Place orders quickly and easily for movies in your cart.
- Receive notifications if any movies are unavailable (e.g., deleted or region-locked).
- View order history with details such as order date, total amount, and status (paid, canceled, pending).
- Cancel orders before payment or request a refund for completed purchases.

**Validation**
- Ensure your cart isn’t empty before placing an order.
- Avoid duplicate orders for the same movie.
- Movies already purchased will not be added to the cart again.

**Moderator Features**
- Admins can filter and view user orders by user, date, and status.

### Payments

**User Features**
- Use Stripe to securely process payments.
- Get payment confirmations both on the website and via email after successful payments.
- Track payment history, including date, amount, and payment status.

**Validation**
- Ensure the total amount is correctly calculated before processing.
- Verify the payment method’s validity.
- The user must be logged in to make a payment.

**Moderator Features**
- Admins can view and filter payments by user, date, and status.

## Technologies Used

- **FastAPI**: The web framework for building high-performance APIs.
- **SQLAlchemy**: ORM for database interaction.
- **Stripe**: For handling payments securely.
- **Alembic**: For managing database migrations.
- **JWT**: For secure authentication.
- **Uvicorn**: ASGI server for running FastAPI apps.
- **Celery Beat**: A scheduler for periodic tasks in Celery, allowing you to run tasks at specific intervals or scheduled times

## Contributing
We welcome contributions! Feel free to fork this repository and submit pull requests. If you find a bug or have an idea for a new feature, please open an issue.

