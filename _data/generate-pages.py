import sys
import os
sys.path.append(os.path.dirname(__file__)+'/lib')
import yaml
from datetime import datetime
from dateutil.parser import parse
import re
import random

with open('_data/incidents.yml') as file:
    # The FullLoader parameter handles the conversion from YAML
    # scalar values to Python the dictionary format
    incidents = yaml.load(file, Loader=yaml.FullLoader)

with open('_data/annual_stats.yml') as file:
    annual_stats = yaml.load(re.sub(r',', '', file.read()), Loader=yaml.FullLoader)

with open('_data/police_areas.yml') as file:
    police_areas = yaml.load(file, Loader=yaml.FullLoader)

with open('_data/vehicle_types.yml') as file:
    vehicle_types = yaml.load(file, Loader=yaml.FullLoader)
used_vehicle_types = dict()

for police_area in police_areas:
    if isinstance(police_areas[police_area], str):
        police_areas[police_area] = {
            'index' : police_areas[police_area],
        }
    if 'news' in police_areas[police_area]:
        del police_areas[police_area]['news']

with open('_data/police_areas.yml', "w") as text_file:
    text = yaml.dump(police_areas)
    text_file.write(text)

with open('_data/police_domain_to_name.yml') as file:
    police_domain_to_name = yaml.load(file, Loader=yaml.FullLoader)

for incident in incidents:
    for key in ['comment', 'community-order', 'court', 'date-of-incident', 'date-of-sentence', 'disqualification', 'editor-notes', 'identifier', 'imprisonment', 'killer-vehicle', 'links', 'offender-/-driver', 'plea', 'police-area', 'police-code', 'victim', 'victim-dob', 'victim-vehicle', 'tags']:
        if key not in incident:
            incident[key] = None
    if 'victim' in incident and isinstance(incident['victim'], str) and '–' in incident['victim']:
        name, dob, doi = re.findall(r'(.+?) *\(([^–]+?) *– *([^\)]+)\)', incident['victim'])[0]
        incident['victim'] = name
        incident['victim-dob'] = dob
        incident['date-of-incident'] = doi
        if not isinstance(incident['police-code'], str) and not isinstance(incident['police-code'], list):
            incident['police-code'] = str(incident['police-code'])

def check_incident(incident):
    for key in ['links', 'date-of-incident', 'victim']:
        if key in incident and incident[key] is not None:
            # print(incident['identifier'] + ' : ' +key)
            return True
    return False



incidents = list(filter(check_incident, incidents))

# print(incidents)

table = ""

def listify(value):
    if value is None:
        return []
    elif isinstance(value, list):
        return list(value)
    else:
        return [value]

def stringify(value):
    if isinstance(value, list):
        return "<br>".join(map(stringify, value))
    elif value is None:
        return '' # <span class="none">?</span>'
    else:
        return re.sub(' ', '&nbsp;', str(value))

def linkify(value):
    if isinstance(value, list):
        return "<br>".join(map(linkify, value))
    elif value is None:
        return stringify(value)
    elif value.startswith('https://twitter.com/'):
        return '<a href="{link}" target="_blank">{text}</a>'.format(link=value, text=re.sub(r'https://twitter.com/([^/]+).*', '@\\1', value))
    else:
        return '<a href="{link}" target="_blank">{text}</a>'.format(link=value, text=re.sub(r'https?://(?:(?:www|en|news)\.)?([^/]+).*', '\\1', value))

def getrandhex(length):
    return ('%0'+str(length)+'x') % random.getrandbits(length*4)

def parse_date(value):
    try:
        return parse(value)
    except:
        return None

def incident_order(incident):
    if 'date-of-incident' in incident and isinstance(incident['date-of-incident'], str):
        return parse(incident['date-of-incident']).strftime('%Y-%m-%d') + '/'.join(listify(incident['victim']))
    else:
        return '0000-00-00' + '/'.join(listify(incident['victim']))


tag_tansforms = {
    "drug" : "drugs",
    "motorcycle" : "motorbike",
    "child" : "",
}

def transform_tags(tag):
    if tag in tag_tansforms:
        return tag_tansforms[tag]
    return tag

incidents.sort(reverse=True, key=incident_order)

total_victim_count = 0

first_year = 1896

total_fatalities = 0

for year in range(first_year, datetime.today().year+1):
    if year not in annual_stats:
        annual_stats[year] = {'total' : None}
    annual_stats[year]['covered'] = 0

for incident in incidents:
    date_of_incident = parse_date(incident['date-of-incident'])
    victim_count = len(listify(incident['victim']))
    if date_of_incident:
        incident['date-of-incident'] = date_of_incident.strftime('%a, %-d %b %Y')
        annual_stats[date_of_incident.year]['covered'] += victim_count

    total_victim_count += victim_count

    if 'identifier' not in incident or incident['identifier'] is None:
        incident['identifier'] = getrandhex(7)

    if isinstance(incident['links'], str):
        links = re.findall(r'(https?://\S+)', incident['links'])
        if len(links) > 1:
            incident['links'] = links

    if isinstance(incident['tags'], str):
        tags = re.findall(r'(\S+)', incident['tags'])
        incident['tags'] = tags

    if isinstance(incident['tags'], list):
        incident['tags'] = ' '.join(sorted(set(map(transform_tags, incident['tags']))))

    if isinstance(incident['links'], list):
        incident['links'].sort()

    if 'police-area' not in incident or incident['police-area'] is None:
        for link in listify(incident['links']):
            # print(link)
            result = re.match(r'https://(?:(?:www|news)\.)?([^.]+)\.police\.uk/', link)
            if result:
                incident['police-area'] = police_domain_to_name[result.groups()[0]]

    def handle_victim(victim):
        table = ''
        table += '<tr id="%s">' % incident['identifier']
        table += '<td/>'
        table += '<td class="column victim">%s</td>' % stringify(victim)
        table += '<td class="column date">%s</td>' % (incident['date-of-incident'] or '')

        vehicles = listify(incident['killer-vehicle']) + listify(incident['victim-vehicle']) + listify(incident['tags'])
        vehicles = map(lambda e: re.findall(r'(\S+)', e), vehicles)

        tags = set()
        for vehicle in [y for x in vehicles for y in x]:
            vehicle = vehicle.lower()
            if vehicle in vehicle_types:
                used_vehicle_types[vehicle] = vehicle_types[vehicle]
                if vehicle_types[vehicle] is not None:
                    tags.add(vehicle)
            else:
                used_vehicle_types[vehicle] = None

        table += '<td class="column collision">%s</td>' % ' '.join(map(lambda tag:'<font face="FontAwesome" title="%s">&#x%s;</font>' % (re.sub('-', ' ', tag), vehicle_types[tag]), sorted(tags)))
        # table += '<td class="column driver">%s</td>' % stringify(incident['offender-/-driver'] if 'offender-/-driver' in incident else None)
        if 'police-area' in incident and incident['police-area'] is not None:
            table += '<td class="column police-area">'
            if isinstance(incident['police-area'], list):
                incident['police-area'].sort()
            for index, police_area in enumerate(listify(incident['police-area'])):
                if index > 0:
                    table += '<br>'
                if police_area in police_areas:
                    table += '<a href="{link}" target="_blank">{text}</a>'.format(link=police_areas[police_area]['index'], text=police_area)
                elif police_area is not None:
                    exit('Invalid police area: %s' % police_area)
                else:
                    table += stringify(police_area)
            table += '</td>'
        else:
            table += '<td class="column police-area">%s</td>' % stringify(None)
        table += '<td class="column police-code">%s</td>' % stringify(incident['police-code'] if 'police-code' in incident else None)
        table += '<td class="column links">%s</td>' % linkify(incident['links'] if 'links' in incident else None)
        table += '<td><a href="#%s"><span class="eep">&#xF0C1;</span></a></td>' % incident['identifier']
        table += '</tr>\n'
        # table += '<tr><td colspan="6"><pre>'+yaml.dump(incident)+'</pre></td></tr>\n'
        return table

    # if isinstance(incident['victim'], list):
    #     for victim in incident['victim']:
    #         table += handle_victim(victim)
    # else:
    table += handle_victim(incident['victim'])

coverage = ''
current_decade = int(10 * round(float(datetime.today().year)/10))
while True:
    coverage += '<tr>'
    coverage += '<th>%s</th>' % stringify(current_decade)
    for year in range(current_decade, current_decade + 10):
        if year in annual_stats:
            if 'total' in annual_stats[year] and annual_stats[year]['total'] is not None:
                total_fatalities += annual_stats[year]['total']
                coverage += '<td>%s <span class="none">/</span> %s</td>' % (stringify(annual_stats[year]['covered']), annual_stats[year]['total'])
            else:
                total_fatalities += annual_stats[year]['covered']
                coverage += '<td>%s</td>' % stringify(annual_stats[year]['covered'])
        else:
            coverage += '<td>%s</td>' % stringify(None)

    coverage += '</tr>\n'
    if current_decade < first_year:
        break
    current_decade -= 10



index_page = """<!DOCTYPE html>
<html>
  <head>
    <link rel="stylesheet" href="assets/index.css">

    <link rel="icon" type="image/png" href="/favicon.png">
        
    <link rel="icon" type="image/png" href="/favicon-dark.png" media="(prefers-color-scheme: dark)">


    <!-- HTML Meta Tags -->
    <title>Road Deaths</title>
    <meta name="description" content="Traffic crash deaths the United Kingdom of Great Britain and Northern Ireland since 1896.">

    <!-- Facebook Meta Tags -->
    <meta property="og:url" content="https://jjrscott.github.io/road-deaths/">
    <meta property="og:type" content="website">
    <meta property="og:title" content="Road Deaths">
    <meta property="og:description" content="Traffic crash deaths the United Kingdom of Great Britain and Northern Ireland since 1896.">
    <meta property="og:image" content="https://jjrscott.github.io/road-deaths/assets/og-image.png">

    <!-- Twitter Meta Tags -->
    <meta name="twitter:card" content="summary_large_image">
    <meta property="twitter:domain" content="jjrscott.github.io">
    <meta property="twitter:url" content="https://jjrscott.github.io/road-deaths/">
    <meta name="twitter:title" content="Road Deaths">
    <meta name="twitter:description" content="Traffic crash deaths the United Kingdom of Great Britain and Northern Ireland since 1896.">
    <meta name="twitter:image" content="https://jjrscott.github.io/road-deaths/assets/og-image.png">

    <!-- Meta Tags Generated via https://www.opengraph.xyz -->

  </head>
  <body>
  <a href="" title="Road Deaths"><h1>Road Deaths</h1></a>

<p>
{total_victim_count} of the over {total_fatalities:,} <a href="https://crashnotaccident.com/" title="Crash Not Accident" target="_blank">traffic crash</a>
 deaths the
<a href="https://en.wikipedia.org/wiki/United_Kingdom" title="United Kingdom of Great Britain and Northern Ireland" target="_blank">United Kingdom of Great Britain and Northern Ireland</a> since {first_year}.
</p>

<p>This page is generated from <a href="https://github.com/jjrscott/road-deaths/blob/main/_data/incidents.yml">incidents.yml</a>.</p>

    <h2 id="victims">Victims</h2>

      <table class="victims">
        <tr>
            <th></th>
            <th class='column victim'>Victim</th>
            <th class='column incident-date'>Date</th>
            <th class='column tags'>Tags</th>
            <th class='column police-area'>Police Area</th>
            <th class='column police-code'>Police Code</th>

            <th class='column links'>Links</th>
            <th></th>
        </tr>
        {table}
     </table>

     <h2 id="coverage">Coverage</h2>
           <table>
             {coverage}
          </table>

    <h2 id="notes">Notes</h2>
    <p>
        The inspiration for this document came from a similar document entitled
        &ldquo;<a href="https://docs.google.com/document/d/1oXV2F5Ts8Ok0ky6928v3OUygeJ4TqG7Drc5axA1lKlE" target="_blank">Sentences for criminal driving</a>&rdquo;
        that was published around 2013, and an epic Twitter thread by <a href="https://twitter.com/ormondroyd">@ormondroyd</a> entitled
        &ldquo;<a href="https://twitter.com/ormondroyd/status/910244326567006211">A thread for all the pundits lining up to wring their hands about dangerous cycling and light sentencing</a>&rdquo;.
    </p>
    <h2 id="other-projects">Other Projects</h2>
    <ul>
        <li><a href="https://visionzerolondon.wordpress.com/latest-pedestrians-and-cyclists-deaths-in-london/">Vision Zero London</a></li>
        <li><a href="https://cyclistskilledontheroads.wordpress.com/">Cyclists killed on the Roads</a></li>
    </ul>
  </body>
</html>

""".format(table=table, total_victim_count=total_victim_count, coverage=coverage, total_fatalities=total_fatalities, first_year = first_year)

with open('index.html', "w") as text_file:
    text_file.write(index_page)

with open('_data/incidents.yml', "w") as text_file:
    text = yaml.dump(incidents)
    text = re.sub(r'(\A|\n)- ', '\\1-\n  ', text)
    text = ("""-
  comment:
  community-order:
  court:
  date-of-incident:
  date-of-sentence:
  disqualification:
  editor-notes:
  imprisonment:
  killer-vehicle:
  links:
  offender-/-driver:
  plea:
  police-area:
  police-code:
  tags:
  victim:
  victim-dob:
  victim-vehicle:
""" * 10) + text
    text_file.write(text)

with open('_data/annual_stats.yml', "w") as text_file:
    text = yaml.dump(annual_stats)
    text_file.write(text)

with open('_data/vehicle_types.yml', "w") as text_file:
    text = yaml.dump(used_vehicle_types)
    text_file.write(text)

print("%s / %s " % (total_victim_count, total_fatalities))
