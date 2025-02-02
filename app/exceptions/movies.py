class BaseMovieError(Exception):
    def __init__(self, message=None):
        if not message:
            message = "A movie-related error occurred."
        super().__init__(message)


class MovieNotFoundError(BaseMovieError):
    def __init__(self, message="Movie not found."):
        super().__init__(message)


class MovieAlreadyLikedError(BaseMovieError):
    def __init__(self, message="You have already liked this movie."):
        super().__init__(message)


class MovieAlreadyDislikedError(BaseMovieError):
    def __init__(self, message="You have already disliked this movie."):
        super().__init__(message)


class MovieAlreadyFavoritedError(BaseMovieError):
    def __init__(self, message="You have already added this movie to favorites."):
        super().__init__(message)


class MovieAlreadyRatedError(BaseMovieError):
    def __init__(self, message="You have already rated this movie."):
        super().__init__(message)


class CommentNotFoundError(BaseMovieError):
    def __init__(self, message="Comment not found."):
        super().__init__(message)


class CommentAlreadyLikedError(BaseMovieError):
    def __init__(self, message="You have already liked this comment."):
        super().__init__(message)
