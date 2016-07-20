from app.blueprint import basic
from flask import request, jsonify

from app.database import DBManager
from app.model.neis import ProviderInfo, Neis
from app.model.user import Provider, Gcm
from app.routes import gcmController

updateKey = "6041cef9600a531f527a69186b66bd21"
db = DBManager.db

@basic.route("/feed/update")
def update():
    result = False

    if request.args.get("key") == updateKey:
        result = True

        for token in getRegProviders():
            pi = ProviderInfo.query.filter(ProviderInfo.token == token).first()

            if pi.type == 0:
                processNeis(token)
            else:
                processRes(token)

    return jsonify({"result": result})


def processNeis(token):
    school = Neis.query.filter(Neis.token == token).first()
    gcms = []

    for p in Provider.query.filter(Provider.prov_token == token).all():
        gcm = Gcm.query.filter(Gcm.sid == p.sid).first()
        if gcm is not None:
            gcms.append(gcm.token)

    gcmController.push(gcms, "EverMeal", "'" + school.name + "' %ec%98%a4%eb%8a%98%ec%9d%98+%eb%a9%94%eb%89%b4%ea%b0%80+%ec%98%ac%eb%9d%bc%ec%99%94%ec%8a%b5%eb%8b%88%eb%8b%a4!")

def processRes(token):
    pass

def getRegProviders():
    query = db.session.query(Provider.prov_token.distinct().label("prov_token"))

    return [row.prov_token for row in query.all()]
