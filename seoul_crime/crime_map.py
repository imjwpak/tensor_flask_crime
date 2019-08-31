from seoul_crime.data_reader import DataReader
import numpy as np
import folium # 지도 그리는 라이브러리

class CrimeMap:
    def __init__(self):
        self.dr = DataReader()

    def hook_process(self):
        self.create_seoul_crime_map()

    def create_seoul_crime_map(self):
        self.dr.context = './saved_data/'
        self.dr.fname = 'police_norm.csv'
        police_norm = self.dr.csv_to_dframe()
        #print(police_norm)

        self.dr.context = './data/'
        self.dr.fname = 'geo_simple.json'
        seoul_geo = self.dr.json_load()

        self.dr.context = './data/'
        self.dr.fname = 'crime_in_seoul.csv'
        crime = self.dr.csv_to_dframe()

        ## 기존코드
        station_names = []
        for name in crime['관서명']:
            station_names.append('서울' + str(name[:-1] + '경찰서'))

        station_addrs = []
        station_lats = []  # 위도
        station_lngs = []  # 경도
        gmaps = self.dr.create_gmaps()
        for name in station_names:
            t = gmaps.geocode(name, language='ko')
            station_addrs.append(t[0].get('formatted_address'))
            t_loc = t[0].get('geometry')
            station_lats.append(t_loc['location']['lat'])
            station_lngs.append(t_loc['location']['lng'])
            #print(name + '---------> ' + t[0].get('formatted_address'))
        ## 기존코드
        self.dr.context = './data/'
        self.dr.fname = 'police_position.csv'
        police_pos = self.dr.csv_to_dframe()
        police_pos['let'] = station_lats
        police_pos['lng'] = station_lngs
        #print(police_pos)

        col = ['살인 검거', '강도 검거', '강간 검거', '절도 검거', '폭력 검거']
        tmp = police_pos[col] / police_pos[col].max()
        police_pos['검거'] = np.sum(tmp, axis=1)
        self.dr.fname = 'geo_simple.json'


        m = folium.Map(location=[37.5502, 126.982], zoom_start=12, title='Stamen Toner')
        m.choropleth(
            geo_data=seoul_geo,
            name='choropleth',
            data=tuple(zip(police_norm['구별'],police_norm['범죄'])), # Tuple 타입으로만 들어가게 되어있음
            key_on='feature.id',
            fill_color='PuRd', # Puple/Red
            fill_opacity=0.7,  # 투명도
            line_opacity=0.2,
            legend_name='Crime Rate (%)'
        )

        for i in police_pos.index:
            folium.CircleMarker([police_pos['let'][i], police_pos['lng'][i]],
                                radius=police_pos['검거'][i] * 10,
                                file_color = '#0a0a32').add_to(m)

        #m.save('./saved_data/Seoul_Crime.html')
        m.save('./saved_data/Seoul_Crime_Map.html')
