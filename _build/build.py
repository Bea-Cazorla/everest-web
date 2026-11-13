"""Genera la web estática del proyecto EVEREST.

Uso:  python _build/build.py   (desde la carpeta everest_web o desde cualquier otra)

Todas las páginas comparten cabecera, franja de financiación y pie: las normas de publicidad de la AEI exigen
el texto de financiación y los logos en todas las páginas y, en la portada, visibles sin desplazarse.
El contenido está en este archivo. Las fotos están en img/fotos (descargadas de Wikimedia Commons) y cada una
muestra su autoría y licencia. Para cambiar un texto, edítalo aquí y vuelve a ejecutar el script.
"""
import math
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UPDATED = 'noviembre de 2026'
FUND = ('Proyecto <span class="mono">PID2023-151939OB-I00</span> financiado por '
        '<span class="mono">MICIU/AEI/10.13039/501100011033</span> y por FEDER, UE.')
FUND_ALT = 'Ministerio de Ciencia, Innovación y Universidades; Cofinanciado por la Unión Europea; Agencia Estatal de Investigación'
MONITOREO_APP = 'https://ee-ugr-default-project.projects.earthengine.app/view/monitoreo'
MONITOREO_GH = 'https://github.com/monitoreo-obsnev/monitoreo'
MONITOREO_DOI = 'https://doi.org/10.5281/zenodo.23814894'
CONTACTS = [('Javier Martínez López', 'javier.martinez@ugr.es'), ('Domingo Alcaraz Segura', 'dalcaraz@ugr.es')]
# Official project title, verbatim from the proposal (Memoria científico-técnica, section 1). Do not edit.
TITLE_ES = ('Variables esenciales para la caracterización y seguimiento remoto de ecosistemas de montaña a lo largo de '
            'un gradiente biogeográfico: del dato a la toma de decisiones')
TITLE_EN = ('Essential Variables for the rEmote characterisation and monitoRing of mountain EcosystemS along a '
            'biogeographical gradienT: from data to decision making')


def ext(url, text):
    return f'<a href="{url}" target="_blank" rel="noopener">{text}</a>'


# ---------------------------------------------------------------------------------------------------------------
# Iconos (24×24, trazo)
# ---------------------------------------------------------------------------------------------------------------
ICONS = {
    'people': '<circle cx="9" cy="8" r="3.2"/><path d="M3 19c0-3.3 2.7-5.5 6-5.5s6 2.2 6 5.5"/><circle cx="17" cy="9" r="2.6"/><path d="M15.5 13.6c3 .2 5.5 2.2 5.5 5.4"/>',
    'layers': '<path d="M12 3l9 5-9 5-9-5 9-5z"/><path d="M3 12.5l9 5 9-5"/><path d="M3 17l9 5 9-5"/>',
    'trend': '<path d="M3 20h18"/><path d="M4 16l5-5 4 3 7-8"/><path d="M15 6h5v5"/>',
    'leaf': '<path d="M5 19c0-8 6-14 15-14 0 9-6 15-14 15"/><path d="M5 19l8-8"/>',
    'tool': '<rect x="3" y="4" width="18" height="12" rx="2"/><path d="M8 20h8M12 16v4"/><path d="M7 12l3-3 2 2 4-4"/>',
    'satellite': '<rect x="9" y="9" width="6" height="6" rx="1" transform="rotate(45 12 12)"/><path d="M8.5 8.5L5 5M3 7l4-4M15.5 15.5L19 19M17 21l4-4"/><path d="M15 3.5a5.5 5.5 0 0 1 5.5 5.5"/>',
    'drop': '<path d="M12 3c3 4 6 7.5 6 11a6 6 0 0 1-12 0c0-3.5 3-7 6-11z"/><path d="M9 14.5a3 3 0 0 0 3 3"/>',
    'sprout': '<path d="M12 21v-9"/><path d="M12 12c0-4-3-6-7-6 0 4 3 6 7 6z"/><path d="M12 14c0-4 3-6 7-6 0 4-3 6-7 6z"/>',
    'mountain': '<path d="M2 20l7-12 4 6 3-4 6 10z"/><path d="M7.4 11l1.6 1.8 1.6-1.3"/>',
    'snow': '<path d="M12 3v18M4.2 7.5l15.6 9M4.2 16.5l15.6-9"/>',
    'doc': '<path d="M7 3h7l5 5v13H7z"/><path d="M14 3v5h5M10 13h6M10 17h6"/>',
    'db': '<ellipse cx="12" cy="6" rx="7" ry="3"/><path d="M5 6v12c0 1.7 3.1 3 7 3s7-1.3 7-3V6"/><path d="M5 12c0 1.7 3.1 3 7 3s7-1.3 7-3"/>',
    'mail': '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/>',
    'pin': '<path d="M12 21s7-6.2 7-11.5a7 7 0 0 0-14 0C5 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/>',
    'code': '<path d="M8 8l-4 4 4 4M16 8l4 4-4 4M14 5l-4 14"/>',
    'sun': '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
    'cloud': '<path d="M7 18h10a4 4 0 0 0 .6-7.96A6 6 0 0 0 6.1 9.6 4.2 4.2 0 0 0 7 18z"/>',
    'globe': '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/>',
    'chat': '<path d="M4 5h16v11H9l-5 4z"/><path d="M8 9h8M8 12h5"/>',
    'term': '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M7 9l3 3-3 3M12 15h5"/>',
    'map': '<path d="M3 6l6-3 6 3 6-3v15l-6 3-6-3-6 3z"/><path d="M9 3v15M15 6v15"/>',
    'plug': '<path d="M9 2v6M15 2v6M6 8h12v4a6 6 0 0 1-12 0z"/><path d="M12 18v4"/>',
}


def icon(name):
    return f'<svg class="ico" viewBox="0 0 24 24" aria-hidden="true">{ICONS[name]}</svg>'


PALETTE = ['blue', 'orange', 'green', 'teal', 'purple']


# ---------------------------------------------------------------------------------------------------------------
# Parques
# ---------------------------------------------------------------------------------------------------------------
REGIONS = {'med': 'Mediterránea', 'alp': 'Alpina', 'atl': 'Atlántica', 'mac': 'Macaronésica'}
TASK_PAGES = {'T1': 't1', 'T2': 't2', 'T3': 't3', 'T4': 't4', 'T5': 't5'}
TASK_NAMES = {'T1': 'Implicación de actores', 'T2': 'Variables Esenciales de la Biodiversidad', 'T3': 'Dinámicas de referencia',
              'T4': 'Aplicación a la gestión', 'T5': 'Transferencia'}
TASK_COLORS = {'T1': 'orange', 'T2': 'green', 'T3': 'blue', 'T4': 'teal', 'T5': 'purple'}
TASK_ICONS = {'T1': 'people', 'T2': 'layers', 'T3': 'trend', 'T4': 'leaf', 'T5': 'tool'}

PARKS = [
    dict(slug='sierra-nevada', name='Sierra Nevada', full='Parque Nacional de Sierra Nevada', country='España',
         where='Granada y Almería (Andalucía)', region='med', declared='1999', peak='Mulhacén, 3.479 m',
         lon=-3.31, lat=37.05, photo=dict(
             page='https://commons.wikimedia.org/wiki/File:Laguna_Hondera_-_Sierra_Nevada_-_Spain.tif',
             author='Bouke ten Cate', lic='CC BY 4.0', licurl='https://creativecommons.org/licenses/by/4.0',
             alt='Laguna Hondera, una laguna de origen glaciar en Sierra Nevada', cap='Laguna Hondera, Sierra Nevada'),
         about=[
             'Sierra Nevada, en el sureste de la península ibérica, alcanza 3.479 m en el Mulhacén, la cumbre más alta de '
             'la Península. Es parque nacional desde 1999 y reserva de la biosfera, y uno de los principales centros de '
             'endemismo vegetal del Mediterráneo.',
             'Sus borreguiles (pastizales húmedos de alta montaña), sus lagunas de origen glaciar y la nieve que los '
             'alimenta son especialmente sensibles al calentamiento y a la sequía. Es además una de las montañas mejor '
             'estudiadas de Europa: el Observatorio de Cambio Global de Sierra Nevada aporta largas series de clima, '
             'nieve, vegetación y fauna, y una colaboración de más de quince años con los gestores del Espacio Natural.'],
         everest=[
             '<strong>Parque piloto.</strong> Aquí se desarrollan y prueban primero los métodos que después se extienden '
             'al resto de parques.',
             '<strong>Borreguiles</strong> (hábitat prioritario 6230*): mapa con un modelo Random Forest de 50 variables '
             'y 584 puntos verificados en 20 cuencas (AUC = 0,87), y condición de cada borreguil respecto a las zonas '
             'bien conservadas mediante la distancia de Mahalanobis.',
             '<strong>Lagunas:</strong> clorofila-a con Sentinel-2 en 56 lagunas muestreadas entre 2020 y 2023, y '
             'delimitación de las láminas de agua con PlanetScope.',
             '<strong>Nieve:</strong> detección calibrada con transectos de campo y sensores de microclima, y serie de '
             'innivación de Landsat de 1985 a 2025.',
             '<strong>Tendencias:</strong> verdor (NDVI) entre 1985 y 2022 y unidades funcionales del paisaje.',
             '<strong>Gestión forestal y restauración:</strong> respuesta de 80 parcelas de pinar de repoblación a los '
             'aclareos (Landsat, 1990–2025), efecto de la retirada de la madera quemada sobre la nieve y efecto de la '
             'restauración de acequias tradicionales.',
             '<strong>Co-diseño:</strong> cinco reuniones de co-diseño y formación en MonitorEO con técnicos del Espacio '
             'Natural Sierra Nevada (diciembre de 2024 – enero de 2026).'],
         extra=['borreguil', 'acequia', 'nieve-satelite'],
         tasks=['T1', 'T2', 'T3', 'T4', 'T5'],
         partners=['Junta de Andalucía: Espacio Natural Sierra Nevada y REDIAM',
                   'Observatorio de Cambio Global de Sierra Nevada', 'Instituto del Agua, Universidad de Granada',
                   'Proyectos PRESINMED y NevadEO']),
    dict(slug='sierra-de-las-nieves', name='Sierra de las Nieves', full='Parque Nacional de la Sierra de las Nieves',
         country='España', where='Málaga (Andalucía)', region='med', declared='2021', peak='Torrecilla, 1.919 m',
         lon=-5.01, lat=36.68, photo=dict(
             page='https://commons.wikimedia.org/wiki/File:Vista_de_Abies_pinsapo_en_la_Sierra_de_las_Nieves.jpg',
             author='JABerrocal', lic='CC BY-SA 4.0', licurl='https://creativecommons.org/licenses/by-sa/4.0',
             alt='Pinsapos (Abies pinsapo) en la Sierra de las Nieves', cap='Pinsapar, Sierra de las Nieves'),
         about=[
             'En el extremo occidental de la cordillera Bética, en la Serranía de Ronda, alcanza 1.919 m en el pico '
             'Torrecilla, la mayor altitud de Andalucía occidental. Declarado en 2021, es el parque nacional más reciente '
             'de la Red.',
             'Destaca por sus pinsapares, bosques del abeto endémico <em>Abies pinsapo</em> que son reliquia de climas '
             'más fríos, y por un relieve kárstico de tajos, simas y dolinas.'],
         everest=[
             'Contacto con la Red de Información Ambiental de Andalucía (REDIAM) para el caso de estudio del parque.',
             'Representa la montaña mediterránea más occidental y de menor altitud en la comparación entre parques de '
             'las Tareas 2 y 3.',
             'Los casos de estudio se seleccionan con los gestores en los talleres de la Tarea 1.'],
         tasks=['T1', 'T2', 'T3'], partners=['Junta de Andalucía: REDIAM']),
    dict(slug='sierra-de-guadarrama', name='Sierra de Guadarrama', full='Parque Nacional de la Sierra de Guadarrama',
         country='España', where='Madrid y Castilla y León', region='med', declared='2013', peak='Peñalara, 2.428 m',
         lon=-3.96, lat=40.83, photo=dict(
             page='https://commons.wikimedia.org/wiki/File:Circo_y_cima_de_Pe%C3%B1alara1.JPG',
             author='Miguel303xm', lic='CC BY-SA 2.5', licurl='https://creativecommons.org/licenses/by-sa/2.5',
             alt='Circo glaciar y cumbre de Peñalara reflejados en una laguna', cap='Circo y laguna de Peñalara'),
         about=[
             'Entre Madrid y Segovia, la sierra de Guadarrama alcanza 2.428 m en Peñalara. Declarado parque nacional en '
             '2013, protege pinares de pino silvestre, piornales y pastizales de cumbre.',
             'En el macizo de Peñalara se conservan lagunas y turberas de origen glaciar con un largo historial de '
             'seguimiento de la calidad del agua.'],
         everest=[
             'Series de calidad del agua de las lagunas de Peñalara, aportadas por el equipo del parque nacional, para '
             'calibrar los modelos de clorofila de la Tarea 4.2.',
             'Presentación de EVEREST y MonitorEO en un seminario del MITECO y el CENEAM sobre el conocimiento de los '
             'hábitats con nuevas tecnologías (Valsaín, Segovia, abril de 2026).'],
         tasks=['T1', 'T2', 'T3', 'T4'], partners=['Parque Nacional de la Sierra de Guadarrama', 'MITECO – CENEAM']),
    dict(slug='picos-de-europa', name='Picos de Europa', full='Parque Nacional de los Picos de Europa',
         country='España', where='Asturias, Cantabria y Castilla y León', region='atl', declared='1918',
         peak='Torre Cerredo, 2.650 m', lon=-4.85, lat=43.20, photo=dict(
             page='https://commons.wikimedia.org/wiki/File:Lagos_de_Covadonga_lago_de_la_Ercina.jpg',
             author='Txo', lic='CC BY-SA 4.0', licurl='https://creativecommons.org/licenses/by-sa/4.0',
             alt='Lago de la Ercina, en los lagos de Covadonga', cap='Lago de la Ercina, Picos de Europa'),
         about=[
             'Primer parque nacional de España, declarado en 1918 como Montaña de Covadonga y ampliado en 1995, se reparte '
             'entre Asturias, Cantabria y Castilla y León y alcanza 2.650 m en Torre Cerredo.',
             'Sus macizos calizos de clima atlántico albergan hayedos, pastos de puerto, valles y circos glaciares y lagos '
             'como los de Covadonga.'],
         everest=[
             'Datos de clorofila-a y sólidos en suspensión de los lagos del parque, aportados por la Confederación '
             'Hidrográfica del Cantábrico (2026), para la Tarea 4.2.',
             'Colaboración con el proyecto MOTIVATE (Universidad de Oviedo – IMIB) en el seguimiento de hábitats con '
             'inventarios de vegetación y teledetección.'],
         tasks=['T1', 'T2', 'T3', 'T4'],
         partners=['Confederación Hidrográfica del Cantábrico', 'Universidad de Oviedo – IMIB (proyecto MOTIVATE)']),
    dict(slug='ordesa-y-monte-perdido', name='Ordesa y Monte Perdido', full='Parque Nacional de Ordesa y Monte Perdido',
         country='España', where='Huesca (Aragón)', region='alp', declared='1918', peak='Monte Perdido, 3.355 m',
         lon=0.03, lat=42.65, photo=dict(
             page='https://commons.wikimedia.org/wiki/File:Ordesa_Valley.jpg',
             author='Martin Stiburek', lic='CC BY-SA 4.0', licurl='https://creativecommons.org/licenses/by-sa/4.0',
             alt='Valle de Ordesa con sus paredes calizas', cap='Valle de Ordesa'),
         about=[
             'En el Pirineo de Huesca, el macizo de Monte Perdido (3.355 m) es uno de los macizos calizos más altos de '
             'Europa. Declarado parque nacional en 1918, forma parte del bien Pirineos – Monte Perdido, patrimonio '
             'mundial de la UNESCO.',
             'Cañones, circos glaciares y pastos alpinos con una flora rica en endemismos pirenaicos.'],
         everest=[
             'Presentación del proyecto en el taller «The Eyes on Pirineu\'s lakes» (Universitat de Barcelona, octubre '
             'de 2025), dedicado al seguimiento de los lagos pirenaicos.',
             'Representa la región alpina, junto con Aigüestortes, en la comparación entre parques de las Tareas 2 y 3.',
             'Los casos de estudio se seleccionan con los gestores en los talleres de la Tarea 1.'],
         tasks=['T1', 'T2', 'T3'], partners=[]),
    dict(slug='aiguestortes', name='Aigüestortes i Estany de Sant Maurici',
         full="Parc Nacional d'Aigüestortes i Estany de Sant Maurici", country='España', where='Lleida (Cataluña)',
         region='alp', declared='1955', peak='Más de 3.000 m', lon=0.95, lat=42.58, photo=dict(
             page='https://commons.wikimedia.org/wiki/File:Sant_Maurici_lake,_Aig%C3%BCestortes_i_Estany_de_Sant_Maurici_National_Park,_Spain_-_Diliff.jpg',
             author='Diliff', lic='CC BY-SA 3.0', licurl='https://creativecommons.org/licenses/by-sa/3.0',
             alt="Estany de Sant Maurici rodeado de montañas y prados en flor", cap="Estany de Sant Maurici"),
         about=[
             'Único parque nacional de Cataluña, declarado en 1955, es un paisaje granítico de alta montaña modelado por '
             'los glaciares, con cumbres de más de 3.000 m y alrededor de doscientos lagos (<em>estanys</em>).',
             'Sus lagos se estudian desde hace décadas y son un referente para el seguimiento de los lagos de montaña.'],
         everest=[
             'Series de calidad del agua de lagos del parque, en colaboración con el Centro de Estudios Avanzados de '
             'Blanes (CEAB-CSIC), para la Tarea 4.2.',
             'Presentación del proyecto en el taller «The Eyes on Pirineu\'s lakes» (Universitat de Barcelona, 2025).'],
         tasks=['T1', 'T2', 'T3', 'T4'], partners=['CEAB-CSIC', 'Universitat de Barcelona']),
    dict(slug='teide', name='Teide', full='Parque Nacional del Teide', country='España', where='Tenerife (Canarias)',
         region='mac', declared='1954', peak='Teide, 3.715 m', lon=-16.64, lat=28.27, photo=dict(
             page='https://commons.wikimedia.org/wiki/File:Teide_Canadas.jpg',
             author='Ingo Mehling', lic='CC BY-SA 4.0', licurl='https://creativecommons.org/licenses/by-sa/4.0',
             alt='El Teide y Las Cañadas desde el borde de la caldera', cap='El Teide y Las Cañadas'),
         about=[
             'En el centro de Tenerife, el Teide alcanza 3.715 m, la cumbre más alta de España. Es parque nacional desde '
             '1954 y patrimonio mundial de la UNESCO desde 2007.',
             'Es el único parque macaronésico del proyecto: una alta montaña volcánica subtropical con matorrales de '
             'cumbre ricos en endemismos, como la retama del Teide y el tajinaste rojo.'],
         everest=[
             'Representa la región macaronésica en la comparación entre parques de las Tareas 2 y 3.',
             'Los casos de estudio se seleccionan con los gestores en los talleres de la Tarea 1.'],
         tasks=['T1', 'T2', 'T3'], partners=[]),
    dict(slug='peneda-geres', name='Peneda-Gerês', full='Parque Nacional da Peneda-Gerês', country='Portugal',
         where='Norte de Portugal, junto a Galicia', region='atl', declared='1971', peak='Nevosa, 1.545 m',
         lon=-8.15, lat=41.80, photo=dict(
             page='https://commons.wikimedia.org/wiki/File:Parque_Nacional_Peneda-G%C3%A9res,_Portugal.jpg',
             author='Harpagornis', lic='CC BY-SA 4.0', licurl='https://creativecommons.org/licenses/by-sa/4.0',
             alt='Panorámica de las montañas de Peneda-Gerês', cap='Parque Nacional da Peneda-Gerês'),
         about=[
             'Único parque nacional de Portugal, declarado en 1971 en el norte del país, junto a la frontera con Galicia. '
             'Sus montañas graníticas de influencia atlántica alcanzan 1.545 m en la Nevosa.',
             'Robledales, turberas, pastos de altura y una larga historia de usos tradicionales. Con la Baixa Limia – '
             'Serra do Xurés forma la Reserva de la Biosfera transfronteriza Gerês-Xurés.'],
         everest=[
             'Caso de estudio a cargo de los socios del CIBIO-InBIO (Universidade do Porto): métricas de resiliencia '
             'tras incendios (Tarea 4.3) y cartografía de vegetación (Tarea 4.1).',
             'Contactos con el Instituto da Conservação da Natureza e das Florestas (ICNF) y la Agência Portuguesa do '
             'Ambiente (APA).'],
         tasks=['T1', 'T2', 'T3', 'T4'], partners=['CIBIO-InBIO, Universidade do Porto', 'ICNF', 'APA']),
]
PARK = {p['slug']: p for p in PARKS}


# ---------------------------------------------------------------------------------------------------------------
# Fotos (img/fotos/<id>.jpg). Autoría y licencia de Wikimedia Commons.
# ---------------------------------------------------------------------------------------------------------------
def jpeg_size(path):
    """Width and height of a JPEG, read from its SOF marker."""
    data = path.read_bytes()
    i = 2
    while i < len(data):
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        if marker in (0xC0, 0xC1, 0xC2):
            h, w = struct.unpack('>HH', data[i + 5:i + 9])
            return w, h
        i += 2 + struct.unpack('>H', data[i + 2:i + 4])[0]
    raise ValueError(f'No JPEG size in {path}')


PHOTOS = {p['slug']: p['photo'] for p in PARKS}
PHOTOS.update({
    'satelite': dict(page='https://commons.wikimedia.org/wiki/File:Sierra_Nevada_National_Park_2017_02_18_(32378207013).jpg',
                     author='Antti Lipponen (Sentinel-2A)', lic='CC BY 2.0', licurl='https://creativecommons.org/licenses/by/2.0',
                     alt='Imagen del satélite Sentinel-2A de Sierra Nevada con las cumbres nevadas, 18 de febrero de 2017',
                     cap='Sierra Nevada desde Sentinel-2 (18 de febrero de 2017)', kind='Imagen'),
    'nieve-satelite': dict(page='https://commons.wikimedia.org/wiki/File:Unprecedented_snowfall_in_Sierra_Nevada,_Spain_(Copernicus_2024-03-18).jpg',
                           author='Unión Europea, imágenes Copernicus Sentinel-2', lic='Atribución',
                           licurl='https://commons.wikimedia.org/wiki/File:Unprecedented_snowfall_in_Sierra_Nevada,_Spain_(Copernicus_2024-03-18).jpg',
                           alt='Sierra Nevada cubierta de nieve vista por Sentinel-2 el 18 de marzo de 2024',
                           cap='Nieve en Sierra Nevada desde Sentinel-2 (18 de marzo de 2024)', kind='Imagen'),
    'borreguil': dict(page='https://commons.wikimedia.org/wiki/File:Borreguil_en_el_Cerro_del_Caballo.jpg',
                      author='Granadaruralsur', lic='CC BY-SA 4.0', licurl='https://creativecommons.org/licenses/by-sa/4.0',
                      alt='Borreguil verde atravesado por un arroyo en el Cerro del Caballo, Sierra Nevada',
                      cap='Borreguil en el Cerro del Caballo, Sierra Nevada'),
    'acequia': dict(page='https://commons.wikimedia.org/wiki/File:Sendero_Acequias_del_Poqueira_in_Capileira,_Sierra_Nevada_National_Park_(DSCF5692).jpg',
                    author='Trougnouf (Benoit Brummer)', lic='CC BY 4.0', licurl='https://creativecommons.org/licenses/by/4.0',
                    alt='Valle del Poqueira desde el sendero de las acequias, en Capileira',
                    cap='Sendero de las acequias del Poqueira, Sierra Nevada'),
    'amanecer': dict(page='https://commons.wikimedia.org/wiki/File:Sunrise_over_a_valley_in_Capileira,_Sierra_Nevada_National_Park_(DSCF5406).jpg',
                     author='Trougnouf (Benoit Brummer)', lic='CC BY 4.0', licurl='https://creativecommons.org/licenses/by/4.0',
                     alt='Amanecer sobre un valle de Capileira, en Sierra Nevada', cap='Amanecer en Capileira, Sierra Nevada'),
})
for _id, _ph in PHOTOS.items():
    _ph['id'] = _id
    _ph['src'] = f'@/img/fotos/{_id}.jpg'
    _ph['w'], _ph['h'] = jpeg_size(ROOT / 'img' / 'fotos' / f'{_id}.jpg')
    _ph.setdefault('kind', 'Foto')
EXTRA_PHOTOS = ['borreguil', 'acequia', 'amanecer', 'satelite', 'nieve-satelite']


def credit(ph):
    return f'{ph["kind"]}: {ext(ph["page"], ph["author"])} · {ext(ph["licurl"], ph["lic"])} · Wikimedia Commons'


def img_tag(ph, lazy=True, cls=''):
    return (f'<img src="{ph["src"]}" width="{ph["w"]}" height="{ph["h"]}" alt="{ph["alt"]}"'
            + (' loading="lazy"' if lazy else '') + (f' class="{cls}"' if cls else '') + '>')


def figure(pid, cls=''):
    ph = PHOTOS[pid]
    return (f'<figure class="photo {cls}">{img_tag(ph)}'
            f'<figcaption><b>{ph["cap"]}</b> · {credit(ph)}</figcaption></figure>')


# ---------------------------------------------------------------------------------------------------------------
# Mapa (equirectangular con escala cos(40°) en x; recuadro de Canarias abajo a la derecha)
# ---------------------------------------------------------------------------------------------------------------
COAST = [
    (-5.60, 36.01), (-5.35, 36.15), (-4.42, 36.70), (-3.50, 36.72), (-2.60, 36.72), (-2.19, 36.73),
    (-1.65, 37.40), (-0.75, 37.60), (-0.48, 38.20), (0.21, 38.73), (-0.30, 39.42), (0.18, 40.08),
    (0.88, 40.72), (1.22, 41.10), (2.18, 41.38), (3.18, 41.88), (3.32, 42.32), (3.08, 42.48),
    (1.72, 42.50), (0.70, 42.85), (-0.60, 42.80), (-1.40, 43.05), (-1.79, 43.37), (-2.92, 43.42),
    (-3.80, 43.47), (-5.00, 43.53), (-5.85, 43.65), (-7.00, 43.56), (-7.68, 43.76), (-8.30, 43.40),
    (-9.20, 43.18), (-9.30, 42.90), (-8.88, 42.22), (-8.87, 41.87), (-8.67, 41.15), (-8.88, 40.20),
    (-9.38, 39.38), (-9.50, 38.78), (-8.90, 38.48), (-8.80, 37.95), (-8.98, 37.02), (-7.92, 37.00),
    (-7.40, 37.18), (-6.95, 37.20), (-6.36, 36.80), (-6.20, 36.42), (-5.60, 36.01)]
BORDER = [
    (-8.87, 41.87), (-8.15, 42.08), (-7.90, 41.86), (-6.90, 41.95), (-6.20, 41.60), (-6.90, 41.00),
    (-6.85, 40.25), (-7.02, 39.66), (-7.50, 39.60), (-7.00, 39.00), (-7.30, 38.40), (-7.00, 38.00),
    (-7.50, 37.58), (-7.40, 37.18)]
TENERIFE = [(-16.92, 28.36), (-16.55, 28.58), (-16.12, 28.57), (-16.40, 28.30), (-16.70, 28.00),
            (-16.92, 28.20), (-16.92, 28.36)]
K, LON0, LAT1, CX = 52.0, -10.0, 44.3, math.cos(math.radians(40))


def xy(lon, lat):
    return round((lon - LON0) * CX * K + 20, 1), round((LAT1 - lat) * K + 10, 1)


W, H = round(xy(3.6, 0)[0] + 20), round(xy(0, 35.7)[1] + 10)
IX, IY, IK = W - 122, H - 110, 90


def ixy(lon, lat):
    return round(IX + (lon + 17.15) * math.cos(math.radians(28)) * IK, 1), round(IY + (28.75 - lat) * IK, 1)


def _path(pts, f, close=True):
    s = ' '.join(f'{"M" if i == 0 else "L"}{x},{y}' for i, (x, y) in enumerate(f(*p) for p in pts))
    return s + (' Z' if close else '')


def _label(p, x, y):
    """Label position and anchor for each park (tuned to avoid overlaps)."""
    s = p['slug']
    if s == 'teide':
        return x + 10, y + 22, 'start', 'Teide'
    if s == 'aiguestortes':
        return x + 4, y - 14, 'middle', 'Aigüestortes'
    if s == 'ordesa-y-monte-perdido':
        return x - 8, y + 22, 'end', p['name']
    if s in ('peneda-geres', 'sierra-nevada'):
        return x + 10, y + 4, 'start', p['name']
    return x - 10, y + 4, 'end', p['name']


def map_svg(uid, link=False, focus=None):
    title = 'Parques nacionales de montaña del proyecto EVEREST'
    desc = ('Mapa esquemático de la península ibérica y Tenerife con los ocho parques nacionales de montaña del '
            'proyecto, coloreados por región biogeográfica.')
    if focus:
        title = f'Situación del {PARK[focus]["full"]}'
        desc = f'Mapa esquemático con la situación del {PARK[focus]["full"]} entre los ocho parques del proyecto.'
    out = [f'<svg class="map" viewBox="0 0 {W} {H}" role="img" aria-labelledby="{uid}-t {uid}-d">',
           f'<title id="{uid}-t">{title}</title><desc id="{uid}-d">{desc}</desc>',
           f'<path class="land" d="{_path(COAST, xy)}"/>',
           f'<path class="border" d="{_path(BORDER, xy, close=False)}"/>',
           f'<rect class="inset" x="{IX - 8}" y="{IY - 26}" width="112" height="96" rx="6"/>',
           f'<text class="inset-label" x="{IX}" y="{IY - 10}">Islas Canarias</text>',
           f'<path class="land" d="{_path(TENERIFE, ixy)}"/>']
    for p in PARKS:
        x, y = (ixy if p['slug'] == 'teide' else xy)(p['lon'], p['lat'])
        cls = p['region'] + ((' focus' if p['slug'] == focus else ' faded') if focus else '')
        g = f'<g class="park {cls}"><circle cx="{x}" cy="{y}" r="6"/>'
        if not focus or p['slug'] == focus:
            tx, ty, anchor, text = _label(p, x, y)
            g += f'<text x="{round(tx, 1)}" y="{round(ty, 1)}" text-anchor="{anchor}">{text}</text>'
        g += '</g>'
        if link and not focus:
            g = f'<a href="@/parques/{p["slug"]}.html" aria-label="{p["full"]}">{g}</a>'
        out.append(g)
    out.append('</svg>')
    return '\n'.join(out)


def legend():
    return ('<ul class="legend" aria-label="Regiones biogeográficas">'
            + ''.join(f'<li class="{k}"><i></i>{v}</li>' for k, v in REGIONS.items()) + '</ul>')


# ---------------------------------------------------------------------------------------------------------------
# Diagrama de recuperación (memoria, figura 1: métricas S95, DIT, RRT y RET)
# ---------------------------------------------------------------------------------------------------------------
def recovery_svg():
    pts = [(60, 82), (80, 76), (100, 84), (120, 78), (140, 83), (160, 77), (180, 82), (198, 79), (202, 200),
           (215, 205), (230, 212), (250, 214), (270, 202), (300, 172), (330, 142), (360, 117), (390, 99), (420, 88),
           (445, 80), (470, 74), (495, 72), (525, 76), (560, 77), (615, 77)]
    d = 'M' + ' L'.join(f'{x},{y}' for x, y in pts)
    span = lambda x2, y, lab: (f'<line class="span" x1="203" y1="{y}" x2="{x2 - 3}" y2="{y}" marker-start="url(#arr-rec)" '
                               f'marker-end="url(#arr-rec)"/><text class="lab" x="{x2 + 8}" y="{y + 5}">{lab}</text>')
    guide = lambda x, y, lab: (f'<line class="guide" x1="{x}" y1="{y}" x2="{x}" y2="240"/>'
                               f'<text class="small" x="{x}" y="258" text-anchor="middle">{lab}</text>')
    return f'''<svg viewBox="0 0 640 350" role="img" aria-labelledby="rec-t rec-d">
<title id="rec-t">Métricas de resistencia y resiliencia a partir de una trayectoria tras una perturbación</title>
<desc id="rec-d">Serie temporal de una variable del ecosistema que cae bruscamente tras una perturbación y se recupera hasta
superar el nivel de referencia previo y estabilizarse. Se marcan la severidad (S95) y los tiempos hasta la inflexión
(DIT), hasta volver a la referencia (RRT) y hasta el nuevo equilibrio (RET).</desc>
<defs><marker id="arr-rec" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
<path class="arrowhead" d="M0,0 L10,5 L0,10 z"/></marker>
<marker id="arr-sev" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
<path class="arrowhead o" d="M0,0 L10,5 L0,10 z"/></marker></defs>
<path class="axis" d="M60,30 L60,240 L622,240"/>
<text class="small" x="620" y="232" text-anchor="end">Tiempo</text>
<text class="small" transform="translate(40 135) rotate(-90)" text-anchor="middle">Variable del ecosistema (p. ej., NDVI)</text>
<line class="refline" x1="60" y1="80" x2="620" y2="80"/>
<text class="small" x="66" y="60">Referencia previa</text>
<line class="event" x1="200" y1="40" x2="200" y2="240"/>
<text class="small" x="200" y="32" text-anchor="middle">Perturbación</text>
{guide(250, 214, 'tINF')}{guide(445, 80, 'tREF')}{guide(525, 76, 'tEQ')}
<path class="curve" d="{d}"/>
<line class="sev" x1="224" y1="83" x2="224" y2="203" marker-start="url(#arr-sev)" marker-end="url(#arr-sev)"/>
<text class="lab o" x="232" y="150">S95</text>
{span(250, 284, 'DIT')}{span(445, 310, 'RRT')}{span(525, 336, 'RET')}
</svg>'''


RECOVERY_TERMS = '''<dl class="terms">
<dt>S95</dt><dd>Severidad: diferencia entre el cuantil del 95 % justo después de la perturbación y el valor de referencia previo. Se relaciona con la resistencia del ecosistema.</dd>
<dt>DIT</dt><dd>Tiempo hasta la inflexión: cuándo la trayectoria cambia de dirección y empieza la recuperación.</dd>
<dt>RRT</dt><dd>Tiempo hasta volver al valor de referencia (resiliencia «ingenieril»).</dd>
<dt>RET</dt><dd>Tiempo hasta alcanzar un nuevo equilibrio (resiliencia ecológica).</dd>
</dl>'''


def recovery_figure():
    return (f'<figure class="diagram"><div class="table-wrap" style="border:0;margin:0">'
            f'<div style="min-width:560px">{recovery_svg()}</div></div>'
            f'<figcaption>Métricas de severidad y recuperación calculadas sobre series temporales de satélite '
            f'(adaptado de la figura 1 de la memoria del proyecto).</figcaption>{RECOVERY_TERMS}</figure>')


PIPELINE_STEPS = [
    ('blue', 'satellite', 'Satélites', 'MODIS, Landsat, Sentinel-2 y PlanetScope, procesados en Google Earth Engine'),
    ('green', 'layers', 'Variables Esenciales de la Biodiversidad', 'Composición, estructura y función: agua, energía y carbono'),
    ('teal', 'trend', 'Referencias y tendencias', 'Dinámicas de referencia, tendencias, anomalías y variabilidad espacial'),
    ('orange', 'people', 'Casos con gestores', 'Hábitats y especies, lagos de alta montaña y restauración'),
    ('purple', 'tool', 'MonitorEO', 'Herramienta abierta para gestores, científicos y ciudadanía'),
]
PIPELINE = ('<ol class="pipeline">' + ''.join(
    f'<li class="c-{c}"><span class="icon">{icon(i)}</span><b>{t}</b><span>{d}</span></li>' for c, i, t, d in PIPELINE_STEPS)
    + '</ol>')


# ---------------------------------------------------------------------------------------------------------------
# Tareas
# ---------------------------------------------------------------------------------------------------------------
JML, DAS, RZ, AM = 'Javier Martínez López', 'Domingo Alcaraz Segura', 'Regino Jesús Zamora Rodríguez', 'Ana Mellado García'
BPC, ITB, JMAM, SAC = 'Beatriz Pérez Cazorla', 'Ingrid Tatiana Bello Rodríguez', 'José Manuel Álvarez Martínez', 'Salvador Arenas Castro'
AJPL, JBL, JH, JG, BM = 'Antonio Jesús Pérez Luque', 'Jorge Bonache López', 'João Honrado', 'João Gonçalves', 'Bruno Marcos'
NP, JLL, AR, TP = 'Nuria Pistón', 'Joana Llodrà Llabrés', 'Andrea Ros', 'Thedmer Postma'
RK, MSA = 'Rohaifa Khaldi', 'Michael Sorochan Armstrong'

OBJECTIVES = [
    'Co-diseñar y co-crear un grupo de trabajo ciencia-gestión que lidere un cambio transformador basado en el uso, por '
    'parte de gestores y responsables de la toma de decisiones, de datos de teledetección científicamente sólidos para '
    'cumplir las obligaciones de reporte derivadas de las normativas europeas.',
    'Identificar y operativizar un conjunto de Variables Esenciales de la Biodiversidad derivadas de teledetección, '
    'científicamente sólidas y relevantes para la gestión, que caractericen la composición, la estructura y el '
    'funcionamiento de los ecosistemas y respondan a esas obligaciones.',
    'Caracterizar las dinámicas de referencia, la variabilidad espacial, las tendencias y las anomalías de las '
    'variables y métricas seleccionadas, y compararlas entre los parques nacionales de montaña.',
    'Probar y validar con los gestores el desempeño de las variables y métricas seleccionadas para evaluar y seguir el '
    'estado de conservación de especies y hábitats, los parámetros de calidad del agua y la recuperación tras '
    'perturbaciones y restauraciones.',
    'Co-producir e implementar una herramienta en línea de apoyo a la decisión, casi en tiempo real, para explotar los '
    'resultados del proyecto con tres tipos de usuarios (científicos, gestores y público general), y proporcionar '
    'guías y divulgación que apoyen la toma de decisiones, la gestión y la sensibilización pública.',
]

# Task cards show the specific objectives exactly as the proposal states them (section 3.1).
TASK_SUMMARIES = {f'T{i}': o for i, o in enumerate(OBJECTIVES, 1)}
GENERAL_OBJECTIVE = (
    'Sentar a gestores y científicos para co-diseñar, co-producir y validar un marco metodológico común, basado en la '
    'experiencia de MonitorEO, que proporcione variables científicamente sólidas y útiles para la gestión, junto con '
    'capacidades de seguimiento y modelización, para informar sobre el estado de conservación de especies y hábitats '
    '(Directiva Hábitats), la calidad del agua (Directiva Marco del Agua) y la recuperación de los ecosistemas tras '
    'perturbaciones y restauraciones (Reglamento de Restauración de la Naturaleza).')


def task_card(code):
    n = code[1]
    return (f'<article class="card task-card c-{TASK_COLORS[code]}"><a class="head" href="@/proyecto/t{n}.html" '
            f'style="text-decoration:none;color:inherit" aria-label="Tarea {n}: {TASK_NAMES[code]}">'
            f'<span class="num">T{n}</span>{icon(TASK_ICONS[code])}</a><div class="body">'
            f'<span class="tag">Objetivo {n}</span><h3><a href="@/proyecto/t{n}.html">{TASK_NAMES[code]}</a></h3>'
            f'<p>{TASK_SUMMARIES[code]}</p><a class="more" href="@/proyecto/t{n}.html">Ver la tarea</a></div></article>')


def tasks_cards():
    return '<div class="cards">' + ''.join(task_card(c) for c in TASK_SUMMARIES) + '</div>'


def factbox(items):
    return '<dl class="factbox">' + ''.join(f'<div><dt>{k}</dt><dd>{v}</dd></div>' for k, v in items) + '</dl>'


def leads(items):
    return '<ul class="leads">' + ''.join(f'<li>{i}</li>' for i in items) + '</ul>'


def park_badges(slugs):
    return '<ul class="badges">' + ''.join(
        f'<li class="{PARK[s]["region"]}"><a href="@/parques/{s}.html"><i class="dot"></i> {PARK[s]["name"]}</a></li>'
        for s in slugs) + '</ul>'


TASK_HERO = {1: 'sierra-de-guadarrama', 2: 'borreguil', 3: 'nieve-satelite', 4: 'sierra-nevada', 5: 'picos-de-europa'}


def task_page(n, title, lede, facts, sections):
    body = factbox(facts) + ''.join(sections)
    nav = []
    if n > 1:
        nav.append(f'<a class="more" href="@/proyecto/t{n - 1}.html" style="margin-right:24px">← Tarea {n - 1}</a>')
    if n < 5:
        nav.append(f'<a class="more" href="@/proyecto/t{n + 1}.html">Tarea {n + 1}</a>')
    body += '<p style="margin-top:40px">' + ''.join(nav) + '</p>'
    return dict(title=f'Tarea {n} · {title}', crumbs=[('Proyecto', None), ('Tareas', '@/proyecto/tareas.html')],
                h1=f'T{n} · {title}', lede=lede, body=body, color=TASK_COLORS[f'T{n}'], img=TASK_HERO[n])


TASK_DETAIL = {}
TASK_DETAIL[1] = task_page(
    1, 'Implicación de actores', OBJECTIVES[0],
    [('Responsable', RZ), ('Equipo', f'{JML}, {DAS}, {JBL}, {NP}, {AR}, {JMAM}, {BPC}, {ITB}'), ('Objetivo específico', '1'),
     ('Estado', 'En curso')],
    ['<section><h2 id="que-hacemos">Qué hacemos</h2>'
     '<p>Revisamos la literatura científica y los documentos de gestión, y usamos encuestas y reuniones para identificar '
     'a los actores clave. Con ellos preparamos un taller inicial presencial, dos talleres en línea para analizar casos '
     'de estudio y un taller final de validación y formación. Los talleres reúnen a gestores de los parques, científicos '
     'e instituciones ambientales nacionales e internacionales para:</p>'
     + leads(['informarles de los objetivos y discutir los resultados preliminares, las variables, los indicadores y los métodos;',
              'alinear el proyecto con sus necesidades reales y aprovechar su conocimiento experto y sus datos sobre los '
              'problemas de gestión y las obligaciones de reporte de cada parque;',
              'seleccionar los casos de estudio de la Tarea 4;',
              'asegurar que MonitorEO se adopte en sus planes de seguimiento y evaluación una vez acabe el proyecto, y '
              'extenderla a otros espacios de la red Natura 2000.'])
     + '</section>',
     '<section><h2 id="avances">Avances</h2>'
     + leads(['<strong>Co-diseño con el Espacio Natural Sierra Nevada.</strong> Cinco reuniones de co-diseño, validación '
              'y formación entre diciembre de 2024 y enero de 2026, con 9 gestores y 19 participaciones. Las necesidades '
              'priorizadas: zonas para repoblación, eficacia de los tratamientos selvícolas, pastos, nieve y agua.',
              '<strong>Cuestionario inicial</strong> a los gestores de los ocho parques nacionales de montaña.',
              '<strong>Red ciencia-gestión.</strong> Mapa de actores e invitación a una red de unos 135 contactos de '
              'España y Portugal (noviembre de 2025).',
              '<strong>Red de Parques Nacionales.</strong> Presentación en el XIII Seminario de Seguimiento a Largo Plazo '
              '(Valsaín, 2024) y en un seminario del MITECO y el CENEAM (Valsaín, 2026). Reunión con el Organismo '
              'Autónomo Parques Nacionales sobre el uso de MonitorEO y su integración con REMOTE (30 de octubre de 2026).',
              '<strong>Colaboraciones.</strong> Datos y casos de estudio aportados por la Junta de Andalucía, la REDIAM, '
              'la Confederación Hidrográfica del Cantábrico, el Parque Nacional de la Sierra de Guadarrama y el CEAB-CSIC, '
              'y sinergias con los proyectos MOTIVATE, PRESINMED y FIRE-TRAN.'])
     + '</section>',
     '<section><h2 id="proximos-pasos">Próximos pasos</h2>'
     + leads(['<strong>Taller nacional ciencia-gestión</strong> (enero–febrero de 2027), organizado con el proyecto '
              'MOTIVATE, el servicio Copernicus de vigilancia terrestre (CLMS), IALE-España y la red BigBioData de la AEET.',
              'Talleres en línea para analizar los casos de estudio de cada parque.',
              'Taller final presencial de validación y formación en MonitorEO.'])
     + '</section>',
     '<section><h2 id="parques">Parques</h2><p>Participan los gestores de los ocho parques.</p>'
     + park_badges([p['slug'] for p in PARKS]) + '</section>'])

TASK_DETAIL[2] = task_page(
    2, 'Variables Esenciales de la Biodiversidad', OBJECTIVES[1],
    [('Responsable', JML), ('Equipo', f'{DAS}, {JMAM}, {SAC}, {AJPL}, {BPC}, {ITB}'), ('Objetivo específico', '2'),
     ('Estado', 'En curso')],
    ['<section><h2 id="que-hacemos">Qué hacemos</h2>'
     '<p>A partir de una revisión bibliográfica, recopilamos series temporales de variables de satélite en los parques '
     'que informan sobre la <strong>composición</strong> (cubiertas del suelo, masas de agua, tipos de hábitat), la '
     '<strong>estructura</strong> (biomasa, fragmentación, altura y heterogeneidad de la vegetación, índice de área '
     'foliar) y la <strong>función</strong> de los ecosistemas: agua, energía y carbono.</p>'
     '<p>De cada variable calculamos cada año métricas con significado biológico y útiles para la gestión: la media '
     'anual (cantidad total), la variabilidad estacional (estacionalidad) y las fechas del máximo y del mínimo '
     '(fenología). Para quedarnos con las métricas más informativas e independientes aplicamos análisis de componentes '
     'principales (PCA) y de correlación. Las seleccionadas son candidatas a Variables Esenciales de la Biodiversidad que se evalúan en las '
     'aplicaciones de la Tarea 4.</p>'
     + figure('satelite')
     + '<p><a class="more" href="@/proyecto/variables.html">Qué variables usamos</a></p></section>',
     '<section><h2 id="avances">Avances</h2>'
     + leads(['<strong>Indicadores oficiales.</strong> Base de datos trazable de unos 90 indicadores de las metodologías '
              'europea y estatal de evaluación del estado de conservación, compilados con ayuda de inteligencia '
              'artificial. Una revisión sistemática muestra que alrededor del 40 % son medibles por teledetección.',
              '<strong>Selección de variables.</strong> Procedimiento de selección (correlación, factor de inflación de '
              'la varianza, PCA, k-means, NMDS y t-SNE) aplicado a los borreguiles, cuyas firmas funcionales los '
              'distinguen de otros pastizales, y a los Tipos Funcionales de Ecosistemas (EFT).',
              '<strong>Tipos Funcionales de Ecosistemas validados con torres de flujo.</strong> Con 50 torres de '
              'covarianza turbulenta de FLUXNET en Europa, los EFT discriminan la dinámica del intercambio neto de CO₂ '
              '(kappa = 0,95; Cazorla et al., 2026, <em>Biogeosciences</em>).',
              '<strong>Catálogo de variables</strong> de MonitorEO, con las variables de satélite disponibles para los gestores.'])
     + '</section>',
     '<section><h2 id="proximos-pasos">Próximos pasos</h2>'
     + leads(['Cerrar el conjunto de variables y métricas para cada obligación de reporte y evaluarlo en los casos de la Tarea 4.',
              'Marco de Tipos Funcionales de Ecosistemas a escala global, con equipos de Argentina, Uruguay, Estados '
              'Unidos y Alemania (manuscrito en preparación).'])
     + '</section>'])

TASK_DETAIL[3] = task_page(
    3, 'Dinámicas de referencia', OBJECTIVES[2],
    [('Responsable', DAS), ('Equipo', f'{JML}, {JMAM}, {MSA}, {RK}, {AJPL}, {BPC}'), ('Objetivo específico', '3'),
     ('Estado', 'En curso')],
    ['<section><h2 id="que-hacemos">Qué hacemos</h2>'
     + leads(['<strong>Dinámicas de referencia:</strong> curva estacional media de cada variable, sus descriptores '
              'estacionales y fenológicos y su variabilidad interanual histórica.',
              '<strong>Tendencias:</strong> cambios graduales a largo plazo con las pruebas de Mann-Kendall y la '
              'pendiente de Sen.',
              '<strong>Anomalías:</strong> desviaciones respecto a la variabilidad histórica, en duración e intensidad, '
              'como señales tempranas de cambio.',
              '<strong>Variabilidad espacial:</strong> heterogeneidad de los Tipos Funcionales de Ecosistemas y '
              'diversidad funcional (riqueza y rareza). Su evolución revela si el paisaje se homogeneiza.'])
     + '</section>',
     '<section><h2 id="avances">Avances</h2>'
     + leads(['<strong>Borreguiles.</strong> Espacio funcional de referencia definido a partir de las zonas bien '
              'conservadas, que permite medir la distancia de cada borreguil a sus condiciones de referencia.',
              '<strong>Nieve.</strong> Detección calibrada con transectos de campo y sensores TOMST-TMS4 para Landsat, '
              'Sentinel-2 y PlanetScope; serie de innivación de Landsat de 1985 a 2025 en Sierra Nevada, con métricas de '
              'duración, último día y frecuencia a lo largo de los gradientes topográficos.',
              '<strong>Verdor.</strong> Tendencias de NDVI de 1985 a 2022: en Sierra Nevada hay menos nieve y más verdor.',
              '<strong>Paisaje.</strong> Unidades funcionales del paisaje de Sierra Nevada a partir de EFT (manuscrito en revisión).',
              '<strong>Herramientas.</strong> eHabitat+ actualizado con Sentinel-2; tendencias (Mann-Kendall y Sen) y '
              'anomalías calculables en línea en MonitorEO, con métricas definidas junto con la Universidad de Oviedo.'])
     + figure('borreguil') + '</section>',
     '<section><h2 id="proximos-pasos">Próximos pasos</h2>'
     + leads(['Extender las dinámicas de referencia, las tendencias y las anomalías a los ocho parques y compararlas '
              'entre regiones biogeográficas.',
              'Contrastar con datos de campo la hipótesis de que las montañas de verano más templado y lluvioso se ven '
              'menos afectadas que las mediterráneas.'])
     + '</section>'])

TASK_DETAIL[4] = task_page(
    4, 'Aplicación a la gestión', OBJECTIVES[3],
    [('Responsables', f'{JML} (4.1.1 y 4.2) y {DAS} (4.1.2 y 4.3)'),
     ('Equipo', f'{RZ}, {JMAM}, {SAC}, {JH}, {JG}, {BM}, {RK}, {MSA}, {JLL}, {TP}, {BPC}, {ITB}'), ('Objetivo específico', '4'),
     ('Estado', 'En curso')],
    ['<section><p class="intro">Con los gestores de cada parque elegimos casos de estudio para tres preguntas de '
     'gestión. Siempre que es posible, calibramos y validamos los índices de satélite con los datos de campo de los '
     'programas de seguimiento.</p></section>',
     '<section class="c-green"><h2 id="habitats">4.1 · Hábitats y especies</h2>'
     '<p class="kicker">MonitorEO4Habitats · MonitorEO4Species · Directiva Hábitats, art. 17</p>'
     '<p>Cartografiamos hábitats de interés comunitario con datos de campo clasificados según EUNIS y modelos de '
     'aprendizaje automático alimentados con teledetección de alta resolución. Separamos el área realmente ocupada del '
     'área potencial y evaluamos su estado de conservación con las condiciones de referencia de la Tarea 3. Para las '
     'especies, modelizamos la idoneidad del hábitat de especies emblemáticas a varias escalas y seguimos sus tendencias.</p>'
     + figure('borreguil') + '<h3>Avances</h3>'
     + leads(['<strong>Borreguiles (6230*).</strong> Los gestores y las sinergias con PRESINMED han priorizado este '
              'hábitat prioritario, muy vulnerable a la reducción de la nieve. Modelo Random Forest con 50 variables y '
              '584 puntos verificados en 20 cuencas (AUC = 0,87 en validación cruzada por cuencas).',
              '<strong>Condición ecológica.</strong> Indicador basado en la distancia de Mahalanobis: tras cartografiar '
              'los borreguiles, identifica qué zonas tienen valores de las variables relevantes similares a los de las '
              'zonas bien conservadas.',
              '<strong>Verdad terreno.</strong> Aplicación de verificación con aprendizaje activo para suplir la escasez '
              'de datos de campo.',
              '<strong>Bases de datos de vegetación.</strong> Con el proyecto MOTIVATE se ha validado espacialmente el '
              '57 % de las parcelas de ReSurveyEurope (manuscrito en revisión).',
              '<strong>Especies.</strong> Caso piloto seleccionado con los gestores.',
              '<strong>Pastos.</strong> Modelo de energía metabólica de los pastos de Andalucía, a petición de los gestores.'])
     + '</section>',
     '<section class="c-teal"><h2 id="lagos">4.2 · Lagos de alta montaña</h2>'
     '<p class="kicker">MonitorEO4Water · Directiva Marco del Agua</p>'
     '<p>Relacionamos los muestreos de clorofila-a, materia orgánica disuelta coloreada y sólidos en suspensión con '
     'índices espectrales de satélite para seguir la calidad del agua de lagos pequeños e inaccesibles.</p>'
     + figure('aiguestortes') + '<h3>Avances</h3>'
     + leads(['<strong>Clorofila-a en 56 lagunas</strong> de Sierra Nevada muestreadas entre 2020 y 2023: comparación de '
              'correcciones atmosféricas y modelos con Sentinel-2; mapas cada unos cinco días, con R² por laguna de hasta '
              '0,88 (Llodrà-Llabrés et al., 2026, <em>Water Resources Research</em>).',
              '<strong>Lagunas pequeñas.</strong> Solo 5 de las 56 lagunas se resuelven bien a 10 m, así que se incorpora '
              'PlanetScope: herramienta de delimitación de láminas de agua validada frente a digitalizaciones.',
              '<strong>Nieve y hielo.</strong> Tendencias de nieve en la lámina de agua, la orilla y la cuenca, y papel '
              'del hielo y la topografía en el calentamiento de las lagunas (manuscrito en revisión).',
              '<strong>Otros parques.</strong> Series de clorofila y sólidos en suspensión de Peñalara (Guadarrama), '
              'Aigüestortes y Picos de Europa para extender los modelos.'])
     + '</section>',
     '<section class="c-orange"><h2 id="recuperacion">4.3 · Recuperación y restauración</h2>'
     '<p class="kicker">MonitorEO4Restoration · Reglamento de Restauración de la Naturaleza</p>'
     '<p>Con los gestores identificamos las perturbaciones y restauraciones de cada parque y comparamos la dinámica de '
     'las variables antes, durante y después con zonas similares no afectadas. Así medimos la severidad y la '
     'resiliencia del ecosistema.</p>' + recovery_figure() + '<h3>Avances</h3>'
     + leads(['<strong>Aclareos.</strong> NDVI mensual de Landsat (1990–2025) en 80 parcelas de pinar del Observatorio '
              'de Cambio Global de Sierra Nevada con tratamientos del 0 al 100 %: los aclareos más intensos aumentan el '
              'NDVI y mitigan el decaimiento forestal. El caso se ha presentado a los gestores.',
              '<strong>Gestión posincendio.</strong> Retirar la madera quemada reduce la persistencia de la nieve '
              '(Cazorla et al., <em>Ecological Applications</em>, en revisión).',
              '<strong>Acequias.</strong> El NDVI aumenta tras restaurar acequias tradicionales, es mayor cerca del cauce '
              'y se mantiene en estiaje.',
              '<strong>Incendios.</strong> Diseño, con el proyecto FIRE-TRAN, de un trabajo de fin de máster sobre la '
              'recuperación tras el incendio de Los Guájares (Granada, 2022).'])
     + figure('acequia') + '</section>',
     '<section><h2 id="proximos-pasos">Próximos pasos</h2>'
     + leads(['Priorizar el caso piloto de especies (Tarea 4.1.2).',
              'Aplicación de evaluación del estado de conservación para usuarios sin programación.',
              'Extender los modelos de calidad del agua a los lagos de Guadarrama, Aigüestortes y Picos de Europa.',
              'Métricas de resiliencia tras incendios en Peneda-Gerês con el CIBIO-InBIO.'])
     + '</section>'])

TASK_DETAIL[5] = task_page(
    5, 'Transferencia', OBJECTIVES[4],
    [('Responsable', AM), ('Equipo', f'{JML}, {DAS}, {RZ}, {JBL}, {TP}, {NP}, {AR}, {JMAM}, {BPC}'), ('Objetivo específico', '5'),
     ('Estado', 'En curso')],
    ['<section><h2 id="que-hacemos">Qué hacemos</h2>'
     '<p><strong>5.1 · Herramienta de apoyo a la decisión.</strong> Incorporamos a MonitorEO los nuevos análisis que '
     'piden los gestores en los talleres, en cuatro ciclos de desarrollo co-diseñados, probados y validados con '
     'investigadores y gestores, siguiendo los principios FAIR. La documentación y los tutoriales se actualizan con '
     'cada novedad.</p>'
     '<p><strong>5.2 · Difusión y reporte.</strong> Formación en línea tras cada versión de MonitorEO, artículos '
     'científicos y congresos, guías y datos para los planes de seguimiento de los parques, y materiales divulgativos: '
     'un vídeo documental, una exposición de pósteres para los centros de visitantes e infografías de los casos de '
     'estudio.</p></section>',
     '<section><h2 id="avances">Avances</h2>'
     + leads(['<strong>MonitorEO</strong> mejorada: filtrado de píxeles, análisis de grandes áreas, módulo de '
              'microclima, visor de resultados, complemento de QGIS y código abierto en GitHub con DOI.',
              '<strong>Aplicaciones complementarias</strong> para usuarios sin programación: lagunas, verdad terreno y '
              'cartografía de borreguiles, estado de conservación y modelos de idoneidad.',
              '<strong>Documentación:</strong> manual en línea, manuales en español e inglés, videotutoriales y '
              'formulario de incidencias (desde abril de 2025).',
              '<strong>Formación a gestores</strong> del Espacio Natural Sierra Nevada (27 de enero de 2026).',
              '<strong>Resultados:</strong> 2 artículos, 1 capítulo aceptado, varios manuscritos en revisión, 16 '
              'contribuciones a congresos y jornadas y actividades de divulgación.'])
     + figure('nieve-satelite')
     + '<p><a class="more" href="@/resultados/recursos.html">Recursos y divulgación</a></p></section>',
     '<section><h2 id="proximos-pasos">Próximos pasos</h2>'
     + leads(['Ciclos de desarrollo de MonitorEO con una empresa externa a partir de las propuestas del taller nacional.',
              'Integración con REMOTE y uso por el Organismo Autónomo Parques Nacionales.',
              'Aplicación de pastos y acequias.',
              'Guías para gestores, vídeo documental y exposición de pósteres en los centros de visitantes.'])
     + '</section>'])


# ---------------------------------------------------------------------------------------------------------------
# Equipo
# ---------------------------------------------------------------------------------------------------------------
TEAM = [
    (JML, 'ip', 'Investigador principal', 'Universidad de Granada', 'Teledetección, modelización y servicios de datos ambientales. Coordina MonitorEO.', 'T2, T4.1.1, T4.2'),
    (DAS, 'ip', 'Investigador principal', 'Universidad de Granada · IISTA-CEAMA', 'Funcionamiento de los ecosistemas y servicios ecosistémicos desde satélite.', 'T3, T4.1.2, T4.3'),
    (RZ, 'inv', 'Equipo de investigación', 'Universidad de Granada', 'Ecología de alta montaña. Coordinador científico del Observatorio de Cambio Global de Sierra Nevada.', 'T1'),
    (AM, 'inv', 'Equipo de investigación', 'LifeWatch ERIC · Oficina ICT-Core (Sevilla)', 'Transferencia de conocimiento a gestores, responsables políticos y ciudadanía.', 'T5'),
    (BPC, 'inv', 'Equipo de investigación', 'Universidad de Granada', 'Teledetección y conservación. Desarrollo y coordinación técnica del proyecto.', 'T1–T5'),
    (ITB, 'trabajo', 'Investigadora predoctoral', 'Universidad de Granada', 'Variables de teledetección para evaluar el estado de conservación de los hábitats.', 'T1, T2, T4'),
    # Equipo de trabajo según la memoria del proyecto (apartado 3.2.2), con sus tareas (apartado 3.2.3)
    (JMAM, 'trabajo', 'Equipo de trabajo', 'Universidad de Oviedo · IMIB', 'Teledetección y cartografía de hábitats.', 'T1, T2, T3, T4.1, T4.3, T5.2'),
    (JBL, 'trabajo', 'Equipo de trabajo', 'Organismo Autónomo Parques Nacionales', 'Gestión de parques nacionales. Co-desarrollador de REMOTE.', 'T1, T5'),
    (NP, 'trabajo', 'Equipo de trabajo', 'Observatorio de Cambio Global de Sierra Nevada · IISTA-CEAMA', 'Co-creación de conocimiento. Co-coordinadora del grupo de trabajo de servicios ecosistémicos de GEO BON.', 'T1, T5.2'),
    (JLL, 'trabajo', 'Equipo de trabajo', 'Observatorio de Cambio Global de Sierra Nevada · IISTA-CEAMA', 'Ecología de aguas continentales.', 'T4.2'),
    (AR, 'trabajo', 'Equipo de trabajo', 'Observatorio de Cambio Global de Sierra Nevada · IISTA-CEAMA', 'Gestión de datos, interoperabilidad e interfaz ciencia-política.', 'T1, T5.2'),
    (TP, 'trabajo', 'Equipo de trabajo', 'Observatorio de Cambio Global de Sierra Nevada · IISTA-CEAMA', 'Teledetección.', 'T4.2, T5.1'),
    (SAC, 'trabajo', 'Equipo de trabajo', 'Universidad de Córdoba', 'Modelos de distribución de especies.', 'T2, T4.1.2'),
    (AJPL, 'trabajo', 'Equipo de trabajo', 'IISTA-CEAMA · Universidad de Granada', 'Teledetección y ecología forestal.', 'T2, T3'),
    (JH, 'trabajo', 'Equipo de trabajo', 'CIBIO-InBIO · Universidade do Porto', 'Cartografía de vegetación y teledetección.', 'T4.1, T4.3'),
    (JG, 'trabajo', 'Equipo de trabajo', 'CIBIO-InBIO · Universidade do Porto', 'Teledetección, modelos de distribución y resiliencia de los ecosistemas.', 'T4.1.2, T4.3'),
    (BM, 'trabajo', 'Equipo de trabajo', 'CIBIO-InBIO · Universidade do Porto', 'Teledetección y recuperación de los ecosistemas tras perturbaciones.', 'T4.3'),
    (RK, 'trabajo', 'Equipo de trabajo', 'Universidad de Granada · Instituto DaSCI', 'Teledetección e inteligencia artificial.', 'T3, T4.1.1'),
    (MSA, 'trabajo', 'Equipo de trabajo', 'Universidad de Granada · Computational Data Science Lab', 'Aprendizaje automático y ciencia de datos.', 'T3, T4.1.1'),
]
GROUPS = [('ip', 'Investigadores principales'), ('inv', 'Equipo de investigación'), ('trabajo', 'Equipo de trabajo')]


def initials(name):
    """First given name + first surname (Spanish names carry two surnames)."""
    parts = name.split()
    return parts[0][0] + (parts[-2][0] if len(parts) >= 3 else parts[-1][0])


COLLABORATORS = [
    ('Pablo Guerrero y Carlos Navarro', 'desarrollo de MonitorEO y casos de estudio'),
    ('Javier Cabello', 'Universidad de Almería: Tipos Funcionales de Ecosistemas'),
    ('Carmen Pérez-Martínez y Manuel Villar-Argaiz', 'Instituto del Agua, Universidad de Granada: limnología de las lagunas'),
    ('Jorge Castro y Alexandro B. Leverkus', 'Universidad de Granada: gestión posincendio'),
    ('Juan Lorite', 'Universidad de Granada: tipos de borreguil'),
    ('Borja Jiménez-Alfaro', 'Universidad de Oviedo – IMIB: proyecto MOTIVATE'),
    ('Ignacio Granados', 'Parque Nacional de la Sierra de Guadarrama: lagunas de Peñalara'),
    ('Lluís Camarero', 'CEAB-CSIC: lagos de Aigüestortes'),
]

INSTITUTIONS = [
    ('UGR', 'Universidad de Granada', 'Departamentos de Ecología y de Botánica · Instituto Interuniversitario de Investigación del Sistema Tierra en Andalucía (IISTA-CEAMA) · Observatorio de Cambio Global de Sierra Nevada · Instituto de Ciencia de Datos e Inteligencia Computacional (DaSCI) · Computational Data Science Lab', 'Granada, España', 'Entidad beneficiaria · coordinación · Tareas 1–5'),
    ('LifeWatch ERIC', 'LifeWatch ERIC', 'Infraestructura europea de e-ciencia para la investigación en biodiversidad y ecosistemas · Oficina ICT-Core', 'Sevilla, España', 'Responsable de la Tarea 5 · infraestructura de MonitorEO'),
    ('OAPN', 'Organismo Autónomo Parques Nacionales', 'Red de Parques Nacionales · sistema de seguimiento por satélite REMOTE', 'Madrid, España', 'Tareas 1 y 5 · enlace con los parques'),
    ('Uniovi · IMIB', 'Universidad de Oviedo', 'Instituto Mixto de Investigación en Biodiversidad (Universidad de Oviedo, CSIC y Principado de Asturias)', 'Mieres, España', 'Tareas 2, 3 y 4.1.1 · cartografía de hábitats'),
    ('UCO', 'Universidad de Córdoba', 'Modelización de la distribución de especies', 'Córdoba, España', 'Tareas 2 y 4.1.2'),
    ('CIBIO-InBIO', 'Universidade do Porto', 'Centro de Investigação em Biodiversidade e Recursos Genéticos', 'Vairão, Portugal', 'Tareas 4.1 y 4.3 · caso de estudio de Peneda-Gerês'),
]

PARTNER_ORGS = [
    ('Junta de Andalucía', 'Consejería de Sostenibilidad y Medio Ambiente, Espacio Natural Sierra Nevada y Red de Información Ambiental de Andalucía (REDIAM): co-diseño de MonitorEO, casos de estudio, datos de campo y cartografía de hábitats.'),
    ('Agencia de Medio Ambiente y Agua de Andalucía (AMAYA)', 'selección de casos de estudio de tratamientos selvícolas y restauración.'),
    ('MITECO y CENEAM', 'grupo de trabajo sobre seguimiento de hábitats y seminarios de la Red de Parques Nacionales.'),
    ('Confederación Hidrográfica del Cantábrico', 'calidad del agua de los lagos de Picos de Europa.'),
    ('Parque Nacional de la Sierra de Guadarrama', 'calidad del agua de las lagunas de Peñalara.'),
    ('Centro de Estudios Avanzados de Blanes (CEAB-CSIC)', 'calidad del agua de los lagos de Aigüestortes.'),
    ('GESTEMASUR', 'aplicación de los Tipos Funcionales de Ecosistemas a las microrreservas de flora de la Estación de Esquí y Montaña de Sierra Nevada y muestreos de borreguiles.'),
    ('Copernicus Land Monitoring Service', 'co-organización del taller nacional de 2027.'),
]

PROJECTS = [
    ('SmartEcoMountains', 'https://smartecomountains.lifewatch.dev', 'LifeWatch ERIC. Proyecto en el que nació MonitorEO.'),
    ('NevadEO', None, 'Observaciones de la Tierra para caracterizar y seguir el funcionamiento de los ecosistemas de Sierra Nevada (FEDER Andalucía, C-EXP-074-UGR23).'),
    ('Mountain BIOREFUGES', None, 'Refugios biogénicos como moduladores del cambio climático en la montaña (TED2021-130888B-I00).'),
    ('EARTHCUL', None, 'Teledetección de los servicios ecosistémicos culturales en áreas protegidas.'),
    ('MOTIVATE', None, 'Biodiversa+. Seguimiento de hábitats europeos con inventarios de vegetación y teledetección.'),
    ('PRESINMED', 'https://presinmed.eu', 'Biodiversa+. Soluciones basadas en la naturaleza para los pastos húmedos de la alta montaña mediterránea.'),
    ('FIRE-TRAN', None, 'Recuperación de los ecosistemas tras los incendios.'),
]
NETWORKS = [('LifeWatch ERIC', 'https://www.lifewatch.eu'), ('GEO BON', 'https://geobon.org/ebvs'),
            ('GLORIA', 'https://obsnev.es/proyecto-gloria'), ('GEO Mountains', 'https://www.geomountains.org'),
            ('eLTER', 'https://elter-ri.eu'), ('NEMOR', 'https://nemor.creaf.cat'),
            ('Observatorio de Cambio Global de Sierra Nevada', 'https://obsnev.es')]


# ---------------------------------------------------------------------------------------------------------------
# Noticias (más recientes primero)
# ---------------------------------------------------------------------------------------------------------------
NEWS = [
    ('2026-11', 'Noviembre de 2026', 'proyecto', 'Nueva web del proyecto',
     'Estrenamos la web de EVEREST: objetivos, tareas, parques y equipo y, a medida que avance el proyecto, '
     'resultados, datos y materiales para gestores y ciudadanía.'),
    ('2026-10-30', '30 de octubre de 2026', 'gestion', 'Reunión con el Organismo Autónomo Parques Nacionales',
     'Reunión en línea con el OAPN para estudiar el uso de MonitorEO en la Red de Parques Nacionales y su posible '
     'integración con REMOTE, el sistema de seguimiento por satélite de la Red.'),
    ('2026-09-04', '4–6 de septiembre de 2026', 'divulgacion', 'Borreguiles en las VII Jornadas Lagunas de Sierra Nevada',
     'Presentamos la cartografía y la evaluación del estado de conservación de los pastizales húmedos de alta montaña '
     'mediante teledetección.'),
    ('2026-06-22', '22–26 de junio de 2026', 'congreso', 'Variables Esenciales de la Biodiversidad para el estado de conservación, en el simposio de la IAVS',
     'En el 68.º Simposio Anual de la Asociación Internacional de Ciencia de la Vegetación (Gijón) presentamos qué '
     'variables de teledetección son útiles para evaluar el estado de conservación de los hábitats en las áreas '
     'protegidas de montaña.'),
    ('2026-06-01', '1–5 de junio de 2026', 'congreso', 'Nieve y microclima desde el satélite, en Montpellier',
     'En la III Microclimate Ecology and Biogeography Conference mostramos la validación de la detección de nieve con '
     'varios satélites y sensores a ras de suelo en Sierra Nevada, y la integración del microclima en MonitorEO.'),
    ('2026-04-22', '22–23 de abril de 2026', 'gestion', 'EVEREST y MonitorEO en el seminario de hábitats del MITECO',
     'En Valsaín (Segovia) presentamos el proyecto y la herramienta en un seminario del MITECO y el CENEAM sobre la '
     'mejora del conocimiento de los hábitats con nuevas tecnologías.'),
    ('2026-03', 'Marzo de 2026', 'publicacion', 'La clorofila de las lagunas pequeñas, desde el espacio',
     '<em>Water Resources Research</em> publica la comparación de correcciones atmosféricas y modelos para estimar la '
     'clorofila-a con Sentinel-2 en las lagunas de alta montaña de Sierra Nevada.'),
    ('2026-02', '2026', 'publicacion', 'Los Tipos Funcionales de Ecosistemas, validados con torres de flujo',
     '<em>Biogeosciences</em> publica que los Tipos Funcionales de Ecosistemas derivados de satélite discriminan la '
     'dinámica del intercambio neto de CO₂ medida en 50 torres de FLUXNET en Europa. '
     + ext('https://doi.org/10.5194/bg-23-1223-2026', 'Leer el artículo') + '.'),
    ('2026-01-27', '27 de enero de 2026', 'gestion', 'Formación en MonitorEO para el Espacio Natural Sierra Nevada',
     'Sesión de formación y validación con técnicos del Espacio Natural, la quinta reunión de co-diseño de la '
     'herramienta desde diciembre de 2024.'),
    ('2025-11-17', '17 de noviembre de 2025', 'gestion', 'Arranca la red ciencia-gestión',
     'Invitamos a unos 135 contactos de España y Portugal, identificados en el mapa de actores del proyecto, a sumarse '
     'a la red ciencia-gestión de EVEREST.'),
    ('2025-10-28', '28–31 de octubre de 2025', 'congreso', 'Los lagos de los Pirineos',
     'Presentamos EVEREST en el taller «The Eyes on Pirineu\'s lakes» de la Universitat de Barcelona.'),
    ('2025-09-14', '14–18 de septiembre de 2025', 'congreso', 'EVEREST en la International Mountain Conference',
     'Comunicación oral sobre el proyecto en la International Mountain Conference (IMC25), en Innsbruck (Austria).'),
    ('2025-07-18', '18–20 de julio de 2025', 'divulgacion', 'Jornadas Lagunas de Sierra Nevada',
     'Participamos en la campaña anual de ciencia ciudadana en las lagunas de Sierra Nevada.'),
    ('2024-12-05', '5 de diciembre de 2024', 'gestion', 'Primera reunión de co-diseño con el Espacio Natural Sierra Nevada',
     'Empieza el co-diseño de MonitorEO con los técnicos del Espacio Natural, que priorizan sus necesidades de seguimiento.'),
    ('2024-11-07', '7–9 de noviembre de 2024', 'congreso', 'EVEREST en el congreso de las montañas de Sierra Nevada',
     'Presentamos el proyecto en el II Congreso Internacional de las Montañas de Sierra Nevada (CIMAS), en Granada.'),
    ('2024-09-30', '30 de septiembre – 2 de octubre de 2024', 'gestion', 'Presentación en la Red de Parques Nacionales',
     'Presentamos EVEREST en el XIII Seminario de Seguimiento a Largo Plazo en la Red de Parques Nacionales, en Valsaín (Segovia).'),
]
NEWS_TAGS = {'proyecto': 'Proyecto', 'gestion': 'Gestión', 'congreso': 'Congreso', 'publicacion': 'Publicación',
             'divulgacion': 'Divulgación'}
NEWS_COLORS = {'proyecto': 'blue', 'gestion': 'orange', 'congreso': 'purple', 'publicacion': 'green', 'divulgacion': 'teal'}


# ---------------------------------------------------------------------------------------------------------------
# Navegación
# ---------------------------------------------------------------------------------------------------------------
NAV = [
    ('proyecto', 'Proyecto', 'blue', [('Resumen y objetivos', 'proyecto/index.html'), ('Variables Esenciales de la Biodiversidad', 'proyecto/variables.html'),
                                      ('Tareas', 'proyecto/tareas.html')]
     + [(f'T{n} · {TASK_NAMES["T" + str(n)]}', f'proyecto/t{n}.html', 'indent') for n in range(1, 6)]),
    ('monitoreo', 'MonitorEO', 'teal', 'monitoreo.html'),
    ('parques', 'Áreas de estudio', 'green', [('Mapa y resumen', 'parques/index.html'), None]
     + [(f'{p["name"]}' + (' · Portugal' if p['country'] == 'Portugal' else ''), f'parques/{p["slug"]}.html', p['region']) for p in PARKS]),
    ('equipo', 'Equipo', 'orange', [('Miembros', 'equipo/index.html'), ('Instituciones', 'equipo/instituciones.html')]),
    ('noticias', 'Noticias', 'teal', 'noticias/index.html'),
    ('resultados', 'Resultados', 'purple', [('Publicaciones', 'resultados/publicaciones.html'), ('Datos abiertos', 'resultados/datos.html'),
                                            ('Recursos y divulgación', 'resultados/recursos.html')]),
    ('galeria', 'Galería', 'blue', 'galeria.html'),
    ('contacto', 'Contacto', 'blue', 'contacto.html'),
]
CARET = '<svg class="caret" viewBox="0 0 12 12" aria-hidden="true"><path d="M2 4l4 4 4-4" fill="none" stroke="currentColor" stroke-width="2"/></svg>'
# Logo: two snow-capped peaks (teal behind, green in front) with a satellite above them.
LOGO = ('<path d="M1 39 L12 20 L23 39 Z" fill="#0f9488"/>'
        '<path d="M12 20 L15.2 25.5 L13.8 24.6 L12.4 26 L10.6 24.4 L8.8 25.5 Z" fill="#ffffff"/>'
        '<path d="M9 39 L24 15 L39 39 Z" fill="#78a02c"/>'
        '<path d="M24 15 L28.4 22 L26.6 21 L24.8 22.6 L22.6 20.8 L19.6 22 Z" fill="#ffffff"/>'
        '<g transform="translate(31 7) rotate(-35)">'
        '<rect x="-3.6" y="-0.45" width="7.2" height="0.9" fill="#9fd0f0"/>'
        '<rect x="-10" y="-2.4" width="6.4" height="4.8" rx=".6" fill="#6db5e2"/>'
        '<rect x="3.6" y="-2.4" width="6.4" height="4.8" rx=".6" fill="#6db5e2"/>'
        '<path d="M-6.8 -2.4 V2.4 M6.8 -2.4 V2.4 M-10 0 H-3.6 M3.6 0 H10" stroke="#0a2440" stroke-width=".5"/>'
        '<rect x="-2.4" y="-2.8" width="4.8" height="5.6" rx="1" fill="#f2b33d"/>'
        '<path d="M0 2.8 V4.4" stroke="#f2b33d" stroke-width="1"/></g>')
BRAND = f'<svg viewBox="0 0 40 40" aria-hidden="true">{LOGO}</svg>'


def nav_html(path, section):
    items = []
    for key, label, color, target in NAV:
        if isinstance(target, str):
            cur = ' aria-current="page"' if target == path else (' aria-current="true"' if key == section else '')
            hl = ' class="hl"' if key == 'monitoreo' else ''
            items.append(f'<li{hl}><a href="@/{target}"{cur}>{label}</a></li>')
            continue
        subs = []
        for s in target:
            if s is None:
                subs.append('<li class="sep" role="presentation"></li>')
                continue
            extra = s[2] if len(s) > 2 else ''
            cur = ' aria-current="page"' if s[1] == path else ''
            if extra in REGIONS:
                subs.append(f'<li class="{extra}"><a href="@/{s[1]}"{cur}><i class="dot"></i>{s[0]}</a></li>')
            else:
                cls = f' class="{extra}"' if extra else ''
                subs.append(f'<li{cls}><a href="@/{s[1]}"{cur}>{s[0]}</a></li>')
        cur = ' aria-current="true"' if key == section else ''
        items.append(f'<li class="c-{color}"><button type="button" aria-expanded="false" aria-controls="sub-{key}"{cur}>{label}{CARET}</button>'
                     f'<ul class="sub" id="sub-{key}">{"".join(subs)}</ul></li>')
    return ('<nav class="nav" id="site-nav" aria-label="Principal"><ul class="menu">' + ''.join(items) + '</ul></nav>')


def footer_html():
    cols = []
    for key, label, color, target in NAV:
        if isinstance(target, str):
            continue
        links = ''.join(f'<li><a href="@/{s[1]}">{s[0]}</a></li>' for s in target if s and (len(s) == 2 or s[2] in REGIONS))
        cols.append(f'<div><h2>{label}</h2><ul>{links}</ul></div>')
    cols.append('<div><h2>Más</h2><ul><li><a href="@/monitoreo.html">MonitorEO</a></li><li><a href="@/noticias/index.html">Noticias</a></li>'
                '<li><a href="@/galeria.html">Galería</a></li><li><a href="@/contacto.html">Contacto</a></li>'
                f'<li>{ext(MONITOREO_GH, "MonitorEO en GitHub")}</li></ul></div>')
    return (f'<footer class="site-footer"><div class="wrap"><nav class="foot-nav" aria-label="Mapa del sitio">{"".join(cols)}</nav>'
            f'<div class="foot-fund"><div class="logos"><img src="@/img/financiacion.png" width="1905" height="370" alt="{FUND_ALT}" loading="lazy"></div>'
            f'<p>{FUND}</p><p>EVEREST · Universidad de Granada · 1 de septiembre de 2024 – 31 de diciembre de 2028 · '
            f'Fotos de Wikimedia Commons con su autoría y licencia · Última actualización: {UPDATED}</p></div></div></footer>')


# ---------------------------------------------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------------------------------------------
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Outfit:wght@500;600;700;800&family=Source+Sans+3:ital,wght@0,400;0,600;0,700;1,400&family=IBM+Plex+Mono:wght@400;500;600;700&display=swap">')


def slugify(text):
    import unicodedata
    t = unicodedata.normalize('NFKD', re.sub(r'<[^>]+>', '', text)).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z0-9]+', '-', t.lower()).strip('-')


def add_ids(body):
    """Give every h2 without id an id derived from its text."""
    return re.sub(r'<h2>(.*?)</h2>', lambda m: f'<h2 id="{slugify(m.group(1))}">{m.group(1)}</h2>', body)


def toc_html(body):
    heads = re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', body)
    if len(heads) < 3:
        return ''
    lis = ''.join(f'<li><a href="#{i}">{re.sub(r"<[^>]+>", "", t)}</a></li>' for i, t in heads)
    return f'<aside class="toc" aria-label="En esta página"><p>En esta página</p><ol>{lis}</ol></aside>'


def render(path, *, title, section, desc, body, hero, color='blue', toc=True, home=False):
    depth = path.count('/')
    R = '../' * depth
    if not home:
        body = add_ids(body)
        toc_part = toc_html(body) if toc else ''
        body = (f'<div class="wrap layout{" has-toc" if toc_part else ""}"><main id="contenido">'
                f'{body}</main>{toc_part}</div>')
    body_cls = color if color in REGIONS else f'c-{color}'
    doc = f'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="icon" href="@/img/favicon.svg" type="image/svg+xml">
{FONTS}
<link rel="stylesheet" href="@/assets/style.css">
</head>
<body class="{body_cls}">
<a class="skip" href="#contenido">Saltar al contenido</a>
<header class="site-header">
  <div class="wrap bar">
    <a class="brand" href="@/index.html" aria-label="EVEREST, inicio">{BRAND}EVEREST</a>
    <button class="menu-btn" id="menu-btn" type="button" aria-expanded="false" aria-controls="site-nav" aria-label="Abrir el menú">
      <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 6h18M3 12h18M3 18h18" stroke="currentColor" stroke-width="2" stroke-linecap="round" fill="none"/></svg>
    </button>
    {nav_html(path, section)}
  </div>
</header>
<div class="funding">
  <div class="wrap">
    <img src="@/img/financiacion.png" width="1905" height="370" alt="{FUND_ALT}">
    <p>{FUND}</p>
  </div>
</div>
{hero}
{body}
{footer_html()}
<script src="@/assets/main.js" defer></script>
</body>
</html>
'''
    doc = doc.replace('@/', R)
    out = ROOT / path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc, encoding='utf-8', newline='\n')
    return path


def page_hero(crumbs, h1, lede='', img=None):
    pills = ''.join(f'<a href="{h}">{t}</a>' if h else f'<span>{t}</span>' for t, h in crumbs)
    style, cred = '', ''
    if img:
        ph = PHOTOS[img]
        style = f' style="background-image:url(\'{ph["src"]}\')"'
        cred = f'<p class="credit">{ph["cap"]} · {credit(ph)}</p>'
    return (f'<section class="page-hero"{style}><div class="wrap"><p class="eyebrow">{pills}</p><h1>{h1}</h1>'
            + (f'<p class="lede">{lede}</p>' if lede else '') + f'</div>{cred}</section>')


def news_item(n):
    iso, date, tag, title, text = n
    return (f'<li class="news-item c-{NEWS_COLORS[tag]}" data-group="{tag}"><div><time datetime="{iso}">{date}</time><br>'
            f'<span class="pill">{NEWS_TAGS[tag]}</span></div><div><h3>{title}</h3><p>{text}</p></div></li>')


def park_card(p, heading='h3'):
    return (f'<article class="card park-card {p["region"]}"><a class="ph" href="@/parques/{p["slug"]}.html" tabindex="-1" aria-hidden="true">'
            f'{img_tag(p["photo"])}<span class="pill">{REGIONS[p["region"]]}</span></a><div class="body">'
            f'<span class="tag">{p["country"]} · desde {p["declared"]}</span>'
            f'<{heading}><a href="@/parques/{p["slug"]}.html">{p["name"]}</a></{heading}>'
            f'<p>{p["about"][0].split(". ")[0]}.</p>'
            f'<a class="more" href="@/parques/{p["slug"]}.html">Ver el parque</a></div></article>')


# ---------------------------------------------------------------------------------------------------------------
# Normativas europeas y MonitorEO (portada y página de la herramienta)
# ---------------------------------------------------------------------------------------------------------------
REGULATIONS = [
    ('green', 'leaf', 'Directiva Hábitats (92/43/CEE) · art. 17', 'Hábitats y especies',
     'Cada seis años, España y Portugal informan a la Comisión Europea del estado de conservación de los hábitats y '
     'especies de interés comunitario. En los hábitats se evalúan cuatro parámetros: área de distribución, superficie '
     'ocupada, estructura y funciones, y perspectivas futuras.',
     'Mapas de alta resolución de la superficie ocupada y variables de estructura y funciones comparadas con sus '
     'condiciones de referencia.', 'MonitorEO4Habitats · MonitorEO4Species', 't4.html#habitats'),
    ('teal', 'drop', 'Directiva Marco del Agua (2000/60/CE)', 'Calidad del agua',
     'Los planes hidrológicos de cuenca, que se revisan cada seis años, evalúan el estado ecológico de las masas de agua. '
     'En los lagos, la clorofila-a es un indicador clave del fitoplancton.',
     'Clorofila-a y sólidos en suspensión estimados desde Sentinel-2 y PlanetScope en lagos de alta montaña pequeños e '
     'inaccesibles, cada pocos días.', 'MonitorEO4Water', 't4.html#lagos'),
    ('orange', 'sprout', 'Reglamento de Restauración de la Naturaleza (UE 2024/1991)', 'Recuperación y restauración',
     'Obliga a preparar planes nacionales de restauración y a seguir y comunicar sus avances, lo que exige indicadores '
     'que muestren si los ecosistemas se recuperan.',
     'Métricas de severidad, resistencia y resiliencia tras incendios, aclareos y restauraciones, comparadas con zonas '
     'no afectadas.', 'MonitorEO4Restoration', 't4.html#recuperacion'),
]


def regs_html(dark=False):
    return '<div class="regs">' + ''.join(
        f'<article class="reg c-{c}"><span class="icon">{icon(i)}</span><p class="law">{law}</p><h3>{t}</h3>'
        f'<p class="ask"><b>Qué hay que informar.</b> {need}</p><p class="give"><b>Qué aporta EVEREST.</b> {give}</p>'
        f'<p class="module">{m}</p><a class="more" href="@/proyecto/{href}">Ver los casos</a></article>'
        for c, i, law, t, need, give, m, href in REGULATIONS) + '</div>'


REPORT_FLOW = ('<ol class="flow" aria-label="Del satélite al informe">'
               + ''.join(f'<li class="c-{c}">{icon(i)}<span>{t}</span></li>' for c, i, t in [
                   ('blue', 'satellite', 'Imagen de satélite'), ('green', 'layers', 'Variable Esencial de la Biodiversidad'),
                   ('teal', 'trend', 'Indicador y referencia'), ('sun', 'doc', 'Informe europeo')]) + '</ol>')

MONITOREO_STATS = ('<ul class="mstats">'
                   '<li><b>3</b><span>satélites: MODIS, Landsat y Sentinel-2</span></li>'
                   '<li><b>10 m</b><span>de resolución máxima</span></li>'
                   '<li><b>1984</b><span>inicio de las series (Landsat)</span></li>'
                   '<li><b>8</b><span>formas de usarla, de la web a Python y R</span></li></ul>')

PROFILES = [('sun', 'people', 'Público general', 'MonitorEO web, sin instalación ni cuenta propia, y visor de resultados en el navegador.'),
            ('green', 'leaf', 'Gestores', 'Complemento de QGIS y un asistente conversacional que prepara mapas, series e informes a partir de preguntas en lenguaje natural.'),
            ('purple', 'code', 'Científicos y técnicos', 'Paquetes de Python y R, línea de comandos y servidor MCP, con el mismo cálculo que el resto de herramientas.')]
MONITOREO_PROFILES = ''.join(f'<article class="card c-{c}"><span class="icon">{icon(i)}</span><h3>{t}</h3><p>{d}</p></article>'
                             for c, i, t, d in PROFILES)


# ---------------------------------------------------------------------------------------------------------------
# Páginas
# ---------------------------------------------------------------------------------------------------------------
def build_home():
    news3 = ''.join(
        f'<article class="card c-{NEWS_COLORS[n[2]]}"><span class="pill">{NEWS_TAGS[n[2]]}</span><time datetime="{n[0]}">{n[1]}</time>'
        f'<h3>{n[3]}</h3><p>{n[4]}</p></article>' for n in NEWS[:3])
    hero_ph = PHOTOS['amanecer']
    hero = (f'<section class="hero" style="background-image:url(\'{hero_ph["src"]}\')"><div class="wrap">'
            '<p class="eyebrow"><span>Proyecto de investigación</span><span style="background:var(--green)">2024–2028</span></p>'
            '<h1>EVEREST</h1>'
            f'<p class="tagline">{TITLE_ES}</p>'
            '<p class="lede">Los gestores de los espacios protegidos deben informar a Europa del estado de la naturaleza '
            'según la Directiva Hábitats, la Directiva Marco del Agua y el Reglamento de Restauración de la Naturaleza. '
            'EVEREST, junto con ellos, define qué variables de satélite sirven para esos informes y las pone a su alcance '
            'en MonitorEO, en ocho parques nacionales de montaña.</p>'
            '<div class="cta"><a class="btn btn-sun" href="@/monitoreo.html">Descubre MonitorEO</a>'
            '<a class="btn btn-ghost" href="@/proyecto/index.html">Conoce el proyecto</a></div>'
            '<ul class="stats"><li class="c-sun"><b>3</b><span>normativas europeas de reporte</span></li>'
            '<li class="c-green"><b>8</b><span>parques nacionales de montaña</span></li>'
            '<li class="c-blue"><b>4</b><span>regiones biogeográficas</span></li></ul>'
            f'</div><p class="credit">{hero_ph["cap"]} · {credit(hero_ph)}</p></section>')
    tiles = [('borreguil', 'green', 'Hábitats', 'Borreguiles', 'Mapa y estado de conservación de los pastizales húmedos', 't4.html#habitats'),
             ('sierra-nevada', 'teal', 'Agua', 'Lagunas', 'Clorofila de 56 lagunas desde Sentinel-2', 't4.html#lagos'),
             ('nieve-satelite', 'blue', 'Clima', 'Nieve', 'Cuarenta años de innivación con Landsat', 't3.html'),
             ('acequia', 'orange', 'Restauración', 'Acequias y bosques', 'Recuperación tras aclareos, incendios y restauraciones', 't4.html#recuperacion')]
    tiles_html = ''.join(
        f'<a class="tile c-{c}" href="@/proyecto/{href}">{img_tag(PHOTOS[pid])}<div><span class="k">{k}</span>'
        f'<b>{t}</b><span>{d}</span></div></a>' for pid, c, k, t, d, href in tiles)
    tiles_credit = ' · '.join(f'{PHOTOS[t[0]]["cap"]}: {ext(PHOTOS[t[0]]["page"], PHOTOS[t[0]]["author"])} ({PHOTOS[t[0]]["lic"]})' for t in tiles)
    body = f'''<main id="contenido">
<section class="band dark"><div class="wrap">
  <p class="kicker">Por qué EVEREST</p>
  <h2>Tres normativas europeas, tres informes obligatorios</h2>
  <p class="prose">Los gestores de los espacios protegidos tienen que informar periódicamente a la Comisión Europea del
  estado de la naturaleza. Hoy lo hacen con metodologías distintas y con datos de campo escasos y desiguales entre parques.
  EVEREST identifica, con ellos, qué variables de satélite sirven para cada informe y las pone a su alcance en
  <a href="@/monitoreo.html" style="color:var(--sun)">MonitorEO</a>.</p>
  {regs_html(dark=True)}
  {REPORT_FLOW}
</div></section>

<section class="band teal"><div class="wrap">
  <div class="split">
    <div>
      <p class="kicker">La herramienta del proyecto</p>
      <h2>MonitorEO: del satélite al informe, sin programar</h2>
      <p>MonitorEO calcula en la nube series temporales, mapas, tendencias y anomalías de Variables Esenciales de la Biodiversidad de
      la biodiversidad para cualquier zona, desde MonitorEO web, que no necesita instalación ni cuenta propia. La
      co-diseñamos con los gestores para que la usen en sus planes de seguimiento y en sus informes.</p>
      {MONITOREO_STATS}
      <ul class="links" style="margin-top:22px">
        <li>{ext(MONITOREO_APP, 'MonitorEO web')}</li>
        <li><a href="@/monitoreo.html">Conoce la herramienta</a></li>
        <li>{ext(MONITOREO_GH, 'Código en GitHub')}</li>
      </ul>
    </div>
    {figure('nieve-satelite')}
  </div>
  <div class="cards fit">{MONITOREO_PROFILES}</div>
</div></section>

<section class="band"><div class="wrap">
  <p class="kicker">Lo que seguimos desde el espacio</p>
  <h2>Cuatro señales del cambio en la montaña</h2>
  <div class="tiles">{tiles_html}</div>
  <p class="credit">Fotos e imágenes de Wikimedia Commons: {tiles_credit}.</p>
</div></section>

<section class="band tint c-green"><div class="wrap split">
  <div>
    <p class="kicker">¿Por qué las montañas?</p>
    <h2>Laboratorios naturales del cambio global</h2>
    <p>Con solo el 25 % de la superficie emergida, las montañas albergan más del 85 % de las especies de mamíferos,
    anfibios y aves del mundo, muchas de ellas endémicas. Las de España y Portugal sufren un doble riesgo: son montañas y
    están junto a la cuenca mediterránea, donde se espera más variabilidad climática, veranos más secos y menos nieve.</p>
    <p>Saber cómo cambian la composición, la estructura y el funcionamiento de sus ecosistemas es imprescindible para
    decidir si un hábitat está bien conservado, si necesita restauración y si las medidas funcionan. Y es una obligación
    legal para los gestores de los espacios protegidos.</p>
    <div class="callout"><p><b>Hipótesis de partida.</b> El aumento de la temperatura y, sobre todo, la menor
    disponibilidad de agua afectarán de forma distinta a los ecosistemas de montaña: las montañas con veranos más
    templados y lluviosos se verán menos afectadas que las de clima más mediterráneo y semiárido.</p></div>
    <p><a class="more" href="@/proyecto/index.html">Resumen y objetivos</a></p>
  </div>
  {figure('ordesa-y-monte-perdido', 'tall')}
</div></section>

<section class="band"><div class="wrap">
  <div class="split rev">
    <div>
      <p class="kicker">Nuestro enfoque</p>
      <h2>Del satélite a la decisión</h2>
      <p>Las series de satélite cubren décadas y todo el territorio, también las zonas de difícil acceso. Las
      convertimos en Variables Esenciales de la Biodiversidad y en métricas que los gestores pueden usar en sus planes de
      seguimiento.</p>
      <p><a class="more" href="@/proyecto/variables.html">Qué son las Variables Esenciales de la Biodiversidad</a></p>
    </div>
    {figure('satelite')}
  </div>
  {PIPELINE}
</div></section>

<section class="band tint c-blue"><div class="wrap">
  <p class="kicker">Áreas de estudio</p>
  <h2>Ocho parques, cuatro regiones biogeográficas</h2>
  <div class="split">
    <div class="prose">
      <p>Siete parques nacionales de montaña de España y uno de Portugal, en las regiones mediterránea, alpina,
      atlántica y macaronésica. Son laboratorios naturales excepcionales y cuentan con programas de seguimiento cuyos
      datos permiten validar el seguimiento desde el satélite.</p>
      <p><a class="more" href="@/parques/index.html">Mapa y resumen</a></p>
    </div>
    <figure class="map-figure" style="margin:0">{map_svg('home-map', link=True)}{legend()}</figure>
  </div>
  <div class="cards">{''.join(park_card(p) for p in PARKS)}</div>
  <p class="credit">Fotos: Wikimedia Commons; autoría y licencia en cada parque y en la <a href="@/galeria.html">galería</a>.</p>
</div></section>

<section class="band"><div class="wrap">
  <p class="kicker">Objetivos</p>
  <h2>Objetivos del proyecto</h2>
  <div class="callout prose"><p><b>Objetivo general.</b> {GENERAL_OBJECTIVE}</p></div>
  <p class="prose">Cinco objetivos específicos, cada uno con su tarea, y estudios piloto en los ocho parques:</p>
  {tasks_cards()}
</div></section>

<section class="band"><div class="wrap">
  <p class="kicker">Actualidad</p>
  <h2>Últimas noticias</h2>
  <div class="cards news-cards">{news3}</div>
  <p style="margin-top:18px"><a class="more" href="@/noticias/index.html">Todas las noticias</a></p>
</div></section>
</main>'''
    render('index.html', title='Proyecto EVEREST', section='inicio', home=True, color='blue',
           desc=f'EVEREST: {TITLE_ES}. Proyecto PID2023-151939OB-I00, Universidad de Granada.',
           body=body, hero=hero)


def build_project():
    questions = [
        '¿Cuáles son las Variables Esenciales de la Biodiversidad y métricas más sólidas científicamente y útiles para la gestión en relación con las obligaciones de reporte europeas en las áreas protegidas de montaña?',
        '¿Cómo pueden derivarse las Variables Esenciales de la Biodiversidad a partir de datos brutos, combinando muestreos de campo, instrumentos automáticos, modelos ecológicos y teledetección?',
        '¿Cómo caracterizar con teledetección las dinámicas de referencia, las tendencias, las anomalías y la variabilidad espacial de la composición, la estructura y la función de los ecosistemas?',
        '¿Cómo seguir la estabilidad de los ecosistemas para detectar trayectorias de recuperación o restauración y posibles cambios de régimen?',
        '¿Pueden identificarse los principales factores de los cambios de distribución y de régimen con modelos que integren las distintas dimensiones del ecosistema?',
        '¿Cómo pueden contribuir la inteligencia artificial y las nuevas técnicas de modelización?',
        '¿Responden y se recuperan antes los atributos funcionales que los de composición y estructura ante perturbaciones y restauraciones?',
        '¿Qué consecuencias tienen los cambios en la estructura y la composición sobre el funcionamiento, y viceversa?',
        '¿Se verá menos afectada por el cambio climático la biodiversidad de las montañas con veranos más templados y lluviosos que la de las montañas mediterráneas y semiáridas?',
        '¿Qué elementos ganan y cuáles pierden según las tendencias observadas en las variables del ecosistema?',
        '¿Detectan con precisión las herramientas de teledetección los efectos de las perturbaciones y de la restauración que los gestores observan sobre el terreno?',
        '¿Qué medidas de gestión activa pueden aplicarse de forma coordinada con los actores implicados para conservar la biodiversidad de estas montañas ante el cambio global?',
    ]
    objs = ''.join(f'<li class="c-{TASK_COLORS["T" + str(i)]}">{o} <a href="@/proyecto/t{i}.html">Tarea {i}</a></li>'
                   for i, o in enumerate(OBJECTIVES, 1))
    body = f'''<p class="intro"><strong>EVEREST</strong> es el acrónimo de «{TITLE_ES}» (en inglés, <em>{TITLE_EN}</em>).
Es un proyecto de investigación orientada de la convocatoria
de Proyectos de Generación de Conocimiento 2023 del Plan Estatal de Investigación Científica, Técnica y de Innovación,
liderado por la Universidad de Granada.</p>
{factbox([('Referencia', '<span class="mono">PID2023-151939OB-I00</span>'), ('Entidad', 'Universidad de Granada'),
          ('Investigadores principales', f'{JML} y {DAS}'), ('Duración', '1 sep. 2024 – 31 dic. 2028'),
          ('Financiación', '297.500 € · MICIU/AEI y FEDER, UE'), ('Parques', '8 parques nacionales de montaña')])}
<section class="prose"><h2>Antecedentes</h2>
<p>Con solo el 25 % de la superficie emergida, las montañas albergan más del 85 % de las especies de mamíferos, anfibios
y aves del mundo, muchas de ellas endémicas. Las áreas protegidas de montaña son una estrategia clave para frenar la
pérdida de biodiversidad, pero soportan presiones crecientes, directas e indirectas. Su conservación depende de una
gestión basada en datos y modelos que permitan seguir y anticipar cómo responden los ecosistemas a múltiples factores de
estrés.</p>
<p>Las montañas de España y Portugal sufren un doble riesgo: son montañas y están junto a la cuenca mediterránea, donde se
espera que aumenten la variabilidad climática y la sequía estival y que disminuya la duración de la nieve. La transición
entre el frío del invierno y la sequía del verano será más rápida y dura, y acortará el periodo de actividad biológica de
plantas, animales y microorganismos del suelo.</p>
{figure('amanecer')}
<p>Saber cómo cambian la composición, la estructura y el funcionamiento de los ecosistemas es imprescindible para decidir
si una especie o un hábitat tiene un estado de conservación adecuado, si necesita restauración y si las medidas aplicadas
funcionan. Además, es una obligación legal derivada de la Directiva Hábitats (artículo 17), la Directiva Marco del Agua y
el Reglamento de Restauración de la Naturaleza.</p>
</section>
<section class="prose c-green"><h2>Por qué Variables Esenciales de la Biodiversidad desde satélite</h2>
{leads(['<strong>Seguimiento continuo y a gran escala.</strong> Las series de MODIS, Landsat y Sentinel cubren décadas y todo el territorio, también las zonas de difícil acceso.',
        '<strong>Respuesta temprana.</strong> Los atributos funcionales (productividad, estacionalidad, fenología) responden antes a las perturbaciones que la composición y la estructura, que tienen más inercia.',
        '<strong>Menor coste.</strong> Seguir la composición de especies sobre el terreno a escala regional es muy caro; el satélite permite priorizar dónde muestrear.',
        '<strong>Comparables entre montañas.</strong> Las mismas métricas permiten comparar parques a lo largo de un gradiente biogeográfico.',
        '<strong>Útiles para el reporte.</strong> Informan sobre el estado de conservación, la calidad del agua y la recuperación tras perturbaciones y restauraciones.'])}
</section>
<section class="prose c-orange"><h2>Retos</h2>
{leads(['<strong>Distancia entre ciencia y gestión.</strong> Muchas herramientas de teledetección no responden a las necesidades reales de los gestores ni se integran en sus planes de seguimiento.',
        '<strong>Metodologías heterogéneas.</strong> Las metodologías oficiales de evaluación del estado de conservación difieren en variables, umbrales, escalas y fechas.',
        '<strong>Datos de campo escasos.</strong> La verdad terreno para calibrar y validar los productos de satélite está repartida de forma desigual entre parques.',
        '<strong>Condiciones de referencia.</strong> A menudo faltan referencias con las que comparar el estado pasado, presente o futuro de los ecosistemas.'])}
<div class="callout"><p><b>Hipótesis de partida.</b> El aumento de la temperatura y, sobre todo, la reducción de la
disponibilidad de agua deberían afectar de forma distinta a los ecosistemas de montaña: las montañas con veranos más
templados y lluviosos se verán menos afectadas que las de clima más mediterráneo y semiárido. Esta susceptibilidad se
trasladará a la composición, la estructura y el funcionamiento de la biodiversidad.</p></div>
</section>
<section class="prose"><h2>Objetivos</h2>
<p><strong>Objetivo general.</strong> Sentar a gestores y científicos para co-diseñar, co-producir y validar un marco
metodológico común, basado en la experiencia de MonitorEO, que proporcione variables científicamente sólidas y útiles para
la gestión, junto con capacidades de seguimiento y modelización, para informar sobre el estado de conservación de especies
y hábitats (Directiva Hábitats), la calidad del agua (Directiva Marco del Agua) y la recuperación de los ecosistemas tras
perturbaciones y restauraciones (Reglamento de Restauración de la Naturaleza).</p>
<p><strong>Objetivos específicos</strong>, con estudios piloto en los ocho parques:</p>
<ol class="num">{objs}</ol>
</section>
<section class="prose c-purple"><h2>Preguntas de investigación</h2>
<ol class="num">{''.join(f'<li>{q}</li>' for q in questions)}</ol>
</section>
<section class="prose c-teal"><h2>Resultados esperados</h2>
{leads(['Un conjunto de Variables Esenciales de la Biodiversidad y métricas de satélite, sólidas y útiles para la gestión, para cada obligación de reporte.',
        'Dinámicas de referencia, tendencias y anomalías de esas variables comparadas a lo largo de un gradiente biogeográfico.',
        'Mapas de hábitats de alta resolución sobre grandes superficies y su estado de conservación.',
        'Nuevos módulos de MonitorEO para hábitats, especies, agua y restauración, disponibles a través de LifeWatch ERIC.',
        'Guías, datos y procedimientos que los gestores puedan usar en sus planes de seguimiento cuando acabe el proyecto.',
        'Un estudio piloto ampliable al resto de la red Natura 2000.'])}
</section>'''
    render('proyecto/index.html', title='Resumen y objetivos · EVEREST', section='proyecto', color='blue',
           desc='Antecedentes, objetivos, preguntas de investigación y resultados esperados del proyecto EVEREST.',
           body=body, hero=page_hero([('Proyecto', None)], 'Resumen y objetivos',
                                     'EVEREST une a gestores y científicos para convertir los datos de satélite en '
                                     'información útil para conservar los ecosistemas de montaña.', img='ordesa-y-monte-perdido'))


def build_variables():
    sensors = [
        ('MODIS', '250 m – 1 km', 'Desde 2000', 'Funcionamiento a escala de paisaje y Tipos Funcionales de Ecosistemas'),
        ('Landsat', '30 m', 'Desde los años ochenta', 'Series largas: nieve, verdor, perturbaciones y restauración'),
        ('Sentinel-2', '10–20 m', 'Desde 2015', 'Hábitats, clorofila de las lagunas y nieve'),
        ('PlanetScope', '≈ 3 m', 'Casi diaria', 'Nieve y lagunas pequeñas'),
        ('LiDAR del PNOA', 'Alta resolución', 'Periodos recientes', 'Altura y estructura de la vegetación'),
    ]
    rows = ''.join(f'<tr><td><strong>{a}</strong></td><td>{b}</td><td>{c}</td><td>{d}</td></tr>' for a, b, c, d in sensors)
    body = f'''<section class="prose"><h2>Qué son las Variables Esenciales de la Biodiversidad</h2>
<p>Las Variables Esenciales de la Biodiversidad son el conjunto mínimo de medidas necesario para estudiar, seguir e
informar sobre los cambios de la biodiversidad, tal como las propone la red internacional GEO BON. Las que se obtienen por
teledetección permiten seguirlas de forma continua, repetible y comparable en grandes territorios, también donde es difícil
llegar a pie.</p>
<p>EVEREST busca cuáles de ellas, y con qué métricas, sirven a los gestores de los parques nacionales de montaña para
cumplir sus obligaciones de reporte.</p>
{figure('satelite')}
</section>
<section><h2>Composición, estructura y función</h2>
<div class="dims">
  <div class="dim c-green"><h3>{icon('layers')}Composición</h3><ul><li>Cubiertas del suelo</li><li>Masas de agua</li><li>Tipos de hábitat</li></ul></div>
  <div class="dim c-orange"><h3>{icon('mountain')}Estructura</h3><ul><li>Biomasa</li><li>Fragmentación</li><li>Altura de la vegetación</li>
    <li>Heterogeneidad (cobertura leñosa y herbácea)</li><li>Índice de área foliar</li></ul></div>
  <div class="dim c-blue"><h3>{icon('trend')}Función</h3>
    <span class="flux c-teal">Agua</span><ul><li>Humedad del suelo y de la vegetación, evapotranspiración, nieve, hidroperiodo</li></ul>
    <span class="flux c-orange">Energía</span><ul><li>Temperatura del aire y de la superficie, albedo, radiación, nubosidad</li></ul>
    <span class="flux c-green">Carbono</span><ul><li>Verdor (producción primaria), fenología y estacionalidad</li></ul></div>
</div>
</section>
<section class="prose"><h2>De la serie temporal a la métrica</h2>
<p>Cada variable es una serie temporal. Para que sea útil la resumimos cada año en <strong>atributos funcionales</strong>
con significado biológico. Por ejemplo, con el índice de vegetación NDVI:</p>
{leads(['<strong>Media anual</strong>: estima la producción primaria total.',
        '<strong>Variabilidad estacional</strong> (desviación típica o coeficiente de variación): describe la estacionalidad.',
        '<strong>Fechas del máximo y del mínimo</strong>: describen la fenología.'])}
<p>Combinando estos atributos se definen los <strong>Tipos Funcionales de Ecosistemas</strong> (EFT): zonas con una
dinámica similar de intercambio de materia y energía. EVEREST ha comprobado con 50 torres de flujo de FLUXNET que los EFT
discriminan la dinámica del intercambio neto de CO₂ (kappa = 0,95).</p>
</section>
<section class="prose c-purple"><h2>Cómo seleccionamos las variables</h2>
<p>Partimos de unos 90 indicadores de las metodologías oficiales de evaluación del estado de conservación, de los que
alrededor del 40 % son medibles por teledetección. Para quedarnos con las métricas más informativas e independientes
aplicamos análisis de componentes principales y de correlación, el factor de inflación de la varianza y técnicas de
agrupación y ordenación (k-means, NMDS y t-SNE). Las variables seleccionadas se prueban con los gestores en los casos de
estudio de la <a href="@/proyecto/t4.html">Tarea 4</a>.</p>
</section>
<section class="c-blue"><h2>Datos y sensores</h2>
<div class="table-wrap"><table><thead><tr><th>Sensor</th><th>Resolución</th><th>Periodo</th><th>Uso en EVEREST</th></tr></thead>
<tbody>{rows}</tbody></table></div>
<p class="prose">Los datos se procesan en Google Earth Engine gracias al acuerdo institucional entre Google, LifeWatch ERIC y
la Universidad de Granada, y se complementan con series climáticas y con los datos de campo de los programas de seguimiento
de cada parque.</p>
</section>
<section class="prose c-teal"><h2>Referencias, tendencias y anomalías</h2>
<p>Para saber si un ecosistema cambia hace falta una referencia. Calculamos la curva estacional media de cada variable y su
variabilidad histórica, las tendencias a largo plazo (pruebas de Mann-Kendall y pendiente de Sen) y las anomalías respecto
a esa variabilidad, que pueden avisar de cambios antes de que sean evidentes. Tras una perturbación, las mismas series
permiten medir la severidad y el tiempo de recuperación (<a href="@/proyecto/t4.html#recuperacion">Tarea 4.3</a>).</p>
{figure('nieve-satelite')}
</section>'''
    render('proyecto/variables.html', title='Variables Esenciales de la Biodiversidad · EVEREST', section='proyecto', color='green',
           desc='Qué variables de satélite mide EVEREST y cómo las convierte en información para la gestión.',
           body=body, hero=page_hero([('Proyecto', None)], 'Variables Esenciales de la Biodiversidad',
                                     'Qué medimos desde el satélite y cómo lo convertimos en información para la gestión.',
                                     img='satelite'))


def build_tasks():
    rows = [('T1', 'Implicación de actores', RZ, '—'), ('T2', 'Variables Esenciales de la Biodiversidad', JML, '—'),
            ('T3', 'Dinámicas de referencia, tendencias y anomalías', DAS, '—'),
            ('T4.1.1', 'Hábitats', JML, 'MonitorEO4Habitats'), ('T4.1.2', 'Especies', DAS, 'MonitorEO4Species'),
            ('T4.2', 'Calidad del agua de los lagos', JML, 'MonitorEO4Water'),
            ('T4.3', 'Recuperación y restauración', DAS, 'MonitorEO4Restoration'),
            ('T5.1', 'Herramienta de apoyo a la decisión', AM, 'MonitorEO'), ('T5.2', 'Difusión y reporte', AM, '—')]
    tr = ''.join(f'<tr><td class="c-{TASK_COLORS[c[:2]]}"><span class="pill">{c}</span></td>'
                 f'<td><a href="@/proyecto/t{c[1]}.html">{t}</a></td><td>{r}</td><td>{m}</td></tr>'
                 for c, t, r, m in rows)
    milestones = [('1 de septiembre de 2024', 'Inicio del proyecto.'),
                  ('5 de diciembre de 2024', 'Primera reunión de co-diseño con el Espacio Natural Sierra Nevada.'),
                  ('2025', 'Cuestionario a los gestores de los ocho parques y mapa de actores.'),
                  ('Febrero de 2026', 'Incorporación de personal investigador contratado por el proyecto.'),
                  ('Noviembre de 2026', 'Informe intermedio a la Agencia Estatal de Investigación.'),
                  ('Enero–febrero de 2027', 'Taller nacional ciencia-gestión.'),
                  ('31 de diciembre de 2028', 'Fin del proyecto.')]
    body = f'''<section class="prose"><h2>Cómo se relacionan</h2>
<p>La <strong>Tarea 1</strong> enmarca todo el proyecto: con los gestores se eligen los casos de estudio y se validan los
resultados. La <strong>Tarea 2</strong> selecciona las Variables Esenciales de la Biodiversidad; la <strong>Tarea 3</strong> describe sus
dinámicas de referencia, tendencias y anomalías; y la <strong>Tarea 4</strong> las aplica a tres obligaciones de reporte.
La <strong>Tarea 5</strong> traslada los resultados a MonitorEO y a la sociedad.</p>
</section>
{PIPELINE}
<section style="margin-top:56px"><h2>Las cinco tareas</h2>{tasks_cards()}</section>
<section><h2>Responsables</h2>
<div class="table-wrap"><table><thead><tr><th>Tarea</th><th>Título</th><th>Responsable</th><th>Módulo</th></tr></thead>
<tbody>{tr}</tbody></table></div></section>
<section class="prose c-orange"><h2>Hitos</h2>
<div class="table-wrap"><table><tbody>{''.join(f'<tr><td style="white-space:nowrap"><strong>{d}</strong></td><td>{t}</td></tr>' for d, t in milestones)}</tbody></table></div>
</section>'''
    render('proyecto/tareas.html', title='Tareas · EVEREST', section='proyecto', color='blue',
           desc='Las cinco tareas del proyecto EVEREST, sus responsables y sus hitos.',
           body=body, hero=page_hero([('Proyecto', None)], 'Tareas',
                                     'El trabajo se organiza en cinco tareas, una por objetivo específico.', img='aiguestortes'))
    for n, t in TASK_DETAIL.items():
        render(f'proyecto/t{n}.html', title=f'{t["title"]} · EVEREST', section='proyecto', color=t['color'],
               desc=re.sub(r'<[^>]+>', '', t['lede'])[:155], body=t['body'],
               hero=page_hero(t['crumbs'], t['h1'], t['lede'], img=t['img']))


def build_parks():
    rows = ''.join(f'<tr class="{p["region"]}"><td><a href="@/parques/{p["slug"]}.html">{p["full"]}</a></td><td>{p["country"]}</td>'
                   f'<td><i class="dot"></i>{REGIONS[p["region"]]}</td><td>{p["declared"]}</td>'
                   f'<td>{p["peak"]}</td></tr>' for p in PARKS)
    body = f'''<section class="prose"><p class="intro">Para obtener resultados generalizables, EVEREST trabaja en ocho
parques nacionales de montaña, siete en España y uno en Portugal, que cubren cuatro regiones biogeográficas y siete
ecorregiones.</p>
<p>Esta diversidad exige adaptar la metodología a la realidad de cada parque con datos de campo y conocimiento experto, y a
la vez demuestra que el enfoque sirve para cualquier montaña. Los parques tienen una larga historia de protección y
programas de seguimiento cuyos datos permiten validar el seguimiento desde el satélite. Los tipos de hábitat comunes y
exclusivos de cada parque sirven como réplicas.</p></section>
<section><h2>Mapa</h2><figure class="map-figure">{map_svg('parks-map', link=True)}{legend()}</figure>
<p class="credit">Pulsa en un parque para ver su ficha.</p></section>
<section><h2>Los parques</h2><div class="cards">{''.join(park_card(p) for p in PARKS)}</div>
<p class="credit">Fotos: Wikimedia Commons; autoría y licencia en la ficha de cada parque.</p></section>
<section><h2>Espacios protegidos</h2>
<div class="table-wrap"><table><thead><tr><th>Parque nacional</th><th>País</th><th>Región biogeográfica</th>
<th>Declarado</th><th>Altitud máxima</th></tr></thead><tbody>{rows}</tbody></table></div></section>'''
    render('parques/index.html', title='Áreas de estudio · EVEREST', section='parques', color='green',
           desc='Los ocho parques nacionales de montaña del proyecto EVEREST en España y Portugal.',
           body=body, hero=page_hero([('Áreas de estudio', None)], 'Mapa y resumen',
                                     'Ocho parques nacionales de montaña a lo largo de un gradiente biogeográfico, del '
                                     'Atlántico a Canarias.', img='peneda-geres'))
    for p in PARKS:
        ph = p['photo']
        hero = (f'<section class="photo-hero {p["region"]}">{img_tag(ph, lazy=False)}'
                f'<div class="wrap"><p class="eyebrow"><a href="@/parques/index.html">Áreas de estudio</a>'
                f'<span>{REGIONS[p["region"]]}</span><span style="background:rgba(6,18,31,.6)">{p["country"]}</span></p>'
                f'<h1>{p["name"]}</h1></div><span class="bar-c"></span></section>')
        tasks = ''.join(f'<li class="c-{TASK_COLORS[t]}"><a href="@/proyecto/{TASK_PAGES[t]}.html">{t} · {TASK_NAMES[t]}</a></li>'
                        for t in p['tasks'])
        partners = (f'<section class="prose"><h2>Colaboran</h2>{leads(p["partners"])}</section>' if p['partners'] else '')
        extra = ''.join(figure(x) for x in p.get('extra', []))
        others = ''.join(f'<a class="{o["region"]}" href="@/parques/{o["slug"]}.html">{img_tag(o["photo"])}<span>{o["name"]}</span></a>'
                         for o in PARKS if o is not p)
        body = f'''<p class="credit" style="margin:-24px 0 26px">{ph["cap"]} · {credit(ph)}</p>
{factbox([('País', p['country']), ('Espacio protegido', p['full']), ('Situación', p['where']),
          ('Región biogeográfica', f'<i class="dot"></i> {REGIONS[p["region"]]}'),
          ('Parque nacional desde', p['declared']), ('Altitud máxima', p['peak'])])}
<section class="prose"><h2>Sobre el parque</h2>{''.join(f'<p>{t}</p>' for t in p['about'])}</section>
<section class="prose"><h2>EVEREST en {p['name']}</h2>{leads(p['everest'])}{extra}</section>
<section><h2>Situación</h2><figure class="map-figure small">{map_svg(f'map-{p["slug"]}', focus=p['slug'])}</figure></section>
<section><h2>Tareas</h2><ul class="badges">{tasks}</ul></section>
{partners}
<section><h2>Otros parques</h2><div class="strip">{others}</div></section>'''
        render(f'parques/{p["slug"]}.html', title=f'{p["name"]} · EVEREST', section='parques', color=p['region'],
               desc=f'{p["full"]}: qué estudia EVEREST en este parque nacional de montaña.', body=body, hero=hero)


def build_team():
    counts = {g: sum(1 for t in TEAM if t[1] == g) for g, _ in GROUPS}
    filters = (f'<div class="filters" data-filter-list="people" role="group" aria-label="Filtrar por grupo">'
               f'<button type="button" data-filter="all" aria-pressed="true">Todos<span class="count">{len(TEAM)}</span></button>'
               + ''.join(f'<button type="button" data-filter="{g}" aria-pressed="false">{label}<span class="count">{counts[g]}</span></button>'
                         for g, label in GROUPS) + '</div>')
    people = ''.join(
        f'<article class="person c-{PALETTE[i % len(PALETTE)]}" data-group="{g}"><span class="avatar" aria-hidden="true">{initials(n)}</span>'
        f'<div><p class="role">{role}</p><h3>{n}</h3><p class="aff">{aff}</p><p class="exp">{exp}</p>'
        f'<p class="tasks">{"".join(f"<span>{t.strip()}</span>" for t in tasks.split(","))}</p></div></article>'
        for i, (n, g, role, aff, exp, tasks) in enumerate(TEAM))
    collab = leads([f'<strong>{n}</strong>: {d}' for n, d in COLLABORATORS])
    body = f'''<section><h2>Miembros</h2>{filters}<div class="people" id="people">{people}</div></section>
<section class="prose c-green"><h2>Colaboran</h2>
<p>Además del equipo, contribuyen al proyecto investigadores y técnicos de otras instituciones:</p>{collab}
<p><a class="more" href="@/equipo/instituciones.html">Instituciones y proyectos vinculados</a></p></section>'''
    render('equipo/index.html', title='Equipo · EVEREST', section='equipo', color='orange',
           desc='Investigadores principales, equipo de investigación y equipo de trabajo del proyecto EVEREST.',
           body=body, hero=page_hero([('Equipo', None)], 'Miembros',
                                     'Ecólogos, botánicos, expertos en teledetección y gestores de parques nacionales de '
                                     'España y Portugal.', img='sierra-de-las-nieves'), toc=False)

    insts = ''.join(f'<article class="inst c-{PALETTE[i % len(PALETTE)]}"><p class="acr">{a}</p><h3>{n}</h3><p>{d}</p>'
                    f'<p>{w}</p><p class="role">{r}</p></article>' for i, (a, n, d, w, r) in enumerate(INSTITUTIONS))
    orgs = leads([f'<strong>{n}</strong>: {d}' for n, d in PARTNER_ORGS])
    projs = leads([f'<strong>{ext(u, n) if u else n}</strong>. {d}' for n, u, d in PROJECTS])
    nets = ''.join(f'<li class="c-{PALETTE[i % len(PALETTE)]}">{ext(u, n)}</li>' for i, (n, u) in enumerate(NETWORKS))
    rows = [('T1 · Implicación de actores', 'Universidad de Granada', 'T1'), ('T2 · Variables Esenciales de la Biodiversidad', 'Universidad de Granada', 'T2'),
            ('T3 · Dinámicas de referencia', 'Universidad de Granada', 'T3'), ('T4 · Aplicación a la gestión', 'Universidad de Granada', 'T4'),
            ('T5 · Transferencia', 'LifeWatch ERIC', 'T5')]
    body = f'''<section class="prose"><p class="intro">EVEREST reúne universidades, centros de investigación, una
infraestructura europea y la administración de los parques nacionales, con experiencia en ecología de montaña,
teledetección, modelización, gestión de datos y transferencia a la gestión.</p></section>
<section><h2>Instituciones del equipo</h2><div class="insts">{insts}</div></section>
<section><h2>Responsables de tareas</h2>
<div class="table-wrap"><table><thead><tr><th>Tarea</th><th>Institución responsable</th></tr></thead>
<tbody>{''.join(f'<tr><td class="c-{TASK_COLORS[c]}"><span class="pill">{a}</span></td><td>{b}</td></tr>' for a, b, c in rows)}</tbody></table></div></section>
<section class="prose c-green"><h2>Administraciones y entidades colaboradoras</h2>{orgs}</section>
<section class="prose c-purple"><h2>Proyectos vinculados</h2>{projs}</section>
<section class="c-teal"><h2>Redes e infraestructuras</h2><ul class="badges">{nets}</ul></section>'''
    render('equipo/instituciones.html', title='Instituciones · EVEREST', section='equipo', color='orange',
           desc='Instituciones, entidades colaboradoras, proyectos vinculados y redes del proyecto EVEREST.',
           body=body, hero=page_hero([('Equipo', None)], 'Instituciones', 'Quién participa en EVEREST y con quién colaboramos.',
                                     img='teide'))


def build_news():
    tags = sorted({n[2] for n in NEWS}, key=list(NEWS_TAGS).index)
    filters = (f'<div class="filters" data-filter-list="news" role="group" aria-label="Filtrar por tipo">'
               f'<button type="button" data-filter="all" aria-pressed="true">Todas<span class="count">{len(NEWS)}</span></button>'
               + ''.join(f'<button type="button" class="c-{NEWS_COLORS[t]}" data-filter="{t}" aria-pressed="false">{NEWS_TAGS[t]}'
                         f'<span class="count">{sum(1 for n in NEWS if n[2] == t)}</span></button>' for t in tags) + '</div>')
    body = f'''<div class="callout" style="margin-top:0"><p><b>Próximamente.</b> Taller nacional ciencia-gestión
(enero–febrero de 2027), organizado con el proyecto MOTIVATE, el servicio Copernicus de vigilancia terrestre (CLMS),
IALE-España y la red BigBioData de la AEET.</p></div>
{filters}<ul class="news" id="news">{''.join(news_item(n) for n in NEWS)}</ul>'''
    render('noticias/index.html', title='Noticias · EVEREST', section='noticias', color='teal',
           desc='Noticias, congresos, publicaciones y actividades del proyecto EVEREST.', body=body,
           hero=page_hero([('Noticias', None)], 'Noticias', 'Reuniones con gestores, congresos, publicaciones y divulgación.',
                          img='acequia'), toc=False)


def build_outputs():
    def refs(items):
        return '<ol class="refs">' + ''.join(f'<li>{i}</li>' for i in items) + '</ol>'
    papers = [
        '<span class="status ok">Publicado</span>Cazorla, B. P., Meijide, A., Cabello, J., Peñas, J., Martínez-López, J., '
        'Vargas, R., … y Alcaraz-Segura, D. (2026). Satellite-derived Ecosystem Functional Types capture ecosystem '
        'functional heterogeneity at regional scale. <em>Biogeosciences</em>, 23(3), 1223–1243. '
        + ext('https://doi.org/10.5194/bg-23-1223-2026', 'doi:10.5194/bg-23-1223-2026'),
        '<span class="status ok">Publicado</span>Llodrà-Llabrés, J., Pérez-Girón, J. C., Postma, T., Pérez-Martínez, C., '
        'Alcaraz-Segura, D. y Martínez-López, J. (2026). Satellite solutions: Facing chlorophyll-a retrieval in small '
        'mountain lakes in the Sierra Nevada, Spain. <em>Water Resources Research</em>, 62(3), e2026WR043523.',
    ]
    chapters = [
        '<span class="status ok">Aceptado</span>Cazorla, B. P., Martínez-López, J., Guerrero, P., Navarro, C., Bello, T., '
        'Zamora, R. y Alcaraz-Segura, D. MonitorEO-OBSNEV: Monitoring Essential Biodiversity Variables using Earth '
        'Observations in Biosphere Reserves. En Reed, M. G., Måren, I. E., Sandström, C. y Moreira-Muñoz, A. (eds.), '
        '<em>Routledge Handbook of UNESCO Biosphere Reserves</em>. Routledge (en prensa).',
    ]
    review = [
        '<span class="status">En revisión</span>Cazorla, B. P., Navarro, C., Martínez-López, J., Postma, T., Leverkus, A., '
        'Alcaraz-Segura, D. y Castro, J. Burnt-tree retention maximizes snow cover after wildfire. <em>Ecological Applications</em>.',
        '<span class="status">En revisión</span>Castañeda, I., Cazorla, B. P., Escudero-Clares, M., Alcaraz-Segura, D., '
        'Salinas-Bonillo, M. J. y Cabello, J. Landscape functional units: mapping the functional organization of a '
        'Mediterranean mountain socio-ecological system (Sierra Nevada, Spain). <em>Land</em>.',
        '<span class="status">En revisión</span>Villar-Argaiz, M., Biddanda, B. A., Cazorla, B. P. y Camacho, J. Beyond '
        'global means: Ice cover and topography drive rapid warming in Mediterranean high-mountain lakes. '
        '<em>Limnology and Oceanography</em>.',
        '<span class="status">En revisión</span>Valdés, A., Álvarez-Martínez, J. M., González Le Barbier, J., '
        'Hernández-Romero, G., Cazorla, B. P., … y Jiménez-Alfaro, B. A remote sensing-based framework for spatial '
        'validation of vegetation databases. <em>Applied Vegetation Science</em>.',
    ]
    talks = {
        '2026': [
            'Cazorla, B. P., Alcaraz-Segura, D., Zamora, R. y Martínez-López, J. Mapeo y evaluación del estado de conservación de hábitats de pastizales alpinos mediante teledetección. VII Jornadas Lagunas de Sierra Nevada, 4–6/09/2026. Oral.',
            'Bello-Rodríguez, T., Cazorla, B. P., Fernández-Bermejo, S., Álvarez-Martínez, J. M., Cabello, J., Zamora, R., Alcaraz-Segura, D. y Martínez-López, J. Policy relevant remote sensing EBVs for conservation status assessment in mountain protected areas. 68th Annual Symposium of the IAVS, Gijón, 22–26/06/2026. Oral.',
            'Valdés, A., Álvarez-Martínez, J. M., González Le Barbier, J., Hernández-Romero, G., Cazorla, B. P. y Jiménez-Alfaro, B. Validation of plot locations in vegetation databases using remote sensing. 68th Annual Symposium of the IAVS, Gijón, 22–26/06/2026. Oral.',
            'Cazorla, B. P., Postma, T., Alcaraz-Segura, D., Martínez-López, J., Agea-Plaza, D., Cabrera-Carrillo, G., Guerrero, P., Galiana, M. y Zamora, R. Validating near-ground snow detection with multi-sensor satellite observations in a Mediterranean mountain (Sierra Nevada, Spain). III Microclimate Ecology and Biogeography Conference, Montpellier, 1–5/06/2026. Oral.',
            'Cazorla, B. P., Martínez-López, J., Guerrero, P., Navarro, C., Cabrera-Carrillo, G., Agea-Plaza, D., Postma, T., Bello, T., Zamora, R. y Alcaraz-Segura, D. From satellite observations to near-ground microclimate: operational integration within the MONITOREO platform. III Microclimate Ecology and Biogeography Conference, Montpellier, 1–5/06/2026. Póster.',
            'Cazorla, B. P., Alcaraz-Segura, D., Guerrero, P., Navarro, C., Postma, T., Bello, T., Mellado, A., Zamora, R. y Martínez-López, J. EVEREST y MonitorEO-OBSNEV. Seminario del MITECO y el CENEAM, Valsaín (Segovia), 22–23/04/2026. Oral.',
        ],
        '2025': [
            'Bello-Rodríguez, T., Cazorla, B. P., Zamora, R., Alcaraz-Segura, D. y Martínez-López, J. Essential Variables for the rEmote characterisation and monitoRing of mountain EcosystemS (EVEREST). Workshop «The Eyes on Pirineu\'s lakes», Universitat de Barcelona, 28–31/10/2025. Oral.',
            'Cazorla, B. P., Guerrero, P., Alcaraz-Segura, D., Navarro, C., Bello, T., Postma, T., Zamora, R. y Martínez-López, J. MonitorEO-OBSNEV: seguimiento de Variables Esenciales de la Biodiversidad mediante teledetección. Jornadas del IISTA, Granada, octubre de 2025. Póster.',
            'Rodríguez Correal, F., Mesa Millán, F., …, Cazorla, B. P., et al. Diseño de Microrreservas de Biodiversidad en la Estación de Esquí y Montaña de Sierra Nevada (Granada). II Congreso Nacional de Botánica, Sevilla, 22–25/09/2025. Póster.',
            'Cazorla, B. P., Alcaraz-Segura, D., Postma, T., Navarro, C. J., Guerrero, P., Mellado, A., Zamora, R. y Martínez-López, J. Essential Variables for the rEmote characterisation and monitoRing of mountain EcosystemS along a biogeographical gradienT: from data to decision making (EVEREST). International Mountain Conference (IMC25), Innsbruck, 14–18/09/2025. Oral.',
            'Valdés, A., Álvarez-Martínez, J. M., Cazorla, B. P., et al. Validation of plot locations in vegetation databases using remotely sensed Essential Biodiversity Variables. European Landscape Ecology Congress, Bratislava, 2025. Oral.',
            'Bello-Rodríguez, T., Cazorla, B. P., Zamora, R., Alcaraz-Segura, D. y Martínez-López, J. Variables esenciales para la caracterización y seguimiento remoto de ecosistemas de montaña (EVEREST). III Jornada de Ecología, Universidad de Granada, 13/06/2025. Conferencia invitada.',
        ],
        '2024': [
            'Cazorla, B. P., et al. Variables esenciales para la caracterización y seguimiento remoto de ecosistemas de montaña a lo largo de un gradiente biogeográfico: del dato a la toma de decisiones (EVEREST). II Congreso Internacional de las Montañas de Sierra Nevada (CIMAS), Granada, 7–9/11/2024. Oral.',
            'Martínez-López, J. Essential Ecosystem Service Variables and Models in Mountain Areas: A case study in Sierra Nevada (Spain). CIMAS, Granada, 7–9/11/2024. Oral.',
            'Rodríguez Correal, F., Mesa Millán, F., Cazorla, B. P., et al. Microrreservas de Biodiversidad en la Estación de Esquí y Montaña de Sierra Nevada. CIMAS, Granada, 7–9/11/2024. Póster.',
            'Martínez-López, J., Alcaraz-Segura, D., Zamora, R. y Mellado, A. Presentación del proyecto EVEREST. XIII Seminario de Seguimiento a Largo Plazo en la Red de Parques Nacionales, Valsaín (Segovia), 30/09–02/10/2024. Oral.',
        ],
    }
    theses = [
        '<span class="status">Tesis en curso</span>Ingrid Tatiana Bello Rodríguez. Variables esenciales derivadas de '
        f'teledetección para el seguimiento de ecosistemas de montaña. Universidad de Granada. Dirección: {JML} y {DAS}.',
        '<span class="status ok">TFM</span>Soledad Fernández Bermejo (2025). Compilación de variables y métricas usadas para '
        'la evaluación del estado de conservación de hábitats de interés comunitario mediante modelos de inteligencia '
        'artificial y evaluación de su posible monitorización mediante teledetección. Máster en Conservación, Gestión y '
        'Restauración de la Biodiversidad, Universidad de Granada.',
        '<span class="status ok">TFM</span>Nicole Salinas Agudelo (2026). Mejora cartográfica de los borreguiles de alta '
        'montaña del Parque Nacional Sierra Nevada (España) mediante teledetección y modelización para su seguimiento y '
        'gestión. Máster en Conservación, Gestión y Restauración de la Biodiversidad, Universidad de Granada.',
        '<span class="status ok">TFM</span>Irene Castañeda Laborde (2026). Organización funcional del paisaje en Sierra '
        'Nevada: entre el gradiente climático y la historia socioecológica. Máster en Uso Sostenible de Recursos Naturales '
        'y Servicios Ecosistémicos, Universidad de Almería.',
    ]
    year_colors = {'2026': 'purple', '2025': 'teal', '2024': 'orange'}
    body = f'''<section class="prose"><p class="intro">Los artículos se publican en acceso abierto siempre que es posible,
con los datos y el código disponibles.</p></section>
<section class="prose c-green"><h2>Artículos</h2>{refs(papers)}</section>
<section class="prose c-blue"><h2>Capítulos de libro</h2>{refs(chapters)}</section>
<section class="prose c-orange"><h2>En revisión</h2>{refs(review)}</section>
<section class="prose"><h2>Congresos y jornadas</h2>{''.join(f'<div class="c-{year_colors[y]}"><span class="year">{y}</span>' + refs(v) + '</div>' for y, v in talks.items())}</section>
<section class="prose c-teal"><h2>Tesis y trabajos fin de máster</h2>{refs(theses)}</section>'''
    render('resultados/publicaciones.html', title='Publicaciones · EVEREST', section='resultados', color='purple',
           desc='Artículos, capítulos, comunicaciones a congresos y trabajos académicos del proyecto EVEREST.',
           body=body, hero=page_hero([('Resultados', None)], 'Publicaciones', 'Artículos, capítulos, congresos y trabajos académicos.',
                                     img='amanecer'))

    repos = [('MonitorEO', 'Series, mapas y tendencias de las Variables Esenciales de la Biodiversidad para cualquier zona', 'Productos de datos', ext(MONITOREO_APP, 'Disponible')),
             ('GitHub', 'Código de MonitorEO y de los análisis', 'Código abierto (GPL-3.0)', ext(MONITOREO_GH, 'Disponible')),
             ('Zenodo', 'Versiones citables del software y de los conjuntos de datos', 'DOI', ext(MONITOREO_DOI, 'Disponible')),
             ('GeoServer del Observatorio y LifeWatch ERIC', 'Productos de imagen accesibles desde cualquier SIG', 'WMS, WCS y WFS', 'Previsto')]
    body = f'''<section class="prose"><p class="intro">La calidad de los datos y la ciencia abierta están en el centro del
proyecto: seguimos los principios FAIR (localizables, accesibles, interoperables y reutilizables) y los de intercambio de
datos de GEO.</p></section>
<section><h2>Gestión de datos</h2>
<p class="prose">Toda la información que produce el proyecto se evalúa y se acompaña de sus metadatos para que sea
transparente y reproducible. El plan de gestión de datos se actualiza durante el proyecto.</p>
<div class="dims">
  <div class="dim c-blue"><h3>{icon('satellite')}Teledetección</h3><p>Variables Esenciales de la Biodiversidad y métricas derivadas de MODIS,
  Landsat, Sentinel-2, PlanetScope y LiDAR, calculadas en Google Earth Engine.</p></div>
  <div class="dim c-orange"><h3>{icon('snow')}Sensores en campo</h3><p>Sensores de microclima (temperatura y humedad del
  suelo y del aire) y nieve del Observatorio de Cambio Global de Sierra Nevada.</p></div>
  <div class="dim c-green"><h3>{icon('leaf')}Observaciones de campo</h3><p>Puntos de verdad terreno de borreguiles,
  muestreos de las lagunas y datos de los programas de seguimiento de los parques.</p></div>
</div></section>
<section><h2>Dónde encontrar los datos</h2>
<div class="table-wrap"><table><thead><tr><th>Repositorio</th><th>Contenido</th><th>Formato</th><th>Estado</th></tr></thead>
<tbody>{''.join(f'<tr><td><strong>{a}</strong></td><td>{b}</td><td>{c}</td><td>{d}</td></tr>' for a, b, c, d in repos)}</tbody></table></div>
</section>
<section class="prose c-teal"><h2>Cómo citar MonitorEO</h2>
<p>MonitorEO tiene un DOI en Zenodo: {ext(MONITOREO_DOI, 'doi:10.5281/zenodo.23814894')}. Las publicaciones del
proyecto citan además la referencia de financiación PID2023-151939OB-I00.</p></section>
<section class="prose c-orange"><h2>Datos personales</h2>
<p>El proyecto solo recoge datos personales en los talleres participativos: los datos de contacto de los participantes,
con su consentimiento libre, específico, informado e inequívoco. Se guardan en un almacenamiento seguro al que solo accede
el equipo, y las respuestas se seudonimizan para su análisis.</p></section>'''
    render('resultados/datos.html', title='Datos abiertos · EVEREST', section='resultados', color='purple',
           desc='Gestión de datos, repositorios y principios de ciencia abierta del proyecto EVEREST.',
           body=body, hero=page_hero([('Resultados', None)], 'Datos abiertos', 'Datos, código y productos accesibles y reutilizables.',
                                     img='satelite'))

    apps = [('teal', 'drop', 'Lagunas', 'Delimitación de las láminas de agua de las lagunas con imágenes PlanetScope.'),
            ('green', 'leaf', 'Verdad terreno de borreguiles', 'Verificación experta de puntos con aprendizaje activo para mejorar la cartografía.'),
            ('blue', 'layers', 'Estado de conservación', 'Evaluación del estado de conservación de los hábitats para usuarios sin programación (en desarrollo).'),
            ('purple', 'pin', 'Modelos de idoneidad', 'Modelos de idoneidad del hábitat para usuarios sin programación.'),
            ('orange', 'sprout', 'Pastos y acequias', 'Seguimiento de los pastos y del efecto de las acequias (prevista).')]
    body = f'''<section class="prose"><p class="intro">EVEREST comunica en tres niveles: a la comunidad científica, a los
usuarios finales (gestores, administraciones y población local) y al público general.</p></section>
<section class="c-teal"><h2>MonitorEO</h2>
<p class="prose">Herramienta abierta para seguir Variables Esenciales de la Biodiversidad con datos de satélite. Calcula en
Google Earth Engine series temporales, mapas y tendencias de vegetación, agua, nieve, energía y perturbaciones a partir de
MODIS, Landsat y Sentinel-2, siempre con el mismo cálculo en todas sus herramientas.</p>
<div class="tool">
  {leads(['<strong>Público general:</strong> MonitorEO web, sin instalación ni cuenta propia, y visor de resultados en el navegador.',
          '<strong>Gestores:</strong> complemento de QGIS y un asistente conversacional que prepara mapas, series e informes a partir de preguntas en lenguaje natural.',
          '<strong>Científicos y técnicos:</strong> paquetes de Python y R, línea de comandos y servidor MCP.'])}
  <ul class="links">
    <li><a href="@/monitoreo.html">Conoce MonitorEO</a></li>
    <li>{ext(MONITOREO_APP, 'MonitorEO web')}</li>
    <li>{ext(MONITOREO_GH + '/wiki', 'Documentación')}</li>
    <li>{ext(MONITOREO_GH, 'Código abierto')}</li>
    <li>{ext(MONITOREO_DOI, 'Cómo citarla')}</li>
  </ul>
</div></section>
<section><h2>Aplicaciones complementarias</h2>
<div class="cards">{''.join(f'<article class="card c-{c}"><span class="icon">{icon(i)}</span><h3>{a}</h3><p>{b}</p></article>' for c, i, a, b in apps)}</div></section>
<section class="prose c-blue"><h2>Manuales y formación</h2>
{leads(['Manual en línea y manuales de usuario en español e inglés (diciembre de 2025).',
        'Videotutoriales (marzo de 2025).',
        'Formulario de incidencias y sugerencias, activo desde abril de 2025.',
        'Formación a los técnicos del Espacio Natural Sierra Nevada (27 de enero de 2026) y, tras cada nueva versión, formación en línea para los gestores de los parques.',
        'Taller nacional ciencia-gestión (enero–febrero de 2027).'])}
</section>
<section class="prose c-orange"><h2>Divulgación</h2>
{leads(['Noche Europea de los Investigadores, Granada (2024).',
        'Jornadas Lagunas de Sierra Nevada, campaña de ciencia ciudadana (18–20 de julio de 2025).',
        'Taller en la Feria de Sostenibilidad de Granada «Alianzas locales para una Granada sostenible», Palacio Quinta Alegre (22 de octubre de 2025).',
        'Talleres para estudiantes de institutos de Granada en el IISTA (6 de noviembre de 2025).'])}
{figure('sierra-nevada')}
</section>
<section class="prose c-purple"><h2>Próximamente</h2>
{leads(['Guías para los gestores de los parques.',
        'Vídeo documental y exposición de pósteres para los centros de visitantes de los parques.',
        'Infografías de los casos de estudio en esta web.'])}
<p class="muted">Los materiales se añadirán aquí a medida que estén disponibles.</p></section>'''
    render('resultados/recursos.html', title='Recursos y divulgación · EVEREST', section='resultados', color='purple',
           desc='MonitorEO, aplicaciones, manuales, formación y divulgación del proyecto EVEREST.',
           body=body, hero=page_hero([('Resultados', None)], 'Recursos y divulgación',
                                     'Herramientas, formación y materiales para gestores, científicos y ciudadanía.',
                                     img='picos-de-europa'))


def build_monitoreo():
    groups = [('teal', 'drop', 'Balance de agua', 'Evapotranspiración y calor latente (MODIS), humedad de la superficie (LSWI, NDWI) y nieve (NDSI), con Landsat, Sentinel-2 y MODIS.'),
              ('orange', 'sun', 'Radiación y temperatura', 'Albedo (Landsat, Sentinel-2 y MODIS) y temperatura de la superficie terrestre (Landsat y MODIS).'),
              ('green', 'leaf', 'Carbono y producción primaria', 'Verdor de la vegetación (NDVI, EVI), índice de área foliar (LAI) y clorofila-a y NDCI en el agua.'),
              ('purple', 'cloud', 'Aerosoles', 'Espesor óptico de aerosoles de MODIS.')]
    ops = ['Series temporales y mapas para cualquier zona, del recinto de una laguna a un parque entero.',
           'Tendencias (prueba de Mann-Kendall y pendiente de Sen) y anomalías respecto a la variabilidad histórica.',
           'Comparaciones entre zonas y entre periodos.',
           'Filtrado de nubes, agua y calidad de los píxeles, y análisis de grandes áreas.',
           'Módulo de microclima que integra los sensores de campo.',
           'Descarga de resultados y servicios para cualquier SIG.']
    tools = [('blue', 'globe', 'MonitorEO web', 'En Google Earth Engine, sin instalar nada ni crear una cuenta.'),
             ('teal', 'map', 'Visor de resultados', 'Para consultar y compartir los resultados en el navegador.'),
             ('green', 'layers', 'Complemento de QGIS', 'Las mismas variables dentro del SIG que ya usan los gestores.'),
             ('orange', 'chat', 'Asistente conversacional', 'Prepara mapas, series e informes a partir de preguntas en lenguaje natural.'),
             ('purple', 'plug', 'Servidor MCP', 'Conecta MonitorEO con asistentes de inteligencia artificial.'),
             ('blue', 'code', 'Paquete de Python', 'Para integrar los cálculos en flujos de trabajo propios.'),
             ('green', 'code', 'Paquete de R', 'Para el análisis estadístico de las series.'),
             ('orange', 'term', 'Línea de comandos', 'Para automatizar cálculos repetidos.')]
    body = f'''<section class="prose"><p class="intro"><strong>MonitorEO</strong> es una herramienta abierta para
seguir Variables Esenciales de la Biodiversidad con datos de satélite. Calcula en la nube, con Google Earth Engine, series
temporales, mapas, tendencias y anomalías de vegetación, agua, nieve, energía y perturbaciones, y se co-diseña con los
gestores para que la usen en sus planes de seguimiento y en sus informes europeos.</p>
<ul class="links"><li>{ext(MONITOREO_APP, 'MonitorEO web')}</li><li>{ext(MONITOREO_GH + '/wiki', 'Documentación')}</li>
<li>{ext(MONITOREO_GH, 'Código en GitHub')}</li><li>{ext(MONITOREO_DOI, 'Cómo citarla')}</li></ul></section>
<section class="c-teal" style="margin-top:36px">{MONITOREO_STATS.replace('class="mstats"', 'class="mstats light"')}</section>
<section><h2>Para los informes europeos</h2>
<p class="prose">EVEREST amplía MonitorEO con un módulo para cada obligación de reporte de los espacios protegidos.</p>
{regs_html()}</section>
<section><h2>Qué calcula</h2>
<div class="dims">{''.join(f'<div class="dim c-{c}"><h3>{icon(i)}{t}</h3><p>{d}</p></div>' for c, i, t, d in groups)}</div>
<div class="prose">{leads(ops)}</div></section>
<section><h2>Para quién</h2><div class="cards fit">{MONITOREO_PROFILES}</div></section>
<section><h2>Ocho formas de usarla</h2>
<p class="prose">Todas las herramientas comparten el mismo núcleo de cálculo, así que dan los mismos resultados.</p>
<div class="cards">{''.join(f'<article class="card c-{c}"><span class="icon">{icon(i)}</span><h3>{t}</h3><p>{d}</p></article>' for c, i, t, d in tools)}</div></section>
<section class="prose c-orange"><h2>Co-diseñada con los gestores</h2>
{leads(['Cinco reuniones de co-diseño, validación y formación con técnicos del Espacio Natural Sierra Nevada entre diciembre de 2024 y enero de 2026, con 9 gestores y 19 participaciones.',
        'Nuevas funciones implementadas a partir de sus propuestas: zonas para repoblación, eficacia de los tratamientos selvícolas, pastos, nieve y agua.',
        'Descargas, servicios para SIG y complemento de QGIS para quienes no pueden acceder a algunos servicios de Google desde su red.',
        'Formulario de incidencias y sugerencias, activo desde abril de 2025.',
        'Reunión con el Organismo Autónomo Parques Nacionales (30 de octubre de 2026) sobre su uso en la Red de Parques Nacionales y su integración con REMOTE.'])}
{figure('borreguil')}</section>
<section><h2>Aplicaciones complementarias</h2>
<p class="prose">Para tareas concretas que no requieren programar: delimitación de lagunas con PlanetScope, verdad terreno
y cartografía de borreguiles, estado de conservación y modelos de idoneidad del hábitat.
<a class="more" href="@/resultados/recursos.html#aplicaciones-complementarias">Ver las aplicaciones</a></p></section>
<section class="prose c-purple"><h2>Origen y cita</h2>
<p>MonitorEO nació en el proyecto {ext('https://smartecomountains.lifewatch.dev', 'SmartEcoMountains')} de LifeWatch ERIC y
la desarrolla el Observatorio de Cambio Global de Sierra Nevada (Universidad de Granada), con los proyectos NevadEO,
PRESINMED y EVEREST. Es código abierto (licencia GPL-3.0) y tiene un DOI en Zenodo:
{ext(MONITOREO_DOI, 'doi:10.5281/zenodo.23814894')}.</p></section>'''
    render('monitoreo.html', title='MonitorEO · EVEREST', section='monitoreo', color='teal',
           desc='MonitorEO, la herramienta abierta de EVEREST para seguir Variables Esenciales de la Biodiversidad con '
                'datos de satélite y apoyar los informes europeos.', body=body,
           hero=page_hero([('Herramienta', None)], 'MonitorEO',
                          'Del satélite al informe, sin programar: Variables Esenciales de la Biodiversidad para gestores, '
                          'científicos y ciudadanía.', img='nieve-satelite'))


def gallery_item(ph, cls):
    return (f'<figure class="{cls}"><button type="button" data-full="{ph["src"]}" aria-label="Ampliar: {ph["cap"]}">'
            f'{img_tag(ph)}</button><figcaption><b>{ph["cap"]}</b> · {credit(ph)}</figcaption></figure>')


def build_gallery():
    parks = ''.join(gallery_item(p['photo'], p['region']) for p in PARKS)
    extra = ''.join(gallery_item(PHOTOS[pid], f'c-{PALETTE[i % len(PALETTE)]}') for i, pid in enumerate(EXTRA_PHOTOS))
    body = f'''<section><p class="prose">Pulsa en una foto para ampliarla. Los miembros del equipo pueden enviar sus fotos de
campo para publicarlas aquí, indicando autoría, lugar y fecha.</p>
<h2>Los parques</h2><div class="gallery">{parks}</div></section>
<section><h2>Paisajes y satélite</h2><div class="gallery">{extra}</div></section>
<section><h2>Ilustraciones del proyecto</h2>
<h3>Los ocho parques</h3><figure class="map-figure">{map_svg('gal-map', link=True)}{legend()}</figure>
<h3>Del satélite a la decisión</h3>{PIPELINE}
<h3>Métricas de recuperación</h3>{recovery_figure()}
</section>
<dialog class="lightbox" id="lightbox" aria-label="Foto ampliada"><button type="button" class="close" aria-label="Cerrar">×</button>
<img alt=""><p></p></dialog>'''
    render('galeria.html', title='Galería · EVEREST', section='galeria', color='blue',
           desc='Fotos de los parques nacionales y figuras del proyecto EVEREST.', body=body,
           hero=page_hero([('Galería', None)], 'Galería', 'Los parques del proyecto, vistos desde el suelo y desde el espacio.',
                          img='teide'), toc=False)


def build_contact():
    people = ''.join(f'<p><strong>{n}</strong><br>{icon("mail")} <a href="mailto:{m}">{m}</a></p>' for n, m in CONTACTS)
    body = f'''<div class="contact">
<article class="inst c-blue"><p class="acr">Coordinación</p><h3>Investigadores principales</h3>
{people}<p class="muted">Universidad de Granada · Granada, España</p></article>
<article class="inst c-teal"><p class="acr">MonitorEO</p><h3>Dudas, incidencias y sugerencias</h3>
<p>Para la herramienta, usa la {ext(MONITOREO_GH + '/issues', 'página de incidencias en GitHub')} o consulta la
{ext(MONITOREO_GH + '/wiki', 'documentación')}.</p></article>
</div>
<section class="prose c-orange" style="margin-top:48px"><h2>Financiación</h2>
<p>{FUND}</p>
<p>EVEREST pertenece a la convocatoria de Proyectos de Generación de Conocimiento 2023 del Plan Estatal de Investigación
Científica, Técnica y de Innovación. Más información en la web de la {ext('https://www.aei.gob.es', 'Agencia Estatal de Investigación')}.</p>
<div class="contact-fund"><div class="logos"><img src="@/img/financiacion.png" width="1905" height="370" alt="{FUND_ALT}" loading="lazy"></div></div>
</section>'''
    render('contacto.html', title='Contacto · EVEREST', section='contacto', color='blue',
           desc='Contacto y financiación del proyecto EVEREST.', body=body,
           hero=page_hero([('Contacto', None)], 'Contacto', 'Coordinación del proyecto, soporte de MonitorEO y financiación.',
                          img='sierra-nevada'), toc=False)


FAVICON = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="-2 -2 44 44"><rect x="-2" y="-2" width="44" height="44" rx="10" fill="#0a2440"/>'
           f'{LOGO}</svg>')

if __name__ == '__main__':
    (ROOT / 'img' / 'favicon.svg').write_text(FAVICON, encoding='utf-8')
    build_home(); build_project(); build_variables(); build_tasks(); build_parks()
    build_team(); build_news(); build_outputs(); build_gallery(); build_contact(); build_monitoreo()
    pages = sorted(str(p.relative_to(ROOT)).replace('\\', '/') for p in ROOT.rglob('*.html'))
    print(len(pages), 'páginas generadas')
