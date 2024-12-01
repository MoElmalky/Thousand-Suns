from mutagen.mp3 import MP3,HeaderNotFoundError
from mutagen.id3 import ID3
from PIL import Image, ImageTk
import io

class Song:
     
    def __init__(self,file_path):
        try:
            audio = MP3(file_path, ID3 = ID3)
        except HeaderNotFoundError:
            print(file_path)
        
        self.file_path = file_path
        self.duration = audio.info.length
        self.title = str(audio.tags.get('TIT2'))
        self.artist = str(audio.tags.get('TPE1'))
        self.album = str(audio.tags.get('TALB'))
        self.year = str(audio.tags.get('TDRC'))
        self.cover_data = None
        for tag in audio.tags:
            if tag.startswith('APIC'):
                self.cover_data = audio.tags[tag].data
    
    def get_cover_tk(self):
        image = Image.open(io.BytesIO(self.cover_data)) if self.cover_data else Image.open("assets/cover.png")
        image = image.resize((100, 100))
        cover = ImageTk.PhotoImage(image)
        return cover
