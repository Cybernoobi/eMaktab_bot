from .base import BaseParser


class CategoryParser(BaseParser):
    def __filter_category(self, category):
        # text = category['href']
        lst = category['href'].split('/')
        return 'podborki.html' not in lst and 'xfsearch' not in lst

    def get_categories_data(self):
        soup = self.get_soup()

        result = []

        wrapper = soup.find('div', class_='leftblok1')
        links = list(filter(self.__filter_category, wrapper.find_all('a')))
        for link in links:
            count = link.next.next.get_text(strip=True).replace('(', '').replace(')', '')
            name = link.get_text(strip=True)
            url = self.BASE_URL + link['href']
            result.append({
                "name": name,
                "url": url,
                "count": count
            })
        return result


        print(links)
