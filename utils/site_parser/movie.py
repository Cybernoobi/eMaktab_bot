from .base import BaseParser


class MovieParser(BaseParser):
    def get_movies(self, categories):
        result = []

        for category in categories[:2]:
            soup = self.get_soup(url=category['url'])
            wrapper = soup.find('div', id='dle-content')
            movies = wrapper.find_all('div', class_='shortstory')
            options = []

            for movie in movies:
                title = movie.find('div', class_='shortstory__title').get_text(strip=True)
                # print(title)
                options_wrapper = movie.find('div', class_='shortstory__info-wrapper').find_all('span')
                for option in options_wrapper:
                    items = option.get_text().split(':')
                    if len(items) > 1:
                        options.append({
                            items[0]: items[1]
                        })
                    else:
                        continue
            