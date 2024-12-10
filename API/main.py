from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_smorest import Api, Blueprint

from controller.FileNames import FileNames, LastUpdatedFile
from controller.uploadFile import uploadFile

from model.Wall import Wall
from model.Room import Room
from model.BillOfMaterials import BillOfMaterials

app = Flask(__name__)

# This adds the title of the api in the specification
app.config["API_TITLE"] = "Configurator"
# This defines the api version in the specification
app.config["API_VERSION"] = "v1"
# This defines the OpenApi version of the specification
app.config["OPENAPI_VERSION"] = "3.1.0"
# This defines the path where the documentation will be stored
app.config["OPENAPI_URL_PREFIX"] = "/docs"
# This defines where the json specifications will be generated
app.config["OPENAPI_JSON_PATH"] = "/openapi.json"
# This defines the rapidoc path after OPENAPI_URL_PREFIX
app.config["OPENAPI_RAPIDOC_PATH"] = "/rapidoc"
# This defines the path to the rapidoc library
app.config["OPENAPI_RAPIDOC_URL"] = "/static/rapidoc-min.js"


CORS(app)
api = Api(app)

blp = Blueprint(
    "Configurator API",
    "wall measures",
    url_prefix="",
    description="List of endpoints used for the API.",
)

"""
@blp.route('/WallMeasures/<string:usdzFile>/', methods=['GET'])
class WallMeasures(MethodView):
    @blp.doc(parameters=[{'in': 'path', 'name': 'usdzFile', 'required': 'true', 'description': 'File name', 'schema': {'type': 'string'}}])
    @blp.response(200, Room.Schema)
    def get(self, usdzFile):
        #usdzFile = "./templates/Fichier_USDZ.usdz"
        usdzFilePath = str(usdzFile)
        return getMeasurement(usdzFilePath)
"""


@app.route("/uploadFile")
def upload_File():
    localFilePath = request.args.get("localFilePath")
    GCPFilePath = request.args.get("GCPFilePath")
    uploadFile(localFilePath, GCPFilePath)
    return "true"


@app.route("/FileNames", methods=["GET"])
def get_fileNames():
    return FileNames()


@app.route("/LastUpdatedFile", methods=["GET"])
def get_lastUpdateddFile():
    return LastUpdatedFile()


@app.route("/getWallMeasures/<usdzFile>/", methods=["GET"])
def get_wall_measures(usdzFile):
    room = Room()
    room.update_from_dict(usdzFile)
    return Room.Schema().dump(room)


@app.route("/tempGetWallMeasures")
def tempGetWallMeasures():
    usdzFile = request.args.get("usdzFile")
    room = Room()
    room.update_from_dict(usdzFile)
    return room.Schema().dump(room)


"""    
    # utiliser ce code quand run en local
    usdzFilePath = "./templates/"+str(usdzFile)
    return getMeasurement(usdzFilePath)
"""


@app.route("/getProcessedWall/", methods=["POST"])
def get_processed_wall():
    wallJson = request.get_json()
    wall = Wall.Schema().load(wallJson)
    wall.update_from_dict()
    return jsonify(wall)


@app.route("/getBestLayout/", methods=["POST"])
def get_best_layout():
    # Init Wall from request body
    wallJson = request.get_json()
    wall = Wall.Schema().load(wallJson)
    wall.update_from_dict()
    # return Wall.Schema().dump(wall.bestLayout)
    # return Wall.Schema().dump(wall)
    return jsonify(wall.bestLayout)


@app.route("/getPanels/", methods=["POST"])
def get_panels():
    # Init Wall from request body
    wallJson = request.get_json()
    wall = Wall.Schema().load(wallJson)
    wall.update_from_dict()
    return wall.panels


@app.route("/getBeams/", methods=["POST"])
def get_beams():
    wallJson = request.get_json()
    wall = Wall.Schema().load(wallJson)
    wall.update_from_dict()
    return wall.beamAssemblies


@app.route("/getMouldings/", methods=["POST"])
def get_mouldings():
    wallJson = request.get_json()
    wall = Wall.Schema().load(wallJson)
    wall.update_from_dict()
    return wall.mouldings


@app.route("/getIClips/", methods=["POST"])
def get_clips():
    wallJson = request.get_json(wallJson)
    wall = Wall.Schema().load(wallJson)
    wall.update_from_dict()
    billOfMaterials = BillOfMaterials(wall)
    return billOfMaterials.getClips()


@app.route("/getBillOfMaterials/", methods=["POST"])
def get_bom():
    wallJson = request.get_json()
    print(wallJson["mouldings"])
    wall = Wall.Schema().load(wallJson)
    wall.update_from_dict()
    billOfMaterials = BillOfMaterials(wall)
    return BillOfMaterials.Schema().dump(billOfMaterials)


if __name__ == "__main__":
    api.register_blueprint(blp)
    app.run(debug=True)
