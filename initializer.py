"""
This part is where all the internal variables and storages are being unitedly initialized for usage in other modules.
"""
import aiogram
import jsondriver
import config
import sys

tran_tagname = {'maths': 'Математика', 'engineering': 'Инженерия', 'science': 'Естественные науки', 'it': 'IT', 
                'clubs': 'Кружки и клубы', 'conference': 'Конференции', 'olympiad': 'Олимпиады', 'education': 'Образовательные мероприятия',
                'popsci': 'Научно-популярные мероприятия', 'tours': 'Экскурсии', 'scientific_seminars': 'Научные семинары'}


TOKEN = config.TOKEN

bot = aiogram.Bot(TOKEN)
dp = aiogram.Dispatcher(bot)

channel_id = -1001522987203 # id админского чата
author_id = 664519103  # id автора
logchat_id = 664519103 # id чата куда пишутся логи
db_path = "db_prod"

# если есть флаг testing, то: @idfed09 админ, логи и прочее пишем в эту беседу
# (пишите мне в лс для добавления)
if "--testing" in sys.argv:
    channel_id = -1002057270905
    author_id = 920061911
    logchat_id = -1002057270905
    db_path = "db_testing"


# setting up data storage
usercoll = jsondriver.AsyncJsonCollection(file_path=db_path+'/usercoll.json')
postcoll = jsondriver.AsyncJsonCollection(file_path=db_path+"/postcoll.json")

# setting up data storage
usercoll = jsondriver.AsyncJsonCollection(file_path=db_path+'/usercoll.json')
postcoll = jsondriver.AsyncJsonCollection(file_path=db_path+"/postcoll.json")

