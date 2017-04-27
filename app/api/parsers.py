from werkzeug.datastructures import FileStorage
from app.api import api

upload_parser = api.parser()
upload_parser.add_argument('file', location='files', type=FileStorage, required=True)

flightplan_parser = api.parser()
flightplan_parser.add_argument('flightplan_id', required=False, type=int, help='FlightPlan unique ID')

recon_parser = api.parser()
recon_parser.add_argument('recon_id', required=False, type=int, help='Recon unique ID')