import os
import re
import gpxpy.gpx
from datetime import datetime

# Regular expression pattern for extracting the relevant data
pattern = re.compile(r'\[(latitude|longitude|rel_alt|abs_alt): ([\d.-]+)\]')

# Directory paths
input_dir = 'input'
output_dir = 'output'

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Loop over all files in the input directory
for filename in os.listdir(input_dir):
    # Check if the file has an SRT extension (ignoring case)
    if filename.lower().endswith('.srt'):
        # Open the SRT file
        with open(os.path.join(input_dir, filename), 'r') as f:
            content = f.read()

        # Create a new GPX file
        gpx = gpxpy.gpx.GPX()

        # Create a new GPX track
        gpx_track = gpxpy.gpx.GPXTrack()
        gpx.tracks.append(gpx_track)

        # Create a new GPX segment
        gpx_segment = gpxpy.gpx.GPXTrackSegment()
        gpx_track.segments.append(gpx_segment)

        # Split the content into blocks
        blocks = content.split('\n\n')

        # Loop over the blocks
        for block in blocks:
            lines = block.split('\n')
            if len(lines) >= 5:
                # Parse the timestamp from the fourth line
                timestamp = datetime.strptime(lines[3].strip(), "%Y-%m-%d %H:%M:%S.%f")

                # Parse the GPS info from the fifth line
                gps_info = lines[4]

                # Use a regular expression to extract the latitude, longitude, and altitude
                data = dict(pattern.findall(gps_info))

                if 'latitude' in data and 'longitude' in data:
                    lat, lon = float(data['latitude']), float(data['longitude'])

                    # Split the altitude information into relative and absolute altitudes
                    rel_alt = data.get('rel_alt')
                    abs_alt = data.get('abs_alt')

                    # If both relative and absolute altitudes are present, use the absolute one
                    if abs_alt:
                        abs_alt = float(abs_alt.split()[0])
                    elif rel_alt:
                        abs_alt = float(rel_alt.split()[0])
                    else:
                        abs_alt = None

                    # Create a new GPX point and add it to the segment
                    gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(lat, lon, elevation=abs_alt, time=timestamp))

        # Write the GPX file
        output_filename = os.path.splitext(filename)[0] + '.gpx'
        with open(os.path.join(output_dir, output_filename), 'w') as f:
            f.write(gpx.to_xml())
