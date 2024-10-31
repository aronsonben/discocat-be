from bs4 import BeautifulSoup
import requests

uri1 = "2zu4O5MNLn9MTmm4OM2Yz1"
uri2 = "3TVXtAsR1Inumwj472S9r4"
uri3 = "1cV2hqt2CbxlRCGh0Pvkij"


class ArtistScraper:
    def __init__(self, uri):
        self.uri = uri
        self.html = ""
        self.monthlyListeners = []

    def get_html(self):
        """
        This function gets the raw html code from the website defined in self.uri

        Takes: self
        Use: defines self.html
        Returns: self.html
        """
        try:
            self.html = BeautifulSoup(requests.get(self.uri).content, 'lxml')
            return self.html
        except TypeError:
            print(
                "This function needs an object of the type 'string' to be passed into it to work.")

    def get_monthlyListeners(self):
        """
        This function gets the monthly listeners from the raw html defined in self.html

        Takes: self
        Use: defines self.images
        Returns: self.images
        """
        divs = self.html.find_all('div')
        for div in divs:
            try:
                if (div['data-testid'] == "monthly-listeners-label"):
                    self.monthlyListeners = int(
                        div.text.split(' ')[0].replace(',', ''))
            except KeyError:
                pass
        return self.monthlyListeners


if __name__ == "__main__":
    # SupaT
    spotifyartist = ArtistScraper(uri1)
    spotifyartist.get_html()
    print(spotifyartist.get_monthlyListeners())

    # Drake
    spotifyartist2 = ArtistScraper(uri2)
    spotifyartist2.get_html()
    print(spotifyartist2.get_monthlyListeners())

    # Satellite Mode
    spotifyartist3 = ArtistScraper(uri3)
    spotifyartist3.get_html()
    print(spotifyartist3.get_monthlyListeners())
