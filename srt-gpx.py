import os
import re
import gpxpy.gpx
from datetime import datetime
from timezonefinder import TimezoneFinder
import pytz

# regex pattern for GPS info
pattern = re.compile(r'\[(\w+): ([\-\d\.]+)\]')

# regex pattern for altitude info
alt_pattern = re.compile(r'\[rel_alt: [\-\d\.]+ abs_alt: ([\-\d\.]+)\]')

input_dir = 'input'
output_dir = 'output'

os.makedirs(output_dir, exist_ok=True)

for filename in os.listdir(input_dir):
    if filename.lower().endswith('.srt'):
        with open(os.path.join(input_dir, filename), 'r') as f:
            content = f.read()

        gpx = gpxpy.gpx.GPX()

        gpx_track = gpxpy.gpx.GPXTrack()
        gpx.tracks.append(gpx_track)

        gpx_segment = gpxpy.gpx.GPXTrackSegment()
        gpx_track.segments.append(gpx_segment)

        tf = TimezoneFinder()

        local_tz = None

        blocks = content.split('\n\n')

        for block in blocks:
            lines = block.split('\n')
            if len(lines) >= 5:
                # Parse the timestamp from the fourth line
                timestamp_str = lines[3].strip()

                # Parse the GPS info from the fifth line
                gps_info = lines[4]

                # extract the latitude and longitude
                data = dict(pattern.findall(gps_info))

                if 'latitude' in data and 'longitude' in data:
                    lat, lon = float(data['latitude']), float(data['longitude'])

                    # Extract altitude
                    alt_match = alt_pattern.search(gps_info)
                    if alt_match:
                        alt = float(alt_match.group(1))
                    else:
                        alt = None  # if no absolute altitude data is available, set it to None

                    if local_tz is None:
                        # Get timezone string for the given latitude and longitude
                        timezone_str = tf.timezone_at(lng=lon, lat=lat)
                        if timezone_str:
                            local_tz = pytz.timezone(timezone_str)

                    if local_tz:
                        timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S.%f")
                        timestamp = local_tz.localize(timestamp)
                    else:
                        timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S.%f")

                    gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(lat, lon, elevation=alt, time=timestamp))

        output_filename = os.path.splitext(filename)[0] + '.gpx'
        with open(os.path.join(output_dir, output_filename), 'w') as f:
            f.write(gpx.to_xml())