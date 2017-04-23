from flask_restplus import fields
from app.api import api

app_informations = api.model('AppInformations', {
    'updated_on' : fields.DateTime(dt_format='iso8601', required = True, description = 'Last app update datetime'),
})

minimal_gpscoord = api.model('MinimalGPSCoord', {
    'lat' : fields.Float(required = True, description = 'Latitute of GPSCoord', min = -90, max = 90),
    'lon' : fields.Float(required = True, description = 'Longitude of GPSCoord', min = -180, max = 180),
})

gpscoord = api.inherit('GPSCoord', minimal_gpscoord, {
    'alt' : fields.Float(required = False, description = 'Altitude of GPSCoord', min = 0, default = 1)
})

gimbal = api.model('Gimbal', {
    'yaw' : fields.Float(required = False, description = 'Yaw value of Gimbal', min = -180, max = 180, default = 0),
    'pitch' : fields.Float(required = False, description='Pitch value of Gimbal', min = -180, max = 180, default = 0),
    'roll' : fields.Float(required = False, description = 'Roll value of Gimbal', min = -180, max = 180, default = 0)
})

droneparameters = api.model('DronesParameters', {
    'rotation' : fields.Integer(required = False, description = 'Rotation of drone on altitude axis', min = -180, max = 180, default = 0),
    'coord' : fields.Nested(gpscoord, required = True, description = 'GPS coordinate of drone'),
    'gimbal' : fields.Nested(gimbal, required = False, description = 'Gimbal parameters')
})

