from site_parser.category import CategoryParser
from site_parser.movie import MovieParser


def main():
    category_parser = CategoryParser()
    categories = category_parser.get_categories_data()

    movie_parser = MovieParser()

    movie_parser.get_movies(categories)


main()

